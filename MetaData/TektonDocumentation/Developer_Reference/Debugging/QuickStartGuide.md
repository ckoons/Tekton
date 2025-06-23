# Tekton Debug System Quick Start Guide

This guide provides a quick reference for adding the Tekton Debug System to new or existing components. For more detailed information, see the [Component Instrumentation Guide](./ComponentInstrumentation.md).

## Frontend (JavaScript) Quick Start

### 1. Check Debug System Availability

Always check if the debug system is available before using it:

```javascript
if (window.TektonDebug) TektonDebug.debug('componentName', 'Your message here');
```

### 2. Log Levels Reference

| Level | Method | Usage |
|-------|--------|-------|
| TRACE | `TektonDebug.trace()` | Fine-grained debugging, function entry/exit |
| DEBUG | `TektonDebug.debug()` | Development information, state changes |
| INFO | `TektonDebug.info()` | General information, initialization |
| WARN | `TektonDebug.warn()` | Potential issues, deprecations |
| ERROR | `TektonDebug.error()` | Errors affecting functionality |
| FATAL | `TektonDebug.fatal()` | Critical failures, system cannot continue |

### 3. Basic Integration Template

```javascript
class MyComponent {
    constructor() {
        // Initialize properties
    }
    
    init() {
        // Legacy logging
        console.log('Component initializing');
        
        // Debug logging
        if (window.TektonDebug) TektonDebug.info('myComponent', 'Initializing component');
        
        // Component initialization
        
        if (window.TektonDebug) TektonDebug.info('myComponent', 'Component initialized');
        return this;
    }
    
    doSomething(data) {
        if (window.TektonDebug) TektonDebug.debug('myComponent', 'Processing data', {data});
        
        try {
            // Implementation
            
            if (window.TektonDebug) TektonDebug.debug('myComponent', 'Operation completed');
        } catch (error) {
            if (window.TektonDebug) TektonDebug.error('myComponent', 'Operation failed', {error: error.message});
            throw error;
        }
    }
}
```

## Backend (Python) Quick Start

### 1. Import Debug Utilities

```python
from tekton.shared.debug.debug_utils import debug, info, warn, error, trace_function, track_performance
```

### 2. Basic Logging

```python
def my_function():
    debug("component_name", "Starting operation")
    
    # Function implementation
    
    info("component_name", "Operation completed")
```

### 3. Function Decorators

```python
@trace_function("component_name")
def complex_function(arg1, arg2):
    # Implementation
    return result

@track_performance("component_name")
def intensive_function(data):
    # Implementation
    return result
```

## Common Instrumentation Points

### Component Lifecycle
- Initialization/Construction
- Configuration loading
- Resource acquisition
- Shutdown/Cleanup

### Operations
- Function entry/exit points
- Data processing
- State changes
- User interactions
- Network requests
- Error handling

### UI Components
- DOM manipulations
- Event handlers
- State updates
- Rendering

## Best Practices

1. **Be Consistent**: Use the same component name throughout your logging.

2. **Log Hierarchically**: Use dot notation for subcomponents:
   ```javascript
   TektonDebug.debug('myComponent.dataLayer', 'Fetching data');
   ```

3. **Include Context**: Add relevant data to help with debugging:
   ```javascript
   TektonDebug.debug('myComponent', 'Processing item', {itemId: item.id, status: item.status});
   ```

4. **Use Appropriate Levels**: Don't overuse higher severity levels.

5. **Zero Overhead**: Always wrap debug calls in conditions to ensure zero overhead when disabled:
   ```javascript
   if (window.TektonDebug) TektonDebug.debug(...);
   ```

6. **Strategic Placement**: Focus on key points in the code rather than logging everything.

## Enabling/Disabling Debug

The debug system can be controlled through environment variables:

- `window.TEKTON_DEBUG = 'true'` - Master switch for enabling/disabling debugging
- `window.TEKTON_LOG_LEVEL = 'DEBUG'` - Set the default log level

For component-specific levels, use:

```javascript
// In JavaScript
if (window.TektonDebug) {
    TektonDebug.config.componentLevels['myComponent'] = 'DEBUG';
    TektonDebug.config.componentLevels['anotherComponent'] = 'ERROR';
}
```

## Tips for Effective Debugging

1. **Log Smart, Not Everything**: Focus on critical paths and state changes.

2. **Use Categories**: Organize logs by functional area.

3. **Pair with Browser DevTools**: Use together with browser debugging tools.

4. **Add Timestamps**: Include timestamps for timing-sensitive operations.

5. **Correlate Logs**: Use consistent IDs for tracking operations across components.

6. **Test Debug Mode**: Verify components work with debug both enabled and disabled.

For more information, see the comprehensive [Component Instrumentation Guide](./ComponentInstrumentation.md).