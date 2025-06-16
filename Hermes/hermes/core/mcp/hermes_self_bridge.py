"""
Hermes Self-Registration Bridge

This module ensures Hermes registers its own MCP tools with itself,
making them discoverable through the same MCP aggregation interface
it provides to other components.
"""

import logging
from typing import Dict, Any, List, Optional
from shared.mcp import MCPService, MCPConfig
from shared.mcp.tools import HealthCheckTool, ComponentInfoTool

logger = logging.getLogger(__name__)

class HermesSelfBridge(MCPService):
    """
    Bridge for Hermes to register its own tools with itself.
    
    This creates a consistent experience where Hermes can be managed
    through the same MCP interface it provides to other components.
    """
    
    def __init__(self, service_registry, message_bus, registration_manager, database_manager=None, component_name: str = "hermes"):
        """Initialize the Hermes self-registration bridge."""
        super().__init__(component_name)
        self.service_registry = service_registry
        self.message_bus = message_bus
        self.registration_manager = registration_manager
        self.database_manager = database_manager
        self._internal_tools = None
        
    async def initialize(self):
        """Initialize and register Hermes's own tools."""
        await super().initialize()
        
        # Note: We don't use HermesMCPClient here to avoid circular dependency
        # Instead, we register tools directly with the local registry
        
        # Load Hermes's internal tools
        try:
            from hermes.core.mcp.tools import (
                get_system_tools,
                get_database_tools,
                get_messaging_tools
            )
            
            system_tools = get_system_tools(self.service_registry)
            messaging_tools = get_messaging_tools(self.message_bus)
            
            self._internal_tools = system_tools + messaging_tools
            
            if self.database_manager:
                database_tools = get_database_tools(self.database_manager)
                self._internal_tools.extend(database_tools)
                
            logger.info(f"Loaded {len(self._internal_tools)} internal Hermes tools")
        except Exception as e:
            logger.error(f"Failed to load internal tools: {e}")
            self._internal_tools = []
            
        # Register standard tools
        await self.register_default_tools()
        
        # Note: Since Hermes already registers its FastMCP tools internally,
        # this bridge mainly ensures consistent health/info tools and
        # provides a pattern for future enhancements
        
    async def register_default_tools(self):
        """Register standard tools like health check and component info."""
        # Health check tool
        health_tool = HealthCheckTool(self.component_name, health_check_func=self._get_health_status)
        
        # Register locally (not through HermesMCPClient to avoid circular dependency)
        await self.register_tool(
            name=f"{self.component_name}.health_check",
            description=health_tool.description,
            input_schema=health_tool.get_input_schema(),
            handler=health_tool.execute
        )
        
        # Component info tool  
        info_tool = ComponentInfoTool(
            component_name=self.component_name,
            component_version="0.2.0",
            component_description="Central registration, messaging, and MCP aggregation hub for Tekton"
        )
        
        await self.register_tool(
            name=f"{self.component_name}.component_info",
            description=info_tool.description,
            input_schema=info_tool.get_input_schema() if hasattr(info_tool, 'get_input_schema') else {"type": "object"},
            handler=info_tool.execute if hasattr(info_tool, 'execute') else info_tool
        )
        
        logger.info("Registered Hermes standard tools")
        
    async def _get_health_status(self) -> Dict[str, Any]:
        """Get health status from Hermes components."""
        try:
            # Check core services
            services_healthy = {
                "service_registry": self.service_registry is not None,
                "message_bus": self.message_bus is not None and self.message_bus._channels is not None,
                "registration_manager": self.registration_manager is not None,
                "database_manager": self.database_manager is not None if self.database_manager else True
            }
            
            # Count registered components
            registered_components = 0
            if self.registration_manager:
                registered_components = len(self.registration_manager.registrations)
            
            # Count message channels
            message_channels = 0
            if self.message_bus:
                message_channels = len(self.message_bus._channels)
            
            all_healthy = all(services_healthy.values())
            
            return {
                "status": "healthy" if all_healthy else "degraded",
                "details": {
                    "services": services_healthy,
                    "registered_components": registered_components,
                    "message_channels": message_channels,
                    "uptime_seconds": None  # Could be calculated if we track start time
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "details": {"error": str(e)}
            }
            
    async def shutdown(self):
        """Shutdown the self-registration bridge."""
        # Hermes tools are managed internally, so we just clean up the base
        await super().shutdown()
        logger.info("Hermes self-registration bridge shut down")