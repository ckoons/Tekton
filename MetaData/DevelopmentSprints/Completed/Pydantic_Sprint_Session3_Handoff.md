# Pydantic Sprint Session 3 Handoff Document

## Sprint Context
**Date**: January 6, 2025  
**Sprint**: Pydantic v2 Standardization  
**Session 2 Completion**: 14% context remaining  
**Approach**: Option 2 - Update both Pydantic models AND launch patterns together

## Critical Note About Shutdown Endpoints
**IMPORTANT**: We attempted to add shutdown endpoints but this caused launch failures. We have removed all shutdown endpoint code. DO NOT re-add without careful testing. The components already have proper shutdown handling in their lifespan context managers.

## Session 2 Accomplishments

### ✅ Completed Components (7/16)

| Component | Pydantic v2 | __main__.py | Launch Script | Notes |
|-----------|-------------|-------------|---------------|-------|
| Hermes | ✅ | ✅ | ⚠️ | Still uses `python -m hermes.api.app` |
| Engram | ✅ | ✅ | ⚠️ | Still uses `python -m engram.api.app` |
| Budget | ✅ | ✅ | ✅ | Fully normalized to `python -m budget` |
| Apollo | ✅ | ✅ | ✅ | Fully normalized to `python -m apollo` |
| Athena | ✅ | ✅ | ✅ | Fully normalized to `python -m athena` |
| Rhetor | ✅ | ✅ | ✅ | Fully normalized to `python -m rhetor` |
| Harmonia | ✅ | ✅ | ✅ | Fully normalized to `python -m harmonia` |

### ❌ Remaining Components (6/16 need Pydantic updates)

| Component | Has Pydantic | Has __main__.py | Launch Pattern | Priority |
|-----------|--------------|-----------------|----------------|----------|
| Prometheus | ✅ (v1) | ❌ | Needs update | HIGH |
| Sophia | ✅ (v1) | ❌ | Needs update | HIGH |
| Metis | ✅ (v1) | ✅ | Needs update | MEDIUM |
| Telos | ✅ (v1) | ❌ | Needs update | MEDIUM |
| Ergon | ✅ (already v2) | ❌ | Already uses `python -m ergon` | LOW (launch only) |
| Synthesis | ❌ | ❌ | Needs update | LOW |

### Skip These Components
- **Terma** - Will be completely revised
- **Codex** - Will be completely revised  
- **Tekton-Core** - Special handling required

## Patterns to Apply

### 1. Pydantic v2 Model Updates
```python
# Change from:
from pydantic import BaseModel, Field, validator

class MyModel(BaseModel):
    field: str
    
    class Config:
        allow_mutation = True
    
    @validator('field')
    def validate_field(cls, v):
        return v

# Change to:
from pydantic import Field, field_validator
from tekton.models import TektonBaseModel

class MyModel(TektonBaseModel):
    field: str
    
    @field_validator('field')
    def validate_field(cls, v):
        return v
```

### 2. Create __main__.py Template
```python
"""Entry point for python -m component"""
from component.api.app import app
import uvicorn
import os

if __name__ == "__main__":
    # Port must be set via environment variable
    port = int(os.environ.get("COMPONENT_PORT"))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 3. Update Launch Script
```bash
# Change from:
python -m component.api.app

# To:
python -m component
```

## Next Session Tasks

### 1. Fix Prometheus (HIGH PRIORITY)
- Update models in `prometheus/models/timeline.py`
- Update models in `prometheus/api/fastmcp_endpoints.py`
- Create `prometheus/__main__.py`
- Update `run_prometheus.sh`

### 2. Fix Sophia (HIGH PRIORITY)
- Update models in `sophia/models/component.py`
- Update models in `sophia/api/app_enhanced.py`
- Update models in `sophia/api/fastmcp_endpoints.py`
- Create `sophia/__main__.py`
- Update `run_sophia.sh`

### 3. Fix Metis (MEDIUM PRIORITY)
- Update models in `metis/api/app.py`
- Update models in `metis/api/schemas.py`
- Update models in `metis/api/fastmcp_endpoints.py`
- Verify `metis/__main__.py` (already exists)
- Update `run_metis.sh`

### 4. Fix Telos (MEDIUM PRIORITY)
- Update models in `telos/api/app.py`
- Update models in `telos/models/export.py`
- Update models in `telos/models/project.py`
- Create `telos/__main__.py`
- Update `run_telos.sh`

### 5. Fix Ergon Launch (LOW PRIORITY)
- Ergon already uses Pydantic v2
- Only needs `ergon/__main__.py`
- Launch script already correct

### 6. Fix Synthesis (LOW PRIORITY)
- Check if it has any Pydantic models
- Create `synthesis/__main__.py`
- Update `run_synthesis.sh`

### 7. Normalize Hermes & Engram Launch
- Update `run_hermes.sh` to use `python -m hermes`
- Update `run_engram.sh` to use `python -m engram`

## Important Reminders

1. **NO HARDCODED PORTS** - Always use environment variables
2. **NO SHUTDOWN ENDPOINTS** - They cause launch failures
3. **Import Order Matters** - Field, ConfigDict from pydantic, not tekton.models
4. **Test Each Component** - Ensure it launches before moving on
5. **@validator → @field_validator** - Don't forget decorator updates

## Quick Test Commands
```bash
# After updating a component:
cd ComponentDir
python -m component  # Test direct launch
./run_component.sh    # Test launch script
curl http://localhost:$PORT/health  # Test health endpoint
```

## Heartbeat Issue
Note: Hermes logs show many "422 Unprocessable Entity" errors for `/api/heartbeat`. This may need investigation but is separate from the Pydantic sprint.

## Success Criteria
- All components use Pydantic v2.11.5
- All components have proper __main__.py files  
- All launch scripts use `python -m component`
- No hardcoded ports anywhere
- All components launch successfully

The foundation is solid. Continue methodically: one component at a time.