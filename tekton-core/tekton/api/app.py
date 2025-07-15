"""
Tekton Core API Server

This module implements the core API server for Tekton, providing system-wide
coordination, monitoring, and management capabilities.
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utils
from shared.utils.global_config import GlobalConfig
from shared.utils.logging_setup import setup_component_logging as setup_component_logger

# Import landmarks for code annotation
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        api_contract,
        state_checkpoint
    )
except ImportError:
    # Landmarks not available, define no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)

# Use shared logger  
from shared.utils.logging_setup import setup_component_logging
logger = setup_component_logging("tekton_core")

# Import TektonCore component
from tekton.core.tekton_core_component import TektonCoreComponent

# Import project management and merge coordination
from tekton.core.project_manager_v2 import ProjectManager
from tekton.core.merge_coordinator import MergeCoordinator, MergeState

# Import our new projects API
from tekton.api import projects as projects_v2

# Create component instance (singleton)
component = TektonCoreComponent()

# Initialize project management - use shared instance for consistency
from tekton.core.shared_instances import get_project_manager

# Architecture Decision: Single ProjectManager instance eliminates V1/V2 confusion
project_manager = get_project_manager()  # One instance, no V1/V2 confusion
merge_coordinator = MergeCoordinator()

@integration_point(
    title="TektonCore Startup Integration",
    target_component="hermes",
    protocol="HTTP Registration",
    data_flow="Component registration and capabilities publishing",
    description="Registers TektonCore with Hermes message bus during startup"
)
@architecture_decision(
    title="Tekton Self-Management on Startup",
    description="Automatically creates Tekton project for dogfooding",
    rationale="Ensures Tekton manages itself using its own project management system"
)
async def startup_callback():
    """Initialize component during startup."""
    # Initialize the component (registers with Hermes, etc.)
    await component.initialize(
        capabilities=component.get_capabilities(),
        metadata=component.get_metadata()
    )
    
    # Initialize Tekton self-management project
    logger.info("Creating Tekton self-management project")
    try:
        await project_manager._check_tekton_self_management()
        logger.info("Tekton self-management project created successfully")
    except Exception as e:
        logger.error(f"Failed to create Tekton self-management project: {e}")
        # Don't fail startup if this fails

# Create FastAPI application using component's create_app
app = component.create_app(
    startup_callback=startup_callback,
    **get_openapi_configuration(
        component_name=component.component_name.replace("_", " ").title(),
        component_version=component.version,
        component_description=component.get_metadata()["description"]
    )
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create standard routers
routers = create_standard_routers(component.component_name.replace("_", " ").title())

# Add infrastructure endpoints to root router
@api_contract(
    title="Health Check API",
    endpoint="/health",
    method="GET",
    request_schema={},
    response_schema={"status": "string", "uptime": "float", "version": "string"},
    description="Standard health check endpoint for monitoring systems"
)
@routers.root.get("/health")
async def health():
    """Health check endpoint."""
    return component.get_health_status()

# Add ready endpoint
@routers.root.get("/ready")
async def ready():
    """Readiness check endpoint."""
    ready_check = create_ready_endpoint(
        component_name=component.component_name.replace("_", " ").title(),
        component_version=component.version,
        start_time=component.global_config._start_time,
        readiness_check=lambda: component.is_ready()
    )
    return await ready_check()

# Add discovery endpoint to v1 router
@routers.v1.get("/discovery")
async def discovery():
    """Service discovery endpoint."""
    capabilities = component.get_capabilities()
    metadata = component.get_metadata()
    
    discovery_check = create_discovery_endpoint(
        component_name=component.component_name.replace("_", " ").title(),
        component_version=component.version,
        component_description=metadata["description"],
        endpoints=[
            EndpointInfo(
                path="/api/v1/components",
                method="GET",
                description="List all registered components"
            ),
            EndpointInfo(
                path="/api/v1/heartbeats",
                method="GET",
                description="Get heartbeat status for all components"
            ),
            EndpointInfo(
                path="/api/v1/resources",
                method="GET",
                description="Get resource usage for all components"
            ),
            EndpointInfo(
                path="/api/v1/dashboard",
                method="GET",
                description="Get monitoring dashboard data"
            )
        ],
        capabilities=capabilities,
        dependencies={
            "hermes": "http://localhost:8001"
        },
        metadata={
            **metadata,
            "documentation": "/api/v1/docs"
        }
    )
    return await discovery_check()

# Component registry endpoints
@routers.v1.get("/components")
async def list_components():
    """List all registered components"""
    if not component.component_registry:
        raise HTTPException(status_code=503, detail="Component registry not initialized")
    
    # Mock implementation - would connect to actual registry
    return {
        "components": [],
        "total": 0
    }


@routers.v1.get("/components/{component_name}")
async def get_component(component_name: str):
    """Get details for a specific component"""
    if not component.component_registry:
        raise HTTPException(status_code=503, detail="Component registry not initialized")
    
    # Mock implementation
    raise HTTPException(status_code=404, detail=f"Component {component_name} not found")


# Heartbeat monitoring endpoints
@routers.v1.get("/heartbeats")
async def get_heartbeats():
    """Get heartbeat status for all components"""
    if not component.heartbeat_monitor:
        raise HTTPException(status_code=503, detail="Heartbeat monitor not initialized")
    
    # Mock implementation
    return {
        "heartbeats": {},
        "healthy_count": 0,
        "unhealthy_count": 0
    }


# Resource monitoring endpoints
@routers.v1.get("/resources")
async def get_resources():
    """Get resource usage for all components"""
    if not component.resource_monitor:
        raise HTTPException(status_code=503, detail="Resource monitor not initialized")
    
    # Mock implementation
    return {
        "total_cpu": 0.0,
        "total_memory": 0.0,
        "components": {}
    }


# Dashboard endpoint
@routers.v1.get("/dashboard")
async def get_dashboard():
    """Get monitoring dashboard data"""
    if not component.monitoring_dashboard:
        raise HTTPException(status_code=503, detail="Monitoring dashboard not initialized")
    
    # Mock implementation
    return {
        "status": "operational",
        "components": [],
        "alerts": [],
        "metrics": {}
    }

# Configuration endpoints
@routers.v1.get("/config/tekton-root")
async def get_tekton_root():
    """Get the TEKTON_ROOT environment variable"""
    tekton_root = os.environ.get("TEKTON_ROOT", os.getcwd())
    return {
        "tekton_root": tekton_root
    }

# Pydantic models for merge coordination
class SubmitMergeRequest(BaseModel):
    """Request to submit a new merge request for AI worker coordination."""
    project_id: str = Field(..., description="Project identifier")
    task_id: str = Field(..., description="Task identifier")
    ai_worker: str = Field(..., description="AI worker name submitting the merge")
    branch: str = Field(..., description="Git branch with changes")
    repo_path: str = Field(..., description="Repository path for merge analysis")

class ResolveMergeRequest(BaseModel):
    """Request to resolve a merge conflict by choosing an option."""
    chosen_option: str = Field(..., description="Selected merge option identifier")
    reason: Optional[str] = Field(None, description="Reason for choosing this option")

# All project endpoints are now handled by the projects.py router at /api/projects

# Merge Coordination API Endpoints
@routers.v1.get("/merge-queue")
async def get_merge_queue():
    """Get current merge queue"""
    try:
        queue = await merge_coordinator.get_merge_queue()
        
        return {
            "queue": [
                {
                    "id": mr.id,
                    "project_id": mr.project_id,
                    "task_id": mr.task_id,
                    "ai_worker": mr.ai_worker,
                    "branch": mr.branch,
                    "state": mr.state.value,
                    "created_at": mr.created_at,
                    "analyzed_at": mr.analyzed_at,
                    "conflicts_count": len(mr.conflicts),
                    "options_count": len(mr.options)
                }
                for mr in queue
            ],
            "total": len(queue)
        }
    except Exception as e:
        logger.error(f"Failed to get merge queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@routers.v1.post("/merge-requests")
async def submit_merge_request(request: SubmitMergeRequest):
    """Submit a new merge request"""
    try:
        merge_request = await merge_coordinator.submit_merge_request(
            project_id=request.project_id,
            task_id=request.task_id,
            ai_worker=request.ai_worker,
            branch=request.branch,
            repo_path=request.repo_path
        )
        
        return {
            "id": merge_request.id,
            "state": merge_request.state.value,
            "message": f"Merge request submitted for {request.ai_worker}/{request.branch}"
        }
    except Exception as e:
        logger.error(f"Failed to submit merge request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@routers.v1.get("/merge-requests/{merge_id}")
async def get_merge_request(merge_id: str):
    """Get detailed merge request information"""
    try:
        queue = await merge_coordinator.get_merge_queue()
        
        for merge_request in queue:
            if merge_request.id == merge_id:
                return {
                    "id": merge_request.id,
                    "project_id": merge_request.project_id,
                    "task_id": merge_request.task_id,
                    "ai_worker": merge_request.ai_worker,
                    "branch": merge_request.branch,
                    "state": merge_request.state.value,
                    "conflicts": [
                        {
                            "type": c.type.value,
                            "files": c.files,
                            "description": c.description,
                            "severity": c.severity,
                            "auto_resolvable": c.auto_resolvable
                        }
                        for c in merge_request.conflicts
                    ],
                    "options": [
                        {
                            "id": o.id,
                            "ai_worker": o.ai_worker,
                            "branch": o.branch,
                            "approach": o.approach,
                            "pros": o.pros,
                            "cons": o.cons,
                            "code_quality": o.code_quality,
                            "test_coverage": o.test_coverage,
                            "files_changed": o.files_changed,
                            "lines_added": o.lines_added,
                            "lines_removed": o.lines_removed
                        }
                        for o in merge_request.options
                    ],
                    "created_at": merge_request.created_at,
                    "analyzed_at": merge_request.analyzed_at,
                    "metadata": merge_request.metadata
                }
        
        raise HTTPException(status_code=404, detail="Merge request not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get merge request {merge_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@routers.v1.post("/merge-requests/{merge_id}/resolve")
async def resolve_merge_conflict(merge_id: str, request: ResolveMergeRequest):
    """Resolve merge conflict by choosing an option"""
    try:
        success = await merge_coordinator.resolve_conflict(
            merge_id=merge_id,
            chosen_option=request.chosen_option,
            reason=request.reason
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Merge request not found")
        
        return {
            "merge_id": merge_id,
            "chosen_option": request.chosen_option,
            "message": "Merge conflict resolved"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve merge conflict: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@routers.v1.post("/merge-requests/{merge_id}/execute")
async def execute_merge(merge_id: str):
    """Execute approved merge"""
    try:
        # For MVP, we'll use current working directory as repo path
        # In production, this would be derived from the project configuration
        repo_path = os.getcwd()
        
        success = await merge_coordinator.execute_merge(merge_id, repo_path)
        
        if not success:
            raise HTTPException(status_code=404, detail="Merge request not found or not ready for execution")
        
        return {
            "merge_id": merge_id,
            "message": "Merge executed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute merge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@routers.v1.get("/merge-statistics")
async def get_merge_statistics():
    """Get merge coordination statistics"""
    try:
        stats = await merge_coordinator.get_merge_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get merge statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@routers.v1.get("/system-overview")
async def get_system_overview():
    """Get comprehensive system overview"""
    try:
        overview = await project_manager.get_system_overview()
        merge_stats = await merge_coordinator.get_merge_statistics()
        
        return {
            "projects": overview,
            "merges": merge_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get system overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount standard routers
mount_standard_routers(app, routers)

# Mount our enhanced projects API - SIMPLE
# Integration Point: Projects API Integration - Primary API integration for project management UI
app.include_router(projects_v2.router)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"[REQUEST] {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"[RESPONSE] {response.status_code}")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for API"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

@routers.root.get("/")
async def root():
    """Root endpoint."""
    metadata = component.get_metadata()
    return {
        "message": f"Welcome to {component.component_name.replace('_', ' ').title()} API",
        "version": component.version,
        "description": metadata["description"],
        "features": [
            "System coordination",
            "Component registry",
            "Heartbeat monitoring",
            "Resource monitoring",
            "System dashboard"
        ],
        "docs": "/api/v1/docs"
    }


if __name__ == "__main__":
    from shared.utils.socket_server import run_component_server
    
    # Get port from GlobalConfig
    global_config = GlobalConfig.get_instance()
    port = global_config.config.tekton_core.port
    
    run_component_server(
        component_name="tekton_core",
        app_module="tekton.api.app",
        default_port=port,
        reload=False
    )