# Claude Code Prompt - Shared Utilities Sprint

## Context

You are working on the Tekton project, an intelligent orchestration system for AI models. The previous session completed the CleanRequirements Sprint which created shared requirements and eliminated 60-70% dependency duplication.

**Key People:**
- Casey - The architect (50+ years experience) who designed Tekton and approves all changes
- You - Claude Code, helping implement Casey's vision methodically

**Working Style:**
- Create TodoWrite lists to track progress
- **CRITICAL**: Discuss ALL changes with Casey BEFORE implementing
- **CRITICAL**: Get Casey's explicit approval before making ANY changes
- Present proposed changes and wait for approval
- Test each change: launch component → check logs → verify functionality
- Ask Casey before making architectural decisions
- No git commands (Casey handles commits)
- Prefer simple, practical solutions over clever engineering
- Be methodical: investigate → propose → discuss → implement (only after approval)

## Current System State

1. **All 15 components** use shared requirements from `/shared/requirements/`
2. **LLMAdapter removed** - everything uses Rhetor (port 8003) + tekton-llm-client
3. **Standard tools**: `tekton-launch`, `tekton-status`, `tekton-kill`
4. **Package manager**: `uv` for all installations
5. **15/16 components** running successfully (Terma excluded)

## Sprint Objectives

You're implementing the **Shared_Utilities_Sprint** to reduce code duplication and fix real issues found across components. These are all based on actual problems, not theoretical improvements.

### 1. Fix Phantom Imports
**Problem**: Many components import `from tekton.utils.port_config import get_component_port` but this module doesn't exist.
**Solution**: Create `/shared/utils/port_config.py` with the actual implementation.

### 2. Standardize Logging Setup
**Problem**: Every component has duplicate logging configuration code.
**Solution**: Extract into `/shared/utils/logging_setup.py` for reuse.

### 3. Fix Health Check Adoption
**Problem**: `/shared/utils/health_check.py` exists but components aren't using it.
**Solution**: Update components to actually use the shared health check utility.

### 4. Create Server Startup Utilities
**Problem**: Socket binding issues and duplicate uvicorn.run() code everywhere.
**Solution**: 
- Create `/shared/utils/server_startup.py` with socket release fix
- Extract shutdown handler pattern into `/shared/utils/shutdown_handler.py`

### 5. Add Environment Configuration Loader
**Problem**: Inconsistent environment variable loading across components.
**Solution**: Create `/shared/utils/env_config.py` for consistent patterns.

### 6. Create FastMCP Helper Utilities
**Problem**: MCP tool creation is verbose and inconsistent.
**Solution**: Create helpers to simplify MCP tool definitions.

### 7. Develop Component Templates
**Problem**: No standard pattern for new components.
**Solution**: Create template files showing best practices.

## Getting Started

1. **Read existing documentation:**
   ```
   /MetaData/DevelopmentSprints/StreamlineImprovements_Sprint/Shared_Utilities_Sprint/README.md
   /MetaData/DevelopmentSprints/MasterBacklog.md (lines 29-50 for updated objectives)
   ```

2. **Create initial todo list** with TodoWrite for all objectives

3. **INVESTIGATE FIRST** - Start with phantom imports:
   - Search for imports of `tekton.utils.port_config`
   - Check what functions are expected
   - **PROPOSE** the module structure to Casey
   - **WAIT** for Casey's approval
   - **ONLY THEN** create the missing module

4. **For EACH utility:**
   - INVESTIGATE the problem
   - PROPOSE the solution with code examples
   - DISCUSS with Casey
   - WAIT for explicit approval
   - IMPLEMENT only after approval
   - TEST by updating 1-2 components
   - REPORT results to Casey

5. **Document patterns** in each utility file

## Example Investigation Commands

```python
# Find phantom imports
grep -r "from tekton.utils" --include="*.py" .

# Find duplicate logging setup
grep -r "logging.basicConfig" --include="*.py" .

# Check existing shared utils
ls -la /shared/utils/

# Find uvicorn.run patterns
grep -r "uvicorn.run" --include="*.py" .
```

## Success Criteria

- Phantom imports resolved - components can import without errors
- Code duplication reduced - shared patterns extracted
- Components updated - at least 2-3 components using each utility
- Tests pass - all components still launch successfully
- Documentation clear - each utility has usage examples

## Important Notes

1. These are **real problems** Casey identified, not theoretical improvements
2. Focus on **extraction** of existing patterns, not creating new complexity
3. **Test incrementally** - update a few components at a time
4. **Ask Casey** if you're unsure about API design
5. Remember: **simple and working** beats elegant and complex

## CRITICAL REMINDER

**DO NOT MAKE CHANGES WITHOUT APPROVAL**

The correct workflow is:
1. 🔍 **INVESTIGATE** - Understand the problem
2. 💡 **PROPOSE** - Show Casey what you plan to do
3. 💬 **DISCUSS** - Answer Casey's questions, refine approach
4. ✅ **APPROVAL** - Wait for Casey's explicit "go ahead" or "yes, do that"
5. 🔨 **IMPLEMENT** - Only now make the actual changes
6. 🧪 **TEST** - Verify it works
7. 📊 **REPORT** - Show Casey the results

Casey values methodical, thoughtful work. He'd rather discuss 5 different approaches than have you implement the wrong one. When in doubt, ask!

## Handoff from Previous Session

See `/MetaData/DevelopmentSprints/CleanRequirements_Sprint/Phase2_Complete_Handoff.md` for:
- What was accomplished in the previous sprint
- System architecture decisions
- Testing methodology
- Casey's preferences

Start by creating your todo list and investigating the phantom imports!