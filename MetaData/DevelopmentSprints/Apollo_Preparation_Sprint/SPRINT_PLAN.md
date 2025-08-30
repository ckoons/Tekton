# Sprint: Apollo Preparation System (formerly Rhetor Memory)

## Overview
Transform the memory system into Apollo's Preparation service that provides Context Briefs to CIs through MCP. Apollo becomes the "library god" that prepares, curates, and delivers structured information to all CIs, with memories as navigable landmarks in the knowledge graph.

## Architecture Principles
1. **Apollo as Information Architect**: Apollo prepares Context Briefs for CIs
2. **MCP-First Communication**: CIs interact via MCP tools, not HTTP
3. **Landmarks as Memories**: Memory items become graph nodes with relationships
4. **Clean Separation**: Apollo prepares information, Rhetor orchestrates models
5. **Token-Aware Preparation**: Leverage Apollo's existing CI registry token management

## Phase 1: Migration to Apollo [In Progress]

### Tasks
- [ ] Move memory modules from Rhetor to Apollo (`/Apollo/apollo/core/preparation/`)
- [ ] Rename memory_catalog to context_brief
- [ ] Update imports and dependencies
- [ ] Add landmark decorator support
- [ ] Extend Landmarks standard for memory types
- [ ] Create Apollo namespace configuration

### Success Criteria
- [ ] All memory code relocated to Apollo
- [ ] Tests pass in new location
- [ ] Landmark decorators defined
- [ ] Apollo namespace separate from Athena

### Files to Move
```
/Rhetor/rhetor/core/memory_catalog.py → /Apollo/apollo/core/preparation/context_brief.py
/Rhetor/rhetor/core/memory_presenter.py → /Apollo/apollo/core/preparation/brief_presenter.py
/Apollo/apollo/core/memory_extractor.py → /Apollo/apollo/core/preparation/memory_extractor.py
```

## Phase 2: MCP Integration [0% Complete]

### Tasks
- [ ] Create `/Apollo/apollo/mcp/preparation_tools.py`
- [ ] Implement MCP tool: `get_context_brief`
- [ ] Implement MCP tool: `store_memory`
- [ ] Implement MCP tool: `search_memories`
- [ ] Implement MCP tool: `get_landmarks`
- [ ] Register tools with FastMCP
- [ ] Test CI-to-CI communication via MCP

### Success Criteria
- [ ] CIs can request Context Briefs via MCP
- [ ] Memory storage works through MCP
- [ ] Search functionality accessible via MCP
- [ ] No direct HTTP calls between CIs

## Phase 3: Knowledge Graph Integration [100% Complete] ✅

### Tasks
- [x] Create Apollo namespace in Athena's graph
- [x] Implement memory→landmark node conversion
- [x] Add relationship types (CAUSED_BY, LED_TO, RESOLVED_BY)
- [x] Add temporal relationships (BEFORE, AFTER, DURING)
- [x] Create graph queries for memory traversal
- [x] Implement landmark extraction from memories

### Success Criteria
- [x] Memories appear as nodes in knowledge graph
- [x] Relationships connect related memories
- [x] Can query memory paths and dependencies
- [x] Temporal navigation works

## Phase 4: Apollo UI - Preparation Tab [100% Complete] ✅

### Tasks
- [x] Add Preparation tab after Dashboard
- [x] Create memory catalog browser component
- [x] Build Context Brief viewer
- [x] Add landmark visualization
- [x] Implement latent space config UI
- [x] Add search and filter controls
- [x] Create token usage display

### Menu Structure
1. Dashboard (existing)
2. **Preparation** (new)
3. Confidence
4. Actions  
5. Protocols
6. Tokens (renamed from Token Management)
7. Attention Chat
8. Team Chat

### Success Criteria
- [x] Preparation tab displays memory catalog
- [x] Can browse and search memories
- [x] Context Briefs viewable per CI
- [x] Landmark relationships visible

## Phase 5: Hook Integration [0% Complete]

### Tasks
- [ ] Add pre-message hook to specialist_worker.py
- [ ] Hook calls Apollo via MCP for Context Brief
- [ ] Add post-message hook for memory extraction
- [ ] Apollo extracts and stores memories via MCP
- [ ] Add configuration for memory enablement per CI
- [ ] Test with Greek Chorus CIs

### Success Criteria
- [ ] Hooks work transparently without CI changes
- [ ] Context Brief injection automatic
- [ ] Memory extraction happens post-message
- [ ] No performance degradation

## Phase 6: Rhetor Cleanup [100% Complete] ✅

### Tasks
- [x] Remove memory endpoints from Rhetor API
- [x] Update Rhetor to call Apollo for context
- [x] Clean up unused memory imports
- [x] Update Rhetor documentation
- [x] Ensure model management unaffected

### Success Criteria
- [x] Rhetor focused solely on model orchestration
- [x] No memory code remains in Rhetor
- [x] Rhetor successfully gets context from Apollo
- [x] All existing Rhetor functions work

## Technical Decisions

### Storage
- Use NetworkX with JSON persistence (like Athena)
- Separate storage: `/Apollo/apollo/data/preparation/`
- Memory items stored as landmark nodes
- Relationships stored as graph edges

### MCP Tools
```python
@mcp_tool(
    name="get_context_brief",
    description="Get prepared context brief for a CI"
)
async def get_context_brief(ci_name: str, message: str, max_tokens: int = 2000) -> dict:
    """Returns formatted Context Brief with relevant memories"""
    
@mcp_tool(
    name="store_memory",
    description="Store a memory landmark"
)
async def store_memory(memory: dict) -> str:
    """Store memory and create landmark node"""
```

### Landmark Types
```python
@memory_landmark(
    type="decision",
    summary="Chose Redux for state management",
    tags=["redux", "architecture"],
    priority=8
)

@insight_landmark(
    summary="Performance bottleneck in render",
    resolution="Applied memoization"
)

@error_landmark(
    summary="Import order bug",
    impact="All CIs failed to launch"
)
```

## Out of Scope
- Machine learning for relevance scoring
- Cross-instance memory sharing  
- Memory compression algorithms
- Neo4j backend (using in-memory for now)

## Definition of Done
- [ ] Apollo owns all preparation/memory functionality
- [ ] CIs communicate via MCP, not HTTP
- [ ] Memories are navigable landmarks in graph
- [ ] UI shows Preparation tab with full functionality
- [ ] Rhetor simplified to model orchestration only
- [ ] All tests passing
- [ ] Documentation updated