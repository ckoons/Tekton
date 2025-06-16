# Claude Code Prompt for MCP External Integration Sprint

## Context

You are assisting with implementing the MCP External Integration Sprint for Tekton, an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This sprint focuses on creating a universal adapter framework for external MCP services, building on the foundation established by the MCP Unified Integration Sprint.

Tekton's architecture includes multiple components, with Ergon serving as the nexus for agents, workflows, tools, and MCP integration. Hermes functions as the central registry and communication hub, providing database services. The current implementation has established a standardized MCP approach using FastMCP, but needs a flexible, future-proof way to integrate with external MCP services.

## Goals

Your task is to implement the universal MCP adapter framework, which includes:

1. Creating core interfaces and adapter base classes in tekton-core
2. Implementing capability registry in Hermes
3. Developing universal MCP client in Ergon
4. Creating reference adapters for key external MCP services
5. Implementing capability composition and security model
6. Developing comprehensive testing infrastructure

## Current State

1. **tekton-core**: Has FastMCP-based MCP implementation but lacks adapter framework
2. **Hermes**: Provides component registry but needs capability registry extension
3. **Ergon**: Serves as MCP integration point but uses direct implementation
4. **External MCP Services**: Various implementations with different interfaces and capabilities
5. **Security Model**: Limited sandboxing and permission management for external tools
6. **Tool Discovery**: No standardized way to discover and integrate external tools

## Universal Adapter Approach

Rather than directly implementing specific external MCP projects, you will create a universal adapter framework that:

1. Defines stable interfaces for Tekton components
2. Creates adapter implementations for different MCP services
3. Handles protocol differences and version variations
4. Supports multiple implementations simultaneously
5. Provides comprehensive security and monitoring

## Implementation Approach

The implementation will follow this approach:

### Phase 1: Core Framework
- Implement `MCPInterface` and `MCPAdapter` base classes in tekton-core
- Create `CapabilityRegistry` in Hermes
- Develop `UniversalMCPClient` in Ergon

### Phase 2: Reference Adapters
- Implement Claude Desktop adapter
- Create Brave Search adapter
- Develop GitHub MCP adapter

### Phase 3: Capability Composition
- Implement capability discovery and search
- Create capability composition engine
- Develop application-specific packagers

### Phase 4: Security and Testing
- Implement security model with sandboxing
- Create comprehensive testing framework
- Develop documentation and examples

## Key Interfaces and Classes

### MCPInterface (tekton-core/tekton/mcp/interface.py)

```python
from typing import Dict, List, Any, Optional

class MCPInterface:
    """Core interface for MCP functionality within Tekton."""
    
    async def discover_tools(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Discover available tools, optionally filtered."""
        raise NotImplementedError("Subclasses must implement discover_tools")
    
    async def execute_tool(self, tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by ID with the given parameters."""
        raise NotImplementedError("Subclasses must implement execute_tool")
    
    async def register_tool(self, tool_spec: Dict[str, Any]) -> str:
        """Register a tool with the MCP system."""
        raise NotImplementedError("Subclasses must implement register_tool")
    
    async def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get tool information by ID."""
        raise NotImplementedError("Subclasses must implement get_tool")
```

### MCPAdapter (tekton-core/tekton/mcp/adapter.py)

```python
from typing import Dict, List, Any, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

class MCPAdapter:
    """Base adapter for external MCP implementations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the adapter with configuration."""
        self.config = config
        self.connected = False
        self.adapter_id = str(uuid.uuid4())
    
    async def connect(self) -> bool:
        """Establish connection to external MCP system."""
        raise NotImplementedError("Subclasses must implement connect")
    
    async def disconnect(self) -> bool:
        """Disconnect from external MCP system."""
        raise NotImplementedError("Subclasses must implement disconnect")
    
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available tools in the external MCP system."""
        raise NotImplementedError("Subclasses must implement discover_tools")
    
    async def execute_tool(self, tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool in the external MCP system."""
        raise NotImplementedError("Subclasses must implement execute_tool")
    
    async def translate_tool_spec(self, tekton_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Translate Tekton tool spec to external system format."""
        raise NotImplementedError("Subclasses must implement translate_tool_spec")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of external MCP system."""
        raise NotImplementedError("Subclasses must implement health_check")
```

## Implementation Tasks

### Task 1: Core Interface Implementation

Implement the core interfaces in tekton-core:

1. Create `MCPInterface` with methods for tool discovery, execution, and management
2. Implement `MCPAdapter` base class for external MCP service adapters
3. Define data models for capability representation
4. Create utilities for protocol normalization and version negotiation

Example:
```python
# In tekton-core/tekton/mcp/models.py
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

class ToolDefinition(BaseModel):
    """Model for MCP tool definition."""
    id: str
    name: str
    description: str
    schema: Dict[str, Any]
    categories: List[str] = []
    version: Optional[str] = None
    adapter_id: Optional[str] = None
    external_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
```

### Task 2: Capability Registry in Hermes

Extend Hermes to serve as the capability registry:

1. Create `CapabilityRegistry` class in Hermes
2. Implement database schema for storing capabilities
3. Develop search and matching algorithms
4. Create registry API endpoints
5. Implement WebSocket events for registry updates

Example:
```python
# In Hermes/hermes/core/capability_registry.py
class CapabilityRegistry:
    """Registry for MCP capabilities across multiple adapters."""
    
    def __init__(self, db_service):
        """Initialize with database service."""
        self.db = db_service
        
    async def register_adapter(self, adapter_info: Dict[str, Any]) -> str:
        """Register an MCP adapter."""
        # Implementation details...
        
    async def register_tool(self, tool_id: str, tool_spec: Dict[str, Any], adapter_id: str) -> str:
        """Register an MCP tool."""
        # Implementation details...
        
    async def search_tools(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for tools matching filters."""
        # Implementation details...
```

### Task 3: Universal MCP Client in Ergon

Implement the universal client in Ergon:

1. Create `UniversalMCPClient` that implements `MCPInterface`
2. Implement adapter management and registration
3. Develop tool execution routing
4. Create error handling and retry mechanisms
5. Implement result normalization

Example:
```python
# In Ergon/ergon/core/universal_mcp_client.py
class UniversalMCPClient(MCPInterface):
    """Client that manages multiple MCP adapters."""
    
    def __init__(self, hermes_client):
        """Initialize with Hermes client for registry access."""
        self.adapters = {}  # adapter_id -> adapter instance
        self.tools = {}  # tool_id -> (adapter_id, external_tool_id)
        self.hermes_client = hermes_client
        
    async def register_adapter(self, adapter: MCPAdapter) -> str:
        """Register an adapter for a specific MCP implementation."""
        # Implementation details...
        
    async def discover_tools(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Discover available tools, optionally filtered."""
        # Implementation details...
        
    async def execute_tool(self, tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool using the appropriate adapter."""
        # Implementation details...
```

### Task 4: Reference Adapter Implementations

Create reference adapters for key external MCP services:

1. Implement Claude Desktop adapter
2. Create Brave Search adapter
3. Develop GitHub MCP adapter
4. Implement connection and authentication
5. Create tool discovery and execution methods

Example:
```python
# In Ergon/ergon/adapters/claude_desktop_adapter.py
import aiohttp
from tekton.mcp.adapter import MCPAdapter

class ClaudeDesktopAdapter(MCPAdapter):
    """Adapter for Claude Desktop MCP."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration."""
        super().__init__(config)
        self.base_url = f"http://{config.get('host', 'localhost')}:{config.get('port', 8000)}"
        self.timeout = config.get("timeout", 30)
        self.session = None
        
    async def connect(self) -> bool:
        """Establish connection to Claude Desktop MCP."""
        # Implementation details...
        
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available tools in Claude Desktop MCP."""
        # Implementation details...
        
    async def execute_tool(self, tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool in Claude Desktop MCP."""
        # Implementation details...
```

### Task 5: Security Framework

Implement the security model for external tools:

1. Create `SecurityManager` for permission management
2. Implement sandboxing for tool execution
3. Create audit logging system
4. Develop permission checking and enforcement
5. Implement resource usage limits

Example:
```python
# In Ergon/ergon/core/security_manager.py
class SecurityManager:
    """Security manager for external MCP tools."""
    
    def __init__(self, db_service):
        """Initialize with database service."""
        self.db = db_service
        
    async def check_permission(self, user_id: str, tool_id: str, action: str) -> bool:
        """Check if user has permission for action on tool."""
        # Implementation details...
        
    async def log_access(self, user_id: str, tool_id: str, action: str, parameters: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Log tool access for audit purposes."""
        # Implementation details...
        
    async def create_sandbox(self, tool_id: str) -> Dict[str, Any]:
        """Create sandbox environment for tool execution."""
        # Implementation details...
```

### Task 6: Capability Composition

Implement capability composition engine:

1. Create `CapabilityComposer` for combining capabilities
2. Implement composition rules and patterns
3. Develop data transformation utilities
4. Create template system for common compositions
5. Implement execution flow management

Example:
```python
# In Ergon/ergon/core/capability_composer.py
class CapabilityComposer:
    """Engine for combining MCP capabilities."""
    
    def __init__(self, universal_client):
        """Initialize with universal MCP client."""
        self.client = universal_client
        
    async def compose_capabilities(self, composition: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a capability composition with input data."""
        # Implementation details...
        
    async def load_template(self, template_id: str) -> Dict[str, Any]:
        """Load a composition template by ID."""
        # Implementation details...
        
    async def save_template(self, template: Dict[str, Any]) -> str:
        """Save a composition template."""
        # Implementation details...
```

### Task 7: Testing Framework

Develop comprehensive testing infrastructure:

1. Create mock adapters for testing
2. Implement contract tests for adapter validation
3. Develop integration tests with real services
4. Create performance and security testing utilities
5. Implement CI/CD integration

Example:
```python
# In tekton-core/tekton/mcp/testing/mock_adapter.py
from tekton.mcp.adapter import MCPAdapter

class MockMCPAdapter(MCPAdapter):
    """Mock adapter for testing."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration."""
        super().__init__(config)
        self.tools = config.get("tools", [])
        self.responses = config.get("responses", {})
        self.errors = config.get("errors", {})
        self.connected = False
        
    async def connect(self) -> bool:
        """Establish mock connection."""
        self.connected = True
        return True
        
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """Return configured mock tools."""
        return self.tools
        
    async def execute_tool(self, tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Return configured mock response for tool."""
        if tool_id in self.errors:
            raise ValueError(self.errors[tool_id])
        return self.responses.get(tool_id, {"result": f"Mock result for {tool_id}"})
```

## Testing Strategy

When implementing this sprint, follow these testing guidelines:

1. **Unit Testing**:
   - Test all interface implementations
   - Test adapter functionality in isolation
   - Test capability registry operations
   - Test security model enforcement

2. **Integration Testing**:
   - Test adapter registration with Hermes
   - Test capability discovery and search
   - Test cross-adapter execution
   - Test security boundaries

3. **End-to-End Testing**:
   - Test with real external MCP services
   - Test complete workflows using composed capabilities
   - Test error handling and recovery
   - Test security under various conditions

4. **Performance Testing**:
   - Test adapter overhead
   - Test capability registry performance
   - Test concurrent execution
   - Test under load

## First Steps

1. Set up the development environment and verify correct branch
2. Implement core interfaces and adapter base classes
3. Create capability registry in Hermes
4. Develop universal MCP client in Ergon
5. Implement the first reference adapter (Claude Desktop)

## Deliverables

Your implementation should result in:

1. Core interfaces in tekton-core
2. Capability registry in Hermes
3. Universal MCP client in Ergon
4. Reference adapters for key external services
5. Security framework implementation
6. Capability composition engine
7. Comprehensive testing infrastructure
8. Complete documentation

## References

- [Sprint Plan](/tmp/mcp-external-docs/SprintPlan.md)
- [Architectural Decisions](/tmp/mcp-external-docs/ArchitecturalDecisions.md)
- [Implementation Plan](/tmp/mcp-external-docs/ImplementationPlan.md)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Claude Desktop MCP Documentation](https://docs.anthropic.com/claude/reference/mcp)