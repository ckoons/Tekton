# Hermes

## Overview

Hermes is the core messaging and service discovery component of the Tekton ecosystem. Named after the Greek messenger of the gods, Hermes enables seamless communication between all Tekton components, providing a centralized registry for service discovery, standardized messaging patterns, and reliable message delivery.

## Key Features

- **Service Registry**: Central registry for component registration and discovery
- **Message Bus**: Reliable message routing between components
- **API Gateway**: Single entry point for external systems to access Tekton services
- **Event Broadcasting**: Publish-subscribe pattern for broadcasting events
- **Single Port Architecture**: Unified port for HTTP, WebSocket, and Event endpoints
- **Standardized Communication**: Consistent message formats and protocols
- **Service Health Monitoring**: Active monitoring of component health
- **Dynamic Component Discovery**: Runtime discovery of available components
- **Authentication & Authorization**: Secure access to component services
- **Logging & Metrics**: Centralized logging and performance metrics

## Architecture

Hermes follows a modular architecture with the following components:

1. **Core Message Bus**: The foundation that handles routing and delivery of messages
   - Message Queue: Ensures reliable message delivery
   - Router: Determines message destinations
   - Protocol Handlers: Supports different message protocols (HTTP, WebSocket, Events)

2. **Service Registry**: Maintains a directory of all available components
   - Registration API: Allows components to register their capabilities
   - Discovery API: Enables components to find and connect to each other
   - Health Checking: Monitors component availability and health

3. **API Layer**: Exposes RESTful and WebSocket interfaces
   - Registry Endpoints: Manage service registration and discovery
   - Message Endpoints: Send and receive messages between components
   - Administrative Endpoints: Manage Hermes configuration and monitoring

4. **Database Layer**: Persistent storage for component registrations
   - Component Registry: Stores component information and capabilities
   - Message History: Optional storage of message history for debugging
   - Configuration Store: Persistent storage for Hermes configuration

## Registration Process

Components register with Hermes during startup:

```python
from hermes.api.client import HermesClient

def register_component():
    client = HermesClient(host="localhost", port=8000)
    
    registration_data = {
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
        "dependencies": ["engram", "rhetor"]
    }
    
    response = client.register_component(registration_data)
    return response
```

## Discovery Process

Components can discover other components through Hermes:

```python
from hermes.api.client import HermesClient

def discover_components():
    client = HermesClient(host="localhost", port=8000)
    
    # Find a specific component
    engram = client.discover_component("engram")
    
    # Find components with specific capabilities
    memory_components = client.discover_components_by_capability("memory_storage")
    
    # Find all available components
    all_components = client.list_components()
    
    return engram, memory_components, all_components
```

## Messaging

Components can send messages to each other through Hermes:

```python
from hermes.api.client import HermesClient

def send_message():
    client = HermesClient(host="localhost", port=8000)
    
    message = {
        "source": "example_component",
        "target": "rhetor",
        "type": "request",
        "payload": {
            "action": "generate_text",
            "parameters": {
                "prompt": "Hello, world!",
                "model": "claude-3-sonnet-20240229"
            }
        }
    }
    
    response = client.send_message(message)
    return response
```

## Event Broadcasting

Components can broadcast and subscribe to events:

```python
from hermes.api.client import HermesClient

# Publishing an event
def publish_event():
    client = HermesClient(host="localhost", port=8000)
    
    event = {
        "source": "example_component",
        "type": "data_updated",
        "payload": {
            "dataset_id": "12345",
            "timestamp": "2024-05-01T10:00:00Z"
        }
    }
    
    client.publish_event(event)

# Subscribing to events
def subscribe_to_events():
    client = HermesClient(host="localhost", port=8000)
    
    # Subscribe to specific event types
    subscription = client.subscribe_to_events(
        event_types=["data_updated", "analysis_completed"],
        callback=handle_event
    )
    
    return subscription

def handle_event(event):
    print(f"Received event: {event['type']}")
    print(f"Payload: {event['payload']}")
```

## Integration with Other Components

Hermes is the central integration point for all Tekton components:

- **Engram**: Hermes enables communication with Engram for memory operations
- **Rhetor**: Components access LLM capabilities through Hermes
- **Athena**: Knowledge graph queries are routed through Hermes
- **Ergon**: Agent communication and tool invocation use Hermes
- **Harmonia**: Workflow orchestration messages flow through Hermes
- **Terma**: Terminal interfaces connect to backend services via Hermes

## API Reference

Hermes provides a comprehensive API for component registration, discovery, and messaging:

### Service Registry API

- `POST /api/hermes/registry/components`: Register a component
- `GET /api/hermes/registry/components`: List all registered components
- `GET /api/hermes/registry/components/{component_id}`: Get component details
- `DELETE /api/hermes/registry/components/{component_id}`: Unregister a component
- `GET /api/hermes/registry/capabilities`: List all available capabilities
- `GET /api/hermes/registry/capabilities/{capability}`: List components with a specific capability

### Messaging API

- `POST /api/hermes/messages`: Send a message
- `GET /api/hermes/messages/{message_id}`: Get message status
- `POST /api/hermes/events`: Publish an event
- `GET /api/hermes/events/subscriptions`: List active event subscriptions
- `POST /api/hermes/events/subscriptions`: Create a new event subscription
- `DELETE /api/hermes/events/subscriptions/{subscription_id}`: Cancel an event subscription

### WebSocket API

- `ws://localhost:8000/ws/hermes/messages`: Real-time message streaming
- `ws://localhost:8000/ws/hermes/events`: Real-time event streaming

## Deployment

Hermes is typically the first component to be deployed in a Tekton system:

```bash
# Start Hermes
cd Hermes
python -m hermes.api.app
```

In the Tekton startup sequence, Hermes is launched first, and other components connect to it during their initialization.

## Configuration

Hermes is configured through environment variables:

```bash
# Core Configuration
HERMES_HOST=0.0.0.0
HERMES_PORT=8000
HERMES_DEBUG=false

# Database Configuration
HERMES_DB_URI=sqlite:///hermes.db

# Security Configuration
HERMES_API_KEY=your_api_key_here
HERMES_JWT_SECRET=your_jwt_secret_here

# Logging Configuration
HERMES_LOG_LEVEL=info
HERMES_LOG_FILE=/var/log/hermes.log
```

## Getting Started

To use Hermes in your Tekton component:

1. Import the Hermes client:

```python
from hermes.api.client import HermesClient
```

2. Create a client instance:

```python
client = HermesClient(host="localhost", port=8000)
```

3. Register your component:

```python
registration_data = {
    "component": "my_component",
    "description": "My Tekton component",
    "version": "1.0.0",
    "endpoints": [...],
    "capabilities": [...],
    "host": "localhost",
    "port": 8006,
    "health_check": "/api/my_component/health"
}

client.register_component(registration_data)
```

4. Discover other components:

```python
engram = client.discover_component("engram")
rhetor = client.discover_component("rhetor")
```

5. Send messages and publish events:

```python
client.send_message(message)
client.publish_event(event)
```

For more detailed information, see the [API Reference](./API_REFERENCE.md) and [Integration Guide](./INTEGRATION_GUIDE.md).