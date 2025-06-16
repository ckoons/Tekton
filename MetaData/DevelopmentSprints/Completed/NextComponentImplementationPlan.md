# MCP Unified Integration Sprint - Next Component Implementation Plan

## Introduction

This document outlines the implementation plan for the next components to be updated with FastMCP in the MCP Unified Integration Sprint. We've already successfully implemented FastMCP in Hermes, Apollo, Athena, Budget, and Engram components.

## Implementation Order

The following order is recommended for updating the remaining components:

1. Ergon
2. Harmonia
3. Hephaestus
4. Metis
5. Prometheus
6. Rhetor
7. Sophia
8. Synthesis
9. Telos
10. Terma

## Implementation Steps for Each Component

Follow these steps when implementing FastMCP for a component:

1. **Add FastMCP as a dependency**
   - Update `requirements.txt` to add `tekton-core>=0.1.0`
   - Update `setup.py` to add `tekton-core>=0.1.0` to install_requires

2. **Create MCP module**
   - Create a `component/core/mcp/` directory
   - Create `__init__.py` that exports all tools and registration functions
   - Create `tools.py` with tool definitions using FastMCP decorators

3. **Update API with FastMCP endpoints**
   - Create an MCP router using `create_mcp_router` from FastMCP utils
   - Add standard MCP endpoints using `add_standard_mcp_endpoints`
   - Maintain backward compatibility if the component has existing MCP endpoints

4. **Adapt message handlers**
   - Implement necessary handler functions for each tool
   - Use dependency injection for component-specific dependencies
   - Register tools during application startup

5. **Add tests**
   - Create test scripts to verify the FastMCP implementation
   - Test all exposed tools and capabilities
   - Document the test procedure

6. **Update documentation**
   - Create an `MCP_INTEGRATION.md` file documenting the implementation
   - Update the ProgressSummary.md with the latest progress

## Ergon Implementation Plan

Ergon is the next component to update with FastMCP. Here's a detailed plan for implementing FastMCP in Ergon:

### 1. Add FastMCP as a dependency
Update Ergon's `requirements.txt` and `setup.py` to add tekton-core as a dependency.

### 2. Create MCP module in Ergon's core
Create a new MCP module with tool definitions:
```
ergon/
  core/
    mcp/
      __init__.py
      tools.py  # Define FastMCP tools
```

Define FastMCP tools for Ergon's functionality:
- Agent operations (create, update, delete, list, execute)
- Workflow operations (create, update, execute, monitor)
- Task management operations (create, list, update, delete)

### 3. Update API Integration
1. Create a new FastMCP router in the MCP endpoints file
2. Add FastMCP standard endpoints:
   - `/mcp/health`
   - `/mcp/capabilities`
   - `/mcp/tools`
   - `/mcp/process`
3. Keep any existing MCP endpoints for backward compatibility

### 4. Implement Core Functionality
1. Add decorators to existing message handler functions:
   - `@mcp_tool` for each message handler
   - `@mcp_capability` to group related tools
2. Create tool registry and registration functions
3. Update core services to use FastMCP

### 5. Leverage Shared Utilities
1. Use `endpoints.py` from shared utilities for router creation
2. Use `tooling.py` for tool registration
3. Use `requests.py` and `response.py` for standardized processing

### 6. Testing
Create test scripts to verify the FastMCP implementation:
1. Test getting capabilities and tools
2. Test agent operations
3. Test workflow operations
4. Test task management operations

## General Guidelines

1. **Implementation Approach**: Choose between two successful patterns:
   - **Direct Integration** (like Budget): Integrate FastMCP directly into existing MCP endpoints
   - **Parallel Integration** (like Engram): Create a separate FastMCP server alongside the existing one

2. **Backward Compatibility**: If a component has an existing MCP implementation, keep it running in parallel with FastMCP for backward compatibility.

3. **Error Handling**: Implement comprehensive error handling in all tool handlers.

4. **Documentation**: Document each tool with clear descriptions, parameter details, and examples.

5. **Dependency Injection**: Use dependency injection to provide component-specific dependencies to tool handlers.

6. **Testing**: Test all aspects of the FastMCP implementation to ensure it works correctly.

7. **Progress Tracking**: Update the ProgressSummary.md document after each component implementation.

## Reference Implementations

### Budget Component (Direct Integration)
The Budget component serves as a reference implementation for directly integrating FastMCP into existing MCP endpoints:

1. **Single MCP Router**: Use a single router for both legacy and FastMCP endpoints
2. **Shared Handler Logic**: Adapt existing handlers to use the decorator pattern
3. **Backward Compatible API**: Maintain existing API paths and response formats

### Engram Component (Parallel Integration)
The Engram component serves as a reference implementation for running FastMCP alongside an existing MCP implementation:

1. **Separate Server Implementation**: Create a dedicated FastMCP server
2. **Independent Routing**: Use separate routers for legacy and FastMCP endpoints
3. **Shared Domain Logic**: Both implementations use the same underlying domain logic

## Conclusion

By following this implementation plan, we can ensure a consistent, standardized approach to FastMCP integration across all Tekton components. Both the direct integration and parallel implementation approaches have been successfully demonstrated, providing flexibility for different component requirements.