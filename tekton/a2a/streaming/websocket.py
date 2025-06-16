"""
WebSocket implementation for A2A Protocol v0.2.1

Provides bidirectional streaming for real-time agent communication.
Supports JSON-RPC 2.0 messages over WebSocket connections.
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any, Callable, Union
from datetime import datetime, timezone
from uuid import uuid4
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from ..jsonrpc import (
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCError,
    parse_jsonrpc_message
)
from .events import StreamEvent, EventType

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """WebSocket connection states"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"


class WebSocketConnection:
    """Represents a single WebSocket connection"""
    
    def __init__(
        self,
        connection_id: str,
        websocket: WebSocket,
        agent_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ):
        self.id = connection_id
        self.websocket = websocket
        self.agent_id = agent_id
        self.filters = filters or {}
        self.state = ConnectionState.CONNECTING
        self.connected_at = datetime.now(timezone.utc)
        self.last_activity = datetime.now(timezone.utc)
        self.message_count = 0
        self.error_count = 0
        
        # Callbacks for handling different message types
        self.on_request: Optional[Callable] = None
        self.on_notification: Optional[Callable] = None
        self.on_response: Optional[Callable] = None
        
        # Pending requests awaiting responses
        self.pending_requests: Dict[Union[str, int], asyncio.Future] = {}
    
    async def accept(self):
        """Accept the WebSocket connection"""
        await self.websocket.accept()
        self.state = ConnectionState.CONNECTED
        logger.info(f"WebSocket connection {self.id} accepted")
    
    async def send_message(self, message: Union[dict, str]) -> bool:
        """Send a message over the WebSocket"""
        try:
            if self.state != ConnectionState.CONNECTED:
                logger.warning(f"Cannot send to {self.id}: state is {self.state}")
                return False
            
            if isinstance(message, dict):
                message = json.dumps(message)
            
            await self.websocket.send_text(message)
            self.last_activity = datetime.now(timezone.utc)
            self.message_count += 1
            return True
            
        except Exception as e:
            logger.error(f"Error sending to {self.id}: {e}")
            self.error_count += 1
            return False
    
    async def send_request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0
    ) -> Any:
        """Send a JSON-RPC request and wait for response"""
        request_id = str(uuid4())
        request = JSONRPCRequest(
            id=request_id,
            method=method,
            params=params
        )
        
        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        try:
            # Send request
            sent = await self.send_message(request.to_dict())
            if not sent:
                raise Exception("Failed to send request")
            
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"Request {request_id} timed out")
            raise
        finally:
            # Clean up pending request
            self.pending_requests.pop(request_id, None)
    
    async def send_notification(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send a JSON-RPC notification (no response expected)"""
        # In JSON-RPC 2.0, a notification is a request without an ID
        notification = JSONRPCRequest(
            method=method,
            params=params,
            id=None  # No ID makes it a notification
        )
        return await self.send_message(notification.to_dict())
    
    async def send_event(self, event: StreamEvent) -> bool:
        """Send a streaming event as a notification"""
        return await self.send_notification(
            method="event.publish",
            params=event.model_dump(mode='json')
        )
    
    async def close(self, code: int = 1000, reason: str = "Normal closure"):
        """Close the WebSocket connection"""
        if self.state in [ConnectionState.DISCONNECTING, ConnectionState.DISCONNECTED]:
            return
        
        self.state = ConnectionState.DISCONNECTING
        try:
            # Check if websocket is still open before closing
            if hasattr(self.websocket, 'state') and self.websocket.state == WebSocketState.CONNECTED:
                await self.websocket.close(code=code, reason=reason)
        except Exception as e:
            # Ignore close errors as they're often expected
            if "Unexpected ASGI message" not in str(e):
                logger.debug(f"WebSocket close for {self.id}: {e}")
        finally:
            self.state = ConnectionState.DISCONNECTED
            
            # Cancel any pending requests
            for future in self.pending_requests.values():
                if not future.done():
                    future.cancel()
            self.pending_requests.clear()
    
    def matches_filters(self, event: StreamEvent) -> bool:
        """Check if an event matches connection filters"""
        if not self.filters:
            return True
        
        # Check task_id filter
        if 'task_id' in self.filters and hasattr(event, 'task_id'):
            if event.task_id != self.filters['task_id']:
                return False
        
        # Check agent_id filter
        if 'agent_id' in self.filters and hasattr(event, 'agent_id'):
            if event.agent_id != self.filters['agent_id']:
                return False
        
        # Check event_types filter
        if 'event_types' in self.filters:
            allowed_types = self.filters['event_types']
            if isinstance(allowed_types, str):
                allowed_types = [allowed_types]
            # Handle both enum value and string comparison
            event_type_value = event.type.value if hasattr(event.type, 'value') else str(event.type)
            if event_type_value not in allowed_types:
                return False
        
        # Check channel filter (for pub/sub)
        if 'channel' in self.filters and hasattr(event, 'channel'):
            if event.channel != self.filters['channel']:
                return False
        
        return True


class WebSocketManager:
    """Manages WebSocket connections for A2A streaming"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self._lock = asyncio.Lock()
        
        # Global message handlers
        self.on_request: Optional[Callable] = None
        self.on_notification: Optional[Callable] = None
    
    async def connect(
        self,
        websocket: WebSocket,
        agent_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> WebSocketConnection:
        """Accept a new WebSocket connection"""
        connection_id = str(uuid4())
        connection = WebSocketConnection(
            connection_id=connection_id,
            websocket=websocket,
            agent_id=agent_id,
            filters=filters
        )
        
        # Accept the connection
        await connection.accept()
        
        # Store connection
        async with self._lock:
            self.connections[connection_id] = connection
        
        # Send initial connection event
        await connection.send_event(
            StreamEvent(
                id=str(uuid4()),
                type=EventType.CONNECTION_ESTABLISHED,
                timestamp=datetime.now(timezone.utc),
                source="websocket",
                data={"connection_id": connection_id}
            )
        )
        
        logger.info(f"WebSocket connection established: {connection_id}")
        return connection
    
    async def disconnect(self, connection_id: str):
        """Disconnect and remove a WebSocket connection"""
        async with self._lock:
            connection = self.connections.pop(connection_id, None)
        
        if connection:
            await connection.close()
            logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def handle_connection(self, connection: WebSocketConnection):
        """Handle messages for a WebSocket connection"""
        try:
            while connection.state == ConnectionState.CONNECTED:
                # Receive message
                try:
                    data = await connection.websocket.receive_text()
                    connection.last_activity = datetime.utcnow()
                except WebSocketDisconnect:
                    break
                
                # Parse JSON-RPC message
                try:
                    message = json.loads(data)
                    parsed = parse_jsonrpc_message(message)
                except Exception as e:
                    logger.error(f"Invalid message from {connection.id}: {e}")
                    await connection.send_message(
                        JSONRPCResponse(
                            id=None,
                            error={
                                "code": -32700,
                                "message": "Parse error"
                            }
                        ).to_dict()
                    )
                    continue
                
                # Handle different message types
                if isinstance(parsed, JSONRPCRequest):
                    # Check if it's a notification (no ID)
                    if parsed.id is None:
                        await self._handle_notification(connection, parsed)
                    else:
                        await self._handle_request(connection, parsed)
                elif isinstance(parsed, JSONRPCResponse):
                    await self._handle_response(connection, parsed)
                # Note: parse_jsonrpc_message only returns JSONRPCRequest or JSONRPCBatch
                # Error responses would come as regular JSONRPCResponse with error field
                
        except Exception as e:
            logger.error(f"Error in WebSocket handler for {connection.id}: {e}")
        finally:
            await self.disconnect(connection.id)
    
    async def _handle_request(
        self,
        connection: WebSocketConnection,
        request: JSONRPCRequest
    ):
        """Handle incoming JSON-RPC request"""
        try:
            # Use connection-specific handler or global handler
            handler = connection.on_request or self.on_request
            if not handler:
                raise Exception("No request handler configured")
            
            # Call handler
            result = await handler(connection, request)
            
            # Send response
            response = JSONRPCResponse(
                id=request.id,
                result=result
            )
            await connection.send_message(response.to_dict())
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            error_response = JSONRPCResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": str(e)
                }
            )
            await connection.send_message(error_response.to_dict())
    
    async def _handle_notification(
        self,
        connection: WebSocketConnection,
        notification: JSONRPCRequest
    ):
        """Handle incoming JSON-RPC notification"""
        try:
            # Use connection-specific handler or global handler
            handler = connection.on_notification or self.on_notification
            if handler:
                await handler(connection, notification)
        except Exception as e:
            logger.error(f"Error handling notification: {e}")
    
    async def _handle_response(
        self,
        connection: WebSocketConnection,
        response: JSONRPCResponse
    ):
        """Handle incoming JSON-RPC response"""
        # Check if this is a response to a pending request
        future = connection.pending_requests.get(response.id)
        if future and not future.done():
            future.set_result(response.result)
        else:
            # Use connection-specific handler if available
            if connection.on_response:
                await connection.on_response(connection, response)
    
    async def _handle_error_response(
        self,
        connection: WebSocketConnection,
        error: JSONRPCError
    ):
        """Handle incoming JSON-RPC error response"""
        # Check if this is an error for a pending request
        future = connection.pending_requests.get(error.id)
        if future and not future.done():
            future.set_exception(
                Exception(f"JSON-RPC Error: {error.error}")
            )
    
    async def broadcast_event(self, event: StreamEvent):
        """Broadcast an event to all matching connections"""
        tasks = []
        
        async with self._lock:
            for connection in self.connections.values():
                if connection.state == ConnectionState.CONNECTED:
                    if connection.matches_filters(event):
                        tasks.append(connection.send_event(event))
        
        # Send to all connections concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for r in results if r is True)
            logger.debug(
                f"Broadcast event {event.type} to "
                f"{success_count}/{len(tasks)} connections"
            )
    
    async def send_to_agent(
        self,
        agent_id: str,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> int:
        """Send a notification to all connections for a specific agent"""
        count = 0
        
        async with self._lock:
            for connection in self.connections.values():
                if (connection.agent_id == agent_id and 
                    connection.state == ConnectionState.CONNECTED):
                    success = await connection.send_notification(method, params)
                    if success:
                        count += 1
        
        return count
    
    def get_connection(self, connection_id: str) -> Optional[WebSocketConnection]:
        """Get a specific connection by ID"""
        return self.connections.get(connection_id)
    
    def get_connections_for_agent(
        self,
        agent_id: str
    ) -> list[WebSocketConnection]:
        """Get all connections for a specific agent"""
        return [
            conn for conn in self.connections.values()
            if conn.agent_id == agent_id
        ]
    
    async def close_all(self):
        """Close all WebSocket connections"""
        async with self._lock:
            connection_ids = list(self.connections.keys())
        
        for connection_id in connection_ids:
            await self.disconnect(connection_id)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


async def handle_websocket(
    websocket: WebSocket,
    agent_id: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    on_request: Optional[Callable] = None,
    on_notification: Optional[Callable] = None
) -> None:
    """
    Handle a WebSocket connection for A2A streaming
    
    Args:
        websocket: FastAPI WebSocket instance
        agent_id: Optional agent ID for the connection
        filters: Optional filters for event routing
        on_request: Optional handler for incoming requests
        on_notification: Optional handler for incoming notifications
    """
    connection = await websocket_manager.connect(websocket, agent_id, filters)
    
    # Set handlers if provided
    if on_request:
        connection.on_request = on_request
    if on_notification:
        connection.on_notification = on_notification
    
    # Handle the connection
    await websocket_manager.handle_connection(connection)