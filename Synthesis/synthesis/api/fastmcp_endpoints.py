"""
FastMCP endpoints for Synthesis.

This module provides FastAPI endpoints for MCP (Model Context Protocol) integration,
allowing external systems to interact with Synthesis data synthesis, integration orchestration,
and workflow composition capabilities.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from tekton.models.base import TektonBaseModel
import asyncio
import sys
import os

# Import shared workflow endpoint
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))
from workflow.endpoint_template import create_workflow_endpoint

from tekton.mcp.fastmcp.server import FastMCPServer
from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints
from tekton.mcp.fastmcp.exceptions import FastMCPError

from synthesis.core.mcp.tools import (
    data_synthesis_tools,
    integration_orchestration_tools,
    workflow_composition_tools
)
from synthesis.core.mcp.capabilities import (
    DataSynthesisCapability,
    IntegrationOrchestrationCapability,
    WorkflowCompositionCapability
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
    name="synthesis",
    version="0.1.0",
    description="Synthesis Data Synthesis, Integration Orchestration, and Workflow Composition MCP Server"
)

# Register capabilities and tools
fastmcp_server.register_capability(DataSynthesisCapability())
fastmcp_server.register_capability(IntegrationOrchestrationCapability())
fastmcp_server.register_capability(WorkflowCompositionCapability())

# Register all tools
for tool in data_synthesis_tools + integration_orchestration_tools + workflow_composition_tools:
    fastmcp_server.register_tool(tool)


# Create router for MCP endpoints
mcp_router = APIRouter(prefix="/api/mcp/v2")

# Add standard MCP endpoints using shared utilities
add_mcp_endpoints(mcp_router, fastmcp_server)


# Additional Synthesis-specific MCP endpoints
@mcp_router.get("/synthesis-status")
async def get_synthesis_status() -> Dict[str, Any]:
    """
    Get overall Synthesis system status.
    
    Returns:
        Dictionary containing Synthesis system status and capabilities
    """
    try:
        # Mock synthesis status - real implementation would check actual synthesis engine
        return {
            "success": True,
            "status": "operational",
            "service": "synthesis-execution-engine",
            "capabilities": [
                "data_synthesis",
                "integration_orchestration",
                "workflow_composition"
            ],
            "active_syntheses": 3,  # Would query actual synthesis processes
            "mcp_tools": len(data_synthesis_tools + integration_orchestration_tools + workflow_composition_tools),
            "synthesis_engine_status": "ready",
            "message": "Synthesis execution and integration engine is operational"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get synthesis status: {str(e)}")


@mcp_router.post("/execute-synthesis-workflow")
async def execute_synthesis_workflow(
    workflow_name: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a predefined synthesis workflow.
    
    Args:
        workflow_name: Name of the workflow to execute
        parameters: Parameters for the workflow
        
    Returns:
        Dictionary containing workflow execution results
    """
    try:
        # Define available workflows
        workflows = {
            "data_unification": _data_unification_workflow,
            "component_integration": _component_integration_workflow,
            "workflow_orchestration": _workflow_orchestration_workflow,
            "end_to_end_synthesis": _end_to_end_synthesis_workflow
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
            "message": f"Synthesis workflow '{workflow_name}' executed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


# ============================================================================
# Workflow Implementations
# ============================================================================

async def _data_unification_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Data unification workflow combining synthesis and validation."""
    from synthesis.core.mcp.tools import (
        synthesize_component_data, merge_data_streams,
        detect_data_conflicts, validate_synthesis_quality
    )
    
    # Extract parameters
    component_ids = parameters.get("component_ids", [])
    unification_strategy = parameters.get("unification_strategy", "merge_with_conflict_resolution")
    quality_threshold = parameters.get("quality_threshold", 0.8)
    
    # Step 1: Synthesize data from each component
    synthesis_results = []
    for component_id in component_ids:
        synthesis_result = await synthesize_component_data(
            component_ids=[component_id],
            synthesis_type="full_context",
            include_metadata=True
        )
        synthesis_results.append({
            "component": component_id,
            "result": synthesis_result,
            "success": synthesis_result["success"]
        })
    
    # Step 2: Merge data streams from successful syntheses
    successful_syntheses = [r for r in synthesis_results if r["success"]]
    merge_result = None
    
    if len(successful_syntheses) >= 2:
        stream_configs = []
        for syn in successful_syntheses:
            stream_configs.append({
                "source_component": syn["component"],
                "data_types": ["context", "memory", "state"],
                "priority": 1.0,
                "merge_strategy": "intelligent_merge"
            })
        
        merge_result = await merge_data_streams(
            stream_configs=stream_configs,
            merge_strategy=unification_strategy,
            conflict_resolution="intelligent_resolution"
        )
    
    # Step 3: Detect any conflicts in merged data
    conflict_result = None
    if merge_result and merge_result["success"]:
        conflict_result = await detect_data_conflicts(
            data_sources=[r["component"] for r in successful_syntheses],
            conflict_types=["schema_mismatch", "value_conflicts", "temporal_inconsistencies"],
            resolution_strategy="automatic"
        )
    
    # Step 4: Validate overall synthesis quality
    quality_result = None
    if merge_result and merge_result["success"]:
        quality_result = await validate_synthesis_quality(
            synthesis_id=merge_result["synthesis"]["synthesis_id"],
            quality_metrics=["completeness", "consistency", "accuracy"],
            validation_rules={"minimum_completeness": quality_threshold}
        )
    
    return {
        "components_processed": len(component_ids),
        "successful_syntheses": len(successful_syntheses),
        "data_merge": merge_result,
        "conflict_detection": conflict_result,
        "quality_validation": quality_result,
        "workflow_summary": {
            "unification_strategy": unification_strategy,
            "quality_threshold": quality_threshold,
            "conflicts_detected": len(conflict_result.get("conflicts", [])) if conflict_result else 0,
            "quality_passed": quality_result["validation"]["overall_score"] >= quality_threshold if quality_result else False,
            "unification_confidence": "high" if quality_result and quality_result["validation"]["overall_score"] >= quality_threshold else "medium"
        }
    }


async def _component_integration_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Component integration workflow including orchestration and monitoring."""
    from synthesis.core.mcp.tools import (
        orchestrate_component_integration, design_integration_workflow,
        monitor_integration_health, resolve_integration_conflicts
    )
    
    # Extract parameters
    primary_component = parameters.get("primary_component", "")
    target_components = parameters.get("target_components", [])
    integration_type = parameters.get("integration_type", "bidirectional")
    
    # Step 1: Design integration workflow
    workflow_result = await design_integration_workflow(
        component_ids=[primary_component] + target_components,
        integration_patterns=["data_sync", "event_propagation", "state_sharing"],
        workflow_complexity="automatic"
    )
    
    # Step 2: Orchestrate the integration
    orchestration_result = None
    if workflow_result["success"]:
        orchestration_result = await orchestrate_component_integration(
            primary_component=primary_component,
            target_components=target_components,
            integration_type=integration_type,
            orchestration_strategy="phased_rollout"
        )
    
    # Step 3: Monitor integration health
    health_result = None
    if orchestration_result and orchestration_result["success"]:
        health_result = await monitor_integration_health(
            integration_id=orchestration_result["integration"]["integration_id"],
            monitoring_metrics=["connectivity", "performance", "data_consistency"],
            monitoring_duration=60
        )
    
    # Step 4: Resolve any conflicts
    conflict_resolution_result = None
    if health_result and health_result["success"]:
        if health_result["health_status"]["issues_detected"] > 0:
            conflict_resolution_result = await resolve_integration_conflicts(
                integration_id=orchestration_result["integration"]["integration_id"],
                conflict_types=["connectivity_issues", "data_inconsistencies"],
                resolution_strategy="automated_healing"
            )
    
    return {
        "workflow_design": workflow_result,
        "integration_orchestration": orchestration_result,
        "health_monitoring": health_result,
        "conflict_resolution": conflict_resolution_result,
        "workflow_summary": {
            "primary_component": primary_component,
            "target_components": target_components,
            "integration_type": integration_type,
            "workflow_phases": len(workflow_result.get("workflow", {}).get("phases", [])) if workflow_result else 0,
            "integration_health": health_result["health_status"]["overall_health"] if health_result else "unknown",
            "conflicts_resolved": len(conflict_resolution_result.get("resolutions", [])) if conflict_resolution_result else 0,
            "integration_confidence": "high" if health_result and health_result["health_status"]["overall_health"] == "healthy" else "medium"
        }
    }


async def _workflow_orchestration_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Workflow orchestration including composition and optimization."""
    from synthesis.core.mcp.tools import (
        compose_multi_component_workflow, execute_composed_workflow,
        analyze_workflow_performance, optimize_workflow_execution
    )
    
    # Extract parameters
    workflow_components = parameters.get("workflow_components", [])
    workflow_type = parameters.get("workflow_type", "sequential")
    optimization_goals = parameters.get("optimization_goals", ["performance", "reliability"])
    
    # Step 1: Compose multi-component workflow
    composition_result = await compose_multi_component_workflow(
        component_definitions=workflow_components,
        workflow_type=workflow_type,
        optimization_hints=optimization_goals
    )
    
    # Step 2: Execute the composed workflow
    execution_result = None
    if composition_result["success"]:
        execution_result = await execute_composed_workflow(
            workflow_id=composition_result["workflow"]["workflow_id"],
            execution_mode="monitored",
            timeout_seconds=300
        )
    
    # Step 3: Analyze workflow performance
    performance_result = None
    if execution_result and execution_result["success"]:
        performance_result = await analyze_workflow_performance(
            workflow_id=composition_result["workflow"]["workflow_id"],
            execution_id=execution_result["execution"]["execution_id"],
            analysis_metrics=["execution_time", "resource_usage", "success_rate"]
        )
    
    # Step 4: Optimize workflow if needed
    optimization_result = None
    if performance_result and performance_result["success"]:
        if performance_result["performance"]["optimization_recommended"]:
            optimization_result = await optimize_workflow_execution(
                workflow_id=composition_result["workflow"]["workflow_id"],
                optimization_strategies=optimization_goals,
                performance_baseline=performance_result["performance"]
            )
    
    return {
        "workflow_composition": composition_result,
        "workflow_execution": execution_result,
        "performance_analysis": performance_result,
        "workflow_optimization": optimization_result,
        "workflow_summary": {
            "workflow_type": workflow_type,
            "components_count": len(workflow_components),
            "optimization_goals": optimization_goals,
            "execution_successful": execution_result["success"] if execution_result else False,
            "performance_score": performance_result["performance"]["overall_score"] if performance_result else 0,
            "optimization_applied": optimization_result["success"] if optimization_result else False,
            "orchestration_confidence": "high" if execution_result and execution_result["success"] else "medium"
        }
    }


async def _end_to_end_synthesis_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Complete end-to-end synthesis workflow combining all capabilities."""
    from synthesis.core.mcp.tools import (
        synthesize_component_data, create_unified_report,
        orchestrate_component_integration, compose_multi_component_workflow,
        optimize_data_flow, validate_synthesis_quality
    )
    
    # Extract parameters
    source_components = parameters.get("source_components", [])
    synthesis_objectives = parameters.get("synthesis_objectives", [])
    integration_requirements = parameters.get("integration_requirements", {})
    
    # Phase 1: Data Synthesis
    data_synthesis_result = await synthesize_component_data(
        component_ids=source_components,
        synthesis_type="comprehensive",
        include_metadata=True
    )
    
    # Phase 2: Create unified report
    report_result = None
    if data_synthesis_result["success"]:
        report_result = await create_unified_report(
            data_sources=source_components,
            report_format="comprehensive",
            include_visualizations=True
        )
    
    # Phase 3: Integration orchestration
    integration_result = None
    if len(source_components) > 1:
        integration_result = await orchestrate_component_integration(
            primary_component=source_components[0],
            target_components=source_components[1:],
            integration_type="bidirectional",
            orchestration_strategy="optimized_workflow"
        )
    
    # Phase 4: Workflow composition
    workflow_result = None
    if integration_result and integration_result["success"]:
        workflow_components = []
        for component in source_components:
            workflow_components.append({
                "component_id": component,
                "role": "data_processor",
                "dependencies": [],
                "configuration": integration_requirements.get(component, {})
            })
        
        workflow_result = await compose_multi_component_workflow(
            component_definitions=workflow_components,
            workflow_type="parallel_with_sync",
            optimization_hints=["performance", "reliability"]
        )
    
    # Phase 5: Data flow optimization
    optimization_result = None
    if workflow_result and workflow_result["success"]:
        optimization_result = await optimize_data_flow(
            synthesis_id=data_synthesis_result["synthesis"]["synthesis_id"],
            optimization_targets=["throughput", "latency", "resource_efficiency"],
            flow_constraints={}
        )
    
    # Phase 6: Final validation
    final_validation = None
    if optimization_result and optimization_result["success"]:
        final_validation = await validate_synthesis_quality(
            synthesis_id=data_synthesis_result["synthesis"]["synthesis_id"],
            quality_metrics=["completeness", "consistency", "performance"],
            validation_rules={"minimum_completeness": 0.9, "minimum_consistency": 0.85}
        )
    
    return {
        "phase_1_data_synthesis": data_synthesis_result,
        "phase_2_unified_report": report_result,
        "phase_3_integration": integration_result,
        "phase_4_workflow_composition": workflow_result,
        "phase_5_optimization": optimization_result,
        "phase_6_validation": final_validation,
        "workflow_summary": {
            "source_components": source_components,
            "synthesis_objectives": synthesis_objectives,
            "phases_completed": sum([
                1 if data_synthesis_result["success"] else 0,
                1 if report_result and report_result["success"] else 0,
                1 if integration_result and integration_result["success"] else 0,
                1 if workflow_result and workflow_result["success"] else 0,
                1 if optimization_result and optimization_result["success"] else 0,
                1 if final_validation and final_validation["success"] else 0
            ]),
            "overall_success": final_validation["success"] if final_validation else False,
            "quality_score": final_validation["validation"]["overall_score"] if final_validation else 0,
            "synthesis_confidence": "high" if final_validation and final_validation["validation"]["overall_score"] >= 0.85 else "medium"
        }
    }

# Add standardized workflow endpoint to the router
workflow_router = create_workflow_endpoint("synthesis") 
for route in workflow_router.routes:
    mcp_router.routes.append(route)

# Export the router
__all__ = ["mcp_router", "fastmcp_server"]