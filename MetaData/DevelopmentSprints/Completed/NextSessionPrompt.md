# MCP Unified Integration Sprint - Next Session Prompt

## Current Project Status

We're implementing a unified Model Context Protocol (MCP) approach across all Tekton components, using FastMCP's decorator-based pattern. The project is a large sprint which requires methodical, step-by-step progress across multiple components. This is a continuation prompt for the next Claude Code session.

## Completed Work

1. **Core FastMCP Implementation**:
   - Added FastMCP as a dependency to tekton-core
   - Created FastMCP integration module with decorators, adapters, schemas, and client functionality
   - Defined JSON schemas for the MCP protocol
   - Created unit tests and example usage documentation
   
2. **Hermes Updates**:
   - Fixed MCP service initialization issues
   - Updated MCP endpoints with better error handling
   - Added health check endpoint
   - Integrated FastMCP implementation into Hermes

3. **Apollo Updates**:
   - Implemented FastMCP integration in Apollo core/mcp module
   - Added support for FastMCP tools in ApolloManager
   - Created MCP endpoints in Apollo API
   - Integrated standard MCP capabilities and tools
   - Updated API routes to include MCP router

4. **Shared MCP Utilities**:
   - Created common utilities in tekton-core/tekton/mcp/fastmcp/utils
   - Implemented shared endpoint creation and routing
   - Added tool registration utilities
   - Created standardized request and response handling
   - These utilities will simplify MCP implementation in remaining components

## Pending Tasks

The next session should work on updating another Tekton component with FastMCP. Specifically, it should focus on **Athena**:

1. **Update Athena with FastMCP Integration**:
   - Add FastMCP as a dependency to Athena
   - Create MCP module in Athena's core with tool definitions
   - Update Athena's API to include MCP endpoints
   - Implement core FastMCP functionality in Athena's entity_manager and query_engine
   - Leverage the shared MCP utilities for standardized implementation
   - Ensure backward compatibility with the existing MCP approach

After completing Athena, if time allows, proceed to implement FastMCP for the Budget component. There are numerous other components that will also need updates, but these should be tackled in future sessions.

## Additional Context

1. **Implementation Pattern**:
   - The implementation follows the pattern established in Apollo and Hermes
   - Each component should have a `core/mcp` module with tools and capabilities
   - API endpoints should include an MCP router
   - Component managers should implement methods for handling FastMCP requests
   - Use the shared MCP utilities from tekton-core for standardized implementation

2. **Shared MCP Utilities**:
   - `endpoints.py` - Utilities for creating MCP routers and endpoints
   - `tooling.py` - Tool registry and registration utilities
   - `requests.py` - Request validation and processing
   - `response.py` - Standardized response creation

3. **Testing Approach**:
   - Test each component's MCP implementation individually
   - Ensure backward compatibility with existing MCP approach
   - Verify that FastMCP tools are properly registered

4. **Integration Considerations**:
   - FastMCP is designed to work with Claude Code
   - The implementation should follow Single Port Architecture principles
   - Components should handle MCP requests via the standardized endpoints

## Handoff Instructions

The next Claude Code session should continue this methodical approach, focusing on one component at a time (starting with Athena). Each component should follow the same general pattern established in Apollo and Hermes, but using the shared utilities whenever possible to reduce duplication.

Due to the large scope of this sprint, the next session will also likely need to prepare for handoff, as there are many components that need to be updated. Please maintain the todo list and create a similar handoff document for subsequent sessions.

Remember that this is a carefully planned refactoring across many components, so a methodical approach with proper testing at each step is essential for success.