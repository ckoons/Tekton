# Hermes User Guide

## Introduction

Hermes is the central communication and service discovery system for the Tekton ecosystem. This guide will help you integrate with Hermes, register your components, and use its messaging capabilities.

## Getting Started

### Installation

1. Ensure you have Python 3.9+ installed
2. Clone the Hermes repository:
   ```bash
   git clone git@github.com:yourusername/Tekton.git
   cd Tekton/Hermes
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Start the Hermes server:
   ```bash
   python -m hermes.api.app
   ```

By default, Hermes runs on port 8002. You can change this by setting the `HERMES_PORT` environment variable.

### Basic Configuration

Create a configuration file named `hermes_config.json`:

```json
{
  "server": {
    "host": "localhost",
    "port": 8002,
    "debug": false
  },
  "database": {
    "type": "sqlite",
    "path": "hermes.db"
  },
  "security": {
    "api_key_required": true,
    "admin_key": "your-admin-key"
  }
}
```

## Registering Your Component

The first step in using Hermes is to register your component or service.

### Using the Registration Helper

The simplest way to register is using the registration helper:

```python
from hermes.utils.registration_helper import register_component

# Register your component
component_info = {
    "name": "MyComponent",
    "version": "1.0.0",
    "description": "My awesome Tekton component",
    "endpoints": {
        "http": "http://localhost:8010/api",
        "websocket": "ws://localhost:8010/ws"
    },
    "capabilities": ["data-processing", "visualization"]
}

api_key = register_component("http://localhost:8002/api/register", component_info)
print(f"Registered successfully, API key: {api_key}")
```

### Using the Registration Script

Alternatively, you can use the provided registration script:

```bash
python register_with_hermes.py --name MyComponent --version 1.0.0 --http-endpoint http://localhost:8010/api --ws-endpoint ws://localhost:8010/ws
```

### Maintaining Registration

To keep your component's registration active, you need to send periodic heartbeats:

```python
import time
import requests

def send_heartbeat(hermes_url, component_id, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(
        f"{hermes_url}/api/heartbeat",
        headers=headers,
        json={"component_id": component_id}
    )
    return response.status_code == 200

# Send heartbeat every 30 seconds
while True:
    success = send_heartbeat("http://localhost:8002", "my-component-id", "my-api-key")
    if not success:
        print("Failed to send heartbeat")
    time.sleep(30)
```

## Discovering Services

You can discover other registered services through the service discovery API.

### Finding All Services

```python
import requests

def get_all_services(hermes_url, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(f"{hermes_url}/api/services", headers=headers)
    return response.json()

services = get_all_services("http://localhost:8002", "my-api-key")
for service in services:
    print(f"Found service: {service['name']} ({service['id']})")
```

### Finding Services by Capability

```python
import requests

def find_services_by_capability(hermes_url, capability, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(
        f"{hermes_url}/api/services",
        headers=headers,
        params={"capability": capability}
    )
    return response.json()

llm_services = find_services_by_capability(
    "http://localhost:8002", 
    "llm-processing", 
    "my-api-key"
)
print(f"Found {len(llm_services)} LLM processing services")
```

## Sending and Receiving Messages

Hermes provides a message bus for component communication.

### Sending Messages

```python
import requests
import uuid

def send_message(hermes_url, topic, message, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "id": str(uuid.uuid4()),
        "topic": topic,
        "payload": message,
        "timestamp": datetime.now().isoformat()
    }
    response = requests.post(
        f"{hermes_url}/api/messages",
        headers=headers,
        json=payload
    )
    return response.json()

# Send a message
result = send_message(
    "http://localhost:8002",
    "data-updates",
    {"data_type": "analytics", "value": 42},
    "my-api-key"
)
print(f"Message sent with ID: {result['id']}")
```

### Subscribing to Messages (WebSocket)

```python
import websocket
import json
import threading

def on_message(ws, message):
    data = json.loads(message)
    print(f"Received message on topic {data['topic']}: {data['payload']}")

def on_open(ws):
    print("Connection opened")
    # Subscribe to topics
    ws.send(json.dumps({
        "type": "subscribe",
        "topics": ["data-updates", "system-notifications"]
    }))

# Connect to Hermes WebSocket endpoint
ws_app = websocket.WebSocketApp(
    "ws://localhost:8002/ws",
    on_open=on_open,
    on_message=on_message
)

# Start WebSocket connection in a separate thread
threading.Thread(target=ws_app.run_forever).start()
```

## Using the A2A (Agent-to-Agent) Protocol

The A2A protocol enables communication between specialized agents.

### Creating a Conversation

```python
import requests

def create_conversation(hermes_url, initiator_id, participants, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "initiator_id": initiator_id,
        "participants": participants
    }
    response = requests.post(
        f"{hermes_url}/api/a2a/conversations",
        headers=headers,
        json=payload
    )
    return response.json()

# Create a conversation between two agents
conversation = create_conversation(
    "http://localhost:8002",
    "browser-agent-1",
    ["browser-agent-1", "code-agent-1"],
    "my-api-key"
)
conversation_id = conversation["id"]
print(f"Created conversation: {conversation_id}")
```

### Sending Messages in a Conversation

```python
import requests

def send_conversation_message(hermes_url, conversation_id, sender_id, content, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "sender_id": sender_id,
        "content": content
    }
    response = requests.post(
        f"{hermes_url}/api/a2a/conversations/{conversation_id}/messages",
        headers=headers,
        json=payload
    )
    return response.json()

# Send a message in the conversation
message = send_conversation_message(
    "http://localhost:8002",
    conversation_id,
    "browser-agent-1",
    {
        "type": "task",
        "task_type": "code_analysis",
        "payload": {
            "code": "function example() { return 'Hello World'; }",
            "language": "javascript"
        }
    },
    "my-api-key"
)
print(f"Sent message: {message['id']}")
```

### Retrieving Conversation History

```python
import requests

def get_conversation_history(hermes_url, conversation_id, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(
        f"{hermes_url}/api/a2a/conversations/{conversation_id}",
        headers=headers
    )
    return response.json()

# Get conversation history
history = get_conversation_history(
    "http://localhost:8002", 
    conversation_id, 
    "my-api-key"
)
print(f"Conversation has {len(history['messages'])} messages")
for msg in history["messages"]:
    print(f"[{msg['timestamp']}] {msg['sender_id']}: {msg['content']['type']}")
```

## Using the MCP (Message Communication Protocol)

The MCP standardizes message formats across components.

### Sending MCP Messages

```python
import requests

def send_mcp_message(hermes_url, source, destination, msg_type, body, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "header": {
            "source": source,
            "destination": destination,
            "type": msg_type
        },
        "body": body
    }
    response = requests.post(
        f"{hermes_url}/api/mcp/send",
        headers=headers,
        json=payload
    )
    return response.json()

# Send MCP message
result = send_mcp_message(
    "http://localhost:8002",
    "my-component",
    "target-component",
    "REQUEST",
    {"action": "get-data", "parameters": {"id": "12345"}},
    "my-api-key"
)
print(f"Message sent with ID: {result['id']}")
```

### Implementing an MCP Handler

To handle incoming MCP messages, implement a handler in your component:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/mcp", methods=["POST"])
def handle_mcp_message():
    message = request.json
    
    # Extract message details
    source = message["header"]["source"]
    msg_type = message["header"]["type"]
    body = message["body"]
    
    print(f"Received {msg_type} message from {source}")
    
    # Process message based on type
    if msg_type == "REQUEST":
        # Handle request
        action = body.get("action")
        if action == "get-data":
            # Process get-data request
            data_id = body["parameters"]["id"]
            result = {"data": f"Data for ID {data_id}"}
            
            # Send response
            send_mcp_message(
                "http://localhost:8002",
                "my-component",
                source,
                "RESPONSE",
                {
                    "request_id": message["header"]["id"],
                    "status": "success",
                    "data": result
                },
                "my-api-key"
            )
    
    return jsonify({"status": "received"})

if __name__ == "__main__":
    app.run(port=8010)
```

## Common Integration Patterns

### Component Registration at Startup

A common pattern is to register your component during startup:

```python
import os
import sys
import requests
import uuid
import signal
import threading
import time

# Component information
component_info = {
    "id": str(uuid.uuid4()),
    "name": "MyComponent",
    "version": "1.0.0",
    "http_endpoint": "http://localhost:8010/api",
    "ws_endpoint": "ws://localhost:8010/ws",
    "capabilities": ["data-processing"]
}

# Register with Hermes
try:
    response = requests.post(
        "http://localhost:8002/api/register",
        json=component_info
    )
    if response.status_code != 200:
        print(f"Failed to register with Hermes: {response.text}")
        sys.exit(1)
        
    result = response.json()
    api_key = result["api_key"]
    print(f"Registered with Hermes, API key: {api_key}")
    
    # Start heartbeat thread
    def heartbeat_loop():
        while True:
            try:
                requests.post(
                    "http://localhost:8002/api/heartbeat",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"component_id": component_info["id"]}
                )
            except Exception as e:
                print(f"Failed to send heartbeat: {e}")
            time.sleep(30)
    
    heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
    heartbeat_thread.start()
    
    # Handle graceful shutdown
    def handle_shutdown(signum, frame):
        print("Deregistering component...")
        try:
            requests.delete(
                f"http://localhost:8002/api/services/{component_info['id']}",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            print("Deregistered successfully")
        except Exception as e:
            print(f"Failed to deregister: {e}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
except Exception as e:
    print(f"Error during registration: {e}")
    sys.exit(1)

# Continue with component startup...
```

### Dynamic Service Discovery

Discover and use services dynamically based on capabilities:

```python
def get_service_for_capability(hermes_url, capability, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(
        f"{hermes_url}/api/services",
        headers=headers,
        params={"capability": capability}
    )
    services = response.json()
    
    if not services:
        return None
        
    # Pick the first available service
    return services[0]

def use_llm_service(text_input):
    service = get_service_for_capability(
        "http://localhost:8002", 
        "llm-processing", 
        "my-api-key"
    )
    
    if not service:
        print("No LLM service available")
        return None
        
    # Call the service's API
    response = requests.post(
        f"{service['http_endpoint']}/process",
        json={"text": text_input}
    )
    
    return response.json()
```

### Event-Based Communication

Use the message bus for event-based communication:

```python
# Publisher: Send event when data changes
def publish_data_change(data_id, new_value):
    send_message(
        "http://localhost:8002",
        "data-changes",
        {
            "data_id": data_id,
            "new_value": new_value,
            "timestamp": datetime.now().isoformat()
        },
        "my-api-key"
    )

# Subscriber: Process data change events
def on_message(ws, message):
    data = json.loads(message)
    
    if data['topic'] == 'data-changes':
        payload = data['payload']
        data_id = payload['data_id']
        new_value = payload['new_value']
        
        print(f"Data changed: {data_id} = {new_value}")
        # Update local cache or UI
        update_local_data(data_id, new_value)
```

## Troubleshooting

### Common Issues

1. **Registration Fails**
   - Check that Hermes is running
   - Verify your component information is valid
   - Ensure no other component is using the same ID

2. **Can't Receive Messages**
   - Check your WebSocket connection
   - Verify you've subscribed to the correct topics
   - Ensure your API key has necessary permissions

3. **Service Not Found**
   - Check that the service is registered and active
   - Verify you're using the correct capability name
   - Check for typos in service ID or name

### Diagnostic Commands

Check the status of Hermes:

```bash
curl http://localhost:8002/api/status
```

List all registered services:

```bash
curl http://localhost:8002/api/services
```

Check your component's registration:

```bash
curl http://localhost:8002/api/services/{your-component-id}
```

## Best Practices

1. **Graceful Degradation**
   - Always handle cases where Hermes is unavailable
   - Implement fallback mechanisms for critical functionality
   - Cache important service information locally

2. **Efficient Message Handling**
   - Keep messages small and focused
   - Use appropriate topics for message organization
   - Only subscribe to topics your component needs

3. **Security**
   - Store API keys securely
   - Never log or expose API keys
   - Validate message sources before processing

4. **Reliability**
   - Implement reconnection logic for WebSocket connections
   - Use try/except blocks when calling Hermes APIs
   - Implement exponential backoff for retries

## Conclusion

This guide covers the basics of integrating with Hermes. For more detailed information, check the [API Reference](./API_REFERENCE.md) and [Technical Documentation](./TECHNICAL_DOCUMENTATION.md).

If you encounter issues or need assistance, please refer to the [Tekton Documentation](../../README.md) for community support options.