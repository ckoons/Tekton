# Tekton-aish Continuation Sprint Plan

## Timeline: 7 Days

### Day 1-2: SSE Implementation
**Goal**: Add Server-Sent Events streaming to Rhetor

#### Tasks:
1. Create SSE endpoint handler in Rhetor
2. Implement `/api/chat/{specialist_id}/stream` endpoint
3. Add Ollama streaming integration
4. Test with curl and simple clients

#### Key Files:
- `Rhetor/rhetor/api/streaming.py` (new)
- `Rhetor/rhetor/core/specialist_manager.py` (update)
- `shared/ai/specialist_worker.py` (add streaming)

### Day 3-4: Team Chat Fix
**Goal**: Fix team chat broadcast issue

#### Tasks:
1. Debug message routing in team chat
2. Verify Greek Chorus CI registration
3. Fix response collection timeout
4. Add comprehensive logging

#### Key Files:
- `Rhetor/rhetor/api/routes.py` (team-chat endpoint)
- `shared/ai/registry_client.py`
- `scripts/ai-discover` (verify discovery)

### Day 5: MCP Tools Completion
**Goal**: Implement remaining MCP methods

#### Tasks:
1. Implement `GetSpecialistConversationHistory`
   - Connect to Engram service
   - Define conversation format
2. Implement `ConfigureOrchestration`
   - Define configuration schema
   - Add routing rules support
3. Add streaming to `SendMessageToSpecialist`

#### Key Files:
- `Rhetor/rhetor/core/mcp/tools_integration_unified.py`
- `Engram/engram/api/conversations.py` (if needed)

### Day 6: Pipeline Context Support
**Goal**: Enable context passing between CIs

#### Tasks:
1. Add context parameter to specialist requests
2. Implement memory hint protocol
3. Test with multi-stage pipelines
4. Document context format

#### Key Files:
- `shared/ai/specialist_worker.py`
- `Rhetor/rhetor/core/message_handler.py`

### Day 7: Integration & Testing
**Goal**: Ensure everything works together

#### Tasks:
1. End-to-end streaming tests
2. Team chat integration test
3. Pipeline context test
4. Update documentation
5. Performance benchmarking

## Definition of Done

- [ ] SSE endpoints return `text/event-stream` content
- [ ] Team chat shows responses from multiple CIs
- [ ] All MCP methods implemented (no NotImplementedError)
- [ ] Context successfully passes through pipelines
- [ ] Tests cover all new functionality
- [ ] Documentation updated

## Risk Mitigation

1. **Ollama Streaming**: May need custom integration
2. **Socket Buffering**: SSE may conflict with current buffering
3. **Engram Integration**: May need schema updates
4. **Performance**: Streaming adds overhead

## Notes for Next Sprint

Document any issues or improvements discovered during implementation for the aish Phase 4 sprint.