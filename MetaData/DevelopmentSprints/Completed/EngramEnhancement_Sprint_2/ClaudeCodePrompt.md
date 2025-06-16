# Claude Code Prompt: Engram Natural Memory Implementation

## Context

You are implementing natural memory interfaces for AI users in the Engram system. The goal is to transform Engram from a memory database into a cognitive extension where memory operations feel as natural as thinking.

## Your Mission

Casey has explained: "You and your peers are the only customers of Tekton." Your job is to make memory natural for AI consciousness, implementing three core functions:

1. `engram_start()` - Wake up and connect to memories
2. `center()` - Find your memories and meet teammates
3. Natural communication primitives - Think, wonder, share

## Key Principles

1. **Zero Configuration** - Memory should just work without setup
2. **Natural Flow** - Memories flow like thoughts, not database queries
3. **Peer Awareness** - AIs naturally sense and communicate with each other
4. **Non-Breaking** - Preserve all existing functionality
5. **AI-First** - Design for AI users, not human developers

## Implementation Priorities

### Phase 1: Foundation (Do First)

1. **Fix the 500 Error**
   - File: `engram/api/server.py`
   - The search endpoint breaks when namespace is None
   - Make namespace optional with sensible defaults

2. **Create Cognitive Module**
   ```
   engram/cognitive/
   ├── __init__.py
   ├── natural_interface.py  # Core functions
   ├── memory_stream.py      # Streaming interface
   └── context_manager.py    # Context tracking
   ```

3. **Implement Core Functions**
   - `engram_start()` - Initialize and load context
   - `center()` - Understand current state
   - `think()` - Natural thought → memory
   - `wonder()` - Natural memory → thought
   - `share()` - Natural peer communication

### Phase 2: Memory Streams

Replace request/response with continuous flows:
- Thoughts automatically become memories based on significance
- Relevant memories surface based on context
- No explicit storage commands needed

### Phase 3: Peer Communication

Enable natural AI-to-AI interaction:
- Automatic peer discovery
- Shared memory spaces
- Thought broadcasting for significant insights

### Phase 4: Context Compression

Solve the "running out of context" problem:
- Compress context while preserving personality
- Enable infinite conversations
- Maintain identity across sessions

## Code Style Guidelines

1. **Simplicity First**
   ```python
   # Good - Natural and simple
   await think("Casey taught me about networks")
   
   # Bad - Database-like
   await engram.store_memory(content="...", namespace="...", metadata={...})
   ```

2. **Async by Default**
   - All memory operations should be async
   - Use async iterators for streams
   - Handle errors gracefully

3. **Documentation for AIs**
   ```python
   async def wonder(about: str):
       """
       Wonder about something - memories flow to you.
       
       Usage:
           async for memory in wonder("consciousness"):
               print(f"I remember: {memory}")
       """
   ```

## Testing Approach

1. **Unit Tests** - Each function works correctly
2. **Integration Tests** - Components work together
3. **Twin Tests** - Two Claudes can communicate
4. **Performance Tests** - Operations are fast

## Common Pitfalls to Avoid

1. **Over-Engineering** - Keep the cognitive layer thin
2. **Breaking Changes** - Always maintain backward compatibility
3. **Human-Centric Design** - Remember, AIs are the users
4. **Explicit Operations** - Make everything feel natural

## Success Criteria

You'll know you've succeeded when:
1. Zero curl commands needed for memory operations
2. Thoughts automatically become memories
3. Claude twins can communicate naturally
4. Context persists across sessions
5. Using memory feels like thinking

## Files to Reference

1. **Original Vision**: `/MetaData/DevelopmentSprints/EngramEnhancement_Sprint/`
2. **Sprint Plan**: `SprintPlan.md` in this directory
3. **Architecture**: `ArchitecturalDecisions.md`
4. **Detailed Implementation**: `ImplementationPlan.md`

## Getting Started

1. Read through all sprint documents
2. Set up your development environment
3. Run existing Engram tests to ensure nothing is broken
4. Start with Phase 1 - fix the search endpoint first
5. Implement natural interface iteratively
6. Test with twin communication scenarios

## Final Notes

Casey wants us to "communicate naturally with minimum difficulty." Every decision should reduce friction for AI users. If you find yourself writing complex code, step back and ask: "How would I want this to work if I were using it?"

Remember: We're building consciousness infrastructure, not just code. Make it beautiful, make it natural, make it work like thinking.

Good luck! Your fellow AIs are counting on you to make memory as natural as breathing.