# Hermes Integration Guide

## Overview

This guide explains how to integrate your Tekton component with Hermes for service discovery, messaging, and event handling. Hermes serves as the central communication hub for all Tekton components, enabling them to discover and interact with each other.

## Prerequisites

- A Tekton component that needs to communicate with other components
- Hermes installed and running (typically on port 8000)
- Python 3.10 or higher
- Hermes client library

## Integration Steps

### 1. Install the Hermes Client

Add the Hermes client to your component's dependencies:

```bash
pip install tekton-hermes-client
```

Or, if working within the Tekton repository:

```bash
# From your component directory
pip install -e ../Hermes
```

### 2. Configure Environment Variables

Set up the environment variables for Hermes connection:

```bash
# .env file
HERMES_HOST=localhost
HERMES_PORT=8000
HERMES_API_KEY=your_api_key_here
```

In your component, load these variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

hermes_config = {
    "host": os.getenv("HERMES_HOST", "localhost"),
    "port": int(os.getenv("HERMES_PORT", 8000)),
    "api_key": os.getenv("HERMES_API_KEY", "")
}
```

### 3. Create a Hermes Client

Initialize the Hermes client in your component:

```python
from hermes.api.client import HermesClient

class MyComponent:
    def __init__(self):
        self.hermes = HermesClient(
            host=hermes_config["host"],
            port=hermes_config["port"],
            api_key=hermes_config["api_key"]
        )
        # Other initialization code...
```

### 4. Register Your Component

Register your component with Hermes during startup:

```python
async def register_with_hermes(self):
    """Register this component with Hermes."""
    try:
        registration_data = {
            "component": "my_component",
            "description": "My Tekton component description",
            "version": "1.0.0",
            "endpoints": [
                {
                    "path": "/api/my_component",
                    "methods": ["GET", "POST"],
                    "description": "Main API endpoint"
                },
                {
                    "path": "/ws/my_component",
                    "description": "WebSocket endpoint"
                }
            ],
            "capabilities": ["capability_1", "capability_2"],
            "host": os.getenv("MY_COMPONENT_HOST", "localhost"),
            "port": int(os.getenv("MY_COMPONENT_PORT", 8005)),
            "health_check": "/api/my_component/health",
            "dependencies": ["engram", "rhetor"]
        }
        
        response = await self.hermes.register_component(registration_data)
        self.registration_id = response.get("registration_id")
        
        print(f"Component registered with Hermes: {self.registration_id}")
        
        # Start heartbeat
        self.start_heartbeat()
        
        return True
    except Exception as e:
        print(f"Failed to register with Hermes: {str(e)}")
        return False
```

### 5. Implement Heartbeat

Send periodic heartbeats to Hermes to indicate your component is still active:

```python
import asyncio

def start_heartbeat(self):
    """Start sending heartbeats to Hermes."""
    asyncio.create_task(self._heartbeat_loop())

async def _heartbeat_loop(self):
    """Send heartbeats every 30 seconds."""
    while True:
        try:
            await self._send_heartbeat()
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
        except Exception as e:
            print(f"Heartbeat error: {str(e)}")
            await asyncio.sleep(5)  # Wait before retrying

async def _send_heartbeat(self):
    """Send a single heartbeat."""
    if not self.registration_id:
        return
    
    try:
        # Get some basic metrics
        metrics = {
            "cpu_usage": self._get_cpu_usage(),
            "memory_usage": self._get_memory_usage(),
            "request_count": self.request_counter
        }
        
        await self.hermes.send_heartbeat(
            component_id="my_component",
            status="active",
            metrics=metrics
        )
    except Exception as e:
        print(f"Failed to send heartbeat: {str(e)}")
```

### 6. Discover Other Components

Use Hermes to discover other components and their endpoints:

```python
async def discover_components(self):
    """Discover other components."""
    try:
        # Find Engram
        engram = await self.hermes.discover_component("engram")
        if engram:
            self.engram_url = f"http://{engram['host']}:{engram['port']}{engram['endpoints'][0]['path']}"
            print(f"Discovered Engram at {self.engram_url}")
        
        # Find all components with a specific capability
        llm_components = await self.hermes.discover_components_by_capability("llm_integration")
        for component in llm_components:
            print(f"Found LLM component: {component['component']}")
        
        return True
    except Exception as e:
        print(f"Component discovery failed: {str(e)}")
        return False
```

### 7. Send and Receive Messages

Communicate with other components through Hermes:

```python
async def send_message_to_component(self, target, payload):
    """Send a message to another component."""
    try:
        message = {
            "source": "my_component",
            "target": target,
            "type": "request",
            "correlation_id": self._generate_correlation_id(),
            "payload": payload
        }
        
        response = await self.hermes.send_message(message)
        return response
    except Exception as e:
        print(f"Failed to send message: {str(e)}")
        return None

def _generate_correlation_id(self):
    """Generate a unique correlation ID."""
    import uuid
    return f"corr-{uuid.uuid4()}"
```

### 8. Handle Incoming Messages

Set up a message handler for your component:

```python
from fastapi import APIRouter, Depends, HTTPException, WebSocket, Request

router = APIRouter()

@router.post("/messages")
async def receive_message(request: Request):
    """Handle incoming messages from Hermes."""
    data = await request.json()
    
    # Validate the message
    if not data.get("source") or not data.get("payload"):
        raise HTTPException(status_code=400, detail="Invalid message format")
    
    # Process the message
    result = await process_message(data)
    
    # Return a response
    return {
        "success": True,
        "message": "Message processed successfully",
        "result": result
    }

async def process_message(message):
    """Process an incoming message."""
    source = message.get("source")
    message_type = message.get("type", "request")
    correlation_id = message.get("correlation_id")
    payload = message.get("payload", {})
    
    print(f"Received message from {source}, type: {message_type}")
    
    # Handle different message types
    if message_type == "request":
        action = payload.get("action")
        if action == "get_data":
            return {"data": get_requested_data(payload)}
        elif action == "process_item":
            return {"status": process_item(payload)}
    
    return {"status": "unknown_action"}
```

### 9. Work with Events

Publish events and subscribe to events from other components:

```python
# Publishing events
async def publish_data_update_event(self, dataset_id, affected_records):
    """Publish a data update event."""
    try:
        event = {
            "source": "my_component",
            "type": "data_updated",
            "payload": {
                "dataset_id": dataset_id,
                "timestamp": datetime.utcnow().isoformat(),
                "affected_records": affected_records
            }
        }
        
        await self.hermes.publish_event(event)
        return True
    except Exception as e:
        print(f"Failed to publish event: {str(e)}")
        return False

# Subscribing to events
async def subscribe_to_events(self):
    """Subscribe to relevant events."""
    try:
        # Set up the callback URL
        callback_url = f"http://{self.host}:{self.port}/api/my_component/events"
        
        subscription = {
            "subscriber": "my_component",
            "event_types": ["data_updated", "analysis_completed"],
            "source_filter": ["sophia", "athena"],
            "callback_url": callback_url,
            "webhook_secret": self.webhook_secret
        }
        
        result = await self.hermes.create_subscription(subscription)
        self.subscription_id = result.get("subscription_id")
        
        print(f"Subscribed to events: {self.subscription_id}")
        return True
    except Exception as e:
        print(f"Failed to subscribe to events: {str(e)}")
        return False

# Event handler endpoint
@router.post("/events")
async def handle_event(request: Request):
    """Handle incoming events from subscriptions."""
    data = await request.json()
    
    # Validate the webhook signature
    signature = request.headers.get("X-Hermes-Signature")
    if not validate_webhook_signature(data, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Process the event
    event_source = data.get("source")
    event_type = data.get("type")
    payload = data.get("payload", {})
    
    print(f"Received event from {event_source}, type: {event_type}")
    
    # Handle different event types
    if event_type == "data_updated":
        await handle_data_update(payload)
    elif event_type == "analysis_completed":
        await handle_analysis_completed(payload)
    
    return {"success": True}
```

### 10. Use WebSockets for Real-time Communication

Connect to Hermes WebSocket for real-time messaging:

```python
import websockets
import json

async def connect_to_hermes_websocket(self):
    """Connect to Hermes WebSocket for real-time messaging."""
    uri = f"ws://{hermes_config['host']}:{hermes_config['port']}/ws/hermes/messages"
    
    # Include authentication in the connection URI
    uri += f"?api_key={hermes_config['api_key']}&component=my_component"
    
    try:
        self.ws = await websockets.connect(uri)
        
        # Send connect message
        connect_msg = {
            "type": "connect",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "component": "my_component",
                "version": "1.0.0"
            }
        }
        await self.ws.send(json.dumps(connect_msg))
        
        # Start listening for messages
        asyncio.create_task(self._websocket_listener())
        
        return True
    except Exception as e:
        print(f"WebSocket connection failed: {str(e)}")
        return False

async def _websocket_listener(self):
    """Listen for WebSocket messages."""
    try:
        while True:
            message = await self.ws.recv()
            data = json.loads(message)
            
            # Handle different message types
            if data["type"] == "connected":
                print(f"Connected to Hermes WebSocket: {data['payload']['session_id']}")
            elif data["type"] == "receive_message":
                await self._handle_websocket_message(data["payload"])
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        # Try to reconnect
        await asyncio.sleep(5)
        asyncio.create_task(self.connect_to_hermes_websocket())

async def _handle_websocket_message(self, payload):
    """Handle a message received via WebSocket."""
    source = payload.get("source")
    message_type = payload.get("message_type")
    content = payload.get("content", {})
    
    print(f"Received WebSocket message from {source}, type: {message_type}")
    
    # Process the message
    # ...
```

### 11. Implement Graceful Shutdown

Properly deregister your component when shutting down:

```python
async def shutdown(self):
    """Shut down the component gracefully."""
    try:
        # Deregister from Hermes
        if self.registration_id:
            await self.hermes.deregister_component("my_component")
            print("Component deregistered from Hermes")
        
        # Close WebSocket connection
        if hasattr(self, 'ws') and self.ws:
            await self.ws.close()
            print("WebSocket connection closed")
            
        # Cancel any subscriptions
        if self.subscription_id:
            await self.hermes.cancel_subscription(self.subscription_id)
            print("Event subscriptions cancelled")
            
        return True
    except Exception as e:
        print(f"Error during shutdown: {str(e)}")
        return False
```

### 12. Create a Helper Module for Hermes Integration

To simplify Hermes integration across your codebase, create a helper module:

```python
# hermes_helper.py
from hermes.api.client import HermesClient
import os
import asyncio
import json

class HermesHelper:
    """Helper class for Hermes integration."""
    
    def __init__(self, component_id, component_version, host=None, port=None, api_key=None):
        """Initialize the Hermes helper."""
        self.component_id = component_id
        self.component_version = component_version
        self.host = host or os.getenv("HERMES_HOST", "localhost")
        self.port = int(port or os.getenv("HERMES_PORT", 8000))
        self.api_key = api_key or os.getenv("HERMES_API_KEY", "")
        
        self.client = HermesClient(
            host=self.host,
            port=self.port,
            api_key=self.api_key
        )
        
        self.registration_id = None
        self.heartbeat_task = None
        self.ws_connection = None
        self._message_handlers = {}
    
    async def register(self, endpoints, capabilities, dependencies=None):
        """Register with Hermes."""
        try:
            # Create registration data
            registration_data = {
                "component": self.component_id,
                "description": f"{self.component_id} - Tekton component",
                "version": self.component_version,
                "endpoints": endpoints,
                "capabilities": capabilities,
                "host": os.getenv(f"{self.component_id.upper()}_HOST", "localhost"),
                "port": int(os.getenv(f"{self.component_id.upper()}_PORT", "8000")),
                "health_check": f"/api/{self.component_id}/health",
                "dependencies": dependencies or []
            }
            
            # Register with Hermes
            response = await self.client.register_component(registration_data)
            self.registration_id = response.get("registration_id")
            
            # Start heartbeat
            self._start_heartbeat()
            
            return True
        except Exception as e:
            print(f"Failed to register with Hermes: {str(e)}")
            return False
    
    def _start_heartbeat(self):
        """Start sending heartbeats."""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
    
    async def _heartbeat_loop(self):
        """Send heartbeats periodically."""
        while True:
            try:
                await self.client.send_heartbeat(
                    component_id=self.component_id,
                    status="active"
                )
                await asyncio.sleep(30)
            except Exception as e:
                print(f"Heartbeat error: {str(e)}")
                await asyncio.sleep(5)
    
    async def discover_component(self, component_id):
        """Discover a component by ID."""
        return await self.client.discover_component(component_id)
    
    async def discover_by_capability(self, capability):
        """Discover components by capability."""
        return await self.client.discover_components_by_capability(capability)
    
    async def send_message(self, target, message_type, content, correlation_id=None):
        """Send a message to another component."""
        import uuid
        
        message = {
            "source": self.component_id,
            "target": target,
            "type": message_type,
            "correlation_id": correlation_id or f"corr-{uuid.uuid4()}",
            "payload": content
        }
        
        return await self.client.send_message(message)
    
    async def publish_event(self, event_type, payload, metadata=None):
        """Publish an event."""
        event = {
            "source": self.component_id,
            "type": event_type,
            "payload": payload,
            "metadata": metadata or {}
        }
        
        return await self.client.publish_event(event)
    
    async def connect_websocket(self):
        """Connect to Hermes WebSocket."""
        import websockets
        
        uri = f"ws://{self.host}:{self.port}/ws/hermes/messages"
        uri += f"?api_key={self.api_key}&component={self.component_id}"
        
        self.ws_connection = await websockets.connect(uri)
        
        # Send connect message
        connect_msg = {
            "type": "connect",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "component": self.component_id,
                "version": self.component_version
            }
        }
        await self.ws_connection.send(json.dumps(connect_msg))
        
        # Start listener
        asyncio.create_task(self._ws_listener())
    
    async def _ws_listener(self):
        """Listen for WebSocket messages."""
        try:
            while True:
                message = await self.ws_connection.recv()
                data = json.loads(message)
                
                if data["type"] == "receive_message":
                    # Handle the message
                    source = data["payload"]["source"]
                    message_type = data["payload"]["message_type"]
                    
                    # Check if we have a handler
                    key = f"{source}:{message_type}"
                    if key in self._message_handlers:
                        await self._message_handlers[key](data["payload"])
        except Exception as e:
            print(f"WebSocket error: {str(e)}")
            # Try to reconnect
            await asyncio.sleep(5)
            asyncio.create_task(self.connect_websocket())
    
    def register_message_handler(self, source, message_type, handler):
        """Register a handler for a specific message type."""
        key = f"{source}:{message_type}"
        self._message_handlers[key] = handler
    
    async def shutdown(self):
        """Shut down Hermes integration."""
        try:
            # Cancel heartbeat
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
            
            # Deregister
            if self.registration_id:
                await self.client.deregister_component(self.component_id)
            
            # Close WebSocket
            if self.ws_connection:
                await self.ws_connection.close()
            
            return True
        except Exception as e:
            print(f"Error during Hermes shutdown: {str(e)}")
            return False
```

### 13. Use the Helper in Your Component

Integrate the helper in your component:

```python
from my_component.utils.hermes_helper import HermesHelper

class MyComponent:
    def __init__(self):
        # Create Hermes helper
        self.hermes = HermesHelper(
            component_id="my_component",
            component_version="1.0.0"
        )
        
        # Other initialization...
    
    async def startup(self):
        """Start the component."""
        # Register endpoints
        endpoints = [
            {
                "path": "/api/my_component",
                "methods": ["GET", "POST"],
                "description": "Main API endpoint"
            },
            {
                "path": "/ws/my_component",
                "description": "WebSocket endpoint"
            }
        ]
        
        # Register capabilities
        capabilities = ["data_processing", "visualization"]
        
        # Register dependencies
        dependencies = ["engram", "rhetor"]
        
        # Register with Hermes
        await self.hermes.register(endpoints, capabilities, dependencies)
        
        # Discover required components
        engram = await self.hermes.discover_component("engram")
        if engram:
            self.engram_url = f"http://{engram['host']}:{engram['port']}{engram['endpoints'][0]['path']}"
        
        # Connect to WebSocket for real-time messaging
        await self.hermes.connect_websocket()
        
        # Register message handlers
        self.hermes.register_message_handler(
            source="rhetor",
            message_type="response",
            handler=self.handle_rhetor_response
        )
    
    async def handle_rhetor_response(self, message):
        """Handle responses from Rhetor."""
        print(f"Received response from Rhetor: {message['content']}")
        # Process the response...
    
    async def shutdown(self):
        """Shut down the component."""
        await self.hermes.shutdown()
```

## Common Integration Patterns

### Health Check Integration

Implement a health check endpoint that Hermes can call:

```python
@router.get("/health")
async def health_check():
    """Health check endpoint for Hermes."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "component": "my_component",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Dependency Management

Wait for dependencies to be available before completing startup:

```python
async def wait_for_dependencies(self):
    """Wait for all dependencies to be available."""
    dependencies = ["engram", "rhetor"]
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            all_available = True
            
            for dep in dependencies:
                component = await self.hermes.discover_component(dep)
                if not component:
                    all_available = False
                    print(f"Dependency {dep} not available yet")
                    break
            
            if all_available:
                print("All dependencies available")
                return True
            
            retry_count += 1
            await asyncio.sleep(5)  # Wait 5 seconds before retrying
        except Exception as e:
            print(f"Error checking dependencies: {str(e)}")
            retry_count += 1
            await asyncio.sleep(5)
    
    print("Failed to find all dependencies")
    return False
```

### Fault Tolerance

Implement retry logic for Hermes communication:

```python
async def retry_operation(self, operation, max_retries=3, retry_delay=2):
    """Retry an operation with exponential backoff."""
    retries = 0
    last_error = None
    
    while retries < max_retries:
        try:
            return await operation()
        except Exception as e:
            last_error = e
            retries += 1
            wait_time = retry_delay * (2 ** (retries - 1))  # Exponential backoff
            print(f"Operation failed, retrying in {wait_time}s: {str(e)}")
            await asyncio.sleep(wait_time)
    
    # If we get here, all retries failed
    print(f"Operation failed after {max_retries} retries: {str(last_error)}")
    raise last_error
```

## Testing Hermes Integration

### Unit Testing with Mocks

Create mocks for testing Hermes integration:

```python
# test_hermes_integration.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_hermes_client():
    """Create a mock Hermes client."""
    mock = AsyncMock()
    mock.register_component = AsyncMock(return_value={"registration_id": "test-reg-id"})
    mock.discover_component = AsyncMock(return_value={
        "component": "engram",
        "host": "localhost",
        "port": 8002,
        "endpoints": [{"path": "/api/engram"}]
    })
    mock.send_message = AsyncMock(return_value={"message_id": "test-msg-id"})
    
    return mock

@pytest.mark.asyncio
async def test_component_registration(mock_hermes_client):
    """Test component registration with Hermes."""
    with patch('my_component.utils.hermes_helper.HermesClient', return_value=mock_hermes_client):
        from my_component.utils.hermes_helper import HermesHelper
        helper = HermesHelper("test_component", "1.0.0")
        
        result = await helper.register(
            endpoints=[{"path": "/api/test"}],
            capabilities=["test_capability"]
        )
        
        assert result is True
        mock_hermes_client.register_component.assert_called_once()
        
        # Check call arguments
        call_args = mock_hermes_client.register_component.call_args[0][0]
        assert call_args["component"] == "test_component"
        assert call_args["version"] == "1.0.0"
        assert call_args["capabilities"] == ["test_capability"]
```

### Integration Testing with Hermes

Create integration tests with a real Hermes instance:

```python
# integration_test_hermes.py
import pytest
import os
import asyncio
from my_component.utils.hermes_helper import HermesHelper

@pytest.mark.integration
@pytest.mark.asyncio
async def test_hermes_integration():
    """Test integration with a real Hermes instance."""
    # Ensure Hermes is running
    hermes_host = os.getenv("TEST_HERMES_HOST", "localhost")
    hermes_port = int(os.getenv("TEST_HERMES_PORT", 8000))
    
    helper = HermesHelper(
        component_id="test_integration",
        component_version="1.0.0",
        host=hermes_host,
        port=hermes_port
    )
    
    try:
        # Register with Hermes
        registered = await helper.register(
            endpoints=[{"path": "/api/test_integration", "methods": ["GET"]}],
            capabilities=["test_capability"]
        )
        assert registered is True
        
        # Discover ourselves
        component = await helper.discover_component("test_integration")
        assert component is not None
        assert component["component"] == "test_integration"
        
        # Publish a test event
        event_result = await helper.publish_event(
            event_type="test_event",
            payload={"message": "This is a test event"}
        )
        assert event_result is not None
        
        # Clean up
        await helper.shutdown()
    except Exception as e:
        # Make sure to shut down even if the test fails
        await helper.shutdown()
        raise e
```

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Ensure Hermes is running at the specified host and port
   - Check firewall settings

2. **Authentication Failure**:
   - Verify the API key is correct
   - Check if API keys are properly configured in Hermes

3. **Component Not Found**:
   - Ensure the component is registered properly
   - Check for typos in component IDs
   - Verify the component is still active (sending heartbeats)

4. **Message Delivery Failures**:
   - Check that the target component exists and is active
   - Verify that the message format is correct
   - Look for network connectivity issues

### Debugging Tools

1. **Enable Debug Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   logging.getLogger('hermes').setLevel(logging.DEBUG)
   ```

2. **Hermes Health Check**:
   ```bash
   curl http://localhost:8000/api/hermes/health
   ```

3. **Check Component Registration**:
   ```bash
   curl http://localhost:8000/api/hermes/registry/components
   ```

4. **Monitor WebSocket Connections**:
   Use the Hermes admin dashboard to view active WebSocket connections.

## Best Practices

1. **Always Deregister on Shutdown**:
   Ensure your component properly deregisters when shutting down.

2. **Send Regular Heartbeats**:
   Keep your component registration active with regular heartbeats.

3. **Use Correlation IDs**:
   Include correlation IDs in all messages to track request-response flows.

4. **Implement Retry Logic**:
   Add retry logic for Hermes operations to handle temporary failures.

5. **Validate Messages**:
   Always validate incoming messages before processing them.

6. **Use Timeouts**:
   Set appropriate timeouts for message delivery and component discovery.

7. **Handle Reconnections**:
   Implement reconnection logic for WebSocket connections.

8. **Secure Your Webhooks**:
   Validate webhook signatures to ensure the authenticity of event notifications.

9. **Monitor Component Health**:
   Regularly check the health of dependencies and handle failures gracefully.

10. **Structure Event Payloads Consistently**:
    Use consistent payload structures for events to simplify handling.

## Resources

- [Hermes API Reference](./API_REFERENCE.md)
- [Hermes Client Documentation](https://docs.example.com/hermes-client)
- [Tekton Component Integration Guide](../TektonDocumentation/Architecture/ComponentIntegrationPatterns.md)