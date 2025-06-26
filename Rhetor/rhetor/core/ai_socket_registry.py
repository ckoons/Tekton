"""AI Socket Registry for Rhetor.

Following Unix philosophy: AIs are just sockets that read and write.
This registry manages the socket lifecycle and provides transparent header routing.

Usage:
    registry = AISocketRegistry()
    await registry.initialize()
    
    # Create a socket
    socket_id = await registry.create("claude-3", "Be helpful", {})
    
    # Write to socket
    await registry.write(socket_id, "Hello AI")
    
    # Read from socket
    messages = await registry.read(socket_id)
    
    # Broadcast to all
    await registry.write("team-chat-all", "Team meeting!")
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from rhetor.utils.engram_helper import get_engram_client, EngramClient

logger = logging.getLogger(__name__)


class SocketState(Enum):
    """Socket states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNRESPONSIVE = "unresponsive"


@dataclass
class AISocket:
    """Represents an AI socket.
    
    Just like Unix sockets, these are simple read/write interfaces.
    No complex state management - that's not the Unix way.
    """
    socket_id: str
    model: str
    prompt: str
    context: Dict[str, Any]
    created_at: str
    state: SocketState = SocketState.ACTIVE
    last_activity: Optional[str] = None
    message_queue: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.message_queue is None:
            self.message_queue = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "socket_id": self.socket_id,
            "model": self.model,
            "prompt": self.prompt,
            "context": self.context,
            "created_at": self.created_at,
            "state": self.state.value,
            "last_activity": self.last_activity,
            "message_queue": self.message_queue
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AISocket":
        """Create from dictionary."""
        data["state"] = SocketState(data.get("state", "active"))
        return cls(**data)


class AISocketRegistry:
    """Registry for AI sockets.
    
    This is the central registry for all AI communication in Rhetor.
    Following Unix philosophy: simple, does one thing well.
    """
    
    def __init__(self):
        """Initialize the registry."""
        self.sockets: Dict[str, AISocket] = {}
        self.engram_client: Optional[EngramClient] = None
        self._initialized = False
        self._namespace = "rhetor_sockets"
        
    async def initialize(self) -> None:
        """Initialize the registry and restore persisted state."""
        if self._initialized:
            return
            
        try:
            # Get Engram client for persistence
            self.engram_client = await get_engram_client()
            
            # Restore socket registry from persistence
            await self._restore_registry()
            
            # Create special broadcast socket
            if "team-chat-all" not in self.sockets:
                await self.create(
                    socket_id="team-chat-all",
                    model="broadcast",
                    prompt="Broadcast to all team members",
                    context={"type": "broadcast", "description": "Team chat broadcast socket"}
                )
            
            self._initialized = True
            logger.info(f"Socket registry initialized with {len(self.sockets)} sockets")
            
        except Exception as e:
            logger.error(f"Failed to initialize socket registry: {e}")
            # Continue without persistence - in-memory only
            self._initialized = True
    
    async def create(
        self,
        model: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        socket_id: Optional[str] = None
    ) -> str:
        """Create a new AI socket.
        
        Args:
            model: The AI model to use
            prompt: The system prompt
            context: Optional context dictionary
            socket_id: Optional specific socket ID (auto-generated if not provided)
            
        Returns:
            The socket ID
        """
        # Generate socket ID if not provided
        if not socket_id:
            import uuid
            base_name = model.lower().replace("-", "_")
            socket_id = f"{base_name}_{uuid.uuid4().hex[:8]}"
        
        # Create socket
        socket = AISocket(
            socket_id=socket_id,
            model=model,
            prompt=prompt,
            context=context or {},
            created_at=datetime.utcnow().isoformat(),
            state=SocketState.ACTIVE
        )
        
        # Register socket
        self.sockets[socket_id] = socket
        
        # Persist
        await self._persist_socket(socket)
        
        logger.info(f"Created socket: {socket_id} (model: {model})")
        return socket_id
    
    async def read(self, socket_id: str) -> List[Dict[str, Any]]:
        """Read messages from a socket.
        
        Automatically adds source headers for routing.
        
        Args:
            socket_id: The socket to read from
            
        Returns:
            List of messages with headers
        """
        if socket_id == "team-chat-all":
            # Read from all sockets
            all_messages = []
            for sid, socket in self.sockets.items():
                if sid != "team-chat-all" and socket.message_queue:
                    # Add source header to each message
                    for msg in socket.message_queue:
                        all_messages.append({
                            "header": f"[team-chat-from-{sid}]",
                            "content": msg.get("content", ""),
                            "timestamp": msg.get("timestamp", ""),
                            "metadata": msg.get("metadata", {})
                        })
                    # Clear the queue after reading
                    socket.message_queue = []
                    socket.last_activity = datetime.utcnow().isoformat()
                    await self._persist_socket(socket)
            return all_messages
        
        # Read from specific socket
        socket = self.sockets.get(socket_id)
        if not socket:
            logger.warning(f"Socket not found: {socket_id}")
            return []
        
        # Get messages and clear queue
        messages = []
        for msg in socket.message_queue:
            messages.append({
                "header": f"[team-chat-from-{socket_id}]",
                "content": msg.get("content", ""),
                "timestamp": msg.get("timestamp", ""),
                "metadata": msg.get("metadata", {})
            })
        
        socket.message_queue = []
        socket.last_activity = datetime.utcnow().isoformat()
        await self._persist_socket(socket)
        
        return messages
    
    async def write(self, socket_id: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Write a message to a socket.
        
        Automatically adds destination headers for routing.
        
        Args:
            socket_id: The socket to write to
            message: The message content
            metadata: Optional metadata
            
        Returns:
            Success status
        """
        timestamp = datetime.utcnow().isoformat()
        
        if socket_id == "team-chat-all":
            # Broadcast to all sockets
            success = True
            for sid, socket in self.sockets.items():
                if sid != "team-chat-all" and socket.state == SocketState.ACTIVE:
                    socket.message_queue.append({
                        "header": f"[team-chat-to-{sid}]",
                        "content": message,
                        "timestamp": timestamp,
                        "metadata": metadata or {}
                    })
                    socket.last_activity = timestamp
                    if not await self._persist_socket(socket):
                        success = False
            return success
        
        # Write to specific socket
        socket = self.sockets.get(socket_id)
        if not socket:
            logger.warning(f"Socket not found: {socket_id}")
            return False
        
        if socket.state != SocketState.ACTIVE:
            logger.warning(f"Socket {socket_id} is not active (state: {socket.state})")
            return False
        
        # Add message to queue
        socket.message_queue.append({
            "header": f"[team-chat-to-{socket_id}]",
            "content": message,
            "timestamp": timestamp,
            "metadata": metadata or {}
        })
        socket.last_activity = timestamp
        
        return await self._persist_socket(socket)
    
    async def delete(self, socket_id: str) -> bool:
        """Delete a socket (terminate AI).
        
        Args:
            socket_id: The socket to delete
            
        Returns:
            Success status
        """
        if socket_id == "team-chat-all":
            logger.warning("Cannot delete broadcast socket")
            return False
        
        if socket_id not in self.sockets:
            logger.warning(f"Socket not found: {socket_id}")
            return False
        
        # Remove from registry
        del self.sockets[socket_id]
        
        # Remove from persistence
        if self.engram_client:
            try:
                await self.engram_client.delete_memory(self._namespace, socket_id)
            except Exception as e:
                logger.error(f"Failed to delete socket from persistence: {e}")
        
        logger.info(f"Deleted socket: {socket_id}")
        return True
    
    async def reset(self, socket_id: str) -> bool:
        """Reset a socket (clear context, keep alive).
        
        Args:
            socket_id: The socket to reset
            
        Returns:
            Success status
        """
        socket = self.sockets.get(socket_id)
        if not socket:
            logger.warning(f"Socket not found: {socket_id}")
            return False
        
        # Clear message queue and reset state
        socket.message_queue = []
        socket.context = {}
        socket.state = SocketState.ACTIVE
        socket.last_activity = datetime.utcnow().isoformat()
        
        # Persist changes
        success = await self._persist_socket(socket)
        
        logger.info(f"Reset socket: {socket_id}")
        return success
    
    async def list_sockets(self) -> List[Dict[str, Any]]:
        """List all registered sockets.
        
        Returns:
            List of socket summaries
        """
        sockets = []
        for socket_id, socket in self.sockets.items():
            sockets.append({
                "socket_id": socket_id,
                "model": socket.model,
                "state": socket.state.value,
                "created_at": socket.created_at,
                "last_activity": socket.last_activity,
                "queue_size": len(socket.message_queue)
            })
        return sockets
    
    async def get_socket_info(self, socket_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a socket.
        
        Args:
            socket_id: The socket ID
            
        Returns:
            Socket information or None if not found
        """
        socket = self.sockets.get(socket_id)
        if not socket:
            return None
        
        return socket.to_dict()
    
    async def mark_unresponsive(self, socket_id: str) -> bool:
        """Mark a socket as unresponsive.
        
        Args:
            socket_id: The socket to mark
            
        Returns:
            Success status
        """
        socket = self.sockets.get(socket_id)
        if not socket:
            logger.warning(f"Socket not found: {socket_id}")
            return False
        
        socket.state = SocketState.UNRESPONSIVE
        socket.last_activity = datetime.utcnow().isoformat()
        
        success = await self._persist_socket(socket)
        logger.warning(f"Marked socket as unresponsive: {socket_id}")
        
        return success
    
    # Private methods for persistence
    
    async def _persist_socket(self, socket: AISocket) -> bool:
        """Persist a socket to Engram."""
        if not self.engram_client:
            return True  # No persistence available
        
        try:
            return await self.engram_client.store_memory(
                namespace=self._namespace,
                key=socket.socket_id,
                data=socket.to_dict(),
                metadata={
                    "type": "ai_socket",
                    "model": socket.model,
                    "state": socket.state.value
                }
            )
        except Exception as e:
            logger.error(f"Failed to persist socket {socket.socket_id}: {e}")
            return False
    
    async def _restore_registry(self) -> None:
        """Restore socket registry from persistence."""
        if not self.engram_client:
            return
        
        try:
            # List all sockets in namespace
            memories = await self.engram_client.list_memories(
                namespace=self._namespace,
                limit=1000
            )
            
            # Restore each socket
            for memory in memories:
                try:
                    socket_data = await self.engram_client.get_memory(
                        namespace=self._namespace,
                        key=memory["key"]
                    )
                    
                    if socket_data:
                        socket = AISocket.from_dict(socket_data)
                        self.sockets[socket.socket_id] = socket
                        logger.info(f"Restored socket: {socket.socket_id}")
                
                except Exception as e:
                    logger.error(f"Failed to restore socket {memory['key']}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to restore socket registry: {e}")


# Singleton instance
_registry_instance: Optional[AISocketRegistry] = None


async def get_socket_registry() -> AISocketRegistry:
    """Get the singleton socket registry instance.
    
    Returns:
        The initialized socket registry
    """
    global _registry_instance
    
    if _registry_instance is None:
        _registry_instance = AISocketRegistry()
        await _registry_instance.initialize()
    
    return _registry_instance