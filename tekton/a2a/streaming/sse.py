"""
Server-Sent Events (SSE) implementation for A2A Protocol

Provides unidirectional streaming from server to clients.
"""

import asyncio
import json
import logging
from typing import Dict, Set, AsyncGenerator, Optional, Any, Callable
from datetime import datetime
from uuid import uuid4

from fastapi import Response
from fastapi.responses import StreamingResponse

from .events import StreamEvent, EventType

logger = logging.getLogger(__name__)


class SSEEvent:
    """Represents a Server-Sent Event"""
    
    def __init__(
        self,
        data: Any,
        event: Optional[str] = None,
        id: Optional[str] = None,
        retry: Optional[int] = None
    ):
        self.data = data
        self.event = event
        self.id = id or str(uuid4())
        self.retry = retry
    
    def format(self) -> str:
        """Format the event for SSE protocol"""
        lines = []
        
        if self.id:
            lines.append(f"id: {self.id}")
        
        if self.event:
            lines.append(f"event: {self.event}")
        
        if self.retry is not None:
            lines.append(f"retry: {self.retry}")
        
        # Handle data serialization
        if isinstance(self.data, str):
            data_str = self.data
        else:
            data_str = json.dumps(self.data)
        
        # SSE requires each line of data to be prefixed with "data: "
        for line in data_str.split('\n'):
            lines.append(f"data: {line}")
        
        # SSE events are terminated with double newline
        return '\n'.join(lines) + '\n\n'


class SSEConnection:
    """Represents an active SSE connection"""
    
    def __init__(self, connection_id: str, filters: Optional[Dict[str, Any]] = None):
        self.id = connection_id
        self.filters = filters or {}
        self.queue: asyncio.Queue[StreamEvent] = asyncio.Queue()
        self.active = True
        self.created_at = datetime.utcnow()
    
    def matches_filters(self, event: StreamEvent) -> bool:
        """Check if event matches connection filters"""
        if not self.filters:
            return True
        
        # Filter by event type
        if "event_types" in self.filters:
            if event.type not in self.filters["event_types"]:
                return False
        
        # Filter by task_id
        if "task_id" in self.filters:
            if hasattr(event, "task_id") and event.task_id != self.filters["task_id"]:
                return False
        
        # Filter by agent_id
        if "agent_id" in self.filters:
            if hasattr(event, "agent_id") and event.agent_id != self.filters["agent_id"]:
                return False
        
        # Filter by channel
        if "channel" in self.filters:
            if hasattr(event, "channel") and event.channel != self.filters["channel"]:
                return False
        
        return True
    
    async def send_event(self, event: StreamEvent) -> None:
        """Send an event to this connection"""
        if self.active and self.matches_filters(event):
            await self.queue.put(event)
    
    def close(self) -> None:
        """Close the connection"""
        self.active = False


class SSEManager:
    """
    Manages Server-Sent Events connections and event distribution
    """
    
    def __init__(self):
        self._connections: Dict[str, SSEConnection] = {}
        self._event_handlers: Dict[EventType, Set[Callable]] = {}
        self._lock = asyncio.Lock()
    
    async def create_connection(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> SSEConnection:
        """Create a new SSE connection"""
        connection_id = f"sse-{uuid4()}"
        connection = SSEConnection(connection_id, filters)
        
        async with self._lock:
            self._connections[connection_id] = connection
            logger.info(f"Created SSE connection {connection_id} with filters: {filters}")
        
        # Send connection established event
        await connection.send_event(
            StreamEvent.create(
                EventType.CONNECTION_ESTABLISHED,
                source="system",
                data={"connection_id": connection_id}
            )
        )
        
        return connection
    
    async def close_connection(self, connection_id: str) -> None:
        """Close an SSE connection"""
        async with self._lock:
            if connection_id in self._connections:
                connection = self._connections[connection_id]
                connection.close()
                del self._connections[connection_id]
                logger.info(f"Closed SSE connection {connection_id}")
    
    async def broadcast_event(self, event: StreamEvent) -> None:
        """Broadcast an event to all matching connections"""
        async with self._lock:
            connections = list(self._connections.values())
        
        # Send to all matching connections
        tasks = []
        for connection in connections:
            if connection.active:
                tasks.append(connection.send_event(event))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.debug(f"Broadcasted event {event.type} to {len(tasks)} connections")
    
    async def stream_events(
        self,
        connection: SSEConnection,
        keepalive_interval: int = 30
    ) -> AsyncGenerator[str, None]:
        """
        Generate SSE stream for a connection
        
        Args:
            connection: The SSE connection
            keepalive_interval: Seconds between keepalive messages
        """
        try:
            while connection.active:
                try:
                    # Wait for event with timeout for keepalive
                    event = await asyncio.wait_for(
                        connection.queue.get(),
                        timeout=keepalive_interval
                    )
                    
                    # Format and yield the event
                    sse_event = SSEEvent(
                        data=event.model_dump(mode='json'),  # Use JSON mode for serialization
                        event=event.type,
                        id=event.id
                    )
                    yield sse_event.format()
                    
                except asyncio.TimeoutError:
                    # Send keepalive comment
                    yield ": keepalive\n\n"
                    
        except asyncio.CancelledError:
            logger.info(f"SSE stream cancelled for connection {connection.id}")
            raise
        finally:
            await self.close_connection(connection.id)
    
    def register_handler(
        self,
        event_type: EventType,
        handler: Callable[[StreamEvent], None]
    ) -> None:
        """Register a handler for specific event types"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = set()
        self._event_handlers[event_type].add(handler)
    
    async def get_active_connections(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active connections"""
        async with self._lock:
            return {
                conn_id: {
                    "id": conn.id,
                    "active": conn.active,
                    "filters": conn.filters,
                    "created_at": conn.created_at.isoformat(),
                    "queue_size": conn.queue.qsize()
                }
                for conn_id, conn in self._connections.items()
            }


def create_sse_response(
    sse_manager: SSEManager,
    filters: Optional[Dict[str, Any]] = None
) -> StreamingResponse:
    """
    Create a FastAPI streaming response for SSE
    
    Args:
        sse_manager: The SSE manager instance
        filters: Optional filters for events
    
    Returns:
        StreamingResponse configured for SSE
    """
    async def event_generator():
        connection = await sse_manager.create_connection(filters)
        async for event in sse_manager.stream_events(connection):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
        }
    )