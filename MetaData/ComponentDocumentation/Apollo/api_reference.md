# Apollo API Reference

This document provides a comprehensive reference for the Apollo API endpoints. Apollo implements the Single Port Architecture pattern with path-based routing for all operations.

## Base URL

The Apollo API is accessible at:

```
http://localhost:{PORT}
```

Where `PORT` is configured via environment variables (default: 8012). You can retrieve the correct port using `apollo.utils.port_config.get_apollo_port()`.

## Authentication

Authentication is not currently implemented. Future versions may include authentication mechanisms.

## Root Endpoints

### GET /

Returns basic information about the Apollo component.

**Response:**

```json
{
  "name": "Apollo Executive Coordinator",
  "version": "0.1.0",
  "status": "running",
  "documentation": "http://localhost:{PORT}/docs"
}
```

### GET /health

Returns the health status of the Apollo component, following Tekton health check standards.

**Response:**

```json
{
  "status": "healthy",  // or "degraded", "error"
  "component": "apollo",
  "version": "0.1.0", 
  "port": 8012,
  "message": "Apollo is running normally"
}
```

- Status code 200: Component is healthy or degraded
- Status code 429: Component is in a degraded state
- Status code 500: Component is in an error state

## API Endpoints

All API endpoints are accessible under the `/api` prefix.

### Context Management

#### GET /api/contexts

Get all active contexts being monitored by Apollo.

**Query Parameters:**

- `status` (optional): Filter contexts by health status (choices: "excellent", "good", "fair", "poor", "critical")

**Response:**

```json
{
  "status": "success",
  "message": "Found X contexts",
  "data": [
    {
      "context_id": "string",
      "component_id": "string",
      "provider": "string",
      "model": "string",
      "task_type": "string",
      "metrics": {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "max_tokens": 0,
        "token_utilization": 0.0,
        "input_token_rate": 0.0,
        "output_token_rate": 0.0,
        "token_rate_change": 0.0,
        "repetition_score": 0.0,
        "self_reference_score": 0.0,
        "coherence_score": 1.0,
        "latency": 0.0,
        "processing_time": 0.0,
        "timestamp": "string"
      },
      "health": "excellent",
      "health_score": 0.0,
      "creation_time": "string",
      "last_updated": "string",
      "metadata": {}
    }
  ]
}
```

#### GET /api/contexts/{context_id}

Get details for a specific context.

**Path Parameters:**

- `context_id`: Context identifier

**Query Parameters:**

- `include_history` (optional): Include context history (default: false)
- `history_limit` (optional): Limit history records (default: 10)

**Response:**

```json
{
  "status": "success",
  "message": "Context {context_id} found",
  "data": {
    "context_id": "string",
    "component_id": "string",
    "provider": "string",
    "model": "string",
    "task_type": "string",
    "metrics": {
      "input_tokens": 0,
      "output_tokens": 0,
      "total_tokens": 0,
      "max_tokens": 0,
      "token_utilization": 0.0,
      "input_token_rate": 0.0,
      "output_token_rate": 0.0,
      "token_rate_change": 0.0,
      "repetition_score": 0.0,
      "self_reference_score": 0.0,
      "coherence_score": 1.0,
      "latency": 0.0,
      "processing_time": 0.0,
      "timestamp": "string"
    },
    "health": "excellent",
    "health_score": 0.0,
    "creation_time": "string",
    "last_updated": "string",
    "metadata": {},
    "history": [
      {
        "context_id": "string",
        "metrics": {},
        "health": "string",
        "health_score": 0.0,
        "timestamp": "string"
      }
    ],
    "prediction": {},
    "actions": []
  }
}
```

#### GET /api/contexts/{context_id}/dashboard

Get comprehensive dashboard data for a specific context.

**Path Parameters:**

- `context_id`: Context identifier

**Response:**

```json
{
  "status": "success",
  "message": "Dashboard for context {context_id}",
  "data": {
    "timestamp": "string",
    "context_id": "string",
    "state": {},
    "history": [],
    "prediction": {},
    "actions": [],
    "health_trend": "stable",
    "summary": {
      "health": "string",
      "health_score": 0.0,
      "token_utilization": 0.0,
      "repetition_score": 0.0,
      "age_minutes": 0.0
    }
  }
}
```

### Prediction Management

#### GET /api/predictions

Get all predictions managed by Apollo.

**Query Parameters:**

- `health` (optional): Filter predictions by health status (choices: "excellent", "good", "fair", "poor", "critical")

**Response:**

```json
{
  "status": "success",
  "message": "Found X predictions",
  "data": [
    {
      "context_id": "string",
      "predicted_metrics": {},
      "predicted_health": "string",
      "predicted_health_score": 0.0,
      "confidence": 0.0,
      "prediction_timestamp": "string",
      "prediction_horizon": 0.0,
      "basis": "string"
    }
  ]
}
```

#### GET /api/predictions/{context_id}

Get prediction for a specific context.

**Path Parameters:**

- `context_id`: Context identifier

**Response:**

```json
{
  "status": "success",
  "message": "Prediction found for context {context_id}",
  "data": {
    "context_id": "string",
    "predicted_metrics": {},
    "predicted_health": "string",
    "predicted_health_score": 0.0,
    "confidence": 0.0,
    "prediction_timestamp": "string",
    "prediction_horizon": 0.0,
    "basis": "string"
  }
}
```

#### POST /api/predictions/request

Request a new prediction for a context.

**Request Body:**

```json
{
  "context_id": "string",
  "component": "string",
  "current_metrics": {},
  "history_length": 10,
  "prediction_horizon": 3
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Prediction request received for context {context_id}",
  "data": {}
}
```

### Action Management

#### GET /api/actions

Get all actions recommended by Apollo.

**Query Parameters:**

- `critical_only` (optional): Only return critical actions (default: false)
- `actionable_now` (optional): Only return actions that should be taken now (default: false)

**Response:**

```json
{
  "status": "success",
  "message": "Found X actions",
  "data": [
    {
      "context_id": "string",
      "action_id": "string",
      "action_type": "string",
      "priority": 0,
      "reason": "string",
      "parameters": {},
      "suggested_time": "string",
      "expires_at": "string",
      "created_at": "string"
    }
  ]
}
```

#### GET /api/actions/{context_id}

Get actions for a specific context.

**Path Parameters:**

- `context_id`: Context identifier

**Query Parameters:**

- `highest_priority_only` (optional): Only return highest priority action (default: false)

**Response:**

```json
{
  "status": "success",
  "message": "Found X actions for context {context_id}",
  "data": [
    {
      "context_id": "string",
      "action_id": "string",
      "action_type": "string",
      "priority": 0,
      "reason": "string",
      "parameters": {},
      "suggested_time": "string",
      "expires_at": "string",
      "created_at": "string"
    }
  ]
}
```

#### POST /api/actions/{action_id}/applied

Mark an action as applied.

**Path Parameters:**

- `action_id`: Action identifier

**Response:**

```json
{
  "status": "success",
  "message": "Action {action_id} marked as applied"
}
```

### Budget Management

#### POST /api/budget/allocate

Allocate a token budget.

**Request Body:**

```json
{
  "context_id": "string",
  "task_type": "string",
  "component": "string",
  "provider": "string",
  "model": "string",
  "priority": 0,
  "token_count": 0
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Budget allocated for context {context_id}",
  "data": {
    "context_id": "string",
    "allocated_tokens": 0,
    "expiration": "string",
    "policy": {}
  }
}
```

### Protocol Management

#### GET /api/protocols

Get all protocol definitions.

**Query Parameters:**

- `type` (optional): Filter protocols by type
- `scope` (optional): Filter protocols by scope

**Response:**

```json
{
  "status": "success",
  "message": "Found X protocols",
  "data": [
    {
      "protocol_id": "string",
      "name": "string",
      "description": "string",
      "type": "string",
      "scope": "string",
      "enforcement_mode": "string",
      "severity": "string",
      "version": "string",
      "created_at": "string",
      "updated_at": "string",
      "applicable_components": [],
      "applicable_endpoints": [],
      "applicable_message_types": [],
      "rules": {},
      "schema": {},
      "enabled": true,
      "priority": 0
    }
  ]
}
```

#### GET /api/protocols/{protocol_id}

Get a specific protocol definition.

**Path Parameters:**

- `protocol_id`: Protocol identifier

**Response:**

```json
{
  "status": "success",
  "message": "Protocol {protocol_id} found",
  "data": {
    "protocol_id": "string",
    "name": "string",
    "description": "string",
    "type": "string",
    "scope": "string",
    "enforcement_mode": "string",
    "severity": "string",
    "version": "string",
    "created_at": "string",
    "updated_at": "string",
    "applicable_components": [],
    "applicable_endpoints": [],
    "applicable_message_types": [],
    "rules": {},
    "schema": {},
    "enabled": true,
    "priority": 0,
    "stats": {
      "protocol_id": "string",
      "total_evaluations": 0,
      "total_violations": 0,
      "violations_by_severity": {},
      "violations_by_component": {},
      "last_violation": "string",
      "last_evaluation": "string"
    }
  }
}
```

#### POST /api/protocols

Create a new protocol definition.

**Request Body:**

```json
{
  "protocol_id": "string",
  "name": "string",
  "description": "string",
  "type": "string",
  "scope": "string",
  "enforcement_mode": "string",
  "severity": "string",
  "version": "string",
  "applicable_components": [],
  "applicable_endpoints": [],
  "applicable_message_types": [],
  "rules": {},
  "schema": {},
  "enabled": true,
  "priority": 0
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Protocol {protocol_id} created",
  "data": {}
}
```

#### PUT /api/protocols/{protocol_id}

Update a protocol definition.

**Path Parameters:**

- `protocol_id`: Protocol identifier

**Request Body:**

```json
{
  "protocol_id": "string",
  "name": "string",
  "description": "string",
  "type": "string",
  "scope": "string",
  "enforcement_mode": "string",
  "severity": "string",
  "version": "string",
  "applicable_components": [],
  "applicable_endpoints": [],
  "applicable_message_types": [],
  "rules": {},
  "schema": {},
  "enabled": true,
  "priority": 0
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Protocol {protocol_id} updated",
  "data": {}
}
```

#### DELETE /api/protocols/{protocol_id}

Delete a protocol definition.

**Path Parameters:**

- `protocol_id`: Protocol identifier

**Response:**

```json
{
  "status": "success",
  "message": "Protocol {protocol_id} deleted"
}
```

#### GET /api/protocols/violations

Get protocol violations.

**Query Parameters:**

- `component` (optional): Filter by component
- `protocol_id` (optional): Filter by protocol ID
- `severity` (optional): Filter by severity
- `limit` (optional): Maximum number of violations to return (default: 100)

**Response:**

```json
{
  "status": "success",
  "message": "Found X violations",
  "data": [
    {
      "violation_id": "string",
      "protocol_id": "string",
      "component": "string",
      "endpoint": "string",
      "message_type": "string",
      "severity": "string",
      "message": "string",
      "details": {},
      "context_id": "string",
      "timestamp": "string",
      "corrective_action_taken": "string"
    }
  ]
}
```

### Message Management

#### POST /api/messages

Send a message from Apollo.

**Request Body:**

```json
{
  "message_id": "string",
  "type": "string",
  "source": "string",
  "timestamp": "string",
  "priority": 0,
  "correlation_id": "string",
  "reply_to": "string",
  "context_id": "string",
  "payload": {},
  "metadata": {}
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Message {message_id} sent",
  "data": {
    "message_id": "string"
  }
}
```

#### POST /api/messages/subscription

Create a message subscription.

**Request Body:**

```json
{
  "message_types": ["string"],
  "filter_expression": "string",
  "callback_url": "string"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Subscription {subscription_id} created",
  "data": {
    "subscription_id": "string"
  }
}
```

#### DELETE /api/messages/subscription/{subscription_id}

Delete a message subscription.

**Path Parameters:**

- `subscription_id`: Subscription identifier

**Response:**

```json
{
  "status": "success",
  "message": "Subscription {subscription_id} deleted"
}
```

### System Status

#### GET /api/status

Get Apollo system status.

**Response:**

```json
{
  "status": "success",
  "message": "Apollo system status",
  "data": {
    "timestamp": "string",
    "active_contexts": 0,
    "health_distribution": {},
    "critical_contexts": 0,
    "critical_predictions": 0,
    "pending_actions": 0,
    "critical_actions": 0,
    "actionable_now": 0,
    "components_status": {
      "context_observer": true,
      "predictive_engine": true,
      "action_planner": true,
      "message_handler": true
    },
    "system_running": true
  }
}
```

## Metrics Endpoints

All metrics endpoints are accessible under the `/metrics` prefix.

#### GET /metrics/health

Get context health metrics.

**Response:**

```json
{
  "status": "success",
  "message": "Context health metrics",
  "data": {
    "health_distribution": {},
    "health_percentages": {},
    "total_contexts": 0,
    "critical_contexts": 0,
    "timestamp": "string"
  }
}
```

#### GET /metrics/predictions

Get prediction metrics.

**Response:**

```json
{
  "status": "success",
  "message": "Prediction metrics",
  "data": {
    "prediction_accuracy": {},
    "critical_predictions": 0,
    "total_predictions": 0,
    "health_distribution": {},
    "timestamp": "string"
  }
}
```

#### GET /metrics/actions

Get action metrics.

**Response:**

```json
{
  "status": "success",
  "message": "Action metrics",
  "data": {
    "total_actions": 0,
    "critical_actions": 0,
    "actionable_now": 0,
    "type_distribution": {},
    "priority_distribution": {},
    "action_stats": {},
    "timestamp": "string"
  }
}
```

#### GET /metrics/protocols

Get protocol metrics.

**Response:**

```json
{
  "status": "success",
  "message": "Protocol metrics",
  "data": {
    "total_protocols": 0,
    "total_evaluations": 0,
    "total_violations": 0,
    "violation_rate": 0.0,
    "violation_summary": {},
    "timestamp": "string"
  }
}
```

#### GET /metrics/messages

Get message metrics.

**Response:**

```json
{
  "status": "success",
  "message": "Message metrics",
  "data": {
    "queue_stats": {
      "outbound_queue_size": 0,
      "outbound_queue_max_size": 0,
      "inbound_queue_size": 0,
      "inbound_queue_max_size": 0,
      "current_batch_size": 0,
      "batch_size_limit": 0,
      "delivery_records_count": 0,
      "local_subscriptions_count": 0,
      "remote_subscriptions_count": 0
    },
    "delivery_stats": {},
    "timestamp": "string"
  }
}
```

## WebSocket Endpoint

### WS /ws

Provides real-time updates for context monitoring, actions, and predictions.

**Query Parameters:**

- `token` (optional): Authentication token

**Messages:**

The WebSocket connection supports bidirectional communication with the following message types:

**Server → Client:**

- `connection_established`: Sent when connection is established
- `error`: Sent when an error occurs
- `context_update`: Sent when a context is updated
- `prediction_created`: Sent when a new prediction is created
- `action_recommended`: Sent when a new action is recommended
- `pong`: Response to ping message

**Client → Server:**

- `ping`: Check connection status
- `subscribe`: Subscribe to specific updates
- `command`: Execute a command

Example subscription message:

```json
{
  "type": "subscribe",
  "message_types": ["context_update", "action_recommended"],
  "filter": {
    "context_id": "specific-context-id"
  }
}
```

## Error Responses

All API endpoints return errors in the following format:

```json
{
  "status": "error",
  "message": "Error message",
  "errors": ["Detailed error message"]
}
```