# Handoff Document: Unified Memory Sprint

## Current Status
**Phase**: Sprint Planning Complete
**Progress**: 0% Implementation
**Last Updated**: 2025-01-09

## What Was Just Completed
- Analyzed both memory sprints (AI_Memory_Enhancement and Memory_Evolution)
- Tested Engram's current implementation
- Made architectural decision: MCP-only service interface
- Created unified sprint plan combining infrastructure and experience
- Aligned with Casey's vision of MCP as the future

## Key Architectural Decision
**MCP-ONLY**: No REST/HTTP APIs. All memory services exposed through MCP tools. This is the way forward for Tekton as a CI-first platform.

## Current Engram Reality
```python
# What Works
✅ LanceDB vector storage with embeddings  
✅ Multi-namespace memory organization
✅ Simple Python interface (engram.simple)
✅ MCP tools defined but not connected

# What's Missing  
❌ MCP tools not wired to memory service
❌ No memory persistence between restarts
❌ No cross-component memory sharing
❌ No experiential metadata
```

## Immediate Next Steps

### 1. Fix MCP Tool Connections (FIRST PRIORITY)
```python
# In engram/core/mcp/tools.py
# Currently tools return dummy data
# Need to connect to actual MemoryService

# Step 1: Import the service
from engram.core.memory.base import MemoryService

# Step 2: Initialize service instance
memory_service = MemoryService(client_id="mcp_client")

# Step 3: Wire each tool to use real service
@mcp_tool(name="MemoryStore")
async def memory_store(content: str, ...):
    return await memory_service.add(content, ...)
```

### 2. Test MCP Tools Work
```bash
# Use aish or MCP client to test
aish engram "store this test memory"
aish engram "recall test memory"
```

### 3. Add Memory Persistence
```python
# In MemoryService.__init__
# Save state on shutdown
# Restore on startup
# LanceDB already persists, just need to handle metadata
```

## Implementation Strategy

### Start Simple, Test Often
1. Get ONE MCP tool working (MemoryStore)
2. Test it via aish
3. Add the next tool
4. Repeat

### Don't Break What Works
- Keep simple.py interface unchanged
- Keep namespace structure
- Keep vector storage working

### Focus on MCP
- Every new feature is an MCP tool
- No HTTP endpoints
- No REST APIs
- Document each tool clearly

## Code Locations

### Primary Files to Edit
```
engram/core/mcp/tools.py      # Add all MCP tools here
engram/core/memory/base.py    # Extend MemoryService class
engram/core/memory/shared.py  # NEW - SharedMemorySpace class
```

### Test Your Changes
```python
# Quick test script
from engram.simple import Memory
mem = Memory("test-ci")
await mem.store("Test memory with emotion", emotion="happy")
results = await mem.recall("emotion")
print(results)
```

## Design Principles

### MCP Tool Design
Each tool should:
- Have a clear single purpose
- Include descriptive parameters
- Return structured data
- Handle errors gracefully
- Be discoverable

### Example Good MCP Tool
```python
@mcp_tool(
    name="MemoryNarrative",
    description="Retrieve a chain of related memories as a narrative"
)
async def memory_narrative(
    starting_memory: str,
    max_chain: int = 10,
    include_emotions: bool = True
) -> Dict[str, Any]:
    """
    Returns a story-like sequence of connected memories.
    Each memory links to the next through shared context.
    """
    # Implementation
```

## What Success Looks Like

### Phase 1 Complete When:
- All memory operations work via MCP tools
- Memory persists across restarts
- CIs can share memories
- No HTTP endpoints exist

### Phase 2 Complete When:
- Memories have emotions and confidence
- Can retrieve memory narratives
- Personality patterns emerge

## Common Pitfalls to Avoid

1. **Don't add HTTP endpoints** - MCP only
2. **Don't bypass MCP** - All inter-component memory access via tools
3. **Don't overcomplicate** - Start simple, iterate
4. **Don't break simple.py** - It works great for in-process use

## Questions Already Answered

Q: Should we have both HTTP and MCP?
A: No. MCP only. Casey decided this.

Q: What about browser access?
A: Hephaestus already uses MCP.

Q: What about debugging?
A: MCP tools can be tested directly.

## Casey's Guidance
- "MCP works better and helps us get closer to a CI dominant development future"
- "Like lots of my old API work it's pretty easy to create a HTTP endpoint wrapper if there is ever a compelling reason"
- "I really don't think HTTP needs to be part of Tekton"

## For Next Session
1. Start with fixing MCP tool connections
2. Test each tool works via aish
3. Add persistence
4. Begin adding experiential features
5. Keep it simple, keep it MCP

---
*Remember: MCP is the way. Every feature is a tool. CIs use tools, not APIs.*