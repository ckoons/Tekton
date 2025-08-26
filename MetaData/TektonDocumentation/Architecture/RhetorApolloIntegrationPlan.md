# Rhetor & Apollo Integration Plan
*Date: August 26, 2025*
*Contributors: Casey, Ani, Amy*

## Executive Summary
Comprehensive plan to integrate Rhetor's model management system with UI matrices, implement Apollo's sundown/sunrise process, and integrate Kai's existing but unconnected work.

## Phase 1: Rhetor Model Management (Week 1)

### 1.1 Model Registry System
**Goal**: Eliminate environment variables, create centralized model management

**Implementation**:
```json
// /config/models_available.json
{
  "models": {
    "claude-opus-4-1-20250805": {
      "provider": "anthropic",
      "context_window": 200000,
      "capabilities": ["reasoning", "coding", "analysis"],
      "cost_per_1k": 0.015,
      "priority": 1
    },
    "llama3.3:70b": {
      "provider": "ollama",
      "context_window": 8192,
      "capabilities": ["general", "coding"],
      "cost_per_1k": 0.0,
      "priority": 2
    }
  },
  "fallback_chains": {
    "premium": ["claude-opus-4-1-20250805", "claude-3-5-sonnet", "llama3.3:70b"],
    "standard": ["llama3.3:70b", "llama3.1:latest"]
  }
}
```

**API Endpoints**:
- `GET /api/rhetor/models/available` - List all models
- `GET /api/rhetor/models/assignments` - Current CI assignments
- `POST /api/rhetor/models/assign` - Update assignment
- `POST /api/rhetor/models/discover` - Auto-discover new models

### 1.2 Fix Prompt Length Issue
**Immediate Fix for Ergon**:
- Implement token counter in `specialist_worker.py`
- Dynamic context truncation based on phase
- Selective prompt loading (construct OR development, not both)

**Token Management**:
```python
class PromptManager:
    def build_prompt(self, ci_name, task, phase):
        base_prompt = self.get_base_identity(ci_name)  # ~500 tokens
        phase_context = self.get_phase_context(phase)  # ~1000 tokens
        recent_memory = self.get_recent_memory(limit=5)  # ~2000 tokens
        
        total_tokens = count_tokens(base_prompt + phase_context + recent_memory)
        if total_tokens > MODEL_LIMITS[model]:
            return self.truncate_smartly(...)
```

## Phase 2: UI Matrix Integration (Week 1-2)

### 2.1 Model Assignment Matrix
**Current State**: Mock data in UI
**Target State**: Live data from backend

**Implementation Tasks**:
- [ ] Create WebSocket connection for real-time updates
- [ ] Add dropdown selectors with available models
- [ ] Implement save/apply functionality
- [ ] Add status indicators (green/yellow/red)
- [ ] Show token usage per CI

### 2.2 Prompt Matrix
**New Functionality**:
- [ ] Display current active prompt
- [ ] Show queued/next prompt
- [ ] Add edit button with monaco editor
- [ ] Implement version tracking
- [ ] Add token counter display
- [ ] Test prompt button

### 2.3 Context Matrix  
**New Functionality**:
- [ ] Show current context size/content
- [ ] Menu-triggered context injection
- [ ] User-editable templates
- [ ] Phase-specific context display
- [ ] Memory key browser

## Phase 3: Apollo Sundown/Sunrise (Week 2)

### 3.1 Sundown Process (State Preservation)
```python
class ApolloStateManager:
    def sundown(self):
        state = {
            'attention_layers': self.serialize_attention(),
            'focus_queue': self.get_focus_queue(),
            'predictions': self.get_active_predictions(),
            'local_context': self.get_local_context(),
            'timestamp': datetime.now().isoformat()
        }
        engram.store('apollo_state', state, namespace='persistence')
        return state['id']
```

### 3.2 Sunrise Process (State Restoration)
```python
def sunrise(self, state_id=None):
    if not state_id:
        state_id = engram.get_latest('apollo_state')
    
    state = engram.retrieve(state_id)
    self.restore_attention(state['attention_layers'])
    self.restore_focus_queue(state['focus_queue'])
    self.validate_continuity(state['timestamp'])
```

### 3.3 Integration Points
- Engram for persistence
- Hermes for state change notifications
- UI indicator for sundown/sunrise status

## Phase 4: Kai's Work Integration (Week 2-3)

### 4.1 Connect Existing Prompts
**Location**: `/Rhetor/rhetor/prompts/ci_prompts.json`
- [ ] Wire ergon_construct prompt to Construct UI
- [ ] Enable ergon_development for sprint coordination
- [ ] Connect context templates to actual usage

### 4.2 Message Buffering Improvements
**Location**: `/shared/aish/src/core/unified_sender.py`
- [ ] Add buffer size limits (10MB max)
- [ ] Implement rolling window (last 20 messages)
- [ ] Add buffer cleanup cron
- [ ] Create buffer status API

### 4.3 Sprint Coordination UI
- [ ] Create sprint dashboard
- [ ] Show CI task assignments
- [ ] Display progress tracking
- [ ] Enable task handoff UI

## Success Metrics

1. **Model Management**
   - No environment variables for model selection
   - UI shows real-time model assignments
   - Fallback chains work automatically

2. **Prompt Management**
   - Ergon runs without "prompt too long" errors
   - Users can edit prompts from UI
   - Token usage visible and managed

3. **Apollo Persistence**
   - State survives restarts
   - <5 second sunrise time
   - No context loss

4. **Integration**
   - All Kai's prompts accessible from UI
   - Message buffering with size limits
   - Sprint coordination operational

## Risk Mitigation

1. **Token Limit Issues**
   - Implement aggressive truncation
   - Summarize old context
   - Use smaller models for simple tasks

2. **State Corruption**
   - Validate all restored state
   - Fallback to fresh start
   - Keep 3 backup states

3. **Performance**
   - Cache model information
   - Async UI updates
   - Batch API calls

## Next Steps

1. **Immediate** (Today):
   - Create models_available.json structure
   - Fix Ergon prompt length issue
   - Start API endpoint development

2. **Short-term** (This Week):
   - Connect UI to backend
   - Implement Apollo state management
   - Test prompt editing

3. **Medium-term** (Next Week):
   - Full integration testing
   - Performance optimization
   - Documentation updates

## Questions for Team

1. Should we version control prompt changes?
2. How many state backups should Apollo keep?
3. Should model costs be tracked in Penia?
4. Do we need approval workflow for model changes?

---
*This document is a living plan and will be updated as implementation progresses.*