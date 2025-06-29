"""
MCP Tools Integration Module for Rhetor - Unified with AI Registry.

This module provides the integration layer between MCP tools and the AI Registry,
replacing the old specialist manager with registry-based discovery.
"""

import logging
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_path)))))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from shared.ai.registry_client import AIRegistryClient
from shared.ai.ai_discovery_service import AIDiscoveryService

logger = logging.getLogger(__name__)


class MCPToolsIntegrationUnified:
    """
    Integration layer connecting MCP tools to the AI Registry.
    
    This class provides real implementations for MCP tool functions,
    using the AI Registry for specialist discovery and management.
    """
    
    def __init__(self, hermes_url: str = "http://localhost:8001"):
        """Initialize the MCP tools integration with AI Registry.
        
        Args:
            hermes_url: URL of the Hermes message bus
        """
        self.hermes_url = hermes_url
        self.registry = AIRegistryClient()
        self.discovery = AIDiscoveryService()
        logger.info("Initialized MCP tools integration with AI Registry")
    
    async def list_specialists(self) -> List[Dict[str, Any]]:
        """List all AI specialists from the registry.
        
        Returns:
            List of specialist information
        """
        try:
            result = await self.discovery.list_ais()
            return result.get('ais', [])
        except Exception as e:
            logger.error(f"Failed to list specialists: {e}")
            return []
    
    async def activate_specialist(self, specialist_id: str) -> Dict[str, Any]:
        """Activate an AI specialist (placeholder - specialists auto-start).
        
        Args:
            specialist_id: ID of the specialist
            
        Returns:
            Activation result
        """
        try:
            # Check if specialist exists
            ai_info = await self.discovery.get_ai_info(specialist_id)
            if not ai_info:
                return {"success": False, "error": f"Specialist {specialist_id} not found"}
            
            # Specialists auto-start with the platform, so just check status
            if ai_info.get('status') == 'healthy':
                return {
                    "success": True,
                    "message": f"Specialist {specialist_id} is already active"
                }
            else:
                return {
                    "success": False,
                    "error": f"Specialist {specialist_id} is not healthy: {ai_info.get('status')}"
                }
        except Exception as e:
            logger.error(f"Failed to activate specialist {specialist_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_message_to_specialist(self, specialist_id: str, message: str, 
                                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a message to an AI specialist.
        
        Args:
            specialist_id: ID of the specialist
            message: Message content
            context: Optional context
            
        Returns:
            Response from specialist
        """
        try:
            # Get specialist info
            ai_info = await self.discovery.get_ai_info(specialist_id)
            if not ai_info:
                return {"success": False, "error": f"Specialist {specialist_id} not found"}
            
            # TODO: Implement actual message sending via socket connection
            raise NotImplementedError(f"SendMessageToSpecialist not implemented for {specialist_id}")
        except Exception as e:
            logger.error(f"Failed to send message to {specialist_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_specialist_conversation_history(self, specialist_id: str, 
                                                limit: int = 10) -> Dict[str, Any]:
        """Get conversation history for a specialist.
        
        Args:
            specialist_id: ID of the specialist
            limit: Maximum number of messages
            
        Returns:
            Conversation history
        """
        # TODO: Implement actual history retrieval from Engram
        raise NotImplementedError(f"GetSpecialistConversationHistory not implemented for {specialist_id}")
    
    async def configure_orchestration(self, settings: Dict[str, Any]) -> bool:
        """Configure AI orchestration settings.
        
        Args:
            settings: New orchestration settings
            
        Returns:
            True if successful
        """
        # TODO: Implement orchestration configuration
        raise NotImplementedError("ConfigureOrchestration not implemented yet")


# Singleton instance
_integration_instance: Optional[MCPToolsIntegrationUnified] = None


def get_mcp_tools_integration() -> Optional[MCPToolsIntegrationUnified]:
    """Get the singleton MCP tools integration instance.
    
    Returns:
        The MCP tools integration instance or None if not initialized
    """
    return _integration_instance


def set_mcp_tools_integration(integration: MCPToolsIntegrationUnified):
    """Set the singleton MCP tools integration instance.
    
    Args:
        integration: The MCP tools integration instance
    """
    global _integration_instance
    _integration_instance = integration