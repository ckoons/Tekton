# GoodLaunch Sprint - Session 5 Prompt

## Context
You are continuing the GoodLaunch Sprint to achieve reliable component launch across the Tekton ecosystem. The previous 4 sessions have made tremendous progress, bringing the system from 0% to 93% operational.

## Current Status
- **13/14 components working (93%)**
- Only Telos remains non-functional due to startup hanging

## Session 4 Achievements
1. Fixed Rhetor's unterminated triple-quoted string literal
2. Fixed Harmonia's missing root endpoint (was returning 404)
3. Fixed Sophia's indentation error in llm_integration.py
4. Fixed Budget's incorrect await on synchronous function
5. System now launches successfully with only one component failing

## Remaining Issues

### Critical (Blocking Launch)
1. **Telos** - Startup hangs indefinitely
   - Uses deprecated @app.on_event("startup") handler
   - Process starts but never completes initialization
   - No log file is created (redirected output issue)
   - Needs investigation into startup event handler

### Non-Critical (Components run but with errors)
1. **Ergon** - MCP tool registration errors
   - Error: `adapt_tool() got an unexpected keyword argument 'component_manager'`
   - Component runs but tools don't register properly
   
2. **Minor timeout warnings** during launch for some components
   - Components eventually start but take longer than expected

## Session 5 Objectives

### Primary Goal
1. Fix Telos startup hang issue
   - Migrate from @app.on_event("startup") to lifespan context manager
   - Ensure proper initialization without blocking
   - Verify log file creation works correctly

### Secondary Goals
1. Fix Ergon's MCP tool registration errors
2. Investigate and optimize component startup times to reduce timeouts
3. Document final system state and any remaining minor issues

### Stretch Goals
1. Create a comprehensive system health check script
2. Document recommended startup order for components
3. Create troubleshooting guide for common launch issues

## Technical Context

### Telos Specific Issues
```python
# Current problematic pattern in Telos
@app.on_event("startup")
async def startup_event():
    # This is deprecated and may be causing the hang
    # Need to migrate to:
    # app = FastAPI(lifespan=lifespan)
```

### Ergon MCP Registration
The issue is in the tooling utility expecting different parameters than what's being passed. Need to trace the actual function signature and fix the mismatch.

## Success Criteria
1. All 14 components launch successfully
2. No critical errors in logs
3. System is stable enough for development use
4. Clear documentation of any remaining minor issues

## Important Notes
- The system is already 93% functional, so be careful not to break working components
- Test changes incrementally 
- Focus on Telos first as it's the last non-functional component
- Document any workarounds needed for full system operation

When you receive the launch log, analyze it for:
1. Telos startup behavior and any error messages
2. Ergon's MCP registration errors
3. Any new issues that may have emerged
4. Overall system health and stability