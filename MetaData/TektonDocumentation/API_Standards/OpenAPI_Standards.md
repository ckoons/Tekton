# OpenAPI Standards

## Overview

All Tekton components must provide comprehensive OpenAPI documentation that follows these standards for consistency and usability.

## Configuration

### Standard OpenAPI Setup
Every component uses the shared configuration helper:

```python
from shared.api import get_openapi_configuration

app = FastAPI(
    **get_openapi_configuration(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION
    ),
    lifespan=lifespan
)
```

This provides:
- Consistent title format: "{ComponentName} API"
- Standardized version (0.1.0)
- Proper description
- Docs URL at `/api/v1/docs`
- ReDoc URL at `/api/v1/redoc`
- OpenAPI schema at `/api/v1/openapi.json`

## Documentation Requirements

### Endpoint Documentation
Every endpoint must have:

```python
@routers.v1.get(
    "/resources",
    response_model=List[ResourceModel],
    summary="List all resources",
    description="""
    Retrieve a list of all resources with optional filtering.
    
    This endpoint supports pagination and filtering by status.
    Results are sorted by creation date in descending order.
    """,
    responses={
        200: {
            "description": "List of resources",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "res-123",
                            "name": "Example Resource",
                            "status": "active",
                            "created_at": "2024-01-01T00:00:00Z"
                        }
                    ]
                }
            }
        },
        503: {"description": "Service unavailable"}
    },
    tags=["resources"]
)
async def list_resources(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    List all resources with optional filtering.
    
    Args:
        status: Optional status filter
        limit: Maximum number of results (1-100)
        offset: Number of results to skip for pagination
        
    Returns:
        List of resources matching the criteria
    """
    # Implementation
```

### Response Models
All response models must be properly documented:

```python
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field
from tekton.models.base import TektonBaseModel

class ResourceModel(TektonBaseModel):
    """Model representing a resource in the system."""
    
    id: str = Field(..., description="Unique identifier for the resource")
    name: str = Field(..., description="Human-readable name", example="My Resource")
    status: str = Field(..., description="Current status", example="active")
    created_at: datetime = Field(..., description="Creation timestamp")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
        example={"type": "primary", "owner": "user123"}
    )
    
    class Config:
        schema_extra = {
            "example": {
                "id": "res-123",
                "name": "Example Resource",
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "metadata": {
                    "type": "primary",
                    "owner": "user123"
                }
            }
        }
```

### Error Responses
Standardized error responses:

```python
class ErrorResponse(TektonBaseModel):
    """Standard error response format."""
    
    error: str = Field(..., description="Error message")
    component: str = Field(..., description="Component that generated the error")
    timestamp: str = Field(..., description="ISO format timestamp")
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Resource not found",
                "component": "mycomponent",
                "timestamp": "2024-01-01T00:00:00Z",
                "details": {
                    "resource_id": "res-123",
                    "search_params": {"status": "active"}
                }
            }
        }
```

## Tags Organization

Use consistent tags for endpoint grouping:

```python
# Define tags with metadata
tags_metadata = [
    {
        "name": "resources",
        "description": "Operations with resources",
    },
    {
        "name": "health",
        "description": "Health and status endpoints",
    },
    {
        "name": "mcp",
        "description": "Model Context Protocol endpoints",
    }
]

# Apply to endpoints
@routers.v1.get("/resources", tags=["resources"])
@routers.root.get("/health", tags=["health"])
```

## OpenAPI Extensions

### Custom Fields
Add component-specific metadata:

```python
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom fields
    openapi_schema["x-component-name"] = COMPONENT_NAME.lower()
    openapi_schema["x-component-category"] = "core"
    openapi_schema["x-api-version"] = "v1"
    
    # Add server information
    openapi_schema["servers"] = [
        {
            "url": f"http://localhost:{port}",
            "description": "Local development server"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### Security Schemes (Future)
When authentication is implemented:

```python
openapi_schema["components"]["securitySchemes"] = {
    "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    },
    "apiKey": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key"
    }
}
```

## Examples in Documentation

### Request Examples
Provide comprehensive examples:

```python
@routers.v1.post(
    "/resources",
    response_model=ResourceModel,
    responses={
        201: {
            "description": "Resource created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "res-456",
                        "name": "New Resource",
                        "status": "pending",
                        "created_at": "2024-01-01T00:00:00Z",
                        "metadata": {}
                    }
                }
            }
        },
        400: {
            "description": "Invalid input",
            "model": ErrorResponse
        }
    }
)
async def create_resource(
    resource: ResourceCreate = Body(
        ...,
        example={
            "name": "New Resource",
            "type": "primary",
            "config": {
                "setting1": "value1",
                "setting2": 42
            }
        }
    )
):
    """Create a new resource."""
    # Implementation
```

### Multiple Examples
For complex endpoints:

```python
resource_examples = {
    "simple": {
        "summary": "Simple resource",
        "value": {
            "name": "Basic Resource",
            "type": "standard"
        }
    },
    "advanced": {
        "summary": "Advanced configuration",
        "value": {
            "name": "Advanced Resource",
            "type": "premium",
            "config": {
                "performance": "high",
                "replication": 3,
                "features": ["monitoring", "backup"]
            }
        }
    }
}

@routers.v1.post(
    "/resources",
    response_model=ResourceModel
)
async def create_resource(
    resource: ResourceCreate = Body(..., examples=resource_examples)
):
    """Create a new resource with various configuration options."""
    # Implementation
```

## API Versioning Documentation

Document version strategy:

```python
"""
## API Versioning

This API follows semantic versioning. The current version is v1.

### Version History
- v1 (current): Initial API version with core functionality

### Deprecation Policy
- APIs are supported for at least 6 months after deprecation
- Deprecation notices included in responses via headers
- Migration guides provided for breaking changes

### Version Selection
- URL path: `/api/v1/` for version 1
- Future: Accept header versioning may be supported
"""
```

## Interactive Documentation Features

### Try It Out
Ensure all endpoints work in the docs UI:
- Proper CORS configuration
- Example values that work
- Clear parameter descriptions
- Accurate response schemas

### Authentication (Future)
When implemented, provide test credentials:
```python
"""
## Authentication

For testing in the documentation:
- Test API Key: `test-key-123`
- Test Bearer Token: `eyJ...test...`

Note: These only work in development mode.
"""
```

## Documentation Best Practices

1. **Clear Descriptions**: Write for developers who don't know your system
2. **Practical Examples**: Use realistic data, not "foo/bar"
3. **Error Documentation**: Document all possible error responses
4. **Deprecation Notices**: Clearly mark deprecated endpoints
5. **Versioning Info**: Explain version strategy and migration
6. **Interactive Testing**: Ensure "Try it out" works for all endpoints
7. **Type Information**: Use proper Pydantic models for all I/O

## Common Documentation Issues

### Missing Response Models
❌ Bad:
```python
@routers.v1.get("/data")
async def get_data():
    return {"data": [1, 2, 3]}
```

✅ Good:
```python
@routers.v1.get("/data", response_model=DataResponse)
async def get_data() -> DataResponse:
    return DataResponse(data=[1, 2, 3])
```

### Unclear Descriptions
❌ Bad:
```python
@routers.v1.get("/process", summary="Process")
```

✅ Good:
```python
@routers.v1.get(
    "/process",
    summary="Process pending tasks",
    description="Trigger processing of all pending tasks in the queue"
)
```

### No Examples
❌ Bad:
```python
resource: ResourceCreate
```

✅ Good:
```python
resource: ResourceCreate = Body(..., example={
    "name": "Production Server",
    "type": "compute",
    "size": "large"
})
```

## Validation

Ensure your OpenAPI documentation:
- Generates without errors
- Validates against OpenAPI 3.0 spec
- Includes all endpoints
- Has consistent formatting
- Provides useful examples
- Documents all errors