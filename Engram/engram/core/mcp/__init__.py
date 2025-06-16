"""
MCP Module for Engram

This module provides Model Context Protocol (MCP) support 
for the Engram memory system using FastMCP.
"""

# Import standardized exports
from .tools import (
    # Memory capabilities
    memory_store,
    memory_query,
    get_context,
    
    # Structured memory capabilities
    structured_memory_add,
    structured_memory_get,
    structured_memory_update,
    structured_memory_delete,
    structured_memory_search,
    
    # Nexus capabilities
    nexus_process,
    
    # Registration functions
    register_memory_tools,
    register_structured_memory_tools,
    register_nexus_tools,
    get_all_tools,
    get_all_capabilities
)