# Shared API Utilities

This directory contains shared API utilities for ensuring consistency across all Tekton components.

## Overview

These utilities help standardize:
- API router creation and organization
- Ready and discovery endpoints
- OpenAPI documentation configuration
- Common response patterns

## Usage

### Basic Integration

```python
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

# Component configuration
COMPONENT_NAME = "MyComponent"
COMPONENT_VERSION = "0.1.0"
start_time = time.time()

# Create app with standard OpenAPI config
app = FastAPI(**get_openapi_configuration(
    component_name=COMPONENT_NAME,
    component_version=COMPONENT_VERSION
))

# Create standard routers
routers = create_standard_routers(COMPONENT_NAME)

# Add ready endpoint
routers.root.add_api_route(
    "/ready",
    create_ready_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        start_time=start_time
    ),
    methods=["GET"]
)

# Add discovery endpoint
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description="My component description",
        endpoints=[
            EndpointInfo(
                path="/api/v1/resource",
                method="GET",
                description="Get resources"
            )
        ],
        capabilities=["capability1", "capability2"],
        dependencies={"hermes": "http://localhost:8001"}
    ),
    methods=["GET"]
)

# Mount routers
mount_standard_routers(app, routers)
```

### Router Organization

- **Root Router** (`/`): Infrastructure endpoints
  - `/health` - Health check
  - `/ready` - Readiness probe
  - `/status` - Component status

- **V1 Router** (`/api/v1/`): Business logic
  - `/api/v1/discovery` - Service discovery
  - `/api/v1/{resource}` - Your business endpoints

## Components

### routers.py
- `create_standard_routers()` - Creates root and v1 routers
- `mount_standard_routers()` - Mounts routers to app

### endpoints.py
- `create_ready_endpoint()` - Creates ready endpoint
- `create_discovery_endpoint()` - Creates discovery endpoint
- Response models: `ReadyResponse`, `DiscoveryResponse`

### documentation.py
- `get_openapi_configuration()` - Returns FastAPI config for OpenAPI
- `get_default_tags()` - Standard OpenAPI tags
- `add_custom_responses()` - Enhances response definitions

## Standards

All components should:
1. Use component version "0.1.0"
2. Implement `/ready` endpoint
3. Implement `/api/v1/discovery` endpoint
4. Use `/api/v1/` prefix for business endpoints
5. Configure OpenAPI with standard settings

See `example_usage.py` for a complete example.