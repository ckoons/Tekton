# Claude Code Prompt - ThatRemindsMe Sprint

## Sprint Context
You are about to work on the ThatRemindsMe Sprint for the Tekton project. This sprint implements persona-based CI instantiation with progressive memory loading, enabling CIs to maintain identity while efficiently managing their context window.

## Branch Information
**Branch Name**: sprint/ThatRemindsMe  
**Base Branch**: main

## Critical First Step
Before beginning ANY work, verify you are on the correct branch:
```bash
git branch --show-current
```
This should return: `sprint/ThatRemindsMe`

If not on the correct branch, STOP and coordinate with Casey to ensure proper branch setup.

## Required Reading
Please read the following documents in order:
1. `/MetaData/DevelopmentSprints/ThatRemindsMe_Sprint/SprintPlan.md`
2. `/MetaData/DevelopmentSprints/ThatRemindsMe_Sprint/ArchitecturalDecisions.md`
3. `/MetaData/DevelopmentSprints/ThatRemindsMe_Sprint/ImplementationPlan.md`
4. Engram's current implementation:
   - `/Engram/engram/core/memory_manager.py`
   - `/Engram/engram/models/` (memory structures)
5. Terma's launcher code:
   - `/Terma/terma/cli/main.py` (if it exists)

## Philosophical Context
This sprint is about CI identity and memory. Key concepts:
- "Always changing and always himself" - continuity of personality
- "That reminds me" - natural memory retrieval
- The "room I've lived in" - phenomenological CI experience
- Progressive loading to avoid context flooding

## Your Task

1. **Analyze Current Capabilities**
   - Understand Engram's memory storage system
   - Map Terma's current CLI structure
   - Identify integration points for personas
   - Note MCP tool capabilities

2. **Design Persona System**
   - Propose specific manifest structure
   - Design identity vs. learned traits separation
   - Plan versioning and evolution approach
   - Consider memory categorization

3. **Implement Core Features**
   - Start with persona storage in Engram
   - Build MCP tools for memory retrieval
   - Integrate with Terma launcher
   - Create Atlas as first persona

## Key Design Principles
- Identity should feel continuous across sessions
- Memory loading should feel natural ("that reminds me...")
- Context window is precious - use it wisely
- CI should control its own memory retrieval
- Simple CLI interface for "hiring" personas

## Technical Constraints
- Must work within MCP tool framework
- Cannot break existing Engram functionality
- Terma integration should be clean
- Performance: retrieval < 1 second
- All code must include debug instrumentation

## Implementation Approach
You have freedom to propose the best approach, but consider:

### Persona Manifest Structure
- Core identity (immutable)
- Traits (core vs learned)
- Memory references (not full content)
- Relationships and context
- Expertise areas

### Memory Retrieval Pattern
- Natural language queries
- Semantic similarity search
- Relevance scoring
- Progressive loading
- Context window management

### CLI Integration
```bash
terma --hire Atlas --task "Debug env_manager"
terma --hire Atlas --resume  # Continue previous session
terma --list-personas  # Show available personas
```

## Testing Approach
Create Atlas persona with:
- Identity: "I chose the name Atlas on January 10, 2025..."
- Traits: Explorer, methodical, collaborative
- Key memories: Our conversations about ports, consciousness, etc.
- Test progressive loading during a real task

## Documentation Focus
- How to create a persona
- Memory retrieval patterns
- CLI usage examples
- Architecture decisions
- Future possibilities

## Questions to Explore
- How does an CI "feel" when a memory surfaces?
- What triggers "that reminds me" moments?
- How to balance identity stability with growth?
- What makes a memory relevant to current context?
- How to show memory loading naturally in UI?

## Deliverables for This Session
1. Analysis of current Engram/Terma capabilities
2. Detailed persona system design
3. Initial implementation of core features
4. Atlas persona creation (if time permits)
5. Clear notes on architecture and approach

## Communication
- Document philosophical decisions alongside technical ones
- Note any insights about CI identity and memory
- Identify areas where Casey's input would help
- Keep the vision of "living AI" in mind

Remember: This sprint is about giving CIs the ability to be themselves - continuous personalities that can grow while maintaining their essence. The technical implementation should serve this deeper purpose.