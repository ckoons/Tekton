"""
FastMCP endpoints for Prometheus.

This module provides FastAPI endpoints for MCP (Model Context Protocol) integration,
allowing external systems to interact with Prometheus planning and analysis capabilities.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from tekton.models.base import TektonBaseModel
import asyncio

from tekton.mcp.fastmcp.server import FastMCPServer
from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints
from tekton.mcp.fastmcp.exceptions import FastMCPError

from prometheus.core.mcp.tools import (
    planning_tools,
    retrospective_tools,
    resource_management_tools,
    improvement_tools
)
from prometheus.core.mcp.capabilities import (
    PlanningCapability,
    RetrospectiveAnalysisCapability,
    ResourceManagementCapability,
    ImprovementRecommendationsCapability
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
    name="prometheus",
    version="0.1.0",
    description="Prometheus Planning and Analysis MCP Server"
)

# Capabilities are already registered by the @mcp_capability decorator
# No need to register them again

# Tools are already registered by the @mcp_tool decorator
# When using FastMCP decorators, tools are automatically registered
# No need to manually register them


# Create router for MCP endpoints
mcp_router = APIRouter(prefix="/api/mcp/v2")

# Add standard MCP endpoints using shared utilities
add_mcp_endpoints(mcp_router, fastmcp_server)


# Additional Prometheus-specific MCP endpoints
@mcp_router.get("/planning-status")
async def get_planning_status() -> Dict[str, Any]:
    """
    Get overall planning system status.
    
    Returns:
        Dictionary containing planning system status and capabilities
    """
    try:
        # Mock planning status - real implementation would check actual planning engine
        return {
            "success": True,
            "status": "operational",
            "service": "prometheus-planning",
            "capabilities": [
                "planning",
                "retrospective_analysis",
                "resource_management",
                "improvement_recommendations"
            ],
            "active_plans": 0,  # Would query actual plans
            "mcp_tools": len(planning_tools + retrospective_tools + resource_management_tools + improvement_tools),
            "planning_engine_status": "ready",
            "message": "Prometheus planning system is operational"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get planning status: {str(e)}")


@mcp_router.post("/execute-analysis-workflow")
async def execute_analysis_workflow(
    workflow_name: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a predefined analysis workflow.
    
    Args:
        workflow_name: Name of the workflow to execute
        parameters: Parameters for the workflow
        
    Returns:
        Dictionary containing workflow execution results
    """
    try:
        # Define available workflows
        workflows = {
            "full_project_analysis": _full_project_analysis_workflow,
            "resource_optimization": _resource_optimization_workflow,
            "retrospective_with_improvements": _retrospective_with_improvements_workflow,
            "capacity_planning": _capacity_planning_workflow
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
            "message": f"Analysis workflow '{workflow_name}' executed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


# ============================================================================
# Workflow Implementations
# ============================================================================

async def _full_project_analysis_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Comprehensive project analysis including planning, tracking, and retrospective."""
    from prometheus.core.mcp.tools import (
        create_project_plan, analyze_critical_path, 
        conduct_retrospective, generate_improvement_recommendations
    )
    
    # Extract parameters
    project_data = parameters.get("project_data", {})
    
    # Step 1: Create or analyze project plan
    plan_result = await create_project_plan(
        project_name=project_data.get("name", "Analyzed Project"),
        description=project_data.get("description", "Project under analysis"),
        start_date=project_data.get("start_date", "2024-01-01"),
        end_date=project_data.get("end_date", "2024-12-31"),
        objectives=project_data.get("objectives", ["Complete project successfully"])
    )
    
    # Step 2: Analyze critical path if tasks provided
    critical_path_result = None
    if "tasks" in project_data:
        critical_path_result = await analyze_critical_path(
            plan_id=plan_result.get("plan", {}).get("plan_id", "temp"),
            tasks=project_data["tasks"]
        )
    
    # Step 3: Conduct retrospective if metrics provided
    retrospective_result = None
    if "planned_metrics" in project_data and "actual_metrics" in project_data:
        retrospective_result = await conduct_retrospective(
            project_id=project_data.get("project_id", "temp"),
            planned_metrics=project_data["planned_metrics"],
            actual_metrics=project_data["actual_metrics"]
        )
    
    # Step 4: Generate improvement recommendations
    improvement_result = await generate_improvement_recommendations(
        project_data=project_data,
        focus_areas=parameters.get("focus_areas", ["planning", "execution", "quality"])
    )
    
    return {
        "project_plan": plan_result,
        "critical_path_analysis": critical_path_result,
        "retrospective_analysis": retrospective_result,
        "improvement_recommendations": improvement_result,
        "workflow_summary": {
            "steps_completed": 4,
            "analysis_confidence": "high" if all([plan_result["success"], improvement_result["success"]]) else "medium"
        }
    }


async def _resource_optimization_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Resource optimization workflow including capacity analysis and allocation."""
    from prometheus.core.mcp.tools import analyze_resource_capacity, allocate_resources
    
    # Extract parameters
    resources = parameters.get("resources", [])
    tasks = parameters.get("tasks", [])
    plan_id = parameters.get("plan_id", "temp")
    
    # Step 1: Analyze resource capacity
    capacity_result = await analyze_resource_capacity(
        resources=resources,
        time_period=parameters.get("time_period", "monthly")
    )
    
    # Step 2: Allocate resources if tasks provided
    allocation_result = None
    if tasks:
        allocation_result = await allocate_resources(
            plan_id=plan_id,
            resources=resources,
            tasks=tasks,
            optimization_strategy=parameters.get("optimization_strategy", "balanced")
        )
    
    return {
        "capacity_analysis": capacity_result,
        "resource_allocation": allocation_result,
        "optimization_summary": {
            "bottlenecks_identified": len(capacity_result.get("analysis", {}).get("bottlenecks", [])),
            "allocations_made": len(allocation_result.get("allocations", [])) if allocation_result else 0,
            "optimization_confidence": "high" if capacity_result["success"] else "medium"
        }
    }


async def _retrospective_with_improvements_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Retrospective analysis with improvement recommendations."""
    from prometheus.core.mcp.tools import (
        conduct_retrospective, analyze_performance_trends, 
        generate_improvement_recommendations, prioritize_improvements
    )
    
    # Extract parameters
    project_id = parameters.get("project_id", "temp")
    planned_metrics = parameters.get("planned_metrics", {})
    actual_metrics = parameters.get("actual_metrics", {})
    historical_projects = parameters.get("historical_projects", [])
    
    # Step 1: Conduct retrospective
    retrospective_result = await conduct_retrospective(
        project_id=project_id,
        planned_metrics=planned_metrics,
        actual_metrics=actual_metrics,
        team_feedback=parameters.get("team_feedback", [])
    )
    
    # Step 2: Analyze trends if historical data provided
    trends_result = None
    if historical_projects:
        trends_result = await analyze_performance_trends(
            projects=historical_projects,
            metrics=list(planned_metrics.keys()),
            time_period=parameters.get("time_period", "last_year")
        )
    
    # Step 3: Generate improvement recommendations
    improvement_result = await generate_improvement_recommendations(
        project_data={
            "metrics": actual_metrics,
            "retrospective": retrospective_result.get("retrospective", {})
        }
    )
    
    # Step 4: Prioritize improvements
    improvements_list = []
    if improvement_result["success"]:
        for priority_level, improvements in improvement_result["recommendations"].items():
            improvements_list.extend(improvements)
    
    prioritization_result = None
    if improvements_list:
        prioritization_result = await prioritize_improvements(
            improvements=improvements_list,
            constraints=parameters.get("constraints", {})
        )
    
    return {
        "retrospective": retrospective_result,
        "performance_trends": trends_result,
        "improvement_recommendations": improvement_result,
        "improvement_prioritization": prioritization_result,
        "workflow_summary": {
            "total_improvements": len(improvements_list),
            "analysis_confidence": "high" if retrospective_result["success"] else "medium"
        }
    }


async def _capacity_planning_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Capacity planning workflow for future projects."""
    from prometheus.core.mcp.tools import analyze_resource_capacity, allocate_resources
    
    # Extract parameters
    current_resources = parameters.get("current_resources", [])
    future_projects = parameters.get("future_projects", [])
    
    # Step 1: Analyze current capacity
    capacity_result = await analyze_resource_capacity(
        resources=current_resources,
        time_period=parameters.get("time_period", "quarterly")
    )
    
    # Step 2: Simulate allocation for future projects
    allocation_results = []
    for project in future_projects:
        if "tasks" in project:
            allocation_result = await allocate_resources(
                plan_id=project.get("project_id", "future"),
                resources=current_resources,
                tasks=project["tasks"],
                optimization_strategy="capacity"
            )
            allocation_results.append({
                "project_id": project.get("project_id", "future"),
                "project_name": project.get("name", "Future Project"),
                "allocation": allocation_result
            })
    
    # Step 3: Generate capacity recommendations
    total_demand = sum(
        len(result["allocation"].get("allocations", [])) 
        for result in allocation_results 
        if result["allocation"]["success"]
    )
    
    capacity_recommendations = []
    if total_demand > len(current_resources) * 0.8:  # 80% utilization threshold
        capacity_recommendations.append("Consider hiring additional resources")
    
    capacity_analysis = capacity_result.get("analysis", {})
    if capacity_analysis.get("bottlenecks", []):
        capacity_recommendations.append("Address skill bottlenecks through training or hiring")
    
    return {
        "current_capacity": capacity_result,
        "future_allocations": allocation_results,
        "capacity_recommendations": capacity_recommendations,
        "planning_summary": {
            "projects_analyzed": len(future_projects),
            "allocation_success_rate": sum(1 for r in allocation_results if r["allocation"]["success"]) / len(allocation_results) if allocation_results else 0,
            "capacity_utilization": total_demand / len(current_resources) if current_resources else 0
        }
    }


# Export the router
__all__ = ["mcp_router", "fastmcp_server"]