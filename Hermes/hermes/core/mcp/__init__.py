"""
MCP Module - FastMCP implementation for Hermes.

This module provides a decorator-based MCP implementation for Hermes,
using the FastMCP integration from tekton-core.
"""

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
    
    fastmcp_available = True
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

# Import tool registry
from hermes.core.mcp.tools import (
    register_system_tools,
    register_database_tools,
    register_messaging_tools
)

# Import MCP service adapters
from hermes.core.mcp.adapters import (
    adapt_legacy_service
)

# Define exports
__all__ = [
    # FastMCP decorators
    "mcp_tool",
    "mcp_capability",
    "mcp_processor",
    "mcp_context",
    
    # Tool registry
    "register_system_tools",
    "register_database_tools",
    "register_messaging_tools",
    
    # Service adapters
    "adapt_legacy_service",
    
    # Availability flag
    "fastmcp_available"
]