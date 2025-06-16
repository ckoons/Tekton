# A2A v2 Protocol Update Sprint

This directory contains documentation and plans for updating Tekton's Agent-to-Agent (A2A) communication framework to align with the new A2A Protocol v0.2.1 specification.

## Sprint Overview

The A2A Protocol has evolved significantly from Tekton's original implementation. The new v0.2.1 specification introduces industry-standard protocols (JSON-RPC 2.0), real-time streaming capabilities (SSE), formal task lifecycle management, and enterprise-ready security features. This sprint will update Tekton's A2A implementation to leverage these improvements.

## Key Documents

- **SprintPlan.md** - High-level goals and approach for the A2A v2 update
- **ArchitecturalDecisions.md** - Key architectural decisions for protocol migration
- **ImplementationPlan.md** - Detailed implementation steps and component updates
- **ClaudeCodePrompt.md** - Initial prompt for the implementation phase

## Sprint Goals

1. Replace custom message format with JSON-RPC 2.0 over HTTP(S)
2. Implement Server-Sent Events (SSE) for real-time streaming
3. Update task management with formal state lifecycle
4. Align Agent Cards with new specification
5. Add enterprise security features

## Affected Components

- **tekton-core**: Core A2A protocol implementation
- **Hermes**: Message bus and A2A service updates
- **Ergon**: A2A endpoint updates
- **All Components**: Agent registration and discovery updates

## References

- [A2A Protocol Specification v0.2.1](https://google-a2a.github.io/A2A/specification/)
- [Current Tekton A2A Implementation](/Tekton/tekton/a2a/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)