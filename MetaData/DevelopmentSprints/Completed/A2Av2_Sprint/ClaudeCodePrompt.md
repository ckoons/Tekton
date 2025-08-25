# A2A v2 Protocol Update - Initial Implementation Prompt

## Context

You are tasked with implementing the A2A v2 Protocol for the Tekton project. Tekton is an intelligent orchestration system that coordinates multiple CI models and resources. This sprint implements Tekton's Agent-to-Agent (A2A) communication framework from scratch to fully comply with the A2A Protocol v0.2.1 specification.

## Current Situation

Tekton needs a fresh A2A implementation. The existing code in `tekton-core/tekton/a2a/` is placeholder code that can be completely replaced. Since Tekton has not been released yet, there are no backward compatibility requirements - you can implement the A2A v0.2.1 specification cleanly and completely.

The A2A Protocol v0.2.1 requires:
- JSON-RPC 2.0 over HTTP(S) as the sole protocol
- Server-Sent Events (SSE) for streaming
- Formal task state management with defined states
- Standard HTTP authentication (Bearer, Basic, API Key)
- Fully specified Agent Card format

## Your Task

Implement Phase 1 of the Implementation Plan: Protocol Foundation.

### Specific Implementation Tasks

1. **Create the protocol module** at `tekton-core/tekton/a2a/protocol/`:
   - Implement JSON-RPC 2.0 request/response classes
   - Create A2A-specific error codes and handlers
   - Define all protocol types from the A2A specification

2. **Create the transport module** at `tekton-core/tekton/a2a/transport/`:
   - Build FastAPI-based HTTP server for A2A endpoints
   - Implement HTTP client with connection pooling
   - Add authentication middleware structure

3. **Create method handlers** at `tekton-core/tekton/a2a/methods/`:
   - Implement `message/send` method
   - Implement `tasks/get` method
   - Implement `tasks/cancel` method

4. **Replace existing placeholder code**:
   - Replace entire contents of `tekton/a2a/` with new implementation
   - Update `tekton/a2a/__init__.py` to export new A2A classes
   - Remove any old placeholder code

### Code Quality Requirements

All code MUST follow these guidelines:

1. **Debug Instrumentation**:
   - Use `debug_log` from `shared.utils.logging_setup`
   - Add `@log_function` decorators to key methods
   - Include component name "a2a" in all debug calls

2. **Documentation**:
   - Comprehensive docstrings for all classes and methods
   - Include parameter types and return values
   - Document any deviations from A2A spec

3. **Error Handling**:
   - Use proper JSON-RPC error codes
   - Include contextual information in errors
   - Log all errors with debug instrumentation

4. **Testing Readiness**:
   - Structure code for easy unit testing
   - Avoid hard dependencies on external services
   - Use dependency injection where appropriate

### Technical Constraints

- Use FastAPI for HTTP endpoints (already in Tekton dependencies)
- Follow the A2A v0.2.1 specification exactly
- Use Pydantic for data models to ensure type safety
- Structure code for future addition of SSE and push notifications

### Key Files to Reference

- A2A Protocol Spec: Read the specification at `/Users/cskoons/projects/github/A2A/docs/specification.md`
- A2A JSON Schema: `/Users/cskoons/projects/github/A2A/specification/json/a2a.json`
- Tekton patterns: `/Tekton/shared/utils/`, `/Tekton/CLAUDE.md`
- FastAPI examples: `/Tekton/Ergon/ergon/api/`, `/Tekton/Hermes/hermes/api/`

### Expected Deliverables

1. Complete protocol module with JSON-RPC handling
2. Working HTTP transport layer with FastAPI
3. Three core method implementations (message/send, tasks/get, tasks/cancel)
4. All A2A data types defined as Pydantic models
5. All code following debug instrumentation guidelines
6. Unit tests for core functionality

### Success Criteria

- JSON-RPC requests can be parsed and validated according to spec
- HTTP endpoint responds correctly to A2A method calls
- All A2A data types match the v0.2.1 specification
- Error responses follow A2A error code standards
- All code has debug instrumentation
- Clean implementation with no legacy code

## Important Notes

- This is Phase 1 of 3 - focus on protocol foundation only
- Streaming (SSE) will be implemented in Phase 2
- Security enhancements will be added in Phase 3
- Prioritize correctness over performance optimization
- Ask for clarification if any specification details are unclear

Begin by reading the A2A specification files to understand the protocol requirements, then proceed with replacing the existing placeholder code with a clean implementation of the A2A v0.2.1 specification.