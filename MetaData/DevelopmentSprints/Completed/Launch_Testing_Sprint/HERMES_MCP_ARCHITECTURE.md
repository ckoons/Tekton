# Hermes MCP Architecture in Tekton

This document describes the Multimodal Cognitive Protocol (MCP) architecture in the Tekton system, focusing on Hermes's role as the central hub and the current implementation status.

## Overview

Tekton's MCP implementation follows a **hub-and-spoke architecture** with Hermes serving as the central MCP gateway. This design provides a unified interface for multimodal communication across all Tekton components while simplifying individual component implementations.

## Architecture Design

### 1. Hermes as the Central MCP Hub

Hermes serves as the centralized MCP hub with the following responsibilities:

- **Capability Aggregation**: Collects and exposes capabilities from all registered components
- **Request Routing**: Routes MCP requests to appropriate specialized components
- **Response Aggregation**: Combines responses from multiple components when needed
- **Service Discovery**: Maintains a registry of component capabilities
- **Component Lifecycle Management**: Can optionally manage component lifecycle

### 2. Component-Specific MCP Implementation

While Hermes provides centralized access, Engram has its own direct MCP implementation:

- **Engram**: Implements direct MCP endpoints for memory and knowledge management
- **Reason**: Specialized memory operations benefit from direct access without routing through Hermes
- **Usage Pattern**: Can be accessed directly or through Hermes based on client needs

### 3. Other Component Access

All other Tekton components (Rhetor, Prometheus, Harmonia, etc.) are accessed through Hermes:

- **No Direct MCP Implementation**: These components don't need to implement MCP endpoints directly
- **Service Registration**: They register their capabilities with Hermes at startup
- **Simplified Integration**: Reduces code duplication and standardizes communication

## MCP Endpoint Structure

### Hermes MCP Endpoints

```
http://localhost:8001/api/mcp/capabilities   - Returns supported modalities and capabilities
http://localhost:8001/api/mcp/process        - Processes a multimodal request
http://localhost:8001/api/mcp/contexts/{id}  - Manages conversation/processing contexts
http://localhost:8001/api/mcp/tools          - Lists available tools
```

### Engram MCP Endpoints

```
http://localhost:8000/api/mcp/capabilities   - Returns memory-specific capabilities
http://localhost:8000/api/mcp/process        - Processes memory-related requests
http://localhost:8000/api/mcp/contexts/{id}  - Manages memory contexts
```

## Implementation Status

Current status of MCP implementation in Tekton components:

| Component | Port | MCP Status | Notes |
|-----------|------|------------|-------|
| Hermes    | 8001 | ✅ Implemented | Central MCP hub at `/api/mcp/*` |
| Engram    | 8000 | ✅ Implemented | Has dedicated MCP implementation |
| Rhetor    | 8003 | ✅ Via Hermes | Capabilities accessed through Hermes |
| Prometheus | 8006 | ✅ Via Hermes | Capabilities accessed through Hermes |
| Harmonia  | 8007 | ✅ Via Hermes | Capabilities accessed through Hermes |
| Telos     | 8008 | ✅ Via Hermes | Capabilities accessed through Hermes |
| Synthesis | 8009 | ✅ Via Hermes | Capabilities accessed through Hermes |

## Client Access Pattern

Clients can access MCP capabilities through:

### 1. Hermes Centralized Access (Recommended)

```python
async def process_request(content):
    """Process a request through Hermes MCP hub."""
    async with aiohttp.ClientSession() as session:
        request_data = {
            "content": [
                {
                    "type": "text",
                    "format": "text/plain",
                    "data": content
                }
            ]
        }
        
        async with session.post(
            "http://localhost:8001/api/mcp/process",
            json=request_data
        ) as response:
            return await response.json()
```

### 2. Direct Component Access (For Engram only)

```python
async def query_memory(query):
    """Query Engram memory directly through MCP."""
    async with aiohttp.ClientSession() as session:
        request_data = {
            "content": [
                {
                    "type": "text",
                    "format": "text/plain",
                    "data": query
                }
            ],
            "processing": {
                "type": "memory_query"
            }
        }
        
        async with session.post(
            "http://localhost:8000/api/mcp/process",
            json=request_data
        ) as response:
            return await response.json()
```

## Advantages of Hub-and-Spoke Architecture

1. **Simplified Client Integration**: Clients only need to interact with a single MCP endpoint
2. **Unified Capabilities**: All component capabilities exposed through a single interface
3. **Reduced Implementation Burden**: Components don't all need to implement full MCP
4. **Centralized Orchestration**: Hermes can coordinate complex multi-component tasks
5. **Better Resource Management**: Control and optimize resource allocation for MCP processing

## Future Enhancements

1. **Client Libraries**: Create standardized MCP client libraries for Python and JavaScript
2. **Advanced Routing**: Implement capability-based routing for optimal component selection
3. **Performance Metrics**: Add performance tracking to optimize request routing
4. **Authentication**: Implement standardized authentication for MCP endpoints
5. **Automatic Capability Discovery**: Enhance registration to auto-detect component capabilities

## Conclusion

The current Hermes-centered MCP architecture provides a solid foundation for multimodal communication within Tekton. By centralizing MCP access through Hermes while allowing specialized components like Engram to have direct implementations, we achieve a balance of efficiency, modularity, and ease of integration. This architecture will enable Tekton components to handle increasingly complex multimodal tasks as the system evolves.