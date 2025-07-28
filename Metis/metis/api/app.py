"""
Metis API Application

This module defines the FastAPI application for the Metis task management service.
It follows Tekton's Single Port Architecture pattern, exposing HTTP, WebSocket,
and Event endpoints through path-based routing.
"""

import os
import sys
import json
import asyncio
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tekton.models.base import TektonBaseModel
from typing import Dict, List, Set, Any, Optional
from uuid import UUID

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

# Import Metis component
from metis.core.metis_component import MetisComponent
from metis.api.routes import router as api_router
from metis.api.sprint_routes import sprint_router
from metis.api.schemas import WebSocketMessage, WebSocketRegistration
from metis.api.fastmcp_endpoints import mcp_router

# Set up logging
logger = setup_component_logging("metis")


# Create component instance (singleton) 
component = MetisComponent()


async def startup_callback():
    """Initialize component during startup."""
    # Initialize the component (registers with Hermes, etc.)
    await component.initialize(
        capabilities=component.get_capabilities(),
        metadata=component.get_metadata()
    )
    
    # Initialize Hermes MCP Bridge with component's task manager
    try:
        from metis.core.mcp.hermes_bridge import MetisMCPBridge
        mcp_bridge = MetisMCPBridge(component.task_manager)
        await mcp_bridge.initialize()
        component.mcp_bridge = mcp_bridge
        logger.info("Hermes MCP Bridge initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Hermes MCP Bridge: {e}")


# Create FastAPI application using component's create_app
app = component.create_app(
    startup_callback=startup_callback,
    **get_openapi_configuration(
        component_name=component.component_name,
        component_version=component.version,
        component_description=component.get_metadata()["description"]
    )
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create standard routers
routers = create_standard_routers(component.component_name)

# Add infrastructure endpoints
@routers.root.get("/ready")
async def ready():
    """Readiness check endpoint."""
    ready_check = create_ready_endpoint(
        component_name=component.component_name,
        component_version=component.version,
        start_time=component.global_config._start_time,
        readiness_check=lambda: component.task_manager is not None
    )
    return await ready_check()


@routers.root.get("/discovery")
async def discovery():
    """Service discovery endpoint."""
    capabilities = component.get_capabilities()
    metadata = component.get_metadata()
    
    discovery_check = create_discovery_endpoint(
        component_name=component.component_name,
        component_version=component.version,
        component_description=metadata["description"],
        endpoints=[
            EndpointInfo(path="/health", method="GET", description="Health check"),
            EndpointInfo(path="/ready", method="GET", description="Readiness check"),
            EndpointInfo(path="/discovery", method="GET", description="Service discovery"),
            EndpointInfo(path="/api/v1/tasks", method="GET", description="List tasks"),
            EndpointInfo(path="/api/v1/tasks", method="POST", description="Create task"),
            EndpointInfo(path="/api/v1/tasks/{id}", method="GET", description="Get task"),
            EndpointInfo(path="/api/v1/tasks/{id}", method="PUT", description="Update task"),
            EndpointInfo(path="/api/v1/tasks/{id}", method="DELETE", description="Delete task"),
            EndpointInfo(path="/api/v1/mcp", method="*", description="MCP endpoints"),
            EndpointInfo(path="/ws", method="WS", description="WebSocket for real-time updates")
        ],
        capabilities=capabilities,
        metadata={
            "category": "planning",
            "task_statuses": ["pending", "in_progress", "completed", "failed", "cancelled"],
            **metadata
        }
    )
    return await discovery_check()

# Mount standard routers
mount_standard_routers(app, routers)

# Include business logic routers (api_router already has /api/v1 prefix)
app.include_router(api_router)
app.include_router(sprint_router)
app.include_router(mcp_router, prefix="/api/v1/mcp", tags=["MCP"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint for Metis API."""
    metadata = component.get_metadata()
    return {
        "name": component.component_name.capitalize(),
        "description": metadata["description"],
        "version": component.version,
        "status": "running",
    }


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint following Tekton standards."""
    return component.get_health_status()


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    import uuid
    client_id = str(uuid.uuid4())  # Generate a random client ID
    
    # Get component from app state
    component = websocket.app.state.component
    if not component or not component.connection_manager:
        await websocket.close(code=1011, reason="Component not initialized")
        return
    
    # Accept the connection
    await component.connection_manager.connect(websocket, client_id)
    
    try:
        # Wait for registration message
        registration_text = await websocket.receive_text()
        registration_data = json.loads(registration_text)
        
        # Validate registration
        try:
            registration = WebSocketRegistration(**registration_data)
            if registration.client_id:
                client_id = registration.client_id  # Use client-provided ID if available
            
            # Subscribe to event types
            component.connection_manager.subscribe(client_id, registration.subscribe_to)
            
            # Send confirmation
            await websocket.send_json({
                "type": "registration_success",
                "data": {
                    "client_id": client_id,
                    "subscriptions": list(component.connection_manager.subscriptions.get(client_id, set()))
                }
            })
            
            # Register event handlers with task manager
            for event_type in registration.subscribe_to:
                if hasattr(component.task_manager, 'register_event_handler'):
                    component.task_manager.register_event_handler(
                        event_type,
                        lambda evt_type, data: asyncio.create_task(
                            component.connection_manager.broadcast({
                                "event": evt_type,
                                "data": data
                            })
                        )
                    )
            
            # Keep connection alive and handle messages
            while True:
                message_text = await websocket.receive_text()
                message_data = json.loads(message_text)
                
                # Handle different message types
                message_type = message_data.get("type")
                
                if message_type == "ping":
                    # Respond to ping
                    await websocket.send_json({"type": "pong", "data": {}})
                
                elif message_type == "subscribe":
                    # Subscribe to event types
                    event_types = message_data.get("data", {}).get("event_types", [])
                    component.connection_manager.subscribe(client_id, event_types)
                
                elif message_type == "unsubscribe":
                    # Unsubscribe from event types
                    event_types = message_data.get("data", {}).get("event_types", [])
                    component.connection_manager.unsubscribe(client_id, event_types)
                
        except Exception as e:
            # Invalid registration
            await websocket.send_json({
                "type": "registration_error",
                "data": {
                    "error": str(e)
                }
            })
            await websocket.close()
    
    except WebSocketDisconnect:
        # Client disconnected
        component.connection_manager.disconnect(client_id)
    
    except Exception as e:
        # Other error
        try:
            await websocket.send_json({
                "type": "error",
                "data": {
                    "error": str(e)
                }
            })
        except:
            pass
        component.connection_manager.disconnect(client_id)




# Custom exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom handler for HTTPException to provide consistent response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Generic exception handler to catch all unhandled exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": f"An unexpected error occurred: {str(exc)}",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Get port from GlobalConfig
    global_config = GlobalConfig.get_instance()
    port = global_config.config.metis.port
    
    uvicorn.run(app, host="0.0.0.0", port=port)