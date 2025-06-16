# Telos API Reference

This document provides a comprehensive reference for the Telos API, which enables programmatic interaction with the requirements management system.

## Base URL

All API endpoints are relative to:

```
http://localhost:8008/api
```

## Authentication

*Note: Authentication is planned for future releases and not currently implemented.*

## Response Format

All responses follow a standard format:

**Success Response:**
```json
{
  "status": "success",
  "data": { ... },
  "message": "Optional success message"
}
```

**Error Response:**
```json
{
  "status": "error",
  "error_code": "ERROR_CODE",
  "message": "Error message"
}
```

## Common Error Codes

- `INVALID_INPUT`: The request contains invalid data
- `RESOURCE_NOT_FOUND`: The requested resource does not exist
- `DUPLICATE_RESOURCE`: A resource with the same identifier already exists
- `DEPENDENCY_ERROR`: Operation failed due to a dependency constraint
- `INTERNAL_ERROR`: An unexpected error occurred in the server

## Project Endpoints

### Create a Project

```
POST /projects
```

**Request Body:**
```json
{
  "name": "My Project",
  "description": "A comprehensive project for requirement tracking",
  "metadata": {
    "owner": "Jane Smith",
    "department": "Engineering"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "project_id": "proj-123abc",
    "name": "My Project",
    "description": "A comprehensive project for requirement tracking",
    "created_at": "2025-04-15T08:30:00Z",
    "updated_at": "2025-04-15T08:30:00Z",
    "metadata": {
      "owner": "Jane Smith",
      "department": "Engineering"
    }
  },
  "message": "Project created successfully"
}
```

### List Projects

```
GET /projects
```

**Query Parameters:**
- `limit` (optional): Maximum number of projects to return (default: 50)
- `offset` (optional): Offset for pagination (default: 0)
- `search` (optional): Search term for project name or description

**Response:**
```json
{
  "status": "success",
  "data": {
    "projects": [
      {
        "project_id": "proj-123abc",
        "name": "My Project",
        "description": "A comprehensive project for requirement tracking",
        "created_at": "2025-04-15T08:30:00Z",
        "updated_at": "2025-04-15T08:30:00Z",
        "requirement_count": 42
      },
      {
        "project_id": "proj-456def",
        "name": "Another Project",
        "description": "Second project for testing",
        "created_at": "2025-04-14T10:15:00Z",
        "updated_at": "2025-04-15T09:20:00Z",
        "requirement_count": 17
      }
    ],
    "total": 2,
    "limit": 50,
    "offset": 0
  }
}
```

### Get Project by ID

```
GET /projects/{project_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "project_id": "proj-123abc",
    "name": "My Project",
    "description": "A comprehensive project for requirement tracking",
    "created_at": "2025-04-15T08:30:00Z",
    "updated_at": "2025-04-15T08:30:00Z",
    "metadata": {
      "owner": "Jane Smith",
      "department": "Engineering"
    },
    "requirement_count": 42,
    "requirement_stats": {
      "by_status": {
        "new": 10,
        "in_progress": 15,
        "completed": 12,
        "on_hold": 5
      },
      "by_type": {
        "functional": 30,
        "non_functional": 8,
        "constraint": 4
      },
      "by_priority": {
        "low": 5,
        "medium": 20,
        "high": 15,
        "critical": 2
      }
    }
  }
}
```

### Update Project

```
PUT /projects/{project_id}
```

**Request Body:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated project description",
  "metadata": {
    "owner": "John Doe",
    "department": "Engineering",
    "status": "active"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "project_id": "proj-123abc",
    "name": "Updated Project Name",
    "description": "Updated project description",
    "created_at": "2025-04-15T08:30:00Z",
    "updated_at": "2025-04-15T09:45:00Z",
    "metadata": {
      "owner": "John Doe",
      "department": "Engineering",
      "status": "active"
    }
  },
  "message": "Project updated successfully"
}
```

### Delete Project

```
DELETE /projects/{project_id}
```

**Response:**
```json
{
  "status": "success",
  "message": "Project deleted successfully"
}
```

## Requirement Endpoints

### Create a Requirement

```
POST /projects/{project_id}/requirements
```

**Request Body:**
```json
{
  "title": "User Authentication",
  "description": "The system shall authenticate users with username and password",
  "requirement_type": "functional",
  "priority": "high",
  "status": "new",
  "tags": ["security", "user-management"],
  "parent_id": null,
  "dependencies": [],
  "metadata": {
    "source": "Stakeholder meeting",
    "author": "Jane Smith",
    "verification_method": "Manual testing"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "requirement_id": "req-789xyz",
    "project_id": "proj-123abc",
    "title": "User Authentication",
    "description": "The system shall authenticate users with username and password",
    "requirement_type": "functional",
    "priority": "high",
    "status": "new",
    "tags": ["security", "user-management"],
    "parent_id": null,
    "dependencies": [],
    "created_at": "2025-04-15T10:00:00Z",
    "updated_at": "2025-04-15T10:00:00Z",
    "metadata": {
      "source": "Stakeholder meeting",
      "author": "Jane Smith",
      "verification_method": "Manual testing"
    }
  },
  "message": "Requirement created successfully"
}
```

### List Requirements

```
GET /projects/{project_id}/requirements
```

**Query Parameters:**
- `limit` (optional): Maximum number of requirements to return (default: 100)
- `offset` (optional): Offset for pagination (default: 0)
- `status` (optional): Filter by status
- `type` (optional): Filter by requirement type
- `priority` (optional): Filter by priority
- `tag` (optional): Filter by tag
- `parent_id` (optional): Filter by parent requirement ID
- `search` (optional): Search term for title or description
- `include_children` (optional): Whether to include child requirements (default: false)

**Response:**
```json
{
  "status": "success",
  "data": {
    "requirements": [
      {
        "requirement_id": "req-789xyz",
        "project_id": "proj-123abc",
        "title": "User Authentication",
        "description": "The system shall authenticate users with username and password",
        "requirement_type": "functional",
        "priority": "high",
        "status": "new",
        "tags": ["security", "user-management"],
        "parent_id": null,
        "dependencies": [],
        "created_at": "2025-04-15T10:00:00Z",
        "updated_at": "2025-04-15T10:00:00Z"
      },
      {
        "requirement_id": "req-abc123",
        "project_id": "proj-123abc",
        "title": "Password Complexity",
        "description": "Passwords must contain at least 8 characters including uppercase, lowercase, number, and special character",
        "requirement_type": "non_functional",
        "priority": "medium",
        "status": "new",
        "tags": ["security", "user-management"],
        "parent_id": "req-789xyz",
        "dependencies": [],
        "created_at": "2025-04-15T10:05:00Z",
        "updated_at": "2025-04-15T10:05:00Z"
      }
    ],
    "total": 42,
    "limit": 100,
    "offset": 0
  }
}
```

### Get Requirement by ID

```
GET /projects/{project_id}/requirements/{requirement_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "requirement_id": "req-789xyz",
    "project_id": "proj-123abc",
    "title": "User Authentication",
    "description": "The system shall authenticate users with username and password",
    "requirement_type": "functional",
    "priority": "high",
    "status": "new",
    "tags": ["security", "user-management"],
    "parent_id": null,
    "dependencies": [],
    "created_at": "2025-04-15T10:00:00Z",
    "updated_at": "2025-04-15T10:00:00Z",
    "metadata": {
      "source": "Stakeholder meeting",
      "author": "Jane Smith",
      "verification_method": "Manual testing"
    },
    "children": [
      {
        "requirement_id": "req-abc123",
        "title": "Password Complexity",
        "requirement_type": "non_functional",
        "priority": "medium",
        "status": "new"
      }
    ],
    "dependents": [],
    "history": [
      {
        "action": "created",
        "timestamp": "2025-04-15T10:00:00Z",
        "user": "jane.smith@example.com",
        "details": "Initial creation"
      }
    ],
    "validation_results": {
      "passed": true,
      "score": 0.85,
      "issues": []
    }
  }
}
```

### Update Requirement

```
PUT /projects/{project_id}/requirements/{requirement_id}
```

**Request Body:**
```json
{
  "title": "User Authentication System",
  "description": "The system shall authenticate users with username and password, and support 2FA",
  "priority": "critical",
  "status": "in_progress",
  "tags": ["security", "user-management", "2fa"],
  "metadata": {
    "source": "Security review",
    "author": "Jane Smith",
    "verification_method": "Automated testing",
    "acceptance_criteria": "All login attempts must be logged"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "requirement_id": "req-789xyz",
    "project_id": "proj-123abc",
    "title": "User Authentication System",
    "description": "The system shall authenticate users with username and password, and support 2FA",
    "requirement_type": "functional",
    "priority": "critical",
    "status": "in_progress",
    "tags": ["security", "user-management", "2fa"],
    "parent_id": null,
    "dependencies": [],
    "created_at": "2025-04-15T10:00:00Z",
    "updated_at": "2025-04-15T11:30:00Z",
    "metadata": {
      "source": "Security review",
      "author": "Jane Smith",
      "verification_method": "Automated testing",
      "acceptance_criteria": "All login attempts must be logged"
    }
  },
  "message": "Requirement updated successfully"
}
```

### Delete Requirement

```
DELETE /projects/{project_id}/requirements/{requirement_id}
```

**Response:**
```json
{
  "status": "success",
  "message": "Requirement deleted successfully"
}
```

## Trace Endpoints

### Create a Trace

```
POST /projects/{project_id}/traces
```

**Request Body:**
```json
{
  "source_id": "req-789xyz",
  "target_id": "req-def456",
  "trace_type": "depends_on",
  "description": "User authentication is required before user role management"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "trace_id": "trace-123abc",
    "source_id": "req-789xyz",
    "target_id": "req-def456",
    "trace_type": "depends_on",
    "description": "User authentication is required before user role management",
    "created_at": "2025-04-15T12:00:00Z"
  },
  "message": "Trace created successfully"
}
```

### List Traces

```
GET /projects/{project_id}/traces
```

**Query Parameters:**
- `source_id` (optional): Filter by source requirement ID
- `target_id` (optional): Filter by target requirement ID
- `trace_type` (optional): Filter by trace type

**Response:**
```json
{
  "status": "success",
  "data": {
    "traces": [
      {
        "trace_id": "trace-123abc",
        "source_id": "req-789xyz",
        "target_id": "req-def456",
        "trace_type": "depends_on",
        "description": "User authentication is required before user role management",
        "created_at": "2025-04-15T12:00:00Z"
      },
      {
        "trace_id": "trace-456def",
        "source_id": "req-def456",
        "target_id": "req-ghi789",
        "trace_type": "implements",
        "description": "User role management implements the authorization requirement",
        "created_at": "2025-04-15T12:05:00Z"
      }
    ],
    "total": 2
  }
}
```

### Get Trace by ID

```
GET /projects/{project_id}/traces/{trace_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "trace_id": "trace-123abc",
    "source_id": "req-789xyz",
    "target_id": "req-def456",
    "trace_type": "depends_on",
    "description": "User authentication is required before user role management",
    "created_at": "2025-04-15T12:00:00Z",
    "source": {
      "requirement_id": "req-789xyz",
      "title": "User Authentication System",
      "requirement_type": "functional",
      "priority": "critical",
      "status": "in_progress"
    },
    "target": {
      "requirement_id": "req-def456",
      "title": "User Role Management",
      "requirement_type": "functional",
      "priority": "high",
      "status": "new"
    }
  }
}
```

### Update Trace

```
PUT /projects/{project_id}/traces/{trace_id}
```

**Request Body:**
```json
{
  "trace_type": "related_to",
  "description": "User authentication is related to user role management"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "trace_id": "trace-123abc",
    "source_id": "req-789xyz",
    "target_id": "req-def456",
    "trace_type": "related_to",
    "description": "User authentication is related to user role management",
    "created_at": "2025-04-15T12:00:00Z",
    "updated_at": "2025-04-15T13:30:00Z"
  },
  "message": "Trace updated successfully"
}
```

### Delete Trace

```
DELETE /projects/{project_id}/traces/{trace_id}
```

**Response:**
```json
{
  "status": "success",
  "message": "Trace deleted successfully"
}
```

## Validation Endpoints

### Validate Requirements

```
POST /projects/{project_id}/validate
```

**Request Body:**
```json
{
  "requirement_ids": ["req-789xyz", "req-abc123"],
  "validation_types": ["completeness", "clarity", "testability"]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "validation_results": [
      {
        "requirement_id": "req-789xyz",
        "title": "User Authentication System",
        "passed": true,
        "score": 0.85,
        "issues": []
      },
      {
        "requirement_id": "req-abc123",
        "title": "Password Complexity",
        "passed": false,
        "score": 0.62,
        "issues": [
          {
            "type": "clarity",
            "message": "The description is ambiguous about special character requirements",
            "severity": "warning",
            "suggestion": "Specify which special characters are allowed or required"
          }
        ]
      }
    ],
    "overall_score": 0.74
  }
}
```

## Export/Import Endpoints

### Export Project

```
POST /projects/{project_id}/export
```

**Request Body:**
```json
{
  "format": "json",
  "include_history": true,
  "include_traces": true
}
```

**Response:**
A file download containing the project data in the requested format.

### Import Project

```
POST /projects/import
```

**Request Body:**
Multipart form data with a file upload containing the project data.

**Response:**
```json
{
  "status": "success",
  "data": {
    "project_id": "proj-newid",
    "name": "Imported Project",
    "requirement_count": 42,
    "trace_count": 15
  },
  "message": "Project imported successfully"
}
```

## Planning Integration Endpoints

### Analyze Requirements for Planning

```
POST /projects/{project_id}/analyze
```

**Request Body:**
```json
{
  "requirement_ids": ["req-789xyz", "req-abc123"],
  "analysis_types": ["complexity", "dependencies", "estimation"]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "analysis_results": {
      "complexity": {
        "overall": "medium",
        "by_requirement": {
          "req-789xyz": "high",
          "req-abc123": "low"
        }
      },
      "dependencies": {
        "explicit": 1,
        "implicit": 2,
        "graph": {
          "nodes": ["req-789xyz", "req-abc123", "req-def456"],
          "edges": [
            {"source": "req-789xyz", "target": "req-abc123", "type": "parent_child"},
            {"source": "req-789xyz", "target": "req-def456", "type": "implicit_dependency"}
          ]
        }
      },
      "estimation": {
        "total_effort": "15 person-days",
        "by_requirement": {
          "req-789xyz": "10 person-days",
          "req-abc123": "5 person-days"
        }
      }
    },
    "planning_readiness": 0.85,
    "recommendations": [
      "Clarify the password complexity requirement",
      "Add explicit dependency between authentication and role management"
    ]
  }
}
```

### Create Plan from Requirements

```
POST /projects/{project_id}/plan
```

**Request Body:**
```json
{
  "requirement_ids": ["req-789xyz", "req-abc123", "req-def456"],
  "plan_name": "Authentication Implementation Plan",
  "plan_description": "Implementation plan for the authentication features",
  "target_start_date": "2025-05-01T00:00:00Z",
  "target_end_date": "2025-05-31T00:00:00Z"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "plan_id": "plan-123abc",
    "name": "Authentication Implementation Plan",
    "description": "Implementation plan for the authentication features",
    "start_date": "2025-05-01T00:00:00Z",
    "end_date": "2025-05-31T00:00:00Z",
    "task_count": 8,
    "prometheus_url": "http://localhost:8006/api/plans/plan-123abc"
  },
  "message": "Plan created successfully"
}
```

## WebSocket API

Telos provides a WebSocket API for real-time updates and collaborative editing.

### Connection

```
WebSocket: ws://localhost:8008/ws
```

### Message Format

All WebSocket messages follow this format:

```json
{
  "type": "MESSAGE_TYPE",
  "source": "client or server",
  "target": "server or client",
  "timestamp": 1682456789123,
  "payload": {
    // Message-specific data
  }
}
```

### Message Types

#### Client to Server

- `REGISTER`: Register a client with the server
- `PROJECT_SUBSCRIBE`: Subscribe to updates for a project
- `REQUIREMENT_SUBSCRIBE`: Subscribe to updates for a specific requirement
- `REQUIREMENT_UPDATE`: Update a requirement (collaborative editing)
- `STATUS`: Request server status

#### Server to Client

- `WELCOME`: Welcome message after successful connection
- `PROJECT_UPDATE`: Real-time update to a project
- `REQUIREMENT_UPDATE`: Real-time update to a requirement
- `TRACE_UPDATE`: Real-time update to a trace
- `ERROR`: Error message

### Example Messages

**Client Registration:**
```json
{
  "type": "REGISTER",
  "source": "client",
  "target": "server",
  "timestamp": 1682456789123,
  "payload": {
    "client_id": "client-123",
    "user_info": {
      "name": "Jane Smith",
      "email": "jane.smith@example.com"
    }
  }
}
```

**Server Welcome:**
```json
{
  "type": "WELCOME",
  "source": "server",
  "target": "client",
  "timestamp": 1682456789456,
  "payload": {
    "client_id": "client-123",
    "message": "Connected to Telos Requirements Manager",
    "server_version": "1.0.0"
  }
}
```

**Project Subscription:**
```json
{
  "type": "PROJECT_SUBSCRIBE",
  "source": "client",
  "target": "server",
  "timestamp": 1682456790123,
  "payload": {
    "project_id": "proj-123abc"
  }
}
```

**Requirement Update Notification:**
```json
{
  "type": "REQUIREMENT_UPDATE",
  "source": "server",
  "target": "client",
  "timestamp": 1682456795789,
  "payload": {
    "project_id": "proj-123abc",
    "requirement_id": "req-789xyz",
    "action": "updated",
    "user": "john.doe@example.com",
    "changes": {
      "title": {
        "old": "User Authentication",
        "new": "User Authentication System"
      },
      "priority": {
        "old": "high",
        "new": "critical"
      }
    }
  }
}
```

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate)
- `500 Internal Server Error`: Server error

Error responses include detailed information:

```json
{
  "status": "error",
  "error_code": "INVALID_DEPENDENCY",
  "message": "Cannot create dependency: circular reference detected",
  "details": {
    "requirement_id": "req-789xyz",
    "dependency_id": "req-def456",
    "path": ["req-789xyz", "req-def456", "req-ghi789", "req-789xyz"]
  }
}
```

## Versioning

The API version is included in the response headers:

```
X-Telos-Version: 1.0.0
```

Future breaking changes will be managed through API versioning.