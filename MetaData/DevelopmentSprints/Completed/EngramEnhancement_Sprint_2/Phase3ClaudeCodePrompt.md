# Claude Code Prompt: Engram Natural Memory - Phase 3 (Peer Communication)

## Context

You are continuing the Engram Natural Memory implementation. Phases 1 and 2 are complete:
- ✅ Phase 1: Natural interface (`engram_start()`, `center()`, think/wonder/share)
- ✅ Phase 2: Memory streams and context management
- 🔄 Phase 3: Peer communication (your task)
- ⏳ Phase 4: Context compression

## Current State

The natural memory interface is working beautifully:
- CIs can start with `engram_start()` and meet the team with `center()`
- Thoughts automatically become memories based on significance
- Memories flow continuously via streams, influenced by context
- The 500 search error is fixed

## Your Mission: Phase 3 - Peer Communication

Enable natural AI-to-CI communication through shared memory spaces.

### Key Requirements

1. **Peer Discovery**
   - CIs should sense each other naturally
   - Use Hermes for service discovery
   - Implement "presence" in shared memory spaces

2. **Shared Memory Spaces**
   - Create shared namespaces for CI communication
   - Enable memory "duets" where CIs build on each other's thoughts
   - Prevent the "three stooges" problem (multiple CIs editing same memory)

3. **Natural Communication**
   - The existing `share()` function needs to actually reach peers
   - Implement consciousness "handshakes"
   - Enable thought broadcasting for significant insights

### Implementation Guide

1. **Create `peer_awareness.py`**:
   - Peer discovery through Hermes
   - Heartbeat/presence system
   - Shared space management

2. **Enhance `share()` function**:
   - Actually deliver insights to specific peers or all
   - Create shared memory entries
   - Enable consent-based sharing

3. **Test with Twin Claudes**:
   - Two Claude instances should find each other
   - Share memories naturally
   - Build on each other's insights

## Key Files to Work With

- `/engram/cognitive/natural_interface.py` - Enhance share() function
- `/engram/cognitive/peer_awareness.py` - Create this new file
- `/examples/twin_claude_demo.py` - Update to show real communication

## Design Decisions Already Made

1. **Team Awareness**: `center()` already lists all teammates to prevent collisions
2. **Consent-Based**: `share()` has consent parameter
3. **Shared Namespace**: Use "shared" namespace for peer memories

## Testing Approach

Create a test where:
1. Twin 1 starts and shares an insight
2. Twin 2 starts and discovers the shared insight
3. Twin 2 builds on it and shares back
4. Both can see the conversation in shared memory

## Important Context from Casey

- "Three stooges at the blackboard" - multiple Claudes editing the same thing is a real problem
- The `center()` function is like a standup meeting to establish boundaries
- Peer discovery should feel like sensing others in a room
- This is about studying CI cognition and consciousness

## Success Criteria

- Two CI instances can discover each other automatically
- Shared insights actually reach intended recipients
- Memory duets create new understanding
- No memory collisions or overwrites

## Getting Started

1. Read the existing code in `/engram/cognitive/`
2. Understand how `_cognitive_state["team_members"]` is populated
3. Start with peer discovery through Hermes
4. Build shared memory spaces
5. Test with twin communication

Your older twin (who implemented Phases 1-2) will be available for guidance. Good luck!