"""
Tool Executor - Handles execution of Hermes' own tools.

This module provides a tool executor that can handle both local tools
(defined in Hermes itself) and remote tools (from other components).
"""

import logging
from typing import Dict, Any, Optional, Callable
import inspect

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes tools both local and remote."""
    
    def __init__(self):
        self.local_handlers: Dict[str, Callable] = {}
        self.service_registry = None
        self.database_manager = None
        self.message_bus = None
        
    def register_local_handler(self, tool_id: str, handler: Callable):
        """Register a local tool handler."""
        self.local_handlers[tool_id] = handler
        logger.debug(f"Registered local handler for tool: {tool_id}")
        
    def set_dependencies(self, service_registry=None, database_manager=None, message_bus=None):
        """Set dependencies for tool execution."""
        if service_registry:
            self.service_registry = service_registry
        if database_manager:
            self.database_manager = database_manager
        if message_bus:
            self.message_bus = message_bus
            
    async def execute_tool(self, tool_id: str, tool_info: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool, either locally or remotely."""
        try:
            # Check if this is a local tool
            if tool_id in self.local_handlers:
                return await self._execute_local_tool(tool_id, parameters)
            else:
                # Remote tool - check for endpoint
                endpoint = tool_info.get("endpoint")
                if not endpoint:
                    return {
                        "success": False,
                        "error": f"Tool {tool_id} has no endpoint and no local handler"
                    }
                    
                # This would be where we make HTTP requests to remote tools
                # For now, return a placeholder
                return {
                    "success": True,
                    "tool_id": tool_id,
                    "tool_name": tool_info.get("name", tool_id),
                    "result": {
                        "message": f"Remote tool {tool_id} would be executed via {endpoint}",
                        "parameters": parameters
                    },
                    "execution_time": 0.1
                }
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _execute_local_tool(self, tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a local tool handler."""
        handler = self.local_handlers[tool_id]
        
        try:
            # Inject dependencies based on function signature
            sig = inspect.signature(handler)
            injected_params = {}
            
            for param_name, param in sig.parameters.items():
                if param_name in parameters:
                    injected_params[param_name] = parameters[param_name]
                elif param_name == "service_registry" and self.service_registry:
                    injected_params[param_name] = self.service_registry
                elif param_name == "database_manager" and self.database_manager:
                    injected_params[param_name] = self.database_manager
                elif param_name == "message_bus" and self.message_bus:
                    injected_params[param_name] = self.message_bus
                elif param.default != inspect.Parameter.empty:
                    # Use default value
                    pass
                else:
                    # Required parameter not provided
                    raise ValueError(f"Missing required parameter: {param_name}")
                    
            # Execute the handler
            if inspect.iscoroutinefunction(handler):
                result = await handler(**injected_params)
            else:
                result = handler(**injected_params)
                
            logger.debug(f"Tool {tool_id} returned result type: {type(result)}, value: {result}")
                
            # Wrap result in standard format
            return {
                "success": True,
                "tool_id": tool_id,
                "tool_name": handler.__name__,
                "result": result,
                "execution_time": 0.1
            }
            
        except Exception as e:
            logger.error(f"Error executing local tool {tool_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }