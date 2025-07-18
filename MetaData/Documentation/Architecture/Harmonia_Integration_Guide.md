# Harmonia Integration Guide

This guide provides detailed instructions for integrating with the Harmonia workflow orchestration engine in the Tekton ecosystem.

## Table of Contents

1. [Overview](#overview)
2. [Integration Patterns](#integration-patterns)
3. [Client Integration](#client-integration)
4. [Component Integration](#component-integration)
5. [Workflow Definition](#workflow-definition)
6. [Event Handling](#event-handling)
7. [State Management](#state-management)
8. [Template System](#template-system)
9. [Single Port Architecture](#single-port-architecture)
10. [Error Handling](#error-handling)
11. [Debugging and Monitoring](#debugging-and-monitoring)
12. [Security Considerations](#security-considerations)

## Overview

Harmonia provides workflow orchestration services to the Tekton ecosystem. It can be integrated in two primary ways:

1. **As a Client**: Components can create and execute workflows, leveraging Harmonia's orchestration capabilities.
2. **As a Provider**: Components can register to handle specific types of tasks within workflows.

## Integration Patterns

### Pattern 1: Workflow Creation and Execution

Use Harmonia to orchestrate complex multi-step processes across multiple components.

```
Client App → Harmonia → Other Components
```

### Pattern 2: Task Handler

Register your component to handle specific task types within workflows.

```
Harmonia → Your Component → Task Results → Harmonia
```

### Pattern 3: Workflow Observer

Subscribe to workflow events to monitor execution without direct participation.

```
Harmonia → WebSocket/SSE → Your Observer Component
```

## Client Integration

### Python Client

```python
import asyncio
from harmonia.client import get_harmonia_client

async def main():
    # Get Harmonia client
    client = await get_harmonia_client()
    
    try:
        # Create workflow
        workflow = await client.create_workflow(
            name="My Workflow",
            description="Example workflow",
            tasks=[
                {
                    "id": "task1",
                    "component": "your_component",
                    "action": "your_action",
                    "input": {"param1": "value1"}
                }
            ]
        )
        
        # Execute workflow
        execution = await client.execute_workflow(
            workflow_id=workflow["workflow_id"],
            input_data={"global_param": "global_value"}
        )
        
        # Get status
        while True:
            status = await client.get_workflow_status(
                execution_id=execution["execution_id"]
            )
            
            if status["status"] in ["completed", "failed", "canceled"]:
                break
                
            await asyncio.sleep(1)
    
    finally:
        await client.close()
```

### JavaScript Client (WebSocket)

```javascript
// Connect to workflow execution events
const ws = new WebSocket('ws://localhost:8002/ws/executions/execution-uuid-here');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Event: ${data.event_type}`, data);
  
  if (data.event_type === 'workflow_completed') {
    console.log('Workflow completed!');
    ws.close();
  }
};

// Optionally send commands to the WebSocket
ws.send(JSON.stringify({
  type: 'ping'
}));
```

### REST API Integration

For custom clients or languages without a dedicated client library:

```bash
# Create a workflow
curl -X POST http://localhost:8002/api/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example_workflow",
    "description": "Example workflow",
    "tasks": [
      {
        "id": "task1",
        "component": "your_component",
        "action": "your_action",
        "input": {"param1": "value1"}
      }
    ]
  }'

# Execute a workflow
curl -X POST http://localhost:8002/api/executions \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "workflow-uuid-here",
    "input": {
      "parameter1": "value1"
    }
  }'

# Get workflow status
curl http://localhost:8002/api/executions/execution-uuid-here
```

## Component Integration

### Registration with Hermes

Components must register with Hermes to be available to Harmonia:

```python
from tekton.core.component_registration import ComponentRegistration

async def register_component():
    registration = ComponentRegistration(
        component_id="your_component_id",
        component_name="Your Component Name",
        hermes_url="http://localhost:5000/api",
        capabilities=[
            {
                "name": "your_action",
                "description": "Description of your action",
                "parameters": {
                    "param1": "string",
                    "param2": "object"
                }
            }
        ],
        metadata={
            "description": "Your component description",
            "version": "1.0.0"
        }
    )
    
    success = await registration.register()
    return success
```

### Implementing Task Handlers

Your component should implement handlers for tasks it supports:

```python
async def handle_task(task_id, task_input):
    """Handle a task request from Harmonia."""
    try:
        # Process the task based on input parameters
        result = {
            "status": "success",
            "data": {
                "processed_result": process_data(task_input)
            }
        }
        return result
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

### Component API Endpoints

Expose API endpoints for Harmonia to call:

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/api/tasks/{task_id}")
async def execute_task(task_id: str, task_input: dict):
    try:
        result = await handle_task(task_id, task_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Workflow Definition

### Basic Workflow Structure

```json
{
  "name": "Data Processing Pipeline",
  "description": "Process and analyze data from multiple sources",
  "tasks": {
    "fetch_data": {
      "component": "data_connector",
      "action": "fetch",
      "input": {
        "source": "database",
        "query": "SELECT * FROM customers"
      }
    },
    "transform_data": {
      "component": "data_processor",
      "action": "transform",
      "input": {
        "data": "${tasks.fetch_data.output.results}",
        "operations": ["normalize", "deduplicate"]
      },
      "depends_on": ["fetch_data"]
    },
    "analyze_data": {
      "component": "analytics",
      "action": "run_analysis",
      "input": {
        "data": "${tasks.transform_data.output.transformed_data}",
        "analysis_type": "segmentation"
      },
      "depends_on": ["transform_data"]
    }
  }
}
```

### Expression Syntax

Harmonia supports dynamic expressions for task input values:

- **Task Output Reference**: `${tasks.<task_id>.output.<path>}`
- **Workflow Input Reference**: `${input.<path>}`
- **Context Variables**: `${context.<path>}`
- **Environment Variables**: `${env.<variable>}`

### Task Dependencies

Tasks can specify dependencies using the `depends_on` property:

```json
"task3": {
  "component": "example",
  "action": "process",
  "depends_on": ["task1", "task2"],
  "input": {
    "combined_data": {
      "part1": "${tasks.task1.output.result}",
      "part2": "${tasks.task2.output.result}"
    }
  }
}
```

### Conditional Execution

Tasks can be conditionally executed based on expressions:

```json
"conditional_task": {
  "component": "example",
  "action": "process",
  "depends_on": ["previous_task"],
  "metadata": {
    "condition": "${tasks.previous_task.output.status == 'success'}"
  },
  "input": {
    "data": "${tasks.previous_task.output.data}"
  }
}
```

## Event Handling

### Event Types

Harmonia emits the following event types:

- `workflow_started`: Workflow execution has started
- `workflow_completed`: Workflow execution has completed successfully
- `workflow_failed`: Workflow execution has failed
- `workflow_canceled`: Workflow execution was canceled
- `workflow_paused`: Workflow execution was paused
- `workflow_resumed`: Workflow execution was resumed
- `task_started`: Task execution has started
- `task_completed`: Task execution has completed successfully
- `task_failed`: Task execution has failed
- `task_skipped`: Task execution was skipped
- `checkpoint_created`: A workflow checkpoint was created
- `retry_attempted`: A task retry was attempted
- `error_occurred`: An error occurred during execution

### WebSocket Subscription

```javascript
// Connect to workflow execution events
const ws = new WebSocket('ws://localhost:8002/ws/executions/execution-uuid-here');

// Event handlers
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch (data.event_type) {
    case 'workflow_started':
      console.log('Workflow started');
      break;
    case 'task_started':
      console.log(`Task ${data.task_id} started`);
      break;
    case 'task_completed':
      console.log(`Task ${data.task_id} completed`);
      break;
    case 'workflow_completed':
      console.log('Workflow completed');
      break;
    default:
      console.log(`Event: ${data.event_type}`, data);
  }
};

// Connection management
ws.onopen = () => console.log('Connected to workflow events');
ws.onerror = (error) => console.error('WebSocket error:', error);
ws.onclose = () => console.log('Disconnected from workflow events');
```

### Server-Sent Events (SSE)

```javascript
// Connect to workflow execution events using SSE
const eventSource = new EventSource('http://localhost:8002/events/executions/execution-uuid-here');

// Event handlers
eventSource.addEventListener('task_started', (event) => {
  const data = JSON.parse(event.data);
  console.log('Task started:', data);
});

eventSource.addEventListener('task_completed', (event) => {
  const data = JSON.parse(event.data);
  console.log('Task completed:', data);
});

eventSource.addEventListener('workflow_completed', (event) => {
  const data = JSON.parse(event.data);
  console.log('Workflow completed:', data);
  eventSource.close();
});

// Generic event handler
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data);
};

// Error handling
eventSource.onerror = (error) => {
  console.error('EventSource error:', error);
  eventSource.close();
};
```

## State Management

### Creating and Restoring Checkpoints

```python
import asyncio
from harmonia.client import get_harmonia_client, get_harmonia_state_client

async def checkpoint_example():
    client = await get_harmonia_client()
    state_client = await get_harmonia_state_client()
    
    # Create a checkpoint for a running workflow
    checkpoint = await state_client.create_checkpoint(
        execution_id="execution-uuid-here"
    )
    
    print(f"Created checkpoint: {checkpoint['checkpoint_id']}")
    
    # Restore from checkpoint
    new_execution = await client.restore_from_checkpoint(
        checkpoint_id=checkpoint["checkpoint_id"]
    )
    
    print(f"Restored as execution: {new_execution['execution_id']}")
```

### Saving Custom State

```python
import asyncio
from harmonia.client import get_harmonia_state_client

async def save_custom_state():
    state_client = await get_harmonia_state_client()
    
    # Save custom state data
    await state_client.save_state(
        execution_id="execution-uuid-here",
        state={
            "custom_data": {
                "key1": "value1",
                "key2": 42,
                "timestamp": "2025-01-01T12:00:00Z"
            },
            "progress": 0.75,
            "processed_items": 150,
            "remaining_items": 50
        }
    )
    
    # Load state
    state = await state_client.load_state(
        execution_id="execution-uuid-here"
    )
    
    print(f"Loaded state: {state}")
```

## Template System

### Creating Templates

```python
import asyncio
from harmonia.client import get_harmonia_client

async def create_template():
    client = await get_harmonia_client()
    
    # Create a workflow first
    workflow = await client.create_workflow(
        name="Parametrized Process",
        tasks=[
            {
                "id": "configurable_task",
                "component": "data_processor",
                "action": "process",
                "input": {
                    "source": "${param.data_source}",
                    "format": "${param.format}",
                    "options": "${param.processing_options}"
                }
            }
        ]
    )
    
    # Create a template from the workflow
    template = await client.create_template(
        name="Data Processing Template",
        workflow_definition_id=workflow["workflow_id"],
        parameters={
            "data_source": {
                "type": "string",
                "required": True,
                "description": "Source of the data to process"
            },
            "format": {
                "type": "string",
                "required": False,
                "default": "json",
                "description": "Format of the data"
            },
            "processing_options": {
                "type": "object",
                "required": False,
                "default": {"normalize": True},
                "description": "Processing options"
            }
        }
    )
    
    return template["template_id"]
```

### Instantiating Templates

```python
import asyncio
from harmonia.client import get_harmonia_client

async def instantiate_template(template_id):
    client = await get_harmonia_client()
    
    # Instantiate the template with specific parameter values
    workflow = await client.instantiate_template(
        template_id=template_id,
        parameter_values={
            "data_source": "s3://mybucket/data.csv",
            "format": "csv",
            "processing_options": {
                "normalize": True,
                "deduplicate": True,
                "remove_nulls": True
            }
        }
    )
    
    # Execute the instantiated workflow
    execution = await client.execute_workflow(
        workflow_id=workflow["workflow_id"]
    )
    
    return execution["execution_id"]
```

## Single Port Architecture

Harmonia follows Tekton's Single Port Architecture pattern, which means all APIs (HTTP, WebSocket, SSE) are exposed through a single port with different path prefixes.

### URL Structure

```
http://localhost:8002/api/*         # HTTP REST API
ws://localhost:8002/ws/*            # WebSocket API
http://localhost:8002/events/*      # Server-Sent Events (SSE) API
```

### Environment Variables

Harmonia uses environment variables for configuration, following the Single Port Architecture pattern:

```bash
# Core settings
HARMONIA_PORT=8002                  # Port for all API interfaces
HARMONIA_HOST=0.0.0.0               # Host to bind to
HARMONIA_LOG_LEVEL=INFO             # Logging level

# Integration settings
HERMES_URL=http://localhost:5000/api # Hermes API URL
HERMES_HEARTBEAT_INTERVAL=60        # Heartbeat interval in seconds

# State management settings
HARMONIA_STATE_DIR=~/.harmonia/state # Directory for state files
HARMONIA_DB_URL=                    # Optional database URL for state storage

# Performance settings
HARMONIA_MAX_CONCURRENT_TASKS=10    # Maximum concurrent tasks per workflow
HARMONIA_CHECKPOINT_INTERVAL=60     # Checkpoint interval in seconds
```

## Error Handling

### Client-Side Error Handling

```python
from harmonia.client import (
    get_harmonia_client,
    ComponentError,
    ComponentNotFoundError,
    CapabilityNotFoundError,
    CapabilityInvocationError,
    ComponentUnavailableError
)

async def error_handling_example():
    try:
        client = await get_harmonia_client()
        
        try:
            # Execute workflow
            execution = await client.execute_workflow(
                workflow_id="workflow-uuid-here"
            )
            
            # Get status
            status = await client.get_workflow_status(
                execution_id=execution["execution_id"]
            )
            
        except ComponentNotFoundError:
            print("Harmonia component not found - check if it's registered")
        except CapabilityNotFoundError:
            print("Requested capability not available in Harmonia")
        except CapabilityInvocationError as e:
            print(f"Error invoking capability: {e}")
        except ComponentUnavailableError:
            print("Harmonia component is unavailable")
        except ComponentError as e:
            print(f"Generic component error: {e}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")
```

### Task Error Handling

When implementing task handlers, follow these guidelines:

```python
async def handle_task(task_id, task_input):
    try:
        # Main task logic
        result = process_data(task_input)
        
        # Return success result
        return {
            "status": "success",
            "result": result,
            "metadata": {
                "processing_time": elapsed_time,
                "records_processed": record_count
            }
        }
        
    except ValueError as e:
        # Input validation error
        return {
            "status": "error",
            "error_type": "validation_error",
            "error_message": str(e),
            "is_retriable": False  # Don't retry validation errors
        }
        
    except ConnectionError as e:
        # Transient error that can be retried
        return {
            "status": "error",
            "error_type": "connection_error",
            "error_message": str(e),
            "is_retriable": True  # Allow retry for connectivity issues
        }
        
    except Exception as e:
        # Unexpected error
        return {
            "status": "error",
            "error_type": "internal_error",
            "error_message": str(e),
            "is_retriable": False
        }
```

## Debugging and Monitoring

### Workflow Monitoring

```python
import asyncio
from harmonia.client import get_harmonia_client

async def monitor_workflow(execution_id):
    client = await get_harmonia_client()
    
    # Get execution summary
    summary = await client.get_workflow_summary(execution_id)
    print(f"Workflow: {summary['workflow_name']} ({summary['status']})")
    print(f"Progress: {summary['completed_tasks']}/{summary['task_count']} tasks")
    
    # Get detailed status including task states
    status = await client.get_workflow_status(execution_id)
    
    print("\nTask Status:")
    for task_id, task_status in status.get("task_statuses", {}).items():
        state = task_status["status"]
        duration = task_status.get("duration", "N/A")
        print(f"  {task_id}: {state} (Duration: {duration})")
        
        if state == "failed" and "error" in task_status:
            print(f"    Error: {task_status['error']}")
        
    # Get execution metrics
    metrics = await client.get_workflow_metrics(execution_id)
    
    print("\nMetrics:")
    print(f"  Total Duration: {metrics.get('total_duration', 'N/A')}")
    print(f"  Average Task Duration: {metrics.get('average_task_duration', 'N/A')}")
    print(f"  Retry Count: {metrics.get('total_retries', 0)}")
```

### Event Logging

```python
import logging
import json

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("workflow_monitor")

# Event handler functions
def log_workflow_event(event):
    """Log a workflow event."""
    event_type = event["event_type"]
    execution_id = event["execution_id"]
    timestamp = event["timestamp"]
    
    if event_type.startswith("workflow_"):
        logger.info(f"Workflow {execution_id} {event_type.replace('workflow_', '')}")
    elif event_type.startswith("task_"):
        task_id = event.get("task_id", "unknown")
        logger.info(f"Task {task_id} in workflow {execution_id} {event_type.replace('task_', '')}")
    else:
        logger.info(f"Event {event_type} for workflow {execution_id}")
    
    # Log detail for debugging
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Event details: {json.dumps(event)}")
```

## Security Considerations

### Authentication

Harmonia integrates with Hermes for component authentication. When making requests to Harmonia, you should include appropriate authorization headers:

```python
from harmonia.client import get_harmonia_client, SecurityContext

async def authenticated_request():
    # Create security context
    security_context = SecurityContext(
        auth_token="your_token_here",
        auth_type="Bearer"
    )
    
    # Get client with security context
    client = await get_harmonia_client(
        security_context=security_context
    )
    
    # Now operations will include authentication
    workflow = await client.create_workflow(...)
```

### Input Validation

Always validate inputs to prevent injection attacks:

```python
def validate_workflow_input(input_data):
    """Validate workflow input data."""
    if not isinstance(input_data, dict):
        raise ValueError("Input must be a dictionary")
    
    # Validate specific fields
    if "command" in input_data:
        command = input_data["command"]
        if not isinstance(command, str):
            raise ValueError("Command must be a string")
        
        # Check for shell injection patterns
        if any(char in command for char in ";&|`$()"): 
            raise ValueError("Command contains potentially unsafe characters")
    
    # Validate nested objects
    if "options" in input_data and isinstance(input_data["options"], dict):
        validate_options(input_data["options"])
    
    return input_data  # Return validated input
```

### Sensitive Data Handling

Be careful with sensitive data in workflows:

```python
# Masking sensitive data in logging and events
def mask_sensitive_data(data):
    """Mask sensitive data for logging."""
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if key.lower() in ("password", "api_key", "secret", "token", "credential"):
                masked[key] = "**REDACTED**"
            elif isinstance(value, (dict, list)):
                masked[key] = mask_sensitive_data(value)
            else:
                masked[key] = value
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    else:
        return data
```

### Resource Limits

Implement resource limits to prevent abuse:

```python
# Environment variables for resource limits
MAX_WORKFLOW_SIZE = int(os.environ.get("HARMONIA_MAX_WORKFLOW_SIZE", "1048576"))  # 1MB
MAX_TASK_COUNT = int(os.environ.get("HARMONIA_MAX_TASK_COUNT", "100"))
MAX_EXECUTION_TIME = int(os.environ.get("HARMONIA_MAX_EXECUTION_TIME", "3600"))  # 1 hour

# Validation function
def validate_workflow_size(workflow_definition):
    """Validate workflow size and complexity."""
    # Check total serialized size
    serialized = json.dumps(workflow_definition)
    if len(serialized) > MAX_WORKFLOW_SIZE:
        raise ValueError(f"Workflow definition exceeds maximum size of {MAX_WORKFLOW_SIZE} bytes")
    
    # Check task count
    if len(workflow_definition.get("tasks", {})) > MAX_TASK_COUNT:
        raise ValueError(f"Workflow exceeds maximum task count of {MAX_TASK_COUNT}")
    
    # Additional validation as needed
    return True
```