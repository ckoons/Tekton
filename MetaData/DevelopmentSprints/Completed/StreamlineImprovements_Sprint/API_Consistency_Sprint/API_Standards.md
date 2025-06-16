# Tekton API Standards

## Overview

This document defines the standardized API patterns for all Tekton components. These standards ensure consistency, predictability, and ease of integration across the entire Tekton ecosystem.

## Core Principles

1. **Consistency**: Same patterns everywhere
2. **Predictability**: Developers know what to expect
3. **Simplicity**: Use existing shared utilities
4. **Forward-looking**: No backward compatibility constraints

## API Standards

### 1. Component Versioning

All components MUST report version "0.1.0" in:
- Health check responses
- Service discovery responses  
- API documentation (OpenAPI)
- Component metadata

```python
COMPONENT_VERSION = "0.1.0"
```

### 2. Endpoint Structure

#### Infrastructure Endpoints (Root Level)
These endpoints remain at the root level without API versioning:

- `GET /health` - Component health status
- `GET /ready` - Readiness probe
- `GET /status` - Detailed component status
- `POST /shutdown` - Graceful shutdown (if implemented)

#### Business Endpoints (Versioned)
All business logic endpoints use API versioning:

- `/api/v1/{resource}` - REST resources
- `/api/v1/{action}` - RPC-style actions
- `/api/v1/discovery` - Service discovery

#### MCP Endpoints (Special Case)
MCP endpoints use MCP protocol versioning (handled in YetAnotherMCP_Sprint):

- `/api/mcp/v2/*` - MCP protocol v2 endpoints

### 3. Health Check Standard

```python
# Response format (already implemented via shared utilities)
{
    "status": "healthy",  # healthy|degraded|unhealthy
    "component": "component-name",
    "version": "0.1.0",
    "port": 8000,
    "registered": true,
    "timestamp": "2024-01-01T00:00:00Z",
    "details": {
        # Optional component-specific checks
        "database": "connected",
        "dependencies": "available"
    }
}
```

HTTP Status Codes:
- 200: Healthy
- 207: Degraded (partial functionality)
- 503: Unhealthy

### 4. Ready Endpoint Standard

```python
# GET /ready
{
    "ready": true,
    "component": "component-name",
    "version": "0.1.0",
    "initialization_time": 1.234,  # seconds
    "timestamp": "2024-01-01T00:00:00Z"
}
```

HTTP Status Codes:
- 200: Ready
- 503: Not ready

### 5. Service Discovery Standard

```python
# GET /api/v1/discovery
{
    "component": "component-name",
    "version": "0.1.0",
    "description": "Component description",
    "endpoints": [
        {
            "path": "/api/v1/resource",
            "method": "GET",
            "description": "List resources"
        }
    ],
    "capabilities": ["capability1", "capability2"],
    "dependencies": {
        "hermes": "http://localhost:8001",
        "rhetor": "http://localhost:8003"
    },
    "metadata": {
        "author": "Tekton Team",
        "documentation": "/api/v1/docs"
    }
}
```

### 6. Error Response Standard

Using existing `ErrorResponse` from `tekton.models.base`:

```python
{
    "error": "RESOURCE_NOT_FOUND",  # Error code
    "message": "The requested resource was not found",
    "component": "component-name",
    "timestamp": "2024-01-01T00:00:00Z",
    "details": {
        "resource_id": "12345",
        "suggestion": "Check the resource ID"
    },
    "trace_id": "uuid-for-debugging"  # Optional
}
```

### 7. API Documentation

All components MUST provide OpenAPI documentation at:
- `/api/v1/docs` - Swagger UI
- `/api/v1/openapi.json` - OpenAPI schema

FastAPI configuration:
```python
app = FastAPI(
    title=f"{COMPONENT_NAME} API",
    version=COMPONENT_VERSION,  # "0.1.0"
    description=f"{COMPONENT_NAME} - Tekton Component",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json"
)
```

### 8. Router Organization

```python
# Root router for infrastructure
root_router = APIRouter()
root_router.add_api_route("/health", health_check, methods=["GET"])
root_router.add_api_route("/ready", ready_check, methods=["GET"])
root_router.add_api_route("/status", status_check, methods=["GET"])

# Versioned router for business logic
v1_router = APIRouter(prefix="/api/v1")
v1_router.add_api_route("/discovery", service_discovery, methods=["GET"])
# Add other business endpoints here

# Include routers
app.include_router(root_router)
app.include_router(v1_router)
```

### 9. Common HTTP Headers

All responses should include:
```
X-Component: component-name
X-Component-Version: 0.1.0
X-Request-ID: unique-request-id
```

### 10. CORS Configuration

Use the shared CORS configuration for all components:
```python
from shared.utils.cors import get_cors_middleware
app.add_middleware(CORSMiddleware, **get_cors_middleware())
```

## Implementation Checklist

For each component, ensure:

- [ ] Version set to "0.1.0"
- [ ] `/health` endpoint returns JSON (not HTML)
- [ ] `/ready` endpoint implemented
- [ ] `/api/v1/discovery` endpoint implemented
- [ ] Business endpoints under `/api/v1/`
- [ ] Error responses use `ErrorResponse` model
- [ ] OpenAPI docs at `/api/v1/docs`
- [ ] Common headers in responses
- [ ] CORS properly configured

## Migration Notes

1. **DO NOT** modify working infrastructure code
2. **DO NOT** change MCP endpoints (handled in YetAnotherMCP_Sprint)
3. **FOCUS ON** API consistency and standardization
4. **TEST** all changes with `tekton-launch`, `tekton-status`, `tekton-kill`