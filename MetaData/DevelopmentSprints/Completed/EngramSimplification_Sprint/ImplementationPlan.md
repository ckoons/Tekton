# Engram Simplification Sprint - Implementation Plan

## Overview

This document provides the detailed implementation plan for simplifying Engram. The plan is organized into specific tasks that can be executed systematically.

## Phase 1: Core Simplification (Current Phase)

### Task 1.1: Create Simple Memory API
**File**: `engram/simple.py`
- [ ] Create Memory class with store(), recall(), context() methods
- [ ] Implement debug logging wrapper
- [ ] Add intelligent defaults
- [ ] Connect to existing storage backend

### Task 1.2: Remove Experimental Features
**Files to remove/clean**:
- [ ] Remove `engram/cognitive/` directory (except what's needed)
- [ ] Remove `engram/core/provenance_*.py`
- [ ] Remove `engram/models/provenance.py`
- [ ] Remove dream, emotional, and peer awareness code
- [ ] Clean up imports and dependencies

### Task 1.3: Consolidate Storage Layer
**Files to modify**:
- [ ] Identify minimal storage interface needed
- [ ] Create single storage abstraction in `engram/storage.py`
- [ ] Remove redundant storage implementations
- [ ] Ensure both file and FAISS backends work

### Task 1.4: Implement Debug Logging
**Files to modify**: All remaining Python files
- [ ] Add ENGRAM_DEBUG environment check
- [ ] Wrap all logger calls in debug conditionals
- [ ] Remove verbose progress bars and status messages
- [ ] Keep only error logging by default

## Phase 2: Migration and Testing

### Task 2.1: Update MCP Tools
**File**: `engram/api/mcp_server.py` or `engram/api/fastmcp_server.py`
- [ ] Wrap new Memory API with MCP-compatible interface
- [ ] Ensure all existing MCP tools continue working
- [ ] Test with other Tekton components

### Task 2.2: Create Compatibility Layer
**File**: `engram/compat.py`
- [ ] Create thin wrappers for most common old API calls
- [ ] Add deprecation warnings
- [ ] Document migration path

### Task 2.3: Update Tests
**Directory**: `tests/`
- [ ] Create tests for new Memory API
- [ ] Update existing tests to use new API
- [ ] Ensure storage backends are tested
- [ ] Add integration tests

### Task 2.4: Update Examples
**Directory**: `examples/`
- [ ] Create simple 5-line example
- [ ] Update existing examples
- [ ] Add migration examples

## Phase 3: Documentation

### Task 3.1: Rewrite README
**File**: `engram/README.md`
- [ ] Clear explanation of what Engram does
- [ ] 5-line quickstart
- [ ] API reference
- [ ] Configuration options

### Task 3.2: Create Migration Guide
**File**: `engram/MIGRATION.md`
- [ ] Map old APIs to new
- [ ] Show before/after examples
- [ ] List removed features
- [ ] Provide compatibility timeline

### Task 3.3: Update Component Docs
**File**: `MetaData/ComponentDocumentation/Engram/`
- [ ] Update technical documentation
- [ ] Update API reference
- [ ] Update integration guide

## Implementation Notes

### Storage Layer Consolidation

Current storage implementations to consolidate:
- `memory.py` - Base memory interface
- `memory_faiss.py` - FAISS vector storage
- `memory_manager.py` - Memory service management
- `structured_memory.py` - Categorized memories

Target: Single `storage.py` with pluggable backends

### API Simplification Example

**Before** (multiple ways):
```python
# Method 1: Direct memory
memory = EngramMemory()
await memory.add("thought", metadata={})

# Method 2: Structured memory  
structured = StructuredMemory()
await structured.add_memory("thought", "category", 0.8)

# Method 3: CLI style
await s("thought")

# Method 4: Natural interface
async with think("thought"):
    pass

# Method 5: MCP tool
await memory_store({"text": "thought"})
```

**After** (one way):
```python
from engram import Memory
mem = Memory()
await mem.store("thought")
```

### Debug Logging Pattern

```python
import os
import logging

DEBUG = os.getenv('ENGRAM_DEBUG', '').lower() == 'true'
logger = logging.getLogger(__name__)

def debug_log(message: str, level=logging.INFO):
    """Log only if debug mode is enabled"""
    if DEBUG:
        logger.log(level, message)

# Usage throughout code:
debug_log("Initializing vector store")  # Silent by default
logger.error("Critical error")  # Always logs errors
```

## Success Metrics

### Phase 1 Complete When:
- [ ] New Memory API implemented and working
- [ ] Experimental features removed
- [ ] No output unless ENGRAM_DEBUG=true
- [ ] Basic tests passing

### Phase 2 Complete When:
- [ ] MCP tools working with new API
- [ ] Other Tekton components tested
- [ ] Migration path documented
- [ ] All tests passing

### Phase 3 Complete When:
- [ ] Documentation reflects reality
- [ ] 5-line quickstart works
- [ ] Migration guide complete
- [ ] Component docs updated

## Risk Mitigation

### Risk: Breaking Other Components
- Maintain MCP interface compatibility
- Test with Apollo, Hermes, others
- Provide compatibility layer if needed

### Risk: Losing Important Features
- Analyze component dependencies first
- Keep all actually-used functionality
- Document what was removed and why

### Risk: Migration Difficulty
- Provide clear examples
- Maintain old APIs temporarily
- Offer assisted migration

## Next Steps

1. Start with Task 1.1: Create simple Memory API
2. Test basic functionality
3. Proceed through tasks systematically
4. Regular testing with other components
5. Update documentation as we go