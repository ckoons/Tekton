# Engram Simplification Sprint - Architectural Decisions

## Overview

This document captures the key architectural decisions made during the Engram Simplification Sprint. These decisions balance the need for radical simplification with preserving functionality that other Tekton components depend on.

## Decision 1: Single API Surface

### Decision
Consolidate all memory operations into a single `Memory` class with exactly three methods: `store()`, `recall()`, and `context()`.

### Rationale
- Current 5+ APIs cause confusion and maintenance overhead
- CI assistants need simplicity, not flexibility
- Three methods cover 100% of actual usage patterns observed

### Consequences
- **Positive**: Dramatic reduction in cognitive load
- **Positive**: Clear, obvious API usage
- **Negative**: Loss of some specialized features (acceptable)

### Implementation
```python
class Memory:
    async def store(self, content: str, **metadata) -> str
    async def recall(self, query: str, limit: int = 5) -> List[MemoryItem]
    async def context(self, query: str, limit: int = 10) -> str
```

## Decision 2: Remove Experimental Features

### Decision
Remove all experimental cognitive features including:
- Katra (memory provenance)
- Dream states
- Emotional memory
- Peer awareness
- Memory streams
- Complex context management

### Rationale
- These features are incomplete and untested
- They add significant complexity for no current benefit
- "Clever means don't touch" - Casey's wisdom

### Consequences
- **Positive**: 70% reduction in codebase size
- **Positive**: Elimination of confusing abstractions
- **Negative**: Loss of potentially interesting future features (can rebuild if needed)

## Decision 3: Silent by Default

### Decision
All logging and debug output hidden unless `ENGRAM_DEBUG=true` is set.

### Rationale
- Current implementation produces 40+ lines of output for simple operations
- CI assistants need results, not process descriptions
- Debug info should be available but not intrusive

### Consequences
- **Positive**: Clean, professional operation
- **Positive**: Easier to use in production
- **Negative**: Debugging requires explicit flag (acceptable tradeoff)

### Implementation
```python
import os
DEBUG = os.getenv('ENGRAM_DEBUG', '').lower() == 'true'

def debug_log(message: str):
    if DEBUG:
        logger.info(message)
```

## Decision 4: Preserve Storage Abstraction

### Decision
Keep the underlying storage abstraction but hide it behind the simple API. Support both file-based and vector (FAISS) backends.

### Rationale
- Storage layer actually works well
- Vector search is natural for CI assistants
- Flexibility in storage backends is valuable

### Consequences
- **Positive**: Proven storage continues to work
- **Positive**: Performance characteristics preserved
- **Negative**: Some complexity remains (hidden from users)

## Decision 5: Maintain MCP Compatibility

### Decision
Preserve MCP tool interfaces to ensure other Tekton components continue functioning.

### Rationale
- Breaking changes would cascade through entire Tekton system
- MCP tools are the primary integration point
- Can wrap new simple API with MCP-compatible interface

### Consequences
- **Positive**: No breaking changes for other components
- **Positive**: Smooth migration path
- **Negative**: Must maintain some legacy code

## Decision 6: Structured Memory as Metadata

### Decision
Fold structured memory (categories, tags, importance) into metadata parameters rather than separate API.

### Rationale
- Reduces API complexity
- Most use cases don't need structured memory
- Can still support categorization through metadata

### Implementation
```python
# Instead of separate structured memory API:
await memory.store("Important insight", 
                  category="insights",
                  tags=["ai", "consciousness"],
                  importance=0.9)
```

## Decision 7: Auto-sensible Defaults

### Decision
Provide intelligent defaults for all operations:
- Auto-generate memory IDs
- Default namespace based on context
- Automatic timestamp and source tracking
- Smart relevance scoring for recall

### Rationale
- Reduces boilerplate code
- Makes the 5-line usage example possible
- CI assistants shouldn't worry about bookkeeping

### Consequences
- **Positive**: Extremely simple to use
- **Positive**: Still flexible when needed
- **Negative**: Some loss of control (acceptable)

## Summary of Changes

### What We Keep
- Core memory storage and retrieval
- Vector-based search
- MCP tool compatibility
- Basic metadata support

### What We Remove
- Multiple API surfaces
- Experimental cognitive features
- Verbose logging
- Complex abstractions
- Incomplete functionality

### What We Add
- Single, simple Memory class
- Silent operation
- Intelligent defaults
- Clear documentation

## Migration Strategy

1. Implement new simple API alongside existing code
2. Wrap new API with MCP-compatible tools
3. Gradually migrate internal usage
4. Deprecate but don't immediately remove old APIs
5. Full removal in future sprint

## Open Questions

1. Should we support async and sync versions of methods?
   - Decision: Async only, following Tekton patterns

2. How much backward compatibility to maintain?
   - Decision: MCP tools must work, other APIs can break

3. What about multi-tenancy/compartments?
   - Decision: Support through namespace metadata, not separate API