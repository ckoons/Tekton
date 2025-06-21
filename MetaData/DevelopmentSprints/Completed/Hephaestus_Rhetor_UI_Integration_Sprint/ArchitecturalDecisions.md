# Hephaestus-Rhetor UI Integration - Architectural Decisions

## Overview

This document captures the key architectural decisions made for the Hephaestus-Rhetor UI Integration Sprint. These decisions guide the implementation and ensure consistency with Tekton's overall architecture.

## Decision Log

### AD-001: Component-Specialist Mapping Strategy

**Status**: Accepted  
**Date**: 2025-01-06

**Context**: Each Tekton component needs its own AI assistant, but we need to decide how to create and manage these specialists.

**Decision**: Use pre-configured specialists with dynamic creation/recreation capabilities. Specialists follow the naming convention `{component_id}-assistant`.

**Rationale**:
- Pre-configuration ensures consistent behavior
- Dynamic recreation allows for requirement changes
- Clear naming convention prevents conflicts

**Consequences**:
- Need specialist configuration registry
- Must implement lifecycle management
- Requires startup initialization logic

### AD-002: Chat UI Design Preservation

**Status**: Accepted  
**Date**: 2025-01-06

**Context**: Hephaestus has an existing chat UI with bubble-style messages. Rhetor has its own advanced chat interface.

**Decision**: Keep the existing Hephaestus bubble-style chat UI for consistency across components.

**Rationale**:
- Maintains UI consistency
- Reduces implementation complexity
- Users already familiar with the interface

**Consequences**:
- No need to port Rhetor's UI
- Focus on backend integration
- May limit some advanced features

### AD-003: Model Selection Strategy

**Status**: Accepted  
**Date**: 2025-01-06

**Context**: Different components have different AI requirements (speed vs. capability).

**Decision**: Assign specific models to each component based on their primary use case, with Ollama fallbacks.

**Rationale**:
- Optimizes cost and performance
- Provides local alternatives
- Allows fine-tuning per component

**Model Assignments**:
- Fast queries: Claude Haiku (athena-assistant)
- Analysis: GPT-4 (budget-assistant, apollo-assistant)
- Complex reasoning: Claude Opus (rhetor-orchestrator, prometheus-assistant)
- Code tasks: Specialized Ollama models (codestral, qwen2.5-coder)

### AD-004: Chat Persistence Approach

**Status**: Accepted  
**Date**: 2025-01-06

**Context**: Users may want to preserve chat histories across sessions, but not always.

**Decision**: Implement component-level SAVE_CHAT_HISTORY setting with localStorage persistence.

**Rationale**:
- Gives users control
- Simple implementation
- No backend storage required

**Implementation**:
- Global default in .env.tekton
- Component override in settings
- localStorage with size limits

### AD-005: Menu Bar Scope

**Status**: Accepted  
**Date**: 2025-01-06

**Context**: The Rhetor menu bar component could expose varying levels of functionality.

**Decision**: When Rhetor is selected in menu, it controls the entire area between header and chat input.

**Rationale**:
- Maximum flexibility for Rhetor UI
- Clear user experience
- Allows full feature access

**Consequences**:
- Need to handle UI state transitions
- Must preserve chat context
- Requires careful event handling

### AD-006: Message Routing Architecture

**Status**: Accepted  
**Date**: 2025-01-06

**Context**: AI messages need to be routed to the correct component chat interface.

**Decision**: Use Hermes message bus with topic pattern `ai.chat.{component_id}`.

**Rationale**:
- Leverages existing infrastructure
- Scalable pattern
- Supports future enhancements

**Implementation**:
- WebSocket messages include component context
- Hermes routes based on topic
- Components subscribe to their topics

### AD-007: Streaming Implementation

**Status**: Accepted  
**Date**: 2025-01-06

**Context**: Real-time AI responses improve user experience but add complexity.

**Decision**: Use existing SSE endpoint with WebSocket fallback for streaming.

**Rationale**:
- SSE already implemented in Rhetor
- WebSocket provides bidirectional backup
- Graceful degradation supported

**Technical Details**:
- Primary: `/api/mcp/v2/stream` SSE endpoint
- Fallback: WebSocket with chunked messages
- UI: Typing indicators during streaming

### AD-008: Component Registration Enhancement

**Status**: Accepted  
**Date**: 2025-01-06

**Context**: Components need to declare their AI assistant requirements.

**Decision**: Extend component registry with AI configuration.

**Rationale**:
- Centralized configuration
- Declarative approach
- Easy to modify

**Schema Addition**:
```json
{
  "ai_config": {
    "specialist_id": "athena-assistant",
    "model_preference": "claude-3-haiku",
    "ollama_fallback": "qwen2.5-coder:7b",
    "system_prompt": "You are Athena's knowledge assistant..."
  }
}
```

### AD-009: Error Handling Strategy

**Status**: Accepted  
**Date**: 2025-01-06

**Context**: AI services can fail, and we need graceful degradation.

**Decision**: Implement fallback chain: Primary Model → Ollama Model → Error Message.

**Rationale**:
- Maximizes availability
- Clear user feedback
- Supports offline work

**Implementation**:
- Try primary model first
- Fall back to Ollama if available
- Show clear error with retry option

### AD-010: Cross-Component Communication

**Status**: Accepted  
**Date**: 2025-01-06

**Context**: This sprint focuses on component-to-specialist communication, not specialist-to-specialist across components.

**Decision**: Defer cross-component AI communication to future A2A work.

**Rationale**:
- Reduces scope complexity
- A2A protocol better suited for this
- Allows focused implementation

**Consequences**:
- Specialists work within component context
- No automatic context sharing between components
- Manual coordination still possible through Rhetor

## Implementation Guidelines

1. **Consistency**: All implementations must follow these architectural decisions
2. **Documentation**: Update component docs when adding AI capabilities
3. **Testing**: Include tests for fallback scenarios
4. **Monitoring**: Log model usage for optimization
5. **Security**: Never expose API keys in frontend code

## Future Considerations

- **Phase 2**: Cross-component AI orchestration via A2A
- **Enhancement**: Shared context between related components
- **Optimization**: Model performance monitoring and auto-selection
- **Scale**: Multi-user chat session management