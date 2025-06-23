# Service URL Construction Guide

## Overview

Tekton uses dynamic service discovery through Hermes to avoid hardcoded URLs. This guide explains the proper way to construct service URLs throughout the Tekton codebase.

## The Problem

Currently, the Tekton codebase contains over 700 hardcoded localhost references and numerous fake environment variables that default to localhost. This approach:
- Prevents deployment flexibility (Docker, Kubernetes, distributed systems)
- Creates maintenance overhead
- Leads to inconsistent patterns across components

## The Solution: GlobalConfig Service Discovery

### ❌ DON'T DO THIS

```python
# Hardcoded URLs
rhetor_url = "http://localhost:8003"
hermes_api = "http://localhost:8001/api"

# Fake environment variables that don't exist
budget_url = os.environ.get("BUDGET_URL", "http://localhost:8013")  # BUDGET_URL is never defined!
rhetor_url = os.environ.get("RHETOR_URL", "http://localhost:8003")  # Just defaults to localhost

# Manual URL construction
engram_url = f"http://localhost:{engram_port}"
```

### ✅ DO THIS

```python
from shared.utils.global_config import GlobalConfig

config = GlobalConfig.get_instance()

# Get base service URL dynamically
rhetor_url = config.get_service_url("rhetor")  # Returns "http://localhost:8003" or actual deployment URL

# Construct specific endpoints
rhetor_api = f"{config.get_service_url('rhetor')}/api"
rhetor_chat = f"{config.get_service_url('rhetor')}/api/chat"
hermes_a2a = f"{config.get_service_url('hermes')}/api/a2a"
engram_memory = f"{config.get_service_url('engram')}/api/memories"
```

## How It Works

1. **Service Registration**: When a component starts, it registers with Hermes, providing its actual endpoint URL
2. **Service Discovery**: GlobalConfig queries Hermes once at startup to get all registered service URLs
3. **Runtime Resolution**: Components call `get_service_url()` to get the correct URL for any service
4. **Automatic Fallback**: If Hermes is unavailable, falls back to localhost defaults

## Common URL Construction Patterns

### Basic API Endpoints

```python
# Get the base URL and append your API path
base_url = config.get_service_url("component_name")
api_url = f"{base_url}/api"
specific_endpoint = f"{base_url}/api/v1/resource"
```

### WebSocket Endpoints

```python
# Convert HTTP URL to WebSocket URL
http_url = config.get_service_url("component_name")
ws_url = http_url.replace('http://', 'ws://').replace('https://', 'wss://')
ws_endpoint = f"{ws_url}/ws"

# Example for Rhetor WebSocket
rhetor_ws = f"{config.get_service_url('rhetor').replace('http://', 'ws://')}/ws"
```

### Health Check Endpoints

```python
# Standard health check pattern
health_url = f"{config.get_service_url('component_name')}/health"
```

### MCP Endpoints

```python
# Model Context Protocol endpoints
mcp_tools = f"{config.get_service_url('component_name')}/api/mcp/v2/tools"
mcp_execute = f"{config.get_service_url('component_name')}/api/mcp/v2/execute"
```

## Component Examples

### Rhetor Client

```python
class RhetorClient:
    def __init__(self):
        config = GlobalConfig.get_instance()
        self.base_url = config.get_service_url("rhetor")
        self.api_url = f"{self.base_url}/api"
        self.ws_url = self.base_url.replace('http://', 'ws://') + '/ws'
```

### Inter-Component Communication

```python
# Prometheus needs to call Rhetor
async def call_rhetor_llm(self, prompt: str):
    config = GlobalConfig.get_instance()
    rhetor_chat_url = f"{config.get_service_url('rhetor')}/api/chat"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(rhetor_chat_url, json={"prompt": prompt}) as response:
            return await response.json()
```

## Benefits

1. **Deployment Flexibility**: Components can run anywhere - localhost, Docker containers, Kubernetes pods
2. **No Configuration Required**: Services discover each other automatically through Hermes
3. **Single Source of Truth**: All service locations managed by Hermes
4. **Backward Compatible**: Falls back to localhost if Hermes is unavailable
5. **Clean Codebase**: No more scattered localhost references or fake environment variables

## Migration Guide

When updating existing code:

1. **Identify hardcoded URLs**:
   ```bash
   grep -r "http://localhost:" --include="*.py" .
   ```

2. **Replace with GlobalConfig**:
   ```python
   # Before
   hermes_url = "http://localhost:8001"
   
   # After
   config = GlobalConfig.get_instance()
   hermes_url = config.get_service_url("hermes")
   ```

3. **Remove fake environment variables**:
   ```python
   # Before
   url = os.environ.get("FAKE_SERVICE_URL", "http://localhost:8000")
   
   # After
   config = GlobalConfig.get_instance()
   url = config.get_service_url("service_name")
   ```

4. **Test locally** to ensure fallback works

## Note on Test/Example Files

Test files and example scripts may continue to use localhost URLs where appropriate. The service discovery pattern is primarily for production component code.

## Future Considerations

This pattern sets up Tekton for:
- Multi-environment deployments
- Service mesh integration
- Load balancing (multiple instances of a service)
- Blue-green deployments
- Containerized and cloud-native architectures

By following this pattern, we ensure Tekton components can communicate regardless of deployment topology.