# Claude Code Prompt for MCP Unified Integration Sprint

## Context

You are assisting with implementing the MCP Unified Integration Sprint for Tekton, an intelligent orchestration system that coordinates multiple CI models and resources to efficiently solve complex software engineering problems. This sprint consolidates previously planned FastMCP_Sprint and MCP_Integration_Sprint efforts into a comprehensive MCP implementation across Tekton components.

Tekton's architecture consists of multiple components including Hermes (communication hub), Ergon (agent and tool management), Rhetor (LLM management), and others. The current MCP implementation has issues with component registration, service initialization, and request routing that need to be fixed.

## Goals

Your task is to implement the MCP Unified Integration plan, which includes:

1. Implementing a standardized MCP approach based on FastMCP's decorator pattern
2. Fixing component registration and MCP service initialization
3. Implementing request routing for cross-component communication
4. Creating integration patterns for external MCP servers
5. Ensuring Claude Code compatibility

## Current State

1. **tekton-core**: Has a custom MCP implementation that is verbose and difficult to maintain
2. **Hermes**: MCP service initialization issues ("MCP service not initialized" errors)
3. **Component Registration**: Validation errors (422) during component registration
4. **Service Registry**: Empty responses from registry endpoints
5. **Request Routing**: No standardized mechanism for routing MCP requests between components

## Implementation Approach

The implementation will follow these phases:

1. **Phase 1**: Core MCP Implementation and Registration
2. **Phase 2**: Cross-Component Integration
3. **Phase 3**: External Integration Points
4. **Phase 4**: Claude Code Compatibility and Testing

Please refer to the [Implementation Plan](./ImplementationPlan.md) for detailed tasks within each phase.

## Key Architectural Decisions

1. **Unified MCP Implementation**: Replace custom MCP with FastMCP-based approach
2. **Separation of Concerns**: Hermes for internal communication, Ergon for external integration
3. **Protocol-First Development**: Define interfaces and contracts before implementation
4. **Adapter Pattern**: Use adapter pattern for external MCP server integration
5. **Standardized Registration**: Implement consistent registration protocol
6. **Multi-Modal Capability Registry**: Track capabilities by modality for optimal routing

For detailed information on these decisions, see [Architectural Decisions](./ArchitecturalDecisions.md).

## Branch Management

Before making any changes, verify you are on the correct branch:

```bash
scripts/github/tekton-branch-verify sprint/mcp-unified-integration-250507
```

All development should be conducted on this branch.

## External Project Context

The implementation should establish patterns for integrating with the following external projects:

1. **open-mcp**: Standardized approach to converting web APIs into MCP servers
2. **pluggedin-mcp-proxy**: Proxy server for aggregating multiple MCP servers
3. **pipedream**: Event-driven integration platform

While actual integration with these projects is out of scope, the architectural foundations for such integration should be established.

## First Steps

1. Set up the development environment and verify correct branch
2. Understand existing MCP implementation across components
3. Begin implementing FastMCP integration in tekton-core
4. Implement standardized registration protocol
5. Fix Hermes MCP service initialization

## Deliverables

Your implementation should result in:

1. Updated tekton-core with FastMCP integration
2. Fixed Hermes MCP service initialization and registration
3. Working cross-component MCP communication
4. Integration patterns for external MCP servers
5. Claude Code compatibility
6. Comprehensive tests and documentation

## References

- [Sprint Plan](./SprintPlan.md)
- [Architectural Decisions](./ArchitecturalDecisions.md)
- [Implementation Plan](./ImplementationPlan.md)
- [FastMCP Documentation](https://gofastmcp.com)
- [Model Context Protocol](https://modelcontextprotocol.io)