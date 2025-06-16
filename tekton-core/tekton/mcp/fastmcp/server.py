"""
FastMCP Server - Lightweight MCP server utilities for Tekton components.

This module provides a simple FastMCP server implementation that acts as a
registry for tools and capabilities, designed for Tekton components that
need to expose MCP endpoints.
"""

import logging
from typing import Any, Dict, List, Optional, Type, Callable, Union

from tekton.mcp.fastmcp.schema import (
    MCPTool,
    MCPCapability,
    ToolSchema,
    CapabilitySchema
)
from tekton.mcp.fastmcp.exceptions import FastMCPError

logger = logging.getLogger(__name__)

class FastMCPServer:
    """
    Lightweight MCP server for Tekton components.
    
    This class provides a registry for tools and capabilities and utilities
    for creating MCP-compliant endpoints. It does NOT run an actual server,
    but provides the infrastructure for components to expose MCP functionality.
    """
    
    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        description: Optional[str] = None
    ):
        """
        Initialize FastMCP server.
        
        Args:
            name: Server name
            version: Server version
            description: Server description
        """
        self.name = name
        self.version = version
        self.description = description or f"FastMCP server for {name}"
        
        self._tools: Dict[str, MCPTool] = {}
        self._capabilities: Dict[str, MCPCapability] = {}
        self._tool_functions: Dict[str, Callable] = {}
        
        logger.info(f"Initialized FastMCP server: {name} v{version}")
    
    def register_tool(
        self,
        tool: Union[MCPTool, ToolSchema, Dict[str, Any]],
        function: Optional[Callable] = None
    ) -> None:
        """
        Register a tool with the server.
        
        Args:
            tool: Tool specification
            function: Optional function to execute the tool
        """
        # Convert to MCPTool if needed
        if isinstance(tool, dict):
            tool = MCPTool(**tool)
        elif isinstance(tool, ToolSchema):
            tool = tool  # MCPTool is an alias for ToolSchema
            
        tool_name = tool.name
        self._tools[tool_name] = tool
        
        if function:
            self._tool_functions[tool_name] = function
            
        logger.debug(f"Registered tool: {tool_name}")
    
    def register_capability(
        self,
        capability: Union[MCPCapability, CapabilitySchema, Dict[str, Any]]
    ) -> None:
        """
        Register a capability with the server.
        
        Args:
            capability: Capability specification
        """
        # Convert to MCPCapability if needed
        if isinstance(capability, dict):
            capability = MCPCapability(**capability)
        elif isinstance(capability, CapabilitySchema):
            capability = capability  # MCPCapability is an alias for CapabilitySchema
            
        cap_name = capability.name
        self._capabilities[cap_name] = capability
        
        logger.debug(f"Registered capability: {cap_name}")
    
    def get_tools(self) -> Dict[str, MCPTool]:
        """Get all registered tools."""
        return self._tools.copy()
    
    def get_capabilities(self) -> Dict[str, MCPCapability]:
        """Get all registered capabilities."""
        return self._capabilities.copy()
    
    def get_tool_function(self, tool_name: str) -> Optional[Callable]:
        """Get the function for a specific tool."""
        return self._tool_functions.get(tool_name)
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self._tools
    
    def has_capability(self, capability_name: str) -> bool:
        """Check if a capability is registered."""
        return capability_name in self._capabilities
    
    def list_tool_names(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self._tools.keys())
    
    def list_capability_names(self) -> List[str]:
        """Get list of all registered capability names."""
        return list(self._capabilities.keys())
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "tools": len(self._tools),
            "capabilities": len(self._capabilities)
        }

def register_tool_from_fn(
    function: Callable,
    name: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs
) -> MCPTool:
    """
    Create a tool registration from a function.
    
    Args:
        function: Function to register as a tool
        name: Tool name (defaults to function name)
        description: Tool description (defaults to function docstring)
        **kwargs: Additional tool parameters
        
    Returns:
        MCPTool instance
    """
    import inspect
    
    tool_name = name or function.__name__
    tool_description = description or function.__doc__ or f"Tool: {tool_name}"
    
    # Extract function signature for parameters
    sig = inspect.signature(function)
    parameters = {}
    
    for param_name, param in sig.parameters.items():
        param_info = {
            "type": "string",  # Default type
            "required": param.default == inspect.Parameter.empty
        }
        
        # Try to infer type from annotation
        if param.annotation != inspect.Parameter.empty:
            if param.annotation == int:
                param_info["type"] = "integer"
            elif param.annotation == float:
                param_info["type"] = "number"
            elif param.annotation == bool:
                param_info["type"] = "boolean"
            elif hasattr(param.annotation, "__origin__"):
                # Handle typing generics like List[str], Dict[str, Any], etc.
                param_info["type"] = "object"
        
        parameters[param_name] = param_info
    
    # Create tool schema
    tool_data = {
        "name": tool_name,
        "description": tool_description,
        "schema": {
            "parameters": parameters,
            "return_type": {"type": "object"}
        },
        **kwargs
    }
    
    return MCPTool(**tool_data)