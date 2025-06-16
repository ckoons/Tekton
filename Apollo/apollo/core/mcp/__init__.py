"""
MCP Module - FastMCP implementation for Apollo.

This module provides a decorator-based MCP implementation for Apollo,
using the FastMCP integration from tekton-core.
"""

from shared.debug.debug_utils import debug_log, log_function
from typing import Dict, List, Any, Optional

# Import FastMCP integration if available
try:
    from tekton.mcp.fastmcp import (
        mcp_tool,
        mcp_capability,
        mcp_processor,
        mcp_context,
        adapt_tool,
        adapt_processor,
        adapt_context,
        MCPClient,
        register_component,
        get_capabilities
    )
    
    # Import schemas
    from tekton.mcp.fastmcp.schema import (
        ToolSchema,
        ProcessorSchema,
        CapabilitySchema,
        ContextSchema,
        MessageSchema,
        ResponseSchema,
        ContentSchema
    )
    
    # FastMCP registry access
    from tekton.mcp.fastmcp.registry import get_registered_tools as _get_registered_tools
    
    fastmcp_available = True
    
    @log_function()
    def get_tools() -> List[Dict[str, Any]]:
        """
        Get all registered MCP tools.
        
        Returns:
            List of registered tool schemas
        """
        try:
            registered_tools = _get_registered_tools()
            debug_log.info("apollo", f"Retrieved {len(registered_tools)} registered tools")
            return [tool.dict() for tool in registered_tools]
        except Exception as e:
            debug_log.error("apollo", f"Error retrieving registered tools: {str(e)}")
            return []
            
except ImportError:
    # Fall back to legacy implementation
    fastmcp_available = False
    
    # Define dummy decorators for backward compatibility
    def mcp_tool(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
        
    def mcp_capability(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
        
    def mcp_processor(*args, **kwargs):
        def decorator(cls):
            return cls
        return decorator
        
    def mcp_context(*args, **kwargs):
        def decorator(cls):
            return cls
        return decorator
            
    # Fallback implementation for get_tools
    def get_tools() -> List[Dict[str, Any]]:
        """
        Fallback implementation for get_tools when FastMCP is not available.
        
        Returns:
            Empty list (no tools available)
        """
        debug_log.warning("apollo", "FastMCP not available, returning empty tools list")
        return []

# Import MCP tools
from apollo.core.mcp.tools import (
    register_action_planning_tools,
    register_context_tools,
    register_message_tools,
    register_prediction_tools,
    register_protocol_tools,
    register_budget_tools,
    get_all_tools
)

# Define exports
__all__ = [
    # FastMCP decorators
    "mcp_tool",
    "mcp_capability",
    "mcp_processor",
    "mcp_context",
    
    # Tool registry
    "register_action_planning_tools",
    "register_context_tools",
    "register_message_tools",
    "register_prediction_tools",
    "register_protocol_tools",
    "register_budget_tools",
    "get_tools",
    "get_all_tools",
    
    # Availability flag
    "fastmcp_available"
]