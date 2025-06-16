"""
Engram API Server

A unified FastAPI server that provides memory services for both
standalone mode and Hermes integration.
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utils
from shared.utils.health_check import create_health_response
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.utils.env_config import get_component_config
from shared.utils.global_config import GlobalConfig
from shared.utils.errors import StartupError
from shared.utils.startup import component_startup, StartupMetrics
from shared.utils.shutdown import GracefulShutdown
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)

# Use shared logger
logger = setup_component_logging("engram")

# Import Engram component and services
from engram.core.engram_component import EngramComponent
from engram.core import MemoryService

# Create component singleton
engram_component = EngramComponent()

# Note: Component configuration and initialization is handled by EngramComponent
# The component manages memory_manager, hermes_adapter, mcp_bridge internally

async def startup_callback():
    """Initialize Engram component (includes Hermes registration)."""
    # Initialize component (includes Hermes registration)
    await engram_component.initialize(
        capabilities=engram_component.get_capabilities(),
        metadata=engram_component.get_metadata()
    )

# Initialize FastAPI app with standard configuration
app = FastAPI(
    **get_openapi_configuration(
        component_name="engram",
        component_version="0.1.0",
        component_description="Memory management system with vector search and semantic similarity"
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
routers = create_standard_routers("engram")

# Store component reference for endpoints
app.state.component = engram_component

# Register startup callback
@app.on_event("startup")
async def startup_event():
    await startup_callback()


# Dependency to get memory service for a client
async def get_memory_service(
    request: Request,
    x_client_id: str = Header(None)
) -> MemoryService:
    client_id = x_client_id or engram_component.default_client_id
    
    if engram_component.memory_manager is None:
        raise HTTPException(status_code=500, detail="Memory manager not initialized")
    
    try:
        return await engram_component.memory_manager.get_memory_service(client_id)
    except Exception as e:
        logger.error(f"Error getting memory service: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting memory service: {str(e)}")

# Define routes
@routers.root.get("/")
async def root():
    """Root endpoint returning basic service information."""
    return {
        "service": "Engram Memory API",
        "version": "0.1.0",
        "description": "Memory management system with vector search and semantic similarity",
        "mode": "hermes" if engram_component.use_hermes else "standalone",
        "fallback": engram_component.use_fallback,
        "docs": "/api/v1/docs"
    }

@routers.root.get("/health")
async def health():
    """Health check endpoint."""
    # Don't trigger memory service initialization during health check
    # This avoids loading the sentence transformer model unnecessarily
    health_status = "healthy" if engram_component.memory_manager is not None else "initializing"
    
    details = {
        "memory_manager_initialized": bool(engram_component.memory_manager),
        "storage_mode": "fallback" if engram_component.use_fallback else "vector",
        "vector_available": not engram_component.use_fallback,
        "hermes_integration": engram_component.use_hermes,
        "default_client_id": engram_component.default_client_id
    }
    
    # Use standardized health response
    global_config = GlobalConfig.get_instance()
    port = global_config.config.engram.port
    return create_health_response(
        component_name="engram",
        port=port,
        version="0.1.0",
        status=health_status,
        registered=engram_component.global_config.is_registered_with_hermes,
        details=details
    )

@routers.v1.post("/memory")
async def add_memory(
    request: Request,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Add a memory."""
    try:
        data = await request.json()
        content = data.get("content")
        namespace = data.get("namespace", "conversations")
        metadata = data.get("metadata")
        
        if not content:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required parameter: content"}
            )
        
        memory_id = await memory_service.add(
            content=content,
            namespace=namespace,
            metadata=metadata
        )
        
        return {
            "id": memory_id,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error adding memory: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error adding memory: {str(e)}"}
        )

@routers.v1.get("/memory/{memory_id}")
async def get_memory(
    memory_id: str,
    namespace: str = "conversations",
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get a memory by ID."""
    try:
        memory = await memory_service.get(memory_id, namespace)
        
        if not memory:
            return JSONResponse(
                status_code=404,
                content={"error": f"Memory {memory_id} not found in namespace {namespace}"}
            )
        
        return memory
    except Exception as e:
        logger.error(f"Error getting memory {memory_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting memory: {str(e)}"}
        )

@routers.v1.post("/search")
async def search_memory(
    request: Request,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Search for memories."""
    try:
        data = await request.json()
        query = data.get("query")
        namespace = data.get("namespace", "conversations")
        limit = data.get("limit", 5)
        
        if not query:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required parameter: query"}
            )
        
        # Handle empty or None namespace
        if not namespace:
            namespace = "conversations"
        
        results = await memory_service.search(
            query=query,
            namespace=namespace,
            limit=limit
        )
        
        # Ensure results is always a dict with expected structure
        if not isinstance(results, dict):
            results = {"results": [], "count": 0}
        
        return results
    except Exception as e:
        logger.error(f"Error searching memory: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error searching memory: {str(e)}"}
        )

@routers.v1.post("/context")
async def get_context(
    request: Request,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get relevant context from multiple namespaces."""
    try:
        data = await request.json()
        query = data.get("query")
        namespaces = data.get("namespaces")
        limit = data.get("limit", 3)
        
        if not query:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required parameter: query"}
            )
        
        context = await memory_service.get_relevant_context(
            query=query,
            namespaces=namespaces,
            limit=limit
        )
        
        return {"context": context}
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting context: {str(e)}"}
        )

@routers.v1.get("/namespaces")
async def list_namespaces(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """List available namespaces."""
    try:
        namespaces = await memory_service.get_namespaces()
        return namespaces
    except Exception as e:
        logger.error(f"Error listing namespaces: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error listing namespaces: {str(e)}"}
        )

@routers.v1.post("/compartments")
async def create_compartment(
    request: Request,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Create a new memory compartment."""
    try:
        data = await request.json()
        name = data.get("name")
        description = data.get("description")
        parent = data.get("parent")
        
        if not name:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required parameter: name"}
            )
        
        compartment_id = await memory_service.create_compartment(
            name=name,
            description=description,
            parent=parent
        )
        
        return {
            "id": compartment_id,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error creating compartment: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error creating compartment: {str(e)}"}
        )

@routers.v1.get("/compartments")
async def list_compartments(
    include_inactive: bool = False,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """List memory compartments."""
    try:
        compartments = await memory_service.list_compartments(include_inactive)
        return compartments
    except Exception as e:
        logger.error(f"Error listing compartments: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error listing compartments: {str(e)}"}
        )

@routers.v1.post("/compartments/{compartment_id}/activate")
async def activate_compartment(
    compartment_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Activate a memory compartment."""
    try:
        success = await memory_service.activate_compartment(compartment_id)
        
        if not success:
            return JSONResponse(
                status_code=404,
                content={"error": f"Compartment {compartment_id} not found"}
            )
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error activating compartment {compartment_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error activating compartment: {str(e)}"}
        )

@routers.v1.post("/compartments/{compartment_id}/deactivate")
async def deactivate_compartment(
    compartment_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Deactivate a memory compartment."""
    try:
        success = await memory_service.deactivate_compartment(compartment_id)
        
        if not success:
            return JSONResponse(
                status_code=404,
                content={"error": f"Compartment {compartment_id} not found"}
            )
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error deactivating compartment {compartment_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error deactivating compartment: {str(e)}"}
        )


# Add ready endpoint
routers.root.add_api_route(
    "/ready",
    create_ready_endpoint(
        component_name="engram",
        component_version="0.1.0",
        start_time=engram_component.global_config._start_time,
        readiness_check=lambda: engram_component.memory_manager is not None
    ),
    methods=["GET"]
)

# Add discovery endpoint to v1 router
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name="engram",
        component_version="0.1.0",
        component_description="Memory management system with vector search and semantic similarity",
        endpoints=[
            EndpointInfo(
                path="/api/v1/memory",
                method="POST",
                description="Add a memory"
            ),
            EndpointInfo(
                path="/api/v1/memory/{memory_id}",
                method="GET",
                description="Get a memory by ID"
            ),
            EndpointInfo(
                path="/api/v1/search",
                method="POST",
                description="Search memories"
            ),
            EndpointInfo(
                path="/api/v1/context",
                method="POST",
                description="Get recent context"
            ),
            EndpointInfo(
                path="/api/v1/namespaces",
                method="GET",
                description="List all namespaces"
            ),
            EndpointInfo(
                path="/api/v1/compartments",
                method="GET",
                description="List all compartments"
            )
        ],
        capabilities=engram_component.get_capabilities(),
        dependencies={
            "hermes": "http://localhost:8001"
        },
        metadata=engram_component.get_metadata()
    ),
    methods=["GET"]
)

# Mount standard routers
mount_standard_routers(app, routers)

# Note: Engram uses shared MCP bridge instead of FastMCP endpoints
# The fastmcp_server.py is a standalone server for alternative MCP mode


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Engram API Server")
    parser.add_argument("--client-id", type=str, default=None,
                      help="Default client ID (default: 'default')")
    parser.add_argument("--port", type=int, default=None,
                      help="Port to run the server on (default: from env config)")
    parser.add_argument("--host", type=str, default=None,
                      help="Host to bind the server to (default: '127.0.0.1')")
    parser.add_argument("--data-dir", type=str, default=None,
                      help="Directory to store memory data (default: '~/.engram')")
    parser.add_argument("--fallback", action="store_true",
                      help="Use fallback file-based implementation without vector database")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug mode")
    return parser.parse_args()

def main():
    """Main entry point for the server when run directly."""
    args = parse_arguments()
    
    # Override environment variables with command line arguments if provided
    if args.client_id:
        os.environ["ENGRAM_CLIENT_ID"] = args.client_id
    
    if args.data_dir:
        os.environ["ENGRAM_DATA_DIR"] = args.data_dir
    
    if args.fallback:
        os.environ["ENGRAM_USE_FALLBACK"] = "1"
    
    if args.debug:
        os.environ["ENGRAM_DEBUG"] = "1"
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get GlobalConfig instance
    global_config = GlobalConfig.get_instance()
    
    # Get host and port from GlobalConfig or arguments
    host = args.host or os.environ.get("ENGRAM_HOST", "127.0.0.1")
    port = args.port or global_config.config.engram.port
    
    # Start the server with socket reuse
    logger.info(f"Starting Engram API server on {host}:{port}")
    from shared.utils.socket_server import run_with_socket_reuse
    run_with_socket_reuse(
        "engram.api.server:app",
        host=host,
        port=port,
        timeout_graceful_shutdown=3,
        server_header=False,
        access_log=False
    )

if __name__ == "__main__":
    main()