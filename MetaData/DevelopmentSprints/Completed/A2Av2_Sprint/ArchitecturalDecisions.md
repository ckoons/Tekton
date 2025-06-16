# A2A v2 Protocol Update - Architectural Decisions

## Overview

This document records the architectural decisions made during the A2A v2 Protocol Update Sprint. It captures the context, considerations, alternatives considered, and rationale behind each significant decision. This serves as a reference for both current implementation and future development.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. The architectural decisions in this document focus on modernizing Tekton's agent-to-agent communication to align with the A2A Protocol v0.2.1 specification.

## Decision 1: Full Implementation of JSON-RPC 2.0 Protocol

### Context

Tekton's A2A implementation is being built fresh to align with the A2A Protocol v0.2.1 specification, which mandates JSON-RPC 2.0 over HTTP(S). Since we haven't released yet, we can implement the specification cleanly without legacy concerns.

### Decision

Implement JSON-RPC 2.0 as the sole protocol for A2A communication, following the A2A v0.2.1 specification exactly.

### Alternatives Considered

#### Alternative 1: Custom Protocol Extension

Extend JSON-RPC 2.0 with Tekton-specific enhancements.

**Pros:**
- Could add Tekton-specific optimizations
- Flexibility for unique features
- Potential performance improvements

**Cons:**
- Breaks A2A specification compliance
- Limits interoperability with other A2A systems
- Increases maintenance burden

#### Alternative 2: Minimal Implementation

Implement only the required subset of A2A methods.

**Pros:**
- Faster initial development
- Simpler codebase
- Easier to test

**Cons:**
- Limited functionality
- Would need expansion later
- May not meet all use cases

### Decision Rationale

Full implementation of the standard protocol ensures maximum compatibility with the A2A ecosystem and provides a solid foundation for Tekton's agent communication. Since we have no legacy code to support, we can build it right from the start.

### Implications

- Performance: Native JSON-RPC 2.0 with no translation overhead
- Maintainability: Clean, standard-compliant codebase
- Extensibility: Can add A2A extensions as defined in spec
- Security: Built-in support for standard auth methods
- Learning curve: Developers need to understand JSON-RPC 2.0 and A2A spec
- Integration: Full compatibility with any A2A-compliant system
- Dependencies: Minimal - just JSON parsing and HTTP libraries

### Implementation Guidelines

1. Follow A2A specification exactly for all data structures
2. Use Pydantic models for type safety and validation
3. Implement all required methods from the spec
4. Add comprehensive debug logging for all operations
5. Structure for easy addition of optional A2A extensions

## Decision 2: Server-Sent Events for Streaming

### Context

The A2A specification requires SSE for real-time updates. Tekton currently uses WebSocket connections through Hermes for real-time communication. We need to decide how to implement SSE support.

### Decision

Implement SSE as a parallel option to WebSockets, with SSE used for A2A protocol compliance and WebSockets retained for internal Tekton communication.

### Alternatives Considered

#### Alternative 1: Replace WebSockets with SSE

Completely replace WebSocket usage with SSE throughout Tekton.

**Pros:**
- Single streaming technology
- Full A2A compliance
- Simpler HTTP-based infrastructure

**Cons:**
- SSE is unidirectional (server-to-client only)
- Would require significant refactoring of Hermes
- Loss of bidirectional real-time features

#### Alternative 2: SSE-to-WebSocket Bridge

Implement SSE endpoints that internally use WebSocket connections.

**Pros:**
- Reuses existing WebSocket infrastructure
- Minimal changes to Hermes
- Maintains bidirectional capabilities internally

**Cons:**
- Complex bridging logic
- Potential for message ordering issues
- Harder to debug streaming problems

### Decision Rationale

Supporting both technologies allows us to comply with A2A specifications while maintaining Tekton's existing real-time capabilities. SSE will be used for A2A-compliant streaming, while WebSockets continue to power internal communication.

### Implications

- Performance: Minimal impact, both are efficient for streaming
- Maintainability: Two streaming technologies to maintain
- Extensibility: New A2A features use SSE, internal features use WebSockets
- Security: Both share authentication layer
- Learning curve: Developers need to understand when to use each
- Integration: External systems use SSE as per A2A spec
- Dependencies: FastAPI's SSE support

### Implementation Guidelines

1. Use FastAPI's `StreamingResponse` for SSE endpoints
2. Implement `SSEManager` class for connection management
3. Create clear naming conventions: `/stream` for SSE, `/ws` for WebSocket
4. Document when to use each technology
5. Share event formatting between both systems

## Decision 3: Task State Management

### Context

The A2A specification defines formal task states (submitted, working, input-required, completed, etc.). Tekton's current task management is more informal. We need to decide how to implement formal state tracking.

### Decision

Implement a formal state machine for task management with explicit state transitions and event emission on state changes.

### Alternatives Considered

#### Alternative 1: Simple Enum States

Use only an enum field to track states without formal transitions.

**Pros:**
- Simple implementation
- Easy to understand
- Minimal code changes

**Cons:**
- No validation of state transitions
- Difficult to track state history
- No automatic event emission

#### Alternative 2: External State Management Service

Create a dedicated service for task state management.

**Pros:**
- Centralized state tracking
- Could support complex workflows
- Reusable across components

**Cons:**
- Over-engineering for current needs
- Additional service to deploy and maintain
- Performance overhead for state queries

### Decision Rationale

A state machine provides the right balance of formality and simplicity. It ensures valid state transitions while being lightweight enough to embed in each component.

### Implications

- Performance: Minimal overhead for state validation
- Maintainability: Clear state transition rules
- Extensibility: Easy to add new states and transitions
- Security: State changes can be access-controlled
- Learning curve: Developers must understand state machine pattern
- Integration: Clean mapping to A2A task states
- Dependencies: Simple state machine implementation (no external library needed)

### Implementation Guidelines

1. Create `TaskStateMachine` class with transition rules
2. Emit events on every state change for streaming
3. Store state history with timestamps
4. Implement guards for conditional transitions
5. Add debug logging for all transitions

## Decision 4: Native A2A Authentication Implementation

### Context

The A2A specification requires standard HTTP authentication (Bearer tokens, API keys, etc.). Since Tekton is implementing A2A fresh, we can build authentication correctly from the start.

### Decision

Implement A2A-compliant authentication as the primary authentication system for agent communication, following the specification's security model exactly.

### Alternatives Considered

#### Alternative 1: Custom Authentication System

Build a Tekton-specific authentication system.

**Pros:**
- Could be optimized for Tekton's needs
- Full control over implementation
- Potential for unique features

**Cons:**
- Not A2A compliant
- More code to maintain
- Security risks from custom implementation

#### Alternative 2: Minimal Authentication

Implement only basic authentication for initial release.

**Pros:**
- Faster to implement
- Simpler codebase
- Easier to test

**Cons:**
- Not suitable for production
- Would need major rework later
- Security concerns

### Decision Rationale

Implementing the full A2A authentication model ensures security best practices and compatibility with the broader A2A ecosystem. Using standard authentication methods reduces security risks.

### Implications

- Performance: Minimal overhead with proper caching
- Maintainability: Standard patterns, well-understood security
- Extensibility: Easy to add new authentication schemes per spec
- Security: Industry-standard authentication methods
- Learning curve: Developers use familiar auth patterns
- Integration: External systems use standard auth methods
- Dependencies: Standard auth libraries (PyJWT, etc.)

### Implementation Guidelines

1. Create `A2AAuthMiddleware` with pluggable authenticators
2. Support Bearer, Basic, and API Key authentication from day one
3. Use FastAPI's security utilities for implementation
4. Add auth scheme to Agent Card as per spec
5. Implement auth caching for performance

## Cross-Cutting Concerns

### Performance Considerations

- HTTP overhead is minimal with connection pooling
- JSON-RPC parsing is fast with modern libraries
- SSE has lower overhead than WebSocket for unidirectional streams
- State machine transitions are O(1) operations
- Authentication caching prevents repeated validation

### Security Considerations

- All A2A communication over HTTPS in production
- Authentication tokens never logged or stored in plain text
- State transitions audit-logged for security monitoring
- Push notification URLs validated to prevent SSRF
- Rate limiting on all A2A endpoints

### Maintainability Considerations

- Clear separation between A2A protocol and internal logic
- Comprehensive debug instrumentation for protocol translation
- Automated tests for all protocol conversions
- Documentation for each A2A method implementation
- Deprecation path for legacy protocol

### Scalability Considerations

- SSE connections managed with connection limits
- Task state stored in distributed cache (Redis)
- HTTP connection pooling for agent-to-agent calls
- Async implementation for all I/O operations
- Webhook queuing for push notifications

## Future Considerations

1. **Advanced Task Workflows**: The state machine could support complex workflows
2. **Agent Collaboration Protocols**: Higher-level protocols built on A2A
3. **Performance Optimization**: Protocol-specific optimizations after stability
4. **External Agent Integration**: Connecting to non-Tekton A2A agents
5. **Monitoring and Observability**: A2A-specific metrics and tracing

## References

- [A2A Protocol Specification v0.2.1](https://google-a2a.github.io/A2A/specification/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [Server-Sent Events W3C Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [Tekton Authentication Architecture](/MetaData/ComponentDocumentation/Hermes/TECHNICAL_DOCUMENTATION.md#authentication)