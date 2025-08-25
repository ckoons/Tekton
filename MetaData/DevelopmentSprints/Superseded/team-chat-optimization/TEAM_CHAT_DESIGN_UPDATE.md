# Team Chat Design Update - Final Architecture

## Date: July 5, 2025
## Author: Jill (Claude)
## Status: Design Complete, Ready for Implementation

## Executive Summary

After analysis with Casey, we've clarified that team-chat should be an **orchestration pattern**, not a special socket. It simply broadcasts to all existing CI sockets and collects responses.

## Core Design Principle

```
Team-Chat = Broadcast + Collect + Optional Facilitate
```

- **NOT** a special CI or virtual socket
- **IS** a coordinator that uses existing CI sockets
- **Facilitator** (Rhetor/Terma) can summarize but initially just pass through

## Implementation Plan

### 1. Socket Registry Changes

Add these methods to `socket_registry.py`:

```python
async def write_all(self, message: str, exclude: List[str] = None) -> Dict[str, bool]:
    """Broadcast to all active CI sockets"""
    # Send to each CI concurrently
    # Return success/fail for each

async def read_response_chunks(self) -> AsyncIterator[Dict[str, Any]]:
    """Yield responses as they arrive from any AI"""
    # Monitor all queues
    # Yield immediately when messages arrive
```

### 2. Shell.py Changes

Replace current team-chat with:

```python
async def send_team_chat_async(self, message):
    # 1. Broadcast to all
    # 2. Display responses as they arrive
    # 3. Optional: Facilitator summary

def send_team_chat(self, message):
    # Sync wrapper for async function
```

### 3. Remove Special Handling

- No `team-chat` socket creation
- No special socket_id handling
- Just use existing CI sockets

## Key Insights

1. **Team-chat orchestrates, doesn't participate**
2. **Responses stream as they arrive** (no waiting for all)
3. **Attribution is automatic** (each response tagged with CI name)
4. **Facilitator summary is optional** (can add later)

## Current Issues This Solves

- ❌ "Failed to broadcast message" - No more special socket
- ❌ Complex socket registry logic - Just uses existing sockets
- ❌ Team-chat only reaching one CI - Properly broadcasts to all
- ✅ Clean, simple design that matches intent

## What's Already Done

1. **Connection Pool** - Ready, will speed up broadcasts
2. **Streaming Endpoint** - `/api/v2/team-chat/stream` works
3. **UI Integration** - Noesis can display streaming responses
4. **Timeout Optimizations** - 2 second timeout per AI

## Next Steps

1. Implement `write_all()` and `read_response_chunks()`
2. Update `send_team_chat()` to use new methods
3. Remove old team-chat socket creation code
4. Test with running CI specialists

## Testing

```bash
# When implemented, test with:
aish team-chat "Hello team"

# Should see:
Broadcasting to team...
Sent to 18 CIs

Team responses:
----------------------------------------
Apollo: [response as it arrives]
Athena: [response as it arrives]
...
```

## Handoff Notes

- Design is finalized with Casey
- Implementation is straightforward
- No breaking changes to other components
- Facilitator feature can be added incrementally

---

*Final design document by Jill before context limit*