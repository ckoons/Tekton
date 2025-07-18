# Tekton Component Lifecycle

**Last Updated:** April 27, 2025

## Overview

This document describes the standardized component lifecycle model used across all Tekton components. A consistent lifecycle approach ensures proper initialization, graceful shutdown, and reliable operation of all system components.

## Table of Contents

1. [Lifecycle States](#lifecycle-states)
2. [Lifecycle Events](#lifecycle-events)
3. [Component Lifecycle Implementation](#component-lifecycle-implementation)
4. [Resource Management](#resource-management)
5. [Health Checks](#health-checks)
6. [Integration with Hermes](#integration-with-hermes)
7. [Signal Handling](#signal-handling)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Migration Guide](#migration-guide)

## Lifecycle States

Tekton components follow a standard state machine with the following states:

| State | Description |
|-------|-------------|
| UNINITIALIZED | Component has been created but not initialized |
| INITIALIZING | Component is in the process of initializing |
| INITIALIZED | Component has been successfully initialized |
| STARTING | Component is in the process of starting |
| RUNNING | Component is running normally |
| STOPPING | Component is in the process of shutting down |
| STOPPED | Component has been gracefully stopped |
| ERROR | Component encountered an error during its lifecycle |

The standard state transitions are:

```
UNINITIALIZED → INITIALIZING → INITIALIZED → STARTING → RUNNING → STOPPING → STOPPED
```

Error transitions can occur from any state to the ERROR state.

## Lifecycle Events

The following events trigger state transitions or actions within the component lifecycle:

| Event | Description |
|-------|-------------|
| INITIALIZE | Start component initialization |
| INITIALIZATION_COMPLETED | Initialization successfully completed |
| INITIALIZATION_FAILED | Initialization failed |
| START | Start the component |
| START_COMPLETED | Component successfully started |
| START_FAILED | Component failed to start |
| STOP | Stop the component |
| STOP_COMPLETED | Component successfully stopped |
| STOP_FAILED | Component failed to stop |
| ERROR | Component encountered an error |
| HEALTH_CHECK | Perform a component health check |
| HEALTH_CHECK_FAILED | Health check failed |
| SHUTDOWN | External shutdown signal received |

## Component Lifecycle Implementation

Tekton provides a standard base class for implementing component lifecycle:

```python
from tekton.utils.tekton_lifecycle import TektonLifecycle

class MyComponent(TektonLifecycle):
    async def initialize(self) -> bool:
        """
        Initialize the component.
        
        This method should set up all resources needed by the component
        but should not start any active processing.
        
        Returns:
            True if initialization was successful
        """
        # Initialize resources, load configuration, etc.
        self.database = self.track_resource(Database())
        return True
    
    async def start(self) -> bool:
        """
        Start the component.
        
        This method should start all active processing such as
        servers, listeners, and background tasks.
        
        Returns:
            True if startup was successful
        """
        # Start active processing
        self.server = self.track_resource(Server())
        self.background_task = self.create_task(self._process_background)
        return True
    
    async def stop(self) -> bool:
        """
        Stop the component.
        
        This method should stop all active processing and
        prepare the component for shutdown.
        
        Returns:
            True if shutdown was successful
        """
        # Any custom shutdown logic
        # (resources will be cleaned up automatically)
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check component health.
        
        This method should verify the component is functioning
        properly and return health information.
        
        Returns:
            Health status information
        """
        # Basic health info is provided by base class
        health_info = await super().health_check()
        
        # Add component-specific health info
        health_info["custom_status"] = self._check_custom_status()
        
        return health_info
    
    async def _process_background(self):
        """Background processing task."""
        while not self.shutdown_event.is_set():
            # Do background work
            await asyncio.sleep(1)
```

## Resource Management

The lifecycle framework provides automatic tracking and cleanup of resources:

```python
# Track a resource for automatic cleanup
database = self.track_resource(
    Database(), 
    close_method_name="close"  # Method to call during cleanup
)

# Create and track an asyncio task
background_task = self.create_task(self._background_processing)
```

Resources are closed in reverse order of registration during component shutdown.

## Health Checks

Components should implement health checks to verify their operational status:

```python
async def health_check(self) -> Dict[str, Any]:
    """Check component health."""
    # Get basic health info
    health_info = await super().health_check()
    
    # Check database connection
    try:
        database_healthy = await self.database.ping()
        database_status = "healthy" if database_healthy else "degraded"
    except Exception as e:
        database_status = "error"
        health_info["database_error"] = str(e)
    
    # Add component-specific health info
    health_info.update({
        "database_status": database_status,
        "pending_tasks": len(self.task_queue),
        "connections": self.connection_count
    })
    
    # Determine overall status
    if database_status == "error":
        health_info["status"] = "degraded"
    
    return health_info
```

Health checks run automatically at a configured interval (default: 60 seconds).

## Integration with Hermes

The lifecycle framework integrates with Hermes for component registration and status reporting:

```python
# Component registration happens during lifecycle_start()
# Status updates happen during lifecycle state changes:

# During initialization
hermes_status = ComponentStatus.INITIALIZING

# After successful start
hermes_status = ComponentStatus.READY

# During health checks
if health_info["status"] == "degraded":
    hermes_status = ComponentStatus.DEGRADED
else:
    hermes_status = ComponentStatus.READY

# During shutdown
hermes_status = ComponentStatus.SHUTDOWN
```

## Signal Handling

The lifecycle framework automatically sets up signal handlers for graceful shutdown:

```python
def setup_signal_handlers(self, loop=None):
    """Set up signal handlers for graceful shutdown."""
    def handle_signal(sig):
        self.logger.info(f"Received signal {sig}, initiating shutdown")
        asyncio.create_task(self.lifecycle_stop())
    
    loop = loop or asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
```

These handlers ensure that components shut down gracefully when the system is terminated.

## Error Handling

The lifecycle framework integrates with Tekton's error handling system:

```python
try:
    # Component logic
except Exception as e:
    # Transition to ERROR state
    self.state = LifecycleState.ERROR
    self.error = e
    self.logger.error(f"Component error: {e}")
    
    # Update Hermes status
    await self.hermes_component.update_status(ComponentStatus.ERROR)
    
    # Trigger error event
    await self._trigger_event(LifecycleEvent.ERROR)
```

## Best Practices

1. **Separate Initialization and Start**: Keep resource setup in `initialize()` and activation in `start()`
2. **Track All Resources**: Use `track_resource()` for all resources that need cleanup
3. **Use Event Handlers**: Register handlers for lifecycle events when needed
4. **Implement Thorough Health Checks**: Health checks should verify all critical functions
5. **Handle Signals Properly**: Don't override the default signal handlers unless necessary
6. **Clean Shutdown**: Ensure `stop()` properly cleans up all resources
7. **Log Lifecycle Events**: Include clear log messages for all state transitions
8. **Resource Cleanup Order**: Register resources in dependency order
9. **Graceful Degradation**: Handle partial failures gracefully in health checks
10. **Component Dependencies**: Check dependent component health in your health checks

## Migration Guide

To migrate existing components to use the standardized lifecycle:

1. **Identify Lifecycle Methods**: Map existing initialization, startup, and shutdown methods
2. **Update Class Definition**: Inherit from `TektonLifecycle`
3. **Implement Required Methods**: Override `initialize()`, `start()`, and `stop()`
4. **Track Resources**: Update resource management to use `track_resource()`
5. **Add Health Checks**: Implement the `health_check()` method
6. **Update Main Function**: Replace custom lifecycle management with `run()`
7. **Test Carefully**: Test each lifecycle phase thoroughly

### Example Migration

Before:
```python
class MyComponent:
    def __init__(self, config_path):
        self.config = load_config(config_path)
        self.database = None
        self.server = None
    
    def initialize(self):
        self.database = Database(self.config["database_url"])
        return True
    
    def start(self):
        self.server = Server(self.config["port"])
        self.server.start()
        return True
    
    def shutdown(self):
        if self.server:
            self.server.stop()
        if self.database:
            self.database.close()

# Main function
def main():
    component = MyComponent("config.json")
    component.initialize()
    component.start()
    
    # Wait for shutdown signal
    try:
        signal.pause()
    except KeyboardInterrupt:
        component.shutdown()
```

After:
```python
from tekton.utils.tekton_lifecycle import TektonLifecycle
from tekton.utils.tekton_config import TektonConfig

class MyComponent(TektonLifecycle):
    async def initialize(self):
        # Load configuration
        self.config = TektonConfig("mycomponent")
        self.config.load_from_file(self.config_file)
        self.config.load_from_env()
        
        # Initialize database
        self.database = self.track_resource(
            Database(self.config.get("database_url")),
            close_method_name="close"
        )
        return True
    
    async def start(self):
        # Start server
        self.server = self.track_resource(
            Server(self.config.get_int("port")),
            close_method_name="stop"
        )
        await self.server.start()
        return True
    
    async def health_check(self):
        health_info = await super().health_check()
        health_info["database_connected"] = self.database.is_connected()
        health_info["server_status"] = self.server.status
        return health_info

# Main function
def main():
    component = MyComponent(
        component_id="mycomponent",
        component_name="My Component",
        version="1.0.0"
    )
    
    # Config file is optional parameter now
    if args.config_file:
        component.config_file = args.config_file
    
    # Run component (handles signals automatically)
    return asyncio.run(component.run())
```