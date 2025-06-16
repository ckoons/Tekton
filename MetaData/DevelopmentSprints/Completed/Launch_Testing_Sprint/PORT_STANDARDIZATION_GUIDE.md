# Port Standardization Guide

This guide documents the implementation of the Single Port Architecture pattern across Tekton components. It provides an overview of the approach, implementation details, and steps for developers to follow when adding port configuration to new or existing components.

## Standard Port Assignments

| Component      | Port | Environment Variable   | Purpose                                 |
|----------------|------|------------------------|----------------------------------------|
| Hephaestus UI  | 8080 | `HEPHAESTUS_PORT`      | UI system (using standard web port)     |
| Engram         | 8000 | `ENGRAM_PORT`          | Memory system                           |
| Hermes         | 8001 | `HERMES_PORT`          | Service registry & messaging            |
| Ergon          | 8002 | `ERGON_PORT`           | Agent system                            |
| Rhetor         | 8003 | `RHETOR_PORT`          | LLM management                          |
| Terma          | 8004 | `TERMA_PORT`           | Terminal system                         |
| Athena         | 8005 | `ATHENA_PORT`          | Knowledge graph                         |
| Prometheus     | 8006 | `PROMETHEUS_PORT`      | Planning system                         |
| Harmonia       | 8007 | `HARMONIA_PORT`        | Workflow system                         |
| Telos          | 8008 | `TELOS_PORT`           | Requirements system                     |
| Synthesis      | 8009 | `SYNTHESIS_PORT`       | Execution engine                        |
| Tekton Core    | 8010 | `TEKTON_CORE_PORT`     | Core orchestration                      |

## Legacy/Special Ports

| Service        | Port | Environment Variable   | Purpose                              |
|----------------|------|------------------------|--------------------------------------|
| LLM Adapter    | 8300 | `LLM_ADAPTER_HTTP_PORT`| LLM Adapter HTTP API (legacy)        |
| Terma WS       | 8767 | `TERMA_WS_PORT`        | WebSocket for Terma (legacy)         |

## Implementation Approach

### 1. Port Configuration Utility

Each component should have a `port_config.py` utility module in its `utils` directory that provides standardized port configuration. This module should contain:

```python
# Standard port assignments
PORT_ASSIGNMENTS = {
    "hephaestus": 8080,
    "engram": 8000,
    "hermes": 8001,
    "ergon": 8002,
    "rhetor": 8003,
    "terma": 8004,
    "athena": 8005,
    "prometheus": 8006,
    "harmonia": 8007,
    "telos": 8008,
    "synthesis": 8009,
    "tekton_core": 8010,
    "llm_adapter": 8300,
}

# Environment variable names
ENV_VAR_NAMES = {
    "hephaestus": "HEPHAESTUS_PORT",
    "engram": "ENGRAM_PORT",
    "hermes": "HERMES_PORT",
    "ergon": "ERGON_PORT",
    "rhetor": "RHETOR_PORT",
    "terma": "TERMA_PORT",
    "athena": "ATHENA_PORT",
    "prometheus": "PROMETHEUS_PORT",
    "harmonia": "HARMONIA_PORT",
    "telos": "TELOS_PORT",
    "synthesis": "SYNTHESIS_PORT", 
    "tekton_core": "TEKTON_CORE_PORT",
    "llm_adapter": "LLM_ADAPTER_HTTP_PORT",
}

# Core function to get a component's port
def get_component_port(component_id):
    """Get the port for a specific component."""
    if component_id not in ENV_VAR_NAMES:
        logger.warning(f"Unknown component ID: {component_id}, using default port 8000")
        return 8000
        
    env_var = ENV_VAR_NAMES[component_id]
    default_port = PORT_ASSIGNMENTS[component_id]
    
    try:
        return int(os.environ.get(env_var, default_port))
    except (ValueError, TypeError):
        logger.warning(f"Invalid port value in {env_var}, using default: {default_port}")
        return default_port

# Component-specific helper
def get_component_specific_port():
    """Get the port for this specific component."""
    return get_component_port("component_id")
```

### 2. URL Construction Utilities

The `port_config.py` module should also contain utilities for constructing URLs for component communication:

```python
def get_component_url(component_id, protocol="http", path=""):
    """Get the full URL for a component endpoint."""
    host = os.environ.get(f"{component_id.upper()}_HOST", "localhost")
    port = get_component_port(component_id)
    
    if not path.startswith("/") and path:
        path = f"/{path}"
        
    return f"{protocol}://{host}:{port}{path}"

def get_api_url(component_id, path=""):
    """Get the API URL for a component."""
    api_path = f"/api{path}" if path else "/api"
    return get_component_url(component_id, protocol="http", path=api_path)

def get_ws_url(component_id, path=""):
    """Get the WebSocket URL for a component."""
    ws_path = f"/ws{path}" if path else "/ws"
    return get_component_url(component_id, protocol="ws", path=ws_path)
```

### 3. Path-Based Routing

Components should use path-based routing for different types of endpoints:

- HTTP API: `/api/...`
- WebSocket: `/ws/...`
- Events: `/events/...`
- Health check: `/health`

Example FastAPI implementation:

```python
app = FastAPI()

# HTTP API
app.include_router(api_router, prefix="/api")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # WebSocket handling
    pass

# Health check
@app.get("/health")
async def health_check():
    # Health check implementation
    return {"status": "healthy"}
```

## Implementation Examples

### Rhetor Example

The Rhetor component has been updated to use the standardized port configuration:

```python
# In rhetor/__main__.py
from rhetor.utils.port_config import get_rhetor_port

def main():
    parser = argparse.ArgumentParser(description="Rhetor LLM Manager")
    parser.add_argument(
        "--port", "-p", 
        type=int, 
        default=get_rhetor_port(),
        help="Port to run the server on (default: 8003)"
    )
    # ...
```

```python
# In rhetor/api/app.py
async def start_server(host="0.0.0.0", port=None, log_level="info"):
    """Start the Rhetor API server."""
    # Use standardized port configuration
    from ..utils.port_config import get_rhetor_port
    if port is None:
        port = get_rhetor_port()
    # ...
```

### Synthesis Example

The Synthesis component uses standardized port configuration in its API server:

```python
# In synthesis/api/app.py
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or use default
    port = get_component_port("synthesis")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
```

The component's configuration in `synthesis.yaml` matches the standardized port assignment:

```yaml
component:
  id: "synthesis"
  name: "Synthesis"
  version: "1.0.0"
  description: "Execution and integration engine for Tekton"
  port: 8009
```

### Terma Example

The Terma component handles both a standard port and a legacy WebSocket port:

```python
# In terma/api/app.py
async def start_server(host="0.0.0.0", port=None, ws_port=None):
    """Start the FastAPI server and WebSocket server."""
    # Use standardized port configuration
    from ..utils.port_config import get_terma_port, get_terma_ws_port
    
    # Set default port using standardized configuration
    if port is None:
        port = get_terma_port()
        logger.info(f"Using standard Terma port: {port}")
    
    # Get WebSocket port from standardized configuration
    if ws_port is None:
        ws_port = get_terma_ws_port()
        logger.info(f"Using WebSocket port {ws_port}")
    # ...
```

## Migration Steps

To migrate a component to use the standardized port configuration:

1. Create a `port_config.py` utility module in the component's `utils` directory
2. Implement the standard port assignments and environment variable names
3. Add component-specific helper functions
4. Update server initialization to use the standardized port configuration
5. Replace hard-coded URLs with the URL construction utilities
6. Implement path-based routing for different endpoint types
7. Test the component to ensure it starts on the correct port

## Future Improvements

Some potential improvements for the future:

1. Extract common port configuration code into a shared library that all components can import
2. Implement automatic service discovery to make port configuration more dynamic
3. Add conflict detection and resolution when multiple components attempt to use the same port
4. Implement a component manager that can automatically assign and track ports