"""
API Server - Main entry point for the Hermes API server.

This module provides the main application server for the Hermes API,
integrating all API endpoints and initializing required services.
"""

import os
import sys
import uvicorn
import asyncio
import time
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utilities
from shared.utils.global_config import GlobalConfig
from shared.utils.logging_setup import setup_component_logging

# Import shared API utilities
from shared.api.documentation import get_openapi_configuration
from shared.api.endpoints import create_ready_endpoint, create_discovery_endpoint, EndpointInfo
from shared.api.routers import create_standard_routers, mount_standard_routers

from hermes.core.hermes_component import HermesComponent

# Configure logging
logger = setup_component_logging("hermes")

# Component configuration
COMPONENT_NAME = "hermes"
COMPONENT_VERSION = "0.1.0"
COMPONENT_DESCRIPTION = "Central registration and messaging service for Tekton ecosystem"

# Create component instance (singleton)
component = HermesComponent()

# Import API endpoints
from hermes.api.endpoints import app as api_app
from hermes.api.database import api_router as database_router
from hermes.api.llm_endpoints import llm_router
from hermes.api.a2a_endpoints import a2a_router
from hermes.api.mcp_endpoints import mcp_router


# Startup callback for component initialization
async def startup_callback():
    """Component startup callback."""
    global component
    try:
        await component.initialize(
            capabilities=component.get_capabilities(),
            metadata=component.get_metadata()
        )
        
        # Add state to api_app for compatibility
        api_app.state.service_registry = component.service_registry
        api_app.state.message_bus = component.message_bus
        api_app.state.registration_manager = component.registration_manager
        api_app.state.database_manager = component.database_manager
        api_app.state.a2a_service = component.a2a_service
        api_app.state.mcp_service = component.mcp_service
        
        logger.info(f"Hermes API server started successfully")
    except Exception as e:
        logger.error(f"Failed to start Hermes: {e}")
        raise


# Main FastAPI application with OpenAPI configuration
app = FastAPI(
    **get_openapi_configuration(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION
    ),
    on_startup=[startup_callback]
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
routers = create_standard_routers(COMPONENT_NAME)

# Add infrastructure endpoints
@routers.root.get("/ready")
async def ready():
    """Readiness check endpoint."""
    ready_check = create_ready_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        start_time=time.time(),
        readiness_check=lambda: component and component.initialized
    )
    return await ready_check()


@routers.root.get("/discovery")
async def discovery():
    """Service discovery endpoint."""
    discovery_check = create_discovery_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION,
        endpoints=[
            EndpointInfo(path="/health", method="GET", description="Health check"),
            EndpointInfo(path="/ready", method="GET", description="Readiness check"),
            EndpointInfo(path="/discovery", method="GET", description="Service discovery"),
            EndpointInfo(path="/api/v1/registry", method="GET", description="Service registry"),
            EndpointInfo(path="/api/v1/register", method="POST", description="Register component"),
            EndpointInfo(path="/api/v1/deregister", method="POST", description="Deregister component"),
            EndpointInfo(path="/api/v1/database", method="*", description="Database services"),
            EndpointInfo(path="/api/v1/llm", method="POST", description="LLM services"),
            EndpointInfo(path="/api/v1/a2a", method="*", description="A2A services"),
            EndpointInfo(path="/api/mcp/v2", method="*", description="MCP services v2")
        ],
        capabilities=component.get_capabilities() if component else [],
        metadata=component.get_metadata() if component else {}
    )
    return await discovery_check()

# Mount standard routers
mount_standard_routers(app, routers)

# Mount API endpoints under v1
app.mount("/api", api_app)  # Keep for backward compatibility
routers.v1.mount("", api_app)  # Mount under /api/v1

# Add business logic routers to v1
api_app.include_router(database_router)
api_app.include_router(llm_router)
api_app.include_router(a2a_router)
api_app.include_router(mcp_router)


@app.get("/")
async def root():
    """Root endpoint that redirects to the API documentation."""
    return {"message": "Welcome to Hermes API. Visit /docs for API documentation."}


@app.get("/health")
async def health():
    """Health check endpoint."""
    global_config = GlobalConfig.get_instance()
    port = global_config.config.hermes.port
    
    # Get component status
    if component:
        component_status = component.get_component_status()
        health_status = "healthy" if component.initialized else "degraded"
    else:
        component_status = {}
        health_status = "degraded"
    
    return {
        "status": health_status,
        "component": COMPONENT_NAME,
        "version": COMPONENT_VERSION,
        "port": port,
        "registered": False,  # Hermes doesn't register with itself
        "services": component_status
    }


def run_server():
    """Run the Hermes API server (for backward compatibility)."""
    import uvicorn
    
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "hermes.api.app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="debug" if debug else "info"
    )


if __name__ == "__main__":
    from shared.utils.socket_server import run_component_server
    
    global_config = GlobalConfig.get_instance()
    port = global_config.config.hermes.port
    
    run_component_server(
        component_name="hermes",
        app_module="hermes.api.app",
        default_port=port,
        reload=False
    )