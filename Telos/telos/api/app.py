"""
FastAPI application for the Telos API that provides HTTP, WebSocket, and Events interfaces.

This module provides a single-port API for requirements management, tracking, validation,
and other requirements-related capabilities following the Tekton Single Port Architecture.
"""

import os
import sys
import logging
import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Query, Path, Depends, Body, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import Field
from tekton.models.base import TektonBaseModel

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utils
from shared.utils.global_config import GlobalConfig
from shared.utils.logging_setup import setup_component_logging as setup_component_logger
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)

# Use shared logger
logger = setup_component_logger("telos")

from ..core.telos_component import TelosComponent
from ..core.project import Project
from ..core.requirement import Requirement
from .. import __version__

# Create component instance (singleton)
component = TelosComponent()

# Request models
class ProjectCreateRequest(TektonBaseModel):
    name: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ProjectUpdateRequest(TektonBaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class RequirementCreateRequest(TektonBaseModel):
    title: str
    description: str
    requirement_type: Optional[str] = "functional"
    priority: Optional[str] = "medium"
    status: Optional[str] = "new"
    tags: Optional[List[str]] = None
    parent_id: Optional[str] = None
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None

class RequirementUpdateRequest(TektonBaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirement_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    parent_id: Optional[str] = None
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class RequirementRefinementRequest(TektonBaseModel):
    feedback: str
    auto_update: Optional[bool] = False

class RequirementValidationRequest(TektonBaseModel):
    criteria: Dict[str, Any]

class ProjectExportRequest(TektonBaseModel):
    format: str = "json"  # json, markdown, pdf, etc.
    sections: Optional[List[str]] = None

class ProjectImportRequest(TektonBaseModel):
    data: Dict[str, Any]
    format: str = "json"
    merge_strategy: Optional[str] = "replace"  # replace, merge, or skip

class TraceCreateRequest(TektonBaseModel):
    source_id: str
    target_id: str
    trace_type: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TraceUpdateRequest(TektonBaseModel):
    trace_type: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class WebSocketRequest(TektonBaseModel):
    type: str
    source: str = "client"
    target: str = "server"
    timestamp: Optional[float] = None
    payload: Dict[str, Any]

class WebSocketResponse(TektonBaseModel):
    type: str
    source: str = "server"
    target: str = "client"
    timestamp: float
    payload: Dict[str, Any]

async def startup_callback():
    """Initialize component during startup."""
    # Initialize the component (registers with Hermes, etc.)
    await component.initialize(
        capabilities=component.get_capabilities(),
        metadata=component.get_metadata()
    )
    
    # Initialize FastMCP integration
    try:
        from tekton.mcp.fastmcp.server import FastMCPServer
        from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints
        from ..core.mcp.tools import (
            requirements_management_tools,
            requirement_tracing_tools,
            requirement_validation_tools,
            prometheus_integration_tools
        )
        
        # Create FastMCP server
        fastmcp_server = FastMCPServer(
            name="telos",
            version=__version__, 
            description="Telos Requirements Management MCP Server"
        )
        
        # Tools are already registered by the @mcp_tool decorator
        # No need to manually register them
        
        # Create MCP router
        mcp_router = APIRouter(prefix="/api/mcp/v2")
        add_mcp_endpoints(mcp_router, fastmcp_server)
        
        # Add custom health endpoint
        @mcp_router.get("/health")
        async def fastmcp_health():
            """Health check endpoint for FastMCP."""
            return {
                "status": "healthy",
                "service": "telos-fastmcp-integrated",
                "version": "1.0.0",
                "tools_registered": len(fastmcp_server._tools),
                "capabilities_registered": len(fastmcp_server._capabilities),
                "requirements_manager_available": component.requirements_manager is not None,
                "prometheus_connector_available": component.prometheus_connector is not None
            }
        
        # Include MCP router in main app
        app.include_router(mcp_router, prefix="/api/mcp/v2")
        
        logger.info(f"FastMCP integration initialized successfully")
        
    except Exception as e:
        logger.warning(f"Failed to initialize FastMCP integration: {e}")
        logger.warning("Telos will continue without FastMCP capabilities")
    
    # Initialize Hermes MCP Bridge
    try:
        from telos.core.mcp.hermes_bridge import TelosMCPBridge
        component.mcp_bridge = TelosMCPBridge(component.requirements_manager, component.prometheus_connector)
        await component.mcp_bridge.initialize()
        logger.info("Hermes MCP Bridge initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Hermes MCP Bridge: {e}")

# Create FastAPI application using component's create_app
app = component.create_app(
    startup_callback=startup_callback,
    **get_openapi_configuration(
        component_name=component.component_name.capitalize(),
        component_version=component.version,
        component_description=component.get_metadata()["description"]
    )
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create standard routers
routers = create_standard_routers(component.component_name.capitalize())

# Add infrastructure endpoints to root router
@routers.root.get("/health")
async def health():
    """Health check endpoint."""
    return component.get_health_status()

# Add ready endpoint
@routers.root.get("/ready")
async def ready():
    """Readiness check endpoint."""
    ready_check = create_ready_endpoint(
        component_name=component.component_name.capitalize(),
        component_version=component.version,
        start_time=component.global_config._start_time,
        readiness_check=lambda: component.requirements_manager is not None
    )
    return await ready_check()

# Add discovery endpoint to v1 router
@routers.v1.get("/discovery")
async def discovery():
    """Service discovery endpoint."""
    capabilities = component.get_capabilities()
    metadata = component.get_metadata()
    
    discovery_check = create_discovery_endpoint(
        component_name=component.component_name.capitalize(),
        component_version=component.version,
        component_description=metadata["description"],
        endpoints=[
            EndpointInfo(
                path="/api/v1/projects",
                method="GET",
                description="List all projects"
            ),
            EndpointInfo(
                path="/api/v1/projects",
                method="POST",
                description="Create a new project"
            ),
            EndpointInfo(
                path="/api/v1/projects/{project_id}/requirements",
                method="GET",
                description="List project requirements"
            ),
            EndpointInfo(
                path="/api/v1/projects/{project_id}/requirements",
                method="POST",
                description="Create a new requirement"
            ),
            EndpointInfo(
                path="/api/v1/projects/{project_id}/validate",
                method="POST",
                description="Validate project requirements"
            ),
            EndpointInfo(
                path="/api/v1/projects/{project_id}/export",
                method="POST",
                description="Export project"
            ),
            EndpointInfo(
                path="/ws",
                method="WEBSOCKET",
                description="WebSocket for real-time updates"
            )
        ],
        capabilities=capabilities,
        dependencies={
            "hermes": "http://localhost:8001",
            "prometheus": "http://localhost:8006"
        },
        metadata={
            **metadata,
            "websocket_endpoint": "/ws",
            "documentation": "/api/v1/docs"
        }
    )
    return await discovery_check()

@routers.root.get("/")
async def root():
    """Root endpoint - provides basic information"""
    metadata = component.get_metadata()
    return {
        "message": f"Welcome to {component.component_name.capitalize()} API",
        "version": component.version,
        "description": metadata["description"],
        "features": [
            "Requirements tracking",
            "Requirement validation",
            "Requirement tracing",
            "Prometheus integration",
            "Export/Import capabilities"
        ],
        "docs": "/api/v1/docs"
    }

# Project management endpoints
@routers.v1.get("/projects")
async def list_projects():
    """List all projects"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
        
    projects = component.requirements_manager.get_all_projects()
    
    # Prepare a simplified response
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

@routers.v1.post("/projects", status_code=201)
async def create_project(request: ProjectCreateRequest):
    """Create a new project"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    project_id = component.requirements_manager.create_project(
        name=request.name,
        description=request.description or "",
        metadata=request.metadata
    )
    
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=500, detail="Failed to create project")
    
    return {
        "project_id": project_id,
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at
    }

@routers.v1.get("/projects/{project_id}")
async def get_project(project_id: str = Path(..., title="The ID of the project to get")):
    """Get a specific project with its requirements"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Get the requirement hierarchy
    hierarchy = project.get_requirement_hierarchy()
    
    # Prepare the response
    result = project.to_dict()
    result["hierarchy"] = hierarchy
    
    return result

@routers.v1.put("/projects/{project_id}")
async def update_project(
    project_id: str = Path(..., title="The ID of the project to update"),
    request: ProjectUpdateRequest = Body(...)
):
    """Update a project"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Update the project
    updates = {}
    if request.name is not None:
        project.name = request.name
        updates["name"] = request.name
    
    if request.description is not None:
        project.description = request.description
        updates["description"] = request.description
    
    if request.metadata is not None:
        # Merge with existing metadata
        project.metadata.update(request.metadata)
        updates["metadata"] = project.metadata
    
    # Only save if there were actually updates
    if updates:
        project.updated_at = datetime.now().timestamp()
        # Save the project
        component.requirements_manager._save_project(project)
    
    return {
        "project_id": project_id,
        "updated": updates,
        "updated_at": project.updated_at
    }

@routers.v1.delete("/projects/{project_id}")
async def delete_project(project_id: str = Path(..., title="The ID of the project to delete")):
    """Delete a project"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    success = component.requirements_manager.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    return {"success": True, "project_id": project_id}

# Requirement management endpoints
@routers.v1.post("/projects/{project_id}/requirements", status_code=201)
async def create_requirement(
    project_id: str = Path(..., title="The ID of the project"),
    request: RequirementCreateRequest = Body(...)
):
    """Create a new requirement in a project"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Ensure project exists
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Create requirement
    requirement_id = component.requirements_manager.add_requirement(
        project_id=project_id,
        title=request.title,
        description=request.description,
        requirement_type=request.requirement_type,
        priority=request.priority,
        status=request.status,
        tags=request.tags,
        parent_id=request.parent_id,
        dependencies=request.dependencies,
        metadata=request.metadata,
        created_by=request.created_by
    )
    
    if not requirement_id:
        raise HTTPException(status_code=500, detail="Failed to create requirement")
    
    # Get the created requirement
    requirement = component.requirements_manager.get_requirement(project_id, requirement_id)
    
    return {
        "project_id": project_id,
        "requirement_id": requirement_id,
        "title": requirement.title,
        "created_at": requirement.created_at
    }

@routers.v1.get("/projects/{project_id}/requirements")
async def list_requirements(
    project_id: str = Path(..., title="The ID of the project"),
    status: Optional[str] = None,
    requirement_type: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None
):
    """List requirements for a project with optional filtering"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Ensure project exists
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Get requirements with optional filters
    requirements = project.get_all_requirements(
        status=status,
        requirement_type=requirement_type,
        priority=priority,
        tag=tag
    )
    
    # Convert requirements to dicts
    result = [req.to_dict() for req in requirements]
    
    return {"requirements": result, "count": len(result)}

@routers.v1.get("/projects/{project_id}/requirements/{requirement_id}")
async def get_requirement(
    project_id: str = Path(..., title="The ID of the project"),
    requirement_id: str = Path(..., title="The ID of the requirement")
):
    """Get a specific requirement"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Get the requirement
    requirement = component.requirements_manager.get_requirement(project_id, requirement_id)
    if not requirement:
        raise HTTPException(
            status_code=404, 
            detail=f"Requirement {requirement_id} not found in project {project_id}"
        )
    
    return requirement.to_dict()

@routers.v1.put("/projects/{project_id}/requirements/{requirement_id}")
async def update_requirement(
    project_id: str = Path(..., title="The ID of the project"),
    requirement_id: str = Path(..., title="The ID of the requirement"),
    request: RequirementUpdateRequest = Body(...)
):
    """Update a requirement"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Prepare updates
    updates = {}
    if request.title is not None:
        updates["title"] = request.title
    
    if request.description is not None:
        updates["description"] = request.description
    
    if request.requirement_type is not None:
        updates["requirement_type"] = request.requirement_type
    
    if request.priority is not None:
        updates["priority"] = request.priority
    
    if request.status is not None:
        updates["status"] = request.status
    
    if request.tags is not None:
        updates["tags"] = request.tags
    
    if request.parent_id is not None:
        updates["parent_id"] = request.parent_id
    
    if request.dependencies is not None:
        updates["dependencies"] = request.dependencies
    
    if request.metadata is not None:
        # Get current requirement to merge metadata
        current_req = component.requirements_manager.get_requirement(project_id, requirement_id)
        if current_req:
            # Merge with existing metadata
            merged_metadata = dict(current_req.metadata)
            merged_metadata.update(request.metadata)
            updates["metadata"] = merged_metadata
        else:
            updates["metadata"] = request.metadata
    
    # Only update if there are changes
    if not updates:
        return {"message": "No updates provided", "requirement_id": requirement_id}
    
    # Update the requirement
    success = component.requirements_manager.update_requirement(
        project_id=project_id,
        requirement_id=requirement_id,
        **updates
    )
    
    if not success:
        raise HTTPException(
            status_code=404, 
            detail=f"Requirement {requirement_id} not found in project {project_id}"
        )
    
    # Get the updated requirement
    updated_requirement = component.requirements_manager.get_requirement(project_id, requirement_id)
    
    return {
        "requirement_id": requirement_id,
        "updated": list(updates.keys()),
        "updated_at": updated_requirement.updated_at if updated_requirement else None
    }

@routers.v1.delete("/projects/{project_id}/requirements/{requirement_id}")
async def delete_requirement(
    project_id: str = Path(..., title="The ID of the project"),
    requirement_id: str = Path(..., title="The ID of the requirement")
):
    """Delete a requirement"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Ensure project exists
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Delete the requirement
    success = project.delete_requirement(requirement_id)
    if not success:
        raise HTTPException(
            status_code=404, 
            detail=f"Requirement {requirement_id} not found in project {project_id}"
        )
    
    # Save the project after deletion
    component.requirements_manager._save_project(project)
    
    return {"success": True, "project_id": project_id, "requirement_id": requirement_id}

# Requirement refinement endpoints
@routers.v1.post("/projects/{project_id}/requirements/{requirement_id}/refine")
async def refine_requirement(
    project_id: str = Path(..., title="The ID of the project"),
    requirement_id: str = Path(..., title="The ID of the requirement"),
    request: RequirementRefinementRequest = Body(...)
):
    """Refine a requirement with feedback"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Get the requirement
    requirement = component.requirements_manager.get_requirement(project_id, requirement_id)
    if not requirement:
        raise HTTPException(
            status_code=404, 
            detail=f"Requirement {requirement_id} not found in project {project_id}"
        )
    
    try:
        # Try to import refinement module
        from ..ui.interactive_refine import refine_requirement_with_feedback
        
        # Refine the requirement
        refined = await refine_requirement_with_feedback(
            requirements_manager=component.requirements_manager,
            project_id=project_id,
            requirement_id=requirement_id,
            feedback=request.feedback,
            auto_update=request.auto_update
        )
        
        return refined
    except ImportError:
        # Fallback if refinement module not available
        logger.warning("Interactive refinement module not available")
        
        # Record the feedback in requirement history
        requirement._add_history_entry(
            action="feedback", 
            description=f"Feedback received: {request.feedback}"
        )
        
        # Update the requirement to save history
        component.requirements_manager.update_requirement(
            project_id=project_id,
            requirement_id=requirement_id,
            history=requirement.history
        )
        
        return {
            "requirement_id": requirement_id,
            "status": "feedback_recorded",
            "message": "Refinement module not available, feedback recorded in history"
        }
    except Exception as e:
        logger.error(f"Error refining requirement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Requirement validation endpoints
@routers.v1.post("/projects/{project_id}/validate")
async def validate_project(
    project_id: str = Path(..., title="The ID of the project"),
    request: RequirementValidationRequest = Body(...)
):
    """Validate a project's requirements against provided criteria"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Ensure project exists
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    try:
        # Get all requirements
        requirements = project.get_all_requirements()
        
        # Basic validation results
        validation_results = []
        
        # Validation criteria
        criteria = request.criteria
        
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
        logger.error(f"Error validating requirements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Requirement tracing endpoints
@routers.v1.get("/projects/{project_id}/traces")
async def list_traces(project_id: str = Path(..., title="The ID of the project")):
    """List all requirement traces for a project"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Ensure project exists
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Get traces from project metadata
    traces = project.metadata.get("traces", [])
    
    return {"traces": traces, "count": len(traces)}

@routers.v1.post("/projects/{project_id}/traces", status_code=201)
async def create_trace(
    project_id: str = Path(..., title="The ID of the project"),
    request: TraceCreateRequest = Body(...)
):
    """Create a new trace between requirements"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Ensure project exists
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Verify source and target requirements exist
    source_req = project.get_requirement(request.source_id)
    target_req = project.get_requirement(request.target_id)
    
    if not source_req:
        raise HTTPException(status_code=404, detail=f"Source requirement {request.source_id} not found")
    
    if not target_req:
        raise HTTPException(status_code=404, detail=f"Target requirement {request.target_id} not found")
    
    # Create trace
    trace_id = f"trace_{int(datetime.now().timestamp())}"
    
    trace = {
        "trace_id": trace_id,
        "source_id": request.source_id,
        "target_id": request.target_id,
        "trace_type": request.trace_type,
        "description": request.description,
        "created_at": datetime.now().timestamp(),
        "metadata": request.metadata or {}
    }
    
    # Add to project metadata
    if "traces" not in project.metadata:
        project.metadata["traces"] = []
    
    project.metadata["traces"].append(trace)
    
    # Save the project
    component.requirements_manager._save_project(project)
    
    return {
        "trace_id": trace_id,
        "source_id": request.source_id,
        "target_id": request.target_id
    }

@routers.v1.get("/projects/{project_id}/traces/{trace_id}")
async def get_trace(
    project_id: str = Path(..., title="The ID of the project"),
    trace_id: str = Path(..., title="The ID of the trace")
):
    """Get a specific trace"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Ensure project exists
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Find the trace
    traces = project.metadata.get("traces", [])
    trace = next((t for t in traces if t.get("trace_id") == trace_id), None)
    
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
    
    return trace

@routers.v1.put("/projects/{project_id}/traces/{trace_id}")
async def update_trace(
    project_id: str = Path(..., title="The ID of the project"),
    trace_id: str = Path(..., title="The ID of the trace"),
    request: TraceUpdateRequest = Body(...)
):
    """Update a trace"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Ensure project exists
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Find the trace
    traces = project.metadata.get("traces", [])
    trace_index = next((i for i, t in enumerate(traces) if t.get("trace_id") == trace_id), None)
    
    if trace_index is None:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
    
    # Update the trace
    trace = traces[trace_index]
    updates = {}
    
    if request.trace_type is not None:
        trace["trace_type"] = request.trace_type
        updates["trace_type"] = request.trace_type
    
    if request.description is not None:
        trace["description"] = request.description
        updates["description"] = request.description
    
    if request.metadata is not None:
        # Merge with existing metadata
        if "metadata" not in trace:
            trace["metadata"] = {}
        trace["metadata"].update(request.metadata)
        updates["metadata"] = trace["metadata"]
    
    # Update timestamp
    trace["updated_at"] = datetime.now().timestamp()
    
    # Save the project
    component.requirements_manager._save_project(project)
    
    return {
        "trace_id": trace_id,
        "updated": updates,
        "updated_at": trace["updated_at"]
    }

@routers.v1.delete("/projects/{project_id}/traces/{trace_id}")
async def delete_trace(
    project_id: str = Path(..., title="The ID of the project"),
    trace_id: str = Path(..., title="The ID of the trace")
):
    """Delete a trace"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Ensure project exists
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Find the trace
    traces = project.metadata.get("traces", [])
    
    # Find and remove the trace
    updated_traces = [t for t in traces if t.get("trace_id") != trace_id]
    
    if len(updated_traces) == len(traces):
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
    
    # Update project metadata
    project.metadata["traces"] = updated_traces
    
    # Save the project
    component.requirements_manager._save_project(project)
    
    return {"success": True, "trace_id": trace_id}

# Project export/import endpoints
@routers.v1.post("/projects/{project_id}/export")
async def export_project(
    project_id: str = Path(..., title="The ID of the project"),
    request: ProjectExportRequest = Body(...)
):
    """Export a project in the specified format"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Ensure project exists
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Get all requirements
    requirements = project.get_all_requirements()
    
    # Get project hierarchy
    hierarchy = project.get_requirement_hierarchy()
    
    # Handle different export formats
    if request.format.lower() == "json":
        # JSON export (full data)
        export_data = project.to_dict()
        
        # Add hierarchy
        export_data["hierarchy"] = hierarchy
        
        return export_data
    
    elif request.format.lower() == "markdown":
        # Markdown export
        from io import StringIO
        
        output = StringIO()
        
        # Project header
        output.write(f"# {project.name}\n\n")
        
        if project.description:
            output.write(f"{project.description}\n\n")
        
        # Project metadata if requested
        if not request.sections or "metadata" in request.sections:
            output.write("## Project Metadata\n\n")
            output.write(f"- **Project ID:** {project.project_id}\n")
            output.write(f"- **Created:** {datetime.fromtimestamp(project.created_at).strftime('%Y-%m-%d %H:%M:%S')}\n")
            output.write(f"- **Last Updated:** {datetime.fromtimestamp(project.updated_at).strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            if project.metadata:
                output.write("- **Custom Metadata:**\n")
                for key, value in project.metadata.items():
                    if key != "traces":  # Skip traces, they'll be in their own section
                        output.write(f"  - **{key}:** {value}\n")
            
            output.write("\n")
        
        # Requirements section
        if not request.sections or "requirements" in request.sections:
            output.write("## Requirements\n\n")
            
            # Group requirements by type
            req_by_type = {}
            for req in requirements:
                req_type = req.requirement_type
                if req_type not in req_by_type:
                    req_by_type[req_type] = []
                req_by_type[req_type].append(req)
            
            # Output each type
            for req_type, reqs in req_by_type.items():
                output.write(f"### {req_type.title()} Requirements\n\n")
                
                for req in reqs:
                    output.write(f"#### {req.title} (ID: {req.requirement_id})\n\n")
                    output.write(f"{req.description}\n\n")
                    output.write(f"- **Status:** {req.status}\n")
                    output.write(f"- **Priority:** {req.priority}\n")
                    
                    if req.tags:
                        output.write(f"- **Tags:** {', '.join(req.tags)}\n")
                    
                    if req.dependencies:
                        output.write(f"- **Dependencies:** {', '.join(req.dependencies)}\n")
                    
                    output.write("\n")
        
        # Traces section
        if (not request.sections or "traces" in request.sections) and "traces" in project.metadata:
            output.write("## Requirement Traces\n\n")
            
            traces = project.metadata.get("traces", [])
            for trace in traces:
                source_id = trace.get("source_id")
                target_id = trace.get("target_id")
                trace_type = trace.get("trace_type")
                
                # Get requirement titles
                source_req = project.get_requirement(source_id)
                target_req = project.get_requirement(target_id)
                
                source_title = source_req.title if source_req else f"Unknown ({source_id})"
                target_title = target_req.title if target_req else f"Unknown ({target_id})"
                
                output.write(f"- **{trace_type}:** {source_title} → {target_title}\n")
                
                if trace.get("description"):
                    output.write(f"  - {trace.get('description')}\n")
                
                output.write("\n")
        
        # Convert to string
        markdown_content = output.getvalue()
        output.close()
        
        return {"format": "markdown", "content": markdown_content}
    
    else:
        # Unsupported format
        raise HTTPException(status_code=400, detail=f"Unsupported export format: {request.format}")

@routers.v1.post("/projects/import", status_code=201)
async def import_project(request: ProjectImportRequest = Body(...)):
    """Import a project from external data"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    # Handle different import formats
    if request.format.lower() == "json":
        try:
            data = request.data
            
            # Create a new project
            project_id = component.requirements_manager.create_project(
                name=data.get("name", "Imported Project"),
                description=data.get("description", ""),
                metadata=data.get("metadata", {})
            )
            
            # Get the project
            project = component.requirements_manager.get_project(project_id)
            if not project:
                raise HTTPException(status_code=500, detail="Failed to create project")
            
            # Import requirements
            imported_count = 0
            for req_id, req_data in data.get("requirements", {}).items():
                # Create requirement
                requirement = Requirement.from_dict(req_data)
                project.add_requirement(requirement)
                imported_count += 1
            
            # Save the project
            component.requirements_manager._save_project(project)
            
            return {
                "project_id": project_id,
                "name": project.name,
                "imported_requirements": imported_count
            }
        
        except Exception as e:
            logger.error(f"Error importing project: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to import project: {str(e)}")
    
    else:
        # Unsupported format
        raise HTTPException(status_code=400, detail=f"Unsupported import format: {request.format}")

# Planning endpoints (integration with Prometheus)
@routers.v1.post("/projects/{project_id}/analyze")
async def analyze_requirements(project_id: str = Path(..., title="The ID of the project")):
    """Analyze requirements for planning readiness"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    if not component.prometheus_connector:
        raise HTTPException(status_code=503, detail="Prometheus connector not initialized")
    
    # Ensure project exists
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    try:
        # Analyze requirements
        analysis = await component.prometheus_connector.prepare_requirements_for_planning(project_id)
        return analysis
    
    except Exception as e:
        logger.error(f"Error analyzing requirements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@routers.v1.post("/projects/{project_id}/plan")
async def create_plan(project_id: str = Path(..., title="The ID of the project")):
    """Create a plan for the project using Prometheus"""
    if not component.requirements_manager:
        raise HTTPException(status_code=503, detail="Requirements manager not initialized")
    
    if not component.prometheus_connector:
        raise HTTPException(status_code=503, detail="Prometheus connector not initialized")
    
    # Ensure project exists
    project = component.requirements_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    try:
        # Create plan
        plan_result = await component.prometheus_connector.create_plan(project_id)
        return plan_result
    
    except Exception as e:
        logger.error(f"Error creating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time interactions
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    
    if not component.requirements_manager:
        await websocket.send_json({
            "type": "ERROR",
            "source": "SERVER",
            "timestamp": datetime.now().timestamp(),
            "payload": {"error": "Requirements manager not initialized"}
        })
        await websocket.close()
        return
    
    client_id = f"client_{int(datetime.now().timestamp())}"
    logger.info(f"WebSocket client connected: {client_id}")
    
    # Send welcome message
    await websocket.send_json({
        "type": "WELCOME",
        "source": "SERVER",
        "timestamp": datetime.now().timestamp(),
        "payload": {
            "client_id": client_id,
            "message": "Connected to Telos Requirements Manager"
        }
    })
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            # Parse as a WebSocketRequest
            request = WebSocketRequest(**request_data)
            
            # Process based on message type
            if request.type == "REGISTER":
                # Client registration
                await websocket.send_json({
                    "type": "RESPONSE",
                    "source": "SERVER",
                    "target": request.source,
                    "timestamp": datetime.now().timestamp(),
                    "payload": {
                        "status": "registered",
                        "client_id": client_id,
                        "message": "Client registered successfully"
                    }
                })
            
            elif request.type == "STATUS":
                # Service status request
                project_count = len(component.requirements_manager.projects)
                
                await websocket.send_json({
                    "type": "RESPONSE",
                    "source": "SERVER",
                    "target": request.source,
                    "timestamp": datetime.now().timestamp(),
                    "payload": {
                        "status": "ok",
                        "service": "telos",
                        "version": component.version,
                        "project_count": project_count,
                        "prometheus_available": component.prometheus_connector.prometheus_available if component.prometheus_connector else False
                    }
                })
            
            elif request.type == "PROJECT_SUBSCRIBE":
                # Subscribe to real-time updates for a project
                project_id = request.payload.get("project_id")
                
                if not project_id:
                    await websocket.send_json({
                        "type": "ERROR",
                        "source": "SERVER",
                        "target": request.source,
                        "timestamp": datetime.now().timestamp(),
                        "payload": {"error": "Missing project_id in subscription request"}
                    })
                    continue
                
                # Check if project exists
                project = component.requirements_manager.get_project(project_id)
                if not project:
                    await websocket.send_json({
                        "type": "ERROR",
                        "source": "SERVER",
                        "target": request.source,
                        "timestamp": datetime.now().timestamp(),
                        "payload": {"error": f"Project {project_id} not found"}
                    })
                    continue
                
                # Acknowledge subscription
                await websocket.send_json({
                    "type": "RESPONSE",
                    "source": "SERVER",
                    "target": request.source,
                    "timestamp": datetime.now().timestamp(),
                    "payload": {
                        "status": "subscribed",
                        "project_id": project_id,
                        "message": f"Subscribed to updates for project {project_id}"
                    }
                })
                
                # TODO: Implement real subscription mechanism
                # For now, just acknowledge the request
            
            else:
                # Unsupported request type
                await websocket.send_json({
                    "type": "ERROR",
                    "source": "SERVER",
                    "target": request.source,
                    "timestamp": datetime.now().timestamp(),
                    "payload": {"error": f"Unsupported request type: {request.type}"}
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "ERROR",
                "source": "SERVER",
                "timestamp": datetime.now().timestamp(),
                "payload": {"error": str(e)}
            })
        except:
            pass

# Mount standard routers
mount_standard_routers(app, routers)

# Import and include MCP router if available
try:
    from telos.api.fastmcp_endpoints import mcp_router
    app.include_router(mcp_router)
    logger.info("FastMCP endpoints added to Telos API")
except ImportError as e:
    logger.warning(f"FastMCP endpoints not available: {e}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for API"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )


if __name__ == "__main__":
    from shared.utils.socket_server import run_component_server
    
    # Get port from GlobalConfig
    global_config = GlobalConfig.get_instance()
    port = global_config.config.telos.port
    
    run_component_server(
        component_name="telos",
        app_module="telos.api.app",
        default_port=port,
        reload=False
    )