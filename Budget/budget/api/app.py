"""
Budget Component API Server

This module initializes and runs the Budget API server, which provides endpoints
for budget management, allocation, and reporting.
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Add the parent directory to sys.path to ensure package imports work correctly
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

# Import shared utils
from shared.utils.health_check import create_health_response
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.utils.shutdown import GracefulShutdown
from shared.utils.env_config import get_component_config
from shared.utils.startup import component_startup, StartupMetrics
from shared.utils.errors import StartupError
from shared.urls import hermes_url
from shared.env import TektonEnviron
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)

# Try to import debug_utils from shared if available
try:
    from shared.debug.debug_utils import debug_log, log_function
except ImportError:
    # Create a simple fallback if shared module is not available
    class DebugLog:
        def __getattr__(self, name):
            def dummy_log(*args, **kwargs):
                pass
            return dummy_log
    debug_log = DebugLog()
    
    def log_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Import API endpoints
from budget.api.endpoints import router as budget_router
from budget.api.mcp_endpoints import mcp_router
from budget.api.assistant_endpoints import router as assistant_router
from budget.api.models import ErrorResponse
from budget.data.repository import db_manager

# Import Hermes helper for service registration
from budget.utils.hermes_helper import register_budget_component

# Configure logging using shared utility
logger = setup_component_logging("budget")

# Import budget component
from budget.core.budget_component import BudgetComponent

# Create component singleton
budget_component = BudgetComponent()

# Import WebSocket manager and handlers
from budget.api.websocket_server import (
    ConnectionManager, add_websocket_routes,
    notify_budget_update, notify_allocation_update, notify_alert, notify_price_update
)

# WebSocket manager will be accessed through component

async def startup_callback():
    """Initialize Budget component (includes Hermes registration)."""
    # Initialize component (includes Hermes registration)
    await budget_component.initialize(
        capabilities=budget_component.get_capabilities(),
        metadata=budget_component.get_metadata()
    )
    
    # Component-specific MCP bridge initialization
    try:
        from tekton.mcp.fastmcp import MCPClient
        from tekton.mcp.fastmcp.utils.tooling import ToolRegistry
        from budget.core.mcp import register_budget_tools, register_analytics_tools
        
        # Create tool registry
        tool_registry = ToolRegistry(component_name="budget")
        
        # Register budget tools with the registry
        await register_budget_tools(budget_component.budget_engine, tool_registry)
        await register_analytics_tools(budget_component.budget_engine, tool_registry)
        
        logger.info("Successfully registered FastMCP tools")
        
        # Initialize Hermes MCP Bridge
        from budget.core.mcp.hermes_bridge import BudgetMCPBridge
        budget_component.mcp_bridge = BudgetMCPBridge(budget_component.budget_engine)
        await budget_component.mcp_bridge.initialize()
        logger.info("Initialized Hermes MCP Bridge for FastMCP tools")
    except ImportError:
        logger.warning("FastMCP not available, continuing with legacy MCP")
    except Exception as e:
        logger.error(f"Error registering FastMCP tools: {str(e)}")
    
    # Initialize WebSocket routes
    add_websocket_routes(app, budget_component.connection_manager, budget_component.budget_engine)

# Create FastAPI app using component
app = budget_component.create_app(
    startup_callback=startup_callback,
    **get_openapi_configuration(
        component_name="budget",
        component_version="0.1.0",
        component_description="Budget management and cost tracking component"
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
routers = create_standard_routers("budget")

# Add exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"General error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

# Health check endpoint
@routers.root.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    debug_log.info("budget_api", "Health check endpoint called")
    
    # Use standardized health response
    config = get_component_config()
    port = config.budget.port if hasattr(config, 'budget') else int(TektonEnviron.get("BUDGET_PORT", "8213"))
    
    return create_health_response(
        component_name="budget",
        port=port,
        version="0.1.0",
        status="healthy",
        registered=budget_component.global_config.is_registered_with_hermes,
        details={
            "services": ["budget_allocation", "cost_tracking", "assistant_service"]
        }
    )

# Root endpoint
@routers.root.get("/")
async def root():
    """
    Root endpoint with basic information.
    """
    debug_log.info("budget_api", "Root endpoint called")
    return {
        "component": "budget",
        "description": "Budget management and cost tracking component",
        "version": "0.1.0",
        "status": "active"
    }

# Add ready endpoint
routers.root.add_api_route(
    "/ready",
    create_ready_endpoint(
        component_name="budget",
        component_version="0.1.0",
        start_time=budget_component.global_config._start_time,
        readiness_check=lambda: budget_component.global_config.is_registered_with_hermes
    ),
    methods=["GET"]
)

# Add discovery endpoint
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name="budget",
        component_version="0.1.0",
        component_description="Budget management and cost tracking component",
        endpoints=[
            EndpointInfo(path="/api/v1/budgets", method="*", description="Budget management"),
            EndpointInfo(path="/api/v1/policies", method="*", description="Budget policies"),
            EndpointInfo(path="/api/v1/allocations", method="*", description="Budget allocations"),
            EndpointInfo(path="/api/v1/usage", method="POST", description="Usage tracking"),
            EndpointInfo(path="/api/v1/alerts", method="GET", description="Budget alerts"),
            EndpointInfo(path="/api/v1/prices", method="GET", description="Pricing information"),
            EndpointInfo(path="/api/v1/assistant", method="POST", description="LLM assistant")
        ],
        capabilities=budget_component.get_capabilities(),
        dependencies={
            "hermes": hermes_url()
        },
        metadata=budget_component.get_metadata()
    ),
    methods=["GET"]
)

# Mount standard routers
mount_standard_routers(app, routers)

# Include business routers with v1 prefix
routers.v1.include_router(budget_router)
routers.v1.include_router(assistant_router)

# Include MCP router at root (not under v1)
app.include_router(mcp_router)

# Store component in app state for access by endpoints
app.state.component = budget_component

if __name__ == "__main__":
    import uvicorn
    from shared.utils.global_config import GlobalConfig
    
    global_config = GlobalConfig.get_instance()
    default_port = global_config.config.budget.port
    
    uvicorn.run(app, host="0.0.0.0", port=default_port)