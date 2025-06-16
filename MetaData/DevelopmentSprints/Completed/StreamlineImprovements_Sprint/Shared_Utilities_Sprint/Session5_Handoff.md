# Shared Utilities Sprint - Session 5 Handoff

## Context for Next Session

You are continuing the Shared Utilities Sprint for the Tekton project. In Sessions 1-4, all phantom import issues were fixed, shared utilities were created, and we've been systematically updating components to use modern patterns. Session 5 focused on updating three more components and discovered a critical issue with component launch mechanisms.

## Current State
- All shared utilities have been created and are working well
- 8 components have been updated (3 in this session)
- A port conflict in Hermes was discovered and fixed
- Launch mechanism inconsistencies were identified

## Completed Components (8/15)
✅ **Apollo** - Updated to lifespan, fixed RhetorInterface protocol issue
✅ **Athena** - Fixed registration issue, now using all shared utilities properly
✅ **Budget** - Was already using modern patterns, cleaned up duplicate registration code
✅ **Engram** - Fixed hardcoded port 8000, updated to use env_config throughout
✅ **Ergon** - Utilities updated, has separate database schema issue (not our concern)
✅ **Harmonia** - Updated to lifespan pattern, FastMCP integration temporarily disabled with TODO
✅ **Hephaestus** - Updated (UI server using HTTP server, not FastAPI)
✅ **Hermes** - Updated to lifespan pattern, fixed port conflict (DB MCP was using 8002 instead of 8500)

## Remaining Components (7/15)
Alphabetically:
- [ ] Metis
- [ ] Prometheus
- [ ] Rhetor
- [ ] Sophia
- [ ] Synthesis
- [ ] Telos
- [ ] Tekton-core (do last)

## Critical Issue Discovered: Launch Mechanism Inconsistency

### The Problem
The enhanced launcher script expects components to launch in a standardized way, but components use different patterns:
- **Ergon**: Requires `uvicorn ergon.api.app:app --host 0.0.0.0 --port 8002`
- **Rhetor**: Requires `python -m rhetor` (which internally starts uvicorn)
- **Others**: May have their own patterns

This causes components to fail to start properly even when the launcher reports success.

### Port Assignments (Verify These)
Based on the code, the correct ports should be:
- Hermes: 8001
- Ergon: 8002
- Rhetor: 8003
- Database MCP Server: 8500 (was incorrectly defaulting to 8002 in Hermes lifespan)

## Key Patterns to Apply (Continue Using)

### 1. Update Imports
```python
# Old
import logging
from fastapi import FastAPI
from tekton.utils.port_config import get_component_port

# New
from contextlib import asynccontextmanager
# Import shared utils
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.utils.env_config import get_component_config
from shared.utils.errors import StartupError
from shared.utils.startup import component_startup, StartupMetrics
from shared.utils.shutdown import GracefulShutdown
```

### 2. Replace Logger
```python
# Old
logger = logging.getLogger(__name__)

# New
logger = setup_component_logging("component_name")
```

### 3. Create Lifespan Pattern
Replace `@app.on_event("startup")` and `@app.on_event("shutdown")` with:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for Component"""
    # Startup logic here
    yield
    # Shutdown logic here
    await asyncio.sleep(0.5)  # Socket release for macOS

app = FastAPI(..., lifespan=lifespan)
```

### 4. Fix Hardcoded Ports
Replace any hardcoded port values with:
```python
config = get_component_config()
port = config.component.port if hasattr(config, 'component') else int(os.environ.get("COMPONENT_PORT", default))
```

## Common Issues to Watch For

1. **Hardcoded ports** - Especially in registration calls
2. **Import errors** - `setup_component_logger` vs `setup_component_logging`
3. **Missing imports** - Some components import from non-existent `tekton.utils.port_config`
4. **Component-specific issues** - Like Harmonia's FastMCP signature mismatch

## Plan for Next Sessions

### Session 6: Complete Shared Utilities Updates
1. Update remaining 7 components (Metis through Tekton-core)
2. Test each component for successful startup and registration
3. Document any component-specific issues

### Session 7: Normalize Launch Process
1. **Analyze Current Launch Patterns**
   - Document how each component currently launches
   - Identify what the enhanced launcher expects
   - Determine the most appropriate standardized pattern

2. **Design Standardized Launch**
   - Option A: All components use `python -m component_name`
   - Option B: All components provide a standardized entry point
   - Option C: Update enhanced launcher to handle different patterns

3. **Implementation Strategy**
   - Add `__main__.py` to components that lack it
   - Ensure all `__main__.py` files follow the same pattern
   - Update run scripts to use consistent commands
   - Test with enhanced launcher

4. **Proposed Standard Pattern**
   ```python
   # component/__main__.py
   import uvicorn
   from .api.app import app
   from shared.utils.env_config import get_component_config
   
   if __name__ == "__main__":
       config = get_component_config()
       port = config.component.port if hasattr(config, 'component') else int(os.environ.get("COMPONENT_PORT", default))
       uvicorn.run(app, host="0.0.0.0", port=port)
   ```

### Final Session: Testing and Retrospective
1. Test all components with standardized launch
2. Verify system health with all components running
3. Document lessons learned
4. Create maintenance guide

## Testing Commands (Per Component)

```bash
# Kill component
python scripts/enhanced_tekton_killer.py --components component_name --force

# Launch component
python scripts/enhanced_tekton_launcher.py --components component_name

# Check health
curl -s http://localhost:PORT/health | python -m json.tool

# Check system status
python scripts/enhanced_tekton_status.py | grep ComponentName
```

## Success Metrics
- [ ] All components start without errors
- [ ] All components register with Hermes (show ✅ in status)
- [ ] No deprecation warnings for FastAPI events
- [ ] All components use env_config for port configuration
- [ ] All components can be launched with enhanced launcher (after normalization)

## Notes for Next Session
- The Hermes port conflict fix is critical - ensure it's committed
- Harmonia's FastMCP issue has a TODO and needs a separate sprint
- Consider creating a component template for future components
- The launch normalization will significantly improve system reliability

## Questions to Consider
1. Should we use uvicorn directly or through a wrapper?
2. Should components that don't need async (like Hephaestus) be converted?
3. How should we handle components with special requirements?

Continue with completing the shared utilities updates first, then tackle launch normalization!