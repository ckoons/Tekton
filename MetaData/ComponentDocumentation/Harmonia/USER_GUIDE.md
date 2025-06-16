# Harmonia User Guide

This guide provides practical instructions for users of the Harmonia workflow orchestration component, focusing on day-to-day usage rather than technical implementation details.

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [Workflow Fundamentals](#workflow-fundamentals)
- [Creating Workflows](#creating-workflows)
- [Executing Workflows](#executing-workflows)
- [Working with Templates](#working-with-templates)
- [Using Expressions](#using-expressions)
- [State Management](#state-management)
- [Component Integration](#component-integration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Introduction

Harmonia is the workflow orchestration component of the Tekton ecosystem, designed to automate complex processes and coordinate activities across multiple components. It enables you to define, execute, and monitor workflows with conditional logic, parallel execution, and dynamic behavior based on system state.

## Getting Started

### Installation and Setup

Harmonia is typically installed as part of the Tekton ecosystem:

```bash
# Launch Harmonia using the Tekton launcher
./scripts/tekton-launch --components harmonia

# Verify Harmonia is running
./scripts/tekton-status | grep harmonia
```

### Accessing Harmonia

Harmonia provides multiple interfaces:

1. **REST API**: For programmatic access
   ```
   http://localhost:8007/api/
   ```

2. **Web UI**: Through the Hephaestus component
   ```
   http://localhost:8080/
   ```
   Then navigate to the Harmonia component in the sidebar.

3. **Python Client**: For application integration
   ```python
   from harmonia.client import HarmoniaClient
   
   client = HarmoniaClient("http://localhost:8007")
   ```

## Workflow Fundamentals

### Understanding Workflows

In Harmonia, workflows are structured processes consisting of:

- **Steps**: Individual actions or operations to perform
- **Transitions**: Connections between steps that define the flow
- **Conditions**: Logic that determines which transitions to follow
- **Actions**: The actual operations performed by steps
- **State**: Data that is passed between steps and persisted
- **Events**: Triggers that can start workflows or steps

### Key Concepts

- **Workflow Definition**: The blueprint for a workflow, defining its steps, transitions, and logic
- **Workflow Instance**: A running or completed execution of a workflow definition
- **Workflow Template**: A reusable pattern for creating workflow definitions
- **Component**: A Tekton component that performs actions within a workflow
- **Expression**: Dynamic logic evaluated at runtime to make decisions or transform data

## Creating Workflows

### Creating a Basic Workflow

#### Using the API:
```bash
curl -X POST http://localhost:8007/api/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Simple Approval Workflow",
    "description": "Basic workflow with approval step",
    "steps": [
      {
        "id": "start",
        "type": "start",
        "transitions": [
          {
            "to": "request_approval",
            "condition": "true"
          }
        ]
      },
      {
        "id": "request_approval",
        "type": "action",
        "component": "ergon",
        "action": "create_task",
        "parameters": {
          "title": "Review Request",
          "description": "Please review the request and approve or reject",
          "priority": "high"
        },
        "transitions": [
          {
            "to": "check_approval",
            "condition": "true"
          }
        ]
      },
      {
        "id": "check_approval",
        "type": "decision",
        "transitions": [
          {
            "to": "approved",
            "condition": "state.task.status == \"approved\""
          },
          {
            "to": "rejected",
            "condition": "state.task.status == \"rejected\""
          }
        ]
      },
      {
        "id": "approved",
        "type": "action",
        "component": "ergon",
        "action": "log_outcome",
        "parameters": {
          "message": "Request was approved",
          "status": "success"
        },
        "transitions": [
          {
            "to": "end",
            "condition": "true"
          }
        ]
      },
      {
        "id": "rejected",
        "type": "action",
        "component": "ergon",
        "action": "log_outcome",
        "parameters": {
          "message": "Request was rejected",
          "status": "failure"
        },
        "transitions": [
          {
            "to": "end",
            "condition": "true"
          }
        ]
      },
      {
        "id": "end",
        "type": "end"
      }
    ]
  }'
```

#### Using the Python Client:
```python
from harmonia.client import HarmoniaClient

async def create_workflow_example():
    client = HarmoniaClient("http://localhost:8007")
    
    workflow_definition = {
        "name": "Simple Approval Workflow",
        "description": "Basic workflow with approval step",
        "steps": [
            {
                "id": "start",
                "type": "start",
                "transitions": [
                    {
                        "to": "request_approval",
                        "condition": "true"
                    }
                ]
            },
            {
                "id": "request_approval",
                "type": "action",
                "component": "ergon",
                "action": "create_task",
                "parameters": {
                    "title": "Review Request",
                    "description": "Please review the request and approve or reject",
                    "priority": "high"
                },
                "transitions": [
                    {
                        "to": "check_approval",
                        "condition": "true"
                    }
                ]
            },
            {
                "id": "check_approval",
                "type": "decision",
                "transitions": [
                    {
                        "to": "approved",
                        "condition": "state.task.status == \"approved\""
                    },
                    {
                        "to": "rejected",
                        "condition": "state.task.status == \"rejected\""
                    }
                ]
            },
            {
                "id": "approved",
                "type": "action",
                "component": "ergon",
                "action": "log_outcome",
                "parameters": {
                    "message": "Request was approved",
                    "status": "success"
                },
                "transitions": [
                    {
                        "to": "end",
                        "condition": "true"
                    }
                ]
            },
            {
                "id": "rejected",
                "type": "action",
                "component": "ergon",
                "action": "log_outcome",
                "parameters": {
                    "message": "Request was rejected",
                    "status": "failure"
                },
                "transitions": [
                    {
                        "to": "end",
                        "condition": "true"
                    }
                ]
            },
            {
                "id": "end",
                "type": "end"
            }
        ]
    }
    
    workflow_id = await client.create_workflow(workflow_definition)
    
    print(f"Created workflow with ID: {workflow_id}")
```

### Creating a Workflow with Parallel Steps

#### Using the API:
```bash
curl -X POST http://localhost:8007/api/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Parallel Processing Workflow",
    "description": "Workflow with parallel execution steps",
    "steps": [
      {
        "id": "start",
        "type": "start",
        "transitions": [
          {
            "to": "fork",
            "condition": "true"
          }
        ]
      },
      {
        "id": "fork",
        "type": "fork",
        "branches": ["process_a", "process_b", "process_c"],
        "transitions": []
      },
      {
        "id": "process_a",
        "type": "action",
        "component": "ergon",
        "action": "process_data",
        "parameters": {
          "data_set": "a",
          "options": {
            "method": "analysis_1"
          }
        },
        "transitions": [
          {
            "to": "join",
            "condition": "true"
          }
        ]
      },
      {
        "id": "process_b",
        "type": "action",
        "component": "ergon",
        "action": "process_data",
        "parameters": {
          "data_set": "b",
          "options": {
            "method": "analysis_2"
          }
        },
        "transitions": [
          {
            "to": "join",
            "condition": "true"
          }
        ]
      },
      {
        "id": "process_c",
        "type": "action",
        "component": "ergon",
        "action": "process_data",
        "parameters": {
          "data_set": "c",
          "options": {
            "method": "analysis_3"
          }
        },
        "transitions": [
          {
            "to": "join",
            "condition": "true"
          }
        ]
      },
      {
        "id": "join",
        "type": "join",
        "join_type": "all",
        "sources": ["process_a", "process_b", "process_c"],
        "transitions": [
          {
            "to": "combine_results",
            "condition": "true"
          }
        ]
      },
      {
        "id": "combine_results",
        "type": "action",
        "component": "ergon",
        "action": "combine_data",
        "parameters": {
          "results": [
            "state.process_a.result",
            "state.process_b.result",
            "state.process_c.result"
          ]
        },
        "transitions": [
          {
            "to": "end",
            "condition": "true"
          }
        ]
      },
      {
        "id": "end",
        "type": "end"
      }
    ]
  }'
```

### Creating a Workflow with Error Handling

#### Using the API:
```bash
curl -X POST http://localhost:8007/api/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Error Handling Workflow",
    "description": "Workflow with error handling and retry logic",
    "steps": [
      {
        "id": "start",
        "type": "start",
        "transitions": [
          {
            "to": "process_data",
            "condition": "true"
          }
        ]
      },
      {
        "id": "process_data",
        "type": "action",
        "component": "ergon",
        "action": "process_data",
        "parameters": {
          "data_source": "external_api",
          "options": {
            "timeout": 30
          }
        },
        "retry": {
          "max_attempts": 3,
          "delay_seconds": 5,
          "backoff_multiplier": 2
        },
        "transitions": [
          {
            "to": "success",
            "condition": "state.process_data.success == true"
          },
          {
            "to": "handle_error",
            "condition": "state.process_data.success == false"
          }
        ]
      },
      {
        "id": "handle_error",
        "type": "action",
        "component": "ergon",
        "action": "log_error",
        "parameters": {
          "error": "state.process_data.error",
          "severity": "high"
        },
        "transitions": [
          {
            "to": "notify_admin",
            "condition": "true"
          }
        ]
      },
      {
        "id": "notify_admin",
        "type": "action",
        "component": "ergon",
        "action": "create_task",
        "parameters": {
          "title": "Data Processing Failed",
          "description": "The data processing operation failed after multiple attempts. Error: ${state.process_data.error}",
          "priority": "critical",
          "assignee": "admin"
        },
        "transitions": [
          {
            "to": "end",
            "condition": "true"
          }
        ]
      },
      {
        "id": "success",
        "type": "action",
        "component": "ergon",
        "action": "log_outcome",
        "parameters": {
          "message": "Data processing completed successfully",
          "status": "success"
        },
        "transitions": [
          {
            "to": "end",
            "condition": "true"
          }
        ]
      },
      {
        "id": "end",
        "type": "end"
      }
    ]
  }'
```

## Executing Workflows

### Starting a Workflow

#### Using the API:
```bash
curl -X POST http://localhost:8007/api/workflows/workflow_id_here/execute \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "request_id": "REQ-12345",
      "requester": "user@example.com",
      "details": {
        "type": "access_request",
        "resource": "database_x"
      }
    }
  }'
```

#### Using the Python Client:
```python
from harmonia.client import HarmoniaClient

async def execute_workflow_example():
    client = HarmoniaClient("http://localhost:8007")
    
    input_data = {
        "request_id": "REQ-12345",
        "requester": "user@example.com",
        "details": {
            "type": "access_request",
            "resource": "database_x"
        }
    }
    
    instance_id = await client.execute_workflow(
        workflow_id="workflow_id_here",
        input=input_data
    )
    
    print(f"Started workflow instance with ID: {instance_id}")
```

### Monitoring Workflow Execution

#### Using the API:
```bash
# Get workflow instance status
curl http://localhost:8007/api/instances/instance_id_here

# Get workflow instance history
curl http://localhost:8007/api/instances/instance_id_here/history
```

#### Using the Python Client:
```python
from harmonia.client import HarmoniaClient

async def monitor_workflow_example():
    client = HarmoniaClient("http://localhost:8007")
    
    # Get instance status
    instance = await client.get_instance("instance_id_here")
    
    print(f"Workflow Instance: {instance['name']}")
    print(f"Status: {instance['status']}")
    print(f"Current Step: {instance['current_step']}")
    
    # Get instance history
    history = await client.get_instance_history("instance_id_here")
    
    print("\nExecution History:")
    for entry in history:
        print(f"- {entry['timestamp']} | {entry['step_id']} | {entry['event_type']}")
        if entry.get('event_data'):
            print(f"  Data: {entry['event_data']}")
```

### Interacting with Workflow Instances

#### Using the API:
```bash
# Pause a workflow instance
curl -X POST http://localhost:8007/api/instances/instance_id_here/pause

# Resume a workflow instance
curl -X POST http://localhost:8007/api/instances/instance_id_here/resume

# Cancel a workflow instance
curl -X POST http://localhost:8007/api/instances/instance_id_here/cancel

# Update workflow instance state
curl -X POST http://localhost:8007/api/instances/instance_id_here/state \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "status": "approved",
      "approver": "manager@example.com",
      "comments": "Approved based on project requirements"
    }
  }'
```

#### Using the Python Client:
```python
from harmonia.client import HarmoniaClient

async def interact_with_workflow_example():
    client = HarmoniaClient("http://localhost:8007")
    
    # Pause instance
    await client.pause_instance("instance_id_here")
    print("Workflow instance paused")
    
    # Update instance state
    await client.update_instance_state(
        instance_id="instance_id_here",
        state_update={
            "task": {
                "status": "approved",
                "approver": "manager@example.com",
                "comments": "Approved based on project requirements"
            }
        }
    )
    print("Workflow instance state updated")
    
    # Resume instance
    await client.resume_instance("instance_id_here")
    print("Workflow instance resumed")
```

## Working with Templates

### Creating a Workflow Template

#### Using the API:
```bash
curl -X POST http://localhost:8007/api/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Approval Process Template",
    "description": "Template for approval workflows",
    "parameters": [
      {
        "name": "approver_role",
        "type": "string",
        "required": true,
        "default": "manager"
      },
      {
        "name": "approval_timeout_hours",
        "type": "number",
        "required": false,
        "default": 24
      },
      {
        "name": "notification_enabled",
        "type": "boolean",
        "default": true
      }
    ],
    "template": {
      "steps": [
        {
          "id": "start",
          "type": "start",
          "transitions": [
            {
              "to": "create_approval_task",
              "condition": "true"
            }
          ]
        },
        {
          "id": "create_approval_task",
          "type": "action",
          "component": "ergon",
          "action": "create_task",
          "parameters": {
            "title": "Approval Required: ${input.request_title}",
            "description": "${input.request_description}",
            "priority": "high",
            "assignee_role": "${parameters.approver_role}",
            "due_in_hours": "${parameters.approval_timeout_hours}"
          },
          "transitions": [
            {
              "to": "notify_approver",
              "condition": "parameters.notification_enabled == true"
            },
            {
              "to": "wait_for_approval",
              "condition": "parameters.notification_enabled == false"
            }
          ]
        },
        {
          "id": "notify_approver",
          "type": "action",
          "component": "ergon",
          "action": "send_notification",
          "parameters": {
            "to_role": "${parameters.approver_role}",
            "subject": "Approval Required: ${input.request_title}",
            "message": "Please review and approve/reject the following request: ${input.request_description}"
          },
          "transitions": [
            {
              "to": "wait_for_approval",
              "condition": "true"
            }
          ]
        },
        {
          "id": "wait_for_approval",
          "type": "wait",
          "wait_for": {
            "state_change": "task.status",
            "timeout_hours": "${parameters.approval_timeout_hours}"
          },
          "transitions": [
            {
              "to": "check_approval",
              "condition": "true"
            }
          ]
        },
        {
          "id": "check_approval",
          "type": "decision",
          "transitions": [
            {
              "to": "handle_approval",
              "condition": "state.task.status == \"approved\""
            },
            {
              "to": "handle_rejection",
              "condition": "state.task.status == \"rejected\""
            },
            {
              "to": "handle_timeout",
              "condition": "state.wait_for_approval.timed_out == true"
            }
          ]
        },
        {
          "id": "handle_approval",
          "type": "action",
          "component": "ergon",
          "action": "process_approval",
          "parameters": {
            "request_id": "${input.request_id}",
            "approver": "${state.task.approver}",
            "comments": "${state.task.comments}"
          },
          "transitions": [
            {
              "to": "end",
              "condition": "true"
            }
          ]
        },
        {
          "id": "handle_rejection",
          "type": "action",
          "component": "ergon",
          "action": "process_rejection",
          "parameters": {
            "request_id": "${input.request_id}",
            "rejecter": "${state.task.approver}",
            "reason": "${state.task.comments}"
          },
          "transitions": [
            {
              "to": "end",
              "condition": "true"
            }
          ]
        },
        {
          "id": "handle_timeout",
          "type": "action",
          "component": "ergon",
          "action": "process_timeout",
          "parameters": {
            "request_id": "${input.request_id}",
            "escalate_to": "director"
          },
          "transitions": [
            {
              "to": "end",
              "condition": "true"
            }
          ]
        },
        {
          "id": "end",
          "type": "end"
        }
      ]
    }
  }'
```

### Creating a Workflow from a Template

#### Using the API:
```bash
curl -X POST http://localhost:8007/api/templates/template_id_here/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Software Access Approval",
    "description": "Workflow for approving software access requests",
    "parameters": {
      "approver_role": "it_manager",
      "approval_timeout_hours": 48
    }
  }'
```

#### Using the Python Client:
```python
from harmonia.client import HarmoniaClient

async def create_from_template_example():
    client = HarmoniaClient("http://localhost:8007")
    
    workflow_id = await client.create_workflow_from_template(
        template_id="template_id_here",
        name="Software Access Approval",
        description="Workflow for approving software access requests",
        parameters={
            "approver_role": "it_manager",
            "approval_timeout_hours": 48
        }
    )
    
    print(f"Created workflow from template with ID: {workflow_id}")
```

## Using Expressions

Harmonia supports expressions for dynamic behavior:

### Basic Expressions

- **State Access**: `state.step_id.property`
- **Input Access**: `input.property`
- **Parameter Access**: `parameters.parameter_name`
- **Environment Access**: `env.variable_name`

### Expression Examples

1. **Simple Condition**:
   ```
   state.task.status == "approved"
   ```

2. **Logical Operators**:
   ```
   state.request.priority == "high" && state.approver.level >= 2
   ```

3. **String Interpolation**:
   ```
   "Approval required for ${input.request_id} from ${input.requester}"
   ```

4. **Array Operations**:
   ```
   state.items.length > 0 && state.items.some(item => item.status == "pending")
   ```

5. **Mathematical Operations**:
   ```
   state.budget.allocated - state.budget.used >= input.request.amount
   ```

6. **Function Calls**:
   ```
   DateTime.now().after(DateTime.parse(state.deadline))
   ```

7. **Conditional (Ternary) Operator**:
   ```
   state.priority == "high" ? "urgent" : "normal"
   ```

## State Management

### Understanding Workflow State

Workflow state consists of:

- **Input**: The initial data provided when starting the workflow
- **Step Results**: The output of each executed step
- **Global Variables**: Values that can be accessed and modified by any step
- **Environment Variables**: System-level values that can be accessed but not modified

### Accessing State in Steps

```json
{
  "id": "format_message",
  "type": "action",
  "component": "ergon",
  "action": "format_text",
  "parameters": {
    "template": "Request ${input.request_id} was ${state.approval_status} by ${state.approver_name}",
    "variables": {
      "approval_status": "${state.check_approval.result.status}",
      "approver_name": "${state.get_approver.result.name}"
    }
  }
}
```

### Updating State

#### Using the API:
```bash
curl -X POST http://localhost:8007/api/instances/instance_id_here/state \
  -H "Content-Type: application/json" \
  -d '{
    "approval_status": "approved",
    "approver_name": "Jane Smith",
    "approval_date": "2025-05-01T10:30:00Z",
    "comments": "Approved as per department policy"
  }'
```

#### Using the Python Client:
```python
from harmonia.client import HarmoniaClient

async def update_state_example():
    client = HarmoniaClient("http://localhost:8007")
    
    await client.update_instance_state(
        instance_id="instance_id_here",
        state_update={
            "approval_status": "approved",
            "approver_name": "Jane Smith",
            "approval_date": "2025-05-01T10:30:00Z",
            "comments": "Approved as per department policy"
        }
    )
    
    print("Workflow state updated")
```

## Component Integration

### Available Component Actions

Harmonia integrates with various Tekton components:

#### Ergon Actions:
- `create_task`: Create a new task
- `update_task`: Update an existing task
- `assign_task`: Assign a task to an agent
- `complete_task`: Mark a task as complete
- `get_task`: Retrieve task details

#### Athena Actions:
- `create_entity`: Create a knowledge graph entity
- `update_entity`: Update an entity
- `create_relationship`: Create a relationship between entities
- `query_knowledge`: Query the knowledge graph
- `get_entity`: Retrieve entity details

#### Engram Actions:
- `store_memory`: Store a memory
- `retrieve_memory`: Retrieve a memory by ID
- `search_memories`: Search for memories
- `update_memory`: Update an existing memory

#### Rhetor Actions:
- `generate_text`: Generate text using an LLM
- `summarize_text`: Summarize text
- `analyze_sentiment`: Analyze sentiment of text
- `extract_entities`: Extract entities from text

### Using Component Actions in Workflows

```json
{
  "id": "analyze_request",
  "type": "action",
  "component": "rhetor",
  "action": "analyze_sentiment",
  "parameters": {
    "text": "${input.request_text}",
    "options": {
      "model": "claude-3-haiku-20240307",
      "include_entities": true
    }
  },
  "transitions": [
    {
      "to": "store_analysis",
      "condition": "true"
    }
  ]
}
```

### Custom Component Integration

You can integrate custom components by registering them with Harmonia:

#### Using the API:
```bash
curl -X POST http://localhost:8007/api/components \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom_service",
    "description": "Custom integration with external service",
    "base_url": "http://custom-service.example.com/api",
    "actions": [
      {
        "name": "process_data",
        "description": "Process data with custom service",
        "path": "/process",
        "method": "POST",
        "parameters": [
          {
            "name": "data",
            "type": "object",
            "required": true
          },
          {
            "name": "options",
            "type": "object",
            "required": false
          }
        ],
        "result_path": "$.result"
      }
    ],
    "authentication": {
      "type": "bearer",
      "token": "${env.CUSTOM_SERVICE_TOKEN}"
    }
  }'
```

## Troubleshooting

### Common Issues

**Issue**: Workflow step fails to execute
**Solution**:
1. Check component availability
2. Verify action parameters
3. Ensure required state variables exist
4. Check component logs for errors

**Issue**: Condition evaluation fails
**Solution**:
1. Check expression syntax
2. Verify state variables exist
3. Check for type mismatches
4. Use expression debugging

**Issue**: Workflow gets stuck
**Solution**:
1. Check for missing transitions
2. Verify condition logic is correct
3. Ensure wait steps have proper timeouts
4. Check for deadlocks in fork/join steps

### Debugging Workflows

#### Using the API:
```bash
# Get detailed instance status
curl http://localhost:8007/api/instances/instance_id_here/debug

# Evaluate an expression against instance state
curl -X POST http://localhost:8007/api/expressions/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "instance_id_here",
    "expression": "state.task.status == \"approved\" && input.priority == \"high\""
  }'

# View instance state
curl http://localhost:8007/api/instances/instance_id_here/state
```

### Log Checking

```bash
# View Harmonia logs
tail -f /path/to/tekton/logs/harmonia.log

# Filter for specific workflow instance
grep "instance_id_here" /path/to/tekton/logs/harmonia.log

# Check for expression evaluation issues
grep "expression evaluation" /path/to/tekton/logs/harmonia.log

# View component action errors
grep "action error" /path/to/tekton/logs/harmonia.log
```

## Best Practices

### Workflow Design

1. **Keep steps focused**: Each step should perform a single logical action
2. **Use meaningful IDs**: Choose step IDs that clearly indicate purpose
3. **Add appropriate error handling**: Include transitions for failure cases
4. **Set timeouts**: Always set timeouts for wait steps and external actions
5. **Document workflows**: Include descriptions for workflows and complex steps

### Expression Writing

1. **Keep expressions simple**: Break complex logic into multiple conditions
2. **Use default values**: Handle potential null values with defaults
3. **Validate inputs**: Check input validity before processing
4. **Use parentheses for clarity**: Make precedence explicit in complex expressions
5. **Test expressions independently**: Use the expression evaluator to test logic

### Component Integration

1. **Check component availability**: Verify components are available before executing actions
2. **Handle action failures**: Always handle potential failures from component actions
3. **Use retry mechanisms**: Configure retry for unreliable actions
4. **Implement fallbacks**: Provide alternative paths when components are unavailable
5. **Monitor integration performance**: Track response times and failure rates

### Performance Optimization

1. **Use parallel execution**: Leverage fork/join for independent steps
2. **Optimize state size**: Store only necessary data in state
3. **Implement caching**: Cache expensive operation results
4. **Batch operations**: Combine related actions when possible
5. **Limit loop iterations**: Avoid infinite or very large loops