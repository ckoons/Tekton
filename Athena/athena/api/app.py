"""
Athena API Application

Main FastAPI application for Athena's REST API.
Provides comprehensive knowledge graph functionality.
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add Tekton root to path for shared imports and landmarks
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)  # Insert at beginning for priority

# Import shared utils
from shared.utils.global_config import GlobalConfig
from shared.utils.logging_setup import setup_component_logging as setup_component_logger
from shared.workflow.endpoint_template import create_workflow_endpoint
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)

# Use shared logger
logger = setup_component_logger("athena")

from .endpoints.knowledge_graph import router as knowledge_router
from .endpoints.entities import router as entities_router
from .endpoints.query import router as query_router
from .endpoints.visualization import router as visualization_router
from .endpoints.llm_integration import router as llm_router
from .endpoints.mcp import mcp_router

# Import Athena component
from athena.core.athena_component import AthenaComponent

# Create component instance (singleton)
component = AthenaComponent()

async def populate_athena_delayed():
    """Populate Athena with component relationships after a delay to ensure all components are started."""
    try:
        # Wait for other components to start up
        await asyncio.sleep(10)
        
        logger.info("Auto-populating Athena with Tekton component relationships...")
        
        # Check if the populate script exists
        populate_script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                                     "populate_athena_relationships.py")
        
        if os.path.exists(populate_script):
            # Run the population script
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                populate_script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info("✅ Successfully populated Athena with component relationships")
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Failed to populate Athena: {error_msg}")
        else:
            logger.warning(f"Athena population script not found at: {populate_script}")
            
    except Exception as e:
        logger.error(f"Error during Athena auto-population: {e}")

async def startup_callback():
    """Initialize component during startup."""
    # Initialize the component (registers with Hermes, etc.)
    await component.initialize(
        capabilities=component.get_capabilities(),
        metadata=component.get_metadata()
    )
    
    # Initialize Athena MCP Bridge
    try:
        from athena.core.mcp.hermes_bridge import AthenaMCPBridge
        mcp_bridge = AthenaMCPBridge(component.knowledge_engine)
        await mcp_bridge.initialize()
        component.mcp_bridge = mcp_bridge
        logger.info("Initialized Hermes MCP Bridge for FastMCP tools")
    except Exception as e:
        logger.warning(f"Failed to initialize MCP Bridge: {e}")
    
    # Auto-populate Athena if enabled
    if os.environ.get('ATHENA_AUTO_POPULATE', 'true').lower() == 'true':
        asyncio.create_task(populate_athena_delayed())

# Create FastAPI application using component's create_app
app = component.create_app(
    startup_callback=startup_callback,
    **get_openapi_configuration(
        component_name=component.component_name.capitalize(),
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
routers = create_standard_routers(component.component_name.capitalize())

# Add infrastructure endpoints to root router
@routers.root.get("/health")
async def health():
    """Health check endpoint."""
    return component.get_health_status()

# Add ready endpoint
@routers.root.get("/ready")
async def ready():
    """Readiness check endpoint."""
    ready_check = create_ready_endpoint(
        component_name=component.component_name.capitalize(),
        component_version=component.version,
        start_time=component.global_config._start_time,
        readiness_check=lambda: component.knowledge_engine is not None
    )
    return await ready_check()

# Add discovery endpoint to v1 router
@routers.v1.get("/discovery")
async def discovery():
    """Service discovery endpoint."""
    capabilities = component.get_capabilities()
    metadata = component.get_metadata()
    
    discovery_check = create_discovery_endpoint(
        component_name=component.component_name.capitalize(),
        component_version=component.version,
        component_description=metadata["description"],
        endpoints=[
            EndpointInfo(
                path="/api/v1/knowledge",
                method="GET",
                description="Get knowledge graph overview"
            ),
            EndpointInfo(
                path="/api/v1/entities",
                method="GET",
                description="List all entities"
            ),
            EndpointInfo(
                path="/api/v1/entities",
                method="POST",
                description="Create new entity"
            ),
            EndpointInfo(
                path="/api/v1/query/search",
                method="POST",
                description="Search entities"
            ),
            EndpointInfo(
                path="/api/v1/visualization/graph",
                method="GET",
                description="Get graph visualization data"
            )
        ],
        capabilities=capabilities,
        dependencies={
            "hermes": "http://localhost:8001",
            "rhetor": "http://localhost:8003"
        },
        metadata={
            **metadata,
            "documentation": "/api/v1/docs"
        }
    )
    return await discovery_check()

# Include business logic routers under v1
routers.v1.include_router(knowledge_router, prefix="/knowledge", tags=["Knowledge Graph"])
routers.v1.include_router(entities_router, prefix="/entities", tags=["Entities"])
routers.v1.include_router(query_router, prefix="/query", tags=["Query"])
routers.v1.include_router(visualization_router, prefix="/visualization", tags=["Visualization"])
routers.v1.include_router(llm_router, prefix="/llm", tags=["LLM Integration"])

# Mount standard routers
mount_standard_routers(app, routers)

# MCP router remains at its current location (handled in YetAnotherMCP_Sprint)
app.include_router(mcp_router)

# Include standardized workflow endpoint
workflow_router = create_workflow_endpoint("athena")
app.include_router(workflow_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for API"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"} 
    )

@routers.root.get("/")
async def root():
    """Root endpoint."""
    metadata = component.get_metadata()
    return {
        "message": f"Welcome to {component.component_name.capitalize()} API",
        "version": component.version,
        "description": metadata["description"],
        "features": [
            "Enhanced entity management",
            "Multiple query modes",
            "Entity merging",
            "Graph and vector integration",
            "FastMCP integration"
        ],
        "docs": "/api/v1/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Get port from GlobalConfig
    global_config = GlobalConfig.get_instance()
    port = global_config.config.athena.port
    
    uvicorn.run(app, host="0.0.0.0", port=port)