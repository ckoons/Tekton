# Tekton API Reference

This document provides a comprehensive reference for the Tekton orchestration system's API endpoints, client libraries, and integration methods.

## Core API

### Component Management

#### Register Component

Register a component with the Tekton orchestration system.

**Endpoint:** `POST /api/tekton/components`

**Request Body:**
```json
{
  "component_id": "my_component",
  "component_name": "My Custom Component",
  "component_type": "service",
  "version": "1.0.0",
  "capabilities": ["data_processing", "visualization"],
  "dependencies": ["engram", "rhetor"],
  "host": "localhost",
  "port": 8500,
  "health_check": "/api/health",
  "metadata": {
    "description": "A custom component for data processing",
    "contact": "developer@example.com"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Component registered successfully",
  "instance_uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### List Components

Get a list of all registered components.

**Endpoint:** `GET /api/tekton/components`

**Parameters:**
- `status` (optional): Filter by component status (ready, initializing, failed)
- `type` (optional): Filter by component type

**Response:**
```json
{
  "components": [
    {
      "component_id": "engram",
      "component_name": "Engram Memory Service",
      "component_type": "memory",
      "version": "1.0.0",
      "status": "ready",
      "host": "localhost",
      "port": 8000,
      "capabilities": ["memory_storage", "vector_search"],
      "last_heartbeat": "2025-04-30T15:20:30Z"
    },
    {
      "component_id": "rhetor",
      "component_name": "Rhetor LLM Manager",
      "component_type": "llm",
      "version": "1.0.0",
      "status": "ready",
      "host": "localhost",
      "port": 8003,
      "capabilities": ["text_generation", "text_embedding", "text_classification"],
      "last_heartbeat": "2025-04-30T15:20:28Z"
    }
  ]
}
```

#### Get Component Details

Get detailed information about a specific component.

**Endpoint:** `GET /api/tekton/components/{component_id}`

**Response:**
```json
{
  "component_id": "engram",
  "component_name": "Engram Memory Service",
  "component_type": "memory",
  "version": "1.0.0",
  "status": "ready",
  "host": "localhost",
  "port": 8000,
  "capabilities": ["memory_storage", "vector_search"],
  "dependencies": ["hermes"],
  "health_check": "/api/health",
  "last_heartbeat": "2025-04-30T15:20:30Z",
  "startup_time": "2025-04-30T15:10:30Z",
  "uptime": "00:10:00",
  "metadata": {
    "description": "Persistent memory system for Tekton",
    "storage_type": "vector"
  },
  "instances": [
    {
      "instance_uuid": "550e8400-e29b-41d4-a716-446655440000",
      "status": "ready",
      "created_at": "2025-04-30T15:10:25Z"
    }
  ]
}
```

#### Start Component

Start a registered component.

**Endpoint:** `POST /api/tekton/components/{component_id}/start`

**Response:**
```json
{
  "success": true,
  "message": "Component starting",
  "instance_uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Stop Component

Stop a running component.

**Endpoint:** `POST /api/tekton/components/{component_id}/stop`

**Request Body:**
```json
{
  "instance_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "force": false,
  "timeout": 30
}
```

**Response:**
```json
{
  "success": true,
  "message": "Component stopped successfully"
}
```

#### Get Component Status

Get the current status of a component.

**Endpoint:** `GET /api/tekton/components/{component_id}/status`

**Response:**
```json
{
  "component_id": "engram",
  "status": "ready",
  "last_heartbeat": "2025-04-30T15:20:30Z",
  "uptime": "00:10:00",
  "instance_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "health_status": {
    "overall": "healthy",
    "database": "healthy",
    "api": "healthy",
    "memory_usage": "low"
  }
}
```

### Dependency Management

#### Get Dependency Graph

Get the current dependency graph of all components.

**Endpoint:** `GET /api/tekton/dependencies`

**Response:**
```json
{
  "dependencies": {
    "api_gateway": ["hermes", "engram", "rhetor"],
    "hermes": [],
    "engram": ["hermes"],
    "rhetor": ["hermes", "engram"],
    "athena": ["hermes", "engram"],
    "ergon": ["hermes", "rhetor"]
  },
  "startup_order": ["hermes", "engram", "rhetor", "athena", "ergon", "api_gateway"],
  "circular_dependencies": []
}
```

#### Get Component Dependencies

Get the dependencies for a specific component.

**Endpoint:** `GET /api/tekton/components/{component_id}/dependencies`

**Response:**
```json
{
  "component_id": "rhetor",
  "depends_on": ["hermes", "engram"],
  "dependent_components": ["ergon", "api_gateway"]
}
```

### Resource Monitoring

#### Get System Resources

Get current system resource usage.

**Endpoint:** `GET /api/tekton/resources`

**Response:**
```json
{
  "cpu": {
    "overall_percent": 45.2,
    "per_core": [35.1, 55.3, 40.2, 50.2],
    "cores": 4,
    "load_average": [2.34, 2.15, 1.97]
  },
  "memory": {
    "total": 16.0,
    "used": 8.5,
    "free": 7.5,
    "percent": 53.1,
    "swap_total": 8.0,
    "swap_used": 1.2,
    "swap_free": 6.8
  },
  "disk": {
    "total": 512.0,
    "used": 256.0,
    "free": 256.0,
    "percent": 50.0
  },
  "gpu": [
    {
      "id": 0,
      "name": "NVIDIA RTX 4090",
      "util": 45,
      "memory_total": 24.0,
      "memory_used": 4.2,
      "memory_free": 19.8,
      "temperature": 65
    }
  ],
  "timestamp": "2025-04-30T15:20:30Z"
}
```

#### Get Component Resource Usage

Get resource usage for a specific component.

**Endpoint:** `GET /api/tekton/components/{component_id}/resources`

**Response:**
```json
{
  "component_id": "rhetor",
  "resource_usage": {
    "cpu_percent": 25.3,
    "memory": {
      "rss": 512.0,
      "vms": 1024.0,
      "percent": 12.5
    },
    "gpu": {
      "id": 0,
      "memory_used": 2.1
    },
    "network": {
      "bytes_sent": 1024000,
      "bytes_recv": 2048000
    },
    "disk_io": {
      "read_bytes": 10485760,
      "write_bytes": 5242880
    }
  },
  "timestamp": "2025-04-30T15:20:30Z"
}
```

### LLM Integration

#### List Available Models

Get a list of available LLM models.

**Endpoint:** `GET /api/tekton/models`

**Response:**
```json
{
  "models": [
    {
      "id": "claude-3-sonnet-20240229",
      "provider": "anthropic",
      "capabilities": ["text_generation", "text_embedding", "summarization"],
      "tier": 3,
      "context_window": 200000,
      "status": "available"
    },
    {
      "id": "gpt-4-turbo",
      "provider": "openai",
      "capabilities": ["text_generation", "text_embedding", "code_generation"],
      "tier": 3,
      "context_window": 128000,
      "status": "available"
    },
    {
      "id": "llama3",
      "provider": "ollama",
      "capabilities": ["text_generation", "code_generation"],
      "tier": 2,
      "context_window": 8000,
      "status": "available"
    }
  ]
}
```

#### Route Task to Model

Route a task to the most appropriate model.

**Endpoint:** `POST /api/tekton/route`

**Request Body:**
```json
{
  "task_type": "code_generation",
  "complexity": "high",
  "context_length": 5000,
  "requirements": {
    "capabilities": ["code_generation", "code_analysis"],
    "min_tier": 2
  },
  "fallback": true
}
```

**Response:**
```json
{
  "selected_model": "claude-3-sonnet-20240229",
  "provider": "anthropic",
  "endpoint": "http://localhost:8003/api/generate",
  "selection_criteria": {
    "complexity_match": true,
    "context_window_sufficient": true,
    "capability_match": true,
    "tier_match": true
  },
  "fallback_models": ["gpt-4-turbo", "llama3"]
}
```

#### List Model Capabilities

Get a list of all model capabilities.

**Endpoint:** `GET /api/tekton/capabilities`

**Response:**
```json
{
  "capabilities": [
    {
      "id": "text_generation",
      "description": "Generate text based on a prompt",
      "supported_models": [
        "claude-3-sonnet-20240229",
        "gpt-4-turbo",
        "llama3"
      ]
    },
    {
      "id": "code_generation",
      "description": "Generate code based on a specification",
      "supported_models": [
        "claude-3-sonnet-20240229",
        "gpt-4-turbo",
        "llama3"
      ]
    },
    {
      "id": "text_embedding",
      "description": "Generate vector embeddings for text",
      "supported_models": [
        "claude-3-sonnet-20240229",
        "gpt-4-turbo"
      ]
    }
  ]
}
```

## WebSocket API

### Component Heartbeat Channel

Subscribe to component heartbeat events.

**Endpoint:** `ws://localhost:8010/ws/tekton/heartbeat`

**Messages:**

1. Client sends subscription request:
```json
{
  "action": "subscribe",
  "component_id": "all"
}
```

2. Server sends heartbeat events:
```json
{
  "event": "heartbeat",
  "component_id": "engram",
  "timestamp": "2025-04-30T15:20:30Z",
  "status": "ready",
  "metrics": {
    "cpu_percent": 15.2,
    "memory_percent": 12.5,
    "active_connections": 5
  }
}
```

### Component State Change Channel

Subscribe to component state change events.

**Endpoint:** `ws://localhost:8010/ws/tekton/state`

**Messages:**

1. Client sends subscription request:
```json
{
  "action": "subscribe",
  "component_types": ["all"]
}
```

2. Server sends state change events:
```json
{
  "event": "state_change",
  "component_id": "rhetor",
  "previous_state": "initializing",
  "new_state": "ready",
  "timestamp": "2025-04-30T15:15:30Z",
  "metadata": {
    "startup_duration": 5.2
  }
}
```

## Client SDK

### Python SDK

The Tekton Python SDK provides a convenient way to interact with the Tekton orchestration system:

```python
from tekton.client import TektonClient, ComponentRegistration

# Create a client
client = TektonClient(host="localhost", port=8010)

# Register a component
registration = ComponentRegistration(
    component_id="my_component",
    component_name="My Custom Component",
    component_type="service",
    version="1.0.0",
    capabilities=["data_processing", "visualization"],
    dependencies=["engram", "rhetor"],
    port=8500
)

success, uuid = await client.register_component(registration)

# Get component status
status = await client.get_component_status("engram")

# Find a component by capability
components = await client.find_components_by_capability("vector_search")

# Start a component
success = await client.start_component("rhetor")

# Monitor resources
resources = await client.get_system_resources()

# Route a task to the appropriate model
route_info = await client.route_task(
    task_type="text_generation",
    complexity="medium",
    context_length=2000
)

# Send heartbeats
heartbeat_task = client.start_heartbeat("my_component", interval=10)

# Stop heartbeats when done
await heartbeat_task.stop()
```

### JavaScript SDK

The Tekton JavaScript SDK provides client-side access to the Tekton API:

```javascript
import { TektonClient } from 'tekton-client';

// Create a client
const client = new TektonClient({
  host: 'localhost',
  port: 8010
});

// Register a component
const registration = {
  component_id: 'my_frontend',
  component_name: 'My Frontend Component',
  component_type: 'ui',
  version: '1.0.0',
  capabilities: ['user_interface', 'data_visualization'],
  dependencies: ['api_gateway']
};

client.registerComponent(registration)
  .then(result => {
    console.log(`Component registered: ${result.success}`);
    console.log(`Instance UUID: ${result.instance_uuid}`);
  });

// Get component status
client.getComponentStatus('engram')
  .then(status => {
    console.log(`Engram status: ${status.status}`);
  });

// Subscribe to heartbeat events
const subscription = client.subscribeToHeartbeats('all', event => {
  console.log(`Heartbeat from ${event.component_id}: ${event.status}`);
});

// Unsubscribe when done
subscription.unsubscribe();
```

## Integration Patterns

### Component Registration

Components should register with Tekton during their startup sequence:

```python
from tekton.utils.tekton_registration import register_with_tekton

async def initialize_component():
    # Step 1: Register with Tekton
    success, instance_uuid = await register_with_tekton(
        component_id="my_component",
        component_name="My Custom Component",
        component_type="service",
        version="1.0.0",
        capabilities=["data_processing", "visualization"],
        dependencies=["engram", "rhetor"],
        port=8500
    )
    
    if not success:
        logger.error("Failed to register with Tekton")
        return False
    
    # Step 2: Start sending heartbeats
    heartbeat_task = start_heartbeat_task(instance_uuid)
    
    # Step 3: Initialize component resources
    # ...
    
    # Step 4: Notify Tekton that the component is ready
    await mark_ready(instance_uuid)
    
    return True
```

### Dependency Resolution

Components should wait for their dependencies to be ready:

```python
from tekton.utils.tekton_client import wait_for_dependencies

async def start_component():
    # Define dependencies
    dependencies = ["engram", "rhetor"]
    
    # Wait for dependencies to be ready
    success, failed_deps = await wait_for_dependencies(
        dependencies=dependencies,
        timeout=60,
        check_interval=1
    )
    
    if not success:
        logger.error(f"Dependencies failed: {failed_deps}")
        return False
    
    # Continue with component initialization
    # ...
    
    return True
```

### Graceful Shutdown

Components should gracefully shut down when requested:

```python
from tekton.utils.tekton_client import listen_for_shutdown

async def run_component():
    # Initialize component
    # ...
    
    # Start listening for shutdown signals
    shutdown_event = asyncio.Event()
    asyncio.create_task(listen_for_shutdown(
        component_id="my_component",
        instance_uuid=instance_uuid,
        shutdown_event=shutdown_event
    ))
    
    # Main component loop
    try:
        while not shutdown_event.is_set():
            # Do component work
            # ...
            await asyncio.sleep(0.1)
    finally:
        # Clean up resources
        await cleanup()
        
        # Notify Tekton that the component is shutting down
        await notify_shutdown(instance_uuid)
```

### Resource Reporting

Components should report their resource usage:

```python
from tekton.utils.tekton_client import report_resources

async def monitor_resources():
    # Create resource reporter
    reporter = ResourceReporter(
        component_id="my_component",
        instance_uuid=instance_uuid,
        interval=10  # seconds
    )
    
    # Start reporting resources
    await reporter.start()
    
    # Stop reporting when done
    try:
        # Wait for shutdown
        await shutdown_event.wait()
    finally:
        await reporter.stop()
```

## Error Codes

| Code | Description |
|------|-------------|
| 1000 | General error |
| 1001 | Component not found |
| 1002 | Registration failed |
| 1003 | Dependency resolution failed |
| 1004 | Startup failed |
| 1005 | Circular dependency detected |
| 1006 | Timeout error |
| 1007 | Resource constraint violated |
| 1008 | Authorization error |
| 1009 | Route not found |
| 1010 | Model not available |
| 1011 | Component already exists |
| 1012 | Invalid component state transition |

## Security

### Authentication

Tekton API endpoints can be secured using JWT-based authentication:

```python
from tekton.client import TektonClient

# Create an authenticated client
client = TektonClient(
    host="localhost",
    port=8010,
    api_key="your_api_key_here"
)
```

### Authorization

Different roles have different access levels:

- **Admin**: Full access to all endpoints
- **Component**: Can register and update itself, send heartbeats
- **Monitor**: Read-only access to component status and metrics
- **User**: Limited access to routing and model information

## Versioning

The Tekton API follows semantic versioning:

- **Major version**: Breaking changes
- **Minor version**: New features, backwards compatible
- **Patch version**: Bug fixes, backwards compatible

The current API version can be obtained from:

**Endpoint:** `GET /api/tekton/version`

**Response:**
```json
{
  "version": "1.0.0",
  "build_date": "2025-04-30",
  "git_commit": "550e8400e29b41d4a716446655440000",
  "api_version": "v1"
}
```