"""
aish MCP module - Model Context Protocol server for aish

This module provides MCP endpoints for all aish functionality,
enabling external systems to interact with aish's messaging,
forwarding, and terminal integration features.
"""

from .server import mcp_router, fastmcp_server

__all__ = ["mcp_router", "fastmcp_server"]