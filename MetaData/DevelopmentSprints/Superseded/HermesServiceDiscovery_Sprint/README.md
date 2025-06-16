# Hermes Service Discovery Sprint

## Overview

This sprint implements dynamic service discovery through Hermes, replacing hardcoded localhost URLs with a centralized service registry. This will enable Tekton to support different deployment scenarios (Docker, Kubernetes, distributed) without configuration changes.

## Sprint Status

**Status**: Not Started  
**Priority**: Medium  
**Prerequisites**: GlobalConfig Sprint (must be completed first)  
**Estimated Duration**: 3-4 days  
**Architect Claude**: Planning Phase  
**Working Claude**: Not Yet Started  

## Problem Statement

Currently, Tekton components construct service URLs manually:
```python
llm_client = TektonLLMClient(base_url=f"http://localhost:{rhetor_port}")
```

This approach:
- Hardcodes "localhost" throughout the codebase
- Doesn't support containerized deployments  
- Requires code changes for different environments
- Bypasses Hermes despite it being the service registry
- Makes distributed deployments impossible
- Prevents load balancing or failover

## Sprint Goals

1. **Add service discovery to Hermes** - New endpoints to retrieve service URLs and metadata
2. **Update GlobalConfig** - Replace hardcoded localhost with dynamic Hermes queries
3. **Support multiple environments** - Automatic detection of Docker, Kubernetes, local
4. **Implement intelligent caching** - Reduce Hermes query overhead with TTL-based cache
5. **Add health-aware discovery** - Only return healthy service instances
6. **Enable fallback mechanisms** - Graceful degradation when Hermes is unavailable

## Affected Components

- **Hermes** - New service discovery endpoints
- **GlobalConfig** - Dynamic service URL resolution
- **All Tekton Components** - Updated to use service discovery

## Success Criteria

- [ ] Hermes service discovery endpoints implemented and tested
- [ ] GlobalConfig.get_service_url() uses Hermes for resolution
- [ ] Environment detection working (local/Docker/K8s)
- [ ] Caching reduces lookup latency to <5ms
- [ ] All hardcoded localhost URLs removed from codebase
- [ ] Docker deployment tested and working
- [ ] Fallback to localhost works when Hermes unavailable
- [ ] Health checks integrated with discovery
- [ ] Performance impact minimal (<10ms per lookup with cache)
- [ ] Documentation updated with deployment guides

## Technical Approach

### Phase 1: Hermes Service Discovery API

Implement new endpoints in Hermes:
- `GET /api/v1/services` - List all registered services
- `GET /api/v1/services/{name}` - Get specific service details
- `GET /api/v1/services/{name}/url` - Get service URL
- `GET /api/v1/services/{name}/endpoints` - Get all healthy endpoints
- `POST /api/v1/services/{name}/select` - Select endpoint with criteria

### Phase 2: Environment Detection

Hermes will detect deployment environment:
- Check Kubernetes environment variables
- Check Docker container indicators
- Check for orchestration metadata
- Default to local development

### Phase 3: GlobalConfig Integration

Update GlobalConfig to use Hermes:
- Async service URL resolution
- Intelligent caching with TTL
- Fallback mechanisms
- Health-aware endpoint selection

### Phase 4: Component Migration

Update all components to use discovery:
- Remove hardcoded URLs
- Use GlobalConfig.get_service_url()
- Handle async resolution
- Add retry logic

## Risk Mitigation

- **Backward compatibility** through fallback mechanisms
- **Gradual rollout** with feature flags
- **Comprehensive testing** in all environments
- **Performance monitoring** to ensure no degradation
- **Clear rollback procedures** documented