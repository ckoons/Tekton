# Harmonia - Workflow Orchestration Engine

![Harmonia](../../../images/icon.jpg)

## Overview

Harmonia is the workflow orchestration engine for the Tekton ecosystem. It coordinates complex workflows across components, manages state persistence, and handles task sequencing. Named after the Greek goddess of harmony and concord, Harmonia brings together various Tekton components to work in unison.

## Key Features

- **Workflow Definition and Execution**: Create and run complex workflows with dependencies
- **Cross-Component Task Orchestration**: Coordinate tasks across various Tekton components
- **State Management and Persistence**: Save and resume workflow state, create checkpoints
- **Template System**: Create reusable workflow templates with parameter substitution
- **Error Handling and Recovery**: Robust retry mechanisms and failure recovery
- **Event-Driven Architecture**: Subscribe to workflow events via WebSockets and SSE
- **Checkpoint/Resume Capability**: Create snapshots of workflow state and resume from them
- **Single Port Architecture**: All APIs accessible through a unified port following Tekton standards
- **Real-time Monitoring**: Monitor workflow execution with real-time updates
- **Cross-Component Integration**: Seamless integration with other Tekton components

## Architecture

Harmonia follows a modular architecture:

1. **Core Engine**: The workflow execution engine and state management
2. **API Layer**: HTTP REST API, WebSocket, and Event Stream endpoints
3. **Storage Layer**: Persistent storage for workflows, state, and templates
4. **Component Registry**: Integration with other Tekton components
5. **Event System**: Real-time event propagation for workflow monitoring

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Tekton.git
cd Tekton/Harmonia

# Run setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### Starting Harmonia

```bash
# Start Harmonia with default settings
./run_harmonia.sh

# Start with custom settings
./run_harmonia.sh --port 8002 --data-dir ~/.harmonia --log-level DEBUG
```

### Register with Hermes

```bash
# Register Harmonia with Hermes
python register_with_hermes.py --verify

# Or use the registration script directly
python -m harmonia.scripts.register_with_hermes
```

### Using Harmonia with Tekton

```bash
# Start with Tekton launch script
../scripts/tekton-launch --components harmonia
```

## API Usage

Harmonia provides a comprehensive API for workflow management. Here are some examples:

### Creating a Workflow

```bash
curl -X POST http://localhost:8002/api/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example_workflow",
    "description": "Example workflow",
    "tasks": {
      "task1": {
        "name": "task1",
        "component": "ergon",
        "action": "execute_command",
        "input": {
          "command": "echo Hello World"
        }
      },
      "task2": {
        "name": "task2",
        "component": "prometheus",
        "action": "analyze_results",
        "input": {
          "data": "${tasks.task1.output.result}"
        },
        "depends_on": ["task1"]
      }
    }
  }'
```

### Executing a Workflow

```bash
curl -X POST http://localhost:8002/api/executions \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "workflow-uuid-here",
    "input": {
      "parameter1": "value1"
    }
  }'
```

### Getting Workflow Status

```bash
curl http://localhost:8002/api/executions/execution-uuid-here
```

## Client Usage

Harmonia provides a Python client for easy integration:

```python
import asyncio
from harmonia.client import get_harmonia_client

async def main():
    # Get Harmonia client
    client = await get_harmonia_client()
    
    # Create a workflow
    workflow = await client.create_workflow(
        name="example_workflow",
        description="Example workflow",
        tasks=[
            {
                "name": "task1",
                "component": "ergon",
                "action": "execute_command",
                "input": {"command": "echo Hello World"}
            },
            {
                "name": "task2",
                "component": "prometheus",
                "action": "analyze_results",
                "input": {"data": "${tasks.task1.output.result}"},
                "depends_on": ["task1"]
            }
        ]
    )
    
    # Execute the workflow
    execution = await client.execute_workflow(
        workflow_id=workflow["workflow_id"]
    )
    
    # Get workflow status
    status = await client.get_workflow_status(
        execution_id=execution["execution_id"]
    )
    
    print(f"Workflow status: {status['status']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## WebSocket API

Harmonia provides a WebSocket API for real-time workflow execution events:

```javascript
// Connect to workflow execution events
const ws = new WebSocket('ws://localhost:8002/ws/executions/execution-uuid-here');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Event: ${data.event_type}`, data);
};

// Send messages to the WebSocket
ws.send(JSON.stringify({
  type: 'ping'
}));
```

## Server-Sent Events (SSE)

For server-sent events:

```javascript
// Connect to workflow execution events
const eventSource = new EventSource('http://localhost:8002/events/executions/execution-uuid-here');

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
```

## Workflow Templates

Harmonia supports reusable workflow templates:

```python
import asyncio
from harmonia.client import get_harmonia_client

async def main():
    client = await get_harmonia_client()
    
    # Create a template from an existing workflow
    template = await client.create_template(
        name="process_data_template",
        workflow_definition_id="workflow-uuid-here",
        parameters={
            "input_file": {
                "type": "string",
                "required": True,
                "description": "Input file path"
            },
            "output_format": {
                "type": "string",
                "required": False,
                "default": "json",
                "description": "Output format"
            }
        }
    )
    
    # Instantiate the template
    workflow = await client.instantiate_template(
        template_id=template["template_id"],
        parameter_values={
            "input_file": "/path/to/data.csv",
            "output_format": "xml"
        }
    )
    
    # Execute the instantiated workflow
    await client.execute_workflow(workflow_id=workflow["workflow_id"])

if __name__ == "__main__":
    asyncio.run(main())
```

## Checkpoints and Recovery

Harmonia supports checkpointing and recovery:

```python
import asyncio
from harmonia.client import get_harmonia_client, get_harmonia_state_client

async def main():
    client = await get_harmonia_client()
    state_client = await get_harmonia_state_client()
    
    # Create checkpoint for a running workflow
    checkpoint = await state_client.create_checkpoint(
        execution_id="execution-uuid-here"
    )
    
    # Restore from checkpoint
    new_execution = await client.restore_from_checkpoint(
        checkpoint_id=checkpoint["checkpoint_id"]
    )
    
    print(f"Restored workflow: {new_execution['execution_id']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Integration with Other Components

Harmonia integrates with other Tekton components:

- **Hermes**: Service discovery and registration
- **Engram**: Long-term memory and state persistence
- **Rhetor**: LLM interactions for workflow decisions
- **Prometheus**: Metrics and monitoring
- **Synthesis**: Task execution and integration
- **Ergon**: Command execution and automation

## Documentation

For detailed documentation, see the following resources:

- [Implementation Guide](./IMPLEMENTATION_GUIDE.md) - Detailed implementation guide
- [Project Structure](./PROJECT_STRUCTURE.md) - Project structure and organization