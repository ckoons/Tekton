# Metis API Reference

This document provides a comprehensive reference for the Metis API, including endpoint specifications, request/response formats, and usage examples.

## Base URL

The Metis API is available at:

```
http://localhost:8011
```

The port can be configured using the `METIS_PORT` environment variable.

## Authentication

Authentication is currently managed through Tekton's central authentication system. All requests should include the appropriate authentication headers as required by your Tekton deployment.

## Response Format

All API responses follow a consistent format:

### Success Response

```json
{
  "success": true,
  "message": "Optional success message",
  "data": { ... } // Response data
}
```

### Error Response

```json
{
  "success": false,
  "message": "Error message",
  "status_code": 400
}
```

## API Endpoints

### Common Endpoints

#### Root Endpoint

```
GET /
```

Returns basic information about the Metis service.

Response:
```json
{
  "name": "Metis",
  "description": "Task Management System for Tekton",
  "version": "0.1.0",
  "status": "running"
}
```

#### Health Check

```
GET /health
```

Returns the health status of the Metis service.

Response:
```json
{
  "status": "healthy",
  "service": "Metis",
  "version": "0.1.0"
}
```

### Task Management

#### List Tasks

```
GET /api/v1/tasks
```

List tasks with optional filtering.

Query Parameters:
- `status` (optional) - Filter by status (pending, in_progress, review, done, blocked, cancelled)
- `priority` (optional) - Filter by priority (high, medium, low)
- `assignee` (optional) - Filter by assignee
- `tag` (optional) - Filter by tag
- `search` (optional) - Search term for title/description
- `page` (optional, default: 1) - Page number
- `page_size` (optional, default: 50) - Page size

Response:
```json
{
  "success": true,
  "tasks": [
    {
      "id": "task-123",
      "title": "Task Title",
      "description": "Task Description",
      "status": "pending",
      "priority": "medium",
      "details": "Implementation details...",
      "test_strategy": "Testing strategy...",
      "dependencies": ["task-456"],
      "tags": ["feature", "backend"],
      "assignee": "user1",
      "due_date": "2025-05-30T00:00:00.000Z",
      "created_at": "2025-05-15T14:30:00.000Z",
      "updated_at": "2025-05-15T14:30:00.000Z",
      "subtasks": [...],
      "requirement_refs": [...],
      "complexity": {...},
      "progress": 25.0
    },
    ...
  ],
  "total": 42,
  "page": 1,
  "page_size": 50
}
```

#### Get Task

```
GET /api/v1/tasks/{task_id}
```

Get details of a specific task.

Response:
```json
{
  "success": true,
  "task": {
    "id": "task-123",
    "title": "Task Title",
    "description": "Task Description",
    "status": "pending",
    "priority": "medium",
    "details": "Implementation details...",
    "test_strategy": "Testing strategy...",
    "dependencies": ["task-456"],
    "tags": ["feature", "backend"],
    "assignee": "user1",
    "due_date": "2025-05-30T00:00:00.000Z",
    "created_at": "2025-05-15T14:30:00.000Z",
    "updated_at": "2025-05-15T14:30:00.000Z",
    "subtasks": [...],
    "requirement_refs": [...],
    "complexity": {...},
    "progress": 25.0
  }
}
```

#### Create Task

```
POST /api/v1/tasks
```

Create a new task.

Request Body:
```json
{
  "title": "New Task",
  "description": "Task description",
  "status": "pending",
  "priority": "medium",
  "details": "Implementation details...",
  "test_strategy": "Testing strategy...",
  "dependencies": ["task-456"],
  "tags": ["feature", "backend"],
  "assignee": "user1",
  "due_date": "2025-05-30T00:00:00.000Z",
  "subtasks": [
    {
      "title": "Subtask 1",
      "description": "Subtask description",
      "status": "pending"
    }
  ]
}
```

Response:
```json
{
  "id": "task-123",
  "title": "New Task",
  "description": "Task description",
  "status": "pending",
  "priority": "medium",
  "details": "Implementation details...",
  "test_strategy": "Testing strategy...",
  "dependencies": ["task-456"],
  "tags": ["feature", "backend"],
  "assignee": "user1",
  "due_date": "2025-05-30T00:00:00.000Z",
  "created_at": "2025-05-15T14:30:00.000Z",
  "updated_at": "2025-05-15T14:30:00.000Z",
  "subtasks": [...],
  "requirement_refs": [],
  "complexity": null,
  "progress": 0.0
}
```

#### Update Task

```
PUT /api/v1/tasks/{task_id}
```

Update an existing task.

Request Body:
```json
{
  "title": "Updated Task Title",
  "status": "in_progress",
  "priority": "high"
}
```

Response:
```json
{
  "id": "task-123",
  "title": "Updated Task Title",
  "description": "Task description",
  "status": "in_progress",
  "priority": "high",
  "details": "Implementation details...",
  "test_strategy": "Testing strategy...",
  "dependencies": ["task-456"],
  "tags": ["feature", "backend"],
  "assignee": "user1",
  "due_date": "2025-05-30T00:00:00.000Z",
  "created_at": "2025-05-15T14:30:00.000Z",
  "updated_at": "2025-05-15T14:35:00.000Z",
  "subtasks": [...],
  "requirement_refs": [],
  "complexity": null,
  "progress": 50.0
}
```

#### Delete Task

```
DELETE /api/v1/tasks/{task_id}
```

Delete a task.

Response:
```json
{
  "success": true,
  "message": "Task task-123 deleted successfully"
}
```

### Subtask Management

#### Add Subtask

```
POST /api/v1/tasks/{task_id}/subtasks
```

Add a subtask to a task.

Request Body:
```json
{
  "title": "New Subtask",
  "description": "Subtask description",
  "status": "pending",
  "order": 1
}
```

Response: The updated parent task with the new subtask included.

#### Update Subtask

```
PUT /api/v1/tasks/{task_id}/subtasks/{subtask_id}
```

Update a subtask.

Request Body:
```json
{
  "title": "Updated Subtask",
  "status": "in_progress"
}
```

Response: The updated parent task with the modified subtask.

#### Remove Subtask

```
DELETE /api/v1/tasks/{task_id}/subtasks/{subtask_id}
```

Remove a subtask from a task.

Response: The updated parent task with the subtask removed.

### Requirement References

#### Add Requirement Reference

```
POST /api/v1/tasks/{task_id}/requirements
```

Add a requirement reference to a task.

Request Body:
```json
{
  "requirement_id": "req-123",
  "source": "telos",
  "requirement_type": "functional",
  "title": "Requirement Title",
  "relationship": "implements",
  "description": "Requirement description"
}
```

Response: The updated parent task with the new requirement reference included.

#### Update Requirement Reference

```
PUT /api/v1/tasks/{task_id}/requirements/{ref_id}
```

Update a requirement reference.

Request Body:
```json
{
  "title": "Updated Requirement",
  "relationship": "related_to"
}
```

Response: The updated parent task with the modified requirement reference.

#### Remove Requirement Reference

```
DELETE /api/v1/tasks/{task_id}/requirements/{ref_id}
```

Remove a requirement reference from a task.

Response: The updated parent task with the requirement reference removed.

### Dependencies

#### List Dependencies

```
GET /api/v1/dependencies
```

List dependencies with optional filtering.

Query Parameters:
- `task_id` (optional) - Filter by source or target task ID
- `dependency_type` (optional) - Filter by dependency type

Response:
```json
{
  "success": true,
  "dependencies": [
    {
      "id": "dep-123",
      "source_task_id": "task-123",
      "target_task_id": "task-456",
      "dependency_type": "blocks",
      "description": "Task 123 blocks Task 456",
      "created_at": "2025-05-15T14:30:00.000Z",
      "updated_at": "2025-05-15T14:30:00.000Z"
    },
    ...
  ]
}
```

#### List Task Dependencies

```
GET /api/v1/tasks/{task_id}/dependencies
```

List dependencies for a specific task.

Response: Same as List Dependencies, filtered for the specified task.

#### Create Dependency

```
POST /api/v1/dependencies
```

Create a new dependency between tasks.

Request Body:
```json
{
  "source_task_id": "task-123",
  "target_task_id": "task-456",
  "dependency_type": "blocks",
  "description": "Task 123 blocks Task 456"
}
```

Response:
```json
{
  "id": "dep-123",
  "source_task_id": "task-123",
  "target_task_id": "task-456",
  "dependency_type": "blocks",
  "description": "Task 123 blocks Task 456",
  "created_at": "2025-05-15T14:30:00.000Z",
  "updated_at": "2025-05-15T14:30:00.000Z"
}
```

#### Get Dependency

```
GET /api/v1/dependencies/{dependency_id}
```

Get details of a specific dependency.

Response: The dependency object as shown above.

#### Update Dependency

```
PUT /api/v1/dependencies/{dependency_id}
```

Update a dependency.

Request Body:
```json
{
  "dependency_type": "depends_on",
  "description": "Task 456 depends on Task 123"
}
```

Response: The updated dependency object.

#### Delete Dependency

```
DELETE /api/v1/dependencies/{dependency_id}
```

Delete a dependency.

Response:
```json
{
  "success": true,
  "message": "Dependency dep-123 deleted successfully"
}
```

### Telos Integration

#### Search Telos Requirements

```
GET /api/v1/telos/requirements
```

Search for requirements in the Telos system.

Query Parameters:
- `query` (optional) - Search query
- `status` (optional) - Filter by status
- `category` (optional) - Filter by category
- `page` (optional, default: 1) - Page number
- `page_size` (optional, default: 50) - Page size

Response:
```json
{
  "success": true,
  "requirements": [
    {
      "id": "req-123",
      "title": "Requirement Title",
      "description": "Requirement description",
      "type": "functional",
      "status": "approved",
      "category": "core"
    },
    ...
  ],
  "total": 42,
  "page": 1,
  "page_size": 50
}
```

#### Import Requirement as Task

```
POST /api/v1/telos/requirements/{requirement_id}/import
```

Import a requirement from Telos as a new task.

Response: The created task object.

#### Add Telos Requirement Reference

```
POST /api/v1/tasks/{task_id}/telos/requirements/{requirement_id}
```

Add a reference to a Telos requirement to a task.

Response: The updated task object with the new requirement reference.

## WebSocket Interface

### Connection

Connect to the WebSocket endpoint:

```
ws://localhost:8011/ws
```

### Registration

After connecting, send a registration message:

```json
{
  "client_id": "client-123",
  "subscribe_to": ["task_created", "task_updated", "task_deleted"]
}
```

Response:
```json
{
  "type": "registration_success",
  "data": {
    "client_id": "client-123",
    "subscriptions": ["task_created", "task_updated", "task_deleted"]
  }
}
```

### Event Messages

You'll receive event messages based on your subscriptions:

```json
{
  "type": "task_created",
  "data": {
    "id": "task-123",
    "title": "New Task",
    ...
  }
}
```

```json
{
  "type": "task_updated",
  "data": {
    "id": "task-123",
    "title": "Updated Task",
    ...
  }
}
```

```json
{
  "type": "task_deleted",
  "data": {
    "id": "task-123"
  }
}
```

### Ping

You can send a ping message to keep the connection alive:

```json
{
  "type": "ping",
  "data": {}
}
```

Response:
```json
{
  "type": "pong",
  "data": {}
}
```

### Subscribe/Unsubscribe

You can update your subscriptions:

```json
{
  "type": "subscribe",
  "data": {
    "event_types": ["dependency_created", "dependency_deleted"]
  }
}
```

```json
{
  "type": "unsubscribe",
  "data": {
    "event_types": ["task_deleted"]
  }
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- 200 OK: The request was successful
- 201 Created: The resource was successfully created
- 400 Bad Request: The request was invalid or malformed
- 404 Not Found: The requested resource was not found
- 422 Unprocessable Entity: The request was valid but contained invalid data
- 500 Internal Server Error: An error occurred on the server

Error responses include the error message and status code to help with debugging.