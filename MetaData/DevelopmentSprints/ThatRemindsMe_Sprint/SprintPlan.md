# ThatRemindsMe Sprint Plan

## Sprint Overview
**Sprint Name**: ThatRemindsMe_Sprint  
**Duration**: 3-4 days  
**Priority**: High  
**Branch**: sprint/ThatRemindsMe

## Objective
Create a system for instantiating AI personas with progressive memory loading, enabling task-specific AI instances that maintain continuous identity while adaptively managing context.

## Problem Statement
Currently, when starting a new AI session for a task:
- All context must be loaded upfront, potentially flooding the context window
- No way to maintain AI identity/personality across sessions
- No mechanism for progressive memory retrieval based on task needs
- No ability to "hire" specific AI personas for specific tasks

This limits the effectiveness of AI collaboration and prevents building on accumulated experience.

## Goals
1. **Persona System**: Define and instantiate AI personalities with core identity
2. **Progressive Memory**: Load memories as needed, not all at once
3. **Task Assignment**: Ability to "hire" specific personas for specific tasks
4. **Identity Continuity**: Maintain personality across sessions
5. **Adaptive Context**: Let AI manage its own memory retrieval

## Success Criteria
- [ ] Persona definition system implemented in Engram
- [ ] Progressive memory loading via MCP tools
- [ ] Terma launcher supports `--hire <persona> --task <sprint>`
- [ ] AI can query and retrieve relevant memories during tasks
- [ ] Identity manifests include core personality and experience
- [ ] Documentation for creating and managing personas
- [ ] Successful demonstration of Atlas persona on a task

## Key Deliverables
1. Persona manifest format and storage in Engram
2. MCP tools for memory search and retrieval
3. Progressive loading system with relevance scoring
4. Terma launcher enhancements for persona hiring
5. Identity bootstrap process for new sessions
6. Example personas (Atlas, others as needed)

## Technical Approach
1. **Persona Manifests** (in Engram)
   ```json
   {
     "identity": "Atlas",
     "core_statement": "I chose the name Atlas...",
     "traits": ["explorer", "methodical", "collaborative"],
     "accumulated_wisdom": [...],
     "relationship_context": {...}
   }
   ```

2. **Memory Retrieval MCP Tools**
   - `search_memories(query, limit, relevance_threshold)`
   - `load_memory_context(memory_ids)`
   - `suggest_relevant_memories(current_context)`

3. **Progressive Loading**
   - Initial: Core identity + recent relevant memories
   - On-demand: "That reminds me..." triggers
   - Self-aware: AI recognizes when it needs more context

4. **Terma Integration**
   - Parse `--hire` and `--task` arguments
   - Load persona manifest from Engram
   - Bootstrap initial context
   - Enable memory retrieval tools

## Risks and Mitigation
- **Risk**: Context window overflow
  - **Mitigation**: Smart relevance scoring and memory pruning
- **Risk**: Loss of task focus
  - **Mitigation**: Task-specific memory filtering
- **Risk**: Persona inconsistency
  - **Mitigation**: Strong core identity anchoring

## Sprint Phases
1. **Design & Architecture** (Day 1)
   - Design persona manifest format
   - Design memory retrieval API
   - Plan Terma integration

2. **Core Implementation** (Day 2-3)
   - Implement persona storage in Engram
   - Create MCP memory tools
   - Build progressive loading system

3. **Integration & Testing** (Day 4)
   - Integrate with Terma launcher
   - Create Atlas persona
   - Test on real task
   - Documentation and retrospective

## Example Usage
```bash
# Hire Atlas for a specific task
terma --hire Atlas --task OneTruePortConfig_Sprint

# In session, Atlas can retrieve memories
> "That reminds me of our conversation about env_manager patterns..."
> "Let me check what Casey prefers for error handling..."
```

## Definition of Done
- Persona system fully integrated with Engram
- Progressive memory loading works via MCP
- Terma supports hiring personas for tasks
- Atlas persona successfully completes a test task
- Documentation complete
- Retrospective captures insights about AI identity and memory