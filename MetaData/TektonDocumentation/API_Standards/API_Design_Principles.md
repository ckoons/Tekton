# API Design Principles

## Core Principles

### 1. Consistency First
All Tekton components follow identical patterns for common operations. This reduces cognitive load and enables developers to work across components easily.

### 2. Infrastructure vs Business Logic Separation
- **Infrastructure endpoints** (`/health`, `/ready`, `/status`, `/shutdown`) remain at the root level
- **Business logic endpoints** are versioned under `/api/v1/`
- **MCP endpoints** remain at `/api/mcp/v2/` for backward compatibility

### 3. Discoverability
Every component must provide a `/api/v1/discovery` endpoint that describes:
- Available endpoints and their methods
- Component capabilities
- Dependencies on other components
- Metadata including documentation URL

### 4. Standardized Responses
All components use the same response formats:
- Health checks use `create_health_response()`
- Ready checks follow a consistent schema
- Error responses use Pydantic models
- All responses include component identification

### 5. Versioning Strategy
- All components use version `"0.1.0"` during initial development
- API paths include version (`/api/v1/`)
- Future versions will follow semantic versioning
- Breaking changes require new API versions

## Design Patterns

### Router Organization
```python
# Standard router pattern
routers = create_standard_routers(COMPONENT_NAME)

# Infrastructure endpoints on root router
@routers.root.get("/health")
@routers.root.get("/ready")
@routers.root.get("/status")

# Business logic on v1 router
@routers.v1.get("/resource")
@routers.v1.post("/action")

# Mount all routers
mount_standard_routers(app, routers)
```

### Component Configuration
```python
# Required constants
COMPONENT_NAME = "ComponentName"  # PascalCase
COMPONENT_VERSION = "0.1.0"      # Standardized
COMPONENT_DESCRIPTION = "Clear description"

# State tracking
start_time = None
is_registered_with_hermes = False
```

### Lifespan Management
All components use the async context manager pattern:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup with timing
    import time
    start_time = time.time()
    
    # Component initialization
    await startup_logic()
    
    yield
    
    # Graceful shutdown
    await cleanup_logic()
    await asyncio.sleep(0.5)  # Socket release
```

## Error Handling

### Consistent Error Responses
```python
class ErrorResponse(TektonBaseModel):
    error: str
    component: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None
```

### HTTP Status Codes
- `200` - Success
- `207` - Degraded (partial functionality)
- `400` - Bad request
- `404` - Not found
- `500` - Internal server error
- `503` - Service unavailable

## Documentation Requirements

### OpenAPI Configuration
```python
app = FastAPI(
    **get_openapi_configuration(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION
    )
)
```

### Endpoint Documentation
Every endpoint must have:
- Clear docstring description
- Response model specified
- Error cases documented
- Example in OpenAPI schema

## Security Considerations

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Future Enhancements
- Authentication/Authorization (not yet standardized)
- Rate limiting (planned)
- Request validation middleware
- API key management

## Performance Guidelines

### Async Operations
- All I/O operations must be async
- Use `httpx` for async HTTP calls
- Proper connection pooling
- Timeout configuration

### Health Check Efficiency
- Health checks must respond quickly (<100ms)
- Avoid expensive operations
- Cache health status when appropriate
- Use circuit breakers for dependencies

## Testing Standards

### Required Tests
1. All endpoints must have tests
2. Health/ready endpoints tested for various states
3. Error cases must be tested
4. Integration tests with Hermes registration
5. MCP tool functionality tests

### Test Patterns
```python
@pytest.mark.asyncio
async def test_health_endpoint():
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["component"] == "mycomponent"
    assert response.json()["version"] == "0.1.0"
```