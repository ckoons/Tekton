# Shared Utilities Integration Updates

**Date**: 2025-06-03  
**Context**: Post-Pydantic v2 Migration Sprint documentation updates

## Overview

This document summarizes the shared utilities integration patterns that are now reflected in the updated Building New Tekton Components documentation. These patterns were established during the Shared Utilities Sprint and are now mandatory for all new components.

## Key Integration Points Updated

### 1. Model Base Class Standardization

**Previous Pattern**:
```python
from pydantic import BaseModel

class ExampleModel(BaseModel):
    field: str
```

**Current Pattern** (Now Documented):
```python
from tekton.models.base import TektonBaseModel

class ExampleModel(TektonBaseModel):
    field: str
```

**Benefits**:
- Centralized validation logic
- Consistent configuration across components
- Future-proof for Pydantic updates

### 2. Port Configuration Management

**Previous Pattern**:
```javascript
config: {
    apiUrl: 'http://localhost:8015',
    wsUrl: 'ws://localhost:8015/ws'
}
```

**Current Pattern** (Now Documented):
```javascript
config: {
    apiUrl: `http://localhost:${window.MYCOMPONENT_PORT || 8015}`,
    wsUrl: `ws://localhost:${window.MYCOMPONENT_PORT || 8015}/ws`
}
```

**Benefits**:
- Dynamic port resolution
- Environment-driven configuration
- Single Port Architecture compliance

### 3. Import Pattern Modernization

**Previous Pattern**:
```python
from pydantic import BaseModel, Field
```

**Current Pattern** (Now Documented):
```python
from tekton.models.base import TektonBaseModel
from pydantic import Field
```

**Benefits**:
- Clear separation of concerns
- Reduced direct Pydantic dependencies
- Easier future migration paths

## Mandatory Shared Utilities (Already Documented)

The documentation already correctly shows these mandatory imports:

```python
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.utils.env_config import get_component_config
from shared.utils.errors import StartupError
from shared.utils.startup import component_startup, StartupMetrics
from shared.utils.shutdown import GracefulShutdown
from shared.utils.health_check import create_health_response
from shared.utils.shutdown_endpoint import add_shutdown_endpoint_to_app
```

These were correctly documented during the Shared Utilities Sprint and remain unchanged.

## Updated Examples Alignment

### MCP Model Definitions

All MCP v2 model examples in the documentation now use TektonBaseModel:

```python
class Tool(TektonBaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

class ToolList(TektonBaseModel):
    """Response for tool listing"""
    tools: List[Tool]
```

### Error Handling Patterns

Error response models updated to maintain consistency:

```python
class ErrorResponse(TektonBaseModel):
    error: str
    component: str = "mycomponent"
    timestamp: str
    details: Optional[Dict[str, Any]] = None

# Method calls updated
return JSONResponse(
    status_code=500,
    content=ErrorResponse(
        error=str(exc),
        timestamp=datetime.utcnow().isoformat()
    ).model_dump()  # Updated from .dict()
)
```

## Implementation Validation

All updated documentation patterns have been validated against:

1. **Working Components**: Examples match implementations in Budget, Apollo, Athena, Rhetor, Harmonia, Prometheus, Telos, Metis, Sophia, Synthesis, Ergon
2. **Import Resolution**: All import statements verified against current codebase structure
3. **Functional Testing**: Patterns tested during component migrations
4. **Consistency Checks**: Cross-referenced with established shared utilities

## Developer Experience Improvements

### Before Updates
- Copy-paste examples would fail with import errors
- Hardcoded ports required manual configuration
- Inconsistent model inheritance patterns

### After Updates
- Copy-paste examples work immediately
- Dynamic port configuration works out-of-the-box
- Consistent TektonBaseModel usage across all examples

## Future Maintenance

These updates establish:

1. **Single Source of Truth**: Documentation matches implementation reality
2. **Reduced Support Load**: Working examples reduce developer questions
3. **Consistency Foundation**: Standard patterns enable easier code reviews
4. **Migration Path**: Clear upgrade path for future Pydantic versions

## Integration with Existing Patterns

The updated documentation maintains full compatibility with:

- **Lifespan Patterns**: No changes to asynccontextmanager usage
- **Shared Utilities**: All mandatory utilities still properly documented
- **Launch Scripts**: Environment variable patterns unchanged
- **Health Endpoints**: Standard health check implementations preserved
- **Component Registration**: Hermes integration patterns maintained

## Summary

These documentation updates complete the alignment between the Building New Tekton Components guides and the current implementation reality established during the Pydantic v2 Migration Sprint. The changes are conservative, syntactic updates that ensure developers have working, copy-paste ready examples while maintaining all existing architectural patterns and shared utility integrations.

The documentation now accurately reflects the modern Tekton component development standards while preserving the comprehensive guidance for implementing robust, well-integrated components.