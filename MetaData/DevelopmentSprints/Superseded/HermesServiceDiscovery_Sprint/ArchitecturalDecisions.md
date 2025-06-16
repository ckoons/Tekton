# Architectural Decisions - Hermes Service Discovery

## Key Design Decisions

### 1. Service Discovery Model

**Decision**: Use a pull-based discovery model with intelligent caching.

**Rationale**:
- Components query Hermes when needed
- Reduces complexity vs push-based updates
- Cache prevents excessive queries
- Fallback ensures reliability

**Alternatives Considered**:
- Push-based model (Hermes pushes updates)
- Event-driven discovery
- Static configuration files

### 2. URL Construction Strategy

**Decision**: Hermes constructs full URLs based on environment.

**Rationale**:
- Centralized logic for URL patterns
- Components don't need environment awareness
- Supports various deployment scenarios
- Simplifies component code

**Implementation**:
```python
# Hermes determines:
# Local: http://localhost:8003
# Docker: http://rhetor:8003
# K8s: http://rhetor.tekton.svc.cluster.local:8003
```

### 3. Caching Architecture

**Decision**: Two-tier caching with TTL and invalidation.

**Rationale**:
- GlobalConfig maintains L1 cache (5-minute TTL)
- Hermes maintains L2 cache of health states
- Manual invalidation for configuration changes
- Balances performance and freshness

**Cache Structure**:
```python
{
    "rhetor": {
        "url": "http://localhost:8003",
        "cached_at": 1234567890,
        "ttl": 300,
        "health": "healthy"
    }
}
```

### 4. Environment Detection

**Decision**: Hierarchical detection with explicit overrides.

**Detection Order**:
1. TEKTON_DEPLOYMENT_ENV variable (explicit)
2. Kubernetes environment variables
3. Docker socket/cgroup detection
4. Default to local development

**Rationale**:
- Explicit control when needed
- Automatic detection for common cases
- Reliable fallback behavior

### 5. Health Integration

**Decision**: Service discovery returns only healthy endpoints by default.

**Rationale**:
- Prevents routing to unhealthy services
- Reduces error handling in components
- Option to get all endpoints if needed
- Integrates with existing health checks

### 6. Async Resolution

**Decision**: Make get_service_url() async but provide sync wrapper.

**Rationale**:
- Network calls should be async
- Some contexts require sync calls
- Gradual migration possible
- Cache makes sync calls acceptable

**Implementation**:
```python
# Async (preferred)
url = await global_config.get_service_url_async("rhetor")

# Sync wrapper (compatibility)
url = global_config.get_service_url("rhetor")  # Uses cache or blocks
```

### 7. Fallback Strategy

**Decision**: Multi-level fallback with predictable behavior.

**Fallback Order**:
1. Cached value (if fresh)
2. Query Hermes
3. Stale cache (if Hermes unavailable)
4. Construct from port configuration
5. Hardcoded localhost as last resort

**Rationale**:
- Maximum reliability
- Graceful degradation
- Components always get a URL
- Clear precedence rules

### 8. Service Metadata

**Decision**: Extend service registry with rich metadata.

**Metadata Includes**:
- Service version
- Capabilities
- Health status
- Performance metrics
- Dependencies
- API documentation URL

**Rationale**:
- Enables smart routing decisions
- Supports service versioning
- Facilitates debugging
- Powers service mesh features

## Implementation Guidelines

### Error Handling

All service discovery operations must:
- Log failures at appropriate levels
- Provide actionable error messages
- Fall back gracefully
- Never crash the component

### Performance Considerations

- Cache hits must be <1ms
- Hermes queries must be <50ms
- Background refresh for stale entries
- Connection pooling for Hermes client

### Security Considerations

- Service discovery requires authentication in production
- URLs validated before returning
- No sensitive data in cache
- Audit trail for discovery queries

## Future Enhancements

1. **Load Balancing**: Round-robin or weighted selection
2. **Circuit Breakers**: Automatic failure detection
3. **Service Mesh**: Integration with Istio/Linkerd
4. **Multi-Region**: Cross-region service discovery
5. **SRV Records**: DNS-based discovery option