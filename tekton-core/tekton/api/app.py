"""
Tekton Core API Server

This module implements the core API server for Tekton, providing system-wide
coordination, monitoring, and management capabilities.
"""

import os
import sys
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
logger = setup_component_logger("tekton_core")

# Import TektonCore component
from tekton.core.tekton_core_component import TektonCoreComponent

# Create component instance (singleton)
component = TektonCoreComponent()

async def startup_callback():
    """Initialize component during startup."""
    # Initialize the component (registers with Hermes, etc.)
    await component.initialize(
        capabilities=component.get_capabilities(),
        metadata=component.get_metadata()
    )

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

# Mount standard routers
mount_standard_routers(app, routers)


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