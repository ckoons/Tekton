# Tekton Component Launch Issues

This document details issues discovered during the Launch Testing Sprint and serves as input for the upcoming FastMCP Development Sprint.

## Core Components

### Hermes

| Issue | Description | Resolution | Status |
|-------|-------------|------------|--------|
| Missing async methods | The `MessageBus` class lacked async versions of `create_channel`, `subscribe`, and `publish` methods | Implemented missing methods with proper async/await syntax | ✅ Fixed |
| Health endpoint error | Missing `time` import in app.py causing 500 error | Added import statement | ✅ Fixed |
| Database MCP missing | The database MCP server script was referenced but missing | Created stub implementation at `/scripts/run_database_mcp.py` | ⚠️ Temporary |
| Process detection | Status script couldn't detect Hermes process | Updated pattern matching in `tekton-status` | ✅ Fixed |
| Coroutine warnings | `MessageBus.subscribe` calls not awaited | Added proper error handling around async method calls | ✅ Fixed |

**Notes for FastMCP Sprint**:
1. The temporary database MCP script is a minimal implementation that should be replaced with a proper MCP service
2. Consider adding proper async wrappers for synchronous code sections
3. Ensure registration manager properly handles both sync and async subscription patterns

### Engram

| Issue | Description | Resolution | Status |
|-------|-------------|------------|--------|
| Memory service error | Error in health check: `'MemoryService' object has no attribute 'get_storage_info'` | Non-critical error, service still functions | ⚠️ Minor |
| Fallback mode dependency | Requires environment variable `ENGRAM_USE_FALLBACK=1` | Correctly set in launch script | ✅ Working |

**Notes for FastMCP Sprint**:
1. Consider implementing the missing `get_storage_info` method in the `MemoryService` class
2. Review Engram's connection to vector database systems
3. Formalize the fallback mode configuration in documentation

### Rhetor

| Issue | Description | Resolution | Status |
|-------|-------------|------------|--------|
| Component directory undefined | Error: `name 'component_dir' is not defined` during launch | Under investigation | 🔄 In Progress |
| Port mismatch | Script uses port 8003, but service runs on 8300 | Need standardization | 🔄 Pending |
| Connection to Engram failed | Warning about inability to connect to Engram | Expected behavior when launched before Engram | ✅ Normal |

**Notes for FastMCP Sprint**:
1. Standardize port configuration and ensure all components use the proper port from `tekton-ports.sh`
2. Review launch order dependencies between components
3. Consider enhancing the `launch_component` function to better handle errors

## Launch Script Issues

### tekton-launch

| Issue | Description | Resolution | Status |
|-------|-------------|------------|--------|
| Bash compatibility | `${component,,}` syntax for lowercase requires bash 4+ | Replaced with `$(echo "$component" \| tr '[:upper:]' '[:lower:]')` | ✅ Fixed |
| Component detection | Inconsistent patterns for detecting running processes | Enhanced detection patterns in status script | ✅ Fixed |
| Error handling | Launch failures didn't provide clear error messages | Improved error capture and display | 🔄 In Progress |

### tekton-kill

| Issue | Description | Resolution | Status |
|-------|-------------|------------|--------|
| Claude process termination | Script would kill Claude Code sessions | Added exclusion pattern and filtered PIDs | ✅ Fixed |
| Port release | Not all ports properly released | Enhanced port management | ✅ Fixed |

### tekton-status

| Issue | Description | Resolution | Status |
|-------|-------------|------------|--------|
| Process detection | Couldn't detect certain process patterns | Added additional detection patterns | ✅ Fixed |
| Hermes service reporting | Reported Hermes as not running when it was | Updated detection logic | ✅ Fixed |

## Recommendations for FastMCP Sprint

1. **Standardize Component Launch Process**:
   - Create a consistent pattern for component startup
   - Implement proper dependency management between components
   - Standardize port usage across all components

2. **Enhance Error Handling**:
   - Improve error reporting and recovery
   - Add comprehensive logging for troubleshooting
   - Create self-healing mechanisms where possible

3. **Refine Message Bus Architecture**:
   - Implement proper async patterns throughout
   - Standardize channel naming and subscription models
   - Enhance event propagation between components

4. **Improve Service Discovery**:
   - Strengthen the registration/discovery process
   - Implement proper heartbeat and health checking
   - Add automatic reconnection capabilities

5. **Documentation and Testing**:
   - Update component documentation with launch requirements
   - Create automated launch tests
   - Document common failure scenarios and resolutions

## Component Launch Order Dependencies

Based on testing, the recommended component launch order is:

1. Hermes (core service registration and messaging)
2. Engram (memory services)
3. Rhetor (LLM management)
4. Mid-level components (Ergon, Prometheus, Harmonia)
5. Higher-level components (Athena, Sophia, Telos, Synthesis, Terma)
6. UI components (Hephaestus)

This order reflects dependency relationships and ensures services are available when needed by higher-level components.