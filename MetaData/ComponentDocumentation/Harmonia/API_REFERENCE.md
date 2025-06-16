# Harmonia API Reference

## Base URL

```
http://localhost:8002/api/harmonia
```

## Authentication

All API requests require authentication via one of the following methods:

- **API Key**: Passed via the `X-API-Key` header
- **Bearer Token**: Passed via the `Authorization` header

## Workflows API

### Create Workflow

Create a new workflow definition.

```
POST /workflows
```

#### Request Body

```json
{
  "name": "data_processing_workflow",
  "description": "Process and analyze data files",
  "version": "1.0.0",
  "tasks": {
    "fetch_data": {
      "name": "fetch_data",
      "component": "ergon",
      "action": "execute_command",
      "input": {
        "command": "curl -o ${workflow.input.output_file} ${workflow.input.data_url}"
      }
    },
    "process_data": {
      "name": "process_data",
      "component": "sophia",
      "action": "analyze_data",
      "input": {
        "file_path": "${workflow.input.output_file}",
        "analysis_type": "${workflow.input.analysis_type}"
      },
      "depends_on": ["fetch_data"]
    },
    "generate_report": {
      "name": "generate_report",
      "component": "rhetor",
      "action": "generate_content",
      "input": {
        "template": "report",
        "data": "${tasks.process_data.output.results}"
      },
      "depends_on": ["process_data"]
    }
  },
  "input_schema": {
    "data_url": {
      "type": "string",
      "format": "uri",
      "description": "URL to the data file"
    },
    "output_file": {
      "type": "string",
      "description": "Path to save the downloaded file"
    },
    "analysis_type": {
      "type": "string",
      "enum": ["basic", "detailed", "comprehensive"],
      "default": "basic",
      "description": "Type of analysis to perform"
    }
  }
}
```

#### Response

```json
{
  "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "name": "data_processing_workflow",
  "description": "Process and analyze data files",
  "version": "1.0.0",
  "created_at": "2025-01-15T12:00:00Z",
  "updated_at": "2025-01-15T12:00:00Z",
  "tasks": { ... },
  "input_schema": { ... }
}
```

### Get Workflow

Retrieve a workflow definition by ID.

```
GET /workflows/{workflow_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `workflow_id` | string | path | The unique identifier of the workflow |

#### Response

```json
{
  "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "name": "data_processing_workflow",
  "description": "Process and analyze data files",
  "version": "1.0.0",
  "created_at": "2025-01-15T12:00:00Z",
  "updated_at": "2025-01-15T12:00:00Z",
  "tasks": { ... },
  "input_schema": { ... }
}
```

### Update Workflow

Update an existing workflow definition.

```
PUT /workflows/{workflow_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `workflow_id` | string | path | The unique identifier of the workflow |

#### Request Body

```json
{
  "name": "data_processing_workflow_v2",
  "description": "Updated data processing workflow",
  "version": "1.1.0",
  "tasks": { ... },
  "input_schema": { ... }
}
```

#### Response

```json
{
  "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "name": "data_processing_workflow_v2",
  "description": "Updated data processing workflow",
  "version": "1.1.0",
  "created_at": "2025-01-15T12:00:00Z",
  "updated_at": "2025-01-15T13:30:00Z",
  "tasks": { ... },
  "input_schema": { ... }
}
```

### Delete Workflow

Delete a workflow definition by ID.

```
DELETE /workflows/{workflow_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `workflow_id` | string | path | The unique identifier of the workflow |

#### Response

```json
{
  "success": true,
  "message": "Workflow deleted successfully"
}
```

### List Workflows

Retrieve a list of workflow definitions.

```
GET /workflows
```

#### Query Parameters

| Name | Type | Description |
|------|------|------------|
| `page` | integer | Page number for pagination (default: 1) |
| `limit` | integer | Number of items per page (default: 20) |
| `sort_by` | string | Field to sort by (default: "created_at") |
| `sort_order` | string | Sort order ("asc" or "desc", default: "desc") |

#### Response

```json
{
  "items": [
    {
      "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
      "name": "data_processing_workflow",
      "description": "Process and analyze data files",
      "version": "1.0.0",
      "created_at": "2025-01-15T12:00:00Z",
      "updated_at": "2025-01-15T12:00:00Z"
    },
    { ... }
  ],
  "total": 42,
  "page": 1,
  "limit": 20
}
```

## Executions API

### Execute Workflow

Execute a workflow with input parameters.

```
POST /executions
```

#### Request Body

```json
{
  "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "input": {
    "data_url": "https://example.com/data.csv",
    "output_file": "/tmp/data.csv",
    "analysis_type": "detailed"
  },
  "execution_options": {
    "async": true,
    "timeout": 3600,
    "retry_policy": {
      "max_retries": 3,
      "retry_interval": 5
    }
  }
}
```

#### Response

```json
{
  "execution_id": "exec-123e4567-e89b-12d3-a456-426614174000",
  "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "status": "pending",
  "created_at": "2025-01-15T14:00:00Z",
  "updated_at": "2025-01-15T14:00:00Z",
  "input": { ... },
  "execution_options": { ... }
}
```

### Get Execution Status

Retrieve the status of a workflow execution.

```
GET /executions/{execution_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `execution_id` | string | path | The unique identifier of the execution |

#### Response

```json
{
  "execution_id": "exec-123e4567-e89b-12d3-a456-426614174000",
  "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "status": "running",
  "progress": {
    "completed_tasks": 1,
    "total_tasks": 3,
    "current_task": "process_data"
  },
  "created_at": "2025-01-15T14:00:00Z",
  "updated_at": "2025-01-15T14:05:00Z",
  "started_at": "2025-01-15T14:00:10Z",
  "completed_at": null,
  "task_status": {
    "fetch_data": {
      "status": "completed",
      "started_at": "2025-01-15T14:00:10Z",
      "completed_at": "2025-01-15T14:01:30Z",
      "output": { ... }
    },
    "process_data": {
      "status": "running",
      "started_at": "2025-01-15T14:01:35Z",
      "completed_at": null
    },
    "generate_report": {
      "status": "pending",
      "started_at": null,
      "completed_at": null
    }
  }
}
```

### List Executions

Retrieve a list of workflow executions.

```
GET /executions
```

#### Query Parameters

| Name | Type | Description |
|------|------|------------|
| `workflow_id` | string | Filter by workflow ID |
| `status` | string | Filter by status ("pending", "running", "completed", "failed") |
| `page` | integer | Page number for pagination (default: 1) |
| `limit` | integer | Number of items per page (default: 20) |

#### Response

```json
{
  "items": [
    {
      "execution_id": "exec-123e4567-e89b-12d3-a456-426614174000",
      "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
      "status": "running",
      "created_at": "2025-01-15T14:00:00Z",
      "updated_at": "2025-01-15T14:05:00Z",
      "started_at": "2025-01-15T14:00:10Z",
      "completed_at": null
    },
    { ... }
  ],
  "total": 28,
  "page": 1,
  "limit": 20
}
```

### Cancel Execution

Cancel a running workflow execution.

```
POST /executions/{execution_id}/cancel
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `execution_id` | string | path | The unique identifier of the execution |

#### Response

```json
{
  "success": true,
  "message": "Execution cancellation requested",
  "execution_id": "exec-123e4567-e89b-12d3-a456-426614174000",
  "status": "cancelling"
}
```

## Templates API

### Create Template

Create a workflow template from an existing workflow or a new definition.

```
POST /templates
```

#### Request Body

```json
{
  "name": "data_processing_template",
  "description": "Template for data processing workflows",
  "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "parameters": {
    "data_url": {
      "type": "string",
      "format": "uri",
      "description": "URL to the data file",
      "required": true
    },
    "output_file": {
      "type": "string",
      "description": "Path to save the downloaded file",
      "required": true
    },
    "analysis_type": {
      "type": "string",
      "enum": ["basic", "detailed", "comprehensive"],
      "default": "basic",
      "description": "Type of analysis to perform"
    }
  }
}
```

#### Response

```json
{
  "template_id": "tmpl-123e4567-e89b-12d3-a456-426614174000",
  "name": "data_processing_template",
  "description": "Template for data processing workflows",
  "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2025-01-15T15:00:00Z",
  "updated_at": "2025-01-15T15:00:00Z",
  "parameters": { ... }
}
```

### Instantiate Template

Create a workflow instance from a template.

```
POST /templates/{template_id}/instantiate
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `template_id` | string | path | The unique identifier of the template |

#### Request Body

```json
{
  "name": "monthly_data_processing",
  "description": "January 2025 data processing workflow",
  "parameter_values": {
    "data_url": "https://example.com/data/jan2025.csv",
    "output_file": "/tmp/jan2025.csv",
    "analysis_type": "comprehensive"
  }
}
```

#### Response

```json
{
  "workflow_id": "wf-abcde123-f456-789d-e012-3456789abcde",
  "template_id": "tmpl-123e4567-e89b-12d3-a456-426614174000",
  "name": "monthly_data_processing",
  "description": "January 2025 data processing workflow",
  "created_at": "2025-01-15T15:30:00Z",
  "updated_at": "2025-01-15T15:30:00Z",
  "tasks": { ... },
  "input_schema": { ... }
}
```

## State API

### Create Checkpoint

Create a checkpoint of the current workflow execution state.

```
POST /state/checkpoints
```

#### Request Body

```json
{
  "execution_id": "exec-123e4567-e89b-12d3-a456-426614174000",
  "name": "mid-processing-checkpoint",
  "description": "Checkpoint before report generation"
}
```

#### Response

```json
{
  "checkpoint_id": "cp-123e4567-e89b-12d3-a456-426614174000",
  "execution_id": "exec-123e4567-e89b-12d3-a456-426614174000",
  "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "name": "mid-processing-checkpoint",
  "description": "Checkpoint before report generation",
  "created_at": "2025-01-15T16:00:00Z",
  "task_states": {
    "fetch_data": {
      "status": "completed",
      "output": { ... }
    },
    "process_data": {
      "status": "completed",
      "output": { ... }
    },
    "generate_report": {
      "status": "pending"
    }
  }
}
```

### Restore from Checkpoint

Restore a workflow execution from a checkpoint.

```
POST /state/restore
```

#### Request Body

```json
{
  "checkpoint_id": "cp-123e4567-e89b-12d3-a456-426614174000",
  "execution_options": {
    "async": true,
    "timeout": 1800
  }
}
```

#### Response

```json
{
  "execution_id": "exec-abcde123-f456-789d-e012-3456789abcde",
  "checkpoint_id": "cp-123e4567-e89b-12d3-a456-426614174000",
  "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "status": "running",
  "created_at": "2025-01-15T16:30:00Z",
  "updated_at": "2025-01-15T16:30:00Z",
  "started_at": "2025-01-15T16:30:05Z",
  "task_status": {
    "fetch_data": {
      "status": "completed",
      "started_at": "2025-01-15T14:00:10Z",
      "completed_at": "2025-01-15T14:01:30Z",
      "output": { ... }
    },
    "process_data": {
      "status": "completed",
      "started_at": "2025-01-15T14:01:35Z",
      "completed_at": "2025-01-15T14:10:00Z",
      "output": { ... }
    },
    "generate_report": {
      "status": "running",
      "started_at": "2025-01-15T16:30:10Z",
      "completed_at": null
    }
  }
}
```

## WebSocket API

The WebSocket API provides real-time interaction with workflow executions.

### Connection

```
ws://localhost:8002/ws/harmonia/executions/{execution_id}
```

Connection requires authentication using either:

- Query parameter: `?api_key=your_api_key_here`
- Header: Include auth token in the connection headers

### Message Format

All WebSocket messages use the following JSON format:

```json
{
  "type": "event_type",
  "timestamp": "2025-01-15T16:45:00Z",
  "execution_id": "exec-abcde123-f456-789d-e012-3456789abcde",
  "data": {  // Event-specific payload
    ...
  }
}
```

### Event Types

#### Execution Started

```json
{
  "type": "execution_started",
  "timestamp": "2025-01-15T16:30:05Z",
  "execution_id": "exec-abcde123-f456-789d-e012-3456789abcde",
  "data": {
    "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
    "workflow_name": "data_processing_workflow"
  }
}
```

#### Task Started

```json
{
  "type": "task_started",
  "timestamp": "2025-01-15T16:30:10Z",
  "execution_id": "exec-abcde123-f456-789d-e012-3456789abcde",
  "data": {
    "task_name": "generate_report",
    "task_index": 2,
    "total_tasks": 3
  }
}
```

#### Task Progress

```json
{
  "type": "task_progress",
  "timestamp": "2025-01-15T16:32:00Z",
  "execution_id": "exec-abcde123-f456-789d-e012-3456789abcde",
  "data": {
    "task_name": "generate_report",
    "progress": 0.5,
    "message": "Generating report sections"
  }
}
```

#### Task Completed

```json
{
  "type": "task_completed",
  "timestamp": "2025-01-15T16:35:00Z",
  "execution_id": "exec-abcde123-f456-789d-e012-3456789abcde",
  "data": {
    "task_name": "generate_report",
    "task_index": 2,
    "total_tasks": 3,
    "output": {
      "report_file": "/tmp/report.pdf",
      "sections": 5,
      "generated_charts": 3
    }
  }
}
```

#### Task Failed

```json
{
  "type": "task_failed",
  "timestamp": "2025-01-15T16:35:00Z",
  "execution_id": "exec-abcde123-f456-789d-e012-3456789abcde",
  "data": {
    "task_name": "generate_report",
    "error": "Failed to generate report: file not found",
    "error_details": {
      "code": "FILE_NOT_FOUND",
      "file": "/tmp/data.csv"
    },
    "retry_count": 1,
    "max_retries": 3
  }
}
```

#### Execution Completed

```json
{
  "type": "execution_completed",
  "timestamp": "2025-01-15T16:35:00Z",
  "execution_id": "exec-abcde123-f456-789d-e012-3456789abcde",
  "data": {
    "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
    "workflow_name": "data_processing_workflow",
    "duration_seconds": 300,
    "output": {
      "report_file": "/tmp/report.pdf",
      "analysis_results": { ... }
    }
  }
}
```

## Server-Sent Events API

The Server-Sent Events (SSE) API provides an alternative to WebSockets for real-time updates.

### Connection

```
http://localhost:8002/events/harmonia/executions/{execution_id}
```

### Event Format

```
event: task_started
data: {"task_name":"generate_report","task_index":2,"total_tasks":3}

event: task_progress
data: {"task_name":"generate_report","progress":0.5,"message":"Generating report sections"}

event: task_completed
data: {"task_name":"generate_report","task_index":2,"total_tasks":3,"output":{...}}
```

## Error Responses

All endpoints follow a standard error response format:

```json
{
  "error": {
    "code": "workflow_not_found",
    "message": "Workflow with ID 'wf-invalid' not found",
    "details": {
      "requested_id": "wf-invalid"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|------------|
| `invalid_request` | 400 | The request was malformed or invalid |
| `authentication_failed` | 401 | Authentication credentials were missing or invalid |
| `permission_denied` | 403 | The authenticated user lacks permission for the requested operation |
| `workflow_not_found` | 404 | The requested workflow was not found |
| `execution_not_found` | 404 | The requested execution was not found |
| `template_not_found` | 404 | The requested template was not found |
| `checkpoint_not_found` | 404 | The requested checkpoint was not found |
| `validation_error` | 422 | The request failed validation checks |
| `component_error` | 500 | An error occurred in a component being orchestrated |
| `execution_error` | 500 | An error occurred during workflow execution |
| `conflict` | 409 | The request conflicts with the current state |
| `rate_limit_exceeded` | 429 | The rate limit for API requests has been exceeded |