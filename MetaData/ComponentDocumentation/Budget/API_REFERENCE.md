# Budget Component API Reference

This document provides detailed information about the Budget component's API endpoints, request/response formats, and usage examples.

## API Overview

The Budget component exposes a RESTful API through the Single Port Architecture pattern. All endpoints are accessible through the base URL:

```
http://{hostname}:{port}/api/...
```

Where:
- `hostname` is the host where Budget is running (default: localhost)
- `port` is the Budget port (default: 8013)

## Authentication

The API currently uses a simple API key-based authentication mechanism. Include the API key in the request header:

```
X-API-Key: {your-api-key}
```

## Common Response Formats

All API responses follow a standard format:

### Success Responses

```json
{
  "status": "success",
  "data": { ... }
}
```

### Error Responses

```json
{
  "status": "error",
  "error": {
    "code": "error_code",
    "message": "Error description",
    "details": { ... }
  }
}
```

## API Endpoints

### Budget Management

#### List Budgets

```
GET /api/budgets
```

**Query Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Number of items per page (default: 20)
- `is_active` (optional): Filter by active status (true/false)
- `owner` (optional): Filter by owner

**Response:**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "budget_id": "string",
        "name": "string",
        "description": "string",
        "owner": "string",
        "is_active": true,
        "creation_time": "datetime",
        "updated_at": "datetime",
        "metadata": { ... }
      }
    ],
    "total": 0,
    "page": 1,
    "limit": 20
  }
}
```

#### Create Budget

```
POST /api/budgets
```

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "owner": "string",
  "metadata": { ... }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "budget_id": "string",
    "name": "string",
    "description": "string",
    "owner": "string",
    "is_active": true,
    "creation_time": "datetime",
    "updated_at": "datetime",
    "metadata": { ... }
  }
}
```

#### Get Budget

```
GET /api/budgets/{budget_id}
```

**Path Parameters:**
- `budget_id`: The budget ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "budget_id": "string",
    "name": "string",
    "description": "string",
    "owner": "string",
    "is_active": true,
    "creation_time": "datetime",
    "updated_at": "datetime",
    "metadata": { ... }
  }
}
```

#### Update Budget

```
PUT /api/budgets/{budget_id}
```

**Path Parameters:**
- `budget_id`: The budget ID

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "owner": "string",
  "is_active": true,
  "metadata": { ... }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "budget_id": "string",
    "name": "string",
    "description": "string",
    "owner": "string",
    "is_active": true,
    "creation_time": "datetime",
    "updated_at": "datetime",
    "metadata": { ... }
  }
}
```

#### Delete Budget

```
DELETE /api/budgets/{budget_id}
```

**Path Parameters:**
- `budget_id`: The budget ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "Budget deleted successfully"
  }
}
```

### Budget Policies

#### List Policies

```
GET /api/policies
```

**Query Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Number of items per page (default: 20)
- `period` (optional): Filter by period (hourly, daily, weekly, monthly)
- `tier` (optional): Filter by tier (LOCAL_LIGHTWEIGHT, LOCAL_MIDWEIGHT, REMOTE_HEAVYWEIGHT)
- `provider` (optional): Filter by provider
- `component` (optional): Filter by component
- `task_type` (optional): Filter by task type
- `enabled` (optional): Filter by enabled status (true/false)

**Response:**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "policy_id": "string",
        "budget_id": "string",
        "type": "string",
        "period": "string",
        "tier": "string",
        "provider": "string",
        "component": "string",
        "task_type": "string",
        "token_limit": 0,
        "cost_limit": 0,
        "warning_threshold": 0.0,
        "action_threshold": 0.0,
        "enabled": true,
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ],
    "total": 0,
    "page": 1,
    "limit": 20
  }
}
```

#### Create Policy

```
POST /api/policies
```

**Request Body:**
```json
{
  "budget_id": "string",
  "type": "string",
  "period": "string",
  "tier": "string",
  "provider": "string",
  "component": "string",
  "task_type": "string",
  "token_limit": 0,
  "cost_limit": 0,
  "warning_threshold": 0.0,
  "action_threshold": 0.0,
  "enabled": true
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "policy_id": "string",
    "budget_id": "string",
    "type": "string",
    "period": "string",
    "tier": "string",
    "provider": "string",
    "component": "string",
    "task_type": "string",
    "token_limit": 0,
    "cost_limit": 0,
    "warning_threshold": 0.0,
    "action_threshold": 0.0,
    "enabled": true,
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

### Budget Allocations

#### Create Allocation

```
POST /api/allocations
```

**Request Body:**
```json
{
  "context_id": "string",
  "component": "string",
  "tokens_allocated": 0,
  "budget_id": "string",
  "tier": "string",
  "provider": "string",
  "model": "string",
  "task_type": "string",
  "priority": 0,
  "metadata": { ... },
  "expiration_time": "datetime"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "allocation_id": "string",
    "budget_id": "string",
    "context_id": "string",
    "component": "string",
    "tokens_allocated": 0,
    "tokens_used": 0,
    "remaining_tokens": 0,
    "tier": "string",
    "provider": "string",
    "model": "string",
    "task_type": "string",
    "priority": 0,
    "is_active": true,
    "creation_time": "datetime",
    "expiration_time": "datetime",
    "metadata": { ... }
  }
}
```

#### List Allocations

```
GET /api/allocations
```

**Query Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Number of items per page (default: 20)
- `context_id` (optional): Filter by context ID
- `component` (optional): Filter by component
- `tier` (optional): Filter by tier
- `provider` (optional): Filter by provider
- `model` (optional): Filter by model
- `task_type` (optional): Filter by task type
- `is_active` (optional): Filter by active status (true/false)

**Response:**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "allocation_id": "string",
        "budget_id": "string",
        "context_id": "string",
        "component": "string",
        "tokens_allocated": 0,
        "tokens_used": 0,
        "remaining_tokens": 0,
        "tier": "string",
        "provider": "string",
        "model": "string",
        "task_type": "string",
        "priority": 0,
        "is_active": true,
        "creation_time": "datetime",
        "expiration_time": "datetime",
        "metadata": { ... }
      }
    ],
    "total": 0,
    "page": 1,
    "limit": 20
  }
}
```

#### Release Allocation

```
POST /api/allocations/{allocation_id}/release
```

**Path Parameters:**
- `allocation_id`: The allocation ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "Allocation released successfully"
  }
}
```

### Usage Tracking

#### Record Usage

```
POST /api/usage/record
```

**Request Body:**
```json
{
  "context_id": "string",
  "allocation_id": "string",
  "component": "string",
  "provider": "string",
  "model": "string",
  "task_type": "string",
  "input_tokens": 0,
  "output_tokens": 0,
  "operation_id": "string",
  "request_id": "string",
  "user_id": "string",
  "metadata": { ... }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "record_id": "string",
    "allocation_id": "string",
    "context_id": "string",
    "component": "string",
    "provider": "string",
    "model": "string",
    "task_type": "string",
    "input_tokens": 0,
    "output_tokens": 0,
    "total_tokens": 0,
    "input_cost": 0.0,
    "output_cost": 0.0,
    "total_cost": 0.0,
    "timestamp": "datetime",
    "metadata": { ... }
  }
}
```

#### Get Usage Summary

```
POST /api/usage/summary
```

**Request Body:**
```json
{
  "period": "string",
  "budget_id": "string",
  "provider": "string",
  "component": "string",
  "model": "string",
  "task_type": "string",
  "start_time": "datetime",
  "end_time": "datetime"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "period": "string",
    "budget_id": "string",
    "provider": "string",
    "component": "string",
    "model": "string",
    "task_type": "string",
    "start_time": "datetime",
    "end_time": "datetime",
    "total_input_tokens": 0,
    "total_output_tokens": 0,
    "total_tokens": 0,
    "total_input_cost": 0.0,
    "total_output_cost": 0.0,
    "total_cost": 0.0,
    "request_count": 0
  }
}
```

### Pricing

#### List Prices

```
GET /api/prices
```

**Query Parameters:**
- `provider` (optional): Filter by provider
- `model` (optional): Filter by model

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "pricing_id": "string",
      "provider": "string",
      "model": "string",
      "price_type": "string",
      "input_cost_per_token": 0.0,
      "output_cost_per_token": 0.0,
      "input_cost_per_char": 0.0,
      "output_cost_per_char": 0.0,
      "cost_per_image": 0.0,
      "cost_per_second": 0.0,
      "fixed_cost_per_request": 0.0,
      "effective_date": "datetime",
      "end_date": "datetime",
      "source": "string",
      "verified": true,
      "created_at": "datetime"
    }
  ]
}
```

#### Get Current Price

```
POST /api/prices/current
```

**Request Body:**
```json
{
  "provider": "string",
  "model": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "pricing_id": "string",
    "provider": "string",
    "model": "string",
    "price_type": "string",
    "input_cost_per_token": 0.0,
    "output_cost_per_token": 0.0,
    "input_cost_per_char": 0.0,
    "output_cost_per_char": 0.0,
    "cost_per_image": 0.0,
    "cost_per_second": 0.0,
    "fixed_cost_per_request": 0.0,
    "effective_date": "datetime",
    "end_date": "datetime",
    "source": "string",
    "verified": true,
    "created_at": "datetime"
  }
}
```

### Model Recommendations

```
POST /api/prices/recommendations
```

**Request Body:**
```json
{
  "provider": "string",
  "model": "string",
  "task_type": "string",
  "context_size": 0
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "provider": "string",
        "model": "string",
        "estimated_cost": 0.0,
        "cost_reduction": 0.0,
        "cost_reduction_percentage": 0.0,
        "confidence": 0.0,
        "quality_impact": "string",
        "speed_impact": "string",
        "description": "string"
      }
    ],
    "current_model": "string",
    "current_provider": "string",
    "current_cost": 0.0
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `invalid_request` | The request payload is invalid |
| `resource_not_found` | The requested resource was not found |
| `resource_exists` | The resource already exists |
| `insufficient_budget` | Budget limit exceeded |
| `invalid_allocation` | The allocation is invalid or expired |
| `authentication_error` | Authentication failed |
| `authorization_error` | Authorization failed |
| `internal_error` | An internal server error occurred |

## Usage Examples

### Example 1: Create a Budget and Policy

```python
import requests

# Create a budget
budget_response = requests.post(
    "http://localhost:8013/api/budgets",
    headers={"X-API-Key": "your-api-key"},
    json={
        "name": "Production API Budget",
        "description": "Budget for production API usage",
        "owner": "api-team"
    }
)
budget = budget_response.json()["data"]

# Create a budget policy
policy_response = requests.post(
    "http://localhost:8013/api/policies",
    headers={"X-API-Key": "your-api-key"},
    json={
        "budget_id": budget["budget_id"],
        "type": "WARN",
        "period": "daily",
        "tier": "REMOTE_HEAVYWEIGHT",
        "token_limit": 1000000,
        "cost_limit": 50.0,
        "warning_threshold": 0.8,
        "action_threshold": 0.95,
        "enabled": True
    }
)
policy = policy_response.json()["data"]
```

### Example 2: Allocate Tokens and Record Usage

```python
import requests

# Allocate tokens
allocation_response = requests.post(
    "http://localhost:8013/api/allocations",
    headers={"X-API-Key": "your-api-key"},
    json={
        "context_id": "my-context-123",
        "component": "my-component",
        "tokens_allocated": 1000,
        "budget_id": "budget-id",
        "tier": "REMOTE_HEAVYWEIGHT",
        "provider": "anthropic",
        "model": "claude-3-opus-20240229",
        "task_type": "generation"
    }
)
allocation = allocation_response.json()["data"]

# Record usage
requests.post(
    "http://localhost:8013/api/usage/record",
    headers={"X-API-Key": "your-api-key"},
    json={
        "context_id": "my-context-123",
        "allocation_id": allocation["allocation_id"],
        "component": "my-component",
        "provider": "anthropic",
        "model": "claude-3-opus-20240229",
        "input_tokens": 100,
        "output_tokens": 250
    }
)
```

### Example 3: Get Usage Summary

```python
import requests
from datetime import datetime, timedelta

# Get today's usage summary
now = datetime.now()
start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)

requests.post(
    "http://localhost:8013/api/usage/summary",
    headers={"X-API-Key": "your-api-key"},
    json={
        "period": "daily",
        "start_time": start_of_day.isoformat(),
        "end_time": now.isoformat()
    }
)
```

## WebSocket API

The Budget component also provides WebSocket endpoints for real-time updates:

```
ws://{hostname}:{port}/ws/budget/updates
```

### Message Format

Messages sent over the WebSocket connection use the following format:

```json
{
  "type": "string",
  "data": { ... }
}
```

### Message Types

| Type | Description | Data |
|------|-------------|------|
| `allocation_update` | Allocation status update | Allocation object |
| `budget_alert` | Budget threshold alert | Alert object |
| `price_update` | Provider price update | Price update object |
| `heartbeat` | Connection keepalive | Timestamp |

### Example WebSocket Client

```javascript
const socket = new WebSocket('ws://localhost:8013/ws/budget/updates');

socket.onopen = function(e) {
  console.log('WebSocket connection established');
  
  // Send authentication message
  socket.send(JSON.stringify({
    type: 'authenticate',
    data: {
      apiKey: 'your-api-key'
    }
  }));
};

socket.onmessage = function(event) {
  const message = JSON.parse(event.data);
  
  switch(message.type) {
    case 'allocation_update':
      console.log('Allocation updated:', message.data);
      break;
    case 'budget_alert':
      console.log('Budget alert received:', message.data);
      break;
    case 'price_update':
      console.log('Price update:', message.data);
      break;
    case 'heartbeat':
      // Silently handle heartbeats
      break;
    default:
      console.log('Unknown message type:', message);
  }
};

socket.onclose = function(event) {
  if (event.wasClean) {
    console.log(`Connection closed cleanly, code=${event.code}, reason=${event.reason}`);
  } else {
    console.log('Connection died');
  }
};

socket.onerror = function(error) {
  console.log('WebSocket error:', error);
};
```

## MCP Protocol

The Budget component supports the Multi-Component Protocol (MCP) for standardized communication with other Tekton components. MCP endpoints are accessible at:

```
http://{hostname}:{port}/api/mcp
```

See the [MCP Protocol Documentation](/MetaData/TektonDocumentation/Architecture/MCPProtocol.md) for detailed information on the MCP protocol.

## Rate Limiting

The Budget API implements rate limiting to prevent abuse. Current limits are:

- 100 requests per minute per API key
- 1000 requests per hour per API key

When a rate limit is exceeded, the API returns a 429 Too Many Requests status code with a Retry-After header indicating how long to wait before making another request.

## Versioning

The Budget API follows semantic versioning. The current version is `0.1.0`.

You can specify the API version in the request header:

```
X-API-Version: 0.1.0
```

## Support

For issues or questions about the Budget API, please contact the Tekton team or open an issue in the Tekton repository.