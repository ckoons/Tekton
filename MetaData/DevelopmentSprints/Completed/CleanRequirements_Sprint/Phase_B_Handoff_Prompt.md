# CleanRequirements Sprint Phase 2 - Phase B Handoff

## Context for New Claude Session

You're picking up work on the CleanRequirements Sprint Phase 2. Phase A is complete, and now we're starting Phase B.

### What Was Completed in Phase A
1. **Created Shared Requirements Structure** in `/shared/requirements/`:
   - base.txt, web.txt, ai.txt, vector.txt, database.txt, data.txt, utilities.txt, dev.txt
   - All files tested and resolve correctly
   - Created utilities: find-test-new-versions.py, verify-dependencies.py, setup-venvs.py

2. **Fixed Rhetor Process Management**:
   - Rhetor was resisting termination due to outdated signal handling
   - Created run_rhetor_fixed.sh with proper cross-platform signal handling
   - Ready for future child CI process management

3. **Documentation Cleanup**:
   - Moved 26 misplaced documentation files to MetaData
   - Remember: Documentation goes in MetaData/ComponentDocumentation/[Component]/ or MetaData/TektonDocumentation/

### Current State
- All 15/16 components launch successfully (only Terma fails, which is expected)
- 30 version conflicts identified across components (will be resolved by shared requirements)
- System is stable and ready for Phase B

### Phase B: Update Core Components

You need to update the core components that other components depend on:

1. **Update Hermes** (port 8001)
   - Central message bus - all components register with it
   - Update requirements.txt to use shared requirements
   - Test that it still starts and accepts registrations

2. **Update tekton-core**
   - Core utilities used by many components
   - Update requirements.txt to use shared requirements
   - Ensure nothing breaks

3. **Update tekton-llm-client**
   - LLM client library replacing LLMAdapter
   - Update requirements.txt to use shared requirements

4. **Verify LLMAdapter deprecation**
   - Check if tekton-llm-client fully replaces LLMAdapter functionality
   - Look for any components still importing from LLMAdapter

5. **Remove LLMAdapter** (with Casey's approval)
   - Only after verification
   - Casey will commit before removal

6. **Test everything**
   - Run `tekton-launch --launch-all`
   - Run `tekton-status` to verify health
   - Check that all components still register with Hermes

### How to Update Component Requirements

Replace the component's requirements.txt with:
```txt
# Include shared requirements
-r ../../shared/requirements/web.txt
-r ../../shared/requirements/ai.txt  # if needed

# Tekton components
tekton-core>=0.1.0
fastmcp>=1.0.0  # if using MCP

# Component-specific dependencies only
# (any unique packages not in shared files)
```

### Important Guidelines
1. **No pip, use uv**: All installations use `uv pip install`
2. **Casey does Git**: Don't use any git commands, only Casey commits
3. **Test after each component**: Update one, test it works, then continue
4. **Documentation in MetaData**: Any new docs go in MetaData structure
5. **Ask before major changes**: Especially before removing components

### Working with Casey
- Casey has 50+ years of software engineering experience
- He's teaching CI assistants proper software engineering
- Be clear about what you're doing and why
- Create TODO lists for planning
- Ask questions when uncertain
- Casey uses fruit fly memory joke but actually remembers everything

### Files to Reference
- `/MetaData/DevelopmentSprints/CleanRequirements_Sprint/README.md` - Sprint overview
- `/MetaData/DevelopmentSprints/CleanRequirements_Sprint/Phase2_Handoff_PhaseA_Complete.md` - What was done
- `/shared/requirements/README.md` - How to use shared requirements
- `/shared/requirements/verify-dependencies.py` - Test dependency resolution

Good luck with Phase B! Focus on updating the core components first, as everything else depends on them.