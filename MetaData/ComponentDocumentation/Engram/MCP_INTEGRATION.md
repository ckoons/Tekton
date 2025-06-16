# Engram Component - FastMCP Integration

This document describes the FastMCP integration for the Engram component.

## Overview

The Engram component now supports the Model Context Protocol (MCP) using FastMCP's decorator-based approach. This integration allows the Engram component to expose its memory and related capabilities to other components in a standardized way.

## Implementation

The FastMCP integration includes:

1. **FastMCP as a Dependency**
   - Added tekton-core as a dependency in requirements.txt and setup.py
   - FastMCP is part of the tekton-core package

2. **MCP Module in Engram Core**
   - Created an MCP module in `engram/core/mcp/`
   - Implemented tool definitions using FastMCP decorators
   - Exposed capabilities for memory operations, structured memory operations, and Nexus processing

3. **New FastMCP Server**
   - Created a new FastMCP server in `engram/api/fastmcp_server.py`
   - Maintained backward compatibility with existing MCP server
   - Added standard MCP endpoints:
     - `/mcp/health` - Health check endpoint
     - `/mcp/capabilities` - Capabilities endpoint
     - `/mcp/tools` - Tools endpoint
     - `/mcp/process` - Process endpoint

4. **FastMCP Adapter**
   - Created a FastMCP adapter in `engram/core/fastmcp_adapter.py`
   - Implemented modern decorator-based approach for handling requests
   - Added support for dependency injection in tool handlers

5. **Added Test Script**
   - Created `examples/test_fastmcp.py` for testing the FastMCP implementation
   - Implemented tests for all exposed tools and capabilities
   - Added a run script `examples/run_fastmcp_test.sh`

## Exposed Tools

The following tools are exposed through the FastMCP interface:

### Memory Operations
- `MemoryStore` - Store information in Engram's memory system
- `MemoryQuery` - Query Engram's memory system for relevant information
- `GetContext` - Get formatted memory context across multiple namespaces

### Structured Memory Operations
- `StructuredMemoryAdd` - Add a memory to the structured memory system
- `StructuredMemoryGet` - Get a memory from the structured memory system by ID
- `StructuredMemoryUpdate` - Update a memory in the structured memory system
- `StructuredMemoryDelete` - Delete a memory from the structured memory system
- `StructuredMemorySearch` - Search for memories in the structured memory system

### Nexus Operations
- `NexusProcess` - Process a message through the Nexus interface

## Running the FastMCP Server

To run the FastMCP server:

```
./run_fastmcp.sh
```

This will start the server on port 8001 by default. You can customize the port using the ENGRAM_PORT environment variable:

```
ENGRAM_PORT=8005 ./run_fastmcp.sh
```

## Testing

To test the FastMCP implementation:

1. Start the FastMCP server:
   ```
   ./run_fastmcp.sh
   ```

2. Run the FastMCP test script:
   ```
   ./examples/run_fastmcp_test.sh
   ```

## Backward Compatibility

The existing MCP implementation is maintained for backward compatibility in `engram/api/mcp_server.py`. The new FastMCP implementation runs independently in `engram/api/fastmcp_server.py`, allowing for a smooth transition.

## Future Enhancements

1. Add more comprehensive documentation for each tool
2. Improve error handling and validation
3. Increase test coverage
4. Gradually phase out the legacy MCP implementation in favor of FastMCP
5. Add support for unified authentication and authorization