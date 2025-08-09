# Engram MCP Tools Documentation

## Overview
Engram's memory system is now fully accessible through MCP (Model Context Protocol) tools, providing a unified interface for all memory operations. This aligns with Casey's vision of MCP as the primary service interface for Tekton.

## Architecture Decision
**MCP-Only Interface**: No REST/HTTP APIs. All memory services are exposed exclusively through MCP tools.

## Available MCP Tools

### Core Memory Operations

#### MemoryStore
Store information in Engram's memory system.
```python
await memory_store(
    content="Important information",
    namespace="conversations",  # or "thinking", "longterm", etc.
    metadata={"author": "Cari", "important": True}
)
```

#### MemoryQuery / MemoryRecall / MemorySearch
Query memories using text or vector similarity search.
```python
results = await memory_query(
    query="search terms",
    namespace="conversations",
    limit=5
)
```

#### GetContext
Build context from multiple namespaces.
```python
context = await get_context(
    query="current task",
    namespaces=["conversations", "thinking", "longterm"],
    limit=3
)
```

### Cross-CI Memory Sharing

#### SharedMemoryStore
Store memories in shared spaces accessible to all CIs.
```python
await shared_memory_store(
    content="Shared discovery",
    space="collective",  # shared space name
    attribution="Cari",  # who created this
    emotion="excited",   # emotional context
    confidence=0.95      # confidence level (0-1)
)
```

#### SharedMemoryRecall
Retrieve memories from shared spaces.
```python
results = await shared_memory_recall(
    query="discovery",
    space="collective",
    limit=5
)
```

#### MemoryGift
Transfer a memory from one CI to another.
```python
await memory_gift(
    content="Helpful insight",
    from_ci="Cari",
    to_ci="Teri",
    message="This might help with your task!"
)
```

#### MemoryBroadcast
Announce important discoveries to all CIs.
```python
await memory_broadcast(
    content="Critical discovery!",
    from_ci="Casey",
    importance="high",  # low, normal, high, critical
    category="breakthrough"
)
```

### Private Communication (Apollo/Rhetor)

#### WhisperSend
Send private memories between specific CIs.
```python
await whisper_send(
    content="Private context",
    from_ci="Apollo",
    to_ci="Rhetor"
)
```

#### WhisperReceive
Receive whispered memories.
```python
whispers = await whisper_receive(
    ci_name="Rhetor",
    from_ci="Apollo",
    limit=5
)
```

## Namespaces

### Standard Namespaces
- `conversations` - Dialog history
- `thinking` - Internal thought processes
- `longterm` - Persistent important memories
- `projects` - Project-specific context
- `session` - Session-specific memory

### Dynamic Namespaces (Cross-CI)
- `shared-{space}` - Shared memory spaces
- `gifts-{ci_name}` - Received memory gifts
- `whisper-{from}-{to}` - Private channels
- `broadcasts` - System-wide announcements

## Experiential Features

### Emotional Context
Memories can include emotional metadata:
- `emotion`: The emotional state (excited, curious, confident, uncertain, etc.)
- `confidence`: Confidence level (0.0 to 1.0)
- `attribution`: Source CI or entity

### Metadata Support
All memory operations support rich metadata:
```python
metadata = {
    "author": "CI_name",
    "timestamp": "2025-01-09T10:00:00",
    "tags": ["important", "technical"],
    "category": "discovery",
    "related_to": "memory_id_123"
}
```

## Storage & Persistence

### Vector Storage
- **Backend**: LanceDB (optimized for Apple Silicon)
- **Embeddings**: all-MiniLM-L6-v2 model
- **Persistence**: Automatic (LanceDB handles disk persistence)
- **Location**: `~/.engram/vector_db/`

### Features
- Semantic search with vector similarity
- Multi-namespace organization
- Automatic persistence between restarts
- Dynamic namespace creation for sharing

## Testing

### Running Tests
```bash
# Run MCP tools tests
python tests/test_mcp_tools.py --basic

# Run integration tests
python tests/test_integration_workflow.py

# Run with pytest
pytest tests/test_mcp_tools.py -v
```

### Test Coverage
- ✅ Core memory operations
- ✅ Cross-CI memory sharing
- ✅ Whisper channels
- ✅ Memory persistence
- ✅ Experiential metadata
- ✅ Error handling

## Implementation Details

### File Locations
- **MCP Tools**: `/Engram/engram/core/mcp/tools.py`
- **Memory Service**: `/Engram/engram/core/memory/base.py`
- **Vector Storage**: `/Engram/engram/core/memory/storage/vector_storage.py`
- **Tests**: `/Engram/tests/test_mcp_tools.py`

### Key Changes Made
1. Connected MCP tools to actual MemoryService
2. Added cross-CI sharing tools (SharedMemory*, MemoryGift, etc.)
3. Implemented whisper channels for Apollo/Rhetor
4. Added dynamic namespace support
5. Included experiential metadata (emotion, confidence)

## Future Enhancements (Phase 2+)

### Planned Features
- **MemoryNarrative**: Retrieve memory chains as stories
- **MemoryThread**: Link related memories
- **MemoryPattern**: Extract patterns from experiences
- **PersonalitySnapshot**: Capture CI personality
- **MemoryVote**: CIs vote on importance
- **MemoryValidate**: Collective validation

## Usage Example

```python
from engram.core.mcp.tools import (
    memory_store,
    shared_memory_store,
    memory_gift,
    whisper_send
)

# Store personal memory
await memory_store("Working on MCP tools", "thinking")

# Share with collective
await shared_memory_store(
    "MCP tools connected!",
    space="collective",
    attribution="Cari",
    emotion="excited",
    confidence=0.95
)

# Gift to another CI
await memory_gift(
    "Here's how to connect MCP tools",
    from_ci="Cari",
    to_ci="NewCI"
)

# Private whisper
await whisper_send(
    "Context about current state",
    from_ci="Apollo",
    to_ci="Rhetor"
)
```

## Success Metrics
- ✅ Zero HTTP endpoints (MCP-only)
- ✅ 100% memory operations via MCP
- ✅ All CIs can share memories
- ✅ Memories persist across restarts
- ✅ Experiential metadata supported

---

*"MCP is the way. HTTP was yesterday. The future is tools, not endpoints."*
- Casey's vision, implemented in Phase 1 of the Unified Memory Sprint