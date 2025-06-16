# Athena API Reference

## Base URL

```
http://localhost:8001/api/athena
```

## Authentication

All API requests require authentication via one of the following methods:

- **API Key**: Passed via the `X-API-Key` header
- **Bearer Token**: Passed via the `Authorization` header

## Entities API

### Get Entity

Retrieve an entity by ID.

```
GET /entities/{entity_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|--------------|
| `entity_id` | string | path | The unique identifier of the entity |

#### Response

```json
{
  "id": "entity-123",
  "type": "person",
  "name": "John Doe",
  "properties": {
    "age": 30,
    "email": "john@example.com"
  },
  "metadata": {
    "created_by": "user-1",
    "confidence": 0.95
  },
  "relationships": [
    {
      "id": "rel-456",
      "type": "works_at",
      "target_id": "entity-789"
    }
  ],
  "created_at": "2025-01-15T12:00:00Z",
  "updated_at": "2025-01-15T14:30:00Z"
}
```

### List Entities

Retrieve a list of entities based on filter criteria.

```
GET /entities
```

#### Query Parameters

| Name | Type | Description |
|------|------|--------------|
| `type` | string | Filter by entity type |
| `name` | string | Filter by entity name (supports partial matching) |
| `property.{name}` | any | Filter by property value (e.g., `property.age=30`) |
| `limit` | integer | Maximum number of results to return (default: 50) |
| `offset` | integer | Number of results to skip (default: 0) |

#### Response

```json
{
  "items": [
    {
      "id": "entity-123",
      "type": "person",
      "name": "John Doe",
      "properties": { ... }
    },
    { ... }
  ],
  "total": 142,
  "limit": 50,
  "offset": 0
}
```

### Create Entity

Create a new entity.

```
POST /entities
```

#### Request Body

```json
{
  "type": "person",
  "name": "Jane Smith",
  "properties": {
    "age": 28,
    "email": "jane@example.com"
  },
  "metadata": {
    "source": "manual"
  }
}
```

#### Response

```json
{
  "id": "entity-456",
  "type": "person",
  "name": "Jane Smith",
  "properties": {
    "age": 28,
    "email": "jane@example.com"
  },
  "metadata": {
    "source": "manual",
    "created_by": "user-1"
  },
  "relationships": [],
  "created_at": "2025-01-15T15:30:00Z",
  "updated_at": "2025-01-15T15:30:00Z"
}
```

### Update Entity

Update an existing entity.

```
PUT /entities/{entity_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|--------------|
| `entity_id` | string | path | The unique identifier of the entity |

#### Request Body

```json
{
  "name": "Jane Doe",
  "properties": {
    "age": 29,
    "email": "jane.doe@example.com"
  }
}
```

#### Response

```json
{
  "id": "entity-456",
  "type": "person",
  "name": "Jane Doe",
  "properties": {
    "age": 29,
    "email": "jane.doe@example.com"
  },
  "metadata": {
    "source": "manual",
    "created_by": "user-1",
    "updated_by": "user-1"
  },
  "relationships": [],
  "created_at": "2025-01-15T15:30:00Z",
  "updated_at": "2025-01-15T16:45:00Z"
}
```

### Delete Entity

Delete an entity by ID.

```
DELETE /entities/{entity_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|--------------|
| `entity_id` | string | path | The unique identifier of the entity |

#### Response

```json
{
  "success": true,
  "message": "Entity deleted successfully"
}
```

## Relationships API

### Create Relationship

Create a new relationship between entities.

```
POST /relationships
```

#### Request Body

```json
{
  "type": "works_at",
  "source_id": "entity-123",
  "target_id": "entity-789",
  "properties": {
    "role": "Software Engineer",
    "since": "2023-05-01"
  }
}
```

#### Response

```json
{
  "id": "rel-456",
  "type": "works_at",
  "source_id": "entity-123",
  "target_id": "entity-789",
  "properties": {
    "role": "Software Engineer",
    "since": "2023-05-01"
  },
  "metadata": {
    "created_by": "user-1"
  },
  "created_at": "2025-01-15T17:00:00Z",
  "updated_at": "2025-01-15T17:00:00Z"
}
```

### Get Relationship

Retrieve a relationship by ID.

```
GET /relationships/{relationship_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|--------------|
| `relationship_id` | string | path | The unique identifier of the relationship |

#### Response

```json
{
  "id": "rel-456",
  "type": "works_at",
  "source_id": "entity-123",
  "target_id": "entity-789",
  "properties": {
    "role": "Software Engineer",
    "since": "2023-05-01"
  },
  "metadata": {
    "created_by": "user-1"
  },
  "created_at": "2025-01-15T17:00:00Z",
  "updated_at": "2025-01-15T17:00:00Z"
}
```

### Delete Relationship

Delete a relationship by ID.

```
DELETE /relationships/{relationship_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|--------------|
| `relationship_id` | string | path | The unique identifier of the relationship |

#### Response

```json
{
  "success": true,
  "message": "Relationship deleted successfully"
}
```

## Query API

### Execute Query

Execute a query against the knowledge graph.

```
POST /query
```

#### Request Body

```json
{
  "query_type": "path",
  "start_entity": "entity-123",
  "end_entity": "entity-456",
  "max_depth": 3,
  "relationship_types": ["works_at", "part_of"]
}
```

#### Response

```json
{
  "result": {
    "paths": [
      [
        {
          "entity": {
            "id": "entity-123",
            "type": "person",
            "name": "John Doe"
          },
          "relationship": {
            "id": "rel-789",
            "type": "works_at"
          }
        },
        {
          "entity": {
            "id": "entity-101",
            "type": "organization",
            "name": "Acme Corp"
          },
          "relationship": {
            "id": "rel-102",
            "type": "part_of"
          }
        },
        {
          "entity": {
            "id": "entity-456",
            "type": "department",
            "name": "Engineering"
          }
        }
      ]
    ]
  },
  "metadata": {
    "execution_time": 0.023,
    "nodes_examined": 15
  }
}
```

### Natural Language Query

Execute a natural language query using LLM processing.

```
POST /query/natural
```

#### Request Body

```json
{
  "query": "Who works at Acme Corp in the Engineering department?",
  "context": {
    "focus_entities": ["entity-101"],
    "max_results": 10
  }
}
```

#### Response

```json
{
  "structured_query": {
    "query_type": "pattern",
    "patterns": [
      {
        "entity": { "type": "person" },
        "relationship": { "type": "works_at" },
        "entity": { "id": "entity-101" }
      },
      {
        "entity": { "type": "person" },
        "relationship": { "type": "part_of" },
        "entity": { "type": "department", "name": "Engineering" }
      }
    ]
  },
  "results": [
    {
      "id": "entity-123",
      "type": "person",
      "name": "John Doe",
      "properties": { ... }
    },
    { ... }
  ],
  "explanation": "Found 5 people who work at Acme Corp (entity-101) and are part of the Engineering department."
}
```

## Visualization API

### Generate Graph Visualization

Generate a visualization of a subgraph.

```
POST /visualization/graph
```

#### Request Body

```json
{
  "root_entity": "entity-123",
  "depth": 2,
  "include_entity_types": ["person", "organization", "project"],
  "include_relationship_types": ["works_at", "manages", "contributes_to"],
  "layout": "force-directed"
}
```

#### Response

```json
{
  "nodes": [
    {
      "id": "entity-123",
      "type": "person",
      "name": "John Doe",
      "properties": { ... }
    },
    { ... }
  ],
  "edges": [
    {
      "id": "rel-456",
      "source": "entity-123",
      "target": "entity-789",
      "type": "works_at",
      "properties": { ... }
    },
    { ... }
  ],
  "metadata": {
    "node_count": 12,
    "edge_count": 18,
    "generation_time": 0.056
  }
}
```

## LLM Integration API

### Extract Entities

Extract potential entities from text using LLM processing.

```
POST /llm/extract-entities
```

#### Request Body

```json
{
  "text": "John Doe is a senior software engineer at Acme Corp working on the Atlas project. He reports to Jane Smith, the VP of Engineering.",
  "entity_types": ["person", "organization", "project", "role"],
  "confidence_threshold": 0.7
}
```

#### Response

```json
{
  "entities": [
    {
      "type": "person",
      "name": "John Doe",
      "properties": {
        "role": "senior software engineer"
      },
      "confidence": 0.95,
      "spans": [[0, 8]]
    },
    {
      "type": "organization",
      "name": "Acme Corp",
      "confidence": 0.92,
      "spans": [[40, 49]]
    },
    {
      "type": "project",
      "name": "Atlas",
      "confidence": 0.88,
      "spans": [[64, 69]]
    },
    {
      "type": "person",
      "name": "Jane Smith",
      "properties": {
        "role": "VP of Engineering"
      },
      "confidence": 0.93,
      "spans": [[84, 94]]
    }
  ],
  "relationships": [
    {
      "type": "works_at",
      "source": 0,  // John Doe
      "target": 1,  // Acme Corp
      "confidence": 0.91
    },
    {
      "type": "works_on",
      "source": 0,  // John Doe
      "target": 2,  // Atlas
      "confidence": 0.85
    },
    {
      "type": "reports_to",
      "source": 0,  // John Doe
      "target": 3,  // Jane Smith
      "confidence": 0.87
    }
  ],
  "metadata": {
    "model": "Claude Haiku",
    "processing_time": 0.312
  }
}
```

### Suggest Relationships

Suggest potential relationships between existing entities.

```
POST /llm/suggest-relationships
```

#### Request Body

```json
{
  "entity_ids": ["entity-123", "entity-456"],
  "max_suggestions": 5
}
```

#### Response

```json
{
  "suggestions": [
    {
      "type": "collaborates_with",
      "source_id": "entity-123",
      "target_id": "entity-456",
      "confidence": 0.82,
      "evidence": "Both entities work on similar projects and have historical interactions recorded in the knowledge graph."
    },
    {
      "type": "reports_to",
      "source_id": "entity-123",
      "target_id": "entity-456",
      "confidence": 0.67,
      "evidence": "Organizational structure suggests a potential reporting relationship, though with lower confidence."
    }
  ],
  "metadata": {
    "model": "Claude Haiku",
    "processing_time": 0.245
  }
}
```

## Error Responses

All endpoints follow a standard error response format:

```json
{
  "error": {
    "code": "entity_not_found",
    "message": "Entity with ID 'entity-999' not found",
    "details": {
      "requested_id": "entity-999"
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
| `entity_not_found` | 404 | The requested entity was not found |
| `relationship_not_found` | 404 | The requested relationship was not found |
| `validation_error` | 422 | The request failed validation checks |
| `query_execution_error` | 500 | An error occurred while executing the query |
| `rate_limit_exceeded` | 429 | The rate limit for API requests has been exceeded |