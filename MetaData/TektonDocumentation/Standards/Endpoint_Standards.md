# Endpoint Standards

## Required Endpoints

Every Tekton component MUST implement these endpoints:

### 1. Root Endpoint - `/`
```python
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
```

### 2. Health Check - `/health`
```python
@routers.root.get("/health")
async def health_check():
    """Health check endpoint using shared utility."""
    return create_health_response(
        component_name=COMPONENT_NAME.lower(),
        port=port,
        version=COMPONENT_VERSION,
        status="healthy",  # or "degraded", "unhealthy"
        registered=is_registered_with_hermes,
        details={
            "uptime": uptime,
            "dependencies": {
                "hermes": "healthy" if is_registered_with_hermes else "not_registered"
            }
        }
    )
```

**Response Schema:**
```json
{
    "status": "healthy",
    "component": "mycomponent",
    "version": "0.1.0",
    "port": 8000,
    "registered": true,
    "timestamp": "2024-01-01T00:00:00Z",
    "details": {
        "uptime": 3600.5,
        "dependencies": {
            "hermes": "healthy"
        }
    }
}
```

### 3. Ready Check - `/ready`
```python
routers.root.add_api_route(
    "/ready",
    create_ready_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        start_time=start_time or 0,
        readiness_check=lambda: custom_readiness_logic()
    ),
    methods=["GET"]
)
```

**Response Schema:**
```json
{
    "ready": true,
    "component": "MyComponent",
    "version": "0.1.0",
    "uptime": 120.5,
    "checks": {
        "custom_check": true
    }
}
```

### 4. Status - `/status`
```python
@routers.root.get("/status")
async def get_status():
    """Status endpoint for tekton-status integration."""
    return {
        "component": COMPONENT_NAME,
        "status": "running",
        "version": COMPONENT_VERSION,
        "port": port,
        "registered": is_registered_with_hermes,
        "uptime": uptime,
        "capabilities": ["capability1", "capability2"],
        "health": {
            "api": "healthy",
            "dependencies": {
                "hermes": "healthy" if is_registered_with_hermes else "disconnected"
            }
        }
    }
```

### 5. Discovery - `/api/v1/discovery`
```python
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION,
        endpoints=[
            EndpointInfo(
                path="/api/v1/resource",
                method="GET",
                description="Get resources"
            ),
            EndpointInfo(
                path="/api/v1/resource",
                method="POST",
                description="Create resource"
            )
        ],
        capabilities=["capability1", "capability2"],
        dependencies={
            "hermes": "http://localhost:8001",
            "rhetor": "http://localhost:8003"
        },
        metadata={
            "documentation": "/api/v1/docs",
            "websocket": "/ws" if has_websocket else None
        }
    ),
    methods=["GET"]
)
```

**Response Schema:**
```json
{
    "component": "MyComponent",
    "version": "0.1.0",
    "description": "Component description",
    "endpoints": [
        {
            "path": "/api/v1/resource",
            "method": "GET",
            "description": "Get resources"
        }
    ],
    "capabilities": ["capability1", "capability2"],
    "dependencies": {
        "hermes": "http://localhost:8001"
    },
    "metadata": {
        "documentation": "/api/v1/docs"
    }
}
```

### 6. Shutdown - `/shutdown`
```python
# Added automatically by shared utility
add_shutdown_endpoint_to_app(app, COMPONENT_NAME.lower())
```

## Business Logic Endpoints

All business logic endpoints MUST:
- Be under `/api/v1/` prefix
- Use the v1 router
- Have clear RESTful paths
- Include proper documentation

### RESTful Patterns
```python
# Collection endpoints
@routers.v1.get("/resources")              # List resources
@routers.v1.post("/resources")             # Create resource

# Item endpoints
@routers.v1.get("/resources/{id}")         # Get specific resource
@routers.v1.put("/resources/{id}")         # Update resource
@routers.v1.delete("/resources/{id}")      # Delete resource

# Action endpoints
@routers.v1.post("/resources/{id}/action") # Perform action on resource
```

### Response Models
All endpoints must use Pydantic models:
```python
class ResourceResponse(TektonBaseModel):
    id: str
    name: str
    created_at: datetime
    metadata: Dict[str, Any]

@routers.v1.get("/resources/{id}", response_model=ResourceResponse)
async def get_resource(id: str) -> ResourceResponse:
    # Implementation
    pass
```

## MCP Endpoints

MCP endpoints remain at `/api/mcp/v2/`:
```python
# MCP router is included separately
app.include_router(mcp_router, prefix="/api/mcp/v2", tags=["mcp"])

# Standard MCP endpoints
POST /api/mcp/v2/tools/list
POST /api/mcp/v2/tools/call
POST /api/mcp/v2/resources/list
POST /api/mcp/v2/resources/get
```

## WebSocket Endpoints

WebSocket endpoints remain at root level:
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # WebSocket logic
```

## Error Handling

### Standard Error Response
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "component": COMPONENT_NAME.lower(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized (future)
- `403` - Forbidden (future)
- `404` - Not Found
- `409` - Conflict
- `422` - Validation Error
- `500` - Internal Server Error
- `503` - Service Unavailable

## Endpoint Naming Conventions

1. Use lowercase with hyphens for multi-word resources
2. Use plural for collections: `/resources` not `/resource`
3. Use verbs only for non-RESTful actions: `/resources/{id}/activate`
4. Keep URLs short and meaningful
5. Avoid deep nesting (max 2 levels)

### Good Examples
```
GET    /api/v1/connections
GET    /api/v1/connections/{id}
POST   /api/v1/connections/{id}/test
GET    /api/v1/metrics
GET    /api/v1/budget-items
```

### Bad Examples
```
GET    /api/v1/getConnections           # Don't use verbs in resource names
GET    /api/v1/connection               # Use plural
GET    /api/v1/connections/active/list  # Too much nesting
POST   /api/v1/test-connection          # Should be under resource
```