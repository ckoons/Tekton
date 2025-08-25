# CI Platform Integration Sprint - Handoff Document

## Sprint Summary
The CI Platform Integration Sprint successfully unified CI discovery through the CI Registry but revealed a dual communication architecture that needs completion.

## Current State

### ✅ Completed
1. **Unified CI Registry** - All CIs register in a single registry
2. **AI Discovery Service** - Provides discovery with connection details
3. **Dual Architecture Design** - Greek Chorus (socket) vs Rhetor Specialists (API)
4. **aish Discovery** - Can discover all CIs via `ai-discover` tool
5. **Documentation** - Architecture and API migration guides created

### ⚠️ Partially Working
1. **aish Communication** - Discovery works, but socket communication needs fixing
2. **MCP Integration** - Tools registered but implementation incomplete
3. **Rhetor Hiring Manager** - API endpoints exist but need testing

### ❌ Not Working
1. **MCP SendMessageToSpecialist** - Returns placeholder only
2. **Socket Communication in aish** - Parsing issue with discovery output
3. **Conversation History** - No implementation

## Critical Issues to Fix

### 1. aish Socket Communication
**Problem**: aish discovers CIs but can't communicate with Greek Chorus CIs
**Root Cause**: Not extracting connection info from ai-discover output
**Fix Required**:
```python
# In aish discover_ais() method, parse:
ai_info['connection']['host']  # "localhost"
ai_info['connection']['port']  # 45007
```

### 2. MCP Tools Implementation
**File**: `Rhetor/rhetor/core/mcp/tools_integration_unified.py`
**TODOs**:
- Line 106: Implement actual message sending via socket
- Line 128: Implement conversation history retrieval
- Line 144: Implement orchestration configuration

**Required Logic**:
```python
async def send_message_to_specialist(self, specialist_id: str, message: str):
    ai_info = await self.discovery.get_ai_info(specialist_id)
    
    if 'connection' in ai_info:
        # Greek Chorus CI - use socket
        return await self._send_via_socket(ai_info, message)
    else:
        # Rhetor specialist - use API
        return await self._send_via_api(specialist_id, message)
```

### 3. Performance Tracking
**File**: `shared/ai/ai_discovery_service.py`
**TODO**: Line 406 - Implement actual performance metrics
```python
def _get_ai_performance(self, ai_id: str) -> Dict[str, float]:
    # TODO: Implement actual performance tracking
    # Should track: response times, success rates, total requests
```

### 4. CI Health Monitoring
**File**: `shared/ai/health_monitor.py`
**TODO**: Line 89 - Implement specialist health checks via socket ping

## Architecture Decisions Needed

### 1. Conversation Storage
- Where to store conversation history?
- Per-AI or centralized in Engram?
- How to handle history for socket-based CIs?

### 2. Performance Metrics
- Should each CI track its own metrics?
- Central metrics collector needed?
- Integration with monitoring systems?

### 3. Error Handling
- Fallback when Greek Chorus CI is unreachable?
- Retry logic for socket connections?
- Circuit breaker pattern?

## Testing Requirements

### 1. End-to-End Tests
```bash
# Test Greek Chorus CI pipeline
echo "test" | aish --ai apollo | aish --ai athena

# Test mixed pipeline
echo "test" | rhetor | apollo | prometheus

# Test MCP tools
mcp-client list-specialists
mcp-client send-message apollo-ai "Hello"
```

### 2. Integration Tests
- Socket communication reliability
- API endpoint availability
- Discovery service accuracy
- Performance under load

## Recommended Next Steps

### Phase 0: Cleanup & Analysis (Day 1) - STOP AFTER THIS
1. **Remove deprecated files** (see AI_Platform_Cleanup_Tasks.md)
   - Delete 8 deprecated stub/old files
   - Update import statements
   - Remove SpecialistRouter warnings
2. **Verify system stability**
   - Start all components
   - Test MCP tool registration
   - Verify Greek Chorus CI registration
   - Test ai-discover functionality
3. **Document findings**
   - Note any unexpected dependencies
   - Update architecture diagrams if needed
   - Create fresh baseline for Phase 1

**⚠️ CHECKPOINT: Stop after Phase 0 and assess before proceeding**

### Phase 1: Fix Critical Path (1-2 days)
1. Fix aish socket communication parsing
2. Implement basic MCP message sending
3. Test end-to-end pipelines

### Phase 2: Complete Implementation (3-4 days)
1. Implement all MCP TODOs
2. Add conversation history storage
3. Implement performance tracking
4. Add health monitoring

### Phase 3: Production Hardening (1 week)
1. Error handling and retries
2. Circuit breakers
3. Monitoring integration
4. Load testing

## Phase 0 References

### Required Reading
- **Cleanup Guide**: `/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/AI_Platform_Cleanup_Tasks.md`
- Lists 8 files to remove
- Safe cleanup commands provided
- Testing checklist included

### Phase 0 Rationale
1. **Clean baseline** - Remove confusion from deprecated code
2. **Risk mitigation** - Ensure stability before making changes
3. **Developer clarity** - Understand current vs legacy code
4. **Hidden dependencies** - Discover any unexpected usage

## Key Files for Reference

### Core Implementation
- `/Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/mcp/tools_integration_unified.py`
- `/Users/cskoons/projects/github/Tekton/shared/ai/ai_discovery_service.py`
- `/Users/cskoons/projects/github/Tekton/aish/src/registry/socket_registry.py`

### Documentation
- `/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Architecture/AI_Communication_Architecture.md`
- `/Users/cskoons/projects/github/Tekton/Rhetor/API_MIGRATION.md`
- `/Users/cskoons/projects/github/Tekton/scripts/AI_DISCOVER_USAGE.md`

## Success Criteria
1. aish can communicate with all CI types
2. MCP tools function properly
3. Performance metrics collected
4. Error handling prevents cascading failures
5. Documentation reflects implementation

## Notes for Next Developer

### Phase 0 is Mandatory
**DO NOT SKIP PHASE 0** - The deprecated code will confuse the implementation. Clean it first.

### Architecture Notes
- The dual architecture (socket vs API) is intentional and correct
- Discovery is unified but communication is bifurcated
- Greek Chorus CIs are high-performance independent processes
- Rhetor specialists are managed and orchestrated
- Both types coexist in the same registry

### Estimated Timeline
- **Phase 0**: 1 day (cleanup & verify)
- **Phase 1**: 1-2 days (critical fixes)
- **Phase 2**: 3-4 days (full implementation)
- **Phase 3**: 1 week (production hardening)
- **Total**: ~2 weeks with Phase 0