"""Integration between AI Socket Registry and AI Specialist Manager.

This module bridges the socket registry with the AI specialist manager,
ensuring that AI specialists automatically get sockets for team chat.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .ai_socket_registry import get_socket_registry
from .ai_specialist_manager import AISpecialistManager, AISpecialistConfig

logger = logging.getLogger(__name__)


class SocketSpecialistIntegration:
    """Integrates socket registry with AI specialist manager."""
    
    def __init__(self, specialist_manager: AISpecialistManager):
        """Initialize integration.
        
        Args:
            specialist_manager: The AI specialist manager instance
        """
        self.specialist_manager = specialist_manager
        self.socket_registry = None
        self.specialist_sockets: Dict[str, str] = {}  # specialist_id -> socket_id
        
    async def initialize(self):
        """Initialize the integration."""
        self.socket_registry = await get_socket_registry()
        
        # Create sockets for existing active specialists
        await self._sync_specialists_to_sockets()
        
        logger.info("Socket-Specialist integration initialized")
    
    async def _sync_specialists_to_sockets(self):
        """Synchronize specialists with sockets."""
        for specialist_id, config in self.specialist_manager.specialists.items():
            if config.status == "active" and specialist_id not in self.specialist_sockets:
                await self.create_socket_for_specialist(specialist_id)
    
    async def create_socket_for_specialist(self, specialist_id: str) -> Optional[str]:
        """Create a socket for an AI specialist.
        
        Args:
            specialist_id: The specialist ID
            
        Returns:
            Socket ID if created, None if failed
        """
        if specialist_id not in self.specialist_manager.specialists:
            logger.error(f"Unknown specialist: {specialist_id}")
            return None
        
        config = self.specialist_manager.specialists[specialist_id]
        
        # Build socket configuration from specialist config
        model = config.model_config.get("model", "default")
        
        # Create system prompt from personality
        personality = config.personality
        prompt_parts = [
            f"You are {personality.get('name', specialist_id)}.",
            personality.get('description', ''),
            personality.get('traits', ''),
            f"Your role is: {personality.get('role', 'specialist')}",
            f"Component: {config.component_id}"
        ]
        prompt = " ".join(filter(None, prompt_parts))
        
        # Create context from capabilities and config
        context = {
            "specialist_id": specialist_id,
            "specialist_type": config.specialist_type,
            "component_id": config.component_id,
            "capabilities": config.capabilities,
            "personality": personality
        }
        
        # Create socket with specialist ID as socket ID
        socket_id = await self.socket_registry.create(
            model=model,
            prompt=prompt,
            context=context,
            socket_id=specialist_id
        )
        
        self.specialist_sockets[specialist_id] = socket_id
        logger.info(f"Created socket {socket_id} for specialist {specialist_id}")
        
        return socket_id
    
    async def remove_socket_for_specialist(self, specialist_id: str) -> bool:
        """Remove socket when specialist stops.
        
        Args:
            specialist_id: The specialist ID
            
        Returns:
            Success status
        """
        socket_id = self.specialist_sockets.get(specialist_id)
        if not socket_id:
            return True
        
        success = await self.socket_registry.delete(socket_id)
        if success:
            del self.specialist_sockets[specialist_id]
            logger.info(f"Removed socket for specialist {specialist_id}")
        
        return success
    
    async def on_specialist_created(self, specialist_id: str):
        """Hook called when a specialist is created.
        
        Args:
            specialist_id: The newly created specialist
        """
        await self.create_socket_for_specialist(specialist_id)
    
    async def on_specialist_stopped(self, specialist_id: str):
        """Hook called when a specialist stops.
        
        Args:
            specialist_id: The stopped specialist
        """
        await self.remove_socket_for_specialist(specialist_id)
    
    async def send_to_specialist(self, specialist_id: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Send a message to a specialist's socket.
        
        Args:
            specialist_id: Target specialist
            message: Message content
            metadata: Optional metadata
            
        Returns:
            Success status
        """
        socket_id = self.specialist_sockets.get(specialist_id)
        if not socket_id:
            logger.warning(f"No socket found for specialist {specialist_id}")
            return False
        
        return await self.socket_registry.write(socket_id, message, metadata)
    
    async def read_from_specialist(self, specialist_id: str) -> List[Dict[str, Any]]:
        """Read messages from a specialist's socket.
        
        Args:
            specialist_id: Source specialist
            
        Returns:
            List of messages
        """
        socket_id = self.specialist_sockets.get(specialist_id)
        if not socket_id:
            logger.warning(f"No socket found for specialist {specialist_id}")
            return []
        
        return await self.socket_registry.read(socket_id)
    
    async def get_active_specialists(self) -> List[Dict[str, Any]]:
        """Get list of active specialists with sockets.
        
        Returns:
            List of specialist info with socket status
        """
        specialists = []
        
        for specialist_id, config in self.specialist_manager.specialists.items():
            socket_id = self.specialist_sockets.get(specialist_id)
            socket_info = None
            
            if socket_id:
                socket_info = await self.socket_registry.get_socket_info(socket_id)
            
            specialists.append({
                "specialist_id": specialist_id,
                "specialist_type": config.specialist_type,
                "component_id": config.component_id,
                "status": config.status,
                "has_socket": socket_id is not None,
                "socket_state": socket_info["state"] if socket_info else None,
                "capabilities": config.capabilities
            })
        
        return specialists
    
    async def health_check_specialists(self) -> Dict[str, bool]:
        """Check health of all specialist sockets.
        
        Returns:
            Dict of specialist_id -> is_healthy
        """
        health_status = {}
        
        for specialist_id, socket_id in self.specialist_sockets.items():
            socket_info = await self.socket_registry.get_socket_info(socket_id)
            is_healthy = socket_info and socket_info["state"] == "active"
            health_status[specialist_id] = is_healthy
            
            if not is_healthy:
                logger.warning(f"Specialist {specialist_id} socket is unhealthy")
        
        return health_status


# Singleton instance
_integration_instance: Optional[SocketSpecialistIntegration] = None


async def get_socket_specialist_integration(specialist_manager: AISpecialistManager) -> SocketSpecialistIntegration:
    """Get the singleton integration instance.
    
    Args:
        specialist_manager: The AI specialist manager
        
    Returns:
        The initialized integration
    """
    global _integration_instance
    
    if _integration_instance is None:
        _integration_instance = SocketSpecialistIntegration(specialist_manager)
        await _integration_instance.initialize()
    
    return _integration_instance