# Engram API Reference

## Base URL

```
http://localhost:8002/api/engram
```

## Authentication

All API requests require authentication via one of the following methods:

- **API Key**: Passed via the `X-API-Key` header
- **Bearer Token**: Passed via the `Authorization` header

## Memory API

### Store Memory

Create or update a memory item.

```
POST /memory
```

#### Request Body

```json
{
  "content": "This is the actual memory content to store.",
  "metadata": {
    "source": "user_input",
    "session_id": "session-123",
    "tags": ["important", "context"],
    "custom_field": "custom value"
  },
  "importance": 0.8,
  "compartment": "working",
  "type": "episodic",
  "references": ["memory-456", "memory-789"],
  "embedding": [0.1, 0.2, 0.3, ...],  // Optional, will be generated if omitted
  "id": "memory-123"  // Optional, will be generated if omitted
}
```

#### Response

```json
{
  "id": "memory-123",
  "content": "This is the actual memory content to store.",
  "metadata": {
    "source": "user_input",
    "session_id": "session-123",
    "tags": ["important", "context"],
    "custom_field": "custom value"
  },
  "importance": 0.8,
  "compartment": "working",
  "type": "episodic",
  "references": ["memory-456", "memory-789"],
  "created_at": "2025-01-15T12:00:00Z",
  "accessed_at": "2025-01-15T12:00:00Z",
  "version": 1
}
```

### Get Memory by ID

Retrieve a specific memory item by its ID.

```
GET /memory/{memory_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `memory_id` | string | path | The unique identifier of the memory |

#### Response

```json
{
  "id": "memory-123",
  "content": "This is the actual memory content to store.",
  "metadata": {
    "source": "user_input",
    "session_id": "session-123",
    "tags": ["important", "context"],
    "custom_field": "custom value"
  },
  "importance": 0.8,
  "compartment": "working",
  "type": "episodic",
  "references": ["memory-456", "memory-789"],
  "created_at": "2025-01-15T12:00:00Z",
  "accessed_at": "2025-01-15T12:15:00Z",
  "version": 1,
  "embedding": [0.1, 0.2, 0.3, ...]  // Included only if specifically requested
}
```

### Delete Memory

Delete a memory item by ID.

```
DELETE /memory/{memory_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `memory_id` | string | path | The unique identifier of the memory |

#### Response

```json
{
  "success": true,
  "message": "Memory deleted successfully"
}
```

### Search Memories

Search for memories based on content similarity and/or metadata.

```
POST /search
```

#### Request Body

```json
{
  "query": "What is the capital of France?",  // Text to search for similar memories
  "filter": {
    "compartment": ["core", "semantic"],  // Optional compartment filter
    "type": ["semantic"],  // Optional type filter
    "metadata": {  // Optional metadata filters
      "tags": ["geography"],
      "source": "user_input"
    },
    "date_range": {  // Optional date range
      "start": "2025-01-01T00:00:00Z",
      "end": "2025-01-31T23:59:59Z"
    }
  },
  "limit": 10,  // Maximum number of results (default: 10)
  "threshold": 0.7,  // Minimum similarity score (0.0 to 1.0)
  "include_embeddings": false  // Whether to include embeddings in results
}
```

#### Response

```json
{
  "results": [
    {
      "id": "memory-456",
      "content": "Paris is the capital of France.",
      "similarity": 0.92,
      "metadata": {
        "source": "user_input",
        "tags": ["geography", "europe"],
        "confidence": 0.95
      },
      "importance": 0.75,
      "compartment": "semantic",
      "type": "semantic",
      "created_at": "2025-01-10T09:15:00Z",
      "accessed_at": "2025-01-15T12:30:00Z"
    },
    { ... }
  ],
  "metadata": {
    "total_matches": 15,
    "returned": 10,
    "execution_time": 0.023
  }
}
```

### Batch Store Memories

Store multiple memory items in a single request.

```
POST /batch/memory
```

#### Request Body

```json
{
  "items": [
    {
      "content": "Memory content 1",
      "metadata": { ... },
      "compartment": "episodic",
      "type": "episodic"
    },
    {
      "content": "Memory content 2",
      "metadata": { ... },
      "compartment": "working",
      "type": "working"
    },
    { ... }
  ],
  "generate_embeddings": true  // Whether to generate embeddings server-side
}
```

#### Response

```json
{
  "items": [
    {
      "id": "memory-789",
      "content": "Memory content 1",
      ...
    },
    {
      "id": "memory-790",
      "content": "Memory content 2",
      ...
    },
    { ... }
  ],
  "metadata": {
    "successful": 5,
    "failed": 0,
    "execution_time": 0.142
  }
}
```

## Compartment API

### List Compartments

Retrieve a list of available memory compartments.

```
GET /compartments
```

#### Response

```json
{
  "compartments": [
    {
      "id": "core",
      "description": "Core, foundational memories",
      "memory_count": 256,
      "policy": "persistent"
    },
    {
      "id": "working",
      "description": "Active working memory",
      "memory_count": 48,
      "policy": "session"
    },
    {
      "id": "episodic",
      "description": "Time-based memory of events and interactions",
      "memory_count": 1024,
      "policy": "time_decay"
    },
    { ... }
  ]
}
```

### Create Compartment

Create a new memory compartment.

```
POST /compartments
```

#### Request Body

```json
{
  "id": "project_x",
  "description": "Memories related to Project X",
  "policy": {
    "type": "custom",
    "retention": "30d",
    "importance_threshold": 0.4,
    "default_importance": 0.7
  },
  "metadata": {
    "owner": "team_a",
    "project_id": "proj-123"
  }
}
```

#### Response

```json
{
  "id": "project_x",
  "description": "Memories related to Project X",
  "memory_count": 0,
  "policy": {
    "type": "custom",
    "retention": "30d",
    "importance_threshold": 0.4,
    "default_importance": 0.7
  },
  "metadata": {
    "owner": "team_a",
    "project_id": "proj-123",
    "created_at": "2025-01-15T13:45:00Z"
  }
}
```

### Delete Compartment

Delete a memory compartment and optionally its contents.

```
DELETE /compartments/{compartment_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `compartment_id` | string | path | The unique identifier of the compartment |
| `delete_memories` | boolean | query | Whether to delete all memories in the compartment (default: false) |

#### Response

```json
{
  "success": true,
  "message": "Compartment deleted successfully",
  "deleted_memories": 48  // Only included if delete_memories=true
}
```

## Context API

### Get Current Context

Retrieve the current active memory context.

```
GET /context
```

#### Response

```json
{
  "id": "ctx-123",
  "active_compartments": ["working", "project_x", "core"],
  "focus": "project_x",
  "recency_window": "1h",
  "importance_threshold": 0.3,
  "metadata": {
    "session_id": "session-456",
    "last_updated": "2025-01-15T13:50:00Z"
  },
  "recent_topics": ["api design", "documentation", "testing"],
  "recent_memories": ["memory-789", "memory-790", "memory-791"]
}
```

### Update Context

Update the current memory context settings.

```
PUT /context
```

#### Request Body

```json
{
  "active_compartments": ["working", "project_y", "core"],
  "focus": "project_y",
  "recency_window": "30m",
  "importance_threshold": 0.5,
  "metadata": {
    "task": "code_review"
  }
}
```

#### Response

```json
{
  "id": "ctx-123",
  "active_compartments": ["working", "project_y", "core"],
  "focus": "project_y",
  "recency_window": "30m",
  "importance_threshold": 0.5,
  "metadata": {
    "session_id": "session-456",
    "task": "code_review",
    "last_updated": "2025-01-15T14:05:00Z"
  },
  "recent_topics": ["api design", "documentation", "testing"],
  "recent_memories": ["memory-789", "memory-790", "memory-791"]
}
```

## Embedding API

### Generate Embedding

Generate a vector embedding for text content.

```
POST /embeddings
```

#### Request Body

```json
{
  "content": "Text to generate embedding for",
  "model": "default"  // Optional, embedding model to use
}
```

#### Response

```json
{
  "embedding": [0.1, 0.2, 0.3, ...],
  "dimensions": 1536,
  "model": "default",
  "metadata": {
    "content_hash": "a1b2c3d4e5f6",
    "generation_time": 0.021
  }
}
```

### Batch Generate Embeddings

Generate embeddings for multiple text items.

```
POST /batch/embeddings
```

#### Request Body

```json
{
  "items": [
    "Text item 1",
    "Text item 2",
    "Text item 3"
  ],
  "model": "default"  // Optional, embedding model to use
}
```

#### Response

```json
{
  "embeddings": [
    [0.1, 0.2, 0.3, ...],
    [0.2, 0.3, 0.4, ...],
    [0.3, 0.4, 0.5, ...]
  ],
  "dimensions": 1536,
  "model": "default",
  "metadata": {
    "generation_time": 0.068
  }
}
```

## WebSocket API

The WebSocket API provides real-time interaction with the memory system.

### Connection

```
ws://localhost:8002/ws/engram
```

Connection requires authentication using either:

- Query parameter: `?api_key=your_api_key_here`
- Header: Include auth token in the connection headers

### Message Format

All WebSocket messages use the following JSON format:

```json
{
  "type": "command_name",
  "id": "request-123",  // Client-generated request ID for correlation
  "data": {  // Command-specific payload
    ...
  }
}
```

### Commands

#### Search Memory Stream

Stream search results as they are found.

```json
// Client request
{
  "type": "search",
  "id": "search-request-1",
  "data": {
    "query": "Search query text",
    "filter": { ... },
    "limit": 20
  }
}

// Server responses (multiple messages)
{
  "type": "search_result",
  "id": "search-request-1",
  "data": {
    "memory": { ... },
    "similarity": 0.92,
    "index": 0  // Result position
  }
}

// Final message indicating completion
{
  "type": "search_complete",
  "id": "search-request-1",
  "data": {
    "total_results": 15,
    "returned_results": 15,
    "execution_time": 0.248
  }
}
```

#### Subscribe to Memory Updates

Receive notifications when memories are created or updated.

```json
// Client request
{
  "type": "subscribe",
  "id": "sub-request-1",
  "data": {
    "compartments": ["working", "project_x"],
    "types": ["episodic", "semantic"],
    "metadata_filter": { ... }  // Optional filter
  }
}

// Server acknowledgment
{
  "type": "subscription_confirmed",
  "id": "sub-request-1",
  "data": {
    "subscription_id": "sub-123",
    "filters": { ... }  // Echo of subscription filters
  }
}

// Server notifications (sent whenever matching memories are updated)
{
  "type": "memory_updated",
  "id": "notification-456",
  "data": {
    "subscription_id": "sub-123",
    "memory": { ... },
    "operation": "create"  // or "update", "delete"
  }
}
```

#### Unsubscribe

Cancel a subscription.

```json
// Client request
{
  "type": "unsubscribe",
  "id": "unsub-request-1",
  "data": {
    "subscription_id": "sub-123"
  }
}

// Server confirmation
{
  "type": "unsubscribe_confirmed",
  "id": "unsub-request-1",
  "data": {
    "subscription_id": "sub-123",
    "message": "Subscription canceled successfully"
  }
}
```

## Error Responses

All endpoints follow a standard error response format:

```json
{
  "error": {
    "code": "memory_not_found",
    "message": "Memory with ID 'memory-999' not found",
    "details": {
      "requested_id": "memory-999"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|--------------|
| `invalid_request` | 400 | The request was malformed or invalid |
| `authentication_failed` | 401 | Authentication credentials were missing or invalid |
| `permission_denied` | 403 | The authenticated user lacks permission for the requested operation |
| `memory_not_found` | 404 | The requested memory was not found |
| `compartment_not_found` | 404 | The requested compartment was not found |
| `validation_error` | 422 | The request failed validation checks |
| `embedding_generation_error` | 500 | An error occurred while generating embeddings |
| `storage_error` | 500 | An error occurred with the underlying storage system |
| `rate_limit_exceeded` | 429 | The rate limit for API requests has been exceeded |