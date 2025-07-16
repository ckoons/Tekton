#!/usr/bin/env python3
"""
Apollo API Server

This module implements the API server for the Apollo component,
following the Single Port Architecture pattern.
"""

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Initialize Tekton environment before other imports
try:
    from shared.utils.tekton_startup import tekton_component_startup
    # Load environment variables from Tekton's three-tier system
    tekton_component_startup("apollo")
except ImportError as e:
    print(f"[APOLLO] Could not load Tekton environment manager: {e}")
    print(f"[APOLLO] Continuing with system environment variables")

# Import shared utilities
from shared.utils.global_config import GlobalConfig
from shared.utils.logging_setup import setup_component_logging
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)

# Import Apollo component
from apollo.core.apollo_component import ApolloComponent

# Import API routes
from apollo.api.routes import api_router, ws_router, metrics_router
from apollo.api.endpoints.mcp import mcp_router

# Use shared logger
logger = setup_component_logging("apollo")

# Create component instance (singleton)
component = ApolloComponent()


async def startup_callback():
    """Initialize Apollo-specific components during startup."""
    # Initialize the component (registers with Hermes, etc.)
    await component.initialize(
        capabilities=component.get_capabilities(),
        metadata=component.get_metadata()
    )
    
    # Store apollo_manager in app.state for backward compatibility with routes
    app.state.apollo_manager = component.apollo_manager
    
    # Initialize Apollo MCP Bridge
    try:
        from apollo.core.mcp.hermes_bridge import ApolloMCPBridge
        mcp_bridge = ApolloMCPBridge(component.apollo_manager)
        await mcp_bridge.initialize()
        component.mcp_bridge = mcp_bridge
        logger.info("Initialized Hermes MCP Bridge for FastMCP tools")
    except Exception as e:
        logger.warning(f"Failed to initialize MCP Bridge: {e}")

# Create FastAPI application using component's create_app
app = component.create_app(
    startup_callback=startup_callback,
    **get_openapi_configuration(
        component_name=component.component_name.upper(),
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
routers = create_standard_routers(component.component_name.upper())


# Root endpoint
@routers.root.get("/")
async def root():
    """Root endpoint for the Apollo API."""
    metadata = component.get_metadata()
    return {
        "name": f"{component.component_name.upper()} Executive Coordinator",
        "version": component.version,
        "status": "running",
        "description": metadata["description"],
        "documentation": "/api/v1/docs"
    }

# Health check endpoint  
@routers.root.get("/health")
async def health_check():
    """Check the health of the Apollo component following Tekton standards."""
    # Use component's built-in health status
    return component.get_health_status()




# Add ready endpoint
@routers.root.get("/ready")
async def ready():
    """Readiness check endpoint."""
    ready_check = create_ready_endpoint(
        component_name=component.component_name.upper(),
        component_version=component.version,
        start_time=component.global_config._start_time,
        readiness_check=lambda: component.apollo_manager is not None and component.apollo_manager.is_running
    )
    return await ready_check()

# Add discovery endpoint
@routers.v1.get("/discovery")  
async def discovery():
    """Service discovery endpoint."""
    capabilities = component.get_capabilities()
    metadata = component.get_metadata()
    metadata.update({
        "websocket_endpoint": "/ws",
        "documentation": "/api/v1/docs"
    })
    
    discovery_check = create_discovery_endpoint(
        component_name=component.component_name.upper(),
        component_version=component.version,
        component_description=metadata["description"],
        endpoints=[
            EndpointInfo(
                path="/api/v1/predict",
                method="POST",
                description="Get predictions for next user actions"
            ),
            EndpointInfo(
                path="/api/v1/context",
                method="GET",
                description="Get current context summary"
            ),
            EndpointInfo(
                path="/api/v1/budget",
                method="GET",
                description="Get token budget status"
            ),
            EndpointInfo(
                path="/api/v1/protocol/validate",
                method="POST",
                description="Validate protocol compliance"
            ),
            EndpointInfo(
                path="/ws",
                method="WEBSOCKET",
                description="WebSocket for real-time events"
            ),
            EndpointInfo(
                path="/api/v1/metrics",
                method="GET",
                description="Get system metrics"
            )
        ],
        capabilities=capabilities,
        dependencies={
            "hermes": "http://localhost:8001",
            "rhetor": "http://localhost:8003"
        },
        metadata=metadata
    )
    return await discovery_check()

# Mount standard routers
mount_standard_routers(app, routers)

# Include existing routers - these should be updated to use v1 prefix
app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router)
app.include_router(metrics_router, prefix="/api/v1")
app.include_router(mcp_router)

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    # Get port from GlobalConfig
    global_config = GlobalConfig.get_instance()
    port = global_config.config.apollo.port
    
    uvicorn.run(app, host="0.0.0.0", port=port)