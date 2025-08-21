"""
Prometheus/Epimethius API Application

This module defines the FastAPI application for the Prometheus/Epimethius Planning System.
It implements the Single Port Architecture pattern with path-based routing.
"""

import os
from shared.env import TektonEnviron
import sys
import asyncio
import time
from typing import Dict, Optional
from fastapi import FastAPI, APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utilities
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.utils.env_config import get_component_config
from shared.utils.errors import StartupError
from shared.utils.startup import component_startup, StartupMetrics
from shared.utils.shutdown import GracefulShutdown

# Import shared API utilities
from shared.api.documentation import get_openapi_configuration
from shared.api.endpoints import create_ready_endpoint, create_discovery_endpoint, EndpointInfo
from shared.api.routers import create_standard_routers, mount_standard_routers

# Set up logging
logger = setup_component_logging("prometheus")

# Component configuration
COMPONENT_NAME = "prometheus"
COMPONENT_VERSION = "0.1.0"
COMPONENT_DESCRIPTION = "Strategic planning and goal management system for Tekton ecosystem"

# Global start time for readiness checks
start_time = time.time()

# Import endpoint routers
from .endpoints import planning, tasks, timelines, resources
from .endpoints import retrospective, history, improvement
from .endpoints import tracking, llm_integration
from .fastmcp_endpoints import mcp_router, fastmcp_server


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for FastAPI application lifespan events.
    
    Args:
        app: FastAPI application
    """
    # Startup: Initialize components
    logger.info("Starting Prometheus/Epimethius API...")
    
    # Get port configuration
    config = get_component_config()
    port = config.prometheus.port if hasattr(config, 'prometheus') else int(TektonEnviron.get("PROMETHEUS_PORT"))
    
    # Register with Hermes
    hermes_registration = HermesRegistration()
    heartbeat_task = None
    
    try:
        await hermes_registration.register_component(
            component_name=COMPONENT_NAME,
            port=port,
            version=COMPONENT_VERSION,
            capabilities=[
                "strategic_planning",
                "goal_management",
                "retrospective_analysis",
                "timeline_tracking",
                "resource_optimization"
            ],
            metadata={
                "description": COMPONENT_DESCRIPTION,
                "category": "planning"
            }
        )
        
        # Start heartbeat task
        if hermes_registration.is_registered:
            heartbeat_task = asyncio.create_task(heartbeat_loop(hermes_registration, "prometheus"))
        
        # Initialize FastMCP server
        try:
            await fastmcp_server.startup()
            logger.info("FastMCP server initialized successfully")
        except Exception as e:
            logger.warning(f"FastMCP server initialization failed: {e}")
        
        # Initialize Hermes MCP Bridge
        try:
            from prometheus.core.mcp.hermes_bridge import PrometheusMCPBridge
            mcp_bridge = PrometheusMCPBridge()
            await mcp_bridge.initialize()
            app.state.mcp_bridge = mcp_bridge
            logger.info("Hermes MCP Bridge initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Hermes MCP Bridge: {e}")
        
        # Initialize engines (will be implemented in future PRs)
        logger.info("Initialization complete")
        
        # Store registration for access in endpoints
        app.state.hermes_registration = hermes_registration
        
        yield
    finally:
        # Cleanup: Shutdown components
        logger.info("Shutting down Prometheus/Epimethius API...")
        
        # Cancel heartbeat task
        if heartbeat_task:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Deregister from Hermes
        if hermes_registration.is_registered:
            await hermes_registration.deregister("prometheus")
        
        # Shutdown FastMCP server
        try:
            await fastmcp_server.shutdown()
            logger.info("FastMCP server shut down successfully")
        except Exception as e:
            logger.warning(f"FastMCP server shutdown failed: {e}")
        
        # Shutdown Hermes MCP Bridge
        if hasattr(app.state, "mcp_bridge") and app.state.mcp_bridge:
            await app.state.mcp_bridge.shutdown()
            logger.info("Hermes MCP Bridge shutdown complete")
        
        # Give sockets time to close on macOS
        await asyncio.sleep(0.5)
        
        # Cleanup resources (will be implemented in future PRs)
        logger.info("Cleanup complete")


def create_app() -> FastAPI:
    """
    Create the FastAPI application.
    
    Returns:
        FastAPI application
    """
    # Get port configuration
    config = get_component_config()
    port = config.prometheus.port if hasattr(config, 'prometheus') else int(TektonEnviron.get("PROMETHEUS_PORT"))
    
    # Create the FastAPI application with OpenAPI configuration
    app = FastAPI(
        **get_openapi_configuration(
            component_name=COMPONENT_NAME,
            component_version=COMPONENT_VERSION,
            component_description=COMPONENT_DESCRIPTION
        ),
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (customize as needed)
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
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
            start_time=start_time,
            readiness_check=lambda: True  # Add proper checks when engines are implemented
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
            capabilities=[
                "strategic_planning",
                "goal_management",
                "retrospective_analysis",
                "timeline_tracking",
                "resource_optimization"
            ],
            metadata={
                "category": "planning",
                "dual_nature": "Prometheus (forward planning) + Epimethius (retrospective analysis)"
            }
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
                "details": str(exc) if TektonEnviron.get("DEBUG", "false").lower() == "true" else None
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
        return {
            "name": "Prometheus/Epimethius Planning System API",
            "version": "0.1.0",
            "status": "online",
            "docs_url": f"http://localhost:{port}/docs"
        }
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint following Tekton standards"""
        return {
            "status": "healthy",
            "component": "prometheus",
            "version": "0.1.0",
            "port": port,
            "message": "Prometheus is running normally"
        }
    
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
    import uvicorn
    
    config = get_component_config()
    port = config.prometheus.port if hasattr(config, 'prometheus') else int(TektonEnviron.get("PROMETHEUS_PORT"))
    
    uvicorn.run(app, host="0.0.0.0", port=port)