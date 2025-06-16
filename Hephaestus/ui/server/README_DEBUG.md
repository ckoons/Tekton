# Tekton Python Debug Instrumentation

This document describes how to use the Python debugging instrumentation in Tekton backend services.

## Overview

Tekton provides a lightweight, zero-overhead debugging system that can be used to instrument Python code with debug logging that:

1. Has virtually no impact when disabled
2. Provides rich context when enabled
3. Can evolve over time without requiring code changes

## Basic Usage

```python
from debug_utils import debug_log

# Simple logging at different levels
debug_log.debug("component_name", "This is a debug message")
debug_log.info("component_name", "This is an info message")
debug_log.warn("component_name", "This is a warning")
debug_log.error("component_name", "This is an error")
debug_log.fatal("component_name", "This is a fatal error")

# Logging with contextual data
debug_log.info("component_name", "Operation completed", {
    "items_processed": 42,
    "duration_ms": 123.45,
    "status": "success"
})

# Logging exceptions
try:
    # Some code that might raise an exception
    result = 1 / 0
except Exception as e:
    debug_log.exception("component_name", "Division failed")
```

## Function Instrumentation

You can instrument entire functions using the `@log_function` decorator:

```python
from debug_utils import log_function, LogLevel

@log_function(level=LogLevel.DEBUG, include_args=True)
def process_data(data_id, options=None):
    # Function code...
    return result
```

This will automatically log:
- Function entry with arguments
- Function exit with return value
- Any exceptions that occur

## Enabling Debug Instrumentation

Debug instrumentation is disabled by default. To enable it:

### Environment Variables

Set environment variables before starting your Python service:

```bash
# Enable debugging
export TEKTON_DEBUG=true

# Set log level (TRACE, DEBUG, INFO, WARN, ERROR, FATAL, OFF)
export TEKTON_LOG_LEVEL=DEBUG

# Optional: Write logs to a file (in addition to stdout)
export TEKTON_LOG_FILE=/path/to/tekton-debug.log

# Optional: Output in JSON format instead of text
export TEKTON_LOG_FORMAT=json
```

### Runtime Configuration

You can also enable and configure debugging at runtime:

```python
from debug_utils import debug_log, LogLevel

# Enable debugging
debug_log.set_enabled(True)

# Set component-specific log levels
debug_log.set_component_level("ergon_service", LogLevel.DEBUG)
debug_log.set_component_level("rhetor_service", LogLevel.TRACE)
debug_log.set_component_level("terma_service", LogLevel.INFO)
```

## Integration with Existing Logging

The debug instrumentation works alongside existing `logger()` calls and can be configured to forward to your current logging system.

If you're using a custom logger, you can extend the `DebugLog` class:

```python
from debug_utils import DebugLog, LogLevel

class CustomDebugLog(DebugLog):
    def _log(self, level, component, message, data=None, caller_info=None):
        # Call the base implementation
        result = super()._log(level, component, message, data, caller_info)
        
        # Also log to your custom system
        if result and self.enabled:
            my_custom_logger.log(level.name, f"[{component}] {message}", data)
            
        return result

# Replace the global instance
debug_log = CustomDebugLog()
```

## Best Practices

1. **Component Naming**: Use consistent component names, typically:
   - Class name for class methods
   - Module name for standalone functions
   - Service name for service-level operations

2. **Log Levels**:
   - **TRACE**: Most detailed information for tracing execution flow
   - **DEBUG**: Development-time debugging information
   - **INFO**: Runtime information showing normal operation
   - **WARN**: Warning conditions that don't prevent operation
   - **ERROR**: Error conditions that may impact functionality
   - **FATAL**: Severe errors that prevent operation

3. **Contextual Data**: Include relevant data objects to provide context for logs:
   ```python
   debug_log.info("processor", "Processing request", {
       "request_id": req_id,
       "user_id": user_id,
       "operation": op_name
   })
   ```

4. **Strategic Placement**: Add instrumentation at:
   - Function/method entry and exit points
   - Branch decisions and state changes
   - Error handling blocks
   - Performance-sensitive sections
   - API boundaries

## Practical Examples

### Server Request Handling

```python
from debug_utils import debug_log, log_function

class RequestHandler:
    def __init__(self, config):
        self.config = config
        debug_log.debug("RequestHandler", "Initialized with config", config)
    
    @log_function()
    def handle_request(self, request):
        request_id = request.get("id", "unknown")
        debug_log.info("RequestHandler", f"Processing request {request_id}", request)
        
        try:
            # Process request
            response = self._process(request)
            debug_log.debug("RequestHandler", "Request processed successfully", {
                "request_id": request_id,
                "response_type": type(response).__name__
            })
            return response
        except Exception as e:
            debug_log.exception("RequestHandler", f"Failed to process request {request_id}")
            raise
    
    def _process(self, request):
        # Processing logic
        return {"status": "success"}
```

### Service Implementation

```python
from debug_utils import debug_log, log_function, LogLevel

class DataService:
    @log_function(level=LogLevel.INFO)
    def __init__(self, database_url):
        self.db_url = database_url
        self.connected = False
        
    @log_function()
    def connect(self):
        debug_log.info("DataService", f"Connecting to database: {self.db_url}")
        
        try:
            # Connection logic
            self.connected = True
            debug_log.info("DataService", "Database connection established")
        except Exception as e:
            debug_log.error("DataService", "Database connection failed", {
                "url": self.db_url,
                "error": str(e)
            })
            raise
    
    @log_function()
    def query(self, sql, params=None):
        if not self.connected:
            debug_log.warn("DataService", "Query attempted without connection")
            self.connect()
        
        debug_log.debug("DataService", "Executing query", {
            "sql": sql,
            "params": params
        })
        
        # Query execution logic
        results = ["row1", "row2"]
        
        debug_log.debug("DataService", "Query returned results", {
            "count": len(results)
        })
        
        return results
```

## Python-JavaScript Bridge

The Python debug instrumentation can be integrated with the JavaScript `TektonDebug` system for end-to-end debug visibility:

```python
from debug_utils import debug_log
from flask import jsonify

@app.route('/api/logs', methods=['POST'])
def receive_frontend_logs():
    """Endpoint to receive logs from frontend"""
    data = request.json
    
    # Forward to our Python debug system
    level_name = data.get('level', 'INFO').upper()
    component = data.get('component', 'frontend')
    message = data.get('message', '')
    extra_data = data.get('data')
    
    # Map to our log levels
    log_method = getattr(debug_log, level_name.lower(), debug_log.info)
    log_method(component, message, extra_data)
    
    return jsonify({"status": "ok"})
```

In the frontend code:

```javascript
// Send logs to backend when using TektonDebug
if (window.TektonDebug) {
    TektonDebug.registerBackendLogger(function(level, component, message, data) {
        fetch('/api/logs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                level: level,
                component: component,
                message: message,
                data: data
            })
        });
    });
}
```

This creates a unified debugging experience across both frontend and backend components.

## Performance Considerations

The debug instrumentation is designed to have minimal impact when disabled:

- Debug calls are wrapped in an initial check (`if debug_log.enabled`) that short-circuits when disabled
- No string formatting or object serialization occurs when disabled
- Function decorators skip all debug logic when the system is disabled

This means you can liberally instrument your code without worrying about performance impacts in production.

When enabling debug logging in production, consider using component-specific log levels to focus on the areas you need to diagnose while keeping other components at higher log levels to minimize impact.