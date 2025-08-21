"""
MCP Tool Registration Utilities for Tekton Components.

This module provides common utilities for managing MCP tools across
Tekton components.
"""

import logging
import inspect
from typing import Any, Dict, List, Optional, Union, Callable

from tekton.mcp.fastmcp import (
    adapt_tool,
    adapt_processor
)
from tekton.mcp.fastmcp.schema import (
    MCPTool,
    MCPCapability
)

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Simple registry for MCP tools and capabilities."""
    
    def __init__(self, component_name: str):
        """
        Initialize the tool registry.
        
        Args:
            component_name: Name of the component
        """
        self.component_name = component_name
        self.tools = {}
        self.capabilities = {}
        
    async def register_tool(self, tool_spec: Dict[str, Any]) -> str:
        """
        Register a tool with the registry.
        
        Args:
            tool_spec: Tool specification
            
        Returns:
            Tool ID
        """
        tool_id = tool_spec.get("id") or tool_spec.get("name")
        if not tool_id:
            raise ValueError("Tool specification missing ID or name")
            
        self.tools[tool_id] = tool_spec
        logger.debug(f"Registered tool {tool_id} for {self.component_name}")
        return tool_id
        
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Get all registered tools.
        
        Returns:
            List of tool specifications
        """
        return list(self.tools.values())
        
    async def register_capability(self, capability_spec: Dict[str, Any]) -> str:
        """
        Register a capability with the registry.
        
        Args:
            capability_spec: Capability specification
            
        Returns:
            Capability ID
        """
        capability_id = capability_spec.get("id") or capability_spec.get("name")
        if not capability_id:
            raise ValueError("Capability specification missing ID or name")
            
        self.capabilities[capability_id] = capability_spec
        logger.debug(f"Registered capability {capability_id} for {self.component_name}")
        return capability_id
        
    def get_all_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get all registered capabilities.
        
        Returns:
            List of capability specifications
        """
        return list(self.capabilities.values())


def create_tool_registry(component_name: str) -> ToolRegistry:
    """
    Create a tool registry for a component.
    
    Args:
        component_name: Name of the component
        
    Returns:
        Initialized tool registry
    """
    return ToolRegistry(component_name)


async def register_tools(
    registry: ToolRegistry,
    tools: List[Callable],
    component_manager: Any
) -> None:
    """
    Register multiple tools with a registry.
    
    Args:
        registry: Tool registry
        tools: List of tool functions
        component_manager: Component manager instance
    """
    for tool_func in tools:
        # Skip non-callables
        if not callable(tool_func):
            continue
            
        # Check if the function has MCP tool metadata
        if not hasattr(tool_func, "_mcp_tool_meta"):
            logger.warning(f"Tool {tool_func.__name__} missing MCP metadata")
            continue
            
        try:
            # Adapt the tool with the component manager
            adapted_tool = adapt_tool(tool_func, component_manager=component_manager)
            
            # Register the tool
            await registry.register_tool(adapted_tool._mcp_tool_meta.to_dict())
        except Exception as e:
            logger.error(f"Error registering tool {tool_func.__name__}: {e}")


def get_component_tools(
    component_module_path: str,
    component_manager: Any
) -> List[MCPTool]:
    """
    Get all MCP tools from a component.
    
    Args:
        component_module_path: Import path to the component's MCP module
        component_manager: Component manager instance
        
    Returns:
        List of MCP tools
    """
    try:
        # Import the component's MCP module
        module = __import__(component_module_path, fromlist=["get_tools"])
        
        # Check if the module has a get_tools function
        if hasattr(module, "get_tools") and callable(module.get_tools):
            return module.get_tools(component_manager)
        else:
            logger.warning(f"Component module {component_module_path} missing get_tools function")
            return []
    except ImportError as e:
        logger.error(f"Error importing component module {component_module_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error getting component tools from {component_module_path}: {e}")
        return []