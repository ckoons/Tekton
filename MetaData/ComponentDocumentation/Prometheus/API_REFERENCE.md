# Prometheus API Reference

This document provides a detailed reference for the Prometheus API endpoints.

## Base URL

All API endpoints are relative to:

```
http://localhost:8006/api
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

- `HTTP_400`: Bad request (invalid input)
- `HTTP_404`: Resource not found
- `HTTP_500`: Internal server error
- `VALIDATION_ERROR`: Input validation failed
- `DEPENDENCY_ERROR`: Operation failed due to dependencies
- `RESOURCE_CONFLICT`: Resource already exists
- `INTERNAL_SERVER_ERROR`: Unexpected error

## Health Check

### Get health status

```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "port": 8006
}
```

## Plans

### Create a plan

```
POST /plans
```

**Request Body:**
```json
{
  "name": "Project Plan",
  "description": "Description of the project plan",
  "start_date": "2025-05-01T00:00:00Z",
  "end_date": "2025-06-30T00:00:00Z",
  "tags": ["engineering", "web-app"],
  "metadata": {
    "priority": "high",
    "project_code": "PRJ-123"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Plan created successfully"
}
```

### List plans

```
GET /plans
```

**Query Parameters:**
- `limit` (optional): Maximum number of plans to return (default: 100)
- `offset` (optional): Offset for pagination (default: 0)
- `tag` (optional): Filter by tag
- `search` (optional): Search term for name or description

**Response:**
```json
{
  "status": "success",
  "data": {
    "plans": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Project Plan",
        "description": "Description of the project plan",
        "start_date": "2025-05-01T00:00:00Z",
        "end_date": "2025-06-30T00:00:00Z",
        "tags": ["engineering", "web-app"],
        "created_at": "2025-04-15T10:30:00Z",
        "updated_at": "2025-04-15T10:30:00Z"
      },
      // ... more plans
    ],
    "total": 15,
    "limit": 10,
    "offset": 0
  }
}
```

### Get plan by ID

```
GET /plans/{plan_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Project Plan",
    "description": "Description of the project plan",
    "start_date": "2025-05-01T00:00:00Z",
    "end_date": "2025-06-30T00:00:00Z",
    "tags": ["engineering", "web-app"],
    "metadata": {
      "priority": "high",
      "project_code": "PRJ-123"
    },
    "created_at": "2025-04-15T10:30:00Z",
    "updated_at": "2025-04-15T10:30:00Z",
    "task_count": 12,
    "resource_count": 5
  }
}
```

### Update plan

```
PUT /plans/{plan_id}
```

**Request Body:**
```json
{
  "name": "Updated Project Plan",
  "description": "Updated description",
  "end_date": "2025-07-15T00:00:00Z",
  "tags": ["engineering", "web-app", "high-priority"]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Updated Project Plan",
    "description": "Updated description",
    "start_date": "2025-05-01T00:00:00Z",
    "end_date": "2025-07-15T00:00:00Z",
    "tags": ["engineering", "web-app", "high-priority"],
    "updated_at": "2025-04-16T14:20:00Z"
  },
  "message": "Plan updated successfully"
}
```

### Delete plan

```
DELETE /plans/{plan_id}
```

**Response:**
```json
{
  "status": "success",
  "message": "Plan deleted successfully"
}
```

## Tasks

### Add task to plan

```
POST /plans/{plan_id}/tasks
```

**Request Body:**
```json
{
  "name": "Design System Architecture",
  "description": "Create the high-level system design",
  "duration": 5,
  "duration_unit": "days",
  "assigned_to": "resource-id-123",
  "dependencies": ["task-id-456"],
  "status": "pending",
  "priority": "high",
  "tags": ["design", "architecture"],
  "metadata": {
    "deliverable": "Architecture document"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "task_id": "task-id-789",
  "message": "Task added successfully"
}
```

### List tasks in plan

```
GET /plans/{plan_id}/tasks
```

**Query Parameters:**
- `limit` (optional): Maximum number of tasks to return (default: 100)
- `offset` (optional): Offset for pagination (default: 0)
- `status` (optional): Filter by status
- `assigned_to` (optional): Filter by assigned resource
- `search` (optional): Search term for name or description

**Response:**
```json
{
  "status": "success",
  "data": {
    "tasks": [
      {
        "id": "task-id-789",
        "name": "Design System Architecture",
        "description": "Create the high-level system design",
        "duration": 5,
        "duration_unit": "days",
        "assigned_to": "resource-id-123",
        "dependencies": ["task-id-456"],
        "status": "pending",
        "priority": "high",
        "tags": ["design", "architecture"],
        "created_at": "2025-04-15T10:35:00Z",
        "updated_at": "2025-04-15T10:35:00Z"
      },
      // ... more tasks
    ],
    "total": 12,
    "limit": 10,
    "offset": 0
  }
}
```

### Get task by ID

```
GET /plans/{plan_id}/tasks/{task_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "task-id-789",
    "name": "Design System Architecture",
    "description": "Create the high-level system design",
    "duration": 5,
    "duration_unit": "days",
    "assigned_to": "resource-id-123",
    "dependencies": ["task-id-456"],
    "status": "pending",
    "priority": "high",
    "tags": ["design", "architecture"],
    "metadata": {
      "deliverable": "Architecture document"
    },
    "created_at": "2025-04-15T10:35:00Z",
    "updated_at": "2025-04-15T10:35:00Z",
    "dependent_tasks": ["task-id-101", "task-id-102"]
  }
}
```

### Update task

```
PUT /plans/{plan_id}/tasks/{task_id}
```

**Request Body:**
```json
{
  "name": "Updated Task Name",
  "duration": 7,
  "status": "in_progress"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "task-id-789",
    "name": "Updated Task Name",
    "duration": 7,
    "status": "in_progress",
    "updated_at": "2025-04-16T14:25:00Z"
  },
  "message": "Task updated successfully"
}
```

### Update task progress

```
PUT /plans/{plan_id}/tasks/{task_id}/progress
```

**Request Body:**
```json
{
  "status": "in_progress",
  "actual_start_date": "2025-05-05T09:00:00Z",
  "completion_percentage": 60,
  "notes": "Making good progress, should complete on time"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "task-id-789",
    "status": "in_progress",
    "actual_start_date": "2025-05-05T09:00:00Z",
    "completion_percentage": 60,
    "notes": "Making good progress, should complete on time",
    "updated_at": "2025-05-08T16:20:00Z"
  },
  "message": "Task progress updated successfully"
}
```

### Delete task

```
DELETE /plans/{plan_id}/tasks/{task_id}
```

**Response:**
```json
{
  "status": "success",
  "message": "Task deleted successfully"
}
```

## Resources

### Add resource to plan

```
POST /plans/{plan_id}/resources
```

**Request Body:**
```json
{
  "name": "Jane Smith",
  "type": "human",
  "skills": ["java", "python", "architecture"],
  "availability": 0.8,
  "cost_rate": 120.00,
  "metadata": {
    "email": "jane.smith@example.com",
    "department": "Engineering"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "resource_id": "resource-id-123",
  "message": "Resource added successfully"
}
```

### List resources in plan

```
GET /plans/{plan_id}/resources
```

**Query Parameters:**
- `limit` (optional): Maximum number of resources to return (default: 100)
- `offset` (optional): Offset for pagination (default: 0)
- `type` (optional): Filter by resource type
- `skill` (optional): Filter by skill
- `search` (optional): Search term for name

**Response:**
```json
{
  "status": "success",
  "data": {
    "resources": [
      {
        "id": "resource-id-123",
        "name": "Jane Smith",
        "type": "human",
        "skills": ["java", "python", "architecture"],
        "availability": 0.8,
        "cost_rate": 120.00,
        "created_at": "2025-04-15T10:40:00Z",
        "updated_at": "2025-04-15T10:40:00Z"
      },
      // ... more resources
    ],
    "total": 5,
    "limit": 10,
    "offset": 0
  }
}
```

### Get resource by ID

```
GET /plans/{plan_id}/resources/{resource_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "resource-id-123",
    "name": "Jane Smith",
    "type": "human",
    "skills": ["java", "python", "architecture"],
    "availability": 0.8,
    "cost_rate": 120.00,
    "metadata": {
      "email": "jane.smith@example.com",
      "department": "Engineering"
    },
    "created_at": "2025-04-15T10:40:00Z",
    "updated_at": "2025-04-15T10:40:00Z",
    "assigned_tasks": ["task-id-789", "task-id-790"]
  }
}
```

### Update resource

```
PUT /plans/{plan_id}/resources/{resource_id}
```

**Request Body:**
```json
{
  "availability": 0.5,
  "skills": ["java", "python", "architecture", "mentoring"]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "resource-id-123",
    "availability": 0.5,
    "skills": ["java", "python", "architecture", "mentoring"],
    "updated_at": "2025-04-16T14:30:00Z"
  },
  "message": "Resource updated successfully"
}
```

### Delete resource

```
DELETE /plans/{plan_id}/resources/{resource_id}
```

**Response:**
```json
{
  "status": "success",
  "message": "Resource deleted successfully"
}
```

## Analysis and Insights

### Calculate critical path

```
GET /plans/{plan_id}/critical-path
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "critical_path": ["task-id-456", "task-id-789", "task-id-101"],
    "critical_path_duration": 15,
    "earliest_start": {
      "task-id-456": 0,
      "task-id-789": 3,
      "task-id-101": 10
    },
    "earliest_finish": {
      "task-id-456": 3,
      "task-id-789": 10,
      "task-id-101": 15
    },
    "latest_start": {
      "task-id-456": 0,
      "task-id-789": 3,
      "task-id-101": 10
    },
    "latest_finish": {
      "task-id-456": 3,
      "task-id-789": 10,
      "task-id-101": 15
    },
    "slack": {
      "task-id-456": 0,
      "task-id-789": 0,
      "task-id-101": 0,
      "task-id-102": 2
    },
    "bottlenecks": [
      {
        "task_id": "task-id-789",
        "reasons": ["Long duration", "High dependent count (3)"],
        "duration": 7,
        "dependencies": ["task-id-456"],
        "dependents": ["task-id-101", "task-id-102", "task-id-103"]
      }
    ]
  }
}
```

### Generate timeline

```
GET /plans/{plan_id}/timeline
```

**Query Parameters:**
- `format` (optional): Timeline format (default, gantt) (default: "default")
- `include_resources` (optional): Whether to include resources (default: true)

**Response:**
```json
{
  "status": "success",
  "data": {
    "plan_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Project Plan",
    "start_date": "2025-05-01T00:00:00Z",
    "end_date": "2025-05-30T00:00:00Z",
    "duration_days": 30,
    "tasks": [
      {
        "id": "task-id-456",
        "name": "Requirements Analysis",
        "start_date": "2025-05-01T00:00:00Z",
        "end_date": "2025-05-03T00:00:00Z",
        "assigned_to": "resource-id-456",
        "is_critical": true
      },
      {
        "id": "task-id-789",
        "name": "Design System Architecture",
        "start_date": "2025-05-04T00:00:00Z",
        "end_date": "2025-05-10T00:00:00Z",
        "assigned_to": "resource-id-123",
        "is_critical": true
      },
      // ... more tasks
    ],
    "resources": [
      {
        "id": "resource-id-123",
        "name": "Jane Smith",
        "tasks": ["task-id-789", "task-id-790"],
        "utilization": 0.75
      },
      // ... more resources
    ]
  }
}
```

### Get plan summary

```
GET /plans/{plan_id}/summary
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "plan_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Project Plan",
    "start_date": "2025-05-01T00:00:00Z",
    "end_date": "2025-05-30T00:00:00Z",
    "duration_days": 30,
    "tasks": 12,
    "resources": 5,
    "critical_path_length": 3,
    "critical_path_duration_days": 15,
    "resource_utilization": 0.82,
    "completion_percentage": 25,
    "status_breakdown": {
      "pending": 8,
      "in_progress": 3,
      "completed": 1,
      "blocked": 0
    },
    "priority_breakdown": {
      "low": 2,
      "medium": 5,
      "high": 4,
      "critical": 1
    }
  }
}
```

### Generate LLM plan analysis

```
GET /plans/{plan_id}/analysis
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "summary": "This project plan appears well-structured with appropriate dependencies and resource allocations. The critical path consists of 3 key tasks spanning 15 days, with the system architecture design representing the most significant bottleneck.",
    "risks": [
      {
        "description": "Resource Jane Smith is overallocated at 120% during the second week of May",
        "probability": "high",
        "impact": "medium",
        "mitigation": "Consider redistributing some tasks or extending the timeline for the architecture design phase"
      },
      {
        "description": "The integration phase has no buffer and is on the critical path",
        "probability": "medium",
        "impact": "high",
        "mitigation": "Add 1-2 days of buffer time before the deployment phase"
      }
    ],
    "recommendations": [
      "Consider adding a QA resource to help with testing",
      "The design phase could be parallelized by splitting into frontend and backend tracks",
      "Add explicit deployment verification tasks to ensure successful rollout"
    ],
    "optimizations": [
      {
        "description": "Parallelize database and API development",
        "expected_saving": "3 days"
      },
      {
        "description": "Move code review earlier in the process",
        "expected_saving": "1 day"
      }
    ]
  }
}
```

## Retrospectives

### Create a retrospective

```
POST /retrospectives
```

**Request Body:**
```json
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Project Retrospective",
  "description": "End-of-project retrospective",
  "date": "2025-06-30T14:00:00Z",
  "participants": ["Jane Smith", "John Doe", "Alice Johnson"],
  "tags": ["web-app", "retrospective"],
  "metadata": {
    "location": "Conference Room A",
    "duration_minutes": 60
  }
}
```

**Response:**
```json
{
  "status": "success",
  "retrospective_id": "retro-id-123",
  "message": "Retrospective created successfully"
}
```

### Get retrospective by ID

```
GET /retrospectives/{retrospective_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "retro-id-123",
    "plan_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Project Retrospective",
    "description": "End-of-project retrospective",
    "date": "2025-06-30T14:00:00Z",
    "participants": ["Jane Smith", "John Doe", "Alice Johnson"],
    "tags": ["web-app", "retrospective"],
    "metadata": {
      "location": "Conference Room A",
      "duration_minutes": 60
    },
    "created_at": "2025-06-25T10:00:00Z",
    "updated_at": "2025-06-25T10:00:00Z",
    "feedback_count": 5
  }
}
```

### List retrospectives

```
GET /retrospectives
```

**Query Parameters:**
- `plan_id` (optional): Filter by plan ID
- `limit` (optional): Maximum number of retrospectives to return (default: 100)
- `offset` (optional): Offset for pagination (default: 0)
- `tag` (optional): Filter by tag
- `search` (optional): Search term for name or description

**Response:**
```json
{
  "status": "success",
  "data": {
    "retrospectives": [
      {
        "id": "retro-id-123",
        "plan_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Project Retrospective",
        "description": "End-of-project retrospective",
        "date": "2025-06-30T14:00:00Z",
        "created_at": "2025-06-25T10:00:00Z",
        "updated_at": "2025-06-25T10:00:00Z"
      },
      // ... more retrospectives
    ],
    "total": 3,
    "limit": 10,
    "offset": 0
  }
}
```

### Add feedback to a retrospective

```
POST /retrospectives/{retrospective_id}/feedback
```

**Request Body:**
```json
{
  "type": "positive",
  "description": "Team collaboration was excellent throughout the project",
  "source": "Jane Smith",
  "priority": "medium",
  "metadata": {
    "category": "collaboration"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "feedback_id": "feedback-id-456",
  "message": "Feedback added successfully"
}
```

### List feedback for a retrospective

```
GET /retrospectives/{retrospective_id}/feedback
```

**Query Parameters:**
- `type` (optional): Filter by feedback type
- `source` (optional): Filter by feedback source
- `priority` (optional): Filter by feedback priority

**Response:**
```json
{
  "status": "success",
  "data": {
    "feedback": [
      {
        "id": "feedback-id-456",
        "type": "positive",
        "description": "Team collaboration was excellent throughout the project",
        "source": "Jane Smith",
        "priority": "medium",
        "created_at": "2025-06-25T10:15:00Z"
      },
      {
        "id": "feedback-id-457",
        "type": "negative",
        "description": "Timeline was too aggressive for the scope of work",
        "source": "John Doe",
        "priority": "high",
        "created_at": "2025-06-25T10:20:00Z"
      },
      // ... more feedback
    ],
    "total": 5
  }
}
```

### Generate improvement suggestions

```
GET /retrospectives/{retrospective_id}/improvement-suggestions
```

**Query Parameters:**
- `max_suggestions` (optional): Maximum number of suggestions to generate (default: 5)

**Response:**
```json
{
  "status": "success",
  "data": {
    "suggestions": [
      {
        "description": "Add buffer time for integration phases in future projects",
        "rationale": "The integration phase took twice as long as planned, causing project delays",
        "expected_impact": "Would reduce schedule overruns by approximately 10%",
        "implementation_difficulty": "low"
      },
      {
        "description": "Implement automated testing earlier in the development cycle",
        "rationale": "Manual testing during integration caused delays and quality issues",
        "expected_impact": "Would reduce integration time by ~30% and improve quality",
        "implementation_difficulty": "medium"
      },
      {
        "description": "Conduct mid-project retrospectives for long projects",
        "rationale": "Issues with estimation were identified too late to correct course",
        "expected_impact": "Would provide earlier feedback and allow course correction",
        "implementation_difficulty": "low"
      }
      // ... more suggestions
    ]
  }
}
```

### Generate retrospective summary

```
GET /retrospectives/{retrospective_id}/summary
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "summary": "The project was largely successful, delivering the core functionality with acceptable quality despite a 10% schedule overrun. Team collaboration was a highlight, while the aggressive timeline and technical integration challenges were the main pain points.",
    "strengths": [
      "Strong team collaboration and communication",
      "High-quality design and architecture",
      "Effective requirements gathering process"
    ],
    "challenges": [
      "Integration with legacy systems took longer than expected",
      "Timeline was too aggressive for the scope",
      "Limited testing resources caused quality issues"
    ],
    "lessons_learned": [
      "Allow more buffer time for integration phases",
      "Involve QA earlier in the development process",
      "Break down large tasks into smaller, measurable units"
    ],
    "action_items": [
      "Create integration test templates for future projects",
      "Revise estimation process to account for complexity factors",
      "Schedule mid-project retrospectives for projects longer than 1 month"
    ]
  }
}
```

## WebSocket API

Prometheus also provides a WebSocket API for real-time updates and interactive planning.

### Connect to WebSocket

```
WebSocket: ws://localhost:8006/ws
```

### Message Format

All WebSocket messages follow this format:

```json
{
  "action": "action_name",
  "data": {
    // Action-specific data
  },
  "id": "optional_message_id"
}
```

### Actions

#### Subscribe to Plan Updates

```json
{
  "action": "subscribe",
  "data": {
    "plan_id": "550e8400-e29b-41d4-a716-446655440000",
    "events": ["task_update", "resource_update", "timeline_change"]
  },
  "id": "msg-1"
}
```

**Response:**
```json
{
  "action": "subscribe_response",
  "data": {
    "status": "success",
    "subscription_id": "sub-123"
  },
  "id": "msg-1"
}
```

#### Task Update

```json
{
  "action": "update_task",
  "data": {
    "plan_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_id": "task-id-789",
    "status": "in_progress",
    "completion_percentage": 60
  },
  "id": "msg-2"
}
```

**Response:**
```json
{
  "action": "update_task_response",
  "data": {
    "status": "success",
    "task_id": "task-id-789"
  },
  "id": "msg-2"
}
```

#### Unsubscribe from Updates

```json
{
  "action": "unsubscribe",
  "data": {
    "subscription_id": "sub-123"
  },
  "id": "msg-3"
}
```

**Response:**
```json
{
  "action": "unsubscribe_response",
  "data": {
    "status": "success"
  },
  "id": "msg-3"
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include detailed information:

```json
{
  "status": "error",
  "error_code": "INVALID_DEPENDENCY",
  "message": "Task dependency creates a circular reference",
  "details": {
    "task_id": "task-id-789",
    "dependency_id": "task-id-101",
    "path": ["task-id-789", "task-id-101", "task-id-102", "task-id-789"]
  }
}
```

## Versioning

The API version is included in the response headers:

```
X-Prometheus-Version: 0.1.0
```

Future breaking changes will be managed through API versioning.