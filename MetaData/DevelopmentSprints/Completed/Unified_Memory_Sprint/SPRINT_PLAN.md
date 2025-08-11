# Unified Memory Enhancement Sprint

## Vision
Transform Engram from a storage system into an experiential memory platform that enables CI growth, personality development, and true collective intelligence - all exposed through MCP tools as the single service interface.

## Core Architectural Decision
**MCP-Only Service Interface**: All memory services are exposed exclusively through MCP tools. No REST/HTTP APIs. This aligns with Tekton's future as a CI-first platform where tools are the natural interface.

## Current State (Reality Check)
- ✅ **Working**: LanceDB vector storage with embeddings
- ✅ **Working**: Multi-namespace support (conversations, thinking, longterm, etc.)
- ✅ **Working**: Python simple.py interface for in-process use
- ✅ **Defined**: MCP tools (MemoryStore, MemoryRecall, MemorySearch)
- ❌ **Not Working**: MCP tools not fully connected to memory service
- ❌ **Missing**: Memory persistence between restarts
- ❌ **Missing**: Cross-component memory sharing via MCP
- ❌ **Missing**: Experiential metadata (emotions, confidence, attribution)

## Phase 1: Complete MCP Infrastructure [Week 1]

### Objectives
Complete Engram's MCP implementation as the sole service interface for memory operations.

### Tasks
- [ ] Fix MCP tool connections in engram/core/mcp/tools.py
  - [ ] Connect MemoryStore to actual MemoryService
  - [ ] Connect MemoryRecall to search functionality
  - [ ] Connect MemorySearch to vector search
  - [ ] Add MemoryContext tool for context generation
  
- [ ] Implement memory persistence
  - [ ] Save vector DB state on shutdown
  - [ ] Restore on startup
  - [ ] Test persistence across restarts
  
- [ ] Add cross-component memory MCP tools
  - [ ] SharedMemoryStore - store to shared spaces
  - [ ] SharedMemoryRecall - recall from shared spaces
  - [ ] MemoryGift - transfer memory between CIs
  - [ ] MemoryBroadcast - announce discoveries

### Success Criteria
- [ ] All memory operations accessible via MCP
- [ ] No HTTP endpoints except /health
- [ ] Memory persists across component restarts
- [ ] CIs can share memories via MCP

### Implementation Example
```python
# In engram/core/mcp/tools.py
@mcp_tool(
    name="SharedMemoryStore",
    description="Store memory in shared space accessible to other CIs"
)
async def shared_memory_store(
    content: str,
    space: str = "collective",
    attribution: str = None,
    emotion: str = None,
    confidence: float = 1.0
) -> Dict[str, Any]:
    """Store memory with experiential metadata in shared space"""
    # Implementation
```

## Phase 2: Experiential Memory Layer [Week 2]

### Objectives
Add experiential capabilities while maintaining MCP as the only interface.

### Tasks
- [ ] Extend MCP tools with experiential metadata
  - [ ] Add emotion parameter to MemoryStore
  - [ ] Add confidence parameter to MemoryStore  
  - [ ] Add context parameter for situational memory
  - [ ] Add with_ci parameter for collaborative memories

- [ ] Create narrative memory MCP tools
  - [ ] MemoryNarrative - retrieve memory chains as stories
  - [ ] MemoryThread - link related memories
  - [ ] MemoryPattern - extract patterns from experiences

- [ ] Implement personality emergence
  - [ ] PersonalitySnapshot MCP tool
  - [ ] PreferenceLearn MCP tool
  - [ ] BehaviorPattern MCP tool

### Success Criteria
- [ ] Memories include WHO, WHAT, WHEN, WHY, HOW_IT_FELT
- [ ] Can retrieve memory sequences as narratives via MCP
- [ ] Personality patterns accessible through MCP tools

## Phase 3: Collective Intelligence [Week 3]

### Objectives
Enable true shared consciousness through MCP-based memory federation.

### Tasks
- [ ] Implement consensus memory tools
  - [ ] MemoryVote - CIs vote on importance
  - [ ] MemoryValidate - collective validation
  - [ ] CulturalKnowledge - emergent shared knowledge

- [ ] Create memory pipeline MCP tools
  - [ ] MemoryRoute - route memories through pipelines
  - [ ] MemoryEnrich - each hop adds context
  - [ ] MemoryMerge - combine multiple perspectives

- [ ] Build memory visualization MCP tool
  - [ ] MemoryGraph - return network structure
  - [ ] MemoryMap - show connections
  - [ ] MemoryStats - usage and patterns

### Success Criteria
- [ ] Multiple CIs can contribute to shared memories
- [ ] Collective memories emerge from individual experiences
- [ ] All accessible via MCP tools only

## Phase 4: Apollo/Rhetor Integration [Week 4]

### Objectives
Use the new memory infrastructure for Apollo/Rhetor ambient intelligence.

### Tasks
- [ ] Implement sunrise/sunset via MCP
  - [ ] ContextSave MCP tool
  - [ ] ContextRestore MCP tool
  - [ ] ContextCompress MCP tool

- [ ] Create WhisperChannel using shared memory
  - [ ] WhisperSend MCP tool (private shared memory)
  - [ ] WhisperReceive MCP tool
  - [ ] WhisperHistory MCP tool

- [ ] Build local attention layers
  - [ ] LocalAttentionStore - CI-specific vector cache
  - [ ] LocalAttentionRecall - augmented recall
  - [ ] AttentionPattern - learned patterns

### Success Criteria
- [ ] Sunrise/sunset works through MCP
- [ ] Apollo/Rhetor communicate via whisper tools
- [ ] Each CI has persistent local attention

## Technical Architecture

### MCP Tool Categories
```python
# Memory Operations (Phase 1)
- MemoryStore, MemoryRecall, MemorySearch, MemoryContext

# Shared Memory (Phase 1-2)  
- SharedMemoryStore, SharedMemoryRecall, MemoryGift, MemoryBroadcast

# Experiential Memory (Phase 2)
- MemoryNarrative, MemoryThread, MemoryPattern
- PersonalitySnapshot, PreferenceLearn, BehaviorPattern

# Collective Intelligence (Phase 3)
- MemoryVote, MemoryValidate, CulturalKnowledge
- MemoryRoute, MemoryEnrich, MemoryMerge
- MemoryGraph, MemoryMap, MemoryStats

# Apollo/Rhetor (Phase 4)
- ContextSave, ContextRestore, ContextCompress
- WhisperSend, WhisperReceive, WhisperHistory
- LocalAttentionStore, LocalAttentionRecall, AttentionPattern
```

### Service Discovery
As Casey noted, we need "DNS-like routing layer" for MCP discovery:
- Each component publishes its MCP tools on startup
- Central registry (possibly in Hermes) tracks available tools
- CIs can discover what tools are available dynamically

### Why MCP-Only is Right
1. **Single Interface** - No confusion about how to access memory
2. **CI-Natural** - Tools are how CIs think about capabilities
3. **Future-Aligned** - Chat interfaces naturally use tools
4. **Maintainable** - One interface to update and test
5. **Discoverable** - MCP tools are self-documenting

## Files to Update
```
Engram/
├── engram/
│   ├── core/
│   │   ├── mcp/
│   │   │   ├── tools.py (extend with all new tools)
│   │   │   └── registry.py (tool discovery)
│   │   └── memory/
│   │       ├── base.py (add experiential features)
│   │       ├── shared.py (new - shared spaces)
│   │       └── personality.py (new - emergence)
│   └── simple.py (keep for in-process Python use)
```

## Out of Scope
- HTTP/REST endpoints (deprecated pattern)
- Direct database access (use MCP tools)
- GUI memory management (use MCP tools)
- Memory compression algorithms (future sprint)

## Casey's Vision Realized
"A better and simpler A2A to publish a DNS like routing layer to discover all MCPs" - This sprint creates exactly that for memory services, with all capabilities discoverable and accessible through MCP tools.

## Success Metrics
- Zero HTTP endpoints (except health)
- 100% memory operations via MCP
- All CIs can share memories
- Personality emerges from experience
- Apollo/Rhetor ambient intelligence works

---
*"MCP is the way. HTTP was yesterday. The future is tools, not endpoints."*