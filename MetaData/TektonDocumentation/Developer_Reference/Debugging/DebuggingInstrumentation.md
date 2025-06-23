# Tekton Debugging Instrumentation Guide

## Overview

This guide explains how to use the Tekton debugging instrumentation system, which provides a lightweight, zero-overhead approach to adding debug logging throughout the codebase. This approach allows you to instrument code now that can evolve into more sophisticated logging in the future without requiring code changes.

## Key Features

- **Zero Overhead**: When disabled, debugging code has virtually no performance impact
- **Conditional Execution**: All debug calls are wrapped in conditional checks
- **Backend Integration**: Can integrate with existing logger() functions and backends
- **Flexible Configuration**: Supports global and component-specific log levels
- **Contextual Information**: Includes timestamps, component names, and log levels
- **Remote Debugging**: Optional support for streaming logs to remote debugging consoles

## Basic Usage

The core pattern for adding debug instrumentation is:

```javascript
// Check if debug system exists before calling it
if (window.TektonDebug) TektonDebug.debug('componentName', 'Debug message');
```

By checking for the existence of `window.TektonDebug` before using it, this code has minimal overhead when debugging is disabled but provides rich information when enabled.

### Log Levels

The system supports multiple log levels:

- **TRACE**: Most verbose, for detailed tracing information
- **DEBUG**: Detailed debugging information
- **INFO**: General information about application state
- **WARN**: Warning conditions that don't prevent operation
- **ERROR**: Error conditions that may impact functionality
- **FATAL**: Severe error conditions that prevent operation

### Examples

```javascript
// Simple message at INFO level
if (window.TektonDebug) TektonDebug.info('ergon', 'Component initialized');

// Warning with additional context data
if (window.TektonDebug) TektonDebug.warn('athena', 'Connection attempt failed', { 
  attempts: 3, 
  error: err.message 
});

// Error condition
if (window.TektonDebug) TektonDebug.error('terma', 'Failed to process command', {
  command: cmd,
  reason: 'Invalid syntax'
});

// Detailed trace with object data
if (window.TektonDebug) TektonDebug.trace('hermes', 'Message processing details', message);
```

## Integration with Backend Logging

The debug shim automatically attempts to integrate with existing backend logging systems:

1. **WebSocket Manager**: If `window.websocketManager.sendLog()` exists
2. **Global Logger**: If `window.logger()` function exists
3. **Tekton UI**: If `window.tektonUI.log()` method exists

You can also register a custom backend logger:

```javascript
// Register custom backend logger
TektonDebug.registerBackendLogger(function(level, component, message, data) {
  // Implement your own logging logic here
  myCustomLogger.log(level, `[${component}] ${message}`, data);
});
```

## Enabling Debug Instrumentation

Debug instrumentation is disabled by default. To enable it:

### 1. Via Environment Variables

Update `env.js` with:

```javascript
window.TEKTON_DEBUG = 'true';           // Enable debugging
window.TEKTON_LOG_LEVEL = 'DEBUG';      // Set global log level
```

### 2. Via JavaScript (Runtime)

You can enable and configure debugging at runtime:

```javascript
// Enable debugging
TektonDebug.config.enabled = true;

// Set global log level
TektonDebug.config.logLevel = 'DEBUG';

// Set component-specific log level
TektonDebug.config.componentLevels.ergon = 'TRACE';
TektonDebug.config.componentLevels.athena = 'INFO';
```

### 3. Remote Debugging

Enable remote debugging to stream logs to a WebSocket server:

```javascript
// Connect to remote debugging server
TektonDebug.enableRemoteDebugging('ws://debug-server.example.com:8080');
```

## Best Practices

1. **Always Use Conditional Checks**: Ensure every debug call is wrapped in a conditional check
   ```javascript
   if (window.TektonDebug) TektonDebug.debug(...);
   ```

2. **Be Specific with Component Names**: Use consistent component names for filtering
   ```javascript
   // Good
   if (window.TektonDebug) TektonDebug.info('ergon', 'Message');
   
   // Avoid
   if (window.TektonDebug) TektonDebug.info('component', 'Message');
   ```

3. **Choose Appropriate Log Levels**:
   - Use TRACE for very detailed execution tracing
   - Use DEBUG for development-time information
   - Use INFO for general runtime information
   - Use WARN for non-critical issues
   - Use ERROR for functional problems
   - Use FATAL for catastrophic failures

4. **Include Contextual Data**: Add relevant objects or data for context
   ```javascript
   if (window.TektonDebug) TektonDebug.debug('hermes', 'Processing message', messageData);
   ```

5. **Strategic Placement**: Place debug calls at key points in the execution flow
   - Component initialization
   - State changes
   - Event handlers
   - Error conditions
   - Complex logic paths

## Evolution Path

This instrumentation system is designed to evolve over time:

1. **Initial Implementation**: Simple console logging with conditional execution
2. **Backend Integration**: Connection to existing logger() functions
3. **Remote Capabilities**: Streaming to remote debugging consoles
4. **Advanced Features**: Log persistence, filtering, and analysis

The key advantage is that as the implementation evolves, the code instrumentation remains the same.

## Example Component with Instrumentation

```javascript
class ExampleComponent {
    constructor() {
        if (window.TektonDebug) TektonDebug.debug('example', 'Component constructor called');
        
        this.state = {
            initialized: false
        };
    }
    
    init() {
        if (window.TektonDebug) TektonDebug.info('example', 'Initializing component');
        
        if (this.state.initialized) {
            if (window.TektonDebug) TektonDebug.debug('example', 'Already initialized');
            return this;
        }
        
        try {
            this.setupEvents();
            this.loadData();
            this.state.initialized = true;
            
            if (window.TektonDebug) TektonDebug.info('example', 'Component successfully initialized');
        } catch (err) {
            if (window.TektonDebug) TektonDebug.error('example', 'Initialization failed', err);
        }
        
        return this;
    }
    
    setupEvents() {
        if (window.TektonDebug) TektonDebug.debug('example', 'Setting up event handlers');
        // Event setup code...
    }
    
    loadData() {
        if (window.TektonDebug) TektonDebug.debug('example', 'Loading component data');
        // Data loading code...
    }
}
```

## Troubleshooting

If your debug instrumentation isn't working:

1. **Verify Enabled Status**: Check if `TektonDebug.config.enabled` is true
2. **Check Log Level**: Make sure your log level is at or above the threshold
3. **Check Console Filters**: Browsers may filter out debug/info messages by default
4. **Check Code Placement**: Ensure debug calls are after the debug shim is loaded
5. **Verify Backend Integration**: If using backend logging, check connectivity