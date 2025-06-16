"""
Hermes Bridge for Prometheus MCP Tools

This module bridges Prometheus's FastMCP tools with Hermes MCP aggregator,
allowing Prometheus's tools to be discoverable and executable through Hermes.
"""

import logging
from typing import Dict, Any, List, Optional
from shared.mcp import MCPService, MCPConfig
from shared.mcp.client import HermesMCPClient
from shared.mcp.tools import HealthCheckTool, ComponentInfoTool

logger = logging.getLogger(__name__)

class PrometheusMCPBridge(MCPService):
    """
    Bridge between Prometheus's FastMCP tools and Hermes MCP aggregator.
    
    This class allows Prometheus to register its tools with Hermes while
    maintaining the existing FastMCP implementation.
    """
    
    def __init__(self, planner=None, component_name: str = "prometheus"):
        """Initialize the Prometheus MCP Bridge."""
        super().__init__(component_name)
        self.planner = planner
        self.hermes_client = None
        self._fastmcp_tools = None
        
    async def initialize(self):
        """Initialize the MCP service and register with Hermes."""
        await super().initialize()
        
        # Create Hermes client
        config = MCPConfig.from_env(self.component_name)
        self.hermes_client = HermesMCPClient(
            hermes_url=config.hermes_url,
            component_name=self.component_name,
            auth_token=getattr(config, "auth_token", None)
        )
        
        # Load FastMCP tools
        try:
            from prometheus.core.mcp.tools import (
                planning_tools,
                resource_management_tools,
                retrospective_tools,
                improvement_tools
            )
            # Combine all tool lists
            self._fastmcp_tools = (
                planning_tools + 
                resource_management_tools + 
                retrospective_tools + 
                improvement_tools
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
            component_description="Strategic planning and project retrospective system"
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
                logger.error(f"Failed to register tool {tool.__name__}: {e}")
                
    async def register_fastmcp_tool(self, tool_func):
        """Register a single FastMCP tool with Hermes."""
        # Get tool metadata from the decorated function
        tool_name = f"{self.component_name}_{tool_func.__name__}"
        
        # Extract MCP metadata if available
        mcp_metadata = getattr(tool_func, '_mcp_metadata', {})
        description = mcp_metadata.get('description', tool_func.__doc__ or '')
        tags = mcp_metadata.get('tags', [])
        category = mcp_metadata.get('category', 'general')
        
        # Create handler that delegates to the tool function
        async def handler(parameters: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Call the tool function directly
                result = await tool_func(**parameters)
                return result
            except Exception as e:
                logger.error(f"Error executing tool {tool_func.__name__}: {e}")
                raise
                
        # Build input schema from function signature
        import inspect
        sig = inspect.signature(tool_func)
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else Any
            param_schema = {"type": "string"}  # Default type
            
            # Map Python types to JSON schema types
            if param_type == int:
                param_schema = {"type": "integer"}
            elif param_type == float:
                param_schema = {"type": "number"}
            elif param_type == bool:
                param_schema = {"type": "boolean"}
            elif param_type == dict or param_type == Dict:
                param_schema = {"type": "object"}
            elif param_type == list or param_type == List:
                param_schema = {"type": "array"}
                
            # Add description from docstring if available
            if tool_func.__doc__:
                # Simple extraction - could be improved
                param_schema["description"] = f"Parameter {param_name}"
                
            properties[param_name] = param_schema
            
            # Check if required
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
                
        input_schema = {
            "type": "object",
            "properties": properties,
            "required": required
        }
        
        # Register with Hermes
        if self.hermes_client:
            try:
                await self.hermes_client.register_tool(
                    name=tool_name,
                    description=description,
                    input_schema=input_schema,
                    output_schema={
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "result": {"type": "object"},
                            "error": {"type": "string"},
                            "message": {"type": "string"}
                        }
                    },
                    handler=handler,
                    metadata={
                        'category': category,
                        'tags': tags,
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
        """Get health status from Prometheus planner."""
        try:
            # Basic health check - can be expanded based on Prometheus internals
            return {
                "status": "healthy",
                "details": {
                    "planner_initialized": self.planner is not None,
                    "tools_loaded": len(self._fastmcp_tools) if self._fastmcp_tools else 0,
                    "capabilities": [
                        "planning",
                        "resource_management",
                        "retrospective_analysis",
                        "improvement_recommendations"
                    ]
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "details": {"error": str(e)}
            }
            
    async def shutdown(self):
        """Shutdown the MCP service and unregister from Hermes."""
        if self.hermes_client:
            # Get all registered tools
            tools_to_unregister = []
            
            # Add default tools
            tools_to_unregister.extend([
                f"{self.component_name}_health_check",
                f"{self.component_name}_component_info"
            ])
            
            # Add FastMCP tools
            if self._fastmcp_tools:
                for tool in self._fastmcp_tools:
                    tools_to_unregister.append(f"{self.component_name}_{tool.__name__}")
                    
            # Unregister all tools
            for tool_id in tools_to_unregister:
                try:
                    await self.hermes_client.unregister_tool(tool_id)
                    logger.info(f"Unregistered tool {tool_id} from Hermes")
                except Exception as e:
                    logger.error(f"Failed to unregister {tool_id}: {e}")
                    
        await super().shutdown()