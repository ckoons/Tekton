# Port Standardization Implementation Guide

This guide provides a step-by-step process for implementing the Single Port Architecture pattern in Tekton components.

## Overview

The Single Port Architecture requires each component to:
1. Use a single port for all operations (HTTP, WebSocket, Events)
2. Use standardized environment variables for port configuration
3. Use path-based routing for different operations
4. Provide consistent health check endpoints

## Implementation Steps

### 1. Create Port Configuration Utility

For each component, create a `port_config.py` module in the component's utils directory:

```python
# Example: /path/to/component/utils/port_config.py

import os
import logging

logger = logging.getLogger(__name__)

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

# Helper functions
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

def get_COMPONENT_port():
    """Get the port for this component."""
    return get_component_port("COMPONENT")

# URL construction utilities
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

### 2. Update Server Initialization

Replace direct port configuration in the component's server initialization code:

```python
# Before
port = int(os.environ.get("COMPONENT_PORT", "8XXX"))

# After
from ..utils.port_config import get_component_port
port = get_component_port("component_name")
```

For async server functions:

```python
async def start_server(host="0.0.0.0", port=None, **kwargs):
    """Start the server."""
    # Use standardized port configuration
    from ..utils.port_config import get_component_port
    if port is None:
        port = get_component_port("component_name")
        
    # Rest of server initialization
    # ...
```

### 3. Update URL Construction

Replace hard-coded URLs with the URL construction utilities:

```python
# Before
hermes_url = os.environ.get("HERMES_URL", "http://localhost:8001")

# After
from ..utils.port_config import get_api_url
hermes_url = get_api_url("hermes")
```

For WebSocket URLs:

```python
# Before
ws_url = f"ws://localhost:{port}/ws"

# After
from ..utils.port_config import get_ws_url
ws_url = get_ws_url("component_name")
```

### 4. Implement Path-Based Routing

Ensure the component uses path-based routing for different operations:

```python
# FastAPI example
app = FastAPI()

# HTTP API endpoints
app.include_router(api_router, prefix="/api")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # WebSocket handling
    pass

# Health check endpoint
@app.get("/health")
async def health_check():
    # Health check implementation
    pass
```

### 5. Testing

Test the component to verify it's using the correct port:

```bash
# 1. Stop all Tekton components
/path/to/tekton-kill

# 2. Start the component
/path/to/tekton-launch --components component_name --no-ui --non-interactive

# 3. Check if the component is responding on the correct port
curl -s http://localhost:XXXX/health

# 4. Test with multiple components to ensure no port conflicts
/path/to/tekton-launch --components component1,component2 --no-ui --non-interactive
```

## Common Issues & Solutions

### Issue: Port Already in Use

If the port is already in use:

1. Check if another component is running on the same port:
   ```bash
   lsof -i :XXXX
   ```

2. Stop all Tekton components:
   ```bash
   /path/to/tekton-kill
   ```

3. Check for lingering processes:
   ```bash
   ps -ef | grep component_name
   ```

### Issue: Component Not Using Standard Port

If a component is not using its standard port:

1. Check environment variables:
   ```bash
   env | grep PORT
   ```

2. Verify the port configuration utility is being used correctly.

3. Check for hard-coded port values in server initialization code.

## Conclusion

By following this standardized approach to port configuration, we ensure all Tekton components use their designated ports consistently, making the system more reliable and maintainable.