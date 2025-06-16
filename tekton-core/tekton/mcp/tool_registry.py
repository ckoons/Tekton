"""
Tool Registry - Registry for MCP tools and their capabilities.

This module provides a registry for MCP tools, allowing them to
advertise their capabilities and be discovered by clients.
"""

import time
import uuid
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Callable, Union

logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    Registry for MCP tools and their capabilities.
    
    This class provides methods for registering tools, discovering
    tools, and executing tool functions.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._callbacks: Dict[str, List[Callable[[str, Dict[str, Any]], None]]] = {
            "registered": [],
            "executed": []
        }
        
        logger.info("Tool registry initialized")
    
    async def register_tool(
        self,
        tool_spec: Dict[str, Any]
    ) -> str:
        """
        Register a tool with the registry.
        
        Args:
            tool_spec: Tool specification
            
        Returns:
            Tool ID
        """
        # Validate tool spec
        required_fields = ["name", "description", "schema"]
        for field in required_fields:
            if field not in tool_spec:
                raise ValueError(f"Tool spec missing required field: {field}")
                
        # Generate ID if not provided
        tool_id = tool_spec.get("id") or f"tool-{uuid.uuid4()}"
        
        # Add registration metadata
        tool_spec["id"] = tool_id
        tool_spec["registered_at"] = time.time()
        
        # Store tool
        self.tools[tool_id] = tool_spec
        logger.info(f"Registered tool: {tool_spec['name']} ({tool_id})")
        
        # Trigger registered callbacks
        for callback in self._callbacks["registered"]:
            try:
                callback(tool_id, tool_spec)
            except Exception as e:
                logger.error(f"Error in tool registered callback: {e}")
        
        return tool_id
    
    async def unregister_tool(self, tool_id: str) -> bool:
        """
        Unregister a tool from the registry.
        
        Args:
            tool_id: Tool ID to unregister
            
        Returns:
            True if unregistration successful
        """
        if tool_id in self.tools:
            tool = self.tools[tool_id]
            del self.tools[tool_id]
            logger.info(f"Unregistered tool: {tool['name']} ({tool_id})")
            return True
            
        logger.warning(f"Tool not found in registry: {tool_id}")
        return False
    
    async def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a tool by ID.
        
        Args:
            tool_id: Tool ID to retrieve
            
        Returns:
            Tool specification or None if not found
        """
        return self.tools.get(tool_id)
    
    async def find_tools_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """
        Find tools with a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of tools with the requested capability
        """
        matching_tools = []
        
        for tool_id, tool in self.tools.items():
            # Check capabilities in tool tags
            tags = tool.get("tags", [])
            if capability in tags:
                matching_tools.append(tool)
                continue
                
            # Check capabilities in tool metadata
            metadata = tool.get("metadata", {})
            capabilities = metadata.get("capabilities", [])
            if capability in capabilities:
                matching_tools.append(tool)
                continue
                
            # Check if the capability is in the name or description
            if (capability.lower() in tool.get("name", "").lower() or 
                capability.lower() in tool.get("description", "").lower()):
                matching_tools.append(tool)
        
        return matching_tools
    
    async def find_tools_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """
        Find tools with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of tools with the requested tag
        """
        matching_tools = []
        
        for tool_id, tool in self.tools.items():
            tags = tool.get("tags", [])
            if tag in tags:
                matching_tools.append(tool)
        
        return matching_tools
    
    async def execute_tool(
        self,
        tool_id: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool.
        
        Args:
            tool_id: ID of the tool to execute
            parameters: Parameters for the tool
            
        Returns:
            Tool execution result
        """
        # Check if tool exists
        if tool_id not in self.tools:
            error_result = {
                "success": False,
                "error": f"Tool not found: {tool_id}"
            }
            logger.warning(error_result["error"])
            return error_result
            
        tool = self.tools[tool_id]
        
        # Check if the tool has a function
        if "function" not in tool:
            error_result = {
                "success": False,
                "error": f"Tool {tool_id} has no executable function"
            }
            logger.warning(error_result["error"])
            return error_result
            
        # Get the function
        func = tool["function"]
        
        try:
            # Execute the function
            start_time = time.time()
            
            # Check if function is coroutine
            if asyncio.iscoroutinefunction(func):
                result = await func(**parameters)
            else:
                result = func(**parameters)
                
            execution_time = time.time() - start_time
            
            # Create result
            execution_result = {
                "success": True,
                "tool_id": tool_id,
                "tool_name": tool["name"],
                "result": result,
                "execution_time": execution_time
            }
            
            # Trigger executed callbacks
            for callback in self._callbacks["executed"]:
                try:
                    callback(tool_id, {
                        "success": True,
                        "parameters": parameters,
                        "result": result,
                        "execution_time": execution_time
                    })
                except Exception as e:
                    logger.error(f"Error in tool executed callback: {e}")
            
            return execution_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "tool_id": tool_id,
                "tool_name": tool["name"],
                "error": str(e)
            }
            logger.error(f"Error executing tool {tool_id}: {e}")
            
            # Trigger executed callbacks with error
            for callback in self._callbacks["executed"]:
                try:
                    callback(tool_id, {
                        "success": False,
                        "parameters": parameters,
                        "error": str(e)
                    })
                except Exception as e:
                    logger.error(f"Error in tool executed callback: {e}")
            
            return error_result
    
    async def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered tools.
        
        Returns:
            Dictionary of all tools
        """
        return self.tools.copy()
    
    def on_registered(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Register a callback for tool registration events.
        
        Args:
            callback: Function to call when a tool is registered
        """
        self._callbacks["registered"].append(callback)
    
    def on_executed(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Register a callback for tool execution events.
        
        Args:
            callback: Function to call when a tool is executed
        """
        self._callbacks["executed"].append(callback)


# Global tool registry instance for convenience functions
_global_registry: Optional[ToolRegistry] = None

def get_registry() -> ToolRegistry:
    """
    Get the global tool registry, creating it if needed.
    
    Returns:
        Global ToolRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry

async def register_tool(tool_spec: Dict[str, Any]) -> str:
    """
    Register a tool with the global registry.
    
    Args:
        tool_spec: Tool specification
        
    Returns:
        Tool ID
    """
    registry = get_registry()
    return await registry.register_tool(tool_spec)

async def find_tools_by_capability(capability: str) -> List[Dict[str, Any]]:
    """
    Find tools with a specific capability using the global registry.
    
    Args:
        capability: Capability to search for
        
    Returns:
        List of tools with the requested capability
    """
    registry = get_registry()
    return await registry.find_tools_by_capability(capability)

async def execute_tool(tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool using the global registry.
    
    Args:
        tool_id: ID of the tool to execute
        parameters: Parameters for the tool
        
    Returns:
        Tool execution result
    """
    registry = get_registry()
    return await registry.execute_tool(tool_id, parameters)