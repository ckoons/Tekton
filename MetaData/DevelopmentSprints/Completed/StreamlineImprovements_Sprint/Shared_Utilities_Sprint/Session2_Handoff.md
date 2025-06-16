# Shared Utilities Sprint - Session 2 Handoff

## Context for Next Session

You are continuing the Shared Utilities Sprint for the Tekton project. In Session 1, all phantom import issues were fixed and components are now properly importing from `shared.utils`. The system is at 71.5% health with 14/16 components running (Terma and Tekton Core are expected to fail as they will be rewritten).

## Current State
- All components have been updated to import from `shared.utils.*` correctly
- PYTHONPATH is properly set in the launcher
- Existing shared utilities: `health_check.py`, `hermes_registration.py`, `logging_setup.py`
- All import errors have been resolved

## Primary Objective
Complete Phase 1 of the Shared Utilities Sprint by creating the remaining utility modules and begin Phase 2 integration.

## Tasks for Session 2

### 1. Create Server Startup Utilities (`/shared/utils/startup.py`)
**Priority: HIGH** - This addresses socket binding issues on macOS

```python
# Key features to implement:
- component_startup() function with timeout and error handling
- StartupMetrics dataclass for tracking startup performance
- Socket release fix for macOS (await asyncio.sleep(0.5) after shutdown)
- Standardized startup sequence with dependency checking
```

Reference the design in: `/MetaData/DevelopmentSprints/StreamlineImprovements_Sprint/Shared_Utilities_Sprint/README.md`

### 2. Create Graceful Shutdown (`/shared/utils/shutdown.py`)
```python
# Key features:
- GracefulShutdown class
- Signal handling (SIGTERM, SIGINT)
- Cleanup task registration
- component_lifespan() context manager for FastAPI
```

### 3. Create Environment Config Loader (`/shared/utils/env_config.py`)
```python
# Key features:
- Centralized environment variable management
- Type conversion and validation
- Default values with override capability
- Component-specific config sections
```

### 4. Create FastMCP Helpers (`/shared/utils/mcp_helpers.py`)
```python
# Key features:
- create_mcp_server() standardized function
- register_mcp_tools() with error handling
- Tool schema conversion helpers (important for Metis-style tools)
```

### 5. Create Component Templates (`/shared/utils/templates.py`)
```python
# Key features:
- create_main_function_template() - fixes missing main() issues
- create_component_scaffolding() - complete component structure
- Standardized FastAPI app creation
```

### 6. Create Error Classes (`/shared/utils/errors.py`)
```python
# Key features:
- TektonError base class
- StartupError, RegistrationError, ConfigurationError
- Component-aware error messages
```

### 7. Begin Integration (Phase 2)
After creating utilities, pick 2-3 components to migrate:
- Start with Budget (already partially updated)
- Then Athena (clean, well-structured)
- Then one more of your choice

## Important Notes

1. **Socket Binding Issue**: Many components need the socket release fix on macOS. Add `await asyncio.sleep(0.5)` in shutdown handlers.

2. **Deprecated FastAPI Events**: Many components use `@app.on_event("startup")` which is deprecated. When you see this, note it but don't fix yet - focus on creating utilities first.

3. **Test Imports**: After creating each utility, test that it imports correctly:
   ```bash
   cd /Users/cskoons/projects/github/Tekton
   python -c "from shared.utils.startup import component_startup; print('Import successful')"
   ```

4. **Maintain Compatibility**: Don't break existing functionality. The utilities should be drop-in replacements.

## Success Metrics
- [ ] All 6 utility modules created and importable
- [ ] At least 2 components migrated to use new utilities
- [ ] No regression in system health (maintain 71.5% or better)
- [ ] Documentation updated with usage examples

## Commands to Start
```bash
# Check current status
cd /Users/cskoons/projects/github/Tekton
python scripts/enhanced_tekton_status.py

# Create the first utility
touch shared/utils/startup.py
# Then implement according to the design in README.md
```

## Questions to Ask User
1. Should we update components to use FastAPI lifespan events instead of deprecated @app.on_event?
2. Any preference on which components to migrate first in Phase 2?
3. Should we create a migration script to automate some of the updates?

Good luck with Session 2! The groundwork is solid, and the path forward is clear.