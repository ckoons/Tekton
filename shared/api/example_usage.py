"""
Example usage of shared API utilities for Tekton components.

This file demonstrates how to integrate the shared API utilities into a component.
"""
import time
from fastapi import FastAPI
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)
from shared.utils.health_check import create_health_response

# Component configuration
COMPONENT_NAME = "Example"
COMPONENT_VERSION = "0.1.0"
COMPONENT_PORT = 8999
COMPONENT_DESCRIPTION = "Example Tekton Component demonstrating API standards"

# Track startup time
start_time = time.time()

# Create FastAPI app with standard configuration
app = FastAPI(**get_openapi_configuration(
    component_name=COMPONENT_NAME,
    component_version=COMPONENT_VERSION,
    component_description=COMPONENT_DESCRIPTION
))

# Create standard routers
routers = create_standard_routers(COMPONENT_NAME)

# Add infrastructure endpoints to root router
@routers.root.get("/health")
async def health_check():
    """Standard health check endpoint."""
    return create_health_response(
        component_name=COMPONENT_NAME,
        port=COMPONENT_PORT,
        version=COMPONENT_VERSION,
        status="healthy",
        registered=True,
        details={
            "uptime": time.time() - start_time,
            "custom_check": "passed"
        }
    )

# Add ready endpoint
routers.root.add_api_route(
    "/ready",
    create_ready_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        start_time=start_time,
        readiness_check=lambda: True  # Custom readiness logic here
    ),
    methods=["GET"]
)

# Add discovery endpoint to v1 router
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION,
        endpoints=[
            EndpointInfo(
                path="/api/v1/examples",
                method="GET",
                description="List all examples"
            ),
            EndpointInfo(
                path="/api/v1/examples/{id}",
                method="GET",
                description="Get example by ID"
            )
        ],
        capabilities=["example_processing", "data_validation"],
        dependencies={
            "hermes": "http://localhost:8001",
            "rhetor": "http://localhost:8003"
        },
        metadata={
            "author": "Tekton Team",
            "documentation": "/api/v1/docs"
        }
    ),
    methods=["GET"]
)

# Add business logic endpoints to v1 router
@routers.v1.get("/examples")
async def list_examples():
    """List all examples."""
    return {"examples": ["example1", "example2"]}

@routers.v1.get("/examples/{example_id}")
async def get_example(example_id: str):
    """Get a specific example."""
    return {"id": example_id, "data": "Example data"}

# Mount standard routers
mount_standard_routers(app, routers)

# The component would also mount MCP endpoints here (handled in YetAnotherMCP_Sprint)
# Example: app.mount("/api/mcp/v2", mcp_app)