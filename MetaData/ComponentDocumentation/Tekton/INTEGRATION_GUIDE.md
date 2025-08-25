# Tekton Integration Guide

This guide provides comprehensive information on integrating your components with the Tekton orchestration system. It covers component registration, communication patterns, lifecycle management, and best practices.

## Overview

Tekton provides a unified framework for component integration through:

1. **Component Registration**: Register your component with the Tekton ecosystem
2. **Service Discovery**: Discover and connect to other components
3. **Messaging**: Communicate with components through standardized protocols
4. **Lifecycle Management**: Coordinate startup, monitoring, and shutdown
5. **Resource Management**: Access and share system resources efficiently

## Component Registration

### Registration Process

Components register with Tekton during their startup process:

```python
from tekton.utils.tekton_registration import register_with_tekton

async def start_my_component():
    # Register with Tekton
    success, instance_uuid = await register_with_tekton(
        component_id="my_component",
        component_name="My Custom Component",
        component_type="service",
        version="1.0.0",
        capabilities=["data_processing", "visualization"],
        dependencies=["engram", "rhetor"],
        port=8500,
        health_check="/api/health",
        metadata={
            "description": "A custom component for data processing",
            "contact": "developer@example.com"
        }
    )
    
    if success:
        print(f"Component registered successfully with UUID: {instance_uuid}")
        return instance_uuid
    else:
        print("Failed to register component")
        return None
```

### Registration Parameters

The registration function accepts the following parameters:

| Parameter | Description | Required |
|-----------|-------------|----------|
| component_id | Unique identifier for the component | Yes |
| component_name | Human-readable name | Yes |
| component_type | Type of component (service, memory, ui, etc.) | Yes |
| version | Component version (semver format) | Yes |
| capabilities | List of component capabilities | No |
| dependencies | List of required components | No |
| host | Component host (defaults to localhost) | No |
| port | Component port | Yes |
| health_check | Health check endpoint | No |
| metadata | Additional component metadata | No |

### Registration with Hermes

If you're using Hermes directly instead of the Tekton utility:

```python
from hermes.api.client import HermesClient

async def register_with_hermes():
    client = HermesClient(host="localhost", port=8001)
    
    registration_data = {
        "component": "my_component",
        "description": "My Custom Component",
        "version": "1.0.0",
        "endpoints": [
            {
                "path": "/api/custom",
                "methods": ["GET", "POST"],
                "description": "Custom endpoint"
            }
        ],
        "capabilities": ["data_processing", "visualization"],
        "host": "localhost",
        "port": 8500,
        "health_check": "/api/health",
        "dependencies": ["engram", "rhetor"]
    }
    
    response = await client.register_component(registration_data)
    return response
```

## Service Discovery

### Finding Components

To find other components in the Tekton ecosystem:

```python
from tekton.utils.component_client import find_component, find_components_by_capability

async def discover_components():
    # Find a specific component by ID
    engram = await find_component("engram")
    if engram:
        print(f"Found Engram at {engram.host}:{engram.port}")
    
    # Find components by capability
    memory_components = await find_components_by_capability("memory_storage")
    for component in memory_components:
        print(f"Found memory component: {component.component_id}")
    
    return engram, memory_components
```

### Component Client

The `ComponentClient` provides a convenient way to interact with discovered components:

```python
from tekton.utils.component_client import ComponentClient

async def use_component_client():
    # Create a client for a specific component
    client = ComponentClient(
        component_id="engram",
        host="localhost",
        port=8000
    )
    
    # Check component health
    health = await client.check_health()
    
    # Call component API
    response = await client.call_api("/api/memory/store", method="POST", data={
        "key": "my_data",
        "value": {"some": "data"}
    })
    
    # Connect via WebSocket
    ws_client = await client.connect_websocket("/ws/memory/changes")
    
    return response
```

### Direct Discovery with Hermes

If you prefer to use Hermes directly:

```python
from hermes.api.client import HermesClient

async def discover_with_hermes():
    client = HermesClient(host="localhost", port=8001)
    
    # Find a specific component
    engram = await client.discover_component("engram")
    
    # Find components by capability
    memory_components = await client.discover_components_by_capability("memory_storage")
    
    # Find all available components
    all_components = await client.list_components()
    
    return engram, memory_components, all_components
```

## Communication Patterns

### HTTP API Calls

The most common way to communicate between components is through HTTP APIs:

```python
from tekton.utils.component_client import find_component

async def api_communication():
    # Find the target component
    engram = await find_component("engram")
    
    if not engram:
        print("Engram component not found")
        return None
    
    # Make an API call
    response = await engram.call_api(
        path="/api/memory/store",
        method="POST",
        data={
            "key": "my_data",
            "value": {"some": "data"}
        },
        headers={"Content-Type": "application/json"}
    )
    
    return response
```

### WebSocket Communication

For real-time, bidirectional communication:

```python
from tekton.utils.component_client import find_component

async def websocket_communication():
    # Find the target component
    rhetor = await find_component("rhetor")
    
    if not rhetor:
        print("Rhetor component not found")
        return None
    
    # Connect via WebSocket
    ws_client = await rhetor.connect_websocket("/ws/generate")
    
    # Send a message
    await ws_client.send_json({
        "prompt": "Write a haiku about programming",
        "model": "claude-3-sonnet-20240229",
        "stream": True
    })
    
    # Handle streaming response
    async for message in ws_client:
        data = message.json()
        if data["type"] == "content":
            print(data["content"], end="", flush=True)
        elif data["type"] == "end":
            break
    
    # Close the connection
    await ws_client.close()
```

### Event-Based Communication

For asynchronous, one-to-many communication:

```python
from tekton.utils.component_client import find_component

async def event_communication():
    # Find the target component
    hermes = await find_component("hermes")
    
    if not hermes:
        print("Hermes component not found")
        return None
    
    # Publish an event
    await hermes.call_api(
        path="/events/publish",
        method="POST",
        data={
            "event_type": "data_updated",
            "payload": {
                "component": "my_component",
                "data_id": "my_data",
                "timestamp": "2025-04-30T15:20:30Z"
            }
        }
    )
    
    # Subscribe to events
    ws_client = await hermes.connect_websocket("/ws/events")
    
    # Send subscription request
    await ws_client.send_json({
        "action": "subscribe",
        "event_types": ["data_updated", "component_status_changed"]
    })
    
    # Handle incoming events
    async for message in ws_client:
        event = message.json()
        print(f"Received event: {event['event_type']}")
        print(f"Payload: {event['payload']}")
    
    # Close the connection
    await ws_client.close()
```

### Message Communication Protocol (MCP)

For structured, high-level communication:

```python
from tekton.mcp.message import Message, MessageType
from tekton.mcp.context import MessageContext
from tekton.utils.component_client import find_component

async def mcp_communication():
    # Find the Tekton core component
    tekton = await find_component("tekton_core")
    
    if not tekton:
        print("Tekton core component not found")
        return None
    
    # Create a message context
    context = MessageContext(
        sender="my_component",
        trace_id="550e8400-e29b-41d4-a716-446655440000"
    )
    
    # Create a message
    message = Message(
        message_type=MessageType.REQUEST,
        content="Generate a description of the Tekton system",
        context=context,
        metadata={
            "priority": "high",
            "timeout": 30
        }
    )
    
    # Send the message
    response = await tekton.call_api(
        path="/api/mcp/process",
        method="POST",
        data=message.to_dict()
    )
    
    # Parse the response
    if response and "message" in response:
        response_message = Message.from_dict(response["message"])
        return response_message.content
    
    return None
```

## Component Lifecycle Management

### Startup Process

Components should implement a standardized startup process:

```python
from tekton.utils.tekton_registration import register_with_tekton
from tekton.utils.tekton_client import wait_for_dependencies

async def startup_process():
    # Step 1: Wait for dependencies
    dependencies = ["engram", "rhetor"]
    success, failed_deps = await wait_for_dependencies(
        dependencies=dependencies,
        timeout=60,
        check_interval=1
    )
    
    if not success:
        print(f"Dependencies failed: {failed_deps}")
        return False
    
    # Step 2: Initialize resources
    try:
        # Initialize database connection
        # Set up in-memory cache
        # Load configuration
        pass
    except Exception as e:
        print(f"Initialization error: {e}")
        return False
    
    # Step 3: Register with Tekton
    success, instance_uuid = await register_with_tekton(
        component_id="my_component",
        component_name="My Custom Component",
        component_type="service",
        version="1.0.0",
        capabilities=["data_processing", "visualization"],
        dependencies=dependencies,
        port=8500
    )
    
    if not success:
        print("Failed to register with Tekton")
        return False
    
    # Step 4: Start API server
    try:
        # Start the server
        pass
    except Exception as e:
        print(f"Server startup error: {e}")
        return False
    
    # Step 5: Start heartbeat
    start_heartbeat_task(instance_uuid)
    
    return True
```

### Heartbeat Mechanism

Components should send regular heartbeats to indicate they're functioning:

```python
import asyncio
from tekton.utils.tekton_client import send_heartbeat

async def send_heartbeats(instance_uuid, interval=10):
    while True:
        try:
            # Collect metrics
            metrics = {
                "cpu_percent": 15.2,
                "memory_percent": 12.5,
                "active_connections": 5,
                "requests_per_second": 10.3
            }
            
            # Send heartbeat
            success = await send_heartbeat(
                component_id="my_component",
                instance_uuid=instance_uuid,
                state="ready",
                metrics=metrics
            )
            
            if not success:
                print("Failed to send heartbeat")
        except Exception as e:
            print(f"Heartbeat error: {e}")
        
        # Wait for next interval
        await asyncio.sleep(interval)

def start_heartbeat_task(instance_uuid):
    # Start heartbeat as background task
    asyncio.create_task(send_heartbeats(instance_uuid))
```

### Graceful Shutdown

Components should implement a graceful shutdown process:

```python
from tekton.utils.tekton_client import deregister_component

async def shutdown_process(instance_uuid):
    # Step 1: Notify Tekton that shutdown is starting
    await update_component_state(
        component_id="my_component",
        instance_uuid=instance_uuid,
        state="stopping"
    )
    
    # Step 2: Complete in-progress work
    # Wait for active requests to complete
    # Cancel pending requests
    
    # Step 3: Release resources
    # Close database connections
    # Free memory resources
    # Save persistent state
    
    # Step 4: Deregister from Tekton
    success = await deregister_component(
        component_id="my_component",
        instance_uuid=instance_uuid
    )
    
    if not success:
        print("Failed to deregister from Tekton")
    
    # Step 5: Stop API server
    # Shut down the server
    
    print("Shutdown complete")
```

### State Transitions

Components should follow the standard state transition flow:

```python
from tekton.utils.tekton_client import update_component_state

async def update_state(instance_uuid, state, metadata=None):
    """Update component state with Tekton.
    
    States:
    - registering: Initial registration
    - initializing: Resource initialization
    - starting: Services starting
    - ready: Fully operational
    - degraded: Operating with reduced functionality
    - stopping: Graceful shutdown in progress
    - stopped: Completely stopped
    - failed: Encountered a critical error
    """
    success = await update_component_state(
        component_id="my_component",
        instance_uuid=instance_uuid,
        state=state,
        metadata=metadata or {}
    )
    
    if not success:
        print(f"Failed to update state to {state}")
    
    return success
```

## Single Port Architecture Integration

### URL Structure

All components should follow the standard URL structure:

```
# Component Base URL
http://localhost:{PORT}/

# API Endpoints
http://localhost:{PORT}/api/...

# WebSocket Endpoints
ws://localhost:{PORT}/ws/...

# Event Endpoints
http://localhost:{PORT}/events/...
```

### Path-Based Routing

Components should implement path-based routing:

```python
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# API routes
@app.get("/api/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/ready")
async def ready():
    return {"status": "ready"}

@app.post("/api/custom")
async def custom_endpoint(data: dict):
    return {"message": "Processed", "data": data}

# WebSocket routes
@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        await websocket.send_json({"message": "Received", "data": data})

# Event routes
@app.post("/events/publish")
async def publish_event(event: dict):
    # Publish event
    return {"message": "Event published"}

# Main entry point
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8500)
```

### Standard Endpoints

All components should implement these standard endpoints:

1. **Health Check**: `/api/health` - Returns the component's health status
2. **Readiness Check**: `/api/ready` - Indicates if the component is ready to accept requests
3. **Version Info**: `/api/version` - Returns component version information
4. **Metrics**: `/api/metrics` - Returns component metrics

```python
@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "checks": {
            "api": "passing",
            "database": "passing",
            "dependencies": "passing"
        },
        "timestamp": "2025-04-30T15:20:30Z"
    }

@app.get("/api/ready")
async def ready():
    return {
        "status": "ready",
        "uptime": 120,  # seconds
        "ready_time": "2025-04-30T15:18:30Z"
    }

@app.get("/api/version")
async def version():
    return {
        "component": "my_component",
        "version": "1.0.0",
        "build_date": "2025-04-30",
        "git_commit": "550e8400e29b41d4a716446655440000"
    }

@app.get("/api/metrics")
async def metrics():
    return {
        "cpu_percent": 15.2,
        "memory_percent": 12.5,
        "active_connections": 5,
        "requests_per_second": 10.3,
        "request_latency_ms": 45.7
    }
```

## Resource Management

### System Resource Monitoring

Components can monitor system resources:

```python
from tekton.core.resource_monitor import ResourceMonitor

def monitor_resources():
    # Create a resource monitor
    monitor = ResourceMonitor(sampling_interval=1.0)  # 1 second interval
    
    # Start monitoring
    monitor.start()
    
    # Get current resource usage
    cpu_usage = monitor.get_cpu_usage()  # e.g., [0.45, 0.2, 0.3, 0.1] for 4 cores
    memory_usage = monitor.get_memory_usage()  # e.g., {"total": 16.0, "used": 8.5, "percent": 53.1}
    gpu_usage = monitor.get_gpu_usage()  # e.g., [{"id": 0, "util": 45, "mem_used": 4.2}]
    
    print(f"CPU usage: {cpu_usage}")
    print(f"Memory usage: {memory_usage}")
    print(f"GPU usage: {gpu_usage}")
    
    # Register a callback for resource thresholds
    monitor.register_threshold_callback(
        resource_type="cpu",
        threshold=80.0,
        callback=lambda: print("CPU usage above 80%!")
    )
    
    # Stop monitoring when done
    monitor.stop()
```

### Resource Constraints

Components should respect resource constraints:

```python
from tekton.utils.tekton_client import get_resource_constraints

async def apply_resource_constraints():
    # Get constraints from Tekton
    constraints = await get_resource_constraints("my_component")
    
    if constraints:
        # Apply CPU constraints
        if "cpu_limit" in constraints:
            cpu_limit = constraints["cpu_limit"]
            print(f"Applying CPU limit: {cpu_limit} cores")
            # Adjust thread pool size based on CPU limit
        
        # Apply memory constraints
        if "memory_limit" in constraints:
            memory_limit = constraints["memory_limit"]
            print(f"Applying memory limit: {memory_limit} MB")
            # Adjust cache size based on memory limit
        
        # Apply GPU constraints
        if "gpu_limit" in constraints:
            gpu_limit = constraints["gpu_limit"]
            print(f"Applying GPU limit: {gpu_limit} MB")
            # Adjust batch size based on GPU limit
    
    return constraints
```

### Resource Reporting

Components should report their resource usage:

```python
from tekton.utils.tekton_client import report_resource_usage

async def report_resources(instance_uuid):
    # Collect resource usage
    usage = {
        "cpu_percent": 15.2,
        "memory_mb": 256.5,
        "memory_percent": 12.5,
        "gpu_memory_mb": 1024.0,
        "gpu_util": 45.3,
        "disk_read_bytes": 1024000,
        "disk_write_bytes": 512000,
        "network_recv_bytes": 2048000,
        "network_sent_bytes": 1024000
    }
    
    # Report to Tekton
    await report_resource_usage(
        component_id="my_component",
        instance_uuid=instance_uuid,
        usage=usage
    )
```

## Model Integration

### Accessing LLM Services

Components can access LLM services through Rhetor:

```python
from tekton.utils.component_client import find_component

async def use_llm_service():
    # Find the Rhetor component
    rhetor = await find_component("rhetor")
    
    if not rhetor:
        print("Rhetor component not found")
        return None
    
    # Generate text
    response = await rhetor.call_api("/api/generate", method="POST", data={
        "prompt": "Explain what Tekton is in one paragraph.",
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 100
    })
    
    if "text" in response:
        return response["text"]
    
    return None
```

### Model Selection

Components can select models based on capabilities:

```python
from tekton.utils.component_client import find_component

async def select_appropriate_model():
    # Find the Tekton core component
    tekton = await find_component("tekton_core")
    
    if not tekton:
        print("Tekton core component not found")
        return None
    
    # Route task to appropriate model
    response = await tekton.call_api("/api/tekton/route", method="POST", data={
        "task_type": "code_generation",
        "complexity": "high",
        "context_length": 5000,
        "requirements": {
            "capabilities": ["code_generation", "code_analysis"],
            "min_tier": 2
        },
        "fallback": True
    })
    
    if "selected_model" in response:
        model = response["selected_model"]
        endpoint = response["endpoint"]
        print(f"Selected model: {model}, endpoint: {endpoint}")
        return model, endpoint
    
    return None, None
```

### Fallback Mechanisms

Components should implement fallback mechanisms for model availability:

```python
from tekton.utils.component_client import find_component
from tekton.core.graceful_degradation import GracefulDegradationManager

async def model_with_fallback():
    # Create a degradation manager
    degradation_manager = GracefulDegradationManager()
    
    # Register fallbacks
    degradation_manager.register_fallback(
        capability="text_generation",
        primary_component="rhetor",
        fallback_component="local_llm",
        fallback_parameters={"model": "llama3"}
    )
    
    # Find the Rhetor component
    rhetor = await find_component("rhetor")
    
    # Try primary model first
    if rhetor:
        try:
            # Generate text with primary model
            response = await rhetor.call_api("/api/generate", method="POST", data={
                "prompt": "Explain what Tekton is in one paragraph.",
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 100
            })
            
            if "text" in response:
                return response["text"]
        except Exception as e:
            print(f"Primary model error: {e}")
    
    # Fall back to local model
    local_llm = await find_component("local_llm")
    if local_llm:
        try:
            # Generate text with fallback model
            response = await local_llm.call_api("/api/generate", method="POST", data={
                "prompt": "Explain what Tekton is in one paragraph.",
                "model": "llama3",
                "max_tokens": 100
            })
            
            if "text" in response:
                return response["text"]
        except Exception as e:
            print(f"Fallback model error: {e}")
    
    # Default response if all models fail
    return "Tekton is an CI orchestration system. (Generated offline due to model unavailability)"
```

## Agent Integration

### Creating an Agent

Components can create agents through Ergon:

```python
from tekton.utils.component_client import find_component

async def create_agent():
    # Find the Ergon component
    ergon = await find_component("ergon")
    
    if not ergon:
        print("Ergon component not found")
        return None
    
    # Create an agent
    response = await ergon.call_api("/api/agents", method="POST", data={
        "agent_id": "my_agent",
        "agent_name": "My Custom Agent",
        "description": "An agent that helps with specific tasks",
        "capabilities": ["task1", "task2", "task3"],
        "system_prompt": "You are a helpful assistant that specializes in specific tasks.",
        "tools": [
            {
                "name": "search_data",
                "description": "Search for data in the repository",
                "parameters": {
                    "query": {"type": "string", "description": "The search query"}
                }
            }
        ]
    })
    
    if "agent_id" in response:
        return response["agent_id"]
    
    return None
```

### Assigning Tasks

Components can assign tasks to agents:

```python
from tekton.utils.component_client import find_component

async def assign_task():
    # Find the Ergon component
    ergon = await find_component("ergon")
    
    if not ergon:
        print("Ergon component not found")
        return None
    
    # Create a task
    response = await ergon.call_api("/api/agents/my_agent/tasks", method="POST", data={
        "task_type": "data_analysis",
        "inputs": {
            "data_source": "customer_data",
            "analysis_type": "clustering",
            "parameters": {
                "clusters": 5,
                "algorithm": "k-means"
            }
        },
        "tools": ["data_loader", "data_analyzer", "chart_generator"],
        "system_context": "The user needs to analyze customer data to identify segments."
    })
    
    if "task_id" in response:
        task_id = response["task_id"]
        print(f"Created task with ID: {task_id}")
        return task_id
    
    return None
```

### Agent-to-Agent Communication

Components can facilitate agent-to-agent communication:

```python
from tekton.utils.component_client import find_component
from tekton.a2a.message import AgentMessage

async def agent_communication():
    # Find the Ergon component
    ergon = await find_component("ergon")
    
    if not ergon:
        print("Ergon component not found")
        return None
    
    # Create a conversation
    response = await ergon.call_api("/api/conversations", method="POST", data={
        "initiator": "my_agent",
        "participants": ["my_agent", "data_analysis_agent", "visualization_agent"]
    })
    
    if "conversation_id" in response:
        conversation_id = response["conversation_id"]
        
        # Send a message in the conversation
        message_response = await ergon.call_api(f"/api/conversations/{conversation_id}/messages", method="POST", data={
            "sender": "my_agent",
            "content": "I need help analyzing this dataset and creating visualizations.",
            "context": {
                "dataset": "customer_data.csv",
                "columns": ["age", "income", "purchases", "location"]
            }
        })
        
        return conversation_id
    
    return None
```

## UI Integration

### Creating UI Components

Components can provide UI elements for the Hephaestus web interface:

1. Create a component template file (my-component.html):

```html
<template id="my-component-template">
  <div class="my-component">
    <h1>My Custom Component</h1>
    <div class="content">
      <!-- Component content -->
      <div class="controls">
        <button id="refreshButton">Refresh</button>
        <button id="analyzeButton">Analyze</button>
      </div>
      
      <div id="resultArea">
        <!-- Results will be displayed here -->
      </div>
    </div>
  </div>

  <style>
    .my-component {
      padding: 20px;
      background-color: #f5f5f5;
      border-radius: 8px;
    }
    
    .controls {
      margin-bottom: 20px;
    }
    
    button {
      padding: 8px 16px;
      background-color: #4a8fff;
      color: white;
      border: none;
      border-radius: 4px;
      margin-right: 10px;
      cursor: pointer;
    }
    
    #resultArea {
      padding: 15px;
      background-color: white;
      border-radius: 4px;
      min-height: 200px;
    }
  </style>
</template>
```

2. Create a component script (my-component.js):

```javascript
class MyComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    const template = document.getElementById('my-component-template');
    this.shadowRoot.appendChild(template.content.cloneNode(true));
    
    // Component state
    this.state = {
      results: [],
      loading: false,
      error: null
    };
    
    // Initialize API client
    this.apiClient = window.tektonAPI.createClient('my_component');
  }

  connectedCallback() {
    // Initialize the component
    this.init();
    
    // Set up event listeners
    this.shadowRoot.getElementById('refreshButton').addEventListener('click', () => this.refresh());
    this.shadowRoot.getElementById('analyzeButton').addEventListener('click', () => this.analyze());
  }
  
  disconnectedCallback() {
    // Clean up event listeners
    this.shadowRoot.getElementById('refreshButton').removeEventListener('click', () => this.refresh());
    this.shadowRoot.getElementById('analyzeButton').removeEventListener('click', () => this.analyze());
  }

  async init() {
    // Initial data fetch
    await this.refresh();
  }
  
  async refresh() {
    this.setState({ loading: true, error: null });
    
    try {
      // Fetch data from component API
      const response = await this.apiClient.get('/api/custom/data');
      
      // Update state with results
      this.setState({ 
        results: response.data,
        loading: false 
      });
      
      // Update UI
      this.renderResults();
    } catch (error) {
      this.setState({ 
        error: error.message,
        loading: false 
      });
      this.renderError();
    }
  }
  
  async analyze() {
    this.setState({ loading: true, error: null });
    
    try {
      // Call analysis endpoint
      const response = await this.apiClient.post('/api/custom/analyze', {
        data: this.state.results
      });
      
      // Update state with analysis results
      this.setState({ 
        analysisResults: response.data,
        loading: false 
      });
      
      // Update UI
      this.renderAnalysis();
    } catch (error) {
      this.setState({ 
        error: error.message,
        loading: false 
      });
      this.renderError();
    }
  }
  
  setState(newState) {
    this.state = { ...this.state, ...newState };
  }
  
  renderResults() {
    const resultArea = this.shadowRoot.getElementById('resultArea');
    
    if (this.state.loading) {
      resultArea.innerHTML = '<div class="loading">Loading...</div>';
      return;
    }
    
    // Render results
    resultArea.innerHTML = `
      <h3>Results (${this.state.results.length})</h3>
      <ul>
        ${this.state.results.map(item => `
          <li>
            <strong>${item.name}</strong>: ${item.value}
          </li>
        `).join('')}
      </ul>
    `;
  }
  
  renderAnalysis() {
    const resultArea = this.shadowRoot.getElementById('resultArea');
    
    // Render analysis results
    resultArea.innerHTML = `
      <h3>Analysis Results</h3>
      <div class="analysis">
        <p>Average: ${this.state.analysisResults.average}</p>
        <p>Maximum: ${this.state.analysisResults.maximum}</p>
        <p>Minimum: ${this.state.analysisResults.minimum}</p>
      </div>
    `;
  }
  
  renderError() {
    const resultArea = this.shadowRoot.getElementById('resultArea');
    
    // Render error message
    resultArea.innerHTML = `
      <div class="error">
        <h3>Error</h3>
        <p>${this.state.error}</p>
      </div>
    `;
  }
}

// Register the component
customElements.define('my-component', MyComponent);

// Register with Tekton UI
window.tektonComponents = window.tektonComponents || {};
window.tektonComponents.myComponent = {
  name: "My Component",
  description: "A custom component for data visualization",
  icon: "bar-chart",
  path: "/my-component",
  element: "my-component",
  scripts: ["/components/my-component.js"],
  styles: ["/styles/my-component.css"]
};
```

3. Create a component registration script (register-component.js):

```javascript
// Register component with Hephaestus UI
(function() {
  // Create script element
  const scriptElement = document.createElement('script');
  scriptElement.src = '/components/my-component.js';
  
  // Create template element
  const templateElement = document.createElement('template');
  templateElement.id = 'my-component-template';
  templateElement.innerHTML = /* HTML template content */;
  
  // Add to document
  document.head.appendChild(scriptElement);
  document.body.appendChild(templateElement);
  
  // Register with Hephaestus UI manager
  if (window.HephaestusUI && window.HephaestusUI.registerComponent) {
    window.HephaestusUI.registerComponent({
      name: "My Component",
      description: "A custom component for data visualization",
      icon: "bar-chart",
      path: "/my-component",
      element: "my-component",
      scripts: ["/components/my-component.js"],
      styles: ["/styles/my-component.css"]
    });
  }
})();
```

### Server-Side Registration

Register your UI component with the Hephaestus server:

```python
from tekton.utils.component_client import find_component

async def register_ui_component():
    # Find the Hephaestus component
    hephaestus = await find_component("hephaestus")
    
    if not hephaestus:
        print("Hephaestus component not found")
        return False
    
    # Register UI component
    response = await hephaestus.call_api("/api/components", method="POST", data={
        "component_id": "my_component",
        "name": "My Component",
        "description": "A custom component for data visualization",
        "icon": "bar-chart",
        "path": "/my-component",
        "element_name": "my-component",
        "resources": {
            "scripts": ["/components/my-component.js"],
            "styles": ["/styles/my-component.css"],
            "templates": ["/components/my-component.html"]
        },
        "permissions": ["read", "write"],
        "order": 5
    })
    
    if response and "success" in response:
        return response["success"]
    
    return False
```

## Security Considerations

### Authentication

Components should implement authentication when communicating with other components:

```python
from tekton.utils.tekton_auth import generate_token, verify_token

# Generate a token for component communication
def get_auth_token():
    token = generate_token(
        subject="my_component",
        issuer="tekton",
        expires_in=3600,  # 1 hour
        claims={
            "component_id": "my_component",
            "role": "component"
        }
    )
    return token

# Verify tokens in API endpoints
async def verify_request_token(token):
    is_valid, claims = verify_token(token)
    if not is_valid:
        return False, None
    
    # Check component permissions
    component_id = claims.get("component_id")
    role = claims.get("role")
    
    # Verify the component has appropriate permissions
    # ...
    
    return True, claims
```

### API Security

Secure your component's API endpoints:

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from tekton.utils.tekton_auth import verify_token

app = FastAPI()

async def verify_token_middleware(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    # Extract token from header
    token = authorization.replace("Bearer ", "")
    
    # Verify token
    is_valid, claims = verify_token(token)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return claims

@app.get("/api/sensitive-data", dependencies=[Depends(verify_token_middleware)])
async def get_sensitive_data():
    return {"data": "This is sensitive data"}
```

### Secure Communication

Use secure communication channels:

```python
from tekton.utils.component_client import ComponentClient

# Create a client with secure options
client = ComponentClient(
    component_id="engram",
    host="localhost",
    port=8000,
    use_https=True,
    verify_ssl=True,
    auth_token=get_auth_token()
)

# Make secure API calls
response = await client.call_api(
    path="/api/memory/store",
    method="POST",
    data={"key": "secret_data", "value": "sensitive information"},
    headers={"Authorization": f"Bearer {get_auth_token()}"}
)
```

## Error Handling

### Component-Level Errors

Components should implement standardized error handling:

```python
from tekton.utils.tekton_errors import TektonError, ComponentError, DependencyError

# Custom error class
class MyComponentError(ComponentError):
    def __init__(self, message, code=None, details=None):
        super().__init__(message, component="my_component", code=code, details=details)

# Error handling function
def handle_component_error(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except DependencyError as e:
            # Handle dependency errors
            print(f"Dependency error: {e}")
            # Log the error
            # Try to recover or fallback
            raise MyComponentError(f"Dependency failure: {e}", code="dependency_error")
        except ComponentError as e:
            # Handle component errors
            print(f"Component error: {e}")
            # Log the error
            raise
        except Exception as e:
            # Handle unexpected errors
            print(f"Unexpected error: {e}")
            # Log the error
            raise MyComponentError(f"Unexpected error: {str(e)}", code="internal_error")
    return wrapper

# Use the error handler
@handle_component_error
async def process_data(data):
    # Process data
    if "required_field" not in data:
        raise MyComponentError("Missing required field", code="validation_error")
    
    # Continue processing
    # ...
    
    return {"result": "processed"}
```

### API Error Responses

Components should return standardized error responses:

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from tekton.utils.tekton_errors import TektonError

app = FastAPI()

# Custom exception handler
@app.exception_handler(TektonError)
async def tekton_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "message": str(exc),
                "code": exc.code,
                "component": exc.component,
                "details": exc.details
            }
        }
    )

@app.get("/api/data/{item_id}")
async def get_data(item_id: str):
    try:
        # Fetch data
        if item_id == "nonexistent":
            raise TektonError(
                message="Item not found",
                component="my_component",
                code="not_found",
                details={"item_id": item_id}
            )
        
        # Return data if found
        return {"id": item_id, "value": "Some data"}
    except Exception as e:
        raise TektonError(
            message=f"Error retrieving data: {str(e)}",
            component="my_component",
            code="internal_error"
        )
```

### Error Reporting

Components should report errors to the Tekton monitoring system:

```python
from tekton.utils.tekton_client import report_error

async def report_component_error(error, instance_uuid):
    # Create error report
    error_report = {
        "component_id": "my_component",
        "instance_uuid": instance_uuid,
        "error_type": type(error).__name__,
        "message": str(error),
        "code": getattr(error, "code", "unknown"),
        "timestamp": time.time(),
        "stack_trace": traceback.format_exc(),
        "context": {
            "request_id": getattr(error, "request_id", None),
            "user_id": getattr(error, "user_id", None),
            "resource": getattr(error, "resource", None)
        }
    }
    
    # Report to Tekton
    await report_error(error_report)
```

## Best Practices

### Component Design

1. **Single Responsibility Principle**: Each component should have a clear, focused responsibility
2. **Dependency Injection**: Components should accept dependencies rather than creating them
3. **Configuration Over Code**: Use configuration files instead of hardcoding values
4. **Statelessness**: Design components to be as stateless as possible
5. **Idempotent Operations**: APIs should be idempotent where possible

### Performance

1. **Asynchronous Processing**: Use async/await for I/O-bound operations
2. **Connection Pooling**: Reuse connections to databases and other components
3. **Caching**: Implement appropriate caching mechanisms
4. **Batch Processing**: Process items in batches where possible
5. **Resource Awareness**: Adjust resource usage based on system load

### Resilience

1. **Circuit Breakers**: Implement circuit breakers for dependent components
2. **Timeouts**: Set appropriate timeouts for all external calls
3. **Retries**: Implement retry mechanisms with exponential backoff
4. **Graceful Degradation**: Provide reduced functionality when dependencies fail
5. **Monitoring**: Implement comprehensive monitoring and alerting

### Testing

1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test component interactions
3. **Load Tests**: Test performance under load
4. **Chaos Testing**: Test resilience under failure conditions
5. **Mocking**: Use mocks for external dependencies

## Example Integration

Here's a complete example of a component that integrates with Tekton:

```python
import asyncio
import logging
import os
import time
import traceback
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
import uvicorn

from tekton.utils.tekton_registration import register_with_tekton
from tekton.utils.tekton_client import (
    find_component, 
    wait_for_dependencies,
    send_heartbeat,
    update_component_state,
    deregister_component
)
from tekton.utils.tekton_errors import TektonError, ComponentError
from tekton.core.lifecycle import ComponentState

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("my_component")

# Create FastAPI app
app = FastAPI()

# Component state
STATE = {
    "component_id": "my_component",
    "instance_uuid": None,
    "state": ComponentState.UNKNOWN.value,
    "start_time": None,
    "heartbeat_task": None,
    "dependencies": ["engram", "rhetor"]
}

# Custom error class
class MyComponentError(ComponentError):
    def __init__(self, message, code=None, details=None):
        super().__init__(message, component="my_component", code=code, details=details)

# API routes
@app.get("/")
async def root():
    return {"message": "My Component API"}

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "checks": {
            "api": "passing",
            "dependencies": "passing"
        },
        "state": STATE["state"],
        "timestamp": time.time()
    }

@app.get("/api/ready")
async def ready():
    return {
        "status": "ready" if STATE["state"] == ComponentState.READY.value else "not_ready",
        "uptime": time.time() - STATE["start_time"] if STATE["start_time"] else 0,
        "ready_time": STATE["start_time"]
    }

@app.get("/api/version")
async def version():
    return {
        "component": "my_component",
        "version": "1.0.0",
        "build_date": "2025-04-30"
    }

@app.get("/api/metrics")
async def metrics():
    return {
        "cpu_percent": 15.2,
        "memory_percent": 12.5,
        "active_connections": 5
    }

@app.get("/api/custom/data")
async def get_data():
    try:
        # Example data processing
        data = [
            {"name": "Item 1", "value": 10},
            {"name": "Item 2", "value": 20},
            {"name": "Item 3", "value": 30}
        ]
        return data
    except Exception as e:
        logger.error(f"Error getting data: {e}")
        raise MyComponentError(f"Error getting data: {str(e)}", code="data_error")

@app.post("/api/custom/analyze")
async def analyze_data(request_data: dict):
    try:
        # Example data analysis
        if "data" not in request_data:
            raise MyComponentError("Missing data field", code="validation_error")
        
        data = request_data["data"]
        
        # Calculate statistics
        values = [item["value"] for item in data]
        average = sum(values) / len(values) if values else 0
        maximum = max(values) if values else 0
        minimum = min(values) if values else 0
        
        return {
            "average": average,
            "maximum": maximum,
            "minimum": minimum
        }
    except MyComponentError:
        raise
    except Exception as e:
        logger.error(f"Error analyzing data: {e}")
        raise MyComponentError(f"Error analyzing data: {str(e)}", code="analysis_error")

# Custom exception handler
@app.exception_handler(TektonError)
async def tekton_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "message": str(exc),
                "code": exc.code,
                "component": exc.component,
                "details": exc.details
            }
        }
    )

# Heartbeat function
async def send_heartbeats():
    while True:
        try:
            # Collect metrics
            metrics = {
                "cpu_percent": 15.2,
                "memory_percent": 12.5,
                "active_connections": 5
            }
            
            # Send heartbeat
            success = await send_heartbeat(
                component_id=STATE["component_id"],
                instance_uuid=STATE["instance_uuid"],
                state=STATE["state"],
                metrics=metrics
            )
            
            if not success:
                logger.warning("Failed to send heartbeat")
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
        
        # Wait for next interval
        await asyncio.sleep(10)

# Startup function
async def startup():
    logger.info("Starting My Component...")
    STATE["start_time"] = time.time()
    
    try:
        # Step 1: Wait for dependencies
        logger.info(f"Waiting for dependencies: {STATE['dependencies']}")
        STATE["state"] = ComponentState.INITIALIZING.value
        
        success, failed_deps = await wait_for_dependencies(
            dependencies=STATE["dependencies"],
            timeout=60,
            check_interval=1
        )
        
        if not success:
            logger.error(f"Dependencies failed: {failed_deps}")
            STATE["state"] = ComponentState.FAILED.value
            return False
        
        # Step 2: Register with Tekton
        logger.info("Registering with Tekton...")
        success, instance_uuid = await register_with_tekton(
            component_id=STATE["component_id"],
            component_name="My Custom Component",
            component_type="service",
            version="1.0.0",
            capabilities=["data_processing", "visualization"],
            dependencies=STATE["dependencies"],
            port=8500
        )
        
        if not success:
            logger.error("Failed to register with Tekton")
            STATE["state"] = ComponentState.FAILED.value
            return False
        
        STATE["instance_uuid"] = instance_uuid
        STATE["state"] = ComponentState.STARTING.value
        
        # Step 3: Initialize resources
        # ... (initialize databases, caches, etc.)
        
        # Step 4: Start heartbeat
        STATE["heartbeat_task"] = asyncio.create_task(send_heartbeats())
        
        # Step 5: Mark as ready
        STATE["state"] = ComponentState.READY.value
        await update_component_state(
            component_id=STATE["component_id"],
            instance_uuid=STATE["instance_uuid"],
            state=STATE["state"]
        )
        
        logger.info("My Component started successfully")
        return True
    except Exception as e:
        logger.error(f"Startup error: {e}")
        STATE["state"] = ComponentState.FAILED.value
        return False

# Shutdown function
async def shutdown():
    logger.info("Shutting down My Component...")
    
    try:
        # Step 1: Update state
        STATE["state"] = ComponentState.STOPPING.value
        await update_component_state(
            component_id=STATE["component_id"],
            instance_uuid=STATE["instance_uuid"],
            state=STATE["state"]
        )
        
        # Step 2: Stop heartbeat task
        if STATE["heartbeat_task"]:
            STATE["heartbeat_task"].cancel()
            try:
                await STATE["heartbeat_task"]
            except asyncio.CancelledError:
                pass
        
        # Step 3: Clean up resources
        # ... (close connections, free resources, etc.)
        
        # Step 4: Deregister from Tekton
        if STATE["instance_uuid"]:
            await deregister_component(
                component_id=STATE["component_id"],
                instance_uuid=STATE["instance_uuid"]
            )
        
        # Step 5: Update final state
        STATE["state"] = ComponentState.STOPPED.value
        
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Startup and shutdown events
@app.on_event("startup")
async def app_startup():
    asyncio.create_task(startup())

@app.on_event("shutdown")
async def app_shutdown():
    await shutdown()

# Main entry point
if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("MY_COMPONENT_PORT", 8500))
    
    # Run the server
    uvicorn.run("app:app", host="0.0.0.0", port=port)
```

## Conclusion

Integrating with Tekton provides your component with a rich ecosystem of services, standardized communication patterns, and robust lifecycle management. By following the best practices outlined in this guide, you can create components that seamlessly work with the Tekton orchestration system and contribute to a unified CI development environment.

For more information, see the API Reference and Technical Documentation.