# Terma Integration Guide

This guide provides detailed information on integrating Terma with other systems, especially within the Tekton ecosystem. It covers integration patterns, APIs, communication protocols, and best practices.

## Table of Contents

- [Integration with Tekton Components](#integration-with-tekton-components)
- [Hermes Integration](#hermes-integration)
- [LLM Adapter Integration](#llm-adapter-integration)
- [Hephaestus UI Integration](#hephaestus-ui-integration)
- [External System Integration](#external-system-integration)
- [Single Port Architecture](#single-port-architecture)
- [Client Libraries](#client-libraries)
- [Event-Based Communication](#event-based-communication)

## Integration with Tekton Components

Terma is designed to work seamlessly with other Tekton components, following the ecosystem's architecture patterns.

### Core Integration Points

1. **Hermes**: For service discovery and message passing
2. **LLM Adapter**: For LLM assistance features
3. **Hephaestus UI**: For visual presentation
4. **Engram**: For persistent memory (future integration)
5. **Rhetor**: For advanced language model features (future integration)

### Integration Architecture

```
┌───────────────────────────────────────┐
│           Hephaestus UI               │
└─────────────────┬─────────────────────┘
                 │
                 ▼
┌───────────────────────────────────────┐
│               Terma                   │
└────┬──────────────┬───────────────┬───┘
     │              │               │
     ▼              ▼               ▼
┌─────────┐  ┌─────────────┐  ┌─────────┐
│ Hermes  │  │ LLM Adapter │  │ Engram  │
└─────────┘  └─────────────┘  └─────────┘
```

## Hermes Integration

Terma integrates with Hermes for service discovery, event publishing, and message handling.

### Registration with Hermes

Terma registers with Hermes by providing its capabilities and API endpoints.

```python
# Python example of Terma registration with Hermes
hermes_integration = HermesIntegration(
    api_url="http://localhost:8000",
    component_name="Terma",
    capabilities=["terminal", "command_execution", "llm_terminal_assistance"]
)
hermes_integration.register_capabilities()
```

### Capabilities Exposed via Hermes

When registered with Hermes, Terma exposes the following capabilities:

1. **Terminal Sessions**: Create, manage, and interact with terminal sessions
2. **Command Execution**: Execute commands in a terminal environment
3. **LLM Terminal Assistance**: Provide AI-powered assistance for terminal commands

### Message Schema

Terma accepts the following message commands via Hermes:

#### Create Session Command

```json
{
  "command": "TERMINAL_CREATE",
  "payload": {
    "shell_command": "/bin/bash"
  }
}
```

#### Execute Command

```json
{
  "command": "TERMINAL_EXECUTE",
  "payload": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "command": "ls -la"
  }
}
```

#### Close Session

```json
{
  "command": "TERMINAL_CLOSE",
  "payload": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Event Publication

Terma publishes the following events to Hermes:

#### Session Created Event

```json
{
  "event": "terminal.session.created",
  "payload": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "shell_command": "/bin/bash",
    "created_at": 1617184632.54
  }
}
```

#### Session Closed Event

```json
{
  "event": "terminal.session.closed",
  "payload": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "closed_at": 1617184932.54
  }
}
```

## LLM Adapter Integration

Terma integrates with the LLM Adapter to provide AI-powered assistance for terminal commands.

### Connection to LLM Adapter

Terma connects to the LLM Adapter using both HTTP and WebSocket protocols:

```python
# Simplified example of LLM Adapter connection
self.adapter_url = self.config.get("llm.adapter_url", "http://localhost:8300")
self.adapter_ws_url = self.config.get("llm.adapter_ws_url", "ws://localhost:8300/ws")
```

### Single Port Architecture Support

With the Single Port Architecture, Terma connects to the LLM Adapter through path-based routing:

```python
# Single Port Architecture LLM Adapter connection
base_url = "http://localhost:8300"
self.adapter_url = f"{base_url}/api"
self.adapter_ws_url = f"{base_url.replace('http', 'ws')}/ws"
```

### Message Format

Terma sends the following message formats to the LLM Adapter:

#### Command Analysis Request

```json
{
  "message": "Please explain this command concisely: find . -name '*.py' | xargs grep 'def'",
  "context_id": "terma",
  "streaming": false,
  "options": {
    "model": "claude-3-sonnet-20240229",
    "provider": "claude",
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```

#### WebSocket Command

```json
{
  "type": "LLM_REQUEST",
  "source": "TERMA",
  "timestamp": 1617184632.54,
  "payload": {
    "message": "Please explain this command concisely: find . -name '*.py' | xargs grep 'def'",
    "context": "terma",
    "streaming": false,
    "options": {
      "model": "claude-3-sonnet-20240229",
      "provider": "claude",
      "temperature": 0.7,
      "max_tokens": 500
    }
  }
}
```

### Graceful Degradation

Terma implements graceful degradation when the LLM Adapter is unavailable:

1. First attempts HTTP API
2. Falls back to WebSocket API if HTTP fails
3. Provides a fallback message if both connection methods fail

## Hephaestus UI Integration

Terma integrates with the Hephaestus UI through a web component that provides a rich terminal interface.

### Component Installation

To install the Terma component in Hephaestus:

```bash
./install_in_hephaestus.sh
```

This script:
1. Copies the component files to Hephaestus UI
2. Updates the component registry
3. Configures the component to connect to Terma

### Component Communication

The Terma component communicates with the Terma server through:

1. REST API for session management
2. WebSocket for real-time terminal I/O

### Service Registration

Terma registers a service with the Hephaestus UI service registry:

```javascript
// JavaScript example of service registration
window.tektonUI.registerService('termaService', termaService);
```

Other components can then access Terma functionality:

```javascript
// Example of another component using Terma
const termaService = window.tektonUI.services.termaService;
termaService.createSession().then(sessionId => {
  console.log(`Created terminal session: ${sessionId}`);
});
```

## External System Integration

Terma can be integrated with external systems through its HTTP and WebSocket APIs.

### REST API Integration

External systems can use the REST API to interact with Terma:

```python
# Python example of REST API integration
import requests

# Create a session
response = requests.post(
    "http://localhost:8765/api/sessions",
    json={"shell_command": "/bin/bash"}
)
session_id = response.json()["session_id"]

# Execute a command
requests.post(
    f"http://localhost:8765/api/sessions/{session_id}/write",
    json={"data": "ls -la\n"}
)

# Read output
response = requests.get(
    f"http://localhost:8765/api/sessions/{session_id}/read"
)
print(response.json()["data"])
```

### WebSocket Integration

For real-time interaction, external systems can use the WebSocket API:

```javascript
// JavaScript example of WebSocket integration
const ws = new WebSocket(`ws://localhost:8765/ws/${sessionId}`);

ws.onopen = () => {
  console.log('WebSocket connected');
  
  // Send input
  ws.send(JSON.stringify({
    type: 'input',
    data: 'ls -la\n'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'output') {
    console.log(message.data);
  }
};
```

## Single Port Architecture

Terma follows the Tekton Single Port Architecture pattern for simplified deployment and integration.

### Path-Based Routing

With Single Port Architecture, all Terma endpoints are accessed through a single port with path-based routing:

- REST API: `/api/*`
- WebSocket: `/ws/*`
- UI: `/terminal/*`

### Configuration for Single Port Architecture

To configure Terma for Single Port Architecture:

```bash
# Set the port for the Single Port Architecture
export TERMA_PORT=8767

# Start Terma with Single Port Architecture
python -m terma.cli.main
```

### Proxy Configuration

When using a reverse proxy for Single Port Architecture:

```nginx
# Nginx example for Single Port Architecture
location /terma/ {
    proxy_pass http://localhost:8767/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

location /terma/ws/ {
    proxy_pass http://localhost:8767/ws/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

## Client Libraries

Terma provides client libraries for easier integration.

### Python Client

```python
from examples.terminal_client import TermaClient

async def example():
    client = TermaClient(base_url="http://localhost:8765")
    
    # Create a session
    session = await client.create_session()
    session_id = session["session_id"]
    
    # Write a command
    await client.write_to_session(session_id, "echo 'Hello, Terma!'\n")
    
    # Read output
    response = await client.read_from_session(session_id)
    print(response["data"])
    
    # Close the session
    await client.close_session(session_id)
```

### JavaScript Client

```javascript
import { TermaClient } from 'terma-client';

const client = new TermaClient({
  baseUrl: 'http://localhost:8765',
  wsUrl: 'ws://localhost:8765/ws'
});

// Create a session
client.createSession()
  .then(sessionId => {
    console.log(`Session created: ${sessionId}`);
    
    // Connect to the session
    return client.connectToSession(sessionId);
  })
  .then(websocket => {
    // Send input
    client.sendInput('echo "Hello, Terma!"\n');
    
    // Register output handler
    client.onOutput(data => console.log(data));
  })
  .catch(error => console.error('Error:', error));
```

## Event-Based Communication

Terma uses event-based communication for asynchronous integration.

### Published Events

Terma publishes the following events:

| Event | Description | Payload |
|-------|-------------|---------|
| `terminal.session.created` | Session created | `session_id`, `shell_command`, `created_at` |
| `terminal.session.closed` | Session closed | `session_id`, `closed_at` |
| `terminal.command.executed` | Command executed | `session_id`, `command`, `timestamp` |
| `terminal.output.received` | Output received | `session_id`, `output`, `timestamp` |

### Subscribing to Events

Other components can subscribe to Terma events through Hermes:

```python
# Python example of subscribing to Terma events through Hermes
hermes_client = HermesClient(api_url="http://localhost:8000")
hermes_client.subscribe_to_event("terminal.session.created", callback_function)
```

### WebSocket Events

Terma also emits events through WebSocket connections:

```javascript
// JavaScript example of handling WebSocket events
const ws = new WebSocket(`ws://localhost:8765/ws/${sessionId}`);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'output':
      console.log('Terminal output:', message.data);
      break;
    case 'error':
      console.error('Terminal error:', message.message);
      break;
    case 'llm_response':
      console.log('LLM response:', message.content);
      break;
  }
};
```

## Integration Best Practices

1. **Use the Client Libraries**: Whenever possible, use the provided client libraries for the most reliable integration.

2. **Handle Reconnections**: Implement WebSocket reconnection logic to maintain connection during network issues.

3. **Graceful Degradation**: Implement fallback mechanisms when dependent services are unavailable.

4. **Event-Based Communication**: Prefer event-based communication over polling for real-time updates.

5. **Security Considerations**: When integrating in production environments, implement proper authentication and authorization.

6. **Resource Management**: Close sessions when no longer needed to free up server resources.

7. **Error Handling**: Implement robust error handling to gracefully handle service failures.

8. **Monitoring Integration**: Set up monitoring for the integration points to detect and address issues quickly.