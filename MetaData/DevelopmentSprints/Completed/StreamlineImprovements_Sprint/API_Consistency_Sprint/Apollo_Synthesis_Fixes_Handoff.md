# Apollo and Synthesis Fixes - Handoff Document

## Context
This document captures the remaining issues found after completing the API Consistency Sprint. All 13 components have been updated to the new API standards, but Apollo and Synthesis have runtime issues.

## Issues Found

### 1. Apollo Issues

#### A. Won't Start Without Environment Variable
**Problem**: Apollo's `__main__.py` calls `int(os.environ.get("APOLLO_PORT"))` which fails with TypeError when APOLLO_PORT is not set.

**Root Cause**: The `tekton_component_startup("apollo")` is called but the environment isn't loaded before trying to access APOLLO_PORT.

**Status**: FIXED - Added proper error handling to check if APOLLO_PORT exists before converting to int.

#### B. Startup/Shutdown Method Errors
**Problem**: Apollo was calling non-existent `start()` and `stop()` methods on `protocol_enforcer` and `token_budget_manager`.

**Status**: FIXED - Removed calls to `apollo_manager.start()` and `apollo_manager.stop()`, only calling start/stop on components that have these methods.

#### C. Variable Name Error
**Problem**: Line 124 used undefined variable `is_registered` instead of `is_registered_with_hermes`.

**Status**: FIXED

#### D. No Log Output
**Problem**: Apollo runs successfully but doesn't write to `~/.tekton/logs/apollo.log`. The log file hasn't been updated since May 25th.

**Root Cause**: The enhanced_tekton_launcher.py captures stdout/stderr with `subprocess.PIPE` but never writes it anywhere:
```python
process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,  # Captures output but doesn't write it
    stderr=subprocess.PIPE,
    ...
)
```

**Status**: NOT FIXED - Requires updating the launcher

### 2. Synthesis Issues

#### A. Health Endpoint Returns 404
**Problem**: `curl http://localhost:8009/health` returns 404 Not Found, causing tekton-status to show "unhealthy".

**Root Cause**: In `synthesis/api/app.py`, `mount_standard_routers(app, routers)` was called on line 362 BEFORE the health endpoint was defined on line 379. This means the health endpoint never got registered with the app.

**Status**: FIXED - Moved `mount_standard_routers()` to line 928, after all endpoint definitions.

### 3. Launcher Issues

#### A. No Log File Output
**Problem**: The enhanced_tekton_launcher.py captures all stdout/stderr but doesn't write it to log files.

**Location**: `/Users/cskoons/projects/github/Tekton/scripts/enhanced_tekton_launcher.py` lines 376-386

**Fix Needed**: Either:
1. Remove `stdout=subprocess.PIPE` and `stderr=subprocess.PIPE` to let output go to console
2. Or redirect to log files: `stdout=open(log_file, 'a')` 
3. Or create a thread to read from pipes and write to log files

## Remaining Tasks

### 1. Fix Launcher Logging
Update `enhanced_tekton_launcher.py` to write component output to log files. Suggested approach:

```python
# In launch_component_process() around line 370
log_dir = os.path.expanduser("~/.tekton/logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"{component_name}.log")

with open(log_file, 'a') as log:
    process = subprocess.Popen(
        cmd,
        cwd=component_dir,
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,  # Combine stderr with stdout
        preexec_fn=os.setsid if platform.system() != "Windows" else None
    )
```

### 2. Test Synthesis Health Endpoint
After restarting Synthesis, verify the health endpoint works:
```bash
tekton-kill synthesis
tekton-launch synthesis
curl http://localhost:8009/health
```

### 3. Update tekton-status (Optional Enhancement)
The current tekton-status could be enhanced to use the new standardized endpoints:
- Use `/ready` endpoint for better readiness information
- Use `/api/v1/discovery` to show component capabilities
- Show more details from the health check response

## Testing Checklist

1. [ ] Restart Synthesis and verify health endpoint works
2. [ ] Fix launcher logging and verify Apollo writes to log file
3. [ ] Run `tekton-status` and verify all components show as healthy
4. [ ] Test Apollo with `APOLLO_PORT=8012 python -m apollo` to ensure it starts correctly
5. [ ] Run full `tekton-launch all` and verify all components start successfully

## Files Modified

1. `/Users/cskoons/projects/github/Tekton/Apollo/apollo/api/app.py` - Fixed startup/shutdown and variable name
2. `/Users/cskoons/projects/github/Tekton/Apollo/apollo/__main__.py` - Added environment loading and error handling
3. `/Users/cskoons/projects/github/Tekton/Apollo/run_apollo.sh` - Removed hardcoded port default
4. `/Users/cskoons/projects/github/Tekton/Synthesis/synthesis/api/app.py` - Moved router mounting to end

## Notes

- All components are now using version "0.1.0" as required
- All have the standard endpoints: `/health`, `/ready`, `/api/v1/discovery`
- Business logic is under `/api/v1/` prefix
- MCP endpoints remain at `/api/mcp/v2/`
- The API Consistency Sprint is complete except for these runtime issues