# API Migration Guide

This guide helps you migrate existing Tekton components to the new API standards.

## Pre-Migration Checklist

Before starting migration:
- [ ] Component has tests that pass
- [ ] Current API is documented
- [ ] Backup current implementation
- [ ] Review the API Standards documentation

## Migration Steps

### Step 1: Add Required Imports

Add these imports after existing shared utilities:
```python
# Add to imports section
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)
```

### Step 2: Update Component Configuration

Add these constants after logger setup:
```python
# Component configuration (REQUIRED - API Consistency Standards)
COMPONENT_NAME = "YourComponent"  # Use PascalCase
COMPONENT_VERSION = "0.1.0"       # Must be 0.1.0
COMPONENT_DESCRIPTION = "Your component description"

# Add tracking variables
start_time = None
is_registered_with_hermes = False
```

### Step 3: Update Lifespan Function

Add global declarations and time tracking:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    global hermes_registration, heartbeat_task, start_time, is_registered_with_hermes
    
    # Track startup time
    import time
    start_time = time.time()
    
    # ... rest of lifespan
```

Update registration to capture status:
```python
# Change from:
is_registered = await hermes_registration.register_component(...)

# To:
is_registered_with_hermes = await hermes_registration.register_component(
    component_name=COMPONENT_NAME.lower(),
    port=port,
    version=COMPONENT_VERSION,  # Use constant
    # ... other params
)
```

### Step 4: Update FastAPI App Creation

Replace:
```python
app = FastAPI(
    title="Your Component API",
    description="Description",
    version="1.0.0",
    lifespan=lifespan
)
```

With:
```python
app = FastAPI(
    **get_openapi_configuration(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION
    ),
    lifespan=lifespan
)
```

### Step 5: Create Standard Routers

After CORS middleware, add:
```python
# Create standard routers (API Consistency Standards)
routers = create_standard_routers(COMPONENT_NAME)
```

### Step 6: Migrate Endpoints

#### Infrastructure Endpoints

Change from:
```python
@app.get("/")
async def root():
    # ...

@app.get("/health")
async def health_check():
    # ...
```

To:
```python
@routers.root.get("/")
async def root():
    return {
        "name": COMPONENT_NAME,
        "version": COMPONENT_VERSION,
        "description": COMPONENT_DESCRIPTION,
        "status": "running",
        "docs": "/api/v1/docs"
    }

@routers.root.get("/health")
async def health_check():
    return create_health_response(
        component_name=COMPONENT_NAME.lower(),
        port=port,
        version=COMPONENT_VERSION,
        status="healthy",
        registered=is_registered_with_hermes,
        details={...}
    )
```

#### Business Logic Endpoints

Change from:
```python
@app.get("/api/resources")
@app.post("/api/resources")
```

To:
```python
@routers.v1.get("/resources")
@routers.v1.post("/resources")
```

### Step 7: Add New Required Endpoints

Add ready endpoint:
```python
routers.root.add_api_route(
    "/ready",
    create_ready_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        start_time=start_time or 0,
        readiness_check=lambda: your_readiness_check()
    ),
    methods=["GET"]
)
```

Add discovery endpoint:
```python
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION,
        endpoints=[
            EndpointInfo(
                path="/api/v1/your-endpoint",
                method="GET",
                description="Endpoint description"
            ),
            # List all your endpoints
        ],
        capabilities=["list", "your", "capabilities"],
        dependencies={
            "hermes": "http://localhost:8001",
            # Add other dependencies
        },
        metadata={
            "documentation": "/api/v1/docs"
        }
    ),
    methods=["GET"]
)
```

### Step 8: Mount Routers

Before including other routers, add:
```python
# Mount standard routers (REQUIRED)
mount_standard_routers(app, routers)

# Then include other routers
app.include_router(your_router, prefix="/api/v1")

# MCP router remains at /api/mcp/v2
app.include_router(mcp_router, prefix="/api/mcp/v2", tags=["mcp"])
```

## Common Migration Issues

### Issue 1: Conflicting Routes
**Problem:** Existing routes conflict with standard routers
**Solution:** Remove old route definitions before mounting standard routers

### Issue 2: Hardcoded Versions
**Problem:** Version hardcoded in multiple places
**Solution:** Use COMPONENT_VERSION constant everywhere

### Issue 3: Missing Global Declarations
**Problem:** UnboundLocalError in lifespan
**Solution:** Add all required globals at start of lifespan

### Issue 4: Old Health Check Format
**Problem:** Custom health check format
**Solution:** Use create_health_response() for consistency

### Issue 5: Business Logic at Root
**Problem:** Endpoints like `/resources` at root
**Solution:** Move under `/api/v1/` using v1 router

## Testing Migration

After migration, test:

```bash
# Basic health checks
curl http://localhost:PORT/health
curl http://localhost:PORT/ready
curl http://localhost:PORT/api/v1/discovery

# Verify version
curl http://localhost:PORT/ | jq .version
# Should return "0.1.0"

# Check all endpoints moved
curl http://localhost:PORT/api/v1/your-endpoints

# Run component tests
pytest tests/
```

## Rollback Plan

If migration causes issues:
1. Git stash or commit changes
2. Revert to previous version
3. Debug specific issues
4. Re-attempt migration step by step

## Component-Specific Notes

### Budget
- Has WebSocket endpoints - keep at root
- Assistant endpoints move to /api/v1/assistant

### Hermes
- Central hub - test thoroughly
- Multiple routers all move under /api/v1/

### Rhetor
- Complex structure - minimal changes for now
- Full reorganization in separate sprint

### Ergon
- A2A endpoints move to /api/v1/a2a
- Memory endpoints move to /api/v1/memory

## Post-Migration Checklist

- [ ] All tests pass
- [ ] Version shows as "0.1.0"
- [ ] Health check uses standard format
- [ ] Ready endpoint responds
- [ ] Discovery lists all capabilities
- [ ] Business logic under /api/v1/
- [ ] MCP at /api/mcp/v2/
- [ ] Documentation updated
- [ ] Component launches successfully
- [ ] tekton-status shows component
- [ ] Shutdown endpoint works

## Support

If you encounter issues:
1. Check the error carefully
2. Review this guide's common issues
3. Look at reference implementations (Athena, Apollo)
4. Check shared/api/example_usage.py