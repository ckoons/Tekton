# YetAnotherMCP_Sprint - Architectural Decisions

## Overview

This document outlines the key architectural decisions for the YetAnotherMCP_Sprint, which focuses on standardizing the Model Context Protocol (MCP) implementation across all Tekton components.

## Key Decision 1: Standardize on `/api/mcp/v2` Endpoint

### Context
Currently, there is inconsistency in MCP endpoint paths across Tekton components. Engram uses `/mcp`, Rhetor uses `/api/mcp/v2`, and Hermes has a broken MCP service using `/mcp`.

### Decision
We will standardize on `/api/mcp/v2` as the single MCP endpoint path for all Tekton components.

### Rationale
- Follows modern API design patterns with resources under `/api`
- Version designation (`v2`) allows for future evolution
- More explicit path structure avoids potential conflicts
- Already implemented in Rhetor, which has a mature MCP implementation

### Implications
- All components need to update their MCP endpoint paths
- Client code needs to be updated to use the standardized endpoint
- Installation scripts need to be updated to reference the correct endpoint

## Key Decision 2: Hermes as Central MCP Aggregator

### Context
Currently, clients like Claude need to connect to each component's MCP endpoint individually, which is inefficient and inconsistent.

### Decision
Hermes will serve as the central MCP aggregator for all Tekton components. Clients will connect only to Hermes's MCP endpoint, which will route requests to the appropriate component.

### Rationale
- Simplifies client integration with a single connection point
- Enables cross-component tool discovery
- Follows the existing "Single Point of Control" architecture principle
- Maintains consistent authentication and authorization

### Implications
- Hermes needs to be enhanced to properly discover and aggregate MCP tools
- Components need to register their MCP tools with Hermes
- Routing logic needs to be implemented in Hermes

## Key Decision 3: MCP Tool Registration During Component Registration

### Context
Currently, components register with Hermes but don't explicitly register their MCP tools, making tool discovery difficult.

### Decision
MCP tools will be registered as part of the standard component registration process, using an enhanced version of `hermes_registration.py`.

### Rationale
- Consolidates registration into a single process
- Makes tool discovery automatic
- Ensures consistency between component and tool registration
- Simplifies component implementation

### Implications
- `hermes_registration.py` needs to be updated to handle MCP tools
- Components need to provide their MCP tools during registration
- Hermes needs to track and manage tool registrations

## Key Decision 4: Create Shared MCP Library in `tekton/mcp`

### Context
Each component currently has its own MCP implementation, leading to duplication and inconsistency.

### Decision
Create a standardized MCP library in `tekton/mcp` that all components will use.

### Rationale
- Reduces code duplication
- Ensures consistency across components
- Makes future updates easier
- Follows DRY (Don't Repeat Yourself) principle

### Implications
- New library needs to be created
- Components need to be updated to use the shared library
- Backward compatibility may be a challenge

## Key Decision 5: Integration with OneHeartbeat Sprint

### Context
The OneHeartbeat Sprint aims to standardize the heartbeat system used by all components.

### Decision
We will integrate with the OneHeartbeat Sprint by ensuring our MCP registration works with the standardized heartbeat system.

### Rationale
- Both sprints aim to standardize core infrastructure
- Heartbeat system is essential for component lifecycle management
- Avoiding duplication of effort

### Implications
- Coordination with OneHeartbeat Sprint is required
- MCP registration needs to use the standardized heartbeat system
- Testing needs to verify both systems work together

## Key Decision 6: Debug Instrumentation for MCP Operations

### Context
MCP operations need proper debug instrumentation for effective troubleshooting.

### Decision
All MCP code will follow the Debug Instrumentation Guidelines, with specific attention to MCP operations.

### Rationale
- MCP operations are critical infrastructure
- Debugging distributed systems requires comprehensive instrumentation
- Follows project-wide instrumentation standards

### Implications
- All MCP code needs appropriate instrumentation
- Documentation needs to include debugging guidelines
- Testing needs to verify instrumentation effectiveness

## Key Decision 7: Centralized Tool Registry in Hermes

### Context
Currently, there's no central registry of available MCP tools across components.

### Decision
Hermes will maintain a centralized registry of all MCP tools from all components.

### Rationale
- Enables tool discovery across components
- Simplifies client integration
- Allows for tool metadata and capability management

### Implications
- Hermes needs a tool registry implementation
- Registration process needs to update the registry
- Tool information needs to be consistently structured

## Conclusion

These architectural decisions provide a solid foundation for standardizing the MCP implementation across Tekton. The focus on a single endpoint pattern, centralized aggregation, and shared code will result in a more maintainable and consistent system.

The decisions align with the broader Tekton architecture principles of standardization, component isolation, and single point of control. By integrating with the OneHeartbeat Sprint, we ensure that both critical infrastructure systems work together effectively.