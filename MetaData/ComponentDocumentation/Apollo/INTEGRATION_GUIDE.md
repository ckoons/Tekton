# Apollo Integration Guide

This guide provides detailed instructions for integrating Apollo with other Tekton components and external systems. It covers API integration, event handling, and best practices for effective component communication.

## Table of Contents

- [Introduction](#introduction)
- [Integration Architecture](#integration-architecture)
- [Core Integration Patterns](#core-integration-patterns)
- [Integrating with Apollo](#integrating-with-apollo)
- [Apollo as a Client](#apollo-as-a-client)
- [Integration with Tekton Components](#integration-with-tekton-components)
- [External System Integration](#external-system-integration)
- [Event-Based Communication](#event-based-communication)
- [Authentication and Security](#authentication-and-security)
- [Error Handling](#error-handling)
- [Performance Considerations](#performance-considerations)
- [Testing Integrations](#testing-integrations)
- [Monitoring Integrations](#monitoring-integrations)
- [Troubleshooting](#troubleshooting)

## Introduction

Apollo serves as the executive coordinator for Tekton's LLM operations, providing context monitoring, token budgeting, protocol enforcement, and action planning. Effective integration with Apollo allows components to benefit from these capabilities while contributing to the overall system's health and performance.

## Integration Architecture

Apollo follows the Tekton Single Port Architecture pattern, which simplifies integration through standardized endpoints:

```
http://localhost:8001/
```

The integration endpoints are organized into three main categories:

1. **HTTP API Endpoints**: RESTful endpoints under `/api/` prefix
2. **WebSocket Endpoints**: Real-time communication under `/ws`
3. **Event-Based Endpoints**: Message handling under `/events`

## Core Integration Patterns

Apollo supports several integration patterns:

### 1. Request-Response Pattern

For synchronous operations where an immediate response is needed:

```
Component → HTTP Request → Apollo → HTTP Response → Component
```

### 2. Subscription Pattern

For receiving updates about specific events:

```
Component → Subscribe → Apollo
Apollo → Event Occurs → Notification → Component
```

### 3. Publish-Subscribe Pattern

For distributing messages to multiple subscribers:

```
Component → Publish Message → Apollo → Distribute → Subscribers
```

### 4. Command Pattern

For executing specific actions:

```
Component → Send Command → Apollo → Execute → Response → Component
```

## Integrating with Apollo

### HTTP API Integration

Components can directly interact with Apollo's HTTP API endpoints:

#### Python Example:

```python
import requests
import json

class ApolloClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        
    def get_contexts(self, health=None):
        """Get all contexts with optional health filter."""
        params = {}
        if health:
            params["health"] = health
            
        response = requests.get(
            f"{self.base_url}/api/contexts",
            params=params
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error getting contexts: {response.text}")
    
    def get_context(self, context_id):
        """Get details for a specific context."""
        response = requests.get(
            f"{self.base_url}/api/contexts/{context_id}"
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error getting context: {response.text}")
    
    def allocate_budget(self, context_id, component, tier, task_type, tokens_requested, priority=5):
        """Allocate token budget for an operation."""
        data = {
            "context_id": context_id,
            "component": component,
            "tier": tier,
            "task_type": task_type,
            "tokens_requested": tokens_requested,
            "priority": priority
        }
        
        response = requests.post(
            f"{self.base_url}/api/budget/allocate",
            json=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error allocating budget: {response.text}")
```

#### JavaScript Example:

```javascript
class ApolloClient {
  constructor(baseUrl = 'http://localhost:8001') {
    this.baseUrl = baseUrl;
  }
  
  async getContexts(health = null) {
    const params = new URLSearchParams();
    if (health) {
      params.append('health', health);
    }
    
    const response = await fetch(
      `${this.baseUrl}/api/contexts?${params.toString()}`
    );
    
    if (response.ok) {
      return await response.json();
    } else {
      throw new Error(`Error getting contexts: ${await response.text()}`);
    }
  }
  
  async getContext(contextId) {
    const response = await fetch(
      `${this.baseUrl}/api/contexts/${contextId}`
    );
    
    if (response.ok) {
      return await response.json();
    } else {
      throw new Error(`Error getting context: ${await response.text()}`);
    }
  }
  
  async allocateBudget(contextId, component, tier, taskType, tokensRequested, priority = 5) {
    const data = {
      context_id: contextId,
      component: component,
      tier: tier,
      task_type: taskType,
      tokens_requested: tokensRequested,
      priority: priority
    };
    
    const response = await fetch(
      `${this.baseUrl}/api/budget/allocate`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    );
    
    if (response.ok) {
      return await response.json();
    } else {
      throw new Error(`Error allocating budget: ${await response.text()}`);
    }
  }
}
```

### WebSocket Integration

For real-time updates, components can connect to Apollo's WebSocket endpoint:

#### Python Example:

```python
import asyncio
import websockets
import json

class ApolloWebSocketClient:
    def __init__(self, base_url="ws://localhost:8001"):
        self.base_url = base_url
        self.websocket = None
        
    async def connect(self):
        """Connect to Apollo WebSocket."""
        self.websocket = await websockets.connect(f"{self.base_url}/ws")
        
    async def subscribe(self, channels, filters=None):
        """Subscribe to specific channels with optional filters."""
        if not self.websocket:
            await self.connect()
            
        subscription = {
            "type": "subscribe",
            "channels": channels
        }
        
        if filters:
            subscription["filters"] = filters
            
        await self.websocket.send(json.dumps(subscription))
        
        # Receive confirmation
        response = await self.websocket.recv()
        return json.loads(response)
        
    async def listen(self, callback):
        """Listen for messages and call the callback."""
        if not self.websocket:
            await self.connect()
            
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await callback(data)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
            
    async def close(self):
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
```

#### JavaScript Example:

```javascript
class ApolloWebSocketClient {
  constructor(baseUrl = 'ws://localhost:8001') {
    this.baseUrl = baseUrl;
    this.socket = null;
    this.listeners = {};
  }
  
  connect() {
    return new Promise((resolve, reject) => {
      this.socket = new WebSocket(`${this.baseUrl}/ws`);
      
      this.socket.onopen = () => {
        console.log('Connected to Apollo WebSocket');
        resolve();
      };
      
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };
      
      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        // Call appropriate listeners based on message type
        if (data.type && this.listeners[data.type]) {
          this.listeners[data.type].forEach(callback => callback(data));
        }
        
        // Call general listeners
        if (this.listeners['*']) {
          this.listeners['*'].forEach(callback => callback(data));
        }
      };
      
      this.socket.onclose = () => {
        console.log('Disconnected from Apollo WebSocket');
      };
    });
  }
  
  subscribe(channels, filters = null) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error('Socket not connected');
    }
    
    const subscription = {
      type: 'subscribe',
      channels: channels
    };
    
    if (filters) {
      subscription.filters = filters;
    }
    
    this.socket.send(JSON.stringify(subscription));
  }
  
  addEventListener(type, callback) {
    if (!this.listeners[type]) {
      this.listeners[type] = [];
    }
    
    this.listeners[type].push(callback);
  }
  
  removeEventListener(type, callback) {
    if (this.listeners[type]) {
      this.listeners[type] = this.listeners[type].filter(cb => cb !== callback);
    }
  }
  
  close() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}
```

## Apollo as a Client

Apollo needs to interact with other components to fulfill its responsibilities. Here's how other components can expose endpoints for Apollo:

### Context Metrics API

Components that generate LLM contexts should implement an API for Apollo to monitor:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

app = FastAPI()

class ContextMetrics(BaseModel):
    context_id: str
    component_id: str
    provider: Optional[str] = None
    model: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    max_tokens: int = 0
    timestamp: datetime

@app.get("/api/contexts")
async def get_contexts():
    """Return all active contexts."""
    # Implementation specific to your component
    return {"contexts": [...]}

@app.get("/api/contexts/{context_id}")
async def get_context(context_id: str):
    """Return details for a specific context."""
    # Implementation specific to your component
    return {...}

@app.get("/api/contexts/{context_id}/metrics")
async def get_context_metrics(context_id: str):
    """Return metrics for a specific context."""
    # Implementation specific to your component
    return {...}

@app.post("/api/actions/{context_id}")
async def apply_action(context_id: str, action: Dict[str, Any]):
    """Apply an action to a context."""
    # Implementation specific to your component
    return {"status": "success", "message": "Action applied"}
```

### Action Application API

Components that can apply Apollo's recommended actions should expose an endpoint:

```python
@app.post("/api/contexts/{context_id}/actions")
async def apply_action(context_id: str, action_data: dict):
    """
    Apply an action to a context.
    
    Action types:
    - context_reduction: Remove redundant content
    - context_restructuring: Reorganize context
    - token_management: Apply token optimization
    - model_switching: Switch to different model
    - session_refresh: Start new session
    - parameter_adjustment: Modify parameters
    """
    action_type = action_data.get("action_type")
    parameters = action_data.get("parameters", {})
    
    if action_type == "context_reduction":
        # Implement context reduction logic
        reduction_amount = parameters.get("target_reduction", 0.3)
        strategy = parameters.get("strategy", "summarize_older_content")
        result = apply_context_reduction(context_id, reduction_amount, strategy)
        
    elif action_type == "context_restructuring":
        # Implement context restructuring logic
        result = apply_context_restructuring(context_id, parameters)
        
    # Additional action types...
        
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported action type: {action_type}")
    
    return {
        "status": "success",
        "context_id": context_id,
        "action_type": action_type,
        "result": result
    }
```

## Integration with Tekton Components

### Rhetor Integration

Apollo integrates with Rhetor to monitor LLM contexts and apply corrective actions:

#### Context Monitoring

1. Apollo subscribes to Rhetor's context metrics:

```python
# Apollo's Rhetor integration
async def subscribe_to_rhetor_metrics():
    rhetor_url = os.environ.get("RHETOR_API_URL", "http://localhost:8000")
    
    # Create subscription
    subscription_data = {
        "event_type": "context_metrics",
        "callback_url": f"http://localhost:8001/api/callbacks/rhetor/metrics"
    }
    
    response = await httpx.post(
        f"{rhetor_url}/api/subscriptions",
        json=subscription_data
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to subscribe to Rhetor metrics: {response.text}")
        
    return response.json()
```

2. Rhetor sends metrics to Apollo's callback endpoint:

```python
# Apollo's callback endpoint for Rhetor metrics
@app.post("/api/callbacks/rhetor/metrics")
async def rhetor_metrics_callback(metrics_data: dict):
    # Process incoming metrics
    context_id = metrics_data.get("context_id")
    
    # Update context state
    await context_observer.update_context_metrics(
        context_id=context_id,
        metrics=metrics_data.get("metrics", {})
    )
    
    return {"status": "success"}
```

#### Action Application

Apollo sends recommended actions back to Rhetor:

```python
# Apollo's action application to Rhetor
async def apply_action_to_rhetor(context_id: str, action: ContextAction):
    rhetor_url = os.environ.get("RHETOR_API_URL", "http://localhost:8000")
    
    action_data = {
        "action_id": action.action_id,
        "action_type": action.action_type,
        "parameters": action.parameters
    }
    
    response = await httpx.post(
        f"{rhetor_url}/api/contexts/{context_id}/actions",
        json=action_data
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to apply action to Rhetor: {response.text}")
        
    # Mark action as applied
    await action_planner.mark_action_applied(
        action_id=action.action_id,
        result=response.json()
    )
    
    return response.json()
```

### Engram Integration

Apollo uses Engram for persistent memory storage:

#### Storing Context History

```python
# Apollo's Engram integration for context history
async def store_context_history(context_id: str, context_state: ContextState):
    engram_url = os.environ.get("ENGRAM_API_URL", "http://localhost:8002")
    
    memory_data = {
        "type": "apollo_context_history",
        "source": "apollo",
        "content": {
            "context_id": context_id,
            "health": str(context_state.health),
            "health_score": context_state.health_score,
            "metrics": context_state.metrics.dict(),
            "timestamp": context_state.last_updated.isoformat()
        },
        "metadata": {
            "component": "apollo",
            "context_id": context_id,
            "health": str(context_state.health)
        }
    }
    
    response = await httpx.post(
        f"{engram_url}/api/memories",
        json=memory_data
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to store context history in Engram: {response.text}")
        
    return response.json()
```

#### Retrieving Context History

```python
# Apollo's Engram integration for retrieving context history
async def get_context_history_from_engram(context_id: str, limit: int = 100):
    engram_url = os.environ.get("ENGRAM_API_URL", "http://localhost:8002")
    
    query = {
        "type": "apollo_context_history",
        "metadata.context_id": context_id,
        "sort": "metadata.timestamp:desc",
        "limit": limit
    }
    
    response = await httpx.post(
        f"{engram_url}/api/memories/search",
        json=query
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve context history from Engram: {response.text}")
        
    return response.json()
```

### Hermes Integration

Apollo uses Hermes for message routing and service discovery:

#### Service Registration

```python
# Apollo's Hermes integration for service registration
async def register_with_hermes():
    hermes_url = os.environ.get("HERMES_API_URL", "http://localhost:8003")
    
    service_data = {
        "service_id": "apollo",
        "name": "Apollo Executive Coordinator",
        "description": "LLM operation monitoring and predictive planning",
        "base_url": f"http://localhost:8001",
        "health_endpoint": "/health",
        "version": "1.0.0",
        "capabilities": ["context_monitoring", "token_budgeting", "protocol_enforcement"],
        "dependencies": ["rhetor", "engram"],
        "endpoints": [
            {
                "path": "/api/contexts",
                "method": "GET",
                "description": "Get all contexts"
            },
            # Additional endpoints...
        ]
    }
    
    response = await httpx.post(
        f"{hermes_url}/api/services",
        json=service_data
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to register with Hermes: {response.text}")
        
    return response.json()
```

#### Message Routing

```python
# Apollo's Hermes integration for message routing
async def send_message_via_hermes(destination: str, message_type: str, content: dict):
    hermes_url = os.environ.get("HERMES_API_URL", "http://localhost:8003")
    
    message_data = {
        "source": "apollo",
        "destination": destination,
        "type": message_type,
        "content": content,
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "priority": "normal"
        }
    }
    
    response = await httpx.post(
        f"{hermes_url}/api/messages",
        json=message_data
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to send message via Hermes: {response.text}")
        
    return response.json()
```

### Synthesis Integration

Apollo coordinates with Synthesis for action execution:

```python
# Apollo's Synthesis integration for action execution
async def execute_action_via_synthesis(context_id: str, action: ContextAction):
    synthesis_url = os.environ.get("SYNTHESIS_API_URL", "http://localhost:8004")
    
    execution_data = {
        "action_id": action.action_id,
        "context_id": context_id,
        "action_type": action.action_type,
        "parameters": action.parameters,
        "priority": action.priority,
        "callback_url": f"http://localhost:8001/api/callbacks/synthesis/action_result"
    }
    
    response = await httpx.post(
        f"{synthesis_url}/api/execute",
        json=execution_data
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to execute action via Synthesis: {response.text}")
        
    return response.json()
```

## External System Integration

Apollo can integrate with external systems for monitoring and control:

### External Metrics Systems

Send Apollo metrics to external monitoring systems:

```python
# Apollo integration with Prometheus
def setup_prometheus_metrics():
    from prometheus_client import Counter, Gauge, start_http_server
    
    # Create metrics
    context_count = Gauge('apollo_active_contexts', 'Number of active contexts')
    health_distribution = Gauge('apollo_context_health', 'Context health distribution', ['health'])
    token_usage = Counter('apollo_token_usage', 'Token usage by tier', ['tier'])
    action_count = Gauge('apollo_actions', 'Number of actions by priority', ['priority'])
    
    # Start metrics server
    start_http_server(8001)
    
    # Update metrics periodically
    async def update_metrics():
        while True:
            # Get context stats
            contexts = await context_observer.get_all_context_states()
            context_count.set(len(contexts))
            
            # Update health distribution
            health_counts = {"excellent": 0, "good": 0, "fair": 0, "poor": 0, "critical": 0}
            for context in contexts:
                health_counts[context.health] += 1
                
            for health, count in health_counts.items():
                health_distribution.labels(health=health).set(count)
            
            # Wait before next update
            await asyncio.sleep(15)
    
    # Start the metrics update loop
    asyncio.create_task(update_metrics())
```

### HTTP Webhooks

Send notifications to external systems via webhooks:

```python
# Apollo webhook integration
async def send_webhook_notification(webhook_url: str, event_type: str, data: dict):
    notification = {
        "event_type": event_type,
        "source": "apollo",
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=notification,
                timeout=5.0
            )
            
            if response.status_code >= 400:
                logger.error(f"Webhook delivery failed: {response.status_code} - {response.text}")
                return False
                
            return True
            
    except Exception as e:
        logger.error(f"Webhook delivery error: {str(e)}")
        return False
```

## Event-Based Communication

Apollo supports event-based communication for loose coupling between components:

### Event Publishing

```python
# Apollo event publishing
async def publish_event(event_type: str, data: dict):
    # Get all subscriptions for this event type
    subscriptions = await subscription_repository.get_subscriptions_by_type(event_type)
    
    # Create event payload
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "source": "apollo",
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    # Deliver to all subscribers
    delivery_results = []
    for subscription in subscriptions:
        result = await deliver_event(subscription.callback_url, event)
        delivery_results.append(result)
        
    # Log delivery results
    success_count = sum(1 for r in delivery_results if r)
    logger.info(f"Event {event_type} delivered to {success_count} of {len(subscriptions)} subscribers")
    
    return {
        "event_id": event["event_id"],
        "total_subscribers": len(subscriptions),
        "successful_deliveries": success_count
    }
```

### Event Subscription

```python
# Apollo event subscription handling
@app.post("/api/subscriptions")
async def create_subscription(subscription_data: dict):
    event_types = subscription_data.get("event_types", [])
    callback_url = subscription_data.get("callback_url")
    
    if not event_types or not callback_url:
        raise HTTPException(status_code=400, detail="Event types and callback URL are required")
        
    # Create subscription
    subscription_id = str(uuid.uuid4())
    subscription = {
        "subscription_id": subscription_id,
        "event_types": event_types,
        "callback_url": callback_url,
        "created_at": datetime.now().isoformat()
    }
    
    # Store subscription
    await subscription_repository.create_subscription(subscription)
    
    return {
        "status": "success",
        "message": "Subscription created",
        "subscription_id": subscription_id
    }
```

## Authentication and Security

### API Key Authentication

Apollo can use API keys for authentication:

```python
# Apollo API key authentication
from fastapi import Security, Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader
import os
from typing import Optional

# API key header
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Get API keys from environment or configuration
API_KEYS = os.environ.get("APOLLO_API_KEYS", "key1,key2").split(",")

async def get_api_key(api_key_header: str = Security(api_key_header)) -> Optional[str]:
    if api_key_header in API_KEYS:
        return api_key_header
    raise HTTPException(
        status_code=403, 
        detail="Invalid API Key"
    )

# Protected endpoint example
@app.get("/api/protected", dependencies=[Depends(get_api_key)])
async def protected_route():
    return {"status": "success"}
```

### SSL/TLS Configuration

For secure communication, configure SSL/TLS:

```python
# Apollo SSL/TLS configuration
import uvicorn
import ssl

# Create SSL context
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain("apollo.crt", keyfile="apollo.key")

# Run with SSL
if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8001,
        ssl_keyfile="apollo.key",
        ssl_certfile="apollo.crt"
    )
```

## Error Handling

Implement robust error handling for integration failures:

```python
# Apollo error handling for integrations
async def call_external_service(service_name: str, url: str, method: str, data: dict = None):
    try:
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, timeout=10.0)
            elif method.upper() == "POST":
                response = await client.post(url, json=data, timeout=10.0)
            elif method.upper() == "PUT":
                response = await client.put(url, json=data, timeout=10.0)
            elif method.upper() == "DELETE":
                response = await client.delete(url, timeout=10.0)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json()
            
    except httpx.TimeoutException:
        logger.error(f"Timeout calling {service_name} at {url}")
        # Implement retry logic
        return await retry_call(service_name, url, method, data)
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error calling {service_name} at {url}: {e.response.status_code} - {e.response.text}")
        # Handle specific status codes
        if e.response.status_code == 429:
            # Rate limited, back off and retry
            await asyncio.sleep(2)
            return await retry_call(service_name, url, method, data)
        else:
            # Log the error and continue with degraded functionality
            return {"error": str(e)}
            
    except Exception as e:
        logger.exception(f"Error calling {service_name} at {url}: {str(e)}")
        # Fall back to default behavior
        return {"error": str(e)}
```

## Performance Considerations

### Efficient Communication

Optimize integration performance:

1. **Batch Operations**: Group related operations
2. **Connection Pooling**: Reuse HTTP connections
3. **Asynchronous Processing**: Use async/await for non-blocking operations
4. **Caching**: Cache frequently accessed data

```python
# Apollo connection pooling example
from httpx import AsyncClient, Limits

# Create a reusable client with connection pooling
limits = Limits(max_connections=100, max_keepalive_connections=20)
http_client = AsyncClient(limits=limits, timeout=10.0)

# Use the client for all requests
async def make_request(url: str, method: str, data: dict = None):
    if method.upper() == "GET":
        response = await http_client.get(url)
    elif method.upper() == "POST":
        response = await http_client.post(url, json=data)
    # Other methods...
    
    return response
```

### Rate Limiting

Implement rate limiting for external calls:

```python
# Apollo rate limiting for external services
from asyncio import Semaphore

# Create rate limiters for different services
rate_limiters = {
    "rhetor": Semaphore(10),    # Max 10 concurrent requests
    "engram": Semaphore(5),     # Max 5 concurrent requests
    "synthesis": Semaphore(3)   # Max 3 concurrent requests
}

async def rate_limited_call(service: str, url: str, method: str, data: dict = None):
    # Get the appropriate rate limiter
    limiter = rate_limiters.get(service, Semaphore(1))
    
    # Acquire the semaphore before making the call
    async with limiter:
        response = await make_request(url, method, data)
        return response
```

## Testing Integrations

### Integration Tests

Create tests for component integrations:

```python
# Apollo integration test example
import pytest
import asyncio
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_rhetor_metrics_integration():
    # Mock Rhetor API
    rhetor_mock = MagicMock()
    rhetor_mock.get_context_metrics.return_value = {
        "context_id": "test_context",
        "metrics": {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150,
            "token_utilization": 0.15,
            "repetition_score": 0.05
        }
    }
    
    # Test the integration
    with patch("apollo.core.interfaces.rhetor.RhetorInterface", return_value=rhetor_mock):
        from apollo.core.context_observer import ContextObserver
        
        # Create observer
        observer = ContextObserver()
        
        # Initialize
        await observer.initialize()
        
        # Check that subscription was created
        rhetor_mock.subscribe_to_metrics.assert_called_once()
        
        # Simulate receiving metrics
        await observer.update_context_metrics(
            context_id="test_context",
            metrics={
                "input_tokens": 100,
                "output_tokens": 50,
                "total_tokens": 150,
                "token_utilization": 0.15,
                "repetition_score": 0.05
            }
        )
        
        # Verify metrics were processed
        context = observer.get_context_state("test_context")
        assert context is not None
        assert context.metrics.total_tokens == 150
        assert context.health == "excellent"  # Should be excellent based on metrics
```

### Mock Services

Create mock services for testing integrations:

```python
# Apollo mock services for testing
from fastapi import FastAPI
import uvicorn
import threading
import time

def create_mock_rhetor():
    app = FastAPI()
    
    @app.get("/api/contexts")
    async def get_contexts():
        return {
            "contexts": [
                {
                    "context_id": "mock_context_1",
                    "component_id": "rhetor",
                    "provider": "anthropic",
                    "model": "claude-3-7-sonnet",
                    "health": "good"
                }
            ]
        }
    
    @app.get("/api/contexts/{context_id}")
    async def get_context(context_id: str):
        return {
            "context_id": context_id,
            "component_id": "rhetor",
            "provider": "anthropic",
            "model": "claude-3-7-sonnet",
            "health": "good"
        }
    
    @app.post("/api/subscriptions")
    async def create_subscription(subscription: dict):
        return {
            "subscription_id": "mock_subscription_1",
            "status": "active"
        }
    
    # Run the mock server in a separate thread
    threading.Thread(
        target=lambda: uvicorn.run(app, host="localhost", port=8000),
        daemon=True
    ).start()
    
    # Wait for server to start
    time.sleep(1)
    
    return "http://localhost:8000"
```

## Monitoring Integrations

### Health Checks

Implement health checks for dependent services:

```python
# Apollo health checks for dependencies
async def check_dependencies_health():
    dependency_health = {}
    
    # Check Rhetor
    rhetor_health = await check_service_health(
        "rhetor", 
        os.environ.get("RHETOR_API_URL", "http://localhost:8000")
    )
    dependency_health["rhetor"] = rhetor_health
    
    # Check Engram
    engram_health = await check_service_health(
        "engram", 
        os.environ.get("ENGRAM_API_URL", "http://localhost:8002")
    )
    dependency_health["engram"] = engram_health
    
    # Return overall health status
    return {
        "dependencies": dependency_health,
        "all_healthy": all(h.get("status") == "healthy" for h in dependency_health.values())
    }

async def check_service_health(service_name: str, base_url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health", timeout=2.0)
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"Received status code {response.status_code}"
                }
                
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

### Integration Metrics

Track integration performance metrics:

```python
# Apollo integration performance metrics
class IntegrationMetrics:
    def __init__(self):
        # Track request counts
        self.request_counts = {
            "rhetor": 0,
            "engram": 0,
            "synthesis": 0,
            "hermes": 0
        }
        
        # Track error counts
        self.error_counts = {
            "rhetor": 0,
            "engram": 0,
            "synthesis": 0,
            "hermes": 0
        }
        
        # Track response times (rolling average)
        self.response_times = {
            "rhetor": [],
            "engram": [],
            "synthesis": [],
            "hermes": []
        }
        
        # Max response times to track
        self.max_samples = 100
        
    def record_request(self, service: str):
        if service in self.request_counts:
            self.request_counts[service] += 1
            
    def record_error(self, service: str):
        if service in self.error_counts:
            self.error_counts[service] += 1
            
    def record_response_time(self, service: str, time_ms: float):
        if service in self.response_times:
            # Add to rolling average
            self.response_times[service].append(time_ms)
            
            # Maintain max sample size
            if len(self.response_times[service]) > self.max_samples:
                self.response_times[service].pop(0)
                
    def get_average_response_time(self, service: str) -> float:
        if service in self.response_times and self.response_times[service]:
            return sum(self.response_times[service]) / len(self.response_times[service])
        return 0.0
        
    def get_error_rate(self, service: str) -> float:
        if service in self.request_counts and self.request_counts[service] > 0:
            return self.error_counts[service] / self.request_counts[service]
        return 0.0
        
    def get_metrics(self):
        return {
            service: {
                "requests": self.request_counts[service],
                "errors": self.error_counts[service],
                "error_rate": self.get_error_rate(service),
                "avg_response_time_ms": self.get_average_response_time(service)
            }
            for service in self.request_counts.keys()
        }
```

## Troubleshooting

### Common Integration Issues

#### Connection Failures

**Symptoms:**
- Timeout errors when connecting to components
- Connection refused errors

**Solutions:**
1. Verify the component is running:
   ```bash
   ./scripts/tekton-status | grep <component_name>
   ```
2. Check the component's port configuration:
   ```bash
   cat config/port_assignments.md | grep <component_name>
   ```
3. Verify network connectivity:
   ```bash
   curl -v http://localhost:<port>/health
   ```

#### Authentication Issues

**Symptoms:**
- 401 or 403 errors when calling APIs
- "Invalid API key" errors

**Solutions:**
1. Check API key configuration:
   ```bash
   ./apollo/cli/apollo config check api_keys
   ```
2. Verify the component's authentication requirements
3. Regenerate API keys if necessary:
   ```bash
   ./apollo/cli/apollo config regenerate_api_keys
   ```

#### Data Format Issues

**Symptoms:**
- 400 Bad Request errors
- "Invalid data format" errors

**Solutions:**
1. Check the API documentation for correct data format
2. Validate your JSON payload
3. Use Apollo's protocol validation endpoint:
   ```bash
   curl -X POST http://localhost:8001/api/protocols/validate \
     -H "Content-Type: application/json" \
     -d '{
       "protocol_id": "message_format",
       "message": {...}
     }'
   ```

### Debugging Tools

#### Integration Logging

Enable detailed logging for integrations:

```bash
# Set log level to DEBUG for integration components
export APOLLO_LOG_LEVEL=DEBUG
export APOLLO_INTEGRATION_LOG_LEVEL=TRACE

# Run Apollo with verbose logging
./run_apollo.sh --verbose
```

#### Request Tracing

Implement request tracing to debug integration flows:

```python
# Apollo request tracing
import time
import uuid

class RequestTracer:
    def __init__(self):
        self.traces = {}
        
    def start_trace(self, operation: str) -> str:
        trace_id = str(uuid.uuid4())
        self.traces[trace_id] = {
            "operation": operation,
            "start_time": time.time(),
            "steps": [],
            "complete": False
        }
        return trace_id
        
    def add_step(self, trace_id: str, step: str, metadata: dict = None):
        if trace_id in self.traces:
            self.traces[trace_id]["steps"].append({
                "step": step,
                "time": time.time(),
                "elapsed": time.time() - self.traces[trace_id]["start_time"],
                "metadata": metadata or {}
            })
            
    def complete_trace(self, trace_id: str, result: dict = None):
        if trace_id in self.traces:
            self.traces[trace_id]["end_time"] = time.time()
            self.traces[trace_id]["duration"] = (
                self.traces[trace_id]["end_time"] - 
                self.traces[trace_id]["start_time"]
            )
            self.traces[trace_id]["result"] = result
            self.traces[trace_id]["complete"] = True
            
    def get_trace(self, trace_id: str):
        return self.traces.get(trace_id)
        
    def cleanup_old_traces(self, max_age_seconds: int = 3600):
        now = time.time()
        to_remove = []
        
        for trace_id, trace in self.traces.items():
            if trace["complete"] and (now - trace["end_time"]) > max_age_seconds:
                to_remove.append(trace_id)
                
        for trace_id in to_remove:
            del self.traces[trace_id]
```

#### Mock Mode

Run Apollo in mock mode for testing integrations:

```bash
# Run Apollo with mock dependencies
./run_apollo.sh --mock-dependencies

# Or set environment variables
export APOLLO_MOCK_RHETOR=true
export APOLLO_MOCK_ENGRAM=true
./run_apollo.sh
```