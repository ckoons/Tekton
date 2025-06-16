"""
MCP Tools Integration Module for Rhetor.

This module provides the integration layer between MCP tools and live Rhetor components,
replacing mock implementations with actual functionality.
"""

import logging
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

from rhetor.core.ai_specialist_manager import AISpecialistManager
from rhetor.core.ai_messaging_integration import AIMessagingIntegration

# Ensure Hermes is in the Python path for clean imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
hermes_path = os.path.join(tekton_root, 'Hermes')
if os.path.exists(hermes_path) and hermes_path not in sys.path:
    sys.path.insert(0, hermes_path)

# Import Hermes message bus - handle import error gracefully
try:
    # Try direct import (works when Hermes is in sys.path)
    from hermes.core.message_bus import MessageBus
except ImportError:
    try:
        # Fallback to full path (works when Tekton root is in sys.path)
        from Hermes.hermes.core.message_bus import MessageBus
    except ImportError:
        MessageBus = None
        import logging
        logging.getLogger(__name__).warning("Hermes MessageBus not available - inter-component messaging disabled")

logger = logging.getLogger(__name__)


class MCPToolsIntegration:
    """
    Integration layer connecting MCP tools to live Rhetor components.
    
    This class provides real implementations for MCP tool functions,
    replacing mock data with actual component interactions.
    """
    
    def __init__(self, 
                 specialist_manager: Optional[AISpecialistManager] = None,
                 messaging_integration: Optional[AIMessagingIntegration] = None,
                 hermes_url: str = "http://localhost:8001"):
        """
        Initialize MCP tools integration.
        
        Args:
            specialist_manager: AI specialist manager instance
            messaging_integration: AI messaging integration instance
            hermes_url: Hermes service URL
        """
        self.specialist_manager = specialist_manager
        self.messaging_integration = messaging_integration
        self.hermes_url = hermes_url
        self.message_bus = None
        
        # Initialize Hermes message bus connection
        self._initialize_message_bus()
        
        logger.info("MCP Tools Integration initialized")
        
    def _initialize_message_bus(self):
        """Initialize connection to Hermes message bus."""
        if MessageBus is None:
            logger.warning("MessageBus class not available, skipping message bus initialization")
            self.message_bus = None
            return
            
        try:
            self.message_bus = MessageBus(
                host="localhost",
                port=5555,
                config={"history_size": 100}
            )
            self.message_bus.connect()
            logger.info("Connected to Hermes message bus")
        except Exception as e:
            logger.error(f"Failed to connect to Hermes message bus: {e}")
            self.message_bus = None
    
    # AI Orchestration Tool Implementations
    
    async def list_ai_specialists(self,
                                  filter_by_status: Optional[str] = None,
                                  filter_by_type: Optional[str] = None,
                                  filter_by_component: Optional[str] = None) -> Dict[str, Any]:
        """
        List available AI specialists and their current status (live implementation).
        
        Args:
            filter_by_status: Filter by status
            filter_by_type: Filter by specialist type
            filter_by_component: Filter by component ID
            
        Returns:
            Dictionary containing list of AI specialists
        """
        try:
            if not self.specialist_manager:
                return {
                    "success": False,
                    "error": "Specialist manager not initialized"
                }
            
            # Get all specialists from the manager
            specialists_data = []
            for spec_id, config in self.specialist_manager.specialists.items():
                # Get specialist status
                status = await self.specialist_manager.get_specialist_status(spec_id)
                
                specialist_info = {
                    "specialist_id": spec_id,
                    "specialist_type": config.specialist_type,
                    "component_id": config.component_id,
                    "status": status.get("status", "unknown"),
                    "model": config.model_config.get("model", "unknown"),
                    "capabilities": config.capabilities,
                    "active_conversations": len(status.get("active_conversations", [])),
                    "last_activity": status.get("last_activity")
                }
                
                # Apply filters
                if filter_by_status and specialist_info["status"] != filter_by_status:
                    continue
                if filter_by_type and specialist_info["specialist_type"] != filter_by_type:
                    continue
                if filter_by_component and specialist_info["component_id"] != filter_by_component:
                    continue
                    
                specialists_data.append(specialist_info)
            
            # Calculate statistics
            stats = {
                "total": len(specialists_data),
                "active": len([s for s in specialists_data if s["status"] == "active"]),
                "inactive": len([s for s in specialists_data if s["status"] == "inactive"]),
                "by_component": {}
            }
            
            for specialist in specialists_data:
                component = specialist["component_id"]
                if component not in stats["by_component"]:
                    stats["by_component"][component] = 0
                stats["by_component"][component] += 1
            
            return {
                "success": True,
                "specialists": specialists_data,
                "statistics": stats,
                "filters_applied": {
                    "status": filter_by_status,
                    "type": filter_by_type,
                    "component": filter_by_component
                },
                "message": f"Found {len(specialists_data)} AI specialists"
            }
            
        except Exception as e:
            logger.error(f"Error listing AI specialists: {e}")
            return {
                "success": False,
                "error": f"Failed to list AI specialists: {str(e)}"
            }
    
    async def activate_ai_specialist(self,
                                     specialist_id: str,
                                     initialization_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Activate an AI specialist for use (live implementation).
        
        Args:
            specialist_id: ID of the specialist to activate
            initialization_context: Optional context for initialization
            
        Returns:
            Dictionary containing activation result
        """
        try:
            if not self.specialist_manager:
                return {
                    "success": False,
                    "error": "Specialist manager not initialized"
                }
            
            # Check if specialist exists
            if specialist_id not in self.specialist_manager.specialists:
                return {
                    "success": False,
                    "error": f"Specialist {specialist_id} not found"
                }
            
            # Activate the specialist
            activation_result = await self.specialist_manager.activate_specialist(
                specialist_id,
                initialization_context
            )
            
            return {
                "success": activation_result.get("success", False),
                "activation_result": activation_result,
                "message": f"AI specialist {specialist_id} {'activated successfully' if activation_result.get('success') else 'activation failed'}"
            }
            
        except Exception as e:
            logger.error(f"Error activating AI specialist: {e}")
            return {
                "success": False,
                "error": f"Failed to activate AI specialist: {str(e)}"
            }
    
    async def send_message_to_specialist(self,
                                         specialist_id: str,
                                         message: str,
                                         context_id: Optional[str] = None,
                                         message_type: str = "chat") -> Dict[str, Any]:
        """
        Send a message to a specific AI specialist (live implementation).
        
        Args:
            specialist_id: ID of the target specialist
            message: Message content
            context_id: Optional context ID
            message_type: Type of message
            
        Returns:
            Dictionary containing message result
        """
        try:
            if not self.messaging_integration:
                return {
                    "success": False,
                    "error": "Messaging integration not initialized"
                }
            
            # Determine if this is a cross-component message
            specialist_config = self.specialist_manager.specialists.get(specialist_id)
            if not specialist_config:
                return {
                    "success": False,
                    "error": f"Specialist {specialist_id} not found"
                }
            
            # Send the message
            if specialist_config.component_id != "rhetor":
                # Cross-component message - use Hermes
                await self.messaging_integration.send_specialist_message(
                    from_specialist="rhetor-orchestrator",
                    to_specialist=specialist_id,
                    content=message,
                    context={
                        "context_id": context_id,
                        "message_type": message_type
                    }
                )
                
                # Return success for cross-component messages
                return {
                    "success": True,
                    "message_id": f"cross-component-{datetime.now().timestamp()}",
                    "specialist_id": specialist_id,
                    "response": {
                        "status": "sent_via_hermes",
                        "timestamp": datetime.now().isoformat()
                    },
                    "context_id": context_id or f"default_{specialist_id}",
                    "message": f"Message sent to {specialist_id} via Hermes successfully"
                }
            else:
                # Internal message
                message_id = await self.specialist_manager.send_message(
                    sender_id="user",
                    receiver_id=specialist_id,
                    content=message,
                    message_type=message_type
                )
                
                return {
                    "success": True,
                    "message_id": message_id,
                    "specialist_id": specialist_id,
                    "response": {
                        "message_id": message_id,
                        "status": "sent",
                        "timestamp": datetime.now().isoformat()
                    },
                    "context_id": context_id or f"default_{specialist_id}",
                    "message": f"Message sent to {specialist_id} successfully"
                }
            
        except Exception as e:
            logger.error(f"Error sending message to specialist: {e}")
            return {
                "success": False,
                "error": f"Failed to send message to specialist: {str(e)}"
            }
    
    async def orchestrate_team_chat(self,
                                    topic: str,
                                    specialists: List[str],
                                    initial_prompt: str,
                                    max_rounds: int = 3,
                                    orchestration_style: str = "collaborative") -> Dict[str, Any]:
        """
        Orchestrate a team chat between multiple AI specialists (live implementation).
        
        Args:
            topic: Discussion topic
            specialists: List of specialist IDs
            initial_prompt: Initial prompt
            max_rounds: Maximum rounds
            orchestration_style: Style of orchestration
            
        Returns:
            Dictionary containing team chat results
        """
        try:
            if not self.messaging_integration:
                return {
                    "success": False,
                    "error": "Messaging integration not initialized"
                }
            
            # Validate specialists exist
            valid_specialists = []
            for spec_id in specialists:
                if spec_id in self.specialist_manager.specialists:
                    valid_specialists.append(spec_id)
                else:
                    logger.warning(f"Specialist {spec_id} not found, skipping")
            
            if len(valid_specialists) < 2:
                return {
                    "success": False,
                    "error": "At least 2 valid specialists required for team chat"
                }
            
            # Use the messaging integration to orchestrate the chat
            messages = await self.messaging_integration.orchestrate_team_chat(
                topic=topic,
                specialists=valid_specialists,
                initial_prompt=initial_prompt,
                max_rounds=max_rounds
            )
            
            # Extract summary from the conversation
            summary = {
                "key_insights": [],
                "next_steps": [],
                "consensus_reached": len(messages) > 0
            }
            
            # Analyze messages for insights
            for msg in messages[-3:]:  # Look at last 3 messages
                if "insight" in msg.get("content", "").lower():
                    summary["key_insights"].append(msg["content"][:100])
                if "next" in msg.get("content", "").lower() or "action" in msg.get("content", "").lower():
                    summary["next_steps"].append(msg["content"][:100])
            
            return {
                "success": True,
                "topic": topic,
                "participants": valid_specialists,
                "conversation": messages,
                "total_messages": len(messages),
                "rounds_completed": min(max_rounds, len(messages) // len(valid_specialists)),
                "orchestration_style": orchestration_style,
                "summary": summary,
                "message": f"Team chat completed successfully with {len(valid_specialists)} specialists"
            }
            
        except Exception as e:
            logger.error(f"Error orchestrating team chat: {e}")
            return {
                "success": False,
                "error": f"Failed to orchestrate team chat: {str(e)}"
            }
    
    async def get_specialist_conversation_history(self,
                                                  specialist_id: str,
                                                  conversation_id: Optional[str] = None,
                                                  limit: int = 10) -> Dict[str, Any]:
        """
        Get conversation history for an AI specialist (live implementation).
        
        Args:
            specialist_id: ID of the specialist
            conversation_id: Optional conversation ID
            limit: Maximum messages to return
            
        Returns:
            Dictionary containing conversation history
        """
        try:
            if not self.specialist_manager:
                return {
                    "success": False,
                    "error": "Specialist manager not initialized"
                }
            
            # Get conversation history from the specialist manager
            history = await self.specialist_manager.get_conversation_history(
                specialist_id=specialist_id,
                conversation_id=conversation_id,
                limit=limit
            )
            
            return {
                "success": True,
                "specialist_id": specialist_id,
                "conversation_id": conversation_id,
                "messages": history.get("messages", []),
                "total_messages": len(history.get("messages", [])),
                "message": f"Retrieved {len(history.get('messages', []))} messages for {specialist_id}"
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return {
                "success": False,
                "error": f"Failed to get conversation history: {str(e)}"
            }
    
    async def configure_ai_orchestration(self,
                                         settings: Dict[str, Any],
                                         apply_immediately: bool = True) -> Dict[str, Any]:
        """
        Configure AI orchestration settings (live implementation).
        
        Args:
            settings: Configuration settings
            apply_immediately: Whether to apply immediately
            
        Returns:
            Dictionary containing configuration result
        """
        try:
            if not self.specialist_manager:
                return {
                    "success": False,
                    "error": "Specialist manager not initialized"
                }
            
            # Get current settings
            current_settings = await self.specialist_manager.get_orchestration_settings()
            
            # Validate and apply new settings
            applied_settings = {}
            validation_errors = []
            
            valid_settings = {
                "message_filtering": ["enabled", "disabled"],
                "auto_translation": ["enabled", "disabled"],
                "orchestration_mode": ["collaborative", "directive", "autonomous"],
                "specialist_allocation": ["dynamic", "static", "hybrid"],
                "max_concurrent_specialists": range(1, 11),
                "default_model_selection": ["performance", "cost", "balanced"]
            }
            
            for key, value in settings.items():
                if key in valid_settings:
                    if isinstance(valid_settings[key], list):
                        if value in valid_settings[key]:
                            applied_settings[key] = value
                        else:
                            validation_errors.append(f"Invalid value for {key}: {value}")
                    elif isinstance(valid_settings[key], range):
                        if value in valid_settings[key]:
                            applied_settings[key] = value
                        else:
                            validation_errors.append(f"Invalid value for {key}: {value}")
                else:
                    validation_errors.append(f"Unknown setting: {key}")
            
            if validation_errors:
                return {
                    "success": False,
                    "errors": validation_errors,
                    "message": "Configuration validation failed"
                }
            
            # Apply settings
            if apply_immediately:
                await self.specialist_manager.update_orchestration_settings(applied_settings)
            
            # Calculate changes
            changes = {}
            for key, value in applied_settings.items():
                if current_settings.get(key) != value:
                    changes[key] = {
                        "old": current_settings.get(key),
                        "new": value
                    }
            
            return {
                "success": True,
                "applied_settings": applied_settings,
                "changes": changes,
                "apply_immediately": apply_immediately,
                "effective_time": datetime.now().isoformat() if apply_immediately else "on_next_restart",
                "message": "AI orchestration configuration updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error configuring AI orchestration: {e}")
            return {
                "success": False,
                "error": f"Failed to configure AI orchestration: {str(e)}"
            }


# Global instance for MCP tools to use
_mcp_tools_integration = None


def get_mcp_tools_integration() -> MCPToolsIntegration:
    """Get the global MCP tools integration instance."""
    global _mcp_tools_integration
    if _mcp_tools_integration is None:
        logger.warning("MCP tools integration not initialized, creating placeholder")
        _mcp_tools_integration = MCPToolsIntegration()
    return _mcp_tools_integration


def set_mcp_tools_integration(integration: MCPToolsIntegration):
    """Set the global MCP tools integration instance."""
    global _mcp_tools_integration
    _mcp_tools_integration = integration
    logger.info("MCP tools integration instance set")