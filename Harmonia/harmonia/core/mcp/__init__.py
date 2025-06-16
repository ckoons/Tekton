"""
Fast MCP integration for Harmonia.

This module provides FastMCP integration for Harmonia, including:
- Tool definitions for workflow orchestration using FastMCP decorators
- MCP capabilities for workflow management, execution, and monitoring
- Registration utilities for FastMCP tools
"""

from tekton.mcp.fastmcp import mcp_tool, mcp_capability, register_tool_from_fn
from tekton.mcp.fastmcp.utils import create_mcp_router, add_standard_mcp_endpoints

from .tools import (
    # Workflow definition tools
    create_workflow_definition, update_workflow_definition, delete_workflow_definition,
    get_workflow_definition, list_workflow_definitions,
    # Workflow execution tools
    execute_workflow, cancel_workflow_execution, pause_workflow_execution,
    resume_workflow_execution, get_workflow_execution_status, list_workflow_executions,
    # Template tools
    create_template, instantiate_template, list_templates,
    # Component tools
    list_components, get_component_actions, execute_component_action,
    # Registration
    register_tools, get_all_tools
)

__all__ = [
    # FastMCP exports
    "mcp_tool", "mcp_capability", "register_tool_from_fn",
    "create_mcp_router", "add_standard_mcp_endpoints",
    
    # Tool definitions
    "create_workflow_definition", "update_workflow_definition", "delete_workflow_definition",
    "get_workflow_definition", "list_workflow_definitions",
    "execute_workflow", "cancel_workflow_execution", "pause_workflow_execution",
    "resume_workflow_execution", "get_workflow_execution_status", "list_workflow_executions",
    "create_template", "instantiate_template", "list_templates",
    "list_components", "get_component_actions", "execute_component_action",
    
    # Registration
    "register_tools",
]