# Budget Component - FastMCP Integration

This document describes the FastMCP integration for the Budget component.

## Overview

The Budget component now supports the Model Context Protocol (MCP) using FastMCP's decorator-based approach. This integration allows the Budget component to expose its capabilities and tools to other components in a standardized way.

## Implementation

The FastMCP integration includes:

1. **FastMCP as a Dependency**
   - Added tekton-core as a dependency in requirements.txt and setup.py
   - FastMCP is part of the tekton-core package

2. **MCP Module in Budget Core**
   - Created an MCP module in `budget/core/mcp/`
   - Implemented tool definitions using FastMCP decorators
   - Exposed capabilities for budget management, model recommendations, and analytics

3. **Updated API with FastMCP Endpoints**
   - Added FastMCP endpoints to the existing MCP router
   - Maintained backward compatibility with existing MCP endpoints
   - Added standard MCP endpoints:
     - `/api/mcp/health` - Health check endpoint
     - `/api/mcp/capabilities` - Capabilities endpoint
     - `/api/mcp/tools` - Tools endpoint
     - `/api/mcp/process` - Process endpoint

4. **Adapted Message Handlers**
   - Adapted existing message handlers to use FastMCP's decorator-based approach
   - Implemented tool registration during app startup
   - Added support for dependency injection in tool handlers

5. **Added Test Script**
   - Created `examples/test_fastmcp.py` for testing the FastMCP implementation
   - Implemented tests for all exposed tools and capabilities
   - Added a run script `examples/run_fastmcp_test.sh`

## Exposed Tools

The following tools are exposed through the FastMCP interface:

### Budget Management
- `AllocateBudget` - Allocate token budget for a task
- `CheckBudget` - Check if a request is within budget limits
- `RecordUsage` - Record token usage for a request
- `GetBudgetStatus` - Get budget status for a component or tier

### Model Recommendations
- `GetModelRecommendations` - Get model recommendations based on budget and task
- `RouteWithBudgetAwareness` - Route to appropriate model based on budget awareness

### Analytics
- `GetUsageAnalytics` - Get token usage analytics

## Testing

To test the FastMCP implementation:

1. Start the Budget server:
   ```
   ./run_budget.sh
   ```

2. Run the FastMCP test script:
   ```
   ./examples/run_fastmcp_test.sh
   ```

## Backward Compatibility

The existing MCP implementation is maintained for backward compatibility. The FastMCP implementation runs in parallel, allowing for a smooth transition.

## Future Enhancements

1. Add more comprehensive documentation for each tool
2. Improve error handling and validation
3. Increase test coverage
4. Gradually phase out the legacy MCP implementation