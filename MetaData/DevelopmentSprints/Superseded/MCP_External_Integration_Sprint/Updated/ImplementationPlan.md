# Implementation Plan: MCP External Integration

This document outlines the detailed implementation plan for the MCP External Integration Sprint, focusing on creating a universal adapter framework for external MCP services.

## Core Components and Changes

### 1. tekton-core MCP Implementation

#### 1.1 FastMCP Interface
- Create `MCPInterface` in tekton-core/tekton/mcp/interface.py
- Implement `MCPAdapter` base class in tekton-core/tekton/mcp/adapter.py
- Define data models for capability representation
- Create utility functions for protocol normalization
- Implement version negotiation logic

#### 1.2 Core Utilities
- Implement capability matching and scoring
- Create modality-specific registries
- Add security and sandboxing utilities
- Develop testing utilities for adapters
- Implement decorator-to-schema translation

#### 1.3 Token Management Integration
- Create token tracking decorators in tekton-core/tekton/mcp/budget.py
- Implement token estimation utilities
- Develop budget integration interfaces
- Add token usage reporting capabilities
- Create monitoring and alerting interfaces

### 2. Hermes Capability Registry

#### 2.1 Registry Implementation
- Create `CapabilityRegistry` in Hermes/hermes/core/capability_registry.py
- Extend database schema for capability storage
- Implement capability indexing and search
- Create health monitoring system
- Develop capability versioning

#### 2.2 Search and Matching
- Implement capability search algorithms
- Create semantic matching utilities
- Develop recommendation engine
- Implement intent-based discovery
- Create filtering and pagination

#### 2.3 Registry API
- Create API endpoints for registry operations
- Implement WebSocket events for registry updates
- Develop client libraries for registry access
- Add documentation and examples
- Implement performance optimizations

### 3. Universal MCP Client in Ergon

#### 3.1 Client Implementation
- Create `UniversalMCPClient` in Ergon/ergon/core/universal_mcp_client.py
- Implement adapter management and registration
- Develop tool execution routing
- Create error handling and retry mechanisms
- Implement result normalization

#### 3.2 Adapter Management
- Create adapter discovery and registration system
- Implement adapter versioning and compatibility checking
- Develop adapter health monitoring
- Add adapter configuration management
- Create adapter lifecycle hooks

#### 3.3 Token Budget Integration
- Implement token usage tracking in client
- Create integration with Budget component
- Develop token usage estimation for external tools
- Add budget constraints enforcement
- Implement usage reporting and analytics

### 4. Reference Adapter Implementations

#### 4.1 Claude Desktop Adapter
- Create `ClaudeDesktopAdapter` in Ergon/ergon/adapters/claude_desktop_adapter.py
- Implement connection and authentication
- Create tool discovery methods
- Implement tool execution logic
- Add token usage tracking and reporting

#### 4.2 Brave Search Adapter
- Create `BraveSearchAdapter` in Ergon/ergon/adapters/brave_search_adapter.py
- Implement connection and authentication
- Create search capability methods
- Develop result processing and normalization
- Implement token usage tracking

#### 4.3 GitHub MCP Adapter
- Create `GitHubMCPAdapter` in Ergon/ergon/adapters/github_adapter.py
- Implement connection and authentication
- Create repository access methods
- Develop code search and management capabilities
- Add token usage tracking for API calls

### 5. Capability Composition

#### 5.1 Composition Engine
- Create `CapabilityComposer` in Ergon/ergon/core/capability_composer.py
- Implement composition rules and patterns
- Develop data transformation utilities
- Create flow control mechanisms
- Add error handling for composition
- Implement token cost estimation for compositions

#### 5.2 Composition Templates
- Create template system for common compositions
- Implement template validation
- Develop template storage and retrieval
- Add documentation and examples
- Create visual representation utilities

#### 5.3 Application Packagers
- Create domain-specific capability bundles
- Implement configuration simplification
- Develop package documentation generators
- Add usage examples
- Create deployment utilities
- Implement budget constraints for packages

### 6. Security Framework

#### 6.1 Permission Model
- Create `SecurityManager` in Ergon/ergon/core/security_manager.py
- Implement permission definitions and checking
- Develop user-specific permission profiles
- Create permission inheritance rules
- Add audit logging for permission checks
- Implement budget-related permissions

#### 6.2 Sandboxing
- Implement tool execution sandboxing
- Create resource usage limits
- Develop network access controls
- Add execution monitoring
- Implement timeout handling
- Enforce budget constraints in sandbox

#### 6.3 Audit System
- Create comprehensive audit logging
- Implement structured log format
- Develop log storage and retrieval
- Add log filtering and analysis
- Create alert mechanisms for suspicious activity
- Implement token usage auditing

### 7. Budget Component Integration

#### 7.1 Token Tracking
- Implement token tracking in Budget component
- Create per-adapter token usage tracking
- Develop token estimation for external services
- Add tracking of composed capability costs
- Implement token usage analytics

#### 7.2 Budget Management
- Create budget allocation for external services
- Implement budget enforcement mechanisms
- Develop budget notification system
- Add budget approval workflows
- Create budget reporting dashboards

#### 7.3 Cost Optimization
- Implement cost-based routing for capabilities
- Create capability cost comparison utilities
- Develop cost-saving recommendations
- Add cost optimization for composed capabilities
- Implement adaptive budgeting

### 8. Testing Framework

#### 8.1 Mock Adapters
- Create mock adapter implementations for testing
- Implement configurable behavior and responses
- Develop testing utilities for adapters
- Add simulation of error conditions
- Create performance testing configurations
- Implement token usage simulation

#### 8.2 Contract Tests
- Implement contract test suite for adapters
- Create validation for adapter behavior
- Develop automated testing for new adapters
- Add compatibility testing
- Create documentation for contract compliance
- Implement budget integration testing

#### 8.3 Integration Tests
- Implement integration tests with real external services
- Create testing infrastructure for end-to-end tests
- Develop performance benchmarking
- Add security testing
- Create CI/CD integration
- Implement budget and token tracking testing

## Implementation Phases

### Phase 1: Core MCP Adapter Framework (Days 1-5)

#### Days 1-2: Interface Design and Core Architecture
- Task 1.1: Create interface and adapter base classes in tekton-core
- Task 1.2: Implement data models for capability representation
- Task 1.3: Define adapter lifecycle and management protocols
- Task 1.4: Create utility functions for protocol normalization
- Task 1.5: Implement version negotiation logic
- Task 1.6: Design token tracking and budget integration

#### Days 3-5: Hermes Capability Registry and Universal Client
- Task 2.1: Implement CapabilityRegistry in Hermes
- Task 2.2: Extend database schema for capability storage
- Task 2.3: Create UniversalMCPClient in Ergon
- Task 2.4: Implement adapter registration and discovery
- Task 2.5: Develop basic testing utilities
- Task 2.6: Create Budget integration interfaces

### Phase 2: Reference Adapter Implementations (Days 6-10)

#### Days 6-7: Claude Desktop Adapter
- Task 3.1: Create Claude Desktop adapter implementation
- Task 3.2: Implement connection and authentication
- Task 3.3: Develop tool discovery and registration
- Task 3.4: Implement tool execution logic
- Task 3.5: Add error handling and tests
- Task 3.6: Implement token usage tracking

#### Days 8-9: Brave Search and GitHub Adapters
- Task 4.1: Create Brave Search adapter implementation
- Task 4.2: Implement GitHub MCP adapter
- Task 4.3: Develop shared utilities for common adapter functionality
- Task 4.4: Add authentication and error handling
- Task 4.5: Implement adapter-specific tests
- Task 4.6: Add token usage tracking for each adapter

#### Day 10: Adapter Integration and Testing
- Task 5.1: Integrate adapters with UniversalMCPClient
- Task 5.2: Test cross-adapter capabilities
- Task 5.3: Implement performance optimizations
- Task 5.4: Add documentation for adapter implementations
- Task 5.5: Create examples for adapter usage
- Task 5.6: Test Budget integration with adapters

### Phase 3: Capability Discovery and Composition (Days 11-15)

#### Days 11-12: Advanced Capability Discovery
- Task 6.1: Implement semantic search over capabilities
- Task 6.2: Create capability categorization and tagging
- Task 6.3: Develop capability recommendation engine
- Task 6.4: Implement intent-based discovery
- Task 6.5: Add tests for search and discovery
- Task 6.6: Implement cost-aware discovery

#### Days 13-15: Capability Composition
- Task 7.1: Create CapabilityComposer for combining capabilities
- Task 7.2: Implement composition rules and patterns
- Task 7.3: Develop data transformation between capabilities
- Task 7.4: Create composition templates for common patterns
- Task 7.5: Implement testing for composed capabilities
- Task 7.6: Add token cost estimation for composed capabilities

### Phase 4: Security and Comprehensive Testing (Days 16-20)

#### Days 16-17: Security Framework
- Task 8.1: Implement SecurityManager with permission model
- Task 8.2: Create sandboxing for external tool execution
- Task 8.3: Implement audit logging system
- Task 8.4: Add rate limiting and resource controls
- Task 8.5: Develop security testing suite
- Task 8.6: Implement budget-based access controls

#### Days 18-19: Comprehensive Testing
- Task 9.1: Create mock adapters for testing all scenarios
- Task 9.2: Implement contract tests for adapter validation
- Task 9.3: Develop integration tests with real services
- Task 9.4: Add performance and load testing
- Task 9.5: Create security validation tests
- Task 9.6: Implement budget constraint testing

#### Day 20: Documentation and Final Integration
- Task 10.1: Create comprehensive documentation
- Task 10.2: Develop examples for common use cases
- Task 10.3: Add integration guides for Tekton components
- Task 10.4: Create adapter development guide
- Task 10.5: Document Budget integration patterns
- Task 10.6: Finalize testing and prepare for release

## Technical Specifications

### 1. Core Interfaces

#### 1.1 MCPInterface (tekton-core/tekton/mcp/interface.py)
```python
from typing import Dict, List, Any, Optional
import uuid
import asyncio

class MCPInterface:
    """Core interface for MCP functionality within Tekton."""
    
    async def discover_tools(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Discover available tools, optionally filtered.
        
        Args:
            filters: Optional filters for capability discovery
            
        Returns:
            List of tool definitions
        """
        raise NotImplementedError("Subclasses must implement discover_tools")
    
    async def execute_tool(self, tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by ID with the given parameters.
        
        Args:
            tool_id: Identifier for the tool to execute
            parameters: Parameters to pass to the tool
            
        Returns:
            Tool execution result
        """
        raise NotImplementedError("Subclasses must implement execute_tool")
    
    async def register_tool(self, tool_spec: Dict[str, Any]) -> str:
        """
        Register a tool with the MCP system.
        
        Args:
            tool_spec: Tool specification
            
        Returns:
            Generated tool ID
        """
        raise NotImplementedError("Subclasses must implement register_tool")
    
    async def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get tool information by ID.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            Tool specification or None if not found
        """
        raise NotImplementedError("Subclasses must implement get_tool")
    
    async def get_token_usage(self, tool_id: str) -> Dict[str, Any]:
        """
        Get token usage information for a tool.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            Token usage information
        """
        raise NotImplementedError("Subclasses must implement get_token_usage")
```

#### 1.2 MCPAdapter (tekton-core/tekton/mcp/adapter.py)
```python
from typing import Dict, List, Any, Optional
import uuid
import asyncio
import logging

logger = logging.getLogger(__name__)

class MCPAdapter:
    """Base adapter for external MCP implementations."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the adapter with configuration.
        
        Args:
            config: Adapter configuration
        """
        self.config = config
        self.connected = False
        self.adapter_id = str(uuid.uuid4())
        self.token_tracker = None
    
    async def connect(self) -> bool:
        """
        Establish connection to external MCP system.
        
        Returns:
            True if connection successful
        """
        raise NotImplementedError("Subclasses must implement connect")
    
    async def disconnect(self) -> bool:
        """
        Disconnect from external MCP system.
        
        Returns:
            True if disconnection successful
        """
        raise NotImplementedError("Subclasses must implement disconnect")
    
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Discover available tools in the external MCP system.
        
        Returns:
            List of tool definitions
        """
        raise NotImplementedError("Subclasses must implement discover_tools")
    
    async def execute_tool(self, tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool in the external MCP system.
        
        Args:
            tool_id: Identifier for the tool to execute
            parameters: Parameters to pass to the tool
            
        Returns:
            Tool execution result
        """
        raise NotImplementedError("Subclasses must implement execute_tool")
    
    async def translate_tool_spec(self, tekton_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate Tekton tool spec to external system format.
        
        Args:
            tekton_spec: Tekton tool specification
            
        Returns:
            External system tool specification
        """
        raise NotImplementedError("Subclasses must implement translate_tool_spec")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of external MCP system.
        
        Returns:
            Health status information
        """
        raise NotImplementedError("Subclasses must implement health_check")
    
    async def estimate_token_usage(self, tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate token usage for tool execution.
        
        Args:
            tool_id: Identifier for the tool
            parameters: Parameters for the tool
            
        Returns:
            Estimated token usage information
        """
        raise NotImplementedError("Subclasses must implement estimate_token_usage")
    
    async def register_token_tracker(self, tracker) -> None:
        """
        Register a token tracking system with this adapter.
        
        Args:
            tracker: Token tracking system
        """
        self.token_tracker = tracker
```

### 2. Universal MCP Client

```python
from typing import Dict, List, Any, Optional
import uuid
import asyncio
import logging
from tekton.mcp.interface import MCPInterface
from tekton.mcp.adapter import MCPAdapter

logger = logging.getLogger(__name__)

class UniversalMCPClient(MCPInterface):
    """Client that manages multiple MCP adapters."""
    
    def __init__(self, hermes_client, budget_client=None):
        """
        Initialize with Hermes client for registry access and optional Budget client.
        
        Args:
            hermes_client: Client for Hermes interactions
            budget_client: Optional client for Budget interactions
        """
        self.adapters = {}  # adapter_id -> adapter instance
        self.tools = {}  # tool_id -> (adapter_id, external_tool_id)
        self.hermes_client = hermes_client
        self.budget_client = budget_client
        
    async def register_adapter(self, adapter: MCPAdapter) -> str:
        """
        Register an adapter for a specific MCP implementation.
        
        Args:
            adapter: MCPAdapter instance
            
        Returns:
            Adapter ID
        """
        adapter_id = adapter.adapter_id
        self.adapters[adapter_id] = adapter
        
        # Connect to external system
        connected = await adapter.connect()
        if not connected:
            logger.error(f"Failed to connect adapter {adapter_id}")
            del self.adapters[adapter_id]
            return None
        
        # Register with budget system if available
        if self.budget_client:
            await adapter.register_token_tracker(self.budget_client)
            
        # Discover and register tools
        try:
            tools = await adapter.discover_tools()
            for tool in tools:
                external_tool_id = tool.get("id")
                if not external_tool_id:
                    continue
                    
                # Generate Tekton tool ID
                tool_id = f"{adapter_id}:{external_tool_id}"
                
                # Register with tool registry
                await self.hermes_client.register_mcp_tool(tool_id, tool, adapter_id)
                
                # Track locally
                self.tools[tool_id] = (adapter_id, external_tool_id)
                
                # Register with budget system if available
                if self.budget_client:
                    token_estimate = await adapter.estimate_token_usage(external_tool_id, {})
                    await self.budget_client.register_tool(tool_id, token_estimate)
                
            logger.info(f"Registered adapter {adapter_id} with {len(tools)} tools")
            return adapter_id
        except Exception as e:
            logger.error(f"Error registering adapter {adapter_id}: {e}")
            await adapter.disconnect()
            del self.adapters[adapter_id]
            return None
    
    async def discover_tools(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Discover available tools, optionally filtered."""
        # Add budget filter if specified
        if self.budget_client and filters and filters.get("budget_constrained", False):
            budget_filters = await self.budget_client.get_budget_constraints()
            if "max_cost" in budget_filters:
                if not filters.get("cost_filters"):
                    filters["cost_filters"] = {}
                filters["cost_filters"]["max_cost"] = budget_filters["max_cost"]
        
        return await self.hermes_client.search_mcp_tools(filters)
    
    async def execute_tool(self, tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool using the appropriate adapter."""
        if tool_id not in self.tools:
            tools = await self.discover_tools({"id": tool_id})
            if not tools:
                raise ValueError(f"Tool not found: {tool_id}")
                
            # Update local cache
            tool = tools[0]
            adapter_id = tool.get("adapter_id")
            external_tool_id = tool.get("external_id")
            self.tools[tool_id] = (adapter_id, external_tool_id)
        
        adapter_id, external_tool_id = self.tools[tool_id]
        adapter = self.adapters.get(adapter_id)
        
        if not adapter:
            # Try to get adapter info and re-register
            adapter_info = await self.hermes_client.get_mcp_adapter(adapter_id)
            if not adapter_info:
                raise ValueError(f"Adapter not found for tool {tool_id}")
                
            # Re-register adapter (simplified for brevity)
            raise ValueError(f"Adapter {adapter_id} not available")
        
        # Check budget constraints if budget client available
        if self.budget_client:
            # Estimate token usage
            token_estimate = await adapter.estimate_token_usage(external_tool_id, parameters)
            
            # Check if within budget
            budget_check = await self.budget_client.check_budget(tool_id, token_estimate)
            if not budget_check["approved"]:
                return {
                    "success": False,
                    "error": f"Budget constraint: {budget_check['reason']}",
                    "budget_info": budget_check
                }
            
        try:
            # Execute the tool
            result = await adapter.execute_tool(external_tool_id, parameters)
            
            # Record token usage if available
            if self.budget_client and "token_usage" in result:
                await self.budget_client.record_usage(tool_id, result["token_usage"])
                
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_id}: {e}")
            # Report error to Hermes for monitoring
            await self.hermes_client.report_mcp_error(tool_id, str(e))
            raise
            
    async def get_token_usage(self, tool_id: str) -> Dict[str, Any]:
        """Get token usage information for a tool."""
        if self.budget_client:
            return await self.budget_client.get_tool_usage(tool_id)
        else:
            return {"error": "Budget client not available"}
```

## Testing Strategy

### Unit Testing
- Test all interface implementations
- Test adapter implementation
- Test capability registry
- Test token tracking and budget integration
- Test security model

### Integration Testing
- Test adapter registration with Hermes
- Test capability discovery and search
- Test cross-adapter execution
- Test Budget integration with adapters
- Test security boundary enforcement

### Security Testing
- Test permission model enforcement
- Test sandboxing implementation
- Test rate limiting and resource controls
- Test audit logging
- Test budget constraint enforcement

### Performance Testing
- Test capability registry performance
- Test adapter overhead
- Test token tracking overhead
- Test composed capability execution
- Test under various load conditions

## Documentation Plan

### Architecture Documentation
- Universal adapter framework design
- Capability registry architecture
- Token tracking and Budget integration
- Security model specification
- Adapter interface standards

### Implementation Guides
- Adapter implementation guide
- Capability composition guide
- Budget integration guide
- Security configuration guide
- Testing guide

### User Documentation
- Tool discovery and usage guide
- Budget management guide
- Capability composition examples
- Security permissions guide
- Troubleshooting and FAQ

## Success Criteria

The implementation will be considered complete when:

1. Universal MCP adapter framework is implemented and tested
2. Hermes capability registry is operational
3. Reference adapters for key external services are working
4. Budget integration for token tracking is implemented
5. Security model is implemented and validated
6. Documentation is complete and accurate
7. End-to-end tests demonstrate correct functionality

## Dependencies

- MCP Unified Integration Sprint completion
- Access to external MCP services for testing
- Hermes database services for registry
- Budget component for token tracking and management

## Risks and Contingencies

### Technical Risks
- Risk: External MCP services change their APIs
  - Contingency: Implement versioning in adapters, maintain compatibility layers
- Risk: Performance issues with token tracking
  - Contingency: Implement sampling and estimation techniques
- Risk: Security vulnerabilities in external tools
  - Contingency: Implement comprehensive sandboxing and permission model

### Schedule Risks
- Risk: Reference adapter implementation takes longer than expected
  - Contingency: Prioritize core functionality, defer advanced features
- Risk: Budget integration more complex than anticipated
  - Contingency: Implement basic tracking first, enhance incrementally
- Risk: Testing with external services introduces delays
  - Contingency: Create comprehensive mock adapters for testing