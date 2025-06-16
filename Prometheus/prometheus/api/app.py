"""
Prometheus/Epimethius API Application

This module defines the FastAPI application for the Prometheus/Epimethius Planning System
using the standardized component patterns.
"""

import os
import sys
from typing import Dict
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utilities
from shared.utils.logging_setup import setup_component_logging
from shared.utils.global_config import GlobalConfig
from shared.api.documentation import get_openapi_configuration
from shared.api.endpoints import create_ready_endpoint, create_discovery_endpoint, EndpointInfo
from shared.api.routers import create_standard_routers, mount_standard_routers

# Import component implementation
from prometheus.core.prometheus_component import PrometheusComponent

# Import endpoint routers
from .endpoints import planning, tasks, timelines, resources
from .endpoints import retrospective, history, improvement
from .endpoints import tracking, llm_integration
from .fastmcp_endpoints import mcp_router

# Set up logging
logger = setup_component_logging("prometheus")

# Component configuration
COMPONENT_NAME = "prometheus"
COMPONENT_VERSION = "0.1.0"
COMPONENT_DESCRIPTION = "Strategic planning and goal management system for Tekton ecosystem"

# Create component instance (singleton)
prometheus = PrometheusComponent()


async def startup_callback():
    """Initialize component during startup."""
    await prometheus.initialize(
        capabilities=prometheus.get_capabilities(),
        metadata=prometheus.get_metadata()
    )


def create_app() -> FastAPI:
    """
    Create the FastAPI application using standardized patterns.
    
    Returns:
        FastAPI application
    """
    # Create app with standardized lifespan
    app = prometheus.create_app(
        startup_callback=startup_callback,
        **get_openapi_configuration(
            component_name=COMPONENT_NAME,
            component_version=COMPONENT_VERSION,
            component_description=COMPONENT_DESCRIPTION
        )
    )
    
    # Store component reference
    app.state.component = prometheus
    
    # Create standard routers
    routers = create_standard_routers(COMPONENT_NAME)
    
    # Add infrastructure endpoints
    @routers.root.get("/ready")
    async def ready():
        """Readiness check endpoint."""
        global_config = GlobalConfig.get_instance()
        ready_check = create_ready_endpoint(
            component_name=COMPONENT_NAME,
            component_version=COMPONENT_VERSION,
            start_time=global_config._start_time,
            readiness_check=lambda: prometheus.planning_engine is not None
        )
        return await ready_check()
    
    # Add discovery endpoint
    routers.v1.add_api_route(
        "/discovery",
        create_discovery_endpoint(
            component_name=COMPONENT_NAME,
            component_version=COMPONENT_VERSION,
            component_description=COMPONENT_DESCRIPTION,
            endpoints=[
                EndpointInfo(path="/health", method="GET", description="Health check"),
                EndpointInfo(path="/ready", method="GET", description="Readiness check"),
                EndpointInfo(path="/api/v1/discovery", method="GET", description="Service discovery"),
                EndpointInfo(path="/api/v1/plans", method="*", description="Strategic plans management"),
                EndpointInfo(path="/api/v1/goals", method="*", description="Goal management"),
                EndpointInfo(path="/api/v1/tasks", method="*", description="Task planning"),
                EndpointInfo(path="/api/v1/timelines", method="*", description="Timeline tracking"),
                EndpointInfo(path="/api/v1/resources", method="*", description="Resource optimization"),
                EndpointInfo(path="/api/v1/retrospectives", method="*", description="Retrospective analysis"),
                EndpointInfo(path="/api/v1/history", method="*", description="Historical analysis"),
                EndpointInfo(path="/api/v1/improvements", method="*", description="Improvement tracking"),
                EndpointInfo(path="/api/v1/tracking", method="*", description="Progress tracking"),
                EndpointInfo(path="/api/v1/llm", method="*", description="LLM integration"),
                EndpointInfo(path="/api/v1/mcp", method="*", description="MCP endpoints"),
                EndpointInfo(path="/ws", method="WS", description="WebSocket for real-time updates")
            ],
            capabilities=prometheus.get_capabilities(),
            metadata=prometheus.get_metadata()
        ),
        methods=["GET"]
    )
    
    # Mount standard routers
    mount_standard_routers(app, routers)
    
    # Add error handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.detail,
                "error_code": f"HTTP_{exc.status_code}"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": str(exc) if GlobalConfig.get_instance().debug else None
            }
        )
    
    # WebSocket events
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_json()
                # Process WebSocket data (will be implemented in future PRs)
                await websocket.send_json({"status": "received", "data": data})
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected")
    
    # Root router
    @app.get("/")
    async def root():
        config = GlobalConfig.get_instance().config
        return {
            "name": "Prometheus/Epimethius Planning System API",
            "version": COMPONENT_VERSION,
            "status": "online",
            "docs_url": f"http://localhost:{config.prometheus.port}/docs"
        }
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint following Tekton standards"""
        return prometheus.get_health_status()
    
    # Mount business logic routers under v1
    # Prometheus (forward planning) API routes
    routers.v1.include_router(planning.router, tags=["Prometheus - Planning"])
    routers.v1.include_router(tasks.router, tags=["Prometheus - Tasks"])
    routers.v1.include_router(timelines.router, tags=["Prometheus - Timelines"])
    routers.v1.include_router(resources.router, tags=["Prometheus - Resources"])
    
    # Epimethius (retrospective analysis) API routes
    routers.v1.include_router(retrospective.router, tags=["Epimethius - Retrospective"])
    routers.v1.include_router(history.router, tags=["Epimethius - History"])
    routers.v1.include_router(improvement.router, tags=["Epimethius - Improvement"])
    
    # Shared API routes
    routers.v1.include_router(tracking.router, tags=["Shared - Tracking"])
    routers.v1.include_router(llm_integration.router, tags=["Shared - LLM"])
    
    # Mount MCP API routes
    routers.v1.include_router(mcp_router, prefix="/mcp", tags=["MCP"])
    
    return app


# Create the application instance
app = create_app()


# Run the application if this module is executed directly
if __name__ == "__main__":
    from shared.utils.socket_server import run_component_server
    
    global_config = GlobalConfig.get_instance()
    port = global_config.config.prometheus.port
    
    run_component_server(
        component_name="prometheus",
        app_module="prometheus.api.app",
        default_port=port,
        reload=False
    )