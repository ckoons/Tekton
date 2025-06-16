# Synthesis API Reference

This document provides a detailed reference for the Synthesis API, following the Single Port Architecture pattern on port 8009.

## Base URL

All API endpoints are accessible under the base URL:

```
http://<host>:8009/api/
```

## Authentication

All API endpoints require authentication using the Tekton authentication system. Include the authentication token in the `Authorization` header:

```
Authorization: Bearer <token>
```

## REST API Endpoints

### Executions API

#### Create Execution

```
POST /api/executions
```

Creates a new execution based on the provided plan.

**Request Body:**

```json
{
  "plan": {
    "name": "Example Plan",
    "description": "An example execution plan",
    "steps": [
      {
        "id": "step1",
        "type": "command",
        "parameters": {
          "command": "echo Hello, World!"
        }
      }
    ]
  },
  "variables": {
    "var1": "value1",
    "var2": "value2"
  },
  "metadata": {
    "tags": ["example", "test"],
    "created_by": "user1"
  }
}
```

**Response:**

```json
{
  "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
  "status": "created",
  "created_at": "2025-05-01T10:15:30Z",
  "plan": {
    "name": "Example Plan",
    "description": "An example execution plan",
    "steps": [
      {
        "id": "step1",
        "type": "command",
        "parameters": {
          "command": "echo Hello, World!"
        }
      }
    ]
  }
}
```

#### List Executions

```
GET /api/executions
```

Lists all executions with optional filtering.

**Query Parameters:**

- `status` - Filter by execution status (e.g., created, running, completed, failed)
- `tag` - Filter by tag
- `created_by` - Filter by creator
- `from_date` - Filter by creation date (from)
- `to_date` - Filter by creation date (to)
- `limit` - Maximum number of results to return (default: 50)
- `offset` - Offset for pagination (default: 0)

**Response:**

```json
{
  "total": 42,
  "offset": 0,
  "limit": 50,
  "executions": [
    {
      "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
      "name": "Example Plan",
      "status": "completed",
      "created_at": "2025-05-01T10:15:30Z",
      "completed_at": "2025-05-01T10:16:45Z",
      "tags": ["example", "test"]
    }
  ]
}
```

#### Get Execution Details

```
GET /api/executions/{execution_id}
```

Retrieves detailed information about a specific execution.

**Path Parameters:**

- `execution_id` - The ID of the execution to retrieve

**Response:**

```json
{
  "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
  "status": "completed",
  "created_at": "2025-05-01T10:15:30Z",
  "started_at": "2025-05-01T10:15:31Z",
  "completed_at": "2025-05-01T10:16:45Z",
  "duration_ms": 74000,
  "plan": {
    "name": "Example Plan",
    "description": "An example execution plan",
    "steps": [
      {
        "id": "step1",
        "type": "command",
        "parameters": {
          "command": "echo Hello, World!"
        }
      }
    ]
  },
  "steps": [
    {
      "id": "step1",
      "type": "command",
      "status": "completed",
      "started_at": "2025-05-01T10:15:31Z",
      "completed_at": "2025-05-01T10:15:32Z",
      "duration_ms": 1000,
      "output": "Hello, World!\n",
      "error": null
    }
  ],
  "variables": {
    "var1": "value1",
    "var2": "value2"
  },
  "metadata": {
    "tags": ["example", "test"],
    "created_by": "user1"
  }
}
```

#### Start Execution

```
POST /api/executions/{execution_id}/start
```

Starts an execution that is in the "created" state.

**Path Parameters:**

- `execution_id` - The ID of the execution to start

**Response:**

```json
{
  "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
  "status": "running",
  "started_at": "2025-05-01T10:15:31Z"
}
```

#### Pause Execution

```
POST /api/executions/{execution_id}/pause
```

Pauses a running execution.

**Path Parameters:**

- `execution_id` - The ID of the execution to pause

**Response:**

```json
{
  "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
  "status": "paused",
  "paused_at": "2025-05-01T10:15:45Z"
}
```

#### Resume Execution

```
POST /api/executions/{execution_id}/resume
```

Resumes a paused execution.

**Path Parameters:**

- `execution_id` - The ID of the execution to resume

**Response:**

```json
{
  "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
  "status": "running",
  "resumed_at": "2025-05-01T10:16:00Z"
}
```

#### Cancel Execution

```
POST /api/executions/{execution_id}/cancel
```

Cancels a running or paused execution.

**Path Parameters:**

- `execution_id` - The ID of the execution to cancel

**Response:**

```json
{
  "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
  "status": "cancelled",
  "cancelled_at": "2025-05-01T10:16:15Z"
}
```

#### Get Execution Steps

```
GET /api/executions/{execution_id}/steps
```

Lists all steps for a specific execution.

**Path Parameters:**

- `execution_id` - The ID of the execution

**Response:**

```json
{
  "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
  "steps": [
    {
      "id": "step1",
      "type": "command",
      "status": "completed",
      "started_at": "2025-05-01T10:15:31Z",
      "completed_at": "2025-05-01T10:15:32Z",
      "duration_ms": 1000,
      "output": "Hello, World!\n",
      "error": null
    }
  ]
}
```

#### Get Execution Step

```
GET /api/executions/{execution_id}/steps/{step_id}
```

Retrieves detailed information about a specific step in an execution.

**Path Parameters:**

- `execution_id` - The ID of the execution
- `step_id` - The ID of the step

**Response:**

```json
{
  "id": "step1",
  "type": "command",
  "status": "completed",
  "started_at": "2025-05-01T10:15:31Z",
  "completed_at": "2025-05-01T10:15:32Z",
  "duration_ms": 1000,
  "parameters": {
    "command": "echo Hello, World!"
  },
  "output": "Hello, World!\n",
  "error": null
}
```

#### Get Execution Variables

```
GET /api/executions/{execution_id}/variables
```

Retrieves the variables for a specific execution.

**Path Parameters:**

- `execution_id` - The ID of the execution

**Response:**

```json
{
  "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
  "variables": {
    "var1": "value1",
    "var2": "value2",
    "step1_output": "Hello, World!\n"
  }
}
```

### Plans API

#### Create Plan

```
POST /api/plans
```

Creates a new execution plan.

**Request Body:**

```json
{
  "name": "Example Plan",
  "description": "An example execution plan",
  "steps": [
    {
      "id": "step1",
      "type": "command",
      "parameters": {
        "command": "echo Hello, World!"
      }
    }
  ],
  "metadata": {
    "tags": ["example", "test"],
    "created_by": "user1"
  }
}
```

**Response:**

```json
{
  "plan_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
  "name": "Example Plan",
  "description": "An example execution plan",
  "created_at": "2025-05-01T10:15:30Z",
  "steps": [
    {
      "id": "step1",
      "type": "command",
      "parameters": {
        "command": "echo Hello, World!"
      }
    }
  ],
  "metadata": {
    "tags": ["example", "test"],
    "created_by": "user1"
  }
}
```

#### List Plans

```
GET /api/plans
```

Lists all execution plans with optional filtering.

**Query Parameters:**

- `tag` - Filter by tag
- `created_by` - Filter by creator
- `from_date` - Filter by creation date (from)
- `to_date` - Filter by creation date (to)
- `limit` - Maximum number of results to return (default: 50)
- `offset` - Offset for pagination (default: 0)

**Response:**

```json
{
  "total": 10,
  "offset": 0,
  "limit": 50,
  "plans": [
    {
      "plan_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
      "name": "Example Plan",
      "description": "An example execution plan",
      "created_at": "2025-05-01T10:15:30Z",
      "tags": ["example", "test"]
    }
  ]
}
```

#### Get Plan

```
GET /api/plans/{plan_id}
```

Retrieves a specific execution plan.

**Path Parameters:**

- `plan_id` - The ID of the plan to retrieve

**Response:**

```json
{
  "plan_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
  "name": "Example Plan",
  "description": "An example execution plan",
  "created_at": "2025-05-01T10:15:30Z",
  "steps": [
    {
      "id": "step1",
      "type": "command",
      "parameters": {
        "command": "echo Hello, World!"
      }
    }
  ],
  "metadata": {
    "tags": ["example", "test"],
    "created_by": "user1"
  }
}
```

#### Update Plan

```
PUT /api/plans/{plan_id}
```

Updates a specific execution plan.

**Path Parameters:**

- `plan_id` - The ID of the plan to update

**Request Body:**

```json
{
  "name": "Updated Example Plan",
  "description": "An updated example execution plan",
  "steps": [
    {
      "id": "step1",
      "type": "command",
      "parameters": {
        "command": "echo Hello, Updated World!"
      }
    }
  ],
  "metadata": {
    "tags": ["example", "test", "updated"],
    "created_by": "user1"
  }
}
```

**Response:**

```json
{
  "plan_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
  "name": "Updated Example Plan",
  "description": "An updated example execution plan",
  "created_at": "2025-05-01T10:15:30Z",
  "updated_at": "2025-05-01T11:30:45Z",
  "steps": [
    {
      "id": "step1",
      "type": "command",
      "parameters": {
        "command": "echo Hello, Updated World!"
      }
    }
  ],
  "metadata": {
    "tags": ["example", "test", "updated"],
    "created_by": "user1"
  }
}
```

#### Delete Plan

```
DELETE /api/plans/{plan_id}
```

Deletes a specific execution plan.

**Path Parameters:**

- `plan_id` - The ID of the plan to delete

**Response:**

```json
{
  "success": true,
  "message": "Plan deleted successfully"
}
```

#### Execute Plan

```
POST /api/plans/{plan_id}/execute
```

Creates and starts an execution of a specific plan.

**Path Parameters:**

- `plan_id` - The ID of the plan to execute

**Request Body:**

```json
{
  "variables": {
    "var1": "value1",
    "var2": "value2"
  },
  "metadata": {
    "tags": ["execution", "test"],
    "created_by": "user1"
  }
}
```

**Response:**

```json
{
  "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
  "status": "running",
  "created_at": "2025-05-01T10:15:30Z",
  "started_at": "2025-05-01T10:15:31Z",
  "plan_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6"
}
```

### Integrations API

#### List Integrations

```
GET /api/integrations
```

Lists all available integrations.

**Response:**

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
      "id": "mcp",
      "name": "Machine Control Protocol",
      "description": "Control external systems using MCP",
      "capabilities": ["connect", "disconnect", "send_command", "receive_response"]
    }
  ]
}
```

#### Get Integration

```
GET /api/integrations/{integration_id}
```

Retrieves detailed information about a specific integration.

**Path Parameters:**

- `integration_id` - The ID of the integration to retrieve

**Response:**

```json
{
  "id": "cli",
  "name": "Command Line",
  "description": "Execute commands on the local system",
  "capabilities": ["execute_command", "execute_script"],
  "parameters": {
    "execute_command": {
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
    },
    "execute_script": {
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
}
```

#### Get Integration Capabilities

```
GET /api/integrations/{integration_id}/capabilities
```

Lists all capabilities for a specific integration.

**Path Parameters:**

- `integration_id` - The ID of the integration

**Response:**

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

#### Invoke Integration Capability

```
POST /api/integrations/{integration_id}/capabilities/{capability_id}
```

Invokes a specific capability of an integration.

**Path Parameters:**

- `integration_id` - The ID of the integration
- `capability_id` - The ID of the capability to invoke

**Request Body:**

```json
{
  "parameters": {
    "command": "echo Hello, Integration!",
    "working_directory": "/tmp",
    "timeout": 30
  }
}
```

**Response:**

```json
{
  "invocation_id": "c1d2e3f4-5g6h-7i8j-9k0l-m1n2o3p4q5r6",
  "integration_id": "cli",
  "capability_id": "execute_command",
  "status": "completed",
  "started_at": "2025-05-01T10:15:30Z",
  "completed_at": "2025-05-01T10:15:31Z",
  "duration_ms": 1000,
  "output": "Hello, Integration!\n",
  "error": null
}
```

#### Get Invocation Status

```
GET /api/integrations/invocations/{invocation_id}
```

Retrieves the status of a specific integration capability invocation.

**Path Parameters:**

- `invocation_id` - The ID of the invocation

**Response:**

```json
{
  "invocation_id": "c1d2e3f4-5g6h-7i8j-9k0l-m1n2o3p4q5r6",
  "integration_id": "cli",
  "capability_id": "execute_command",
  "status": "completed",
  "started_at": "2025-05-01T10:15:30Z",
  "completed_at": "2025-05-01T10:15:31Z",
  "duration_ms": 1000,
  "parameters": {
    "command": "echo Hello, Integration!",
    "working_directory": "/tmp",
    "timeout": 30
  },
  "output": "Hello, Integration!\n",
  "error": null
}
```

### Events API

#### List Events

```
GET /api/events
```

Lists all events with optional filtering.

**Query Parameters:**

- `type` - Filter by event type
- `execution_id` - Filter by execution ID
- `from_date` - Filter by timestamp (from)
- `to_date` - Filter by timestamp (to)
- `limit` - Maximum number of results to return (default: 50)
- `offset` - Offset for pagination (default: 0)

**Response:**

```json
{
  "total": 100,
  "offset": 0,
  "limit": 50,
  "events": [
    {
      "event_id": "e1f2g3h4-5i6j-7k8l-9m0n-o1p2q3r4s5t6",
      "type": "execution_started",
      "timestamp": "2025-05-01T10:15:31Z",
      "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
      "payload": {
        "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
        "plan_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
        "name": "Example Plan"
      }
    }
  ]
}
```

#### Get Event

```
GET /api/events/{event_id}
```

Retrieves a specific event.

**Path Parameters:**

- `event_id` - The ID of the event to retrieve

**Response:**

```json
{
  "event_id": "e1f2g3h4-5i6j-7k8l-9m0n-o1p2q3r4s5t6",
  "type": "execution_started",
  "timestamp": "2025-05-01T10:15:31Z",
  "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
  "payload": {
    "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
    "plan_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
    "name": "Example Plan"
  }
}
```

#### Subscribe to Events

```
POST /api/events/subscriptions
```

Creates a subscription to specific event types.

**Request Body:**

```json
{
  "types": ["execution_started", "execution_completed", "step_started", "step_completed"],
  "filter": {
    "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f"
  },
  "callback_url": "http://example.com/callback",
  "expiration": "2025-05-02T10:15:30Z"
}
```

**Response:**

```json
{
  "subscription_id": "s1t2u3v4-5w6x-7y8z-9a0b-c1d2e3f4g5h6",
  "types": ["execution_started", "execution_completed", "step_started", "step_completed"],
  "filter": {
    "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f"
  },
  "callback_url": "http://example.com/callback",
  "created_at": "2025-05-01T10:15:30Z",
  "expiration": "2025-05-02T10:15:30Z"
}
```

#### List Subscriptions

```
GET /api/events/subscriptions
```

Lists all event subscriptions.

**Response:**

```json
{
  "subscriptions": [
    {
      "subscription_id": "s1t2u3v4-5w6x-7y8z-9a0b-c1d2e3f4g5h6",
      "types": ["execution_started", "execution_completed", "step_started", "step_completed"],
      "filter": {
        "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f"
      },
      "callback_url": "http://example.com/callback",
      "created_at": "2025-05-01T10:15:30Z",
      "expiration": "2025-05-02T10:15:30Z"
    }
  ]
}
```

#### Delete Subscription

```
DELETE /api/events/subscriptions/{subscription_id}
```

Deletes a specific event subscription.

**Path Parameters:**

- `subscription_id` - The ID of the subscription to delete

**Response:**

```json
{
  "success": true,
  "message": "Subscription deleted successfully"
}
```

### System API

#### Health Check

```
GET /health
```

Checks the health status of the Synthesis component.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "components": {
    "api": "healthy",
    "execution_engine": "healthy",
    "storage": "healthy",
    "event_system": "healthy"
  }
}
```

#### Metrics

```
GET /metrics
```

Retrieves metrics for the Synthesis component.

**Response:**

```json
{
  "executions": {
    "total": 1250,
    "active": 5,
    "completed": 1200,
    "failed": 45,
    "cancelled": 0
  },
  "steps": {
    "total": 7500,
    "succeeded": 7450,
    "failed": 50
  },
  "performance": {
    "average_execution_time_ms": 2500,
    "average_step_time_ms": 500,
    "p95_execution_time_ms": 5000,
    "p95_step_time_ms": 1000
  },
  "resource_usage": {
    "memory_mb": 256,
    "cpu_percent": 8.5
  }
}
```

## WebSocket API

### Execution Updates

```
WebSocket: ws://<host>:8009/ws/executions/{execution_id}
```

Provides real-time updates about execution progress.

**Connection URL Parameters:**

- `execution_id` - The ID of the execution to monitor

**Messages:**

1. Execution Started:
```json
{
  "type": "execution_started",
  "timestamp": "2025-05-01T10:15:31Z",
  "data": {
    "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
    "plan_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
    "name": "Example Plan"
  }
}
```

2. Step Started:
```json
{
  "type": "step_started",
  "timestamp": "2025-05-01T10:15:31Z",
  "data": {
    "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
    "step_id": "step1",
    "step_type": "command"
  }
}
```

3. Step Output:
```json
{
  "type": "step_output",
  "timestamp": "2025-05-01T10:15:31Z",
  "data": {
    "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
    "step_id": "step1",
    "output": "Hello, World!\n"
  }
}
```

4. Step Completed:
```json
{
  "type": "step_completed",
  "timestamp": "2025-05-01T10:15:32Z",
  "data": {
    "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
    "step_id": "step1",
    "status": "completed",
    "duration_ms": 1000
  }
}
```

5. Execution Completed:
```json
{
  "type": "execution_completed",
  "timestamp": "2025-05-01T10:16:45Z",
  "data": {
    "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
    "status": "completed",
    "duration_ms": 74000
  }
}
```

### Event Stream

```
WebSocket: ws://<host>:8009/ws/events
```

Provides a real-time stream of all system events.

**Connection URL Parameters:**

- None

**Messages:**

1. Event:
```json
{
  "event_id": "e1f2g3h4-5i6j-7k8l-9m0n-o1p2q3r4s5t6",
  "type": "execution_started",
  "timestamp": "2025-05-01T10:15:31Z",
  "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
  "payload": {
    "execution_id": "f8c2e9b4-5c3d-4a1e-8f5d-6b7a8c9d0e1f",
    "plan_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
    "name": "Example Plan"
  }
}
```

## API Clients

Synthesis provides client libraries for easy integration:

### Python Client

```python
from synthesis.client import SynthesisClient
import asyncio

async def example():
    # Create client
    client = SynthesisClient(base_url="http://localhost:8009")
    
    try:
        # Create and execute a simple plan
        execution_id = await client.execute_plan({
            "name": "Example Plan",
            "description": "An example execution plan",
            "steps": [
                {
                    "id": "step1",
                    "type": "command",
                    "parameters": {
                        "command": "echo Hello, World!"
                    }
                }
            ]
        })
        
        # Wait for completion
        result = await client.wait_for_execution(execution_id)
        
        print(f"Execution completed with status: {result['status']}")
        
        # Get step outputs
        steps = await client.get_execution_steps(execution_id)
        for step in steps["steps"]:
            print(f"Step {step['id']} output: {step['output']}")
            
    finally:
        # Close client
        await client.close()

# Run the example
asyncio.run(example())
```

### JavaScript Client

```javascript
import { SynthesisClient } from 'synthesis-client';

async function example() {
  // Create client
  const client = new SynthesisClient('http://localhost:8009');
  
  try {
    // Create and execute a simple plan
    const executionId = await client.executePlan({
      name: 'Example Plan',
      description: 'An example execution plan',
      steps: [
        {
          id: 'step1',
          type: 'command',
          parameters: {
            command: 'echo Hello, World!'
          }
        }
      ]
    });
    
    // Subscribe to real-time updates
    const ws = client.subscribeToExecution(executionId);
    
    ws.onmessage = function(event) {
      const data = JSON.parse(event.data);
      console.log(`Event: ${data.type}`);
      
      if (data.type === 'execution_completed') {
        ws.close();
      }
    };
    
    // Wait for completion
    const result = await client.waitForExecution(executionId);
    
    console.log(`Execution completed with status: ${result.status}`);
    
    // Get step outputs
    const steps = await client.getExecutionSteps(executionId);
    steps.steps.forEach(step => {
      console.log(`Step ${step.id} output: ${step.output}`);
    });
    
  } finally {
    // Close client
    client.close();
  }
}

example();
```

## Error Responses

All API endpoints return standard error responses in the following format:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "steps",
        "message": "At least one step is required"
      }
    ]
  }
}
```

Common error codes:

- `validation_error`: Request validation failed
- `not_found`: Resource not found
- `already_exists`: Resource already exists
- `permission_denied`: Permission denied
- `execution_failed`: Execution failed
- `integration_error`: Integration error
- `internal_error`: Internal server error