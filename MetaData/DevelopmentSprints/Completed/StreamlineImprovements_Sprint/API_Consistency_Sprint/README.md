# API Consistency Sprint

## Overview

This sprint standardizes API patterns across all Tekton components, building on the shared utilities to create consistent interfaces for health checks, error responses, MCP registration, and inter-component communication.

## Current State

Inconsistent patterns observed during GoodLaunch debugging:
- Different health check implementations (or missing entirely)
- Web UI servers returning HTML instead of JSON (Hephaestus issue)
- Missing main() functions causing startup failures (Athena, Sophia)
- Varied error response formats
- Mixed approaches to MCP tool/capability registration
- No standard timeout handling
- Inconsistent API versioning
- Components launched successfully but not actually running (process vs server binding issues)

## Goals

1. **Standardize Endpoints**: Consistent API patterns across components
2. **Fix Startup Patterns**: All components must have working main() functions with uvicorn
3. **JSON-Only Health Checks**: Web UI and API servers both return JSON health responses
4. **Unified Error Handling**: Same error format everywhere
5. **Registration Patterns**: Standard MCP registration approach
6. **Health Monitoring**: Reliable health checks for all components
7. **Configuration Hierarchy**: Clear precedence for port/config resolution
8. **API Documentation**: OpenAPI/Swagger for all endpoints

## Implementation Plan

### Phase 1: API Standards Definition (0.5 sessions)

Define standard patterns for:
- Health check endpoints
- Error response format
- MCP registration APIs
- Component discovery
- API versioning

### Phase 2: Core Implementation (1 session)

Create shared API utilities:
```
tekton-core/tekton/shared/api/
├── __init__.py
├── health.py       # Health check standards
├── errors.py       # Error response handlers
├── registration.py # MCP registration patterns
├── discovery.py    # Service discovery helpers
└── models.py       # Shared API models
```

### Phase 3: Component Updates (2 sessions)

Update all components to use standard patterns:
- **CRITICAL**: Add missing main() functions (Athena, Sophia pattern)
- Add missing health checks using shared utilities
- Fix web UI servers to return JSON health responses (Hephaestus pattern)
- Standardize error responses
- Unify MCP registration
- Implement service discovery
- Establish configuration hierarchy (CLI → env → config → defaults)

### Phase 4: Documentation (0.5 sessions)

- API standards guide
- OpenAPI documentation
- Integration examples

## Key Standards

### 1. Health Check Pattern
```python
# Standard health check for all components
@router.get("/health")
async def health_check() -> HealthResponse:
    """Standard health check endpoint."""
    return HealthResponse(
        status="healthy",
        component=COMPONENT_NAME,
        version=COMPONENT_VERSION,
        timestamp=datetime.utcnow(),
        checks={
            "database": check_database(),
            "dependencies": check_dependencies(),
            "memory": check_memory_usage()
        }
    )

@router.get("/ready")
async def readiness_check() -> ReadyResponse:
    """Readiness probe for startup completion."""
    return ReadyResponse(
        ready=is_component_ready(),
        component=COMPONENT_NAME,
        initialization_time=startup_duration
    )
```

### 2. Error Response Format
```python
# Standardized error response
class ErrorResponse(BaseModel):
    error: str          # Error type/code
    message: str        # Human-readable message
    component: str      # Component that generated error
    timestamp: datetime # When error occurred
    details: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None

# Error handler
@app.exception_handler(TektonError)
async def tekton_error_handler(request: Request, exc: TektonError):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.error_code,
            message=str(exc),
            component=exc.component,
            timestamp=datetime.utcnow(),
            details=exc.details
        ).model_dump()
    )
```

### 3. MCP Registration Standard
```python
# Consistent registration pattern
class MCPRegistration:
    """Standard MCP registration handler."""
    
    @staticmethod
    def register_capability(capability_class: Type) -> CapabilityRegistration:
        """Register capability with validation."""
        if not inspect.isclass(capability_class):
            raise RegistrationError("Capability must be a class")
        
        instance = capability_class()
        if not hasattr(instance, 'name'):
            raise RegistrationError("Capability must have 'name' attribute")
            
        return CapabilityRegistration(
            name=instance.name,
            instance=instance,
            registered_at=datetime.utcnow()
        )
    
    @staticmethod
    def register_tool(tool_func: Callable, **metadata) -> ToolRegistration:
        """Register tool with consistent schema."""
        # Validate and register with standard pattern
        pass
```

### 4. Service Discovery
```python
# Component discovery endpoint
@router.get("/discovery")
async def service_discovery() -> ServiceInfo:
    """Provide service discovery information."""
    return ServiceInfo(
        component=COMPONENT_NAME,
        version=COMPONENT_VERSION,
        endpoints=get_available_endpoints(),
        capabilities=get_registered_capabilities(),
        tools=get_registered_tools(),
        dependencies=get_service_dependencies()
    )
```

### 5. API Versioning
```python
# Version prefix for all APIs
app = FastAPI(title=f"{COMPONENT_NAME} API", version="v1")

# Versioned routers
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(mcp_router, prefix="/mcp")
v1_router.include_router(health_router, prefix="/health")
```

## Benefits

1. **Predictability**: Same patterns everywhere
2. **Debugging**: Consistent error information
3. **Monitoring**: Reliable health checks
4. **Integration**: Easier component integration
5. **Documentation**: Auto-generated API docs

## Success Criteria

- [ ] All components have health/ready endpoints
- [ ] Standardized error response format
- [ ] Consistent MCP registration patterns
- [ ] Service discovery implemented
- [ ] API documentation generated

## Migration Guide

1. **Add Health Checks**: Use shared health utilities
2. **Update Error Handlers**: Implement standard format
3. **Fix Registration**: Use consistent patterns
4. **Add Discovery**: Implement service info endpoint
5. **Version APIs**: Add versioning prefix

## Timeline

Total effort: 4 sessions
- Standards Definition: 0.5 sessions
- Core Implementation: 1 session
- Component Updates: 2 sessions
- Documentation: 0.5 sessions