# API Consistency Sprint - Session 2 Handoff Document

## Sprint Overview
The API Consistency Sprint standardizes API patterns across all Tekton components. Session 1 has completed Phase 1 (Standards Definition), Phase 2 (Shared Utilities Creation), and begun Phase 3 (Component Updates).

## What Session 1 Accomplished

### Phase 1: API Standards Definition ✅
Created `/MetaData/DevelopmentSprints/StreamlineImprovements_Sprint/API_Consistency_Sprint/API_Standards.md` which defines:
- Component versioning (all must be "0.1.0")
- Endpoint structure (infrastructure vs business)
- Standard endpoints: `/health`, `/ready`, `/api/v1/discovery`
- Business endpoints under `/api/v1/` prefix
- Error response format using existing models
- OpenAPI documentation standards

### Phase 2: Shared API Utilities ✅
Created in `/Tekton/shared/api/`:
- `routers.py` - Standard router creation (`create_standard_routers`, `mount_standard_routers`)
- `endpoints.py` - Ready and discovery endpoint factories
- `documentation.py` - OpenAPI configuration helper
- `example_usage.py` - Complete integration example
- `README.md` - Documentation

### Phase 3: Component Updates (6 of 13 completed) 🟡

#### Completed Components:
1. **Athena** ✅ - Version 1.0.0→0.1.0, full standardization
2. **Rhetor** ✅ - Version 1.0.0→0.1.0, minimal update (see Rhetor_Reorganization_Plan.md)
3. **Synthesis** ✅ - Version 1.0.0→0.1.0, full standardization
4. **Engram** ✅ - Version 0.8.0→0.1.0, full standardization
5. **Telos** ✅ - Version already 0.1.0, full standardization
6. **Apollo** ✅ - Version already 0.1.0, full standardization

## What Session 2 Needs to Complete

### Remaining Components (7):
1. **Budget** - Already has 0.1.0, needs standard endpoints
2. **Ergon** - Already has 0.1.0, needs standard endpoints
3. **Harmonia** - Already has 0.1.0, needs standard endpoints
4. **Hermes** - Already has 0.1.0, needs standard endpoints (central hub, be careful)
5. **Metis** - Already has 0.1.0, needs standard endpoints
6. **Prometheus** - Already has 0.1.0, needs standard endpoints
7. **Sophia** - Already has 0.1.0, needs standard endpoints

### Standard Update Pattern

For each component, follow these steps:

#### 1. Add Shared API Imports
After the existing shared utils imports, add:
```python
from shared.utils.health_check import create_health_response
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)
```

#### 2. Add Component Configuration
After logger setup, add:
```python
# Component configuration
COMPONENT_NAME = "ComponentName"
COMPONENT_VERSION = "0.1.0"
COMPONENT_DESCRIPTION = "Component description"
start_time = None
is_registered_with_hermes = False
```

#### 3. Update Lifespan/Startup
- Add `global start_time, is_registered_with_hermes` to lifespan
- Add `import time; start_time = time.time()` at start
- Change registration to capture status: `is_registered_with_hermes = await hermes_registration.register_component(...)`
- Use `COMPONENT_VERSION` instead of hardcoded version

#### 4. Update FastAPI App Creation
Replace:
```python
app = FastAPI(
    title="...",
    version="...",
    ...
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
    lifespan=...
)
```

#### 5. Create Standard Routers
After CORS middleware, add:
```python
# Create standard routers
routers = create_standard_routers(COMPONENT_NAME)
```

#### 6. Update Endpoints
- Change `@app.get("/")` to `@routers.root.get("/")`
- Change `@app.get("/health")` to `@routers.root.get("/health")`
- Update health response to use `create_health_response()`
- Change `@app.get("/api/...)` to `@routers.v1.get("/...)`
- Same for POST, PUT, DELETE

#### 7. Add Ready and Discovery Endpoints
Before mounting routers, add:
```python
# Add ready endpoint
routers.root.add_api_route(
    "/ready",
    create_ready_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        start_time=start_time or 0,
        readiness_check=lambda: [component-specific check]
    ),
    methods=["GET"]
)

# Add discovery endpoint
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION,
        endpoints=[
            # List main endpoints
        ],
        capabilities=[
            # List capabilities
        ],
        dependencies={
            "hermes": "http://localhost:8001",
            # Other dependencies
        },
        metadata={
            "documentation": "/api/v1/docs"
        }
    ),
    methods=["GET"]
)
```

#### 8. Mount Routers
Add:
```python
# Mount standard routers
mount_standard_routers(app, routers)

# Include MCP router if available
try:
    from component.api.fastmcp_endpoints import mcp_router
    app.include_router(mcp_router)
except ImportError:
    pass
```

### Special Considerations

#### Budget
- Has assistant and budget routers that need `/api/v1/` prefix
- WebSocket endpoint should remain at root

#### Hermes
- Central hub component - be extra careful
- Has multiple routers (database, llm, a2a)
- All should move under `/api/v1/` prefix

#### Harmonia
- Already has good structure with `/api` prefix
- Just needs to change to `/api/v1/`

#### Prometheus & Sophia
- Simple components with `/api` prefix
- Straightforward updates

### Testing Each Component
After updating, test with:
```bash
tekton-launch [component]
curl http://localhost:[port]/health
curl http://localhost:[port]/ready
curl http://localhost:[port]/api/v1/discovery
tekton-status
tekton-kill
```

### Phase 4: Documentation
After all components are updated:
1. Create migration guide for future components
2. Update main API documentation
3. Create integration examples

## Key Files to Reference
- `/MetaData/DevelopmentSprints/StreamlineImprovements_Sprint/API_Consistency_Sprint/API_Standards.md` - Standards to follow
- `/MetaData/DevelopmentSprints/StreamlineImprovements_Sprint/API_Consistency_Sprint/Component_Changes_Required.md` - Original analysis
- `/Tekton/shared/api/example_usage.py` - Complete example
- Any completed component (Athena, Synthesis, Engram, Telos, Apollo) - Reference implementations

## Success Criteria
- All components report version "0.1.0"
- All have `/health`, `/ready`, `/api/v1/discovery` endpoints
- All business logic under `/api/v1/` prefix
- All use shared utilities for consistency
- All components launch, report healthy, and shutdown cleanly

## Notes
- DO NOT modify MCP endpoints (leave for YetAnotherMCP_Sprint)
- DO NOT break existing functionality
- WebSocket endpoints typically remain at root level
- If uncertain about an endpoint, check completed components for patterns