# Tekton Component Debug Instrumentation Guide

This guide explains how to add the Tekton Debug System to any component in the Tekton ecosystem. The debug system provides zero-overhead logging and debugging capabilities that can be enabled/disabled at runtime.

## Overview

The Tekton Debug System consists of two main parts:

1. **Frontend (JavaScript)**: A lightweight debug shim that provides conditional logging with component-specific log levels
2. **Backend (Python)**: Utilities for logging with context, function tracing, and performance metrics

This guide will walk you through how to integrate both parts into your components.

## Frontend Instrumentation

### 1. Add Debug Logging to JavaScript Components

To add debug instrumentation to any JavaScript component:

1. **Check for Debug Availability**:
   First, verify that the TektonDebug object exists before using it:

   ```javascript
   if (window.TektonDebug) TektonDebug.debug('myComponent', 'Message here');
   ```

2. **Use Appropriate Log Levels**:
   Choose the right log level for your message:

   ```javascript
   // Most detailed - for fine-grained tracing
   if (window.TektonDebug) TektonDebug.trace('myComponent', 'Entering function with args', {args: someArgs});
   
   // Development debugging
   if (window.TektonDebug) TektonDebug.debug('myComponent', 'Processing data...');
   
   // General information
   if (window.TektonDebug) TektonDebug.info('myComponent', 'Component initialized');
   
   // Potential issues that don't break functionality
   if (window.TektonDebug) TektonDebug.warn('myComponent', 'Network response slow');
   
   // Errors that affect functionality
   if (window.TektonDebug) TektonDebug.error('myComponent', 'Failed to load data');
   
   // Critical failures
   if (window.TektonDebug) TektonDebug.fatal('myComponent', 'System cannot continue');
   ```

3. **Component Naming Convention**:
   Use consistent names for your components, typically camelCase:
   - `ergonComponent` - Main component
   - `ergonComponent.agentManager` - Submodule
   - `ergonComponent.networkLayer` - Another submodule

4. **Add Debug to Key Functions**:
   Instrument strategically important functions:

   ```javascript
   class MyComponent {
       init() {
           if (window.TektonDebug) TektonDebug.info('myComponent', 'Initializing component');
           
           // Component initialization code
           
           if (window.TektonDebug) TektonDebug.debug('myComponent', 'Component initialized successfully');
       }
       
       processData(data) {
           if (window.TektonDebug) TektonDebug.debug('myComponent', 'Processing data', {dataSize: data.length});
           
           try {
               // Data processing code
               
               if (window.TektonDebug) TektonDebug.debug('myComponent', 'Data processed successfully');
           } catch (error) {
               if (window.TektonDebug) TektonDebug.error('myComponent', 'Error processing data', {error: error.message});
               throw error;
           }
       }
   }
   ```

### 2. Example: Ergon Component Integration

The Ergon component shows a complete integration. Here are key patterns to follow:

```javascript
// In the constructor
constructor() {
    this.state = { /* ... */ };
    
    // Other initialization
}

// In the initialization method
init() {
    // Regular console logging for backward compatibility
    console.log('Initializing component');
    
    // Debug instrumentation
    if (window.TektonDebug) TektonDebug.info('ergonComponent', 'Initializing component');
    
    // Rest of init code...
    
    if (window.TektonDebug) TektonDebug.debug('ergonComponent', 'Component initialized successfully');
}

// For UI operations like tab activation
activateTab(tabId) {
    console.log(`Activating tab: ${tabId}`);
    
    // Debug instrumentation
    if (window.TektonDebug) TektonDebug.debug('ergonComponent', `Activating tab: ${tabId}`);
    
    // Function implementation...
    
    // Log success/completion
    if (window.TektonDebug) TektonDebug.debug('ergonComponent', `Tab ${tabId} activated successfully`);
}
```

## Backend Instrumentation (Python)

### 1. Add Debug Utilities to Python Components

1. **Import Debug Utilities**:
   Add this import to your Python files:

   ```python
   from tekton.shared.debug.debug_utils import debug, info, warn, error, trace_function, track_performance
   ```

2. **Add Basic Logging**:
   Use log functions throughout your code:

   ```python
   def process_data(data):
       debug("data_processor", f"Processing {len(data)} items")
       
       # Processing code
       
       info("data_processor", "Data processing complete")
       return result
   ```

3. **Function Tracing**:
   Use the trace_function decorator for automatic entry/exit logging:

   ```python
   @trace_function("data_processor")
   def process_complex_data(data, options=None):
       # Function implementation
       result = perform_calculation(data)
       return result
   ```

4. **Performance Tracking**:
   Measure performance of critical functions:

   ```python
   @track_performance("data_processor")
   def compute_intensive_task(data):
       # Intensive computation
       return result
   ```

5. **Context Managers**:
   For tracking code blocks:

   ```python
   def process_in_stages(data):
       with performance_tracker("data_processor", "stage_1"):
           # Stage 1 processing
           
       with performance_tracker("data_processor", "stage_2"):
           # Stage 2 processing
   ```

### 2. Example: Python Server Component Integration

```python
from tekton.shared.debug.debug_utils import debug, info, warn, error, trace_function

class DataProcessor:
    def __init__(self, config):
        self.config = config
        info("data_processor", "Initialized with config", extra={"config_name": config.name})
    
    @trace_function("data_processor")
    def process(self, data):
        debug("data_processor", f"Processing {len(data)} records")
        
        try:
            # Processing logic
            if not data:
                warn("data_processor", "Empty data set received")
                return []
                
            result = self._transform_data(data)
            info("data_processor", f"Successfully processed {len(result)} records")
            return result
            
        except Exception as e:
            error("data_processor", f"Error during processing: {str(e)}")
            raise
    
    def _transform_data(self, data):
        debug("data_processor", "Transforming data")
        # Transformation logic
        return transformed_data
```

## Additional Best Practices

### Component-specific Considerations

1. **UI Components (HTML/JS)**:
   - Add debug logs for user interactions
   - Log DOM manipulations
   - Track component lifecycle (init, update, destroy)

2. **Backend Services**:
   - Log API requests and responses
   - Track database operations
   - Monitor resource usage

3. **Integration Points**:
   - Extra logging at component boundaries
   - Log data format transformations
   - Track network requests

### Logging Level Guidelines

1. **TRACE**: Extremely detailed information
   - Function entry/exit
   - Loop iterations
   - Variable values during execution

2. **DEBUG**: Detailed information useful during development
   - Configuration values
   - State transitions
   - Intermediate calculation results

3. **INFO**: General information about the system operation
   - Component initialization/shutdown
   - User actions
   - Successful operations

4. **WARN**: Potential issues that don't prevent operation
   - Performance degradation
   - Using fallback mechanisms
   - Deprecated function usage

5. **ERROR**: Issues that prevent a function from working
   - Failed requests
   - Invalid input
   - Exception handling

6. **FATAL**: Severe errors that prevent system operation
   - Unrecoverable failures
   - Critical resource unavailable
   - Security breaches

## Implementation Checklist

When instrumenting a new component, use this checklist:

- [ ] Add debug checks to the component constructor/initialization
- [ ] Add debug logging to all major functions
- [ ] Add error handling with debug logging
- [ ] Add performance tracking for intensive operations
- [ ] Ensure consistent component naming
- [ ] Use appropriate log levels
- [ ] Test with debug enabled and disabled

## Example: Complete Component Integration

Here's how a typical component would look with full debug instrumentation:

### JavaScript Component

```javascript
class MyComponent {
    constructor() {
        this.state = {
            initialized: false,
            // Other state properties
        };
    }
    
    init() {
        // Legacy logging
        console.log('Initializing MyComponent');
        
        // Debug logging
        if (window.TektonDebug) TektonDebug.info('myComponent', 'Initializing component');
        
        try {
            // Check if already initialized
            if (this.state.initialized) {
                if (window.TektonDebug) TektonDebug.debug('myComponent', 'Component already initialized');
                return this;
            }
            
            // Setup component
            this.setupUI();
            this.loadData();
            
            this.state.initialized = true;
            if (window.TektonDebug) TektonDebug.info('myComponent', 'Component successfully initialized');
            return this;
            
        } catch (error) {
            if (window.TektonDebug) TektonDebug.error('myComponent', 'Initialization failed', {error: error.message});
            throw error;
        }
    }
    
    setupUI() {
        if (window.TektonDebug) TektonDebug.debug('myComponent', 'Setting up UI elements');
        
        // UI setup code
        
        if (window.TektonDebug) TektonDebug.debug('myComponent', 'UI setup complete');
    }
    
    loadData() {
        if (window.TektonDebug) TektonDebug.debug('myComponent', 'Loading data');
        
        // Data loading code
        
        if (window.TektonDebug) TektonDebug.debug('myComponent', 'Data loaded successfully');
    }
    
    processUserAction(action, data) {
        if (window.TektonDebug) TektonDebug.debug('myComponent', `Processing user action: ${action}`, {data});
        
        // Action processing code
        
        if (window.TektonDebug) TektonDebug.debug('myComponent', 'User action processed');
    }
}

// Create global instance
window.myComponent = new MyComponent();
```

### Python Component

```python
from tekton.shared.debug.debug_utils import debug, info, warn, error, trace_function, track_performance

class DataService:
    def __init__(self, config):
        info("data_service", "Initializing service", extra={"config": config.name})
        self.config = config
        self.db_connection = None
        self._initialize_db()
        info("data_service", "Service initialized successfully")
    
    def _initialize_db(self):
        debug("data_service", "Connecting to database")
        try:
            # DB connection code
            self.db_connection = create_connection(self.config.db_url)
            debug("data_service", "Database connection established")
        except Exception as e:
            error("data_service", "Database connection failed", extra={"error": str(e)})
            raise
    
    @trace_function("data_service")
    def get_data(self, query_params):
        debug("data_service", "Fetching data", extra={"params": query_params})
        
        try:
            # Data retrieval code
            result = self.db_connection.execute_query(query_params)
            debug("data_service", f"Retrieved {len(result)} records")
            return result
        except Exception as e:
            error("data_service", "Data retrieval failed", extra={"error": str(e)})
            raise
    
    @track_performance("data_service")
    def process_batch(self, items):
        info("data_service", f"Processing batch of {len(items)} items")
        
        results = []
        for i, item in enumerate(items):
            debug("data_service", f"Processing item {i+1}/{len(items)}")
            # Processing code
            results.append(processed_item)
        
        info("data_service", f"Batch processing complete, {len(results)} items processed")
        return results
```

By following these patterns, you'll ensure consistent, powerful debugging capabilities across all Tekton components.