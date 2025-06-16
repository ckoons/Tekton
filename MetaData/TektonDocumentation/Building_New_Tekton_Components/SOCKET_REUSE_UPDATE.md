# Socket Reuse Update Documentation

## Update Date: January 6, 2025 (Completed June 3, 2025)

## Summary

Successfully implemented complete socket reuse solution across all Tekton components. This change enables immediate port rebinding after shutdown, eliminating the 60-120 second TIME_WAIT delay on macOS.

**See [SOCKET_REUSE_COMPLETE.md](./SOCKET_REUSE_COMPLETE.md) for the full implementation details and results.**

## Key Changes

### 1. Backend Implementation Guide
- Added new "Socket Reuse Requirements" section explaining why it's mandatory
- Updated `__main__.py` example to use `run_component_server()`
- Updated `app.py` if __name__ section to use `run_with_socket_reuse()`
- Removed all hardcoded port fallbacks (no more `port=8015` defaults)
- Updated warning from "DON'T use socket_server wrapper" to "DON'T use plain uvicorn.run()"

### 2. Step By Step Tutorial
- Updated Nexus example `__main__.py` to use `run_component_server()`
- Updated Nexus `app.py` main section to use `run_with_socket_reuse()`
- Removed all hardcoded port defaults (8016)
- Updated all references to use environment variables without fallbacks
- Updated curl examples to use `$NEXUS_PORT` instead of hardcoded 8016

### 3. README.md
- Added requirement: "Use `socket_server` utilities for port reuse (no plain `uvicorn.run()`)"

## Implementation Pattern

### For `__main__.py`:
```python
from shared.utils.socket_server import run_component_server

if __name__ == "__main__":
    # Get port from environment variable - NO HARDCODED DEFAULTS!
    default_port = int(os.environ.get("MYCOMPONENT_PORT"))
    
    run_component_server(
        component_name="mycomponent",
        app_module="mycomponent.api.app",
        default_port=default_port,
        reload=True
    )
```

### For `app.py` (if __name__ == "__main__"):
```python
from shared.utils.socket_server import run_with_socket_reuse

if __name__ == "__main__":
    # Get port from environment - NEVER hardcode
    port = int(os.environ.get("MYCOMPONENT_PORT"))
    
    # Use socket reuse for quick port release
    run_with_socket_reuse(
        "mycomponent.api.app:app",
        host="0.0.0.0",
        port=port,
        timeout_graceful_shutdown=3,
        server_header=False,
        access_log=False
    )
```

## Benefits

1. **Immediate Port Reuse**: Components can restart immediately without waiting
2. **No More "Address already in use" Errors**: `SO_REUSEADDR` prevents binding issues
3. **Fast Graceful Shutdown**: 3-second timeout ensures quick cleanup
4. **Consistent Behavior**: All components use the same pattern

## Migration Notes

For existing components:
1. Replace `uvicorn.run()` with socket reuse utilities
2. Remove all hardcoded port fallbacks
3. Ensure ports come from environment variables only
4. Test rapid restart capability

## Related Files

- `/shared/utils/socket_server.py` - Socket reuse implementation
- All component `__main__.py` files - Updated to use `run_component_server()`
- All component `app.py` files - Updated to use `run_with_socket_reuse()`

## Implementation Completion (June 3, 2025)

### Final Implementation Details
1. **Fixed SO_LINGER**: Corrected format to `struct.pack('ii', 1, 0)` for immediate close
2. **Enhanced Launcher**: Modified to detect only LISTEN state processes, not TIME_WAIT
3. **Disabled Reload**: Changed all `reload=True` to `reload=False` to prevent reloader conflicts
4. **Special Fixes**: 
   - Harmonia: Fixed async/await mismatch
   - Hermes: Removed dynamic reload based on DEBUG

### Results Achieved
- ✅ **0 second port reuse time** (immediate restart capability)
- ✅ **15/16 components** work perfectly (only Terma has unrelated issues)
- ✅ **Full system restart** in under 40 seconds
- ✅ **No more port binding errors** during rapid development

See [SOCKET_REUSE_COMPLETE.md](./SOCKET_REUSE_COMPLETE.md) for the complete technical documentation.