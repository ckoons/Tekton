# YetAnotherMCP_Sprint

## Overview

This Development Sprint focuses on standardizing the Model Context Protocol (MCP) implementation across all Tekton components, with Hermes serving as the central MCP aggregator. It aims to resolve existing issues with the MCP service, establish consistent endpoints, and create a shared library for all components to use.

## Key Documents

- [SprintPlan.md](SprintPlan.md) - High-level sprint plan
- [ArchitecturalDecisions.md](ArchitecturalDecisions.md) - Key architectural decisions
- [ImplementationPlan.md](ImplementationPlan.md) - Detailed implementation plan

## Relationship to OneHeartbeat Sprint

This sprint has been designed to work in conjunction with the OneHeartbeat Sprint, which focuses on standardizing the heartbeat system used by all components. The two sprints are complementary:

1. **OneHeartbeat Sprint**:
   - Standardizes on `HermesRegistration` with `heartbeat_loop` as the single standard
   - Removes unused `ComponentHeartbeat`
   - Ensures all components use the same pattern
   - Leverages existing graceful shutdown for cleanup

2. **YetAnotherMCP Sprint**:
   - Fixes the Hermes MCP service initialization bug
   - Standardizes on `/api/mcp/v2` endpoint across all components
   - Enhances component registration to include MCP tools
   - Creates a shared MCP library

The `YetAnotherMCP_Sprint` builds on the foundation provided by the `OneHeartbeat_Sprint`, ensuring that the standardized registration and heartbeat system also handles MCP tool registration and status reporting.

## Implementation Strategy

To ensure smooth integration with the OneHeartbeat Sprint, our implementation will:

1. **Use the standardized registration system** from OneHeartbeat Sprint
2. **Extend `HermesRegistration`** to include MCP tool registration
3. **Include MCP status in heartbeats** using the standard heartbeat mechanism
4. **Leverage the existing graceful shutdown** for proper MCP service cleanup

This approach ensures that both critical infrastructure systems work together effectively, without duplication or conflicts.

## Getting Started

To begin working on this sprint:

1. Review the sprint documents to understand the goals and approach
2. Start with Phase 1: Fixing the Hermes MCP service initialization bug
3. Coordinate with the OneHeartbeat Sprint team for registration and heartbeat integration
4. Follow the detailed implementation steps in the [ImplementationPlan.md](ImplementationPlan.md)

## Testing

Comprehensive testing is crucial for this sprint:

1. **Unit tests** for the MCP service initialization and operation
2. **Integration tests** for MCP tool registration and discovery
3. **End-to-end tests** for Claude integration with the Hermes MCP endpoint

All tests should verify that both the MCP system and the heartbeat system work together correctly.

## Contributing

When contributing to this sprint, please ensure:

1. All code includes proper debug instrumentation
2. Changes are compatible with the OneHeartbeat Sprint
3. Documentation is updated to reflect the changes
4. Tests are included for all new functionality

## Status

Current sprint status: **Planning**

See the [StatusReports](StatusReports/) directory for detailed status updates.