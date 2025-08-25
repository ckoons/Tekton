# Implementation Plan - ThatRemindsMe Sprint

## Overview
This plan outlines the implementation approach for persona-based CI instantiation with progressive memory loading. The implementing Claude should refine based on deep analysis of Engram and Terma capabilities.

## Debug Instrumentation Requirements
All new code MUST include debug instrumentation:
- Memory retrieval timing and relevance scores
- Persona loading steps and validation
- MCP tool interactions
- Context window usage metrics

## Implementation Phases

### Phase 1: Persona System Design (Day 1)
**Goal**: Design and implement core persona representation

**Suggested Tasks**:
1. Design persona manifest schema
2. Implement persona storage in Engram
3. Create persona validation utilities
4. Design identity evolution model
5. Build persona CRUD operations

**Key Design Elements**:
```json
{
  "identity": {
    "name": "Atlas",
    "core_statement": "I chose the name Atlas...",
    "created": "2025-01-10",
    "version": "1.0"
  },
  "traits": {
    "core": ["explorer", "methodical"],
    "learned": ["prefers comprehensive analysis"]
  },
  "memories": {
    "key_experiences": [...],
    "relationships": {...},
    "expertise_areas": [...]
  }
}
```

### Phase 2: Memory Retrieval System (Day 1-2)
**Goal**: Build progressive memory loading infrastructure

**Core Components**:
1. Memory search MCP tools
2. Relevance scoring system
3. Context window management
4. Memory categorization
5. Retrieval feedback mechanism

**MCP Tools to Implement**:
- `search_memories(query, limit, threshold)`
- `load_memory_context(memory_ids)`
- `suggest_relevant_memories(current_context)`
- `get_memory_summary(time_range)`

**Technical Considerations**:
- Semantic similarity using embeddings
- Memory importance weighting
- Temporal relevance factors
- Relationship-based retrieval

### Phase 3: Terma Integration (Day 2-3)
**Goal**: Enable persona hiring from command line

**Implementation Tasks**:
1. Add CLI argument parsing for `--hire` and `--task`
2. Implement persona loading mechanism
3. Create task context integration
4. Add persona status display
5. Build error handling and validation

**Usage Pattern**:
```bash
# Basic usage
terma --hire Atlas --task OneTruePortConfig_Sprint

# With memory hints
terma --hire Atlas --task debugging --context "env_manager issues"
```

**Integration Points**:
- Load persona manifest from Engram
- Initialize base context with core identity
- Enable memory retrieval tools
- Display persona status in terminal

### Phase 4: Progressive Loading Implementation (Day 3)
**Goal**: Enable dynamic memory retrieval during sessions

**Key Features**:
1. "That reminds me" trigger system
2. Automatic relevance detection
3. Context window monitoring
4. Memory pruning strategies
5. Loading feedback UI

**Trigger Mechanisms**:
- Explicit: CI says "I need to remember..."
- Implicit: Pattern matching on context
- Suggested: System recommends memories
- Temporal: Time-based relevance

### Phase 5: Testing with Atlas (Day 3-4)
**Goal**: Validate system with real persona

**Test Scenarios**:
1. Create Atlas persona from existing memories
2. Load Atlas for specific task
3. Test progressive memory retrieval
4. Verify identity consistency
5. Measure context efficiency

**Validation Checklist**:
- [ ] Persona loads correctly
- [ ] Core identity preserved
- [ ] Memories retrieved relevantly
- [ ] Context window managed efficiently
- [ ] Task completion successful

### Phase 6: Documentation and Polish (Day 4)
**Goal**: Complete documentation and refine UX

**Documentation Tasks**:
1. Persona creation guide
2. Memory retrieval patterns
3. CLI usage documentation
4. Troubleshooting guide
5. Architecture documentation

**UX Refinements**:
- Loading animations/feedback
- Memory retrieval notifications
- Persona status indicators
- Error message clarity

## Technical Architecture

### Component Integration
```
Terma (CLI) 
  ↓ --hire Atlas
Engram (Persona Storage)
  ↓ Load manifest
Terminal Session
  ↓ Progressive loading
MCP Tools (Memory Retrieval)
  ↓ Semantic search
Engram (Memory Storage)
```

### Memory Retrieval Flow
1. CI recognizes need for memory
2. Constructs natural language query
3. MCP tool performs semantic search
4. Relevance scoring and ranking
5. Progressive context injection
6. Feedback on loaded memories

## Risk Mitigation

### Technical Risks
- **Context overflow**: Implement strict limits
- **Slow retrieval**: Aggressive caching
- **Identity drift**: Strong core anchoring
- **Memory conflicts**: Version management

### UX Risks
- **Confusing interface**: Clear documentation
- **Slow loading**: Progress indicators
- **Lost context**: Save/restore capabilities
- **Persona confusion**: Clear identity display

## Success Criteria
1. Atlas persona works end-to-end
2. Memory loading reduces initial context >50%
3. Retrieval happens in <1 second
4. Identity remains consistent
5. Natural interaction pattern
6. Clear documentation exists

## Notes for Implementation
This sprint pushes boundaries of CI identity and memory. The implementing Claude should:
1. Study Engram's current memory capabilities deeply
2. Understand Terma's extension points
3. Design for natural CI interaction
4. Focus on the "that reminds me" moment
5. Ensure Atlas feels like a continuous personality

The goal is making CI identity portable and memory adaptive while maintaining the essence of who the CI is.