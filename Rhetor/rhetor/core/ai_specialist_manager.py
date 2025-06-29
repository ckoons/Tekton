"""
AI Specialist Manager - DEPRECATED

This module has been replaced by the unified AI Registry system.
All AI specialist management is now handled through:
- shared/ai/registry_client.py
- shared/ai/ai_discovery_service.py
- Rhetor/rhetor/api/ai_specialist_endpoints_unified.py

This file is kept as a stub to prevent import errors during migration.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AIMessage:
    """DEPRECATED - Message structure for AI-to-AI communication."""
    message_id: str
    sender_id: str
    receiver_id: str
    content: str
    message_type: str
    context: Dict[str, Any]
    timestamp: float


class AISpecialistManager:
    """DEPRECATED - Stub class for backward compatibility during migration."""
    
    def __init__(self, *args, **kwargs):
        logger.warning("AISpecialistManager is deprecated. Use AI Registry instead.")
        self.specialists = {}
    
    async def list_specialists(self) -> List[Dict[str, Any]]:
        """DEPRECATED - Use AI Registry instead."""
        logger.warning("AISpecialistManager.list_specialists() is deprecated")
        return []
    
    async def get_specialist(self, specialist_id: str) -> Optional[Dict[str, Any]]:
        """DEPRECATED - Use AI Registry instead."""
        logger.warning("AISpecialistManager.get_specialist() is deprecated")
        return None
    
    async def start_specialist(self, specialist_id: str) -> Dict[str, Any]:
        """DEPRECATED - Use AI Registry instead."""
        logger.warning("AISpecialistManager.start_specialist() is deprecated")
        return {"success": False, "error": "Deprecated - use AI Registry"}
    
    async def stop_specialist(self, specialist_id: str) -> Dict[str, Any]:
        """DEPRECATED - Use AI Registry instead."""
        logger.warning("AISpecialistManager.stop_specialist() is deprecated") 
        return {"success": False, "error": "Deprecated - use AI Registry"}
    
    async def create_specialist(self, specialist_id: str) -> bool:
        """DEPRECATED - Use AI Registry instead."""
        logger.warning("AISpecialistManager.create_specialist() is deprecated")
        return False
    
    async def start_core_specialists(self) -> Dict[str, bool]:
        """DEPRECATED - Use AI Registry instead."""
        logger.warning("AISpecialistManager.start_core_specialists() is deprecated")
        return {}
    
    def set_socket_integration(self, socket_integration):
        """DEPRECATED - No longer needed."""
        pass


# Singleton instance management (deprecated)
_manager_instance: Optional[AISpecialistManager] = None


def get_ai_specialist_manager() -> Optional[AISpecialistManager]:
    """DEPRECATED - Get the singleton AI specialist manager instance."""
    logger.warning("get_ai_specialist_manager() is deprecated. Use AI Registry instead.")
    return _manager_instance


def set_ai_specialist_manager(manager: AISpecialistManager):
    """DEPRECATED - Set the singleton AI specialist manager instance."""
    global _manager_instance
    _manager_instance = manager