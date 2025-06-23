# Tekton Debug System

The Tekton Debug System provides a comprehensive, zero-overhead debugging infrastructure for both frontend and backend components in the Tekton ecosystem.

## Key Features

- **Zero Overhead**: No performance impact when disabled
- **Cross-Component**: Works across JavaScript and Python components
- **Controllable**: Configurable via environment variables
- **Component-Specific**: Set different log levels for different components
- **Context-Rich**: Include relevant data with log messages
- **Performance Tracking**: Measure and monitor execution time

## Documentation

- [Quick Start Guide](./QuickStartGuide.md) - Get started in minutes
- [Component Instrumentation Guide](./ComponentInstrumentation.md) - Detailed implementation instructions
- [DebuggingInstrumentation.md](./DebuggingInstrumentation.md) - Technical design and architecture

## Debug Components

- **Frontend (JavaScript)**: [/Hephaestus/ui/scripts/debug-shim.js](../../../../Hephaestus/ui/scripts/debug-shim.js)
- **Backend (Python)**: [/shared/debug/debug_utils.py](../../../../shared/debug/debug_utils.py)

## Implementation Status

The Debug System has been implemented in the following components:

- ✅ Ergon Component
- ✅ Athena Component
- ❌ Rhetor Component (to be implemented)
- ❌ Terma Component (to be implemented)
- ❌ Hermes Component (to be implemented)
- ❌ Engram Component (to be implemented)

## Usage Example

### JavaScript

```javascript
// Check if debug system is available
if (window.TektonDebug) {
    // Log at different levels
    TektonDebug.trace('myComponent', 'Detailed tracing', {data: someData});
    TektonDebug.debug('myComponent', 'Debug information');
    TektonDebug.info('myComponent', 'Component initialized');
    TektonDebug.warn('myComponent', 'Potential issue detected');
    TektonDebug.error('myComponent', 'Operation failed', {error: errorObj});
    TektonDebug.fatal('myComponent', 'Critical system failure');
}
```

### Python

```python
from tekton.shared.debug.debug_utils import debug, info, warn, error, trace_function

# Basic logging
debug("component_name", "Detailed message", extra={"key": "value"})
info("component_name", "Information message")
warn("component_name", "Warning message")
error("component_name", "Error message")

# Function tracing
@trace_function("component_name")
def my_function():
    # Implementation
    return result

# Performance tracking
@track_performance("component_name")
def intensive_operation():
    # Implementation
    return result
```

## Configuration

### JavaScript (Frontend)

The debug system can be controlled through environment variables in [env.js](../../../../Hephaestus/ui/scripts/env.js):

```javascript
// Master switch for debug instrumentation
window.TEKTON_DEBUG = 'true';

// Default log level (TRACE, DEBUG, INFO, WARN, ERROR, FATAL, OFF)
window.TEKTON_LOG_LEVEL = 'DEBUG';
```

### Python (Backend)

Configure through environment variables:

```bash
# Master switch for debug instrumentation
export TEKTON_DEBUG=true

# Default log level (TRACE, DEBUG, INFO, WARN, ERROR, FATAL)
export TEKTON_LOG_LEVEL=DEBUG

# Component-specific configuration
export TEKTON_DEBUG_COMPONENTS='{"component_name":"DEBUG","another_component":"INFO"}'
```

## Contributing

When adding debug instrumentation to components:

1. Follow the patterns in the [Component Instrumentation Guide](./ComponentInstrumentation.md)
2. Update this README to mark your component as implemented
3. Test with debug both enabled and disabled
4. Ensure appropriate log levels for different types of messages

## Future Enhancements

Planned features for the Debug System:

1. **Visual Debug Console**: In-browser debug console for viewing logs
2. **Remote Debugging**: Send logs to a central debugging service
3. **Log Storage**: Persistent storage of debug logs for post-mortem analysis
4. **Debug Profiles**: Presets for different debugging scenarios
5. **Automated Testing Integration**: Special debugging hooks for automated tests