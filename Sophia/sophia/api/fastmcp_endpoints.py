"""
FastMCP endpoints for Sophia.

This module provides FastAPI endpoints for MCP (Model Context Protocol) integration,
allowing external systems to interact with Sophia's ML/CI analysis, research management,
and intelligence measurement capabilities.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import Field
import asyncio

from tekton.models.base import TektonBaseModel

from tekton.mcp.fastmcp.server import FastMCPServer
from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints
from tekton.mcp.fastmcp.exceptions import FastMCPError

from sophia.core.mcp.tools import (
    ml_analysis_tools,
    research_management_tools,
    intelligence_measurement_tools
)
from sophia.core.mcp.capabilities import (
    MLAnalysisCapability,
    ResearchManagementCapability,
    IntelligenceMeasurementCapability
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
    name="sophia",
    version="0.1.0",
    description="Sophia ML/CI Analysis and Research Management MCP Server"
)

# Register capabilities and tools (instantiate the capability classes)
fastmcp_server.register_capability(MLAnalysisCapability())
fastmcp_server.register_capability(ResearchManagementCapability())
fastmcp_server.register_capability(IntelligenceMeasurementCapability())

# Register all tools
for tool in ml_analysis_tools + research_management_tools + intelligence_measurement_tools:
    fastmcp_server.register_tool(tool)


# Create router for MCP endpoints
fastmcp_router = APIRouter(prefix="/api/mcp/v2")

# Add standard MCP endpoints using shared utilities
add_mcp_endpoints(fastmcp_router, fastmcp_server)


# Additional Sophia-specific MCP endpoints
@fastmcp_router.get("/ml-status")
async def get_ml_status() -> Dict[str, Any]:
    """
    Get overall ML/CI system status.
    
    Returns:
        Dictionary containing ML system status and capabilities
    """
    try:
        # Mock ML status - real implementation would check actual ML engines
        return {
            "success": True,
            "status": "operational",
            "service": "sophia-ml-analysis",
            "capabilities": [
                "ml_analysis",
                "research_management",
                "intelligence_measurement"
            ],
            "active_experiments": 3,  # Would query actual experiments
            "mcp_tools": len(ml_analysis_tools + research_management_tools + intelligence_measurement_tools),
            "ml_engine_status": "ready",
            "research_projects": 5,  # Would query actual projects
            "message": "Sophia ML/CI analysis system is operational"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ML status: {str(e)}")


@fastmcp_router.post("/execute-research-workflow")
async def execute_research_workflow(
    workflow_name: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a predefined research workflow.
    
    Args:
        workflow_name: Name of the workflow to execute
        parameters: Parameters for the workflow
        
    Returns:
        Dictionary containing workflow execution results
    """
    try:
        # Define available workflows
        workflows = {
            "complete_research_analysis": _complete_research_analysis_workflow,
            "intelligence_assessment": _intelligence_assessment_workflow,
            "component_optimization": _component_optimization_workflow,
            "trend_analysis": _trend_analysis_workflow
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
            "message": f"Research workflow '{workflow_name}' executed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


# ============================================================================
# Workflow Implementations
# ============================================================================

async def _complete_research_analysis_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Complete research analysis including data collection, analysis, and recommendations."""
    from sophia.core.mcp.tools import (
        analyze_component_performance, extract_patterns,
        create_research_project, generate_research_recommendations
    )
    
    # Extract parameters
    component_ids = parameters.get("component_ids", [])
    research_focus = parameters.get("research_focus", "performance")
    analysis_period = parameters.get("analysis_period", "last_month")
    
    # Step 1: Analyze component performance
    performance_results = []
    for component_id in component_ids:
        perf_result = await analyze_component_performance(
            component_id=component_id,
            analysis_period=analysis_period,
            metrics=["efficiency", "accuracy", "responsiveness"]
        )
        performance_results.append(perf_result)
    
    # Step 2: Extract patterns from performance data
    pattern_result = await extract_patterns(
        data_source="component_performance",
        data_points=[r["analysis"] for r in performance_results if r["success"]],
        pattern_types=["trend", "anomaly", "correlation"]
    )
    
    # Step 3: Create research project for findings
    project_result = await create_research_project(
        title=f"Component Analysis: {research_focus.title()}",
        description=f"Analysis of {len(component_ids)} components focusing on {research_focus}",
        research_questions=[
            f"What patterns emerge in {research_focus} metrics?",
            "Which components show the most improvement potential?",
            "What correlations exist between component interactions?"
        ],
        target_components=component_ids,
        methodology="data_analysis"
    )
    
    # Step 4: Generate research recommendations
    recommendation_result = await generate_research_recommendations(
        project_id=project_result.get("project", {}).get("project_id", "temp"),
        findings=pattern_result.get("patterns", []),
        focus_areas=[research_focus, "optimization", "integration"]
    )
    
    return {
        "component_analysis": performance_results,
        "pattern_extraction": pattern_result,
        "research_project": project_result,
        "recommendations": recommendation_result,
        "workflow_summary": {
            "components_analyzed": len(component_ids),
            "patterns_found": len(pattern_result.get("patterns", [])),
            "recommendations_generated": len(recommendation_result.get("recommendations", [])),
            "analysis_confidence": "high" if all(r["success"] for r in performance_results) else "medium"
        }
    }


async def _intelligence_assessment_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Intelligence assessment workflow for evaluating component capabilities."""
    from sophia.core.mcp.tools import (
        measure_component_intelligence, compare_intelligence_profiles,
        track_intelligence_evolution, generate_intelligence_insights
    )
    
    # Extract parameters
    component_ids = parameters.get("component_ids", [])
    intelligence_dimensions = parameters.get("dimensions", ["reasoning", "learning", "adaptation"])
    assessment_period = parameters.get("assessment_period", "quarterly")
    
    # Step 1: Measure intelligence for each component
    intelligence_measurements = []
    for component_id in component_ids:
        for dimension in intelligence_dimensions:
            measurement = await measure_component_intelligence(
                component_id=component_id,
                dimension=dimension,
                measurement_method="automated_assessment",
                context={"period": assessment_period}
            )
            intelligence_measurements.append(measurement)
    
    # Step 2: Compare intelligence profiles
    comparison_result = await compare_intelligence_profiles(
        component_ids=component_ids,
        dimensions=intelligence_dimensions,
        comparison_type="comprehensive"
    )
    
    # Step 3: Track intelligence evolution over time
    evolution_result = await track_intelligence_evolution(
        component_ids=component_ids,
        time_period=assessment_period,
        dimensions=intelligence_dimensions
    )
    
    # Step 4: Generate intelligence insights
    insights_result = await generate_intelligence_insights(
        measurements=intelligence_measurements,
        comparisons=comparison_result.get("comparisons", []),
        evolution_data=evolution_result.get("evolution", {})
    )
    
    return {
        "intelligence_measurements": intelligence_measurements,
        "profile_comparison": comparison_result,
        "evolution_tracking": evolution_result,
        "intelligence_insights": insights_result,
        "workflow_summary": {
            "components_assessed": len(component_ids),
            "dimensions_evaluated": len(intelligence_dimensions),
            "insights_generated": len(insights_result.get("insights", [])),
            "assessment_confidence": "high" if len(intelligence_measurements) >= len(component_ids) * len(intelligence_dimensions) else "medium"
        }
    }


async def _component_optimization_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Component optimization workflow using ML analysis and recommendations."""
    from sophia.core.mcp.tools import (
        analyze_component_performance, predict_optimization_impact,
        design_ml_experiment, validate_optimization_results
    )
    
    # Extract parameters
    component_id = parameters.get("component_id", "")
    optimization_goals = parameters.get("optimization_goals", ["performance", "efficiency"])
    baseline_period = parameters.get("baseline_period", "last_month")
    
    # Step 1: Analyze current component performance
    baseline_analysis = await analyze_component_performance(
        component_id=component_id,
        analysis_period=baseline_period,
        metrics=optimization_goals + ["resource_usage", "error_rate"]
    )
    
    # Step 2: Predict optimization impact
    prediction_result = await predict_optimization_impact(
        component_id=component_id,
        current_metrics=baseline_analysis.get("analysis", {}).get("metrics", {}),
        optimization_strategies=["algorithm_tuning", "resource_optimization", "workflow_improvement"]
    )
    
    # Step 3: Design ML experiment for optimization
    experiment_result = await design_ml_experiment(
        experiment_name=f"Optimization: {component_id}",
        component_ids=[component_id],
        hypothesis=f"Targeted optimizations will improve {', '.join(optimization_goals)}",
        variables={"optimization_strategy": "adaptive", "measurement_interval": "hourly"},
        success_criteria=optimization_goals
    )
    
    # Step 4: Validate optimization approach
    validation_result = await validate_optimization_results(
        experiment_id=experiment_result.get("experiment", {}).get("experiment_id", "temp"),
        baseline_metrics=baseline_analysis.get("analysis", {}).get("metrics", {}),
        predicted_improvements=prediction_result.get("predictions", [])
    )
    
    return {
        "baseline_analysis": baseline_analysis,
        "optimization_predictions": prediction_result,
        "experiment_design": experiment_result,
        "validation_results": validation_result,
        "workflow_summary": {
            "component_id": component_id,
            "optimization_goals": optimization_goals,
            "predicted_improvement": prediction_result.get("overall_improvement_score", 0),
            "experiment_designed": experiment_result["success"],
            "optimization_confidence": "high" if baseline_analysis["success"] and prediction_result["success"] else "medium"
        }
    }


async def _trend_analysis_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Trend analysis workflow for ecosystem-wide insights."""
    from sophia.core.mcp.tools import (
        analyze_ecosystem_trends, extract_patterns,
        forecast_system_evolution, generate_strategic_insights
    )
    
    # Extract parameters
    analysis_scope = parameters.get("scope", "ecosystem")
    time_horizon = parameters.get("time_horizon", "6_months")
    trend_categories = parameters.get("categories", ["performance", "usage", "efficiency", "innovation"])
    
    # Step 1: Analyze ecosystem trends
    trend_analysis = await analyze_ecosystem_trends(
        scope=analysis_scope,
        time_period=time_horizon,
        categories=trend_categories,
        granularity="weekly"
    )
    
    # Step 2: Extract deeper patterns from trends
    pattern_result = await extract_patterns(
        data_source="ecosystem_trends",
        data_points=trend_analysis.get("trends", []),
        pattern_types=["cyclical", "growth", "decline", "stability"]
    )
    
    # Step 3: Forecast system evolution
    forecast_result = await forecast_system_evolution(
        current_trends=trend_analysis.get("trends", []),
        patterns=pattern_result.get("patterns", []),
        forecast_horizon="1_year",
        confidence_level=0.8
    )
    
    # Step 4: Generate strategic insights
    insights_result = await generate_strategic_insights(
        trends=trend_analysis.get("trends", []),
        patterns=pattern_result.get("patterns", []),
        forecasts=forecast_result.get("forecasts", []),
        strategic_focus=["scalability", "innovation", "optimization"]
    )
    
    return {
        "trend_analysis": trend_analysis,
        "pattern_extraction": pattern_result,
        "evolution_forecast": forecast_result,
        "strategic_insights": insights_result,
        "workflow_summary": {
            "scope": analysis_scope,
            "time_horizon": time_horizon,
            "trends_identified": len(trend_analysis.get("trends", [])),
            "patterns_found": len(pattern_result.get("patterns", [])),
            "insights_generated": len(insights_result.get("insights", [])),
            "forecast_confidence": forecast_result.get("confidence_score", 0)
        }
    }


# Export the router
__all__ = ["fastmcp_router", "fastmcp_server"]