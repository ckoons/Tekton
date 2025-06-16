# Hermes API Usage Guide

This document provides guidance on how to properly interact with the Hermes API following the Single Port Architecture implementation.

## Hermes API Structure

Hermes follows a nested FastAPI application structure, with main endpoints available under the `/api` path. This follows the Single Port Architecture pattern by providing different types of services under different paths on the same port.

### Base URL

```
http://localhost:8001
```

### Available Endpoints

#### Root Endpoints

- `GET /` - Root endpoint (redirects to documentation)
- `GET /health` - Health check endpoint (returns status of core components)

#### API Documentation

- `/docs` - Main API documentation
- `/api/docs` - Service registry API documentation

#### Service Registry Endpoints (under `/api`)

The service registry endpoints are mounted under the `/api` path:

- `POST /api/register` - Register a component
- `POST /api/query` - Query available services
- `POST /api/heartbeat` - Send a component heartbeat
- `POST /api/unregister` - Unregister a component

#### Other API Namespaces

- `/api/a2a/*` - Agent-to-Agent communication endpoints
- `/api/database/*` - Database access endpoints
- `/api/llm/*` - LLM integration endpoints
- `/api/mcp/*` - Multimodal Cognitive Protocol endpoints

## Using the Service Registry

### Register a Component

```bash
curl -X POST http://localhost:8001/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Component",
    "version": "0.1.0", 
    "type": "service",
    "endpoint": "http://localhost:8005",
    "capabilities": ["feature1", "feature2"],
    "metadata": {
      "description": "My awesome component"
    }
  }'
```

### Query Available Services

```bash
# Query all services
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{}'

# Query by capability
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "feature1"
  }'

# Query healthy services only
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "healthy_only": true
  }'
```

### Send a Heartbeat

```bash
curl -X POST http://localhost:8001/api/heartbeat \
  -H "Content-Type: application/json" \
  -H "X-Authentication-Token: your_token_here" \
  -d '{
    "component_id": "your_component_id",
    "status": {
      "healthy": true,
      "message": "Component is running normally"
    }
  }'
```

### Unregister a Component

```bash
curl -X POST http://localhost:8001/api/unregister \
  -H "X-Authentication-Token: your_token_here" \
  -d "component_id=your_component_id"
```

## Important Notes

1. **Endpoint Path Structure**: Remember to use `/api/` prefix for all service registry endpoints.

2. **Authentication**: Most endpoints (except querying) require the `X-Authentication-Token` header with the token received during registration.

3. **Component IDs**: Component IDs should be alphanumeric, possibly with underscores. Avoid using periods in component IDs as this can cause registration issues.

4. **Content-Type**: Always specify `Content-Type: application/json` for all requests that include a request body.

5. **Health Checks**: It's recommended to send heartbeats at regular intervals (e.g., every 30 seconds) to maintain "healthy" status in the service registry.

## Troubleshooting

If you're having issues with the Hermes service registry:

1. Check if Hermes is running: `curl http://localhost:8001/health`
2. Verify path structure: ensure `/api/` prefix is used for service registry endpoints
3. Check authentication: ensure token is passed correctly in the header
4. Verify component ID format: should be alphanumeric (with possible underscores)

## Client Implementation Example

Here's a simple Python client implementation:

```python
import aiohttp
import asyncio
import json

class HermesClient:
    """Client for interacting with Hermes service registry."""
    
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.component_id = None
    
    async def register(self, name, version, component_type, endpoint, capabilities=None, metadata=None):
        """Register a component with Hermes."""
        if capabilities is None:
            capabilities = []
        if metadata is None:
            metadata = {}
            
        data = {
            "name": name,
            "version": version,
            "type": component_type,
            "endpoint": endpoint,
            "capabilities": capabilities,
            "metadata": metadata
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/register", json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.token = result.get("token")
                    self.component_id = result.get("component_id")
                    return True, self.component_id, self.token
                else:
                    error = await response.text()
                    return False, None, f"Registration failed: {error}"
    
    async def query_services(self, capability=None, component_type=None, healthy_only=False):
        """Query available services."""
        data = {
            "capability": capability,
            "component_type": component_type,
            "healthy_only": healthy_only
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/query", json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    return f"Query failed: {error}"
```