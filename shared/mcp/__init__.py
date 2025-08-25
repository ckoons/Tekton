"""
Shared MCP (Model Context Protocol) implementation for Tekton components.

This package provides a standardized implementation of MCP v2 that all Tekton
components can use to expose tools and capabilities to CI assistants.

Key components:
- base: Base classes for MCP services and tools
- tools: Common tool implementations
- client: MCP client for connecting to Hermes
- config: Configuration helpers
- utils: Utility functions
"""

# Version info
__version__ = "0.1.0"

# Import key classes for convenience
from .base.service import MCPService
from .base.tool import MCPTool
from .client.hermes_client import HermesMCPClient
from .config.settings import MCPConfig

__all__ = [
    "MCPService",
    "MCPTool", 
    "HermesMCPClient",
    "MCPConfig",
]