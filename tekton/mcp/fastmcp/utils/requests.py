"""
MCP Request Handling Utilities for Tekton Components.

This module provides common utilities for processing MCP requests
across Tekton components.
"""

import logging
import importlib
import inspect
from typing import Any, Dict, List, Optional, Union, Callable

from tekton.mcp.fastmcp.schema import (
    MCPRequest,
    MCPResponse
)

logger = logging.getLogger(__name__)

def validate_mcp_request(request: MCPRequest) -> Dict[str, Any]:
    """
    Validate an MCP request.
    
    Args:
        request: MCP request to validate
        
    Returns:
        Dictionary with validation result
    """
    errors = []
    
    # Check required fields
    if not request.tool:
        errors.append("Missing required field: 'tool'")
    
    # Check parameters (if tool schema is available)
    # This would require a tool registry to look up the schema
    
    if errors:
        return {
            "valid": False,
            "errors": errors
        }
    else:
        return {
            "valid": True
        }


async def process_mcp_request(
    component_manager: Any,
    request: MCPRequest,
    component_module_path: str
) -> MCPResponse:
    """
    Process an MCP request for a component.
    
    Args:
        component_manager: Component manager instance
        request: MCP request to process
        component_module_path: Import path to the component's MCP tools module
        
    Returns:
        MCP response
    """
    # Validate the request
    validation = validate_mcp_request(request)
    if not validation["valid"]:
        return MCPResponse(
            status="error",
            error=f"Invalid request: {', '.join(validation['errors'])}",
            result=None
        )
    
    try:
        # Get the tool name from the request
        tool_name = request.tool
        
        # Try to import the tool module
        try:
            module = importlib.import_module(component_module_path)
        except ImportError:
            return MCPResponse(
                status="error",
                error=f"Tool module {component_module_path} not found",
                result=None
            )
        
        # Find the tool implementation in the module
        tool_impl = None
        for name, obj in inspect.getmembers(module):
            if callable(obj) and hasattr(obj, "_mcp_tool_meta"):
                if obj._mcp_tool_meta.name == tool_name:
                    tool_impl = obj
                    break
        
        if not tool_impl:
            return MCPResponse(
                status="error",
                error=f"Tool '{tool_name}' not found in module {component_module_path}",
                result=None
            )
        
        # Call the tool with the component manager and request parameters
        result = await tool_impl(component_manager, **request.parameters)
        
        # Return the response
        return MCPResponse(
            status="success",
            error=None,
            result=result
        )
        
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        return MCPResponse(
            status="error",
            error=f"Error processing request: {str(e)}",
            result=None
        )