# Building New Tekton Components Documentation Update - Handoff

## Context
The "Building New Tekton Components" documentation was created in earlier sessions to guide developers in creating new Tekton components. As the codebase has evolved through the Shared Utilities Sprint, this documentation needs to be updated to reflect current best practices and patterns.

## Session Context Summary
During Session 4 of the Shared Utilities Sprint, we discovered critical launch mechanism inconsistencies:
- **Issue Found**: Components require different startup commands (e.g., `uvicorn ergon.api.app:app` vs `python -m rhetor`)
- **Root Cause**: Components were built incrementally over time with different patterns
- **Impact**: Enhanced launcher script doesn't use correct launch commands for all components
- **Affected Components**: Rhetor uses `python -m rhetor`, while Ergon uses standard uvicorn pattern
- **Completed Work**: Updated 5 components (Apollo, Athena, Budget, Engram, Ergon) to use shared utilities
- **Remaining Work**: 10 components still need updates, starting with Harmonia

## Documentation Location
- Main documentation: `/MetaData/TektonDocumentation/Building_New_Tekton_Components/`
- Key files to update:
  - `README.md` - Overview and guide structure
  - `Backend_Implementation_Guide.md` - FastAPI patterns and implementation
  - `Component_Architecture_Guide.md` - Architecture decisions and patterns
  - `Shared_Patterns_Reference.md` - Common patterns across components
  - `USAGE_GUIDE.md` - Step-by-step instructions

## Key Updates Needed

### 1. Shared Utilities Integration
The documentation should reflect the new shared utilities that all components must use:
- `shared.utils.logging_setup` - For consistent logging
- `shared.utils.env_config` - For configuration management
- `shared.utils.hermes_registration` - For service registration
- `shared.utils.startup` - For startup metrics
- `shared.utils.shutdown` - For graceful shutdown

### 2. FastAPI Lifespan Pattern
Update all examples to use the modern lifespan pattern instead of deprecated `@app.on_event`:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    yield
    # Shutdown logic
    await asyncio.sleep(0.5)  # Socket release for macOS
```

### 3. Launch Standardization (Critical Update Needed)
**Important Discovery from Session 4**: Components have inconsistent launch mechanisms that cause issues with the enhanced launcher.

Current patterns found:
- **Standard uvicorn pattern**: `uvicorn component.api.app:app --host 0.0.0.0 --port PORT`
  - Used by: Ergon, Apollo, Athena, Budget, Engram
- **Module pattern**: `python -m component`
  - Used by: Rhetor (requires `__main__.py` with uvicorn.run)
- **Custom patterns**: Some components may have other variations

Documentation must be updated to:
- Mandate a single standard launch pattern for all components
- Provide clear `__main__.py` template for module-based launches
- Document how to make components compatible with enhanced launcher
- Include migration guide for existing components

### 4. Lessons Learned
Document the common issues discovered during the sprint:
- **Port conflicts**: Hermes DB MCP server was defaulting to port 8002 (Ergon's port) instead of 8500
- **Import path issues**: Some components had hardcoded imports instead of using shared utilities
- **Launch mechanism inconsistencies**: Different components use different startup commands
- **Component-specific quirks**:
  - Hephaestus uses Python HTTP server instead of FastAPI
  - Harmonia has FastMCP integration issues (signature mismatch in register_tools)
  - Some components still use deprecated @app.on_event patterns

### 5. Updated Examples
Update all code examples to reflect:
- Current import patterns
- Proper error handling with shared utilities
- Consistent health check format
- Registration with Hermes

## Specific Files to Update

### Backend_Implementation_Guide.md
- Update FastAPI app initialization example
- Replace old startup/shutdown with lifespan
- Update import statements
- Add troubleshooting section

### Shared_Patterns_Reference.md
- Add new shared utilities section
- Update health check pattern
- Update registration pattern
- Add launch standardization (after Session 7)

### USAGE_GUIDE.md
- Update step-by-step with new patterns
- Add common pitfalls section
- Update testing instructions
- Add debugging tips

## Critical Bugs Found and Fixed
Document these bugs that were discovered during the sprint:
1. **Hermes Port Conflict** (Fixed in Session 4)
   - File: `/Hermes/hermes/api/app.py` line 139
   - Bug: DB MCP server defaulting to "8002" instead of "8500"
   - Impact: Caused Rhetor and Ergon to fail after Hermes update
   - Fix: Changed default port to correct value

2. **Harmonia FastMCP Issue** (Workaround applied)
   - File: `/Harmonia/harmonia/api/fastmcp_endpoints.py`
   - Bug: register_tools() signature mismatch
   - Workaround: Temporarily disabled FastMCP with TODO comments

## Retrospective Items to Include
1. **What Worked Well**
   - Shared utilities eliminated duplicate code
   - Lifespan pattern is cleaner than events
   - Consistent logging improves debugging
   - Systematic approach to updating components

2. **Challenges**
   - Launch mechanism varies by component age
   - Some components have unique requirements
   - Port management needs clear documentation
   - FastMCP integration varies across components

3. **Best Practices Discovered**
   - Always use env_config for ports
   - Include socket release delay for macOS
   - Test registration before declaring success
   - Use consistent health check format
   - Test each component after updates before moving to next

## Documentation Update Process
1. Review current documentation
2. Identify outdated patterns
3. Update code examples
4. Add new sections for shared utilities
5. Include troubleshooting guide
6. Add migration guide for existing components

## Priority Order
1. **High Priority** - Update code examples to prevent new components using old patterns
2. **Medium Priority** - Add troubleshooting and common issues
3. **Low Priority** - Retrospective and lessons learned (can be added incrementally)

## Success Criteria
- [ ] All code examples use shared utilities
- [ ] No deprecated patterns in documentation
- [ ] Clear guidance on component creation
- [ ] Troubleshooting section covers known issues
- [ ] Migration guide for updating old components

## Notes for Implementation
- Keep examples minimal but complete
- Test all code snippets
- Include both "correct" and "incorrect" examples
- Reference completed components as examples
- Consider creating a component template/cookiecutter

## Important Note on Timing
This documentation update should be done after the Shared Utilities Sprint is complete (including launch standardization) to ensure all patterns are finalized. However, the **launch mechanism standardization** section is CRITICAL and should be prioritized as it's causing active issues with the enhanced launcher script.

## Summary of Key Discoveries from Session 4
1. Launch mechanism inconsistency is a critical issue affecting component management
2. Port conflicts can cause cascading failures (Hermes DB MCP bug affected multiple components)
3. FastMCP integration needs careful attention during updates
4. Testing after each component update is essential to catch regressions early
5. The enhanced launcher needs to be updated to handle different launch patterns