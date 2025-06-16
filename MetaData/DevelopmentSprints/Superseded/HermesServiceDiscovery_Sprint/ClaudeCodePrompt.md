# Claude Code Prompt - Hermes Service Discovery Implementation

You are tasked with implementing the Hermes Service Discovery system for Tekton. This sprint builds upon the completed GlobalConfig sprint to enable dynamic service discovery, replacing hardcoded localhost URLs throughout the codebase.

## Context

Tekton currently has all components using hardcoded localhost URLs when connecting to other services. This prevents deployment in containerized environments (Docker, Kubernetes) where services have different hostnames. Hermes already acts as the service registry but doesn't provide discovery endpoints.

## Your Task

Implement service discovery in Hermes and update GlobalConfig to use it for dynamic URL resolution.

## Prerequisites

1. The GlobalConfig sprint is complete - all components use GlobalConfig for configuration
2. Components are registered with Hermes and send heartbeats
3. The codebase uses `global_config.get_service_url()` which currently returns hardcoded localhost

## Implementation Requirements

### Phase 1: Hermes Service Discovery API

1. **Add environment detection** (`hermes/core/environment.py`):
   - Detect if running in local, Docker, or Kubernetes
   - Check TEKTON_DEPLOYMENT_ENV first, then auto-detect
   - Return appropriate hostname patterns

2. **Create service models** (`hermes/models/service.py`):
   - ServiceEndpoint with host, port, health, metadata
   - ServiceDiscoveryResponse with selected URL and TTL

3. **Implement discovery endpoints** (`hermes/api/discovery_endpoints.py`):
   - GET /api/v1/services - list all services
   - GET /api/v1/services/{name}/url - get service URL
   - GET /api/v1/services/{name}/endpoints - get all endpoints
   - Only return healthy services by default

### Phase 2: GlobalConfig Integration

1. **Update GlobalConfig** (`shared/utils/global_config.py`):
   - Add `get_service_url_async()` method
   - Query Hermes for service URLs
   - Implement caching with 5-minute TTL
   - Keep sync wrapper for compatibility
   - Add fallback chain (cache → Hermes → localhost)

2. **Create discovery client** (`shared/utils/hermes_discovery_client.py`):
   - Async HTTP client for Hermes
   - Handle timeouts and errors gracefully
   - Connection pooling for performance

3. **Implement caching** (`shared/utils/discovery_cache.py`):
   - TTL-based cache with async operations
   - Thread-safe for concurrent access
   - Invalidation support

### Phase 3: Component Migration

1. Update components to use async discovery where possible
2. Remove all hardcoded "localhost" strings
3. Ensure proper error handling
4. Test fallback behavior

## Important Considerations

1. **Backward Compatibility**: The system must work even if Hermes is unavailable
2. **Performance**: Cache hits should be <1ms, Hermes queries <50ms
3. **Error Handling**: Never let discovery failures crash components
4. **Testing**: Test in local and Docker environments

## Code Patterns

### Environment Detection Example
```python
def detect_environment() -> str:
    # Explicit override
    if env := os.environ.get("TEKTON_DEPLOYMENT_ENV"):
        return env
    
    # Kubernetes detection
    if os.environ.get("KUBERNETES_SERVICE_HOST"):
        return "kubernetes"
    
    # Docker detection
    if os.path.exists("/.dockerenv"):
        return "docker"
    
    return "local"
```

### URL Construction Example
```python
def construct_service_url(service_name: str, port: int, environment: str) -> str:
    if environment == "kubernetes":
        return f"http://{service_name}.tekton.svc.cluster.local:{port}"
    elif environment == "docker":
        return f"http://{service_name}:{port}"
    else:
        return f"http://localhost:{port}"
```

### Caching Example
```python
async def get_service_url_async(self, component_name: str) -> str:
    # Check cache first
    if cached := await self._cache.get(component_name):
        return cached
    
    try:
        # Query Hermes
        url = await self._discovery_client.get_service_url(component_name)
        await self._cache.set(component_name, url, ttl=300)
        return url
    except Exception as e:
        logger.warning(f"Discovery failed: {e}, using fallback")
        # Fallback to constructed URL
        return self._construct_fallback_url(component_name)
```

## Testing Strategy

1. Start with Hermes and one other component
2. Verify discovery returns correct URLs
3. Test cache behavior
4. Test fallback when Hermes is down
5. Test in Docker environment

## Success Criteria

- All components can discover each other via Hermes
- No hardcoded localhost URLs remain
- System works in Docker containers
- Fallback ensures reliability
- Performance meets targets

Begin with implementing the Hermes discovery endpoints, then move to GlobalConfig integration.