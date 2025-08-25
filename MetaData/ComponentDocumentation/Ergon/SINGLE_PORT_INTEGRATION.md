# Ergon: Single Port Architecture Integration

## Overview

This document details how Ergon has been integrated with Tekton's Single Port Architecture, which provides a standardized approach to port assignments and API endpoint structures across all Tekton components.

## Single Port Implementation

Ergon fully implements the Single Port Architecture pattern, allowing it to expose multiple communication protocols (HTTP, WebSocket, Events) through a single network port.

### Port Configuration

Ergon's API server is configured to use port 8002 as specified in the Tekton port assignment schema:

```
Ergon API: 8002
```

This port is used for:
- REST API endpoints
- WebSocket connections
- Server-Sent Events
- A2A protocol communication
- MCP protocol endpoints

### Environment Variables

Ergon uses standardized environment variables for port configuration:

```
ERGON_PORT=8002
ERGON_HOST=localhost
```

These variables can be overridden to change the port assignment if needed.

## URL Structure

Following the Single Port Architecture pattern, Ergon organizes its endpoints into a logical hierarchy:

### HTTP API

REST API endpoints follow this structure:
```
http://host:port/api/{resource}/{id}
```

Examples:
- `http://localhost:8002/api/agents` - Agent collection endpoint
- `http://localhost:8002/api/agents/1` - Specific agent endpoint
- `http://localhost:8002/api/docs/search` - Documentation search endpoint

### WebSocket API

WebSocket connections use this structure:
```
ws://host:port/ws
```

With protocol selector in the initial message:
```json
{
  "protocol": "a2a|mcp",
  "type": "message|event|command"
}
```

### Server-Sent Events

Event streams follow this structure:
```
http://host:port/api/stream/{stream_type}
```

Examples:
- `http://localhost:8002/api/stream/agent/1` - Stream agent execution
- `http://localhost:8002/api/terminal/stream` - Stream terminal responses

## Protocol Routing

Ergon uses protocol-based routing to handle different types of requests through the same port:

### Protocol Detection

The system detects the appropriate protocol based on:
1. URL path (`/api/`, `/ws/`, etc.)
2. HTTP headers (Accept, Content-Type)
3. Message content for WebSockets (protocol field)

### Protocol Handlers

Different protocol handlers process requests based on their type:
- FastAPI router for HTTP requests
- WebSocket handlers for real-time communication
- SSE handlers for event streaming

## Integration with Other Components

### Hermes Integration

Ergon registers with Hermes using the Single Port Architecture pattern:

```python
await register_with_hermes(
    service_id="ergon",
    name="Ergon Agent Framework",
    capabilities=["agent_creation", "agent_execution", "mcp", "a2a"],
    metadata={
        "port": 8002,
        "url_prefix": "/api",
        "ws_endpoint": "/ws",
        "ui_enabled": True
    }
)
```

### Client Configuration

Ergon's client libraries automatically detect and use the Single Port Architecture:

```python
from ergon.utils.tekton_integration import get_component_port, configure_for_single_port

# Get port configuration
port_config = configure_for_single_port()

# Use in client initialization
client = ErgonClient(host="localhost", port=port_config["port"])
```

### UI Integration

Ergon's UI components use environment-based configuration for connection:

```javascript
// In UI component
import { getComponentConfig } from './env.js';

const config = getComponentConfig('ergon');
const apiUrl = `http://${config.host}:${config.port}/api`;
const wsUrl = `ws://${config.host}:${config.port}/ws`;
```

## Implementation Details

### Single Port Configuration

The Single Port Architecture is implemented in `ergon/utils/tekton_integration.py`:

```python
def configure_for_single_port():
    """Configure component for Single Port Architecture."""
    port = int(os.environ.get("ERGON_PORT", "8002"))
    host = os.environ.get("ERGON_HOST", "localhost")
    
    return {
        "port": port,
        "host": host,
        "base_url": f"http://{host}:{port}",
        "ws_url": f"ws://{host}:{port}/ws"
    }
```

### FastAPI Configuration

The FastAPI application is configured to support the Single Port Architecture in `ergon/api/app.py`:

```python
# Get port configuration
port_config = configure_for_single_port()
logger.info(f"Ergon API configured with port {port_config['port']}")

# Create FastAPI app with appropriate path structure
app = FastAPI(
    title="Ergon API",
    description="REST API for the Ergon CI agent builder and A2A/MCP services",
    version="0.1.0"
)

# Include routers for different protocols
app.include_router(api_router, prefix="/api")
app.include_router(a2a_router, prefix="/api/a2a")
app.include_router(mcp_router, prefix="/api/mcp")
```

### WebSocket Endpoint

The WebSocket endpoint supports multiple protocols:

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for A2A and MCP communication."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process message based on its protocol
            if "protocol" in message:
                if message["protocol"] == "a2a":
                    # Handle A2A message
                    await handle_a2a_message(message, websocket)
                elif message["protocol"] == "mcp":
                    # Handle MCP message
                    await handle_mcp_message(message, websocket)
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Unknown protocol: {message.get('protocol')}"
                    }))
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Missing protocol field"
                }))
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()
```

## Client Usage

### JavaScript Client

```javascript
// Initialize client with Single Port Architecture
const ergonClient = new ErgonClient({
    baseUrl: 'http://localhost:8002/api',
    wsUrl: 'ws://localhost:8002/ws'
});

// HTTP API request
const agents = await ergonClient.listAgents();

// WebSocket connection
ergonClient.connectWebSocket({
    protocol: 'a2a',
    onMessage: (message) => {
        console.log('Received:', message);
    }
});

// Send A2A message
ergonClient.sendA2AMessage({
    recipient: 'agent_2',
    content: 'Hello from JavaScript client'
});
```

### Python Client

```python
from ergon.client import ErgonClient

# Initialize client with Single Port Architecture
client = ErgonClient(host="localhost", port=8002)

# HTTP API request
agents = await client.list_agents()

# WebSocket connection
async def on_message(message):
    print(f"Received: {message}")

await client.connect_websocket(protocol="a2a", on_message=on_message)

# Send A2A message
await client.send_a2a_message(
    recipient="agent_2",
    content="Hello from Python client"
)
```

## Upgrading from Previous Versions

If you're upgrading from a version of Ergon that used multiple ports, follow these steps:

1. Update environment variables:
   ```
   # Old (multiple ports)
   ERGON_API_PORT=8002
   ERGON_WS_PORT=8003
   
   # New (single port)
   ERGON_PORT=8002
   ```

2. Update client code:
   ```python
   # Old
   client = ErgonClient(
       api_url=f"http://localhost:{api_port}/",
       ws_url=f"ws://localhost:{ws_port}/"
   )
   
   # New
   client = ErgonClient(host="localhost", port=8002)
   ```

3. Update WebSocket connections:
   ```javascript
   // Old
   const ws = new WebSocket(`ws://localhost:${wsPort}/`);
   
   // New
   const ws = new WebSocket(`ws://localhost:${port}/ws`);
   ```

## Testing

To verify Ergon's compatibility with the Single Port Architecture:

1. Test HTTP endpoints:
   ```bash
   curl http://localhost:8002/api/agents
   ```

2. Test WebSocket connection:
   ```bash
   websocat ws://localhost:8002/ws
   ```
   Then send a JSON message with protocol field:
   ```json
   {"protocol": "a2a", "type": "ping"}
   ```

3. Test Server-Sent Events:
   ```bash
   curl -H "Accept: text/event-stream" http://localhost:8002/api/terminal/stream
   ```

## Troubleshooting

Common issues with Single Port Architecture integration:

### Connection Refused

If you get "Connection refused" errors:
- Verify Ergon is running on the expected port
- Check firewall settings allowing traffic to port 8002
- Ensure no other service is using port 8002

### Protocol Error

If you get protocol-related errors:
- Verify the WebSocket URL includes the `/ws` path
- Check that WebSocket messages include the `protocol` field
- Use the correct protocol identifier ("a2a" or "mcp")

### Path Not Found

If you get "Not Found" errors:
- Verify you're using the correct path structure (`/api/resource`)
- Check that the API is running and accessible
- Ensure you're using the correct HTTP method (GET, POST, etc.)