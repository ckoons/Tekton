# Tekton Single Port Architecture

## Overview

The Tekton Single Port Architecture is a design pattern that simplifies component communication by using a single port for all operations (HTTP, WebSocket, and Events) via path-based routing. This documentation explains the implementation and benefits of this architecture.

## Port Assignments

Each Tekton component now has a dedicated port for all its operations:

| Component | Port | Environment Variable | Description |
|-----------|------|----------------------|-------------|
| Hephaestus UI | 8080 | HEPHAESTUS_PORT | UI system (standard web UI port) |
| Engram | 8000 | ENGRAM_PORT | Memory system |
| Hermes | 8001 | HERMES_PORT | Service registry & database |
| Ergon | 8002 | ERGON_PORT | Agent system |
| Rhetor | 8003 | RHETOR_PORT | LLM management |
| Terma | 8004 | TERMA_PORT | Terminal system |
| Athena | 8005 | ATHENA_PORT | Knowledge graph |
| Prometheus | 8006 | PROMETHEUS_PORT | Planning system |
| Harmonia | 8007 | HARMONIA_PORT | Workflow system |
| Telos | 8008 | TELOS_PORT | Requirements system |
| Synthesis | 8009 | SYNTHESIS_PORT | Execution engine |
| Tekton Core | 8010 | TEKTON_CORE_PORT | Core orchestration |

## Implementation Details

### 1. Environment Variables

All port values are configured through environment variables, which are set in the `tekton-launch` script and used consistently across all components. For example:

```bash
export HEPHAESTUS_PORT=8080
export ENGRAM_PORT=8000
export HERMES_PORT=8001
# ...etc.
```

### 2. Path-Based Routing

Each component uses path-based routing to direct different types of requests:
- HTTP API: `/api/...`
- WebSocket: `/ws`
- Events: `/events`
- Health Checks: `/health`

Example: 
```
http://localhost:8003/api/message   # HTTP API endpoint on Rhetor
ws://localhost:8003/ws              # WebSocket endpoint on Rhetor
http://localhost:8003/health        # Health check endpoint on Rhetor
```

### 3. Client-Side Implementation

The frontend uses a configuration system to access component ports:

1. **Environment Variables**: Client-side environment variables provide port values:
   ```javascript
   window.HEPHAESTUS_PORT = 8080;
   window.RHETOR_PORT = 8003;
   // ...etc.
   ```

2. **Server Configuration Endpoint**: The UI server provides current port values:
   ```
   GET /api/config/ports
   ```

3. **Dynamic URL Construction**: Components build URLs using these variables:
   ```javascript
   const wsUrl = `ws://localhost:${window.RHETOR_PORT}/ws`;
   ```

### 4. Server-Side Implementation

Each service has been updated to:

1. Use a single port for all operations
2. Read port values from environment variables
3. Implement path-based routing for different protocols
4. Support WebSocket connections on the same port as HTTP

### 5. Standardized Utilities

To complement the Single Port Architecture, Tekton now provides standardized utilities for component communication and configuration:

1. **HTTP Client Utility**: Standardized HTTP request handling with consistent error handling, timeouts, and retries.
   ```python
   from tekton.utils.tekton_http import create_hermes_client
   
   hermes_client = create_hermes_client()
   components = await hermes_client.get("/api/components")
   ```

2. **Configuration Management**: Unified configuration loading from environment variables, files, and defaults.
   ```python
   from tekton.utils.tekton_config import get_component_port
   
   port = get_component_port("hermes")  # Automatically uses HERMES_PORT env var
   ```

3. **WebSocket Management**: Standardized WebSocket client and server with connection management and error handling.
   ```python
   from tekton.utils.tekton_websocket import get_component_websocket_url
   
   ws_url = get_component_websocket_url("rhetor")  # ws://localhost:8003/ws
   ```

For more information on these utilities, see the [Shared Utilities](../DeveloperGuides/SharedUtilities.md) documentation.

## Benefits

1. **Simplified Configuration**: Only one port per component to configure and remember
2. **Easier Firewall Management**: Fewer ports to manage and expose
3. **Consistent Pattern**: All components follow the same model
4. **Better Environment Variable Management**: Clean naming scheme for ports
5. **Enhanced Documentation**: Clear port assignments make integration easier
6. **Standardized Utilities**: Shared code for HTTP, WebSocket, and configuration management
7. **Consistent Error Handling**: Standardized error handling across all components
8. **Simplified Component Creation**: Boilerplate code is reduced through shared utilities

## Migrating to Single Port Architecture

When updating existing components to use the Single Port Architecture:

1. Update environment variable usage to read from the new port variables
2. Modify WebSocket server initialization to use the same port as HTTP
3. Implement path-based routing for different types of requests
4. Update client-side code to construct URLs using the environment variables
5. Adopt the shared utilities for HTTP, WebSocket, and configuration management:
   ```python
   # Before
   port = int(os.environ.get("CUSTOM_PORT", 8000))
   
   # After
   from tekton.utils.tekton_config import get_component_port
   port = get_component_port("mycomponent")
   ```

## Testing Single Port Components

To verify that a component correctly implements the Single Port Architecture:

1. Launch the component using the standard environment variable
2. Test HTTP API access on the component's port with `/api/...` endpoints
3. Test WebSocket connections on the same port with the `/ws` path
4. Test health check endpoint at `/health`
5. Verify that the component reads the port from the correct environment variable
6. Ensure the component correctly uses the standardized utilities

## Standard URL Patterns

The Single Port Architecture defines standard URL patterns for all components:

| Path Pattern | Protocol | Purpose |
|--------------|----------|---------|
| `/api/...` | HTTP | REST API endpoints |
| `/api/v1/...` | HTTP | Versioned REST API |
| `/ws` | WebSocket | Main WebSocket endpoint |
| `/ws/events` | WebSocket | Event-specific WebSocket |
| `/events` | HTTP | Server-sent events endpoint |
| `/health` | HTTP | Health check endpoint |
| `/metrics` | HTTP | Metrics endpoint (for monitoring) |

## Health Check Implementation

All components now implement a standard health check endpoint:

```python
@app.get("/health")
async def health_check():
    # Get component health status
    health_info = await component.health_check()
    
    # Set HTTP status code based on health
    status_code = 200
    if health_info["status"] == "error":
        status_code = 500
    elif health_info["status"] == "degraded":
        status_code = 429
    
    return JSONResponse(
        content=health_info,
        status_code=status_code
    )
```

## Future Enhancements

Future enhancements to the Single Port Architecture may include:

1. Automatic port conflict detection and resolution
2. Component-specific path prefixes for better routing (e.g., `/rhetor/api/...`)
3. Enhanced logging of port usage and connections
4. Service discovery integration for dynamic port allocation
5. Load balancing and failover support
6. Metrics collection and reporting for all endpoints

## See Also

- [Component Integration Patterns](./ComponentIntegrationPatterns.md)
- [Shared Utilities](../DeveloperGuides/SharedUtilities.md)
- [Component Implementation Plan](../DeveloperGuides/ComponentImplementationPlan.md)