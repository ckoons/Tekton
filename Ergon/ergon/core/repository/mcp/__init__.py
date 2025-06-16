"""
MCP integration for Ergon's tool repository.

This module provides integration between Ergon's tool repository and MCP (Model Control Protocol).
It allows external tools to be registered, validated, and used through the MCP interface.
"""

from .registration import register_tool, unregister_tool, update_tool_registry
from .tool_adapter import MCPToolAdapter, adapt_tool_for_mcp

__all__ = [
    "register_tool",
    "unregister_tool", 
    "update_tool_registry",
    "MCPToolAdapter",
    "adapt_tool_for_mcp"
]