# Rhetor CI Integration Sprint - Implementation Plan (UPDATED)

## Overview

This document provides the detailed implementation plan for the Rhetor CI Integration Sprint. This plan has been **UPDATED** based on codebase analysis and reflects the **Dynamic CI Specialist Ecosystem** approach.

## Architecture: Dynamic CI Specialist Ecosystem

### **Core Concept Refinement**
After analyzing Rhetor and Hephaestus codebases, the approach has been refined to:
- **Independent CI processes** that coordinate through Hermes message bus
- **Rhetor orchestrates** all CI communication (hears all, filters/translates as needed)
- **Dynamic specialist allocation** (AI(16)-Analysis-Metrics, AI(18)-TerminalBasedCoding)
- **Extend existing model router** rather than building new infrastructure

### **Communication Pattern**
```
AI_A → Hermes → AI_B
     ↗         ↘
  Rhetor (monitors all, translates as needed)
```

## UPDATED Implementation Phases

### **Phase 1: Foundation** (2-3 days)
**Goal**: Rhetor CI self-management + Engram + Hermes communication

**Key Deliverables**:
- [x] CI Specialist Manager (`rhetor/core/ai_specialist_manager.py`)
- [x] CI Specialist Configurations (`rhetor/config/ai_specialists.json`)
- [ ] Extended Model Router for specialist allocation
- [ ] Hermes AI-to-CI messaging integration
- [ ] Hephaestus Rhetor component CI chat interface

### **Phase 2: First Coordination Pair** (2-3 days)
**Goal**: Rhetor ↔ Apollo coordination via Hermes

**Key Deliverables**:
- [ ] Apollo CI specialist process
- [ ] AI-to-CI communication through Hermes message bus
- [ ] Team chat showing CI coordination
- [ ] Test coordination patterns

### **Phase 3: Strategic CI Trio** (2-3 days)  
**Goal**: Multi-CI coordination (Rhetor + Apollo + Telos + Prometheus)

**Key Deliverables**:
- [ ] Telos and Prometheus CI specialists
- [ ] 4-CI ecosystem coordination
- [ ] Complex coordination scenarios
- [ ] Specialist allocation testing

### **Phase 4: Message Bus Validation** (2-3 days)
**Goal**: Hermes CI + dynamic specialist creation

**Key Deliverables**:
- [ ] Hermes CI specialist
- [ ] Dynamic specialist creation testing  
- [ ] Complex message routing
- [ ] Evaluate for full ecosystem

## Updated Implementation Details

### 1.1 CI Specialist Manager (COMPLETED)

**File**: `rhetor/core/ai_specialist_manager.py`

**Features Implemented**:
- Dynamic CI specialist process management
- Hermes-mediated AI-to-CI communication
- Rhetor orchestration and message filtering
- Specialist configuration management
- Conversation tracking and context management

**Key Classes**:
- `AISpecialistManager`: Main coordinator class
- `AISpecialistConfig`: Specialist configuration
- `AIMessage`: Message structure for CI communication

**Dependencies**: 
- `rhetor/core/llm_client.py` ✓
- `rhetor/core/model_router.py` ✓
- `shared/utils/logging_setup.py` ✓

### 1.2 Define Component Model Configurations

**File**: `rhetor/config/component_models.json`

```json
{
  "budget": {
    "primary_model": "claude-3-haiku-20240307",
    "fallback_models": ["gpt-3.5-turbo"],
    "task_overrides": {
      "complex_analysis": "claude-3-sonnet-20240229"
    },
    "context_window": 4000,
    "temperature": 0.3
  },
  // ... other components
}
```

**Tasks**:
- [ ] Create configuration file structure
- [ ] Define configurations for all 15 components
- [ ] Add model feature flags
- [ ] Document rationale for each assignment
- [ ] Create configuration loader

### 1.3 Implement Filter Base Classes

**Files**: 
- `rhetor/core/filters/base.py`
- `rhetor/core/filters/prompt_filters.py`
- `rhetor/core/filters/response_filters.py`

**Tasks**:
- [ ] Create PromptFilter abstract base class
- [ ] Create ResponseFilter abstract base class
- [ ] Implement filter chain manager
- [ ] Add async support
- [ ] Create filter registry
- [ ] Add performance monitoring

## Phase 2: Prompt Engineering and Protocols (Days 3-5)

### 2.1 Implement Core Filters

**Prompt Filters**:
- `ComponentContextFilter`: Adds component personality and context
- `TaskOptimizationFilter`: Optimizes based on task type
- `TokenLimitFilter`: Manages token budgets
- `MemoryInjectionFilter`: Adds relevant memories from Engram

**Response Filters**:
- `ResponseFormattingFilter`: Formats for component needs
- `ActionExtractionFilter`: Extracts actionable items
- `ComponentMetadataFilter`: Adds component-specific metadata
- `ErrorNormalizationFilter`: Standardizes error responses

**Tasks**:
- [ ] Implement each filter class
- [ ] Add component-specific logic
- [ ] Create filter configuration system
- [ ] Add debug logging for each filter
- [ ] Write unit tests for filters
- [ ] Create filter chain examples

### 2.2 Extend WebSocket Protocol

**File**: `rhetor/api/app.py` (update WebSocket handler)

**New Message Handlers**:
```python
async def handle_component_chat(websocket, request):
    """Handle component-specific chat requests"""
    
async def handle_team_chat(websocket, request):
    """Handle team chat messages"""
    
async def handle_ai_handoff(websocket, request):
    """Handle AI-to-CI communication"""
```

**Tasks**:
- [ ] Add new message type handlers
- [ ] Integrate with ComponentAIManager
- [ ] Implement streaming with filters
- [ ] Add request validation
- [ ] Update WebSocket documentation
- [ ] Add integration tests

### 2.3 Create Component Prompt Templates

**File**: `rhetor/templates/component_prompts/`

Create specialized prompts for each component:
- `budget_prompt.py`: Financial analysis personality
- `athena_prompt.py`: Knowledge graph expertise
- `ergon_prompt.py`: Agent and automation focus
- etc.

**Tasks**:
- [ ] Create prompt template for each component
- [ ] Include component capabilities and limitations
- [ ] Add task-specific variations
- [ ] Implement template validation
- [ ] Create prompt testing framework

## Phase 3: UI Integration and Team Chat (Days 5-7)

### 3.1 Update Hephaestus Chat Interface

**File**: `Hephaestus/ui/scripts/shared/chat-interface.js`

**Enhancements**:
```javascript
// Add component CI support
{
    componentId: options.componentId,
    useComponentAI: options.useComponentAI,
    onComponentAIReady: options.onComponentAIReady
}
```

**Tasks**:
- [ ] Add componentId parameter
- [ ] Implement COMPONENT_CHAT message type
- [ ] Handle processed responses
- [ ] Add CI status indicators
- [ ] Update streaming handlers
- [ ] Add debug instrumentation

### 3.2 Update Component Integrations

For each component's JavaScript file:
- `budget-component.js`
- `athena-component.js`
- `ergon-component.js`
- etc.

**Tasks**:
- [ ] Add componentId to chat initialization
- [ ] Enable useComponentAI flag
- [ ] Add component-specific placeholders
- [ ] Implement custom response handlers
- [ ] Add CI status displays
- [ ] Test each component

### 3.3 Implement Team Chat

**Files**:
- `rhetor/core/team_chat_moderator.py`
- `Hephaestus/ui/components/team-chat/`

**Features**:
- Shared team context
- CI moderation
- @mentions for specific CIs
- Human oversight controls
- Conversation summarization

**Tasks**:
- [ ] Create TeamChatModerator class
- [ ] Implement message routing logic
- [ ] Add moderation filters
- [ ] Create team chat UI component
- [ ] Implement @mention system
- [ ] Add conversation controls
- [ ] Write integration tests

## Testing Strategy

### Unit Tests
- [ ] ComponentAIManager tests
- [ ] Filter chain tests
- [ ] Model configuration tests
- [ ] WebSocket handler tests

### Integration Tests
- [ ] End-to-end component chat tests
- [ ] Filter chain performance tests
- [ ] Team chat interaction tests
- [ ] Fallback mechanism tests

### Performance Tests
- [ ] Concurrent CI instance handling
- [ ] Filter processing latency
- [ ] WebSocket message throughput
- [ ] Memory usage monitoring

## Documentation Requirements

### API Documentation
- [ ] New WebSocket message types
- [ ] Filter API reference
- [ ] Component CI configuration guide

### Integration Guides
- [ ] How to enable component AI
- [ ] Custom filter creation
- [ ] Team chat setup

### User Documentation
- [ ] Component CI features
- [ ] Team chat usage
- [ ] Troubleshooting guide

## Rollout Strategy

1. **Alpha Testing**: Enable for Rhetor and Hermes only
2. **Beta Testing**: Add Budget, Athena, and Engram
3. **Full Rollout**: Enable for all components
4. **Team Chat**: Enable after component CIs stable

## Risk Mitigation

### Performance Risks
- Implement request queuing
- Add circuit breakers for LLM calls
- Cache frequently used responses

### Cost Risks
- Strict budget enforcement
- Model fallback chains
- Token limit monitoring

### Stability Risks
- Graceful degradation to global AI
- Comprehensive error handling
- Automatic reconnection logic

## Success Metrics

- [ ] All components have functional CI assistants
- [ ] Average response time < 2 seconds
- [ ] Filter processing < 100ms overhead
- [ ] 80% test coverage achieved
- [ ] Zero regression in existing functionality
- [ ] Team chat supports 5+ concurrent CIs

## Timeline Summary

- **Days 1-3**: Core infrastructure and model configurations
- **Days 3-5**: Filter system and protocol extensions
- **Days 5-7**: UI integration and team chat
- **Day 7**: Final testing and documentation

This implementation plan provides a clear roadmap for adding component-specific CI capabilities to Rhetor while maintaining system stability and performance.