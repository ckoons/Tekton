"""
Hermes Bridge for Metis MCP Tools

This module bridges Metis's FastMCP tools with Hermes MCP aggregator,
allowing Metis's tools to be discoverable and executable through Hermes.
"""

import logging
import os
from typing import Dict, Any, List, Optional
from shared.mcp import MCPService, MCPConfig
from shared.mcp.client import HermesMCPClient
from shared.mcp.tools import HealthCheckTool, ComponentInfoTool
from shared.utils.env_config import get_component_config

logger = logging.getLogger(__name__)

class MetisMCPBridge(MCPService):
    """
    Bridge between Metis's FastMCP tools and Hermes MCP aggregator.
    
    This class allows Metis to register its tools with Hermes while
    maintaining the existing FastMCP implementation.
    """
    
    def __init__(self, task_manager=None, component_name: str = "metis"):
        """Initialize the Metis MCP Bridge."""
        super().__init__(component_name)
        self.task_manager = task_manager
        self.hermes_client = None
        self._fastmcp_tools = None
        
    async def initialize(self):
        """Initialize the MCP service and register with Hermes."""
        await super().initialize()
        
        # Create Hermes client
        config = MCPConfig.from_env(self.component_name)
        component_config = get_component_config()
        metis_port = component_config.metis.port if hasattr(component_config, 'metis') else None
        
        self.hermes_client = HermesMCPClient(
            hermes_url=config.hermes_url,
            component_name=self.component_name,
            component_port=metis_port,
            auth_token=getattr(config, "auth_token", None)
        )
        
        # Load FastMCP tools
        try:
            from metis.core.mcp.tools import (
                task_management_tools,
                dependency_management_tools,
                analytics_tools,
                telos_integration_tools
            )
            # Combine all tool lists
            self._fastmcp_tools = (
                task_management_tools + 
                dependency_management_tools + 
                analytics_tools + 
                telos_integration_tools
            )
            logger.info(f"Loaded {len(self._fastmcp_tools)} FastMCP tools")
        except Exception as e:
            logger.error(f"Failed to load FastMCP tools: {e}")
            self._fastmcp_tools = []
            
        # Register tools with both local registry and Hermes
        await self.register_default_tools()
        await self.register_fastmcp_tools()
        
    async def register_default_tools(self):
        """Register standard tools like health check and component info."""
        # Health check tool
        health_tool = HealthCheckTool(self.component_name)
        health_tool.get_health_func = self._get_health_status
        await self.register_tool_with_hermes(health_tool)
        
        # Component info tool  
        info_tool = ComponentInfoTool(
            component_name=self.component_name,
            component_version="0.1.0",
            component_description="AI-powered task and project management system"
        )
        await self.register_tool_with_hermes(info_tool)
        
    async def register_fastmcp_tools(self):
        """Register FastMCP tools with Hermes."""
        if not self._fastmcp_tools:
            logger.warning("No FastMCP tools to register")
            return
            
        for tool in self._fastmcp_tools:
            try:
                # Create a wrapper that converts FastMCP tool to shared MCP format
                await self.register_fastmcp_tool(tool)
            except Exception as e:
                logger.error(f"Failed to register tool {tool.get('name', 'unknown')}: {e}")
                
    async def register_fastmcp_tool(self, fastmcp_tool: Dict[str, Any]):
        """Register a single FastMCP tool with Hermes."""
        tool_name = fastmcp_tool['name']  # Don't add prefix here, client will handle it
        
        # Register with Hermes
        if self.hermes_client:
            try:
                # Extract parameter schema
                input_schema = fastmcp_tool.get('parameters', {})
                
                await self.hermes_client.register_tool(
                    name=tool_name,
                    description=fastmcp_tool.get('description', ''),
                    input_schema=input_schema,
                    tags=['tasks', 'ai', 'management'],
                    metadata={
                        'category': 'task_management',
                        'fastmcp': True
                    }
                )
                logger.info(f"Registered tool {tool_name} with Hermes")
            except Exception as e:
                logger.error(f"Failed to register {tool_name} with Hermes: {e}")
                
    async def register_tool_with_hermes(self, tool):
        """Register a standard MCP tool with Hermes."""
        if not self.hermes_client:
            logger.warning("Hermes client not initialized")
            return
            
        tool_name = f"{self.component_name}_{tool.name}"
        
        try:
            await self.hermes_client.register_tool(
                name=tool_name,
                description=tool.description,
                input_schema=tool.get_input_schema(),
                output_schema=getattr(tool, "output_schema", {}),
                handler=tool,  # The tool itself is callable
                metadata=tool.get_metadata()
            )
            logger.info(f"Registered tool {tool_name} with Hermes")
        except Exception as e:
            logger.error(f"Failed to register {tool_name} with Hermes: {e}")
            
    async def _get_health_status(self) -> Dict[str, Any]:
        """Get health status from Metis task manager."""
        try:
            # Import here to avoid circular imports
            from metis.api.routes import task_manager as tm
            
            if tm:
                # Get task statistics
                all_tasks = await tm.list_tasks()
                
                # Calculate status summary
                status_counts = {}
                for task in all_tasks:
                    status_counts[task.status] = status_counts.get(task.status, 0) + 1
                
                return {
                    "status": "healthy",
                    "details": {
                        "total_tasks": len(all_tasks),
                        "status_breakdown": status_counts,
                        "task_manager_initialized": True
                    }
                }
            else:
                return {
                    "status": "starting",
                    "details": {"message": "Metis task manager initializing"}
                }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "details": {"error": str(e)}
            }
            
    async def shutdown(self):
        """Shutdown the MCP service and unregister from Hermes."""
        if self.hermes_client:
            try:
                await self.hermes_client.cleanup()
            except Exception as e:
                logger.error(f"Error during Hermes client cleanup: {e}")
                    
        await super().shutdown()