"""
FastMCP tools for Telos.

This module defines FastMCP tools for requirements management, tracing, validation,
and strategic planning using the decorator-based approach.
"""

import logging
from typing import Dict, Any, List, Optional

# Check if FastMCP is available
try:
    from tekton.mcp.fastmcp.decorators import mcp_tool, mcp_capability
    from tekton.mcp.fastmcp.schema import MCPTool
    fastmcp_available = True
except ImportError:
    fastmcp_available = False
    # Define dummy decorators
    def mcp_tool(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def mcp_capability(*args, **kwargs):
        def decorator(cls):
            return cls
        return decorator
    
    MCPTool = None

logger = logging.getLogger(__name__)


@mcp_capability(
    name="requirements_management",
    description="Comprehensive requirements management with CRUD operations"
)
class RequirementsManagementCapability:
    """Capability for creating, reading, updating, and deleting requirements."""
    pass


@mcp_tool(
    category="requirements_management",
    name="create_project",
    description="Create a new requirements project"
)
async def create_project(
    name: str,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    requirements_manager=None
) -> Dict[str, Any]:
    """
    Create a new requirements project.
    
    Args:
        name: Name of the project
        description: Optional project description
        metadata: Optional metadata dictionary
        requirements_manager: Injected RequirementsManager instance
        
    Returns:
        Dict containing project_id, name, and creation details
    """
    if not requirements_manager:
        return {"error": "Requirements manager not available"}
    
    try:
        project_id = requirements_manager.create_project(
            name=name,
            description=description or "",
            metadata=metadata
        )
        
        project = requirements_manager.get_project(project_id)
        if not project:
            return {"error": "Failed to create project"}
        
        return {
            "project_id": project_id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at,
            "status": "created"
        }
    except Exception as e:
        return {"error": f"Failed to create project: {str(e)}"}


@mcp_tool(
    category="requirements_management",
    name="get_project",
    description="Get a project with its requirements and hierarchy"
)
async def get_project(
    project_id: str,
    requirements_manager=None
) -> Dict[str, Any]:
    """
    Get a project with its requirements and hierarchy.
    
    Args:
        project_id: ID of the project to retrieve
        requirements_manager: Injected RequirementsManager instance
        
    Returns:
        Dict containing project details, requirements, and hierarchy
    """
    if not requirements_manager:
        return {"error": "Requirements manager not available"}
    
    try:
        project = requirements_manager.get_project(project_id)
        if not project:
            return {"error": f"Project {project_id} not found"}
        
        # Get the requirement hierarchy
        hierarchy = project.get_requirement_hierarchy()
        
        # Prepare the response
        result = project.to_dict()
        result["hierarchy"] = hierarchy
        
        return result
    except Exception as e:
        return {"error": f"Failed to get project: {str(e)}"}


@mcp_tool(
    category="requirements_management",
    name="list_projects",
    description="List all requirements projects"
)
async def list_projects(
    requirements_manager=None
) -> Dict[str, Any]:
    """
    List all requirements projects.
    
    Args:
        requirements_manager: Injected RequirementsManager instance
        
    Returns:
        Dict containing list of projects with summary information
    """
    if not requirements_manager:
        return {"error": "Requirements manager not available"}
    
    try:
        projects = requirements_manager.get_all_projects()
        
        result = []
        for project in projects:
            result.append({
                "project_id": project.project_id,
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "requirement_count": len(project.requirements)
            })
        
        return {"projects": result, "count": len(result)}
    except Exception as e:
        return {"error": f"Failed to list projects: {str(e)}"}


@mcp_tool(
    category="requirements_management",
    name="create_requirement",
    description="Create a new requirement in a project"
)
async def create_requirement(
    project_id: str,
    title: str,
    description: str,
    requirement_type: Optional[str] = "functional",
    priority: Optional[str] = "medium",
    status: Optional[str] = "new",
    tags: Optional[List[str]] = None,
    parent_id: Optional[str] = None,
    dependencies: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    created_by: Optional[str] = None,
    requirements_manager=None
) -> Dict[str, Any]:
    """
    Create a new requirement in a project.
    
    Args:
        project_id: ID of the project
        title: Requirement title
        description: Requirement description
        requirement_type: Type of requirement (functional, non-functional, etc.)
        priority: Priority level (low, medium, high, critical)
        status: Current status (new, in-progress, completed, etc.)
        tags: Optional list of tags
        parent_id: Optional parent requirement ID
        dependencies: Optional list of dependency requirement IDs
        metadata: Optional metadata dictionary
        created_by: Optional creator identifier
        requirements_manager: Injected RequirementsManager instance
        
    Returns:
        Dict containing requirement_id and creation details
    """
    if not requirements_manager:
        return {"error": "Requirements manager not available"}
    
    try:
        # Ensure project exists
        project = requirements_manager.get_project(project_id)
        if not project:
            return {"error": f"Project {project_id} not found"}
        
        # Create requirement
        requirement_id = requirements_manager.add_requirement(
            project_id=project_id,
            title=title,
            description=description,
            requirement_type=requirement_type,
            priority=priority,
            status=status,
            tags=tags,
            parent_id=parent_id,
            dependencies=dependencies,
            metadata=metadata,
            created_by=created_by
        )
        
        if not requirement_id:
            return {"error": "Failed to create requirement"}
        
        # Get the created requirement
        requirement = requirements_manager.get_requirement(project_id, requirement_id)
        
        return {
            "project_id": project_id,
            "requirement_id": requirement_id,
            "title": requirement.title,
            "created_at": requirement.created_at,
            "status": "created"
        }
    except Exception as e:
        return {"error": f"Failed to create requirement: {str(e)}"}


@mcp_tool(
    category="requirements_management",
    name="get_requirement",
    description="Get a specific requirement by ID"
)
async def get_requirement(
    project_id: str,
    requirement_id: str,
    requirements_manager=None
) -> Dict[str, Any]:
    """
    Get a specific requirement by ID.
    
    Args:
        project_id: ID of the project
        requirement_id: ID of the requirement
        requirements_manager: Injected RequirementsManager instance
        
    Returns:
        Dict containing requirement details
    """
    if not requirements_manager:
        return {"error": "Requirements manager not available"}
    
    try:
        requirement = requirements_manager.get_requirement(project_id, requirement_id)
        if not requirement:
            return {"error": f"Requirement {requirement_id} not found in project {project_id}"}
        
        return requirement.to_dict()
    except Exception as e:
        return {"error": f"Failed to get requirement: {str(e)}"}


@mcp_tool(
    category="requirements_management",
    name="update_requirement",
    description="Update a requirement with new information"
)
async def update_requirement(
    project_id: str,
    requirement_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    requirement_type: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[List[str]] = None,
    parent_id: Optional[str] = None,
    dependencies: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    requirements_manager=None
) -> Dict[str, Any]:
    """
    Update a requirement with new information.
    
    Args:
        project_id: ID of the project
        requirement_id: ID of the requirement to update
        title: New title
        description: New description
        requirement_type: New requirement type
        priority: New priority
        status: New status
        tags: New tags list
        parent_id: New parent requirement ID
        dependencies: New dependencies list
        metadata: New metadata dictionary
        requirements_manager: Injected RequirementsManager instance
        
    Returns:
        Dict containing update status and details
    """
    if not requirements_manager:
        return {"error": "Requirements manager not available"}
    
    try:
        # Prepare updates
        updates = {}
        
        if title is not None:
            updates["title"] = title
        if description is not None:
            updates["description"] = description
        if requirement_type is not None:
            updates["requirement_type"] = requirement_type
        if priority is not None:
            updates["priority"] = priority
        if status is not None:
            updates["status"] = status
        if tags is not None:
            updates["tags"] = tags
        if parent_id is not None:
            updates["parent_id"] = parent_id
        if dependencies is not None:
            updates["dependencies"] = dependencies
        if metadata is not None:
            # Get current requirement to merge metadata
            current_req = requirements_manager.get_requirement(project_id, requirement_id)
            if current_req:
                merged_metadata = dict(current_req.metadata)
                merged_metadata.update(metadata)
                updates["metadata"] = merged_metadata
            else:
                updates["metadata"] = metadata
        
        # Only update if there are changes
        if not updates:
            return {"message": "No updates provided", "requirement_id": requirement_id}
        
        # Update the requirement
        success = requirements_manager.update_requirement(
            project_id=project_id,
            requirement_id=requirement_id,
            **updates
        )
        
        if not success:
            return {"error": f"Requirement {requirement_id} not found in project {project_id}"}
        
        # Get the updated requirement
        updated_requirement = requirements_manager.get_requirement(project_id, requirement_id)
        
        return {
            "requirement_id": requirement_id,
            "updated": list(updates.keys()),
            "updated_at": updated_requirement.updated_at if updated_requirement else None,
            "status": "updated"
        }
    except Exception as e:
        return {"error": f"Failed to update requirement: {str(e)}"}


@mcp_capability(
    name="requirement_tracing",
    description="Bidirectional requirement tracing and dependency management"
)
class RequirementTracingCapability:
    """Capability for creating and managing requirement traces and dependencies."""
    pass


@mcp_tool(
    category="requirement_tracing",
    name="create_trace",
    description="Create a trace between two requirements"
)
async def create_trace(
    project_id: str,
    source_id: str,
    target_id: str,
    trace_type: str,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    requirements_manager=None
) -> Dict[str, Any]:
    """
    Create a trace between two requirements.
    
    Args:
        project_id: ID of the project
        source_id: ID of the source requirement
        target_id: ID of the target requirement
        trace_type: Type of trace (derives, implements, tests, etc.)
        description: Optional description of the trace
        metadata: Optional metadata dictionary
        requirements_manager: Injected RequirementsManager instance
        
    Returns:
        Dict containing trace_id and creation details
    """
    if not requirements_manager:
        return {"error": "Requirements manager not available"}
    
    try:
        from datetime import datetime
        
        # Ensure project exists
        project = requirements_manager.get_project(project_id)
        if not project:
            return {"error": f"Project {project_id} not found"}
        
        # Verify source and target requirements exist
        source_req = project.get_requirement(source_id)
        target_req = project.get_requirement(target_id)
        
        if not source_req:
            return {"error": f"Source requirement {source_id} not found"}
        
        if not target_req:
            return {"error": f"Target requirement {target_id} not found"}
        
        # Create trace
        trace_id = f"trace_{int(datetime.now().timestamp())}"
        
        trace = {
            "trace_id": trace_id,
            "source_id": source_id,
            "target_id": target_id,
            "trace_type": trace_type,
            "description": description,
            "created_at": datetime.now().timestamp(),
            "metadata": metadata or {}
        }
        
        # Add to project metadata
        if "traces" not in project.metadata:
            project.metadata["traces"] = []
        
        project.metadata["traces"].append(trace)
        
        # Save the project
        requirements_manager._save_project(project)
        
        return {
            "trace_id": trace_id,
            "source_id": source_id,
            "target_id": target_id,
            "trace_type": trace_type,
            "status": "created"
        }
    except Exception as e:
        return {"error": f"Failed to create trace: {str(e)}"}


@mcp_tool(
    category="requirement_tracing",
    name="list_traces",
    description="List all traces for a project"
)
async def list_traces(
    project_id: str,
    requirements_manager=None
) -> Dict[str, Any]:
    """
    List all requirement traces for a project.
    
    Args:
        project_id: ID of the project
        requirements_manager: Injected RequirementsManager instance
        
    Returns:
        Dict containing list of traces
    """
    if not requirements_manager:
        return {"error": "Requirements manager not available"}
    
    try:
        # Ensure project exists
        project = requirements_manager.get_project(project_id)
        if not project:
            return {"error": f"Project {project_id} not found"}
        
        # Get traces from project metadata
        traces = project.metadata.get("traces", [])
        
        return {"traces": traces, "count": len(traces)}
    except Exception as e:
        return {"error": f"Failed to list traces: {str(e)}"}


@mcp_capability(
    name="requirement_validation",
    description="Quality assurance and validation of requirements"
)
class RequirementValidationCapability:
    """Capability for validating requirements quality and completeness."""
    pass


@mcp_tool(
    category="requirement_validation",
    name="validate_project",
    description="Validate all requirements in a project against quality criteria"
)
async def validate_project(
    project_id: str,
    check_completeness: bool = True,
    check_verifiability: bool = True,
    check_clarity: bool = True,
    custom_criteria: Optional[Dict[str, Any]] = None,
    requirements_manager=None
) -> Dict[str, Any]:
    """
    Validate all requirements in a project against quality criteria.
    
    Args:
        project_id: ID of the project to validate
        check_completeness: Whether to check requirement completeness
        check_verifiability: Whether to check requirement verifiability
        check_clarity: Whether to check requirement clarity
        custom_criteria: Optional custom validation criteria
        requirements_manager: Injected RequirementsManager instance
        
    Returns:
        Dict containing validation results and summary
    """
    if not requirements_manager:
        return {"error": "Requirements manager not available"}
    
    try:
        from datetime import datetime
        
        # Ensure project exists
        project = requirements_manager.get_project(project_id)
        if not project:
            return {"error": f"Project {project_id} not found"}
        
        # Get all requirements
        requirements = project.get_all_requirements()
        
        # Basic validation results
        validation_results = []
        
        # Validation criteria
        criteria = {
            "check_completeness": check_completeness,
            "check_verifiability": check_verifiability,
            "check_clarity": check_clarity
        }
        
        if custom_criteria:
            criteria.update(custom_criteria)
        
        # Perform validation based on criteria
        for req in requirements:
            result = {
                "requirement_id": req.requirement_id,
                "title": req.title,
                "issues": [],
                "passed": True
            }
            
            # Check for completeness
            if criteria.get("check_completeness", False):
                if not req.description or len(req.description) < 10:
                    result["issues"].append({
                        "type": "completeness",
                        "message": "Description is too short or missing"
                    })
                    result["passed"] = False
            
            # Check for verifiability
            if criteria.get("check_verifiability", False):
                # Basic heuristic - look for measurable terms
                verifiable_terms = ["measure", "test", "verify", "validate", "percent", "seconds", "minutes"]
                found_verifiable = any(term in req.description.lower() for term in verifiable_terms)
                
                if not found_verifiable:
                    result["issues"].append({
                        "type": "verifiability",
                        "message": "Requirement may not be easily verifiable"
                    })
                    result["passed"] = False
            
            # Check for clarity
            if criteria.get("check_clarity", False):
                vague_terms = ["etc", "and so on", "and/or", "tbd", "maybe", "should", "could"]
                found_vague = any(term in req.description.lower() for term in vague_terms)
                
                if found_vague:
                    result["issues"].append({
                        "type": "clarity",
                        "message": "Requirement contains vague or ambiguous terms"
                    })
                    result["passed"] = False
            
            # Add to results
            validation_results.append(result)
        
        # Summary
        passed_count = sum(1 for r in validation_results if r["passed"])
        
        return {
            "project_id": project_id,
            "validation_date": datetime.now().timestamp(),
            "results": validation_results,
            "summary": {
                "total_requirements": len(validation_results),
                "passed": passed_count,
                "failed": len(validation_results) - passed_count,
                "pass_percentage": (passed_count / len(validation_results)) * 100 if validation_results else 0
            },
            "criteria": criteria
        }
    except Exception as e:
        return {"error": f"Failed to validate project: {str(e)}"}


@mcp_capability(
    name="prometheus_integration",
    description="Planning and strategic analysis integration with Prometheus"
)
class PrometheusIntegrationCapability:
    """Capability for integration with Prometheus planning and analysis."""
    pass


@mcp_tool(
    category="prometheus_integration",
    name="analyze_requirements",
    description="Analyze requirements for planning readiness using Prometheus"
)
async def analyze_requirements(
    project_id: str,
    requirements_manager=None,
    prometheus_connector=None
) -> Dict[str, Any]:
    """
    Analyze requirements for planning readiness using Prometheus.
    
    Args:
        project_id: ID of the project to analyze
        requirements_manager: Injected RequirementsManager instance
        prometheus_connector: Injected Prometheus connector
        
    Returns:
        Dict containing analysis results
    """
    if not requirements_manager:
        return {"error": "Requirements manager not available"}
    
    if not prometheus_connector:
        return {"error": "Prometheus connector not available"}
    
    try:
        # Ensure project exists
        project = requirements_manager.get_project(project_id)
        if not project:
            return {"error": f"Project {project_id} not found"}
        
        # Analyze requirements
        analysis = await prometheus_connector.prepare_requirements_for_planning(project_id)
        return analysis
    except Exception as e:
        return {"error": f"Failed to analyze requirements: {str(e)}"}


@mcp_tool(
    category="prometheus_integration",
    name="create_plan",
    description="Create a strategic plan for the project using Prometheus"
)
async def create_plan(
    project_id: str,
    requirements_manager=None,
    prometheus_connector=None
) -> Dict[str, Any]:
    """
    Create a strategic plan for the project using Prometheus.
    
    Args:
        project_id: ID of the project to plan
        requirements_manager: Injected RequirementsManager instance
        prometheus_connector: Injected Prometheus connector
        
    Returns:
        Dict containing plan creation results
    """
    if not requirements_manager:
        return {"error": "Requirements manager not available"}
    
    if not prometheus_connector:
        return {"error": "Prometheus connector not available"}
    
    try:
        # Ensure project exists
        project = requirements_manager.get_project(project_id)
        if not project:
            return {"error": f"Project {project_id} not found"}
        
        # Create plan
        plan_result = await prometheus_connector.create_plan(project_id)
        return plan_result
    except Exception as e:
        return {"error": f"Failed to create plan: {str(e)}"}


# Tool collections for easy import
requirements_management_tools = [
    create_project,
    get_project,
    list_projects,
    create_requirement,
    get_requirement,
    update_requirement
]

requirement_tracing_tools = [
    create_trace,
    list_traces
]

requirement_validation_tools = [
    validate_project
]

prometheus_integration_tools = [
    analyze_requirements,
    create_plan
]

# Export all tools
__all__ = [
    "RequirementsManagementCapability",
    "RequirementTracingCapability", 
    "RequirementValidationCapability",
    "PrometheusIntegrationCapability",
    "requirements_management_tools",
    "requirement_tracing_tools",
    "requirement_validation_tools",
    "prometheus_integration_tools",
    "create_project",
    "get_project",
    "list_projects",
    "create_requirement",
    "get_requirement",
    "update_requirement",
    "create_trace",
    "list_traces",
    "validate_project",
    "analyze_requirements",
    "create_plan"
]

def get_all_tools(component_manager=None):
    """Get all Telos MCP tools."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, returning empty tools list")
        return []
        
    tools = []
    
    # Telos tools
    tools.append(create_project._mcp_tool_meta.to_dict())
    tools.append(get_project._mcp_tool_meta.to_dict())
    tools.append(list_projects._mcp_tool_meta.to_dict())
    tools.append(create_requirement._mcp_tool_meta.to_dict())
    tools.append(get_requirement._mcp_tool_meta.to_dict())
    tools.append(update_requirement._mcp_tool_meta.to_dict())
    tools.append(create_trace._mcp_tool_meta.to_dict())
    tools.append(list_traces._mcp_tool_meta.to_dict())
    tools.append(validate_project._mcp_tool_meta.to_dict())
    tools.append(analyze_requirements._mcp_tool_meta.to_dict())
    tools.append(create_plan._mcp_tool_meta.to_dict())
    
    logger.info(f"get_all_tools returning {len(tools)} Telos MCP tools")
    return tools