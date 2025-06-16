"""
Fast MCP integration for Ergon.

This module provides FastMCP integration for Ergon, including:
- Tool definitions using FastMCP decorators
- MCP capabilities for agent, workflow, and task management
- Registration utilities for FastMCP tools
"""

from tekton.mcp.fastmcp import mcp_tool, mcp_capability, register_tool_from_fn
from tekton.mcp.fastmcp.utils import create_mcp_router, add_standard_mcp_endpoints

from .tools import (
    # Agent tools
    create_agent, update_agent, delete_agent, get_agent, list_agents,
    # Workflow tools
    create_workflow, update_workflow, execute_workflow, get_workflow_status,
    # Task management tools
    create_task, assign_task, update_task_status, get_task, list_tasks,
    # Registration
    register_tools, get_all_tools
)

__all__ = [
    # FastMCP exports
    "mcp_tool", "mcp_capability", "register_tool_from_fn",
    "create_mcp_router", "add_standard_mcp_endpoints",
    
    # Tool definitions
    "create_agent", "update_agent", "delete_agent", "get_agent", "list_agents",
    "create_workflow", "update_workflow", "execute_workflow", "get_workflow_status",
    "create_task", "assign_task", "update_task_status", "get_task", "list_tasks",
    
    # Registration
    "register_tools",
    "get_all_tools"
]