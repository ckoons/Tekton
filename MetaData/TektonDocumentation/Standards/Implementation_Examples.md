# Implementation Examples

This document provides complete examples of components following the API consistency standards.

## Complete Component Example

Here's a minimal but complete component following all standards:

```python
#!/usr/bin/env python3
"""
Example Component API Server

This example demonstrates all required API standards.
"""

import os
import sys
import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field
from tekton.models.base import TektonBaseModel

# REQUIRED: Add Tekton root to path
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utilities
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.utils.env_config import get_component_config
from shared.utils.errors import StartupError
from shared.utils.startup import component_startup
from shared.utils.shutdown import GracefulShutdown
from shared.utils.health_check import create_health_response
from shared.utils.shutdown_endpoint import add_shutdown_endpoint_to_app

# Import shared API utilities
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)

# Component configuration
COMPONENT_NAME = "Example"
COMPONENT_VERSION = "0.1.0"
COMPONENT_DESCRIPTION = "Example component demonstrating API standards"

# Logger setup
logger = setup_component_logging(COMPONENT_NAME.lower())

# Global state
hermes_registration = None
heartbeat_task = None
start_time = None
is_registered_with_hermes = False

# Models
class ItemModel(TektonBaseModel):
    """Example item model."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Item name")
    status: str = Field(..., description="Item status", example="active")
    created_at: datetime = Field(..., description="Creation timestamp")

class ItemCreate(TektonBaseModel):
    """Model for creating items."""
    name: str = Field(..., description="Item name", example="My Item")
    description: Optional[str] = Field(None, description="Optional description")

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager."""
    global hermes_registration, heartbeat_task, start_time, is_registered_with_hermes
    
    # Track startup time
    start_time = time.time()
    
    # Startup
    logger.info(f"Starting {COMPONENT_NAME} API")
    
    async def startup_logic():
        """Component-specific startup."""
        try:
            # Get configuration
            config = get_component_config()
            port = int(os.environ.get("EXAMPLE_PORT", 8020))
            
            # Register with Hermes
            global hermes_registration, heartbeat_task, is_registered_with_hermes
            hermes_registration = HermesRegistration()
            
            is_registered_with_hermes = await hermes_registration.register_component(
                component_name=COMPONENT_NAME.lower(),
                port=port,
                version=COMPONENT_VERSION,
                capabilities=["item_management", "example_operations"],
                metadata={"category": "example"}
            )
            
            if is_registered_with_hermes:
                logger.info("Successfully registered with Hermes")
                heartbeat_task = asyncio.create_task(
                    heartbeat_loop(hermes_registration, COMPONENT_NAME.lower(), interval=30)
                )
            else:
                logger.warning("Failed to register with Hermes")
                
            # Initialize component services
            app.state.items = {}  # Simple in-memory storage
            
        except Exception as e:
            logger.error(f"Error during startup: {e}")
            raise StartupError(str(e), COMPONENT_NAME, "STARTUP_FAILED")
    
    # Execute startup
    try:
        metrics = await component_startup(COMPONENT_NAME, startup_logic, timeout=30)
        logger.info(f"{COMPONENT_NAME} started in {metrics.total_time:.2f}s")
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        raise
    
    # Create shutdown handler
    shutdown = GracefulShutdown(COMPONENT_NAME)
    
    # Register cleanup
    async def cleanup_hermes():
        """Cleanup Hermes registration."""
        if heartbeat_task:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if hermes_registration and is_registered_with_hermes:
            await hermes_registration.deregister(COMPONENT_NAME.lower())
            logger.info("Deregistered from Hermes")
    
    shutdown.register_cleanup(cleanup_hermes)
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {COMPONENT_NAME} API")
    await shutdown.shutdown_sequence(timeout=10)
    await asyncio.sleep(0.5)  # Socket release

# Create app
app = FastAPI(
    **get_openapi_configuration(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION
    ),
    lifespan=lifespan
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create routers
routers = create_standard_routers(COMPONENT_NAME)

# Root endpoint
@routers.root.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": COMPONENT_NAME,
        "version": COMPONENT_VERSION,
        "description": COMPONENT_DESCRIPTION,
        "status": "running",
        "docs": "/api/v1/docs"
    }

# Health check
@routers.root.get("/health")
async def health_check():
    """Health check endpoint."""
    port = int(os.environ.get("EXAMPLE_PORT", 8020))
    
    return create_health_response(
        component_name=COMPONENT_NAME.lower(),
        port=port,
        version=COMPONENT_VERSION,
        status="healthy",
        registered=is_registered_with_hermes,
        details={
            "uptime": time.time() - start_time if start_time else 0,
            "items_count": len(app.state.items) if hasattr(app.state, "items") else 0
        }
    )

# Status endpoint
@routers.root.get("/status")
async def get_status():
    """Status endpoint for tekton-status."""
    port = int(os.environ.get("EXAMPLE_PORT", 8020))
    
    return {
        "component": COMPONENT_NAME,
        "status": "running",
        "version": COMPONENT_VERSION,
        "port": port,
        "registered": is_registered_with_hermes,
        "uptime": time.time() - start_time if start_time else 0,
        "capabilities": ["item_management", "example_operations"]
    }

# Add ready endpoint
routers.root.add_api_route(
    "/ready",
    create_ready_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        start_time=start_time or 0,
        readiness_check=lambda: hasattr(app.state, "items")
    ),
    methods=["GET"]
)

# Add discovery endpoint
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION,
        endpoints=[
            EndpointInfo(
                path="/api/v1/items",
                method="GET",
                description="List all items"
            ),
            EndpointInfo(
                path="/api/v1/items",
                method="POST",
                description="Create a new item"
            ),
            EndpointInfo(
                path="/api/v1/items/{item_id}",
                method="GET",
                description="Get item by ID"
            ),
            EndpointInfo(
                path="/api/v1/items/{item_id}",
                method="DELETE",
                description="Delete item"
            )
        ],
        capabilities=["item_management", "example_operations"],
        dependencies={
            "hermes": "http://localhost:8001"
        },
        metadata={
            "documentation": "/api/v1/docs",
            "category": "example"
        }
    ),
    methods=["GET"]
)

# Business logic endpoints
@routers.v1.get("/items", response_model=List[ItemModel])
async def list_items(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100, description="Max items to return")
):
    """List all items with optional filtering."""
    if not hasattr(app.state, "items"):
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    items = list(app.state.items.values())
    
    # Apply filters
    if status:
        items = [item for item in items if item.status == status]
    
    # Apply limit
    return items[:limit]

@routers.v1.post("/items", response_model=ItemModel, status_code=201)
async def create_item(item_data: ItemCreate):
    """Create a new item."""
    if not hasattr(app.state, "items"):
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Create item
    item_id = f"item-{len(app.state.items) + 1}"
    item = ItemModel(
        id=item_id,
        name=item_data.name,
        status="active",
        created_at=datetime.utcnow()
    )
    
    app.state.items[item_id] = item
    return item

@routers.v1.get("/items/{item_id}", response_model=ItemModel)
async def get_item(item_id: str):
    """Get a specific item by ID."""
    if not hasattr(app.state, "items"):
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    if item_id not in app.state.items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return app.state.items[item_id]

@routers.v1.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: str):
    """Delete an item."""
    if not hasattr(app.state, "items"):
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    if item_id not in app.state.items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    del app.state.items[item_id]

# Mount routers
mount_standard_routers(app, routers)

# Add MCP endpoints (if available)
try:
    from example.api.mcp_endpoints import mcp_router
    app.include_router(mcp_router, prefix="/api/mcp/v2", tags=["mcp"])
except ImportError:
    logger.info("MCP endpoints not available")

# Add shutdown endpoint
add_shutdown_endpoint_to_app(app, COMPONENT_NAME.lower())

# Main entry point
if __name__ == "__main__":
    from shared.utils.socket_server import run_with_socket_reuse
    
    port = int(os.environ.get("EXAMPLE_PORT", 8020))
    
    run_with_socket_reuse(
        "example.api.app:app",
        host="0.0.0.0",
        port=port,
        timeout_graceful_shutdown=3,
        server_header=False,
        access_log=False
    )
```

## MCP Endpoint Example

```python
# example/api/mcp_endpoints.py
from fastapi import APIRouter
from typing import List, Dict, Any
from tekton.models.base import TektonBaseModel

router = APIRouter()

class Tool(TektonBaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class ToolCall(TektonBaseModel):
    name: str
    arguments: Dict[str, Any] = {}

class ToolResponse(TektonBaseModel):
    content: List[Dict[str, Any]]
    isError: bool = False

# Available tools
TOOLS = [
    Tool(
        name="list_items",
        description="List all items in the system",
        inputSchema={
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "Filter by status"}
            }
        }
    ),
    Tool(
        name="create_item",
        description="Create a new item",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Item name"}
            },
            "required": ["name"]
        }
    )
]

@router.post("/tools/list")
async def list_tools():
    """List available MCP tools."""
    return {"tools": TOOLS}

@router.post("/tools/call")
async def call_tool(request: ToolCall):
    """Execute an MCP tool."""
    if request.name == "list_items":
        # Call the actual endpoint logic
        return ToolResponse(
            content=[{
                "type": "text",
                "text": "Listed items successfully"
            }]
        )
    elif request.name == "create_item":
        name = request.arguments.get("name", "Unnamed")
        return ToolResponse(
            content=[{
                "type": "text",
                "text": f"Created item: {name}"
            }]
        )
    else:
        return ToolResponse(
            content=[{
                "type": "text",
                "text": f"Unknown tool: {request.name}"
            }],
            isError=True
        )
```

## Testing Example

```python
# tests/test_api_standards.py
import pytest
from httpx import AsyncClient
from example.api.app import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_all_required_endpoints(client):
    """Test that all required endpoints exist and respond correctly."""
    
    # Test root
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/api/v1/docs"
    
    # Test health
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["component"] == "example"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data
    
    # Test ready
    response = await client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert data["component"] == "Example"
    
    # Test discovery
    response = await client.get("/api/v1/discovery")
    assert response.status_code == 200
    data = response.json()
    assert data["component"] == "Example"
    assert len(data["endpoints"]) > 0
    assert data["metadata"]["documentation"] == "/api/v1/docs"

@pytest.mark.asyncio
async def test_business_endpoints_under_v1(client):
    """Test that business logic is under /api/v1/."""
    
    # Should NOT work at root
    response = await client.get("/items")
    assert response.status_code == 404
    
    # Should work under /api/v1/
    response = await client.get("/api/v1/items")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_mcp_endpoints(client):
    """Test MCP endpoints are at correct path."""
    
    response = await client.post("/api/mcp/v2/tools/list")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
```

## Launch Script Example

```bash
#!/bin/bash
# run_example.sh

# Component configuration
COMPONENT_NAME="Example"
COMPONENT_MODULE="example"
PORT_VAR="EXAMPLE_PORT"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Setup Python path
export PYTHONPATH="$SCRIPT_DIR:$(dirname "$SCRIPT_DIR"):$PYTHONPATH"

# Get port from environment
PORT="${!PORT_VAR}"
if [ -z "$PORT" ]; then
    echo "Error: $PORT_VAR not set"
    exit 1
fi

# Check port availability
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "Error: Port $PORT is already in use"
    exit 1
fi

# Start component
echo "Starting $COMPONENT_NAME on port $PORT..."
python -m $COMPONENT_MODULE.api.app
```

## Common Patterns Reference

### Dependency Injection
```python
async def get_item_service() -> ItemService:
    """Dependency to get item service."""
    if not hasattr(app.state, "item_service"):
        raise HTTPException(status_code=503, detail="Service not initialized")
    return app.state.item_service

@routers.v1.get("/items")
async def list_items(
    service: ItemService = Depends(get_item_service)
):
    return await service.list_items()
```

### WebSocket Example
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # Process data
            await websocket.send_json({"echo": data})
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
```

### Background Tasks
```python
from fastapi import BackgroundTasks

@routers.v1.post("/items")
async def create_item(
    item: ItemCreate,
    background_tasks: BackgroundTasks
):
    # Create item
    new_item = await create_item_logic(item)
    
    # Add background task
    background_tasks.add_task(
        notify_item_created,
        item_id=new_item.id
    )
    
    return new_item
```

This completes the comprehensive API standards documentation for Tekton components!