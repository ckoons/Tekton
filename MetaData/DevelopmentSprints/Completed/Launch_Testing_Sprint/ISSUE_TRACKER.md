# Tekton Launch Testing & Port Standardization - Issue Tracker

This document tracks the issues found during the Launch Testing Sprint and their current status, including port standardization efforts.

## High Priority Issues

| Issue | Component | Status | Notes | Next Action |
|-------|-----------|--------|-------|------------|
| Component directory variable not passed | tekton-process.sh | ✅ Fixed | Error: `name 'component_dir' is not defined` | Created separate `component_launcher.py` script |
| Missing method in PromptTemplateRegistry | Rhetor | ✅ Fixed | Error: `'PromptTemplateRegistry' object has no attribute 'load_from_directory'` | Created monkey patch in `registry_fix.py` |
| Port mismatch (8003 vs 8300) | Rhetor | ✅ Fixed | Script uses 8003, but service runs on 8300 | Implemented port standardization |
| Hard-coded URLs in components | Multiple | 🟡 In Progress | Components use hard-coded URLs to reach others | Implementing standardized port configuration |

## Medium Priority Issues

| Issue | Component | Status | Notes | Next Action |
|-------|-----------|--------|-------|------------|
| Database MCP stub implementation | Hermes | 🟡 Temporary Fix | Created stub script that will need replacement | Full implementation in FastMCP sprint |
| Multiple coroutine warnings | Hermes | ✅ Fixed | `coroutine 'MessageBus.subscribe' was never awaited` | Added proper async implementations |
| Health check method missing | Engram | 🟡 Needs Improvement | `'MemoryService' object has no attribute 'get_storage_info'` | Implement missing method |
| Legacy WebSocket port usage | Terma | 🟡 In Progress | Uses separate port (8767) for WebSocket | Needs path-based routing (/ws) |

## Fixed Issues

| Issue | Component | Resolution | Notes |
|-------|-----------|------------|-------|
| Missing async methods | Hermes | ✅ Implemented | Added async versions of `create_channel`, `subscribe`, and `publish` |
| Claude process termination | tekton-kill | ✅ Fixed | Added exclusion pattern for Claude/Anthropic processes |
| Bash compatibility issues | tekton-process.sh | ✅ Fixed | Replaced Bash 4.x features with POSIX-compatible alternatives |
| Process detection patterns | tekton-status | ✅ Fixed | Enhanced patterns to detect all component variants |
| Missing time import | Hermes | ✅ Fixed | Added import statement to fix health endpoint |
| Port standardization - Rhetor | Rhetor | ✅ Fixed | Created standardized port utilities, now uses port 8003 correctly |
| Port standardization - Terma | Terma | ✅ Fixed | Created standardized port utilities, now uses port 8004 correctly |
| Port standardization - Engram | Engram | ✅ Fixed | Created standardized port utilities, now uses port 8000 correctly |
| Port standardization - Hermes | Hermes | ✅ Fixed | Created standardized port utilities, now uses port 8001 correctly |
| Port standardization - Prometheus | Prometheus | ✅ Fixed | Created standardized port utilities, will use port 8006 when fully implemented |

## Implemented Solutions

### 1. Component Directory Variable Fix

The issue occurred in the `tekton_start_component_server` function in `/scripts/lib/tekton-process.sh` where variables weren't correctly being passed to Python code.

Implementation:
- Created a standalone Python script `component_launcher.py` that properly handles directory paths
- Placed it in `/Users/cskoons/projects/github/Tekton/scripts/lib/` directory
- Modified shell scripts to use the launcher with proper argument passing
- Ensured script is executable with proper error handling

### 2. Rhetor PromptTemplateRegistry Fix

Fixed the issue where Rhetor was failing with: `'PromptTemplateRegistry' object has no attribute 'load_from_directory'`

Implementation:
- Created a monkey patch in `registry_fix.py` to add the missing method
- Added implementation that loads templates from a directory
- Integrated the fix into Rhetor's startup process

### 3. Port Standardization

Implemented the Single Port Architecture pattern across multiple components:

| Component  | Standard Port | Implementation |
|------------|--------------|----------------|
| Rhetor     | 8003 | Created `port_config.py` utility with standardized helpers |
| Terma      | 8004 | Created `port_config.py` utility with WebSocket port handling |
| Engram     | 8000 | Created `port_config.py` utility for standardized configuration |
| Hermes     | 8001 | Created `port_config.py` utility and updated registration URLs |
| Prometheus | 8006 | Created `port_config.py` utility for future implementation |

Implementation details:
- Created a standardized `port_config.py` utility module for each component
- Implemented helper functions like `get_component_port()`, `get_api_url()`, etc.
- Updated server initialization to use the standardized port configuration
- Ensured components use consistent environment variable naming
- Fixed URL construction for component-to-component communication

## Next Steps

1. **Complete Port Standardization for Remaining Components**:
   - Harmonia (8007)
   - Telos (8008)
   - Synthesis (8009)
   - Tekton Core (8010)

2. **Review and Standardize Launch Scripts**:
   - Ensure all launch scripts use the standardized ports
   - Implement port conflict detection and reporting
   - Add validation to ensure port consistency

3. **Consolidate Port Configuration Utilities**:
   - Extract common port configuration code into a shared library
   - Implement import from shared library in all components

4. **Test Full Component Stack**:
   - Test launching all components together
   - Verify proper communication between components
   - Document any remaining issues