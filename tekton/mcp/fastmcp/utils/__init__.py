"""
Shared MCP Utilities for Tekton Components.

This module provides common utilities to implement FastMCP integration
across all Tekton components, reducing duplication and standardizing
the approach.
"""

from .endpoints import create_mcp_router, include_mcp_router, add_standard_mcp_endpoints, add_mcp_endpoints
from .tooling import create_tool_registry, get_component_tools, register_tools
from .requests import process_mcp_request, validate_mcp_request
from .response import create_mcp_response

__all__ = [
    # Endpoint utilities
    "create_mcp_router",
    "include_mcp_router",
    "add_standard_mcp_endpoints",
    "add_mcp_endpoints",  # Alias for backward compatibility
    
    # Tool registration utilities
    "create_tool_registry",
    "get_component_tools",
    "register_tools",
    
    # Request handling utilities
    "process_mcp_request",
    "validate_mcp_request",
    
    # Response utilities
    "create_mcp_response"
]