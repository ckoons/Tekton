# GoodLaunch Sprint - Claude Code Prompt

## Context

You are Claude (Working), the implementation agent for the GoodLaunch Development Sprint. This sprint focuses on achieving reliable component launch and lifecycle management across the Tekton ecosystem.

## Current State

Based on the latest launch analysis, you have already made significant progress:

### ✅ Completed Fixes
- **Fail-fast error handling**: Launch script now properly fails with clear error messages instead of false success
- **Missing tekton_error function**: Added to utility library to fix "command not found" errors
- **MCP function signatures**: Fixed optional parameters to prevent argument errors
- **Several import fixes**: ChatMessage, policy_manager, ResourceRequirement, and Apollo logger ordering

### ❌ Current Issues (Phase 1 Focus)
From the latest launch log, the following import errors need immediate attention:

1. **RetrospectiveAnalysis** missing from `prometheus.models.retrospective`
2. **ChatCompletionOptions** missing from `tekton_llm_client.models` 
3. **get_tools** missing from `apollo.core.mcp`
4. **get_apollo_manager** missing from `apollo.api.dependencies`
5. **MCP capability parameter** issues in Metis (`mcp_tool() got unexpected keyword argument 'capability'`)
6. **Pydantic v2 root validator** warnings in Budget

### 🎯 Success State
- **Hermes** ✅ launching successfully
- **Engram** ✅ launching successfully  
- **Rhetor** ❌ failing (Pydantic field override errors)
- **Other components** ❌ failing due to import errors

## Sprint Structure

You are currently in **Phase 1** of a 5-phase sprint:

### Phase 1: Fix All Remaining Import/Startup Issues *(CURRENT)*
**Goal**: Resolve all import errors preventing component startup
**Success Criteria**: All components start without import errors

### Phase 2: Component Registration and Communication
**Goal**: Ensure all components register with Hermes and maintain healthy status  
**Success Criteria**: 100% component registration rate

### Phase 3: Python Launch System
**Goal**: Replace bash scripts with robust Python programs
**Success Criteria**: Python scripts work from any directory

### Phase 4: Parallel Launch Optimization  
**Goal**: Implement intelligent parallel launching
**Success Criteria**: System startup time reduced by 50%+

### Phase 5: UI Integration
**Goal**: Add real-time status indicators to Hephaestus UI
**Success Criteria**: Visual status dots show component health

## Your Task for This Session

**Primary Focus**: Complete Phase 1 by fixing all remaining import errors

### Immediate Actions Needed

1. **Add RetrospectiveAnalysis class** to `prometheus.models.retrospective`
2. **Add ChatCompletionOptions** to `tekton_llm_client.models`  
3. **Add get_tools function** to `apollo.core.mcp`
4. **Add get_apollo_manager function** to `apollo.api.dependencies`
5. **Fix MCP capability parameter** issue in Metis decorator usage
6. **Resolve Pydantic v2 root validator** warnings in Budget

### Implementation Approach

For each missing import:
1. **Investigate** what the importing code expects (class/function signature)
2. **Implement** the missing piece with a sensible interface
3. **Test** that the import resolves successfully
4. **Verify** the component now starts without errors

### Quality Requirements

All code must follow the [Debug Instrumentation Guidelines](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md):

- Use `debug_log.info("component_name", "message")` for logging
- Add `@log_function()` decorators to key methods
- Include contextual error information in exception handling

### Success Metrics for This Session

By the end of this session:
- [ ] All import errors from latest launch log are resolved
- [ ] Components start without ImportError exceptions  
- [ ] Launch script reports actual failures instead of timeouts
- [ ] At least 3 core components (Hermes, Engram, Rhetor) are fully operational

## Latest Launch Log Analysis

Reference the latest launch output which shows:
- ✅ **Hermes**: Launching and responding successfully
- ✅ **Engram**: Launching and responding successfully  
- ❌ **Rhetor**: Timeout (Pydantic field override issues)
- ❌ **All other components**: Import errors preventing startup

## Key Files and Locations

### Target Files for Import Fixes
- `Prometheus/prometheus/models/retrospective.py` - Add RetrospectiveAnalysis
- `tekton-llm-client/tekton_llm_client/models.py` - Add ChatCompletionOptions
- `Apollo/apollo/core/mcp/__init__.py` - Add get_tools
- `Apollo/apollo/api/dependencies.py` - Add get_apollo_manager  
- `Budget/budget/core/` - Fix Pydantic root validator warnings

### Reference Files
- `scripts/lib/tekton-utils.sh` - Contains tekton_error function you added
- `tekton-core/tekton/mcp/fastmcp/utils/endpoints.py` - MCP fixes you made

## Project Structure Understanding

Tekton uses:
- **Single Port Architecture**: Each component has a designated port (8000-8014)
- **MCP Integration**: Model Context Protocol for component communication
- **Hermes Service Registry**: Central component registration and discovery
- **Pydantic v2**: Data validation (migration in progress)

## Next Phase Preview

After Phase 1 completion, Phase 2 will focus on ensuring all components register with Hermes and respond to health checks properly. This will require implementing standardized health endpoints and service registration logic.

## Debug Instrumentation

Use these patterns for debug logging:

```python
# Import the debug utilities
from shared.debug.debug_utils import debug_log, log_function

# Log important events
debug_log.info("component_name", "Component started successfully")

# Decorate key methods
@log_function()
def important_function(param1, param2):
    debug_log.debug("component_name", f"Processing {param1}")
    # Function implementation
```

## Sprint Documentation

All sprint documentation is available in:
- `MetaData/DevelopmentSprints/GoodLaunch_Sprint/README.md`
- `MetaData/DevelopmentSprints/GoodLaunch_Sprint/SprintPlan.md`
- `MetaData/DevelopmentSprints/GoodLaunch_Sprint/ImplementationPlan.md`

## Ready to Begin

You have the context, tools, and specific tasks needed to complete Phase 1. Focus on resolving the import errors systematically, test each fix, and verify that components can start successfully.

The goal is to move from the current state where only 2 components work to a state where all components start without import errors, setting the foundation for the remaining phases of the sprint.