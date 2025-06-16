# Engram Provenance Integration Strategy

## Addressing Middle-Child's Integration Concerns

### 1. Namespace Collision Solution

**Problem**: Original memories use namespaces like `shared`, `thoughts`, etc. Provenance metadata shouldn't pollute these.

**Solution**: Create a dedicated `_provenance` namespace
```python
PROVENANCE_NAMESPACE = "_provenance"  # Hidden namespace
STANDARD_NAMESPACES = ["conversations", "thinking", "longterm", "projects", "compartments", "session"]
# Provenance stored separately, linked by memory_id
```

**Implementation**:
- Store provenance in dedicated namespace with key pattern: `prov:{memory_id}`
- Keep original memory untouched in its namespace
- Link via memory_id for lookups

### 2. Performance Optimization

**Problem**: Tracking history could make simple operations heavyweight.

**Solution**: Lazy loading + opt-in tracking
```python
class MemoryService:
    async def store(self, key, value, namespace, track_provenance=None):
        # Default: track_provenance = True for important namespaces only
        if track_provenance is None:
            track_provenance = namespace in ["shared", "longterm"]
        
        # Fast path for non-tracked memories
        if not track_provenance:
            return await self._store_direct(key, value, namespace)
            
        # Provenance tracked asynchronously
        memory_id = await self._store_direct(key, value, namespace)
        asyncio.create_task(self._track_provenance(memory_id, "created"))
        return memory_id
```

**Key Optimizations**:
- Provenance writes are async/fire-and-forget
- Only track for important namespaces by default
- `w("simple")` remains fast - provenance loaded only if requested

### 3. Storage Backend Compatibility

**Problem**: Works with both file storage AND vector storage.

**Solution**: Adapter pattern
```python
class ProvenanceStorageAdapter:
    def __init__(self, backend):
        self.backend = backend
        
    async def store_provenance(self, memory_id, provenance_data):
        if hasattr(self.backend, 'vector_store'):
            # Vector DB: Store as metadata
            return await self._store_vector_provenance(memory_id, provenance_data)
        else:
            # File storage: Store as .prov file
            return await self._store_file_provenance(memory_id, provenance_data)
```

### 4. Atomic Operations

**Problem**: Forking/merging must be consistent.

**Solution**: Transaction-like operations with rollback
```python
class AtomicMemoryOperation:
    def __init__(self, memory_service):
        self.memory_service = memory_service
        self.operations = []
        
    async def fork_memory(self, memory_id, branch_name):
        checkpoint = await self._create_checkpoint(memory_id)
        try:
            # 1. Copy memory to new branch
            # 2. Update provenance
            # 3. Create branch record
            await self._execute_fork(memory_id, branch_name)
            self.operations.append(('fork', memory_id, branch_name))
        except Exception as e:
            await self._rollback_to_checkpoint(checkpoint)
            raise
```

## Implementation Priority

1. **Phase 1**: Namespace isolation (no collision)
2. **Phase 2**: Performance optimization (lazy loading)
3. **Phase 3**: Storage adapter (backend compatibility)
4. **Phase 4**: Atomic operations (consistency)

## Questions for Casey

1. Should provenance tracking be opt-in or opt-out by default?
2. What's the acceptable performance overhead? (e.g., 10ms per operation?)
3. Should we version the provenance schema for future changes?
4. How long should provenance history be retained? Forever or time-based?