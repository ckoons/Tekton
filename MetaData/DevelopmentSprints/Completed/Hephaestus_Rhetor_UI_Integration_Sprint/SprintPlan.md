# Hephaestus-Rhetor UI Integration Sprint - Sprint Plan

## Overview

This document outlines the high-level plan for the Hephaestus-Rhetor UI Integration Development Sprint. It provides an overview of the goals, approach, and expected outcomes.

Tekton is an intelligent orchestration system that coordinates multiple CI models and resources to efficiently solve complex software engineering problems. This Development Sprint focuses on enabling Rhetor CI specialists to power the right panel chat interfaces in Hephaestus and enhancing the Rhetor menu bar component to expose full API capabilities.

## Sprint Goals

The primary goals of this sprint are:

1. **Enable AI-Powered Component Chats**: Connect Rhetor CI specialists to power the right panel chat interfaces for all Tekton components in Hephaestus
2. **Enhance Menu Bar Integration**: Expand the Rhetor menu bar component to expose full specialist management and orchestration capabilities
3. **Implement Persistent Chat Options**: Add configurable chat history persistence with component-level settings

## Business Value

This sprint delivers value by:

- **Unified CI Experience**: Every Tekton component will have its own CI assistant accessible through a consistent chat interface
- **Improved Developer Productivity**: Direct CI assistance within each component's context reduces context switching
- **Enhanced Orchestration**: Menu bar access to Rhetor capabilities enables quick CI orchestration across components
- **Flexible History Management**: Users can choose to preserve or discard chat histories based on their workflow

## Current State Assessment

### Existing Implementation

The Rhetor CI Integration Sprint successfully implemented:
- 6 pre-configured CI specialists with distinct roles and personalities
- Dynamic specialist creation from 8 templates
- Real-time streaming support via Server-Sent Events (SSE)
- WebSocket bidirectional communication
- MCP tools for CI orchestration
- Internal specialist-to-specialist communication

However, the integration with Hephaestus remains incomplete:
- Component chat tabs exist but aren't connected to CI specialists
- The Rhetor menu bar component has limited functionality
- No cross-component CI routing infrastructure
- Chat histories are not persisted

### Pain Points

- **Disconnected AI**: Rhetor specialists exist but can't be accessed from component UIs
- **Limited Menu Access**: Users must open full Rhetor component for most operations
- **No Context Preservation**: Chat histories are lost on page refresh
- **Manual Specialist Assignment**: No automatic mapping of specialists to components

## Proposed Approach

### Key Components Affected

- **Hephaestus UI**: Enhanced terminal chat integration, component-AI mapping, streaming support
- **Rhetor Backend**: Component specialist registry, enhanced routing, persistence layer
- **Hermes Message Bus**: Component-specific topic routing for CI messages
- **Component Registry**: CI assistant configuration per component

### Technical Approach

1. **Component-AI Mapping System**
   - Pre-configured specialists for each component (e.g., "athena-assistant", "budget-assistant")
   - Dynamic creation/recreation based on component requirements
   - Specialist registry maintained in Rhetor

2. **Enhanced Message Routing**
   - Hermes topics: `ai.chat.{component_id}` for component-specific routing
   - WebSocket message enhancement with component context
   - Response routing to correct chat panels

3. **Menu Bar API Integration**
   - Expose specialist management endpoints
   - Quick actions for common operations
   - Component-aware specialist switching

4. **Chat Persistence Layer**
   - localStorage for chat histories
   - Component-level SAVE_CHAT_HISTORY setting
   - Global default in .env.tekton

## Code Quality Requirements

### Debug Instrumentation

All code produced in this sprint **MUST** follow the [Debug Instrumentation Guidelines](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md):

- Frontend JavaScript must use conditional `TektonDebug` calls
- Backend Python must use the `debug_log` utility and `@log_function` decorators
- All debug calls must include appropriate component names and log levels
- Error handling must include contextual debug information

### Documentation

Code must be documented according to the following guidelines:

- Class and method documentation with clear purpose statements
- API contracts and parameter descriptions
- Requirements for component initialization
- Error handling strategy

### Testing

The implementation must include appropriate tests:

- Unit tests for core functionality
- Integration tests for component interactions
- Performance tests for streaming operations

## Out of Scope

The following items are explicitly out of scope for this sprint:

- Complete rewrite of Hephaestus chat UI (keeping existing bubble design)
- Cross-component AI-to-AI communication (reserved for future A2A work)
- Advanced CI orchestration features beyond basic team chat
- Migration of existing Rhetor UI to different framework

## Dependencies

This sprint has the following dependencies:

- Rhetor CI Integration Sprint completion (DONE)
- Hermes message bus operational
- Component registry system functional
- Ollama models available locally

## Timeline and Phases

This sprint is planned to be completed in 4 phases:

### Phase 1: Foundation & Routing (Days 1-2)
- **Duration**: 2 days
- **Focus**: Component-AI mapping and message routing infrastructure
- **Key Deliverables**: 
  - Component specialist registry
  - Enhanced Hermes routing
  - Specialist auto-creation logic

### Phase 2: Right Panel Integration (Days 3-4)
- **Duration**: 2 days
- **Focus**: Connect CI specialists to component chat interfaces
- **Key Deliverables**:
  - Component CI chat service
  - Terminal chat enhancement
  - Streaming support integration

### Phase 3: Menu Bar Enhancement (Days 5-6)
- **Duration**: 2 days
- **Focus**: Expand Rhetor menu bar capabilities
- **Key Deliverables**:
  - Full API exposure in menu
  - Quick action controls
  - Component context switching

### Phase 4: Settings & Polish (Day 7)
- **Duration**: 1 day
- **Focus**: Chat persistence and final integration
- **Key Deliverables**:
  - SAVE_CHAT_HISTORY setting
  - Hephaestus settings integration
  - Documentation and examples

## Specialist Model Assignments

Based on component requirements and available models:

### Cloud Models (Primary)
- **rhetor-orchestrator**: Claude Opus (meta-orchestration, complex reasoning)
- **athena-assistant**: Claude Haiku (fast knowledge queries)
- **budget-assistant**: GPT-4 (financial analysis, cost optimization)
- **engram-assistant**: Claude Sonnet (memory management, context handling)
- **apollo-assistant**: GPT-4 (executive coordination, planning)
- **prometheus-assistant**: Claude Opus (strategic analysis, metrics)

### Ollama Models (Local Alternatives)
- **code-reviewer**: `codestral:22b` (specialized for code review)
- **bug-hunter**: `qwen2.5-coder:32b` (excellent at finding issues)
- **architecture-advisor**: `deepseek-r1:32b` (reasoning-focused)
- **api-designer**: `mixtral:latest` (balanced general purpose)
- **performance-optimizer**: `llama3.3:70b` (large context, detailed analysis)
- **security-auditor**: `command-r:35b` (comprehensive analysis)
- **documentation-writer**: `qwen3:32b` (excellent writing capabilities)
- **data-analyst**: `solar:10.7b` (efficient for data tasks)

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| WebSocket connection complexity | High | Medium | Use existing Hermes infrastructure, implement reconnection logic |
| Performance with multiple CI chats | Medium | High | Implement message queuing, use streaming for better UX |
| Model availability/cost | Medium | Medium | Provide Ollama fallbacks for all specialists |
| Chat history storage limits | Low | Medium | Implement size limits and rotation policies |

## Success Criteria

This sprint will be considered successful if:

- All Tekton components have functional CI chat interfaces in right panel
- Rhetor menu bar provides access to key specialist management features
- Chat histories can be optionally preserved across sessions
- Streaming responses work smoothly with typing indicators
- All code follows the Debug Instrumentation Guidelines
- Documentation is complete and accurate
- Tests pass with 80% coverage

## Key Stakeholders

- **Casey**: Human-in-the-loop project manager
- **Architect Claude**: Sprint planning and architecture
- **Working Claude**: Implementation and testing

## References

- [Rhetor CI Integration Sprint](/MetaData/DevelopmentSprints/Rhetor_AI_Integration_Sprint/)
- [Hephaestus Component Implementation Guide](/MetaData/ComponentDocumentation/Hephaestus/ComponentImplementationGuide.md)
- [MCP Implementation Guide](/MetaData/TektonDocumentation/DeveloperGuides/MCP_IMPLEMENTATION_GUIDE.md)
- [Debug Instrumentation Guidelines](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md)