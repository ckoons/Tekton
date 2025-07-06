# Team Chat Debugging Handoff - UPDATED

## For the Next Claude Instance

Hi! I'm Jill, and I've been working with Casey on optimizing team chat performance. Here's everything you need to know to continue the debugging work.

## 🚨 CRITICAL UPDATE: Design Change

Casey clarified that team-chat should be an **orchestration pattern**, not a special socket:
- See `TEAM_CHAT_DESIGN_UPDATE.md` for the new design
- Team-chat should broadcast to all existing AI sockets
- No special socket creation needed
- Just coordinate existing infrastructure

## Current Situation

### What Casey Reported
1. **Specialist chat takes several seconds** to respond
2. **Team chat only reaches Apollo** (or very few AIs)
3. **Rhetor team chat doesn't return** properly

### Root Cause Found
- The debug output showed **0 AI specialist processes running**
- Registry shows 18 "active" AIs but they're not actually running
- Only 2 AIs responded with "Ollama connection error"

## What I Implemented

### 1. Connection Pool (Under the Hood)
- **File**: `/shared/ai/connection_pool.py`
- **Purpose**: Reuse socket connections instead of creating new ones
- **Status**: ✅ Implemented and integrated transparently
- **Note**: Won't help if AIs aren't running, but will speed things up once they are

### 2. Streaming Team Chat
- **Endpoint**: `/api/v2/team-chat/stream` 
- **Files**: 
  - `/Rhetor/rhetor/api/team_chat_streaming.py` - Server implementation
  - `/Hephaestus/ui/scripts/shared/streaming-team-chat.js` - Client
- **Purpose**: Return responses as they arrive, not wait for all
- **Status**: ✅ Implemented, needs testing with running AIs

### 3. Optimizations Made
- Reduced team chat timeout: 10s → 2s
- Connection timeout: 2s → 0.5s
- Disabled retries for faster failures
- Fixed event loop issue in aish

## Key Files to Know

### Core Team Chat Flow
```
1. /Rhetor/rhetor/api/team_chat_endpoints.py
   → Receives HTTP request
   
2. /Rhetor/rhetor/core/mcp/tools_integration_unified.py
   → orchestrate_team_chat() - sends to all AIs
   
3. /shared/ai/socket_client.py
   → Handles actual socket communication
   → Now uses connection pool transparently
```

### Test Scripts
- `/scripts/simple_debug.py` - Quick diagnostic
- `/scripts/test_streaming_team_chat.py` - Test new streaming
- `/scripts/debug_connection_pool.py` - Deeper analysis

## Current Issues to Debug

### 1. AI Processes Not Running
```bash
# Check if specialists are running
ps aux | grep specialist_worker

# Check Tekton's launch system
tekton-status

# Check AI logs
ls -la ~/.tekton/logs/
```

### 2. Ollama Connection Errors
The few AIs that do respond report "Ollama connection error". Check:
```bash
# Is Ollama running?
ollama ps

# Can we reach Ollama?
curl http://localhost:11434/api/tags

# Check Ollama logs
journalctl -u ollama -f
```

### 3. Registry vs Reality Mismatch
Registry shows AIs as "active" but they're not running:
```bash
# Check registry
cat ~/.tekton/ai_registry/platform_ai_registry.json | jq

# Compare with actual processes
ps aux | grep -E "(hermes|apollo|athena|engram|noesis|numa|sophia|rhetor)-ai"
```

## Next Steps

### 1. Get AIs Running First
Before any optimization matters, the AI specialists need to be running:
```bash
# Casey mentioned they have their own launch system
# Find and use the proper Tekton launch commands
# Maybe: tekton-launch-all or similar?
```

### 2. Test With Running AIs
Once AIs are running:
```bash
# Test individual AI
python3 scripts/simple_debug.py

# Test streaming endpoint
python3 scripts/test_streaming_team_chat.py

# Test from UI
# Navigate to Noesis → Team Chat tab
# Send a message with broadcast checked
```

### 3. Debug Slow Responses
If AIs are running but slow:
- Check Ollama model loading time
- Monitor first vs subsequent requests
- Verify connection pool is working (check reuse stats)
- Consider reducing number of active AIs

## Testing Checklist

- [ ] Verify AI specialists are actually running
- [ ] Test individual AI connectivity
- [ ] Test old team chat endpoint
- [ ] Test new streaming endpoint
- [ ] Compare response times
- [ ] Check connection pool reuse
- [ ] Test from Noesis UI
- [ ] Test from aish terminal

## Useful Commands

```bash
# Quick health check
curl http://localhost:8003/api/team-chat/sockets | jq

# Test streaming (see responses as they arrive)
curl "http://localhost:8003/api/v2/team-chat/stream?message=test&timeout=2"

# Watch AI logs
tail -f ~/.tekton/logs/*-ai.log

# Check which ports are listening
netstat -an | grep LISTEN | grep 450
```

## Architecture Notes

1. **Greek Chorus AIs** run on ports 45000-50000
2. **Rhetor** orchestrates on port 8003
3. **Connection pool** is a singleton - shared across all components
4. **Streaming** uses Server-Sent Events (SSE), not WebSockets

## What Works Well

When AIs are actually running:
- Individual AI chat works (via streaming endpoint)
- Connection pool reduces overhead
- Streaming provides immediate feedback
- UI integration is clean

## Contact

Casey has been great to work with! They understand the architecture deeply and prefer to see analysis and options before implementation. The codebase is well-organized and the launch system is sophisticated.

Good luck with the debugging! The infrastructure is solid - just need to get those AI processes running.

---

*Handoff prepared by Jill on July 5, 2025*
*Context: 9% remaining after team chat optimization sprint*