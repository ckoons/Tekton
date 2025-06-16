# Synthesis User Guide

This guide provides practical instructions for users of the Synthesis component, focusing on day-to-day usage rather than technical implementation details.

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [Creating Execution Plans](#creating-execution-plans)
- [Managing Executions](#managing-executions)
- [Working with Integrations](#working-with-integrations)
- [Using the UI](#using-the-ui)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Introduction

Synthesis is the execution and integration engine for the Tekton ecosystem. It allows you to:

- Execute multi-step processes with dependencies
- Integrate with external systems via CLI, API, and other protocols
- Orchestrate workflows involving multiple Tekton components
- Monitor execution progress in real-time
- Manage integrations with external systems

This guide will help you make the most of Synthesis's capabilities in your daily workflow.

## Getting Started

### Installation

Synthesis is installed as part of the Tekton ecosystem:

```bash
# Clone the repository (if not already done)
git clone https://github.com/yourusername/Tekton.git
cd Tekton

# Run the setup script
cd Synthesis
./setup.sh

# Start Synthesis using the unified launcher
cd ..
./scripts/tekton-launch --components synthesis
```

### Verifying Installation

Check that Synthesis is running correctly:

```bash
# Check status using the tekton-status script
./scripts/tekton-status | grep synthesis

# Test the API directly
curl http://localhost:8009/health
```

You should see something like:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 1234,
  "components": {
    "api": "healthy",
    "execution_engine": "healthy",
    "storage": "healthy",
    "event_system": "healthy"
  }
}
```

### Configuration

Synthesis can be configured using environment variables or a configuration file:

```bash
# Set the port (default is 8009)
SYNTHESIS_PORT=9000 ./scripts/tekton-launch --components synthesis

# Set the storage type
SYNTHESIS_STORAGE_TYPE=file SYNTHESIS_STORAGE_PATH=/data/synthesis ./scripts/tekton-launch --components synthesis
```

## Creating Execution Plans

Execution plans define the steps that Synthesis will execute.

### Basic Structure

A basic plan consists of:

- A name and description
- One or more steps with unique IDs
- Optional dependencies between steps
- Optional variables

### Creating a Simple Plan

Here's a simple plan that executes two commands in sequence:

```bash
curl -X POST http://localhost:8009/api/plans \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Simple Two-Step Plan",
    "description": "A plan with two sequential steps",
    "steps": [
      {
        "id": "step1",
        "type": "command",
        "parameters": {
          "command": "echo \"Hello from step 1\""
        }
      },
      {
        "id": "step2",
        "type": "command",
        "parameters": {
          "command": "echo \"Processing data from step 1\""
        },
        "dependencies": ["step1"]
      }
    ]
  }'
```

### Step Types

Synthesis supports various step types:

#### Command Step

Executes a shell command:

```json
{
  "id": "command_step",
  "type": "command",
  "parameters": {
    "command": "ls -la /tmp",
    "working_directory": "/home/user",
    "timeout": 30
  }
}
```

#### API Step

Makes an HTTP request:

```json
{
  "id": "api_step",
  "type": "api",
  "parameters": {
    "method": "GET",
    "url": "https://api.example.com/data",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}"
    },
    "timeout": 30
  }
}
```

#### Function Step

Calls a registered Python function:

```json
{
  "id": "function_step",
  "type": "function",
  "parameters": {
    "function": "process_data",
    "args": {
      "input_data": "${api_step.response.body}",
      "options": {
        "normalize": true,
        "validate": true
      }
    }
  }
}
```

#### Condition Step

Executes steps conditionally:

```json
{
  "id": "condition_step",
  "type": "condition",
  "parameters": {
    "condition": "${api_step.response.status_code} == 200",
    "true_steps": [
      {
        "id": "success_step",
        "type": "command",
        "parameters": {
          "command": "echo \"API request succeeded\""
        }
      }
    ],
    "false_steps": [
      {
        "id": "error_step",
        "type": "command",
        "parameters": {
          "command": "echo \"API request failed\""
        }
      }
    ]
  },
  "dependencies": ["api_step"]
}
```

#### Loop Step

Iterates over items or repeats steps:

```json
{
  "id": "loop_step",
  "type": "loop",
  "parameters": {
    "type": "foreach",
    "items": "${api_step.response.body.items}",
    "item_variable": "current_item",
    "steps": [
      {
        "id": "process_item",
        "type": "command",
        "parameters": {
          "command": "echo \"Processing item ${current_item.id}: ${current_item.name}\""
        }
      }
    ]
  },
  "dependencies": ["api_step"]
}
```

#### Variable Step

Manipulates variables:

```json
{
  "id": "variable_step",
  "type": "variable",
  "parameters": {
    "operations": [
      {
        "operation": "set",
        "variable": "formatted_date",
        "value": "${new Date().toISOString()}"
      },
      {
        "operation": "set",
        "variable": "item_count",
        "value": "${api_step.response.body.items.length}"
      }
    ]
  }
}
```

#### LLM Step

Interacts with language models:

```json
{
  "id": "llm_step",
  "type": "llm",
  "parameters": {
    "model": "claude-3-haiku-20240307",
    "prompt": "Summarize the following data in 3 bullet points:\n\n${api_step.response.body}",
    "max_tokens": 500,
    "temperature": 0.7
  },
  "dependencies": ["api_step"]
}
```

### Using Dependencies

Steps can depend on other steps to create execution flows:

```json
{
  "steps": [
    {
      "id": "step1",
      "type": "command",
      "parameters": {
        "command": "echo \"Step 1\""
      }
    },
    {
      "id": "step2",
      "type": "command",
      "parameters": {
        "command": "echo \"Step 2\""
      }
    },
    {
      "id": "step3",
      "type": "command",
      "parameters": {
        "command": "echo \"Steps 1 and 2 completed\""
      },
      "dependencies": ["step1", "step2"]
    }
  ]
}
```

In this example, `step3` will only execute after both `step1` and `step2` have completed successfully, which can execute in parallel.

### Using Variables

Variables can be used for dynamic values:

```json
{
  "steps": [
    {
      "id": "step1",
      "type": "command",
      "parameters": {
        "command": "echo \"Hello, ${username}!\""
      }
    },
    {
      "id": "step2",
      "type": "command",
      "parameters": {
        "command": "echo \"Output from step1: ${step1.output}\""
      },
      "dependencies": ["step1"]
    }
  ],
  "variables": {
    "username": "John Doe",
    "environment": "production"
  }
}
```

Variables can come from:
- Predefined plan variables
- Step outputs (e.g., `${step1.output}`)
- Environment variables
- Execution context

### Variable Substitution

Synthesis supports various forms of variable substitution:

- Simple substitution: `${variable}`
- JSON path: `${response.data.items[0].id}`
- Expressions: `${count > 5 ? 'many' : 'few'}`
- Functions: `${new Date().toISOString()}`

## Managing Executions

Once you have created a plan, you can execute it and manage the execution.

### Executing a Plan

To execute a plan:

```bash
# Execute a plan by ID
curl -X POST http://localhost:8009/api/plans/your-plan-id/execute \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "username": "Jane Smith",
      "environment": "testing"
    },
    "metadata": {
      "tags": ["test", "example"],
      "created_by": "user1"
    }
  }'
```

You'll receive a response with the execution ID:

```json
{
  "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
  "status": "created",
  "created_at": "2025-05-01T10:15:30Z",
  "plan_id": "your-plan-id"
}
```

### Checking Execution Status

To check the status of an execution:

```bash
curl http://localhost:8009/api/executions/f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f
```

Response:

```json
{
  "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
  "status": "running",
  "created_at": "2025-05-01T10:15:30Z",
  "started_at": "2025-05-01T10:15:31Z",
  "plan_id": "your-plan-id",
  "steps": [
    {
      "id": "step1",
      "type": "command",
      "status": "completed",
      "started_at": "2025-05-01T10:15:31Z",
      "completed_at": "2025-05-01T10:15:32Z"
    },
    {
      "id": "step2",
      "type": "command",
      "status": "running",
      "started_at": "2025-05-01T10:15:32Z"
    }
  ]
}
```

### Controlling Executions

You can control running executions:

#### Pause an Execution

```bash
curl -X POST http://localhost:8009/api/executions/f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f/pause
```

#### Resume an Execution

```bash
curl -X POST http://localhost:8009/api/executions/f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f/resume
```

#### Cancel an Execution

```bash
curl -X POST http://localhost:8009/api/executions/f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f/cancel
```

### Viewing Execution Results

To view the results of a completed execution:

```bash
curl http://localhost:8009/api/executions/f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f
```

To view step outputs specifically:

```bash
curl http://localhost:8009/api/executions/f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f/steps
```

### Real-time Monitoring

For real-time updates, use the WebSocket interface:

```javascript
// JavaScript WebSocket example
const ws = new WebSocket('ws://localhost:8009/ws/executions/f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log(`Event: ${data.type}`, data);
};
```

## Working with Integrations

Synthesis provides integrations with external systems and other Tekton components.

### Listing Available Integrations

To list available integrations:

```bash
curl http://localhost:8009/api/integrations
```

Response:

```json
{
  "integrations": [
    {
      "id": "cli",
      "name": "Command Line",
      "description": "Execute commands on the local system",
      "capabilities": ["execute_command", "execute_script"]
    },
    {
      "id": "api",
      "name": "HTTP API",
      "description": "Make HTTP requests to external APIs",
      "capabilities": ["http_get", "http_post", "http_put", "http_delete"]
    },
    {
      "id": "prometheus",
      "name": "Prometheus",
      "description": "Integration with Prometheus planning component",
      "capabilities": ["get_plan", "update_execution_status"]
    }
  ]
}
```

### Viewing Integration Capabilities

To view the capabilities of a specific integration:

```bash
curl http://localhost:8009/api/integrations/cli/capabilities
```

Response:

```json
{
  "integration_id": "cli",
  "capabilities": [
    {
      "id": "execute_command",
      "name": "Execute Command",
      "description": "Execute a single command",
      "parameters": {
        "command": {
          "type": "string",
          "description": "The command to execute",
          "required": true
        },
        "working_directory": {
          "type": "string",
          "description": "The working directory for the command",
          "required": false
        },
        "timeout": {
          "type": "integer",
          "description": "Timeout in seconds",
          "required": false,
          "default": 60
        }
      }
    },
    {
      "id": "execute_script",
      "name": "Execute Script",
      "description": "Execute a multi-line script",
      "parameters": {
        "script": {
          "type": "string",
          "description": "The script to execute",
          "required": true
        },
        "interpreter": {
          "type": "string",
          "description": "The script interpreter",
          "required": false,
          "default": "bash"
        },
        "working_directory": {
          "type": "string",
          "description": "The working directory for the script",
          "required": false
        },
        "timeout": {
          "type": "integer",
          "description": "Timeout in seconds",
          "required": false,
          "default": 300
        }
      }
    }
  ]
}
```

### Testing an Integration

To test an integration capability directly:

```bash
curl -X POST http://localhost:8009/api/integrations/cli/capabilities/execute_command \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "command": "echo \"Testing integration\"",
      "working_directory": "/tmp",
      "timeout": 30
    }
  }'
```

Response:

```json
{
  "invocation_id": "c1d2e3f4-5g6h-7i8j-9k0l-m1n2o3p4q5r6",
  "integration_id": "cli",
  "capability_id": "execute_command",
  "status": "completed",
  "started_at": "2025-05-01T10:15:30Z",
  "completed_at": "2025-05-01T10:15:31Z",
  "duration_ms": 1000,
  "output": "Testing integration\n",
  "error": null
}
```

## Using the UI

Synthesis integrates with the Hephaestus UI system, providing a graphical interface for managing executions.

### Accessing the UI

The UI is available through Hephaestus:

1. Launch Hephaestus: `./scripts/tekton-launch --components hephaestus synthesis`
2. Open your browser: `http://localhost:8080`
3. Navigate to the Synthesis component

### UI Features

The Synthesis UI provides:

#### Execution Management

- Create new execution plans
- Execute existing plans
- Monitor execution progress
- View execution history
- Control running executions

#### Process Visualization

- View process flow as a graph
- See step dependencies
- Track execution progress visually
- Identify bottlenecks and issues

#### Integration Management

- View available integrations
- Test integration capabilities
- Configure integration settings
- Monitor integration usage

#### Real-time Monitoring

- See real-time execution updates
- View streaming step output
- Get immediate notification of errors
- Track execution metrics

### UI Walkthrough

1. **Create a Plan**:
   - Click "New Plan"
   - Enter name and description
   - Add steps using the step editor
   - Set dependencies using the graph view
   - Click "Save Plan"

2. **Execute a Plan**:
   - Select a plan from the list
   - Click "Execute"
   - Enter any variable values
   - Click "Start Execution"

3. **Monitor Execution**:
   - See real-time progress in the execution view
   - View step outputs by clicking on steps
   - Check execution logs for details
   - Use the timeline view to see execution history

4. **Manage Integrations**:
   - Navigate to the Integrations tab
   - Select an integration to view details
   - Test capabilities using the test panel
   - Configure settings using the configuration panel

## Advanced Features

Synthesis provides several advanced features for power users.

### Parallel Execution

Execute steps in parallel by omitting dependencies:

```json
{
  "steps": [
    {
      "id": "parallel_step_1",
      "type": "command",
      "parameters": {
        "command": "echo 'Parallel 1'"
      }
    },
    {
      "id": "parallel_step_2",
      "type": "command",
      "parameters": {
        "command": "echo 'Parallel 2'"
      }
    },
    {
      "id": "final_step",
      "type": "command",
      "parameters": {
        "command": "echo 'All parallel steps completed'"
      },
      "dependencies": ["parallel_step_1", "parallel_step_2"]
    }
  ]
}
```

### Conditional Execution

Use conditions to execute steps based on dynamic criteria:

```json
{
  "steps": [
    {
      "id": "check_environment",
      "type": "variable",
      "parameters": {
        "operations": [
          {
            "operation": "set",
            "variable": "is_production",
            "value": "${environment == 'production'}"
          }
        ]
      }
    },
    {
      "id": "production_step",
      "type": "command",
      "parameters": {
        "command": "echo 'Running in production mode'"
      },
      "condition": "${is_production}",
      "dependencies": ["check_environment"]
    },
    {
      "id": "non_production_step",
      "type": "command",
      "parameters": {
        "command": "echo 'Running in development mode'"
      },
      "condition": "${!is_production}",
      "dependencies": ["check_environment"]
    }
  ],
  "variables": {
    "environment": "development"
  }
}
```

### Error Handling

Implement error recovery with retry logic:

```json
{
  "steps": [
    {
      "id": "api_call",
      "type": "api",
      "parameters": {
        "method": "GET",
        "url": "https://api.example.com/data",
        "retry": {
          "max_attempts": 3,
          "initial_delay_ms": 1000,
          "backoff_factor": 2,
          "error_types": ["timeout", "server_error"]
        }
      }
    },
    {
      "id": "handle_success",
      "type": "command",
      "parameters": {
        "command": "echo 'API call succeeded'"
      },
      "condition": "${api_call.status == 'completed'}",
      "dependencies": ["api_call"]
    },
    {
      "id": "handle_error",
      "type": "command",
      "parameters": {
        "command": "echo 'API call failed after retries'"
      },
      "condition": "${api_call.status == 'failed'}",
      "dependencies": ["api_call"]
    }
  ]
}
```

### LLM-Powered Workflow Enhancements

Use LLMs to enhance workflows:

```json
{
  "steps": [
    {
      "id": "fetch_data",
      "type": "command",
      "parameters": {
        "command": "cat /tmp/data.json"
      }
    },
    {
      "id": "analyze_data",
      "type": "llm",
      "parameters": {
        "model": "claude-3-sonnet-20240229",
        "prompt": "Analyze this JSON data and identify any anomalies or issues:\n\n${fetch_data.output}",
        "max_tokens": 1000
      },
      "dependencies": ["fetch_data"]
    },
    {
      "id": "generate_commands",
      "type": "llm",
      "parameters": {
        "model": "claude-3-sonnet-20240229",
        "prompt": "Based on the analysis, generate a shell command to fix any identified issues:\n\n${analyze_data.output}",
        "max_tokens": 500
      },
      "dependencies": ["analyze_data"]
    },
    {
      "id": "execute_fix",
      "type": "command",
      "parameters": {
        "command": "${generate_commands.output}"
      },
      "dependencies": ["generate_commands"]
    }
  ]
}
```

### Event Subscriptions

Subscribe to events for integration with other systems:

```bash
curl -X POST http://localhost:8009/api/events/subscriptions \
  -H "Content-Type: application/json" \
  -d '{
    "types": ["execution_completed"],
    "filter": {
      "tags": ["important"]
    },
    "callback_url": "https://your-service.example.com/webhook",
    "expiration": "2025-12-31T23:59:59Z"
  }'
```

### Custom Functions

Register custom Python functions and use them in workflows:

```python
# Register a custom function
from synthesis.client import SynthesisClient

async def register_function():
    client = SynthesisClient()
    
    await client.register_function(
        name="process_data",
        function=lambda data, options: {
            "processed": True,
            "input_size": len(data),
            "normalized": data.upper() if options.get("normalize") else data
        }
    )
```

Then use it in a plan:

```json
{
  "steps": [
    {
      "id": "get_data",
      "type": "command",
      "parameters": {
        "command": "echo 'sample data'"
      }
    },
    {
      "id": "process",
      "type": "function",
      "parameters": {
        "function": "process_data",
        "args": {
          "data": "${get_data.output}",
          "options": {
            "normalize": true
          }
        }
      },
      "dependencies": ["get_data"]
    }
  ]
}
```

## Troubleshooting

Common issues and their solutions:

### Execution Fails to Start

**Problem**: Execution created but doesn't start running.

**Solutions**:
1. Check Synthesis service status: `./scripts/tekton-status | grep synthesis`
2. Verify the execution was created properly: `curl http://localhost:8009/api/executions/{execution_id}`
3. Check for errors in the logs: `tail -f /var/log/tekton/synthesis.log`
4. Ensure required integrations are available

### Step Fails with Error

**Problem**: A step in the execution fails with an error.

**Solutions**:
1. Check the step details: `curl http://localhost:8009/api/executions/{execution_id}/steps/{step_id}`
2. Examine the error message for specific issues
3. Verify external services are available (for API steps)
4. Check if commands exist and have correct permissions (for command steps)
5. Validate variable substitutions in the step

### Performance Issues

**Problem**: Executions are slow or resource-intensive.

**Solutions**:
1. Use parallel execution where possible for independent steps
2. Optimize loops to reduce redundant operations
3. Consider smaller, more focused plans instead of large monolithic ones
4. Use appropriate timeouts for external operations
5. Implement caching for repeated operations

### Integration Problems

**Problem**: Issues with external system integrations.

**Solutions**:
1. Test the integration directly: `curl -X POST http://localhost:8009/api/integrations/{integration_id}/capabilities/{capability_id}`
2. Check connectivity to the external system
3. Verify authentication credentials
4. Check for rate limiting or access restrictions
5. Examine detailed error messages from the integration

### UI Issues

**Problem**: UI doesn't show executions or components correctly.

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify WebSocket connectivity
3. Ensure Hephaestus is properly configured with Synthesis
4. Try clearing browser cache and refreshing
5. Confirm URL paths match the Single Port Architecture pattern

## Best Practices

Follow these best practices for effective use of Synthesis:

### Plan Design

1. **Keep Plans Focused**: Create smaller, focused plans rather than large monolithic ones
2. **Use Dependencies Wisely**: Only require dependencies where truly needed
3. **Leverage Parallel Execution**: Run independent steps in parallel
4. **Implement Error Handling**: Add appropriate error handling and recovery
5. **Use Clear Step IDs**: Choose descriptive, consistent step IDs

### Variables

1. **Prefer Plan Variables**: Define common values as plan variables
2. **Use Explicit Outputs**: Reference step outputs explicitly with full paths
3. **Validate Inputs**: Add validation steps for critical variables
4. **Default Values**: Provide sensible defaults for optional variables
5. **Scope Management**: Keep variable usage clear and well-scoped

### Integration

1. **Test in Isolation**: Test integration capabilities independently
2. **Handle Errors**: Implement proper error handling for external systems
3. **Set Timeouts**: Always set appropriate timeouts for external calls
4. **Credential Management**: Use secure methods for credential storage
5. **Validate Responses**: Add validation for external system responses

### Execution Management

1. **Monitor Actively**: Use WebSocket for real-time monitoring
2. **Use Tags**: Apply consistent tags to executions for filtering
3. **Preserve History**: Keep execution history for analysis
4. **Implement Retries**: Use retry mechanisms for transient failures
5. **Limit Concurrency**: Control how many executions run simultaneously

### UI Usage

1. **Leverage Visualization**: Use the graph view to understand workflow
2. **Save Templates**: Create and save plan templates for common tasks
3. **Export/Import**: Export valuable plans for backup and sharing
4. **Organize by Tags**: Use consistent tagging to organize executions
5. **Monitor in Real-time**: Use the real-time view for important executions