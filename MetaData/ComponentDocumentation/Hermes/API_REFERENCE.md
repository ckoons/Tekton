# Hermes API Reference

## Base URL

```
http://localhost:8000/api/hermes
```

## Authentication

All API requests require authentication via one of the following methods:

- **API Key**: Passed via the `X-API-Key` header
- **Bearer Token**: Passed via the `Authorization` header

## Component Registry API

### Register Component

Register a component with Hermes.

```
POST /registry/components
```

#### Request Body

```json
{
  "component": "example_component",
  "description": "Example Tekton component",
  "version": "1.0.0",
  "endpoints": [
    {
      "path": "/api/example",
      "methods": ["GET", "POST"],
      "description": "Main API endpoint"
    },
    {
      "path": "/ws/example",
      "description": "WebSocket endpoint"
    }
  ],
  "capabilities": ["data_processing", "visualization"],
  "host": "localhost",
  "port": 8005,
  "health_check": "/api/example/health",
  "dependencies": ["engram", "rhetor"],
  "metadata": {
    "ui_enabled": true,
    "batch_processing": false
  }
}
```

#### Response

```json
{
  "success": true,
  "message": "Component registered successfully",
  "registration_id": "reg-123e4567-e89b-12d3-a456-426614174000",
  "component": "example_component",
  "timestamp": "2025-01-15T12:00:00Z"
}
```

### Get Component

Retrieve component information by ID.

```
GET /registry/components/{component_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `component_id` | string | path | The component identifier |

#### Response

```json
{
  "component": "example_component",
  "description": "Example Tekton component",
  "version": "1.0.0",
  "endpoints": [
    {
      "path": "/api/example",
      "methods": ["GET", "POST"],
      "description": "Main API endpoint"
    },
    {
      "path": "/ws/example",
      "description": "WebSocket endpoint"
    }
  ],
  "capabilities": ["data_processing", "visualization"],
  "host": "localhost",
  "port": 8005,
  "health_check": "/api/example/health",
  "dependencies": ["engram", "rhetor"],
  "metadata": {
    "ui_enabled": true,
    "batch_processing": false
  },
  "status": "active",
  "last_heartbeat": "2025-01-15T12:05:00Z",
  "registered_at": "2025-01-15T12:00:00Z",
  "registration_id": "reg-123e4567-e89b-12d3-a456-426614174000"
}
```

### List Components

Retrieve a list of all registered components.

```
GET /registry/components
```

#### Query Parameters

| Name | Type | Description |
|------|------|------------|
| `status` | string | Filter by status (active, inactive, all) |
| `capability` | string | Filter by capability |
| `page` | integer | Page number for pagination (default: 1) |
| `limit` | integer | Number of items per page (default: 20) |

#### Response

```json
{
  "items": [
    {
      "component": "example_component",
      "description": "Example Tekton component",
      "version": "1.0.0",
      "capabilities": ["data_processing", "visualization"],
      "host": "localhost",
      "port": 8005,
      "status": "active",
      "last_heartbeat": "2025-01-15T12:05:00Z"
    },
    {
      "component": "rhetor",
      "description": "LLM orchestration component",
      "version": "1.2.0",
      "capabilities": ["llm_integration", "prompt_management"],
      "host": "localhost",
      "port": 8005,
      "status": "active",
      "last_heartbeat": "2025-01-15T12:04:30Z"
    },
    {
      "component": "engram",
      "description": "Memory management component",
      "version": "0.9.5",
      "capabilities": ["memory_storage", "memory_retrieval"],
      "host": "localhost",
      "port": 8002,
      "status": "active",
      "last_heartbeat": "2025-01-15T12:04:45Z"
    }
  ],
  "total": 3,
  "page": 1,
  "limit": 20
}
```

### Update Component

Update a registered component.

```
PUT /registry/components/{component_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `component_id` | string | path | The component identifier |

#### Request Body

```json
{
  "description": "Updated example component",
  "version": "1.0.1",
  "endpoints": [
    {
      "path": "/api/example",
      "methods": ["GET", "POST", "PUT"],
      "description": "Main API endpoint (updated)"
    },
    {
      "path": "/ws/example",
      "description": "WebSocket endpoint"
    }
  ],
  "capabilities": ["data_processing", "visualization", "data_export"],
  "host": "localhost",
  "port": 8005,
  "health_check": "/api/example/health",
  "dependencies": ["engram", "rhetor", "athena"],
  "metadata": {
    "ui_enabled": true,
    "batch_processing": true
  }
}
```

#### Response

```json
{
  "success": true,
  "message": "Component updated successfully",
  "component": "example_component",
  "timestamp": "2025-01-15T13:00:00Z"
}
```

### Deregister Component

Deregister a component from Hermes.

```
DELETE /registry/components/{component_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `component_id` | string | path | The component identifier |

#### Response

```json
{
  "success": true,
  "message": "Component deregistered successfully",
  "component": "example_component",
  "timestamp": "2025-01-15T14:00:00Z"
}
```

### Send Heartbeat

Send a heartbeat to indicate component is still active.

```
POST /registry/components/{component_id}/heartbeat
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `component_id` | string | path | The component identifier |

#### Request Body

```json
{
  "status": "active",
  "metrics": {
    "cpu_usage": 12.5,
    "memory_usage": 256.7,
    "request_count": 1245
  }
}
```

#### Response

```json
{
  "success": true,
  "message": "Heartbeat received",
  "component": "example_component",
  "timestamp": "2025-01-15T12:10:00Z"
}
```

### List Capabilities

Retrieve a list of all capabilities across registered components.

```
GET /registry/capabilities
```

#### Response

```json
{
  "capabilities": [
    {
      "name": "data_processing",
      "components": ["example_component", "sophia"]
    },
    {
      "name": "visualization",
      "components": ["example_component", "athena"]
    },
    {
      "name": "llm_integration",
      "components": ["rhetor"]
    },
    {
      "name": "memory_storage",
      "components": ["engram"]
    },
    {
      "name": "memory_retrieval",
      "components": ["engram"]
    }
  ]
}
```

### Find Components by Capability

Find components that provide a specific capability.

```
GET /registry/capabilities/{capability}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `capability` | string | path | The capability name |

#### Response

```json
{
  "capability": "data_processing",
  "components": [
    {
      "component": "example_component",
      "description": "Example Tekton component",
      "version": "1.0.1",
      "host": "localhost",
      "port": 8005,
      "status": "active"
    },
    {
      "component": "sophia",
      "description": "Data science and ML component",
      "version": "0.8.2",
      "host": "localhost",
      "port": 8007,
      "status": "active"
    }
  ]
}
```

## Messaging API

### Send Message

Send a message to another component.

```
POST /messages
```

#### Request Body

```json
{
  "source": "example_component",
  "target": "rhetor",
  "type": "request",
  "correlation_id": "corr-123e4567-e89b-12d3-a456-426614174000",
  "reply_to": "example_component.reply_queue",
  "payload": {
    "action": "generate_text",
    "parameters": {
      "prompt": "Hello, world!",
      "model": "claude-3-sonnet-20240229"
    }
  },
  "metadata": {
    "priority": "high",
    "timeout": 30
  }
}
```

#### Response

```json
{
  "message_id": "msg-123e4567-e89b-12d3-a456-426614174000",
  "status": "delivered",
  "timestamp": "2025-01-15T15:00:00Z"
}
```

### Get Message Status

Check the status of a message.

```
GET /messages/{message_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `message_id` | string | path | The message identifier |

#### Response

```json
{
  "message_id": "msg-123e4567-e89b-12d3-a456-426614174000",
  "source": "example_component",
  "target": "rhetor",
  "type": "request",
  "correlation_id": "corr-123e4567-e89b-12d3-a456-426614174000",
  "status": "delivered",
  "created_at": "2025-01-15T15:00:00Z",
  "delivered_at": "2025-01-15T15:00:01Z",
  "response_id": "msg-abcde123-f456-789d-e012-3456789abcde"
}
```

### List Messages

Retrieve a list of messages with optional filtering.

```
GET /messages
```

#### Query Parameters

| Name | Type | Description |
|------|------|------------|
| `source` | string | Filter by source component |
| `target` | string | Filter by target component |
| `type` | string | Filter by message type |
| `status` | string | Filter by status |
| `correlation_id` | string | Filter by correlation ID |
| `start_time` | string | Filter by start time (ISO 8601) |
| `end_time` | string | Filter by end time (ISO 8601) |
| `page` | integer | Page number for pagination (default: 1) |
| `limit` | integer | Number of items per page (default: 20) |

#### Response

```json
{
  "items": [
    {
      "message_id": "msg-123e4567-e89b-12d3-a456-426614174000",
      "source": "example_component",
      "target": "rhetor",
      "type": "request",
      "status": "delivered",
      "created_at": "2025-01-15T15:00:00Z"
    },
    {
      "message_id": "msg-abcde123-f456-789d-e012-3456789abcde",
      "source": "rhetor",
      "target": "example_component",
      "type": "response",
      "status": "delivered",
      "created_at": "2025-01-15T15:00:05Z"
    }
  ],
  "total": 2,
  "page": 1,
  "limit": 20
}
```

## Event API

### Publish Event

Publish an event to the system.

```
POST /events
```

#### Request Body

```json
{
  "source": "example_component",
  "type": "data_updated",
  "payload": {
    "dataset_id": "12345",
    "timestamp": "2024-05-01T10:00:00Z",
    "affected_records": 256
  },
  "metadata": {
    "importance": "medium",
    "tags": ["data", "update", "batch"]
  }
}
```

#### Response

```json
{
  "event_id": "evt-123e4567-e89b-12d3-a456-426614174000",
  "published_at": "2025-01-15T16:00:00Z"
}
```

### Create Subscription

Create a subscription to events.

```
POST /events/subscriptions
```

#### Request Body

```json
{
  "subscriber": "example_component",
  "event_types": ["data_updated", "analysis_completed"],
  "source_filter": ["sophia", "athena"],
  "callback_url": "http://localhost:8005/api/example/events",
  "webhook_secret": "your_webhook_secret",
  "metadata": {
    "description": "Data processing events subscription",
    "max_retry": 3
  }
}
```

#### Response

```json
{
  "subscription_id": "sub-123e4567-e89b-12d3-a456-426614174000",
  "subscriber": "example_component",
  "event_types": ["data_updated", "analysis_completed"],
  "source_filter": ["sophia", "athena"],
  "created_at": "2025-01-15T16:30:00Z",
  "status": "active"
}
```

### List Subscriptions

List event subscriptions.

```
GET /events/subscriptions
```

#### Query Parameters

| Name | Type | Description |
|------|------|------------|
| `subscriber` | string | Filter by subscriber component |
| `event_type` | string | Filter by event type |
| `status` | string | Filter by subscription status |
| `page` | integer | Page number for pagination (default: 1) |
| `limit` | integer | Number of items per page (default: 20) |

#### Response

```json
{
  "items": [
    {
      "subscription_id": "sub-123e4567-e89b-12d3-a456-426614174000",
      "subscriber": "example_component",
      "event_types": ["data_updated", "analysis_completed"],
      "source_filter": ["sophia", "athena"],
      "created_at": "2025-01-15T16:30:00Z",
      "status": "active"
    },
    {
      "subscription_id": "sub-abcde123-f456-789d-e012-3456789abcde",
      "subscriber": "prometheus",
      "event_types": ["task_completed", "workflow_started", "workflow_completed"],
      "source_filter": ["harmonia"],
      "created_at": "2025-01-14T10:15:00Z",
      "status": "active"
    }
  ],
  "total": 2,
  "page": 1,
  "limit": 20
}
```

### Get Subscription

Get details of a specific subscription.

```
GET /events/subscriptions/{subscription_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `subscription_id` | string | path | The subscription identifier |

#### Response

```json
{
  "subscription_id": "sub-123e4567-e89b-12d3-a456-426614174000",
  "subscriber": "example_component",
  "event_types": ["data_updated", "analysis_completed"],
  "source_filter": ["sophia", "athena"],
  "callback_url": "http://localhost:8005/api/example/events",
  "created_at": "2025-01-15T16:30:00Z",
  "updated_at": "2025-01-15T16:30:00Z",
  "status": "active",
  "metadata": {
    "description": "Data processing events subscription",
    "max_retry": 3
  },
  "delivery_stats": {
    "delivered": 42,
    "failed": 2,
    "last_delivery": "2025-01-15T17:45:00Z"
  }
}
```

### Cancel Subscription

Cancel an event subscription.

```
DELETE /events/subscriptions/{subscription_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `subscription_id` | string | path | The subscription identifier |

#### Response

```json
{
  "success": true,
  "message": "Subscription cancelled successfully",
  "subscription_id": "sub-123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-01-15T18:00:00Z"
}
```

## WebSocket API

### Message Streaming

Connect to the messages WebSocket endpoint to send and receive messages in real-time.

```
ws://localhost:8000/ws/hermes/messages
```

#### Connection Parameters

| Name | Type | Description |
|------|------|------------|
| `api_key` | string | API key for authentication |
| `component` | string | Component identifier |

#### Message Format

All WebSocket messages use the following JSON format:

```json
{
  "type": "message_type",
  "timestamp": "2025-01-15T18:30:00Z",
  "payload": {  // Message-specific payload
    ...
  }
}
```

#### Connect Message

```json
{
  "type": "connect",
  "timestamp": "2025-01-15T18:30:00Z",
  "payload": {
    "component": "example_component",
    "version": "1.0.1"
  }
}
```

#### Connected Response

```json
{
  "type": "connected",
  "timestamp": "2025-01-15T18:30:00Z",
  "payload": {
    "session_id": "sess-123e4567-e89b-12d3-a456-426614174000",
    "component": "example_component",
    "server_time": "2025-01-15T18:30:00Z"
  }
}
```

#### Send Message

```json
{
  "type": "send_message",
  "timestamp": "2025-01-15T18:30:10Z",
  "payload": {
    "target": "rhetor",
    "message_type": "request",
    "correlation_id": "corr-123e4567-e89b-12d3-a456-426614174000",
    "content": {
      "action": "generate_text",
      "parameters": {
        "prompt": "Hello, world!",
        "model": "claude-3-sonnet-20240229"
      }
    }
  }
}
```

#### Receive Message

```json
{
  "type": "receive_message",
  "timestamp": "2025-01-15T18:30:15Z",
  "payload": {
    "message_id": "msg-abcde123-f456-789d-e012-3456789abcde",
    "source": "rhetor",
    "message_type": "response",
    "correlation_id": "corr-123e4567-e89b-12d3-a456-426614174000",
    "content": {
      "text": "Hello! How can I assist you today?",
      "model": "claude-3-sonnet-20240229"
    }
  }
}
```

### Event Streaming

Connect to the events WebSocket endpoint to receive real-time event notifications.

```
ws://localhost:8000/ws/hermes/events
```

#### Connection Parameters

| Name | Type | Description |
|------|------|------------|
| `api_key` | string | API key for authentication |
| `component` | string | Component identifier |

#### Subscribe to Events

```json
{
  "type": "subscribe",
  "timestamp": "2025-01-15T19:00:00Z",
  "payload": {
    "event_types": ["data_updated", "analysis_completed"],
    "source_filter": ["sophia", "athena"]
  }
}
```

#### Subscription Confirmed

```json
{
  "type": "subscription_confirmed",
  "timestamp": "2025-01-15T19:00:00Z",
  "payload": {
    "subscription_id": "ws-sub-123e4567-e89b-12d3-a456-426614174000",
    "event_types": ["data_updated", "analysis_completed"],
    "source_filter": ["sophia", "athena"]
  }
}
```

#### Event Notification

```json
{
  "type": "event",
  "timestamp": "2025-01-15T19:05:00Z",
  "payload": {
    "event_id": "evt-123e4567-e89b-12d3-a456-426614174000",
    "source": "sophia",
    "event_type": "analysis_completed",
    "content": {
      "analysis_id": "an-123",
      "dataset_id": "ds-456",
      "result_url": "https://example.com/results/an-123",
      "summary": "Analysis completed successfully with 95% confidence"
    },
    "occurred_at": "2025-01-15T19:04:55Z"
  }
}
```

## Error Responses

All endpoints follow a standard error response format:

```json
{
  "error": {
    "code": "component_not_found",
    "message": "Component with ID 'invalid_component' not found",
    "details": {
      "requested_id": "invalid_component"
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
| `component_not_found` | 404 | The requested component was not found |
| `message_not_found` | 404 | The requested message was not found |
| `subscription_not_found` | 404 | The requested subscription was not found |
| `component_conflict` | 409 | A component with the same ID already exists |
| `validation_error` | 422 | The request failed validation checks |
| `delivery_failed` | 500 | Message or event delivery failed |
| `internal_error` | 500 | An internal server error occurred |
| `rate_limit_exceeded` | 429 | The rate limit for API requests has been exceeded |