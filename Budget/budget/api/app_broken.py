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
from shared.utils.logging_setup import setup_component_logger
from shared.utils.shutdown import component_lifespan
from shared.utils.env_config import get_component_config

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
logger = setup_component_logger("budget")

# Global state for Hermes registration
is_registered_with_hermes = False
hermes_registration = None
heartbeat_task = None

# Define startup and cleanup functions for lifespan
async def startup_tasks():
    """Initialize Budget services."""
    global hermes_client, is_registered_with_hermes, hermes_registration, heartbeat_task
    logger.info("Initializing Budget API server")
    
    # Initialize database
    db_manager.initialize()
    
    # Construct the endpoint URL based on the port
    config = get_component_config()
    port = config.budget.port if hasattr(config, 'budget') else int(os.environ.get("BUDGET_PORT"))
    hostname = os.environ.get("BUDGET_HOST", "localhost")
    endpoint = f"http://{hostname}:{port}"
    
    logger.info(f"Registering with Hermes using endpoint: {endpoint}")
    
    try:
        hermes_client = await register_budget_component(endpoint)
        if hermes_client:
            logger.info("Successfully registered with Hermes")
        else:
            logger.warning("Failed to register with Hermes, continuing startup")
    except Exception as e:
        logger.error(f"Error registering with Hermes: {str(e)}")
    
    # Initialize WebSocket routes
    from budget.core.engine import get_budget_engine
    budget_engine = get_budget_engine()
    add_websocket_routes(app, ws_manager, budget_engine)
    
    # Initialize FastMCP if available
    try:
        from tekton.mcp.fastmcp import MCPClient
        from tekton.mcp.fastmcp.utils.tooling import ToolRegistry
        from budget.core.mcp import register_budget_tools, register_analytics_tools
        
        # Create tool registry
        tool_registry = ToolRegistry()
        
        # Register budget tools with the registry
        await register_budget_tools(budget_engine, tool_registry)
        await register_analytics_tools(budget_engine, tool_registry)
        
        logger.info("Successfully registered FastMCP tools")
    except ImportError:
        logger.warning("FastMCP not available, continuing with legacy MCP")
    except Exception as e:
        logger.error(f"Error registering FastMCP tools: {str(e)}")
    
    # Register with Hermes using standardized registration
    hermes_registration = HermesRegistration()
    is_registered_with_hermes = await hermes_registration.register_component(
        component_name="budget",
        port=8013,
        version="0.1.0",
        capabilities=[
            "budget_allocation",
            "cost_tracking",
            "usage_monitoring",
            "assistant_service",
            "websocket_support"
        ],
        metadata={
            "database": "enabled",
            "assistant": "enabled",
            "websocket": "enabled"
        }
    )
    
    # Start heartbeat task if registered
    if is_registered_with_hermes:
        heartbeat_task = asyncio.create_task(
            heartbeat_loop(hermes_registration, "budget", interval=30)
        )
        logger.info("Started Hermes heartbeat task")
    
    logger.info("Budget API server initialized with WebSocket support")

async def cleanup_tasks():
    """Cleanup Budget resources."""
    global hermes_client, heartbeat_task
    logger.info("Shutting down Budget API server")
    
    # Cancel heartbeat task
    if heartbeat_task:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
    
    # Deregister from Hermes
    if hermes_registration and is_registered_with_hermes:
        await hermes_registration.deregister("budget")
    
    # Unregister from Hermes service registry (legacy)
    if hermes_client:
        logger.info("Unregistering from Hermes")
        try:
            await hermes_client.close()
            logger.info("Successfully unregistered from Hermes")
        except Exception as e:
            logger.error(f"Error unregistering from Hermes: {str(e)}")
    
    # Clean up WebSocket connections
    ws_manager.cleanup()
    logger.info("WebSocket connections cleaned up")
    
    # Close database connections
    db_manager.close()
    
    logger.info("Budget API server shutdown complete")

# Create FastAPI app with proper URL paths following Single Port Architecture
app = FastAPI(
    title="Budget API",
    description="API for Tekton Budget component",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=component_lifespan(
        "budget",
        startup_tasks,
        [cleanup_tasks],
        port=8013
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

# Include routers
app.include_router(budget_router)
app.include_router(mcp_router)
app.include_router(assistant_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    debug_log.info("budget_api", "Health check endpoint called")
    
    # Use standardized health response
    return create_health_response(
        component_name="budget",
        port=8013,
        version="0.1.0",
        status="healthy",
        registered=is_registered_with_hermes,
        details={
            "services": ["budget_allocation", "cost_tracking", "assistant_service"]
        }
    )

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with basic information.
    """
    debug_log.info("budget_api", "Root endpoint called")
    return {
        "component": "budget",
        "description": "Tekton Budget Component API",
        "version": "0.1.0",
        "status": "active"
    }

# Import WebSocket manager and handlers
from budget.api.websocket_server import (
    ConnectionManager, add_websocket_routes,
    notify_budget_update, notify_allocation_update, notify_alert, notify_price_update
)

# Create WebSocket connection manager
ws_manager = ConnectionManager()

# Global variable to store Hermes registration client
hermes_client = None

# Legacy startup handler (removed - using lifespan instead)
# The startup logic is now in startup_tasks() function above
    """
    Initialization tasks on application startup.
    """
    global hermes_client, is_registered_with_hermes, hermes_registration, heartbeat_task
    logger.info("Initializing Budget API server")
    
    # Initialize database
    db_manager.initialize()
    
    # Construct the endpoint URL based on the port
    config = get_component_config()
    port = config.budget.port if hasattr(config, 'budget') else int(os.environ.get("BUDGET_PORT"))
    hostname = os.environ.get("BUDGET_HOST", "localhost")
    endpoint = f"http://{hostname}:{port}"
    
    logger.info(f"Registering with Hermes using endpoint: {endpoint}")
    
    try:
        hermes_client = await register_budget_component(endpoint)
        if hermes_client:
            logger.info("Successfully registered with Hermes")
        else:
            logger.warning("Failed to register with Hermes, continuing startup")
    except Exception as e:
        logger.error(f"Error registering with Hermes: {str(e)}")
    
    # Initialize WebSocket routes
    from budget.core.engine import get_budget_engine
    budget_engine = get_budget_engine()
    add_websocket_routes(app, ws_manager, budget_engine)
    
    # Initialize FastMCP if available
    try:
        from tekton.mcp.fastmcp import MCPClient
        from tekton.mcp.fastmcp.utils.tooling import ToolRegistry
        from budget.core.mcp import register_budget_tools, register_analytics_tools
        
        # Create tool registry
        tool_registry = ToolRegistry()
        
        # Register budget tools with the registry
        await register_budget_tools(budget_engine, tool_registry)
        await register_analytics_tools(budget_engine, tool_registry)
        
        logger.info("Successfully registered FastMCP tools")
    except ImportError:
        logger.warning("FastMCP not available, continuing with legacy MCP")
    except Exception as e:
        logger.error(f"Error registering FastMCP tools: {str(e)}")
    
    # Register with Hermes using standardized registration
    hermes_registration = HermesRegistration()
    is_registered_with_hermes = await hermes_registration.register_component(
        component_name="budget",
        port=8013,
        version="0.1.0",
        capabilities=[
            "budget_allocation",
            "cost_tracking",
            "usage_monitoring",
            "assistant_service",
            "websocket_support"
        ],
        metadata={
            "database": "enabled",
            "assistant": "enabled",
            "websocket": "enabled"
        }
    )
    
    # Start heartbeat task if registered
    if is_registered_with_hermes:
        heartbeat_task = asyncio.create_task(
            heartbeat_loop(hermes_registration, "budget", interval=30)
        )
        logger.info("Started Hermes heartbeat task")
    
    logger.info("Budget API server initialized with WebSocket support")

# Legacy shutdown handler (removed - using lifespan instead)
# The shutdown logic is now in cleanup_tasks() function above
    """
    Cleanup tasks on application shutdown.
    """
    global hermes_client, heartbeat_task
    logger.info("Shutting down Budget API server")
    
    # Cancel heartbeat task
    if heartbeat_task:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
    
    # Deregister from Hermes
    if hermes_registration and is_registered_with_hermes:
        await hermes_registration.deregister("budget")
    
    # Unregister from Hermes service registry (legacy)
    if hermes_client:
        logger.info("Unregistering from Hermes")
        try:
            await hermes_client.close()
            logger.info("Successfully unregistered from Hermes")
        except Exception as e:
            logger.error(f"Error unregistering from Hermes: {str(e)}")
    
    # Clean up WebSocket connections
    ws_manager.cleanup()
    logger.info("WebSocket connections cleaned up")
    
    # Close database connections
    db_manager.close()
    
    logger.info("Budget API server shutdown complete")

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration
    config = get_component_config()
    port = config.budget.port if hasattr(config, 'budget') else int(os.environ.get("BUDGET_PORT"))
    
    # Configure uvicorn with socket reuse
    uvicorn.run(
        "budget.api.app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        # Enable socket reuse to prevent port binding issues
        server_header=False,
        access_log=False,
        use_colors=True
    )