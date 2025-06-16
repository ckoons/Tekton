"""
Initialize MCP Tools Integration with Live Components.

This module sets up the integration between MCP tools and live Rhetor components,
enabling real AI orchestration functionality.
"""

import logging
from typing import Optional

from rhetor.core.ai_specialist_manager import AISpecialistManager
from rhetor.core.ai_messaging_integration import AIMessagingIntegration
from rhetor.core.mcp.tools_integration import set_mcp_tools_integration, MCPToolsIntegration

logger = logging.getLogger(__name__)


def initialize_mcp_integration(
    specialist_manager: AISpecialistManager,
    messaging_integration: AIMessagingIntegration,
    hermes_url: str = "http://localhost:8001"
) -> MCPToolsIntegration:
    """
    Initialize the MCP tools integration with live components.
    
    This function creates and configures the integration layer that connects
    MCP tools to the actual AISpecialistManager and AIMessagingIntegration.
    
    Args:
        specialist_manager: The AI specialist manager instance
        messaging_integration: The AI messaging integration instance
        hermes_url: URL of the Hermes service
        
    Returns:
        Configured MCPToolsIntegration instance
    """
    logger.info("Initializing MCP tools integration with live components")
    
    try:
        # Create the integration instance
        integration = MCPToolsIntegration(
            specialist_manager=specialist_manager,
            messaging_integration=messaging_integration,
            hermes_url=hermes_url
        )
        
        # Set it as the global instance for MCP tools
        set_mcp_tools_integration(integration)
        
        logger.info("MCP tools integration initialized successfully")
        return integration
        
    except Exception as e:
        logger.error(f"Failed to initialize MCP tools integration: {e}")
        raise


async def setup_hermes_subscriptions(integration: MCPToolsIntegration):
    """
    Set up Hermes message bus subscriptions for cross-component AI communication.
    
    Args:
        integration: The MCP tools integration instance
    """
    if not integration.message_bus:
        logger.warning("Message bus not available, skipping subscription setup")
        return
    
    try:
        # Subscribe to AI specialist topics
        topics = [
            "ai.specialist.rhetor.*",  # Messages for Rhetor specialists
            "ai.orchestration.*",      # Orchestration messages
            "ai.team_chat.*"          # Team chat messages
        ]
        
        for topic in topics:
            async def message_handler(message):
                """Handle incoming messages from Hermes."""
                try:
                    payload = message.get("payload", {})
                    headers = message.get("headers", {})
                    
                    logger.info(f"Received message on topic {headers.get('topic', 'unknown')}")
                    
                    # Route to appropriate handler based on topic
                    if "ai.specialist.rhetor" in headers.get("topic", ""):
                        # Handle specialist messages
                        await integration.messaging_integration.send_specialist_message(
                            from_specialist=payload.get("from", "unknown"),
                            to_specialist=payload.get("to", "unknown"),
                            content=payload.get("content", ""),
                            context=payload.get("context", {})
                        )
                    
                except Exception as e:
                    logger.error(f"Error handling Hermes message: {e}")
            
            # Subscribe to the topic
            success = await integration.message_bus.subscribe_async(topic, message_handler)
            if success:
                logger.info(f"Subscribed to Hermes topic: {topic}")
            else:
                logger.error(f"Failed to subscribe to topic: {topic}")
                
    except Exception as e:
        logger.error(f"Error setting up Hermes subscriptions: {e}")


async def test_mcp_integration(integration: MCPToolsIntegration):
    """
    Test the MCP tools integration to ensure it's working properly.
    
    Args:
        integration: The MCP tools integration instance
    """
    logger.info("Testing MCP tools integration...")
    
    try:
        # Test listing specialists
        result = await integration.list_ai_specialists()
        if result["success"]:
            logger.info(f"✓ List specialists: Found {result['statistics']['total']} specialists")
        else:
            logger.error(f"✗ List specialists failed: {result.get('error')}")
        
        # Test activating a specialist
        result = await integration.activate_ai_specialist("rhetor-orchestrator")
        if result["success"]:
            logger.info("✓ Activate specialist: rhetor-orchestrator activated")
        else:
            logger.error(f"✗ Activate specialist failed: {result.get('error')}")
        
        # Test configuration
        test_settings = {"orchestration_mode": "collaborative"}
        result = await integration.configure_ai_orchestration(test_settings)
        if result["success"]:
            logger.info("✓ Configure orchestration: Settings updated")
        else:
            logger.error(f"✗ Configure orchestration failed: {result.get('error')}")
        
        logger.info("MCP tools integration tests completed")
        
    except Exception as e:
        logger.error(f"Error testing MCP integration: {e}")