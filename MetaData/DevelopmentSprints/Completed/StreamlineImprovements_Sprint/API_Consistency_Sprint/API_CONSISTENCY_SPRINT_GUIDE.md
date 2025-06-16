# API Consistency Sprint Implementation Guide

**Sprint Start Date**: TBD  
**Status**: Ready to Begin  
**Prerequisites**: Shared_Utilities_Sprint ✅, Pydantic_V2_Migration_Sprint ✅

## Context from Previous Sprints

### What's Already Standardized
1. **Shared Utilities** (Completed):
   - `create_health_response()` for health endpoints
   - `add_shutdown_endpoint_to_app()` for shutdown handling
   - `component_startup()` for startup metrics
   - `setup_component_logging()` for consistent logging
   - `get_component_config()` for configuration management

2. **Pydantic v2** (Completed):
   - All models use `TektonBaseModel`
   - Consistent validation patterns
   - No hardcoded ports

## Sprint Objectives with Implementation Details

### 1. Define Standard API Patterns

**Current State**: Each component has slightly different API organization
**Target State**: Consistent API structure across all components

#### Standard API Directory Structure
```
component/
├── api/
│   ├── __init__.py
│   ├── app.py              # FastAPI app with lifespan
│   ├── dependencies.py     # Shared dependencies
│   ├── models.py          # Request/Response models
│   └── endpoints/
│       ├── __init__.py
│       ├── core.py        # Component-specific endpoints
│       ├── mcp.py         # MCP v2 endpoints
│       └── admin.py       # Admin endpoints (new)
```

#### Standard Endpoint Patterns

**Create `shared/api/base_endpoints.py`**:
```python
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from tekton.models.base import TektonBaseModel

class StandardResponse(TektonBaseModel):
    """Standard API response wrapper"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

def create_standard_router(component_name: str) -> APIRouter:
    """Create a router with standard endpoints"""
    router = APIRouter()
    
    @router.get("/info", response_model=StandardResponse)
    async def get_info():
        """Get component information"""
        return StandardResponse(
            success=True,
            data={
                "component": component_name,
                "api_version": "v1",
                "mcp_version": "v2"
            }
        )
    
    return router
```

### 2. Create Shared API Utilities

**Create `shared/api/exceptions.py`**:
```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from shared.utils.logging_setup import get_component_logger

class TektonAPIException(HTTPException):
    """Base exception for Tekton API errors"""
    def __init__(self, status_code: int, detail: str, component: str):
        self.component = component
        super().__init__(status_code=status_code, detail=detail)

async def tekton_exception_handler(request: Request, exc: TektonAPIException):
    """Consistent exception handling across components"""
    logger = get_component_logger(exc.component)
    logger.error(f"API Exception: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "component": exc.component,
            "path": str(request.url)
        }
    )
```

**Create `shared/api/middleware.py`**:
```python
from fastapi import Request
import time
from shared.utils.logging_setup import get_component_logger

async def request_timing_middleware(request: Request, call_next):
    """Log request timing for all endpoints"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

async def component_identification_middleware(request: Request, call_next, component_name: str):
    """Add component identification to all responses"""
    response = await call_next(request)
    response.headers["X-Tekton-Component"] = component_name
    response.headers["X-Tekton-Version"] = "0.1.0"
    return response
```

### 3. Add Missing main() Functions

**Components Missing `__main__.py`**:
1. Athena
2. Sophia

**Standard `__main__.py` Template**:
```python
"""Entry point for python -m component_name"""
from component_name.api.app import app
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("COMPONENT_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 4. Standardize Health Checks and Error Responses

**Current Issues**:
- Some components return different health response formats
- Error responses are inconsistent
- Status endpoints have varying information

**Standard Health Response** (already exists, ensure adoption):
```python
# All components should use:
from shared.utils.health_check import create_health_response

@app.get("/health")
async def health_check():
    return create_health_response(
        component_name=COMPONENT_NAME,
        port=port,
        version="0.1.0",
        status="healthy",  # or "degraded", "unhealthy"
        registered=hermes_registration.is_registered,
        uptime=uptime,
        details={...}
    )
```

**Standard Status Response**:
```python
# Create shared/api/models.py
class ComponentStatus(TektonBaseModel):
    """Standard component status response"""
    component: str
    status: str
    version: str
    port: int
    registered: bool
    uptime: float
    capabilities: List[str]
    health: Dict[str, str]
    mcp_tools: Optional[List[str]] = None
    connections: Optional[Dict[str, str]] = None
```

### 5. Implement Service Discovery

**Approach**: Enhance Hermes as the service discovery mechanism

**Create `shared/api/discovery.py`**:
```python
from typing import Dict, List, Optional
import httpx
from shared.utils.logging_setup import get_component_logger

class ServiceDiscovery:
    """Service discovery client for Tekton components"""
    
    def __init__(self, hermes_url: str = None):
        self.hermes_url = hermes_url or os.environ.get("HERMES_URL", "http://localhost:8001")
        self.logger = get_component_logger("service_discovery")
        self._cache = {}
        self._client = httpx.AsyncClient()
    
    async def get_component_endpoint(self, component_name: str) -> Optional[str]:
        """Get the endpoint for a component"""
        try:
            response = await self._client.get(
                f"{self.hermes_url}/api/components/{component_name}"
            )
            if response.status_code == 200:
                data = response.json()
                return f"http://localhost:{data['port']}"
        except Exception as e:
            self.logger.error(f"Failed to discover {component_name}: {e}")
        return None
    
    async def list_components(self) -> List[Dict[str, Any]]:
        """List all available components"""
        try:
            response = await self._client.get(f"{self.hermes_url}/api/components")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to list components: {e}")
        return []
    
    async def call_component(self, component_name: str, endpoint: str, **kwargs):
        """Call another component's API"""
        base_url = await self.get_component_endpoint(component_name)
        if not base_url:
            raise Exception(f"Component {component_name} not found")
        
        url = f"{base_url}{endpoint}"
        return await self._client.request(**kwargs, url=url)
```

**Update Components to Use Service Discovery**:
```python
# In component's app.py
from shared.api.discovery import ServiceDiscovery

# In lifespan
app.state.discovery = ServiceDiscovery()

# Usage in endpoints
@router.get("/test-connection/{component}")
async def test_connection(component: str):
    discovery = app.state.discovery
    endpoint = await discovery.get_component_endpoint(component)
    if endpoint:
        return {"connected": True, "endpoint": endpoint}
    return {"connected": False}
```

## Implementation Order

### Phase 1: Create Shared API Modules
1. Create `/shared/api/` directory
2. Implement `base_endpoints.py`
3. Implement `exceptions.py`
4. Implement `middleware.py`
5. Implement `models.py`
6. Implement `discovery.py`

### Phase 2: Add Missing Entry Points
1. Create `Athena/athena/__main__.py`
2. Create `Sophia/sophia/__main__.py`
3. Test both components can be launched with `python -m`

### Phase 3: Update All Components
For each component:
1. Add standard middleware
2. Ensure health endpoint uses `create_health_response`
3. Standardize status endpoint format
4. Add error handling with `TektonAPIException`
5. Integrate service discovery

### Phase 4: Update MCP Endpoints
1. Standardize all MCP endpoints to `/api/mcp/v2/`
2. Ensure consistent tool listing format
3. Add MCP tool discovery to component registration

## Files to Update

### Components to Update (15 total):
1. Hermes
2. Engram
3. Budget
4. Apollo
5. Athena (+ add __main__.py)
6. Rhetor
7. Harmonia
8. Prometheus
9. Telos
10. Metis
11. Sophia (+ add __main__.py)
12. Synthesis
13. Ergon
14. tekton-core
15. Hephaestus

### Specific File Updates per Component:
- `component/api/app.py` - Add middleware, standardize endpoints
- `component/api/endpoints/mcp.py` - Move to `/api/mcp/v2/` path
- `component/api/dependencies.py` - Add service discovery dependency
- NEW: `component/api/endpoints/admin.py` - Standard admin endpoints

## Success Criteria

1. **Consistent API Structure**: All 15 components follow the same directory structure
2. **Standard Endpoints**: All components have `/health`, `/status`, `/info` with consistent responses
3. **Entry Points**: All components can be launched with `python -m component_name`
4. **Error Handling**: All components use `TektonAPIException` and consistent error responses
5. **Service Discovery**: Components can discover and communicate with each other via Hermes
6. **MCP Standardization**: All MCP endpoints at `/api/mcp/v2/` with consistent formatting
7. **Zero Breaking Changes**: Existing functionality preserved, only adding consistency

## Testing Checklist

For each component:
- [ ] `python -m component_name` launches successfully
- [ ] `/health` returns standard health response
- [ ] `/status` returns `ComponentStatus` model
- [ ] `/info` returns component information
- [ ] `/api/mcp/v2/tools/list` returns MCP tools
- [ ] Errors return consistent format
- [ ] Service discovery can find component
- [ ] Component can discover other services

## Example Migration

### Before (Inconsistent):
```python
# Some component's app.py
@app.get("/health")
async def health():
    return {"status": "ok", "component": "mycomponent"}

@app.get("/component-status")  # Non-standard path
async def status():
    return {"running": True, "port": 8000}  # Hardcoded port

# No error handling
@app.post("/api/operation")
async def operation():
    raise Exception("Something went wrong")  # Unhandled
```

### After (Standardized):
```python
# Updated app.py
from shared.utils.health_check import create_health_response
from shared.api.models import ComponentStatus
from shared.api.exceptions import TektonAPIException

@app.get("/health")
async def health_check():
    return create_health_response(
        component_name=COMPONENT_NAME,
        port=app.state.port,
        version="0.1.0",
        status="healthy",
        registered=hermes_registration.is_registered,
        uptime=uptime,
        details={...}
    )

@app.get("/status", response_model=ComponentStatus)
async def get_status():
    return ComponentStatus(
        component=COMPONENT_NAME,
        status="running",
        version="0.1.0",
        port=app.state.port,
        registered=hermes_registration.is_registered,
        uptime=uptime,
        capabilities=["capability1", "capability2"],
        health={"api": "healthy"},
        mcp_tools=["tool1", "tool2"]
    )

@app.post("/api/operation")
async def operation():
    try:
        # operation logic
    except Exception as e:
        raise TektonAPIException(
            status_code=500,
            detail=str(e),
            component=COMPONENT_NAME
        )
```

## Notes for Implementation

1. **Preserve Existing Functionality**: This sprint adds consistency, not new features
2. **Use Existing Patterns**: Build on shared utilities from previous sprints
3. **Document Changes**: Update component READMEs with new standard endpoints
4. **Test Incrementally**: Update and test one component at a time
5. **Backward Compatibility**: Keep old endpoints working with deprecation notices

## Commit Message Template
```
feat: Standardize API patterns for [Component]

- Add standard middleware and error handling
- Implement consistent health and status endpoints
- Integrate service discovery via Hermes
- Standardize MCP endpoints to /api/mcp/v2/
- Add [__main__.py for python -m support] (if applicable)

Part of API_Consistency_Sprint

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

This guide provides everything needed for a successful API Consistency Sprint implementation.