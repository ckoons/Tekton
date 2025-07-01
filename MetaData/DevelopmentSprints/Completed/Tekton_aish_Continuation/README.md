# Tekton-aish Continuation Sprint

## Overview

This sprint implements Tekton-side features needed for aish Phase 3 and 4, focusing on streaming support, team chat fixes, and MCP tools completion.

## Sprint Goals

1. **Add SSE Streaming to Rhetor** - Enable progressive AI responses
2. **Fix Team Chat** - Resolve "No responses yet" issue
3. **Complete MCP Tools** - Implement remaining NotImplementedError methods
4. **Pipeline Context Support** - Enable memory passing between AIs

## Success Criteria

- [ ] SSE endpoints working with progressive token streaming
- [ ] Team chat successfully broadcasts to all AIs
- [ ] MCP tools fully implemented
- [ ] Context can be passed between pipeline stages
- [ ] All tests passing

## Duration

7 days (Tekton-side work)

## Key Deliverables

### 1. SSE Endpoints
- `/api/chat/{specialist_id}/stream` - Stream individual AI responses
- `/api/team-chat/stream` - Stream team chat responses
- Progressive token delivery from Ollama

### 2. Team Chat Fix
- Debug message routing to Greek Chorus AIs
- Fix response collection mechanism
- Add proper timeout handling

### 3. MCP Tools
- `GetSpecialistConversationHistory` - Integrate with Engram
- `ConfigureOrchestration` - Dynamic routing rules
- Streaming support in `SendMessageToSpecialist`

### 4. Pipeline Support
- Context parameter in AI requests
- Memory hints for continuity
- State passing between specialists

## Technical Context

- Greek Chorus AIs: Ports 45000+ (socket-based)
- Rhetor API: Port 8003 (HTTP/REST)
- MCP Tools: `Rhetor/rhetor/core/mcp/tools_integration_unified.py`
- Current issue: Team chat not reaching specialists

## Dependencies

- Ollama with streaming support
- Engram service for history storage
- All Greek Chorus AIs running

## Next Sprint

After this Tekton work is complete, return to aish for Phase 4 client-side streaming implementation.