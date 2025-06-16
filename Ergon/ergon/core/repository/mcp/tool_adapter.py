"""
Tool adapter for MCP protocol.

This module provides adapters that convert Ergon tools to MCP-compatible formats
and handle execution of tools through MCP interfaces.
"""

import json
import logging
import inspect
from typing import Dict, Any, List, Callable, Optional, Union, Tuple

logger = logging.getLogger(__name__)

class MCPToolAdapter:
    """Adapter for converting tools to MCP-compatible formats."""
    
    @staticmethod
    def adapt_function_to_schema(
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Adapt a Python function to MCP tool schema.
        
        Args:
            func: Function to adapt
            name: Optional name override (uses function name by default)
            description: Optional description (uses docstring by default)
            
        Returns:
            MCP-compatible schema
        """
        # Get function signature
        sig = inspect.signature(func)
        
        # Extract function name and docstring
        func_name = name or func.__name__
        func_description = description or (func.__doc__ or "").strip()
        
        # Build schema
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            # Skip self in methods
            if param_name == "self" and len(sig.parameters) > 0:
                continue
                
            # Determine parameter type
            param_type = "string"  # Default
            
            # Check for annotations
            if param.annotation != inspect.Parameter.empty:
                if param.annotation in (str, Optional[str]):
                    param_type = "string"
                elif param.annotation in (int, Optional[int]):
                    param_type = "integer"
                elif param.annotation in (float, Optional[float]):
                    param_type = "number"
                elif param.annotation in (bool, Optional[bool]):
                    param_type = "boolean"
                elif param.annotation in (list, List, Optional[list], Optional[List]):
                    param_type = "array"
                elif param.annotation in (dict, Dict, Optional[dict], Optional[Dict]):
                    param_type = "object"
            
            # Create property
            param_property = {
                "type": param_type,
                "description": f"Parameter: {param_name}"
            }
            
            # Add default if available
            if param.default != inspect.Parameter.empty:
                param_property["default"] = param.default
            else:
                required.append(param_name)
                
            properties[param_name] = param_property
        
        # Create full schema
        schema = {
            "name": func_name,
            "description": func_description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
        
        return schema
    
    @staticmethod
    def execute_tool(
        tool_func: Callable,
        parameters: Dict[str, Any]
    ) -> Tuple[bool, Any]:
        """
        Execute a tool function with given parameters.
        
        Args:
            tool_func: Function to execute
            parameters: Parameters to pass to the function
            
        Returns:
            Tuple of (success, result)
        """
        try:
            result = tool_func(**parameters)
            return True, result
        except Exception as e:
            logger.error(f"Error executing tool: {str(e)}")
            return False, {"error": str(e)}


def adapt_tool_for_mcp(
    func: Callable,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    version: str = "0.1.0"
) -> Dict[str, Any]:
    """
    Adapt a Python function as an MCP-compatible tool.
    
    Args:
        func: Function to adapt
        name: Optional name override
        description: Optional description override
        tags: Optional tags for categorizing
        metadata: Optional additional metadata
        version: Tool version
        
    Returns:
        MCP-compatible tool definition
    """
    schema = MCPToolAdapter.adapt_function_to_schema(
        func=func,
        name=name,
        description=description
    )
    
    tool = {
        "name": schema["name"],
        "description": schema["description"],
        "schema": schema,
        "function": func,
        "tags": tags or [],
        "metadata": metadata or {},
        "version": version
    }
    
    return tool