"""
Sophia API Server

This module implements the Sophia API server using FastAPI with Single Port Architecture,
providing HTTP and WebSocket endpoints for accessing Sophia's capabilities.
"""

import os
import sys
import json
import asyncio
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from fastapi import FastAPI, APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

# Import Sophia core modules
from sophia.core.sophia_component import SophiaComponent
from sophia.core.intelligence_measurement import IntelligenceDimension

# Import models
from sophia.models.metrics import MetricSubmission, MetricQuery, MetricResponse, MetricAggregationQuery, MetricDefinition
from sophia.models.experiment import ExperimentCreate, ExperimentUpdate, ExperimentQuery, ExperimentResponse, ExperimentResult
from sophia.models.recommendation import RecommendationCreate, RecommendationUpdate, RecommendationQuery, RecommendationResponse
from sophia.models.intelligence import IntelligenceMeasurementCreate, IntelligenceMeasurementQuery, IntelligenceMeasurementResponse, ComponentIntelligenceProfile
from sophia.models.component import ComponentRegister, ComponentUpdate, ComponentQuery, ComponentResponse
from sophia.models.research import ResearchProjectCreate, ResearchProjectUpdate, ResearchProjectQuery, ResearchProjectResponse

# Import Sophia version
from sophia import __version__

# Set up logging
logger = setup_component_logging("sophia")

# Component configuration
COMPONENT_NAME = "sophia"
COMPONENT_VERSION = "0.1.0"
COMPONENT_DESCRIPTION = "Machine learning and continuous improvement system for Tekton ecosystem"

# Create component instance (singleton)
component = SophiaComponent()


# Startup callback for component initialization
async def startup_callback():
    """Component startup callback."""
    global component
    try:
        await component.initialize(
            capabilities=component.get_capabilities(),
            metadata=component.get_metadata()
        )
        
        # Initialize MCP bridge after component startup
        await component.initialize_mcp_bridge()
        
        logger.info(f"Sophia API server started successfully")
    except Exception as e:
        logger.error(f"Failed to start Sophia: {e}")
        raise


# Create FastAPI app with OpenAPI configuration
app = FastAPI(
    **get_openapi_configuration(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION
    ),
    on_startup=[startup_callback]
)

# Enable CORS
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
    # Check if all engines are initialized
    all_initialized = component.check_all_engines_initialized() if component else False
    
    ready_check = create_ready_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        start_time=time.time(),
        readiness_check=lambda: all_initialized
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
            EndpointInfo(path="/api/v1/metrics", method="*", description="Metrics management"),
            EndpointInfo(path="/api/v1/experiments", method="*", description="Experiment management"),
            EndpointInfo(path="/api/v1/recommendations", method="*", description="Recommendation system"),
            EndpointInfo(path="/api/v1/intelligence", method="*", description="Intelligence measurement"),
            EndpointInfo(path="/api/v1/research", method="*", description="Research project management"),
            EndpointInfo(path="/api/v1/components", method="*", description="Component management"),
            EndpointInfo(path="/ws", method="WS", description="WebSocket connection")
        ],
        capabilities=component.get_capabilities() if component else [],
        dependencies={
            "hermes": "http://localhost:8001"
        },
        metadata=component.get_metadata() if component else {}
    )
    return await discovery_check()


@routers.root.get("/health")
async def health():
    """Health check endpoint."""
    global_config = GlobalConfig.get_instance()
    port = global_config.config.sophia.port
    
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
        "registered": component.global_config.is_registered_with_hermes if component else False,
        "engines": component_status
    }


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    
    # Add to active connections
    if component:
        component.active_connections.append(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process message based on type
            message_type = data.get("type")
            
            if message_type == "ping":
                await websocket.send_json({"type": "pong", "timestamp": time.time()})
            
            elif message_type == "subscribe":
                # Handle subscription to specific event types
                event_types = data.get("event_types", [])
                await websocket.send_json({
                    "type": "subscribed",
                    "event_types": event_types,
                    "timestamp": time.time()
                })
            
            elif message_type == "metric":
                # Handle real-time metric submission
                if component and component.metrics_engine:
                    metric_data = data.get("data", {})
                    await component.metrics_engine.submit_metric(
                        component_name=metric_data.get("component_name"),
                        metric_name=metric_data.get("metric_name"),
                        value=metric_data.get("value"),
                        timestamp=metric_data.get("timestamp"),
                        tags=metric_data.get("tags", {})
                    )
                    await websocket.send_json({
                        "type": "metric_received",
                        "timestamp": time.time()
                    })
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": time.time()
                })
    
    except WebSocketDisconnect:
        # Remove from active connections
        if component and websocket in component.active_connections:
            component.active_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if component and websocket in component.active_connections:
            component.active_connections.remove(websocket)


# Import endpoint modules
from sophia.api.endpoints import (
    metrics,
    experiments,
    recommendations,
    intelligence,
    research,
    components
)

# Include endpoint routers
routers.v1.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
routers.v1.include_router(experiments.router, prefix="/experiments", tags=["Experiments"])
routers.v1.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
routers.v1.include_router(intelligence.router, prefix="/intelligence", tags=["Intelligence"])
routers.v1.include_router(research.router, prefix="/research", tags=["Research"])
routers.v1.include_router(components.router, prefix="/components", tags=["Components"])

# Import and include MCP router
try:
    from sophia.api.fastmcp_endpoints import mcp_router
    app.include_router(mcp_router)
except ImportError:
    logger.warning("FastMCP endpoints not available")

# Mount standard routers
mount_standard_routers(app, routers)

# Include custom MCP routes
try:
    from sophia.core.mcp.hermes_bridge import get_mcp_routes
    mcp_routes = get_mcp_routes()
    if mcp_routes:
        app.include_router(mcp_routes, prefix="/mcp", tags=["MCP"])
except Exception as e:
    logger.debug(f"MCP routes not available: {e}")


if __name__ == "__main__":
    from shared.utils.socket_server import run_component_server
    
    global_config = GlobalConfig.get_instance()
    port = global_config.config.sophia.port
    
    run_component_server(
        component_name="sophia",
        app_module="sophia.api.app",
        default_port=port,
        reload=False
    )