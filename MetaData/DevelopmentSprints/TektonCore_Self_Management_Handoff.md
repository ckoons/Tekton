# TektonCore Self-Management Handoff

## Current Issue
**PROBLEM**: Tekton should automatically appear in the dashboard at startup but doesn't.

**SYMPTOM**: 
- Projects.json exists but is empty: `{"projects": []}`
- No "Tekton" project in dashboard despite startup code
- New projects save but don't appear in dashboard

## Root Cause
**BAD ARCHITECTURE**: Multiple ProjectManager instances with complex inheritance/sharing patterns.

Current broken state:
- `app.py` has `project_manager` (V1) and `project_manager_v2` (V2) 
- `projects.py` has its own `ProjectManager` instance
- Startup calls one instance, API calls another
- Different storage paths, different behaviors

## The Clean Solution
**ONE PROJECTMANAGER CLASS, ONE INSTANCE, SIMPLE STARTUP**

### Step 1: Consolidate ProjectManager
- Keep only `project_manager_v2.py` (has GitHub CLI integration)
- Delete or deprecate `project_manager.py` (legacy)
- One class, one instance, one projects.json file

### Step 2: Fix Startup Flow
```python
# In app.py startup_callback():
await project_manager._ensure_tekton_self_check()
```

This should:
1. Check if "Tekton" project exists in projects.json
2. If not, create it with TEKTON_ROOT path and git remotes
3. Save to projects.json

### Step 3: Use Same Instance Everywhere
- `app.py` creates ONE instance
- `projects.py` imports/uses that same instance
- No V1/V2 confusion

## Key Files to Fix

### `/tekton-core/tekton/api/app.py`
- Line 54-55: Create ONE ProjectManager instance
- Line 68-69: Call `_ensure_tekton_self_check()` at startup
- Remove V1/V2 confusion

### `/tekton-core/tekton/api/projects.py`
- Line 54-55: Use shared instance from app.py
- Remove duplicate ProjectManager creation

### `/tekton-core/tekton/core/project_manager_v2.py`
- Lines 577-582: `_check_tekton_self_management()` method
- This should create "Tekton" project if it doesn't exist
- Uses `$TEKTON_ROOT` path and git remotes

## Current Working Features (Don't Break)
✅ **GitHub CLI Integration**: `gh repo fork`, `gh repo clone` working
✅ **Comprehensive Logging**: All git commands logged to .tekton/logs/tekton_core.log
✅ **UI Improvements**: Field clearing, button protection, proper error handling
✅ **Project Creation**: API endpoint works, saves to projects.json

## Test Plan
1. Restart TektonCore
2. Check dashboard - should show "Tekton" project automatically
3. Create new project - should appear in dashboard
4. Both should persist in same projects.json file

## Storage Location
- Projects saved to: `$TEKTON_ROOT/.tekton/projects/projects.json`
- Dashboard reads from: Same file
- Must be consistent!

## Success Criteria
1. **Startup**: "Tekton" project appears in dashboard automatically
2. **Creation**: New projects appear in dashboard after creation
3. **Persistence**: Both use same projects.json file
4. **Simplicity**: One ProjectManager class, one instance, clean code

## Context Notes
- Casey wants SIMPLE code, not complex patterns
- GitHub CLI (`gh`) integration is working correctly
- UI field clearing and button protection implemented
- Comprehensive git logging in place
- Focus on fixing the core startup issue, not rewriting everything