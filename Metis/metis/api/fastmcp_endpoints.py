"""
FastMCP endpoints for Metis.

This module provides FastAPI endpoints for MCP (Model Context Protocol) integration,
allowing external systems to interact with Metis task management capabilities.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from tekton.models.base import TektonBaseModel
import asyncio

from tekton.mcp.fastmcp.server import FastMCPServer
from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints
from tekton.mcp.fastmcp.exceptions import FastMCPError

from metis.core.mcp.tools import (
    task_management_tools,
    dependency_management_tools,
    analytics_tools,
    telos_integration_tools
)
from metis.core.mcp.capabilities import (
    TaskManagementCapability,
    DependencyManagementCapability,
    TaskAnalyticsCapability,
    TelosIntegrationCapability
)


class MCPRequest(TektonBaseModel):
    """Request model for MCP tool execution."""
    tool_name: str
    arguments: Dict[str, Any]


class MCPResponse(TektonBaseModel):
    """Response model for MCP tool execution."""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Create FastMCP server instance
fastmcp_server = FastMCPServer(
    name="metis",
    version="0.1.0",
    description="Metis Task Management MCP Server"
)

# Register capabilities and tools
fastmcp_server.register_capability(TaskManagementCapability())
fastmcp_server.register_capability(DependencyManagementCapability()) 
fastmcp_server.register_capability(TaskAnalyticsCapability())
fastmcp_server.register_capability(TelosIntegrationCapability())

# Register all tools - convert to proper ToolSchema format
for tool_dict in task_management_tools + dependency_management_tools + analytics_tools + telos_integration_tools:
    # Convert the tool dict to match ToolSchema expectations
    tool_schema = {
        "name": tool_dict["name"],
        "description": tool_dict["description"],
        "schema": {  # This is the 'input_schema' field aliased as 'schema'
            "type": "object",
            "properties": tool_dict["parameters"]["properties"],
            "required": tool_dict["parameters"].get("required", [])
        }
    }
    fastmcp_server.register_tool(tool_schema)


# Create router for MCP endpoints
mcp_router = APIRouter(prefix="/api/mcp/v2")

# Add standard MCP endpoints using shared utilities
add_mcp_endpoints(mcp_router, fastmcp_server)


# Additional Metis-specific MCP endpoints
@mcp_router.get("/task-status")
async def get_task_status() -> Dict[str, Any]:
    """
    Get overall task management status.
    
    Returns:
        Dictionary containing task management status and statistics
    """
    try:
        # Import here to avoid circular imports
        from metis.api.routes import task_manager
        
        # Get all tasks
        all_tasks = await task_manager.list_tasks()
        
        # Calculate status summary
        status_counts = {}
        for task in all_tasks:
            status_counts[task.status] = status_counts.get(task.status, 0) + 1
        
        return {
            "success": True,
            "status": "operational",
            "service": "metis-task-management",
            "total_tasks": len(all_tasks),
            "status_breakdown": status_counts,
            "capabilities": [
                "task_management",
                "dependency_management", 
                "task_analytics",
                "telos_integration"
            ],
            "mcp_tools": len(task_management_tools + dependency_management_tools + analytics_tools + telos_integration_tools)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@mcp_router.post("/execute-workflow")
async def execute_task_workflow(
    workflow_name: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a predefined task management workflow.
    
    Args:
        workflow_name: Name of the workflow to execute
        parameters: Parameters for the workflow
        
    Returns:
        Dictionary containing workflow execution results
    """
    try:
        # Define available workflows
        workflows = {
            "create_task_with_subtasks": _create_task_with_subtasks_workflow,
            "import_and_analyze_requirement": _import_and_analyze_requirement_workflow,
            "batch_update_tasks": _batch_update_tasks_workflow,
            "analyze_project_complexity": _analyze_project_complexity_workflow
        }
        
        if workflow_name not in workflows:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown workflow: {workflow_name}. Available workflows: {list(workflows.keys())}"
            )
        
        # Execute the workflow
        result = await workflows[workflow_name](parameters)
        
        return {
            "success": True,
            "workflow": workflow_name,
            "result": result,
            "message": f"Workflow '{workflow_name}' executed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


# ============================================================================
# Workflow Implementations
# ============================================================================

async def _create_task_with_subtasks_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Create a main task with multiple subtasks."""
    from metis.core.mcp.tools import create_task, add_subtask
    
    # Extract parameters
    main_task_data = parameters.get("main_task", {})
    subtasks_data = parameters.get("subtasks", [])
    
    # Create main task
    main_task_result = await create_task(**main_task_data)
    if not main_task_result["success"]:
        return main_task_result
    
    task_id = main_task_result["task"]["id"]
    
    # Create subtasks
    subtask_results = []
    for subtask_data in subtasks_data:
        subtask_result = await add_subtask(task_id, **subtask_data)
        subtask_results.append(subtask_result)
    
    return {
        "main_task": main_task_result["task"],
        "subtasks": subtask_results,
        "total_subtasks": len(subtask_results)
    }


async def _import_and_analyze_requirement_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Import a requirement from Telos and analyze its complexity."""
    from metis.core.mcp.tools import import_requirement_as_task, analyze_task_complexity
    
    # Extract parameters
    requirement_id = parameters.get("requirement_id")
    priority = parameters.get("priority", "medium")
    assignee = parameters.get("assignee")
    complexity_factors = parameters.get("complexity_factors")
    
    # Import requirement as task
    import_result = await import_requirement_as_task(requirement_id, priority, assignee)
    if not import_result["success"]:
        return import_result
    
    task_id = import_result["task"]["id"]
    
    # Analyze complexity
    complexity_result = await analyze_task_complexity(task_id, complexity_factors)
    
    return {
        "imported_task": import_result["task"],
        "complexity_analysis": complexity_result["complexity"] if complexity_result["success"] else None,
        "requirement_id": requirement_id
    }


async def _batch_update_tasks_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Update multiple tasks in batch."""
    from metis.core.mcp.tools import update_task, list_tasks
    
    # Extract parameters
    filters = parameters.get("filters", {})
    updates = parameters.get("updates", {})
    
    # Get tasks to update
    tasks_result = await list_tasks(**filters)
    if not tasks_result["success"]:
        return tasks_result
    
    # Update each task
    update_results = []
    for task in tasks_result["tasks"]:
        update_result = await update_task(task["id"], **updates)
        update_results.append(update_result)
    
    successful_updates = sum(1 for result in update_results if result["success"])
    
    return {
        "total_tasks_found": len(tasks_result["tasks"]),
        "successful_updates": successful_updates,
        "failed_updates": len(update_results) - successful_updates,
        "update_results": update_results
    }


async def _analyze_project_complexity_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze complexity for all tasks in a project."""
    from metis.core.mcp.tools import list_tasks, analyze_task_complexity, get_task_statistics
    
    # Extract parameters
    project_filters = parameters.get("filters", {})
    
    # Get all project tasks
    tasks_result = await list_tasks(**project_filters)
    if not tasks_result["success"]:
        return tasks_result
    
    # Analyze complexity for each task
    complexity_results = []
    for task in tasks_result["tasks"]:
        if not task.get("complexity"):  # Only analyze if not already analyzed
            complexity_result = await analyze_task_complexity(task["id"])
            complexity_results.append(complexity_result)
    
    # Get updated statistics
    stats_result = await get_task_statistics()
    
    return {
        "total_tasks": len(tasks_result["tasks"]),
        "analyzed_tasks": len(complexity_results),
        "complexity_analyses": complexity_results,
        "overall_statistics": stats_result["statistics"] if stats_result["success"] else None
    }


# Export the router
__all__ = ["mcp_router", "fastmcp_server"]