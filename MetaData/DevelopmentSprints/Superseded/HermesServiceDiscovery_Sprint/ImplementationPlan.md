# Implementation Plan - Hermes Service Discovery

## Phase 1: Hermes Service Discovery API

### 1.1 Data Model Updates

**File**: `hermes/models/service.py`
```python
class ServiceEndpoint(BaseModel):
    """Extended service information for discovery"""
    name: str
    host: str
    port: int
    url: str
    environment: str  # local, docker, kubernetes
    health_status: str
    last_heartbeat: datetime
    metadata: Dict[str, Any]
    
class ServiceDiscoveryResponse(BaseModel):
    """Response for service discovery queries"""
    service_name: str
    endpoints: List[ServiceEndpoint]
    selected_url: str
    cache_ttl: int = 300
```

### 1.2 Environment Detection

**File**: `hermes/core/environment.py`
```python
class EnvironmentDetector:
    @staticmethod
    def detect_environment() -> str:
        # Check TEKTON_DEPLOYMENT_ENV
        # Check Kubernetes env vars
        # Check Docker indicators
        # Return environment type
    
    @staticmethod
    def get_hostname_pattern(environment: str) -> str:
        # Return hostname pattern for environment
```

### 1.3 Service Discovery Endpoints

**File**: `hermes/api/discovery_endpoints.py`
```python
@router.get("/api/v1/services")
async def list_services()

@router.get("/api/v1/services/{name}")
async def get_service(name: str)

@router.get("/api/v1/services/{name}/url")
async def get_service_url(name: str)

@router.get("/api/v1/services/{name}/endpoints")
async def get_service_endpoints(name: str, include_unhealthy: bool = False)

@router.post("/api/v1/services/{name}/select")
async def select_endpoint(name: str, criteria: SelectionCriteria)
```

## Phase 2: GlobalConfig Integration

### 2.1 Update GlobalConfig

**File**: `shared/utils/global_config.py`

Add new methods:
```python
async def get_service_url_async(self, component_name: str) -> str:
    """Get service URL with discovery"""
    # Check cache
    # Query Hermes if needed
    # Update cache
    # Return URL

def get_service_url(self, component_name: str) -> str:
    """Sync wrapper for compatibility"""
    # Use cache if available
    # Otherwise block on async call
    # Fallback logic
```

### 2.2 Caching Implementation

**File**: `shared/utils/discovery_cache.py`
```python
class DiscoveryCache:
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[str]
    async def set(self, key: str, value: str, ttl: int)
    async def invalidate(self, key: str)
    def is_fresh(self, entry: CacheEntry) -> bool
```

### 2.3 Hermes Client

**File**: `shared/utils/hermes_discovery_client.py`
```python
class HermesDiscoveryClient:
    async def get_service_url(self, service_name: str) -> str
    async def get_all_endpoints(self, service_name: str) -> List[ServiceEndpoint]
    async def select_endpoint(self, service_name: str, criteria: Dict) -> str
```

## Phase 3: Component Migration

### 3.1 Update Import Statements

Replace in all components:
```python
# Old
from shared.utils.env_config import get_component_config

# New  
from shared.utils.global_config import GlobalConfig
```

### 3.2 Update URL Construction

Replace in all components:
```python
# Old
rhetor_url = f"http://localhost:{rhetor_port}"

# New
rhetor_url = await global_config.get_service_url_async("rhetor")
```

### 3.3 Migration Order

1. **Low-risk components first**:
   - Prometheus (already uses GlobalConfig)
   - Metis
   - Apollo

2. **Core services**:
   - Budget
   - Athena
   - Harmonia

3. **Critical path last**:
   - Rhetor
   - Hermes (self-discovery)
   - Engram

## Phase 4: Testing Strategy

### 4.1 Unit Tests

- Environment detection tests
- Cache behavior tests
- Fallback logic tests
- URL construction tests

### 4.2 Integration Tests

- Service discovery flow
- Cache invalidation
- Health check integration
- Multi-component scenarios

### 4.3 Environment Tests

**Local Development**:
```bash
# Start all components
tekton-launch -a
# Verify discovery works
tekton-test discovery
```

**Docker Testing**:
```bash
# Build images
docker-compose build
# Start services
docker-compose up
# Run tests
docker-compose exec tester pytest
```

### 4.4 Performance Tests

- Measure cache hit latency
- Measure discovery query time
- Load test Hermes endpoints
- Monitor memory usage

## Implementation Timeline

**Day 1**:
- Morning: Hermes data model and environment detection
- Afternoon: Service discovery endpoints

**Day 2**:
- Morning: GlobalConfig integration
- Afternoon: Caching implementation

**Day 3**:
- Morning: Component migration (batch 1)
- Afternoon: Component migration (batch 2)

**Day 4**:
- Morning: Testing and debugging
- Afternoon: Documentation and cleanup

## Rollback Procedures

If issues occur:

1. **Quick rollback**: Set `TEKTON_DISCOVERY_ENABLED=false`
2. **Component rollback**: Revert individual components
3. **Cache clear**: Delete cache to force fresh lookups
4. **Full rollback**: Revert GlobalConfig changes

## Monitoring

Add metrics for:
- Discovery query count
- Cache hit rate
- Query latency
- Fallback usage
- Error rates