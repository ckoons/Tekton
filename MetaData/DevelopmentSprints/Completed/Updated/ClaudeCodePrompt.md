# Claude Code Prompt for MCP Unified Integration Sprint

## Context

You are assisting with implementing the MCP Unified Integration Sprint for Tekton, an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This sprint consolidates previously planned FastMCP_Sprint and MCP_Integration_Sprint efforts into a comprehensive MCP implementation across Tekton components.

Tekton's architecture consists of multiple components including Hermes (communication hub), Ergon (agent and tool management), Rhetor (LLM management), Engram (memory), and others. The current implementation has fragmented MCP implementation, separate registration systems, and inconsistent patterns across components.

## Goals

Your task is to implement the MCP Unified Integration plan, which includes:

1. Implementing a standardized MCP approach based on FastMCP's decorator pattern
2. Creating a unified registration protocol for both component and MCP registration
3. Fixing MCP service initialization and request routing
4. Implementing FastMCP across all active Tekton components
5. Ensuring Claude Code compatibility

## Current State

1. **tekton-core**: Has a custom MCP implementation that is verbose and difficult to maintain
2. **Hermes**: MCP service initialization issues ("MCP service not initialized" errors)
3. **Ergon**: External MCP server integration lacks standardized adapters
4. **Engram**: Full MCP implementation but uses custom approach
5. **Apollo**: Has an empty MCP placeholder file, missing implementation
6. **Athena**: Has API structure but no MCP endpoints
7. **Rhetor**: Minimal MCP implementation, needs standardization
8. **LLMAdapter**: Partial MCP implementation, needs standardization
9. **Harmonia, Prometheus, Sophia, Synthesis, etc.**: Other components require implementation
10. **Registration Issues**: Separate systems for component registration and MCP registration
11. **Cross-component Communication**: No standardized patterns for routing

## Component-Specific Implementation Guidance

### Core Infrastructure
- **tekton-core**: Implement the FastMCP foundation, focusing on decorator utilities and unified registration client
- **Hermes**: Create unified registration system, fix initialization issues, and implement request routing
- **Ergon**: Create adapter interfaces for external MCP servers, update tool management

### LLM Components
- **Rhetor**: Convert LLM tool definitions to use FastMCP decorators
- **LLMAdapter**: Standardize HTTP and WebSocket endpoints

### Memory and Knowledge Components
- **Engram**: Update memory access tools with FastMCP
- **Athena**: Convert knowledge graph tools to standard MCP
- **Metis**: Update monitoring capabilities

### Planning and Workflow Components
- **Prometheus**: Convert planning tools to FastMCP
- **Harmonia**: Update workflow state management
- **Synthesis**: Implement tool composition

### Specialized Components
- **Apollo**: Update predictive engine with MCP
- **Sophia**: Convert embedding tools to FastMCP
- **Telos**: Update task management tools

## Implementation Approach

The implementation will follow these phases:

1. **Phase 1**: Core Infrastructure and Unified Registration
   - Implement FastMCP in tekton-core
   - Create unified registration protocol in Hermes
   - Develop helper utilities and testing framework

2. **Phase 2**: Tier 1 & 2 Component Migration
   - Fix Hermes MCP service initialization
   - Migrate high-priority components (Ergon, Rhetor, Engram)
   - Implement request routing

3. **Phase 3**: Tier 3 & 4 Component Migration
   - Complete migration of remaining components
   - Implement component-specific patterns
   - Test cross-component interactions

4. **Phase 4**: Testing, Integration, and Documentation
   - Finalize Claude Code integration
   - Conduct comprehensive testing
   - Create documentation and examples

## Key Architectural Decisions

1. **Unified MCP Implementation**: Replace custom MCP with FastMCP-based approach
2. **Unified Registration Protocol**: Consolidate component and MCP registration into a single process
3. **Separation of Concerns**: Hermes for internal communication, Ergon for external integration
4. **Protocol-First Development**: Define interfaces and contracts before implementation
5. **Adapter Pattern**: Use adapter pattern for external MCP server integration
6. **Multi-Modal Capability Registry**: Track capabilities by modality for optimal routing
7. **Component-Specific Integration Patterns**: Define patterns based on component categories
8. **Authentication Integration**: Unified authentication across registration systems

## Branch Management

Before making any changes, verify you are on the correct branch:

```bash
scripts/github/tekton-branch-verify sprint/Clean_Slate_051125
```

All development should be conducted on this branch.

## FastMCP Implementation Guide

### Core Decorator Pattern

FastMCP uses Python decorators to define tools and capabilities. Here's a basic example:

```python
from fastmcp import mcp_server, tool

@mcp_server
class MyMCPServer:
    @tool
    def hello_world(self, name: str) -> str:
        """
        A simple greeting tool.
        
        Args:
            name: The name to greet
            
        Returns:
            A greeting message
        """
        return f"Hello, {name}!"
    
    @tool(tags=["math", "calculation"])
    def add_numbers(self, a: float, b: float) -> float:
        """
        Add two numbers together.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The sum of a and b
        """
        return a + b
```

### Unified Registration Implementation

For unified registration, we need to create a registration client that handles both component and MCP registration:

```python
from tekton.core.registration import UnifiedRegistrationClient

async def register_component():
    client = UnifiedRegistrationClient(
        component_id="my_component",
        name="My Component",
        version="1.0.0",
        capabilities=["capability1", "capability2"],
        mcp_tools=[add_numbers, hello_world],  # These are FastMCP decorated functions
        host="localhost",
        port=8000
    )
    
    # Register both component and MCP capabilities
    registration_result = await client.register_with_hermes()
    
    return registration_result
```

## First Steps

1. Set up the development environment and verify correct branch
2. Understand existing MCP implementation across components
3. Begin implementing FastMCP integration in tekton-core
4. Implement unified registration protocol in Hermes
5. Start migrating high-priority components

## Component Migration Template

For each component, follow these steps to migrate to FastMCP:

1. Add FastMCP dependency to component requirements
2. Create a dedicated MCP module if not exists
3. Define tools and capabilities using FastMCP decorators
4. Implement unified registration with Hermes
5. Add tests for tool execution and registration
6. Update documentation with new patterns

Example migration for a component:

```python
# Before migration
class ComponentTool:
    def __init__(self):
        self.name = "example_tool"
        self.description = "An example tool"
        
    def execute(self, param1, param2):
        return {"result": param1 + param2}

# After migration with FastMCP
from fastmcp import mcp_server, tool
from tekton.core.registration import UnifiedRegistrationClient

@mcp_server
class ComponentMCPServer:
    @tool(tags=["example", "addition"])
    def example_tool(self, param1: int, param2: int) -> dict:
        """
        An example tool that adds two numbers.
        
        Args:
            param1: First parameter
            param2: Second parameter
            
        Returns:
            Dict containing the result
        """
        return {"result": param1 + param2}
    
# Registration
async def register_with_hermes():
    client = UnifiedRegistrationClient(
        component_id="my_component",
        name="My Component",
        version="1.0.0",
        capabilities=["example"],
        mcp_server=ComponentMCPServer(),
        host="localhost",
        port=8000
    )
    
    return await client.register()
```

## Testing Guide

When implementing tests for the MCP implementation, follow these guidelines:

1. **Unit Tests**:
   - Test each FastMCP decorator implementation
   - Validate tool registration functionality
   - Test message processing pipeline
   - Use mock objects for external dependencies

2. **Integration Tests**:
   - Test component registration with actual Hermes instance
   - Test cross-component tool discovery and execution
   - Verify routing of MCP messages through the system
   - Test failover and error recovery scenarios

3. **Test Structure**:
   - Create test files in a `tests/mcp` directory within each component
   - Name test files based on functionality being tested (e.g., `test_registration.py`)
   - Use fixtures for common setup and teardown
   - Include both positive and negative test cases

## Deliverables

Your implementation should result in:

1. Unified registration protocol implementation in Hermes
2. FastMCP integration in tekton-core
3. Component-specific MCP implementations for all active components
4. Working cross-component MCP communication
5. Integration patterns for external MCP servers
6. Claude Code compatibility
7. Comprehensive tests and documentation

## References

- [Sprint Plan](/tmp/updated-sprint-docs/SprintPlan.md)
- [Architectural Decisions](/tmp/updated-sprint-docs/ArchitecturalDecisions.md)
- [Implementation Plan](/tmp/updated-sprint-docs/ImplementationPlan.md)
- [FastMCP Documentation](https://gofastmcp.com)
- [Model Context Protocol](https://modelcontextprotocol.io)