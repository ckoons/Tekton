# Shared Utilities Sprint - Session 4 Handoff

## Context for Next Session

You are continuing the Shared Utilities Sprint for the Tekton project. In Sessions 1-3, all phantom import issues were fixed, shared utilities were created, and we began systematically updating components to use modern patterns. The system is healthy with most components running and properly importing from `shared.utils`.

## Current State
- All shared utilities have been created and are working well
- 5 components have been fully updated to modern patterns
- System health is good with proper registrations

## Completed Components (5/15)
✅ **Apollo** - Updated to lifespan, fixed RhetorInterface protocol issue, worked around missing start() methods
✅ **Athena** - Fixed registration issue, now using all shared utilities properly
✅ **Budget** - Was already using modern patterns, cleaned up duplicate registration code
✅ **Engram** - Fixed hardcoded port 8000, updated to use env_config throughout
✅ **Ergon** - Utilities updated, has separate database schema issue (not our concern)

## Remaining Components (10/15)
Alphabetically:
- [ ] Harmonia
- [ ] Hephaestus  
- [ ] Hermes
- [ ] Metis
- [ ] Prometheus
- [ ] Rhetor
- [ ] Sophia
- [ ] Synthesis
- [ ] Telos
- [ ] Tekton-core (do last)

## Key Patterns to Apply

### 1. Update Imports
```python
# Old
import logging
from fastapi import FastAPI
# Import Hermes registration utility

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

1. **Hardcoded ports** - Especially in registration calls (port=8000, etc.)
2. **Import errors** - `setup_component_logger` vs `setup_component_logging`
3. **Missing imports** - Some components import from non-existent `tekton.utils.port_config`
4. **Component-specific issues** - Like Apollo's ProtocolEnforcer lacking start() method

## Commands to Test Each Component

```bash
# Kill component
python scripts/enhanced_tekton_killer.py --components component_name --force

# Launch component
python scripts/enhanced_tekton_launcher.py --components component_name

# Check health
curl -s http://localhost:PORT/health | python -m json.tool | grep -E "(status|registered)"

# Check system status
python scripts/enhanced_tekton_status.py | grep ComponentName
```

## Success Metrics
- [ ] Component starts without errors
- [ ] Component registers with Hermes (shows ✅ in status)
- [ ] No deprecation warnings for FastAPI events
- [ ] Uses env_config for port configuration

## Notes for Next Session
- Ergon has a database schema issue unrelated to shared utilities
- Most updates are mechanical and follow the same pattern
- Budget was already mostly compliant, just needed cleanup
- Apollo had the most complex issues with component start methods

## Questions Already Answered
1. Should we update to FastAPI lifespan? **YES**
2. Should we fix hardcoded ports? **YES** - use env_config
3. Skip Codex and Terma? **YES** - they will be rewritten

Continue alphabetically through the remaining components!