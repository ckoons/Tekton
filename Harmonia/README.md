# Harmonia

## Overview

Harmonia is the workflow orchestration engine for the Tekton ecosystem. It coordinates complex multi-component workflows, manages state persistence, and provides robust error handling and recovery mechanisms for reliable task execution.

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

## Quick Start

```bash
# Install Harmonia
cd Harmonia
pip install -e .

# Start the Harmonia server
python -m harmonia.api.app
# Or use the launch script
./scripts/tekton-launch --components harmonia

# Use the CLI
harmonia workflow list
harmonia execution status <execution-id>
harmonia template create --from-workflow <workflow-id>
```

## Configuration

Harmonia uses the standard Tekton configuration system with TektonEnviron.

### Environment Variables

```bash
# Harmonia-specific settings (managed by TektonEnviron)
HARMONIA_PORT=8002                    # API port (default)
HARMONIA_AI_PORT=45002                # CI specialist port
HARMONIA_DATA_DIR=~/.harmonia         # Data directory
HARMONIA_MAX_CONCURRENT_WORKFLOWS=10  # Concurrent limit

# Workflow settings
HARMONIA_DEFAULT_TIMEOUT=3600         # Default task timeout (seconds)
HARMONIA_RETRY_MAX_ATTEMPTS=3         # Max retry attempts
HARMONIA_CHECKPOINT_INTERVAL=300      # Auto-checkpoint interval
```

### Database Configuration

Harmonia uses Hermes database services for state persistence:
- Document database for workflow state storage
- Key-value store for metadata and quick lookups
- Automatic fallback to file-based storage if Hermes is unavailable

### Configuration File

Create `.env.harmonia` for persistent settings:

```bash
# Execution policies
ENABLE_AUTO_RETRY=true
ENABLE_CHECKPOINTS=true
ENABLE_PARALLEL_EXECUTION=true

# Resource limits
MAX_WORKFLOW_DEPTH=10
MAX_TASK_DURATION=7200
```

## API Reference

### REST API Endpoints

- `POST /api/workflows` - Create a new workflow
- `GET /api/workflows` - List all workflows
- `GET /api/workflows/{id}` - Get workflow details
- `POST /api/executions` - Execute a workflow
- `GET /api/executions/{id}` - Get execution status
- `POST /api/executions/{id}/pause` - Pause execution
- `POST /api/executions/{id}/resume` - Resume execution
- `POST /api/templates` - Create workflow template
- `POST /api/checkpoints` - Create checkpoint
- `GET /api/status` - Get system status

### WebSocket Endpoints

- `/ws/executions/{id}` - Real-time execution updates
- `/ws/events` - Global workflow events

### Server-Sent Events

- `/events/executions/{id}` - Execution event stream

For detailed API documentation, run the server and visit `/docs`.

## Integration Points

Harmonia seamlessly integrates with:

- **Hermes**: Service discovery and event distribution
- **Ergon**: Agent-based task execution
- **Engram**: Workflow state persistence
- **Prometheus**: Strategic workflow planning
- **CI Specialists**: Harmonia CI for workflow optimization

### Example Integration

```python
from harmonia.client import HarmoniaClient

client = HarmoniaClient(host="localhost", port=8008)

# Create multi-component workflow
workflow = client.create_workflow(
    name="data_processing_pipeline",
    tasks=[
        {
            "name": "fetch_data",
            "component": "ergon",
            "action": "fetch_from_api",
            "input": {"url": "https://api.example.com/data"}
        },
        {
            "name": "analyze",
            "component": "apollo",
            "action": "analyze_metrics",
            "input": {"data": "${tasks.fetch_data.output}"},
            "depends_on": ["fetch_data"]
        },
        {
            "name": "store",
            "component": "engram",
            "action": "store_results",
            "input": {"results": "${tasks.analyze.output}"},
            "depends_on": ["analyze"]
        }
    ]
)

# Execute with monitoring
execution = client.execute_workflow(workflow.id)
client.monitor_execution(execution.id)
```

## Troubleshooting

### Common Issues

#### 1. Workflow Stuck in Running State
**Symptoms**: Workflow shows as running but no progress

**Solutions**:
```bash
# Check task status
harmonia execution tasks <execution-id>

# Force checkpoint
harmonia checkpoint create <execution-id>

# Retry failed tasks
harmonia execution retry <execution-id>
```

#### 2. Component Communication Failures
**Symptoms**: Tasks fail with connection errors

**Solutions**:
```bash
# Verify component registration
harmonia components list

# Test component connectivity
harmonia components test <component-name>

# Re-register with Hermes
harmonia register
```

#### 3. State Recovery Issues
**Symptoms**: Cannot restore from checkpoint

**Solutions**:
```bash
# List available checkpoints
harmonia checkpoint list --execution <execution-id>

# Validate checkpoint
harmonia checkpoint validate <checkpoint-id>

# Force state rebuild
harmonia state rebuild <execution-id>
```

### Performance Tuning

- Adjust concurrent workflow limits based on resources
- Enable parallel task execution for independent tasks
- Configure appropriate checkpoint intervals
- Use workflow templates for repeated patterns

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

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=harmonia tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

### Debug Mode

```bash
# Enable debug logging
export HARMONIA_DEBUG=true
export HARMONIA_LOG_LEVEL=DEBUG

# Run with verbose output
python -m harmonia.api.app --debug
```

### Workflow Development

1. Use templates for reusable patterns
2. Test workflows in isolation first
3. Enable checkpoints for long-running workflows
4. Use parameter validation
5. Implement proper error handling

## Related Documentation

- [Workflow Templates Guide](/MetaData/ComponentDocumentation/Harmonia/TEMPLATES_GUIDE.md)
- [State Management](/MetaData/ComponentDocumentation/Harmonia/STATE_MANAGEMENT.md)
- [Component Integration](/MetaData/ComponentDocumentation/Harmonia/INTEGRATION_GUIDE.md)
- [API Reference](/Harmonia/docs/api_reference.md)
## UI Integration

Harmonia includes a comprehensive web interface integrated with Hephaestus:

### Features
- **Workflows Tab**: View, create, and manage workflow definitions
- **Templates Tab**: Browse and use workflow templates
- **Executions Tab**: Monitor running and completed executions
- **Monitor Tab**: Real-time workflow monitoring and metrics
- **Workflow Chat**: AI-assisted workflow creation and debugging

### Accessing the UI
1. Start Hephaestus UI server
2. Navigate to the Harmonia component
3. All workflow operations are available through the interface

### API Integration
The UI connects to the following endpoints:
- `GET/POST /api/workflows` - Workflow management
- `GET/POST /api/templates` - Template operations
- `GET /api/executions` - Execution monitoring
- `WebSocket /ws/executions/{id}` - Real-time updates

## Recent Updates (Renovation Sprint)

### Configuration
- Migrated from direct os.environ to TektonEnviron
- Standardized port configuration (default: 8002)
- Removed hardcoded values

### Database Integration
- Integrated with Hermes database services via MCP
- Document database for workflow persistence
- Key-value store for metadata
- Automatic fallback to file storage

### UI Improvements
- Removed all mock data
- Connected to real backend endpoints
- Added proper loading and error states
- Semantic HTML structure with accessibility features
