# Tekton Backend Architectural Patterns

## Overview
Based on AST analysis of 465 source files across 11 core components, here are the key architectural patterns and decisions found in the Tekton backend.

## Core Patterns Identified

### 1. **Asynchronous Architecture**
- **Pattern**: Extensive use of `async/await` throughout the codebase
- **Components**: All major components use async patterns
- **Key Areas**: 
  - API endpoints (FastAPI async handlers)
  - WebSocket communications
  - Component startup/shutdown sequences
  - Inter-component messaging

### 2. **Component Communication**
- **Central Hub**: Hermes acts as the message bus
  - 572 landmarks in Hermes component
  - WebSocket-based pub/sub pattern
  - All components register with Hermes on startup
- **Pattern**: Event-driven architecture with topic-based routing

### 3. **Singleton Services**
- **Pattern**: Most core components use singleton pattern
- **Implementation**: `get_instance()` methods found in multiple components
- **Purpose**: Ensures single instance per component for state management

### 4. **API Structure**
- **Framework**: FastAPI used consistently across components
- **Pattern**: RESTful endpoints with async handlers
- **Found**: 531 API endpoint landmarks
- **Common structure**:
  ```python
  @router.post("/endpoint")
  async def handler(request: Model) -> Response:
      ...
  ```

### 5. **MCP (Model Context Protocol) Integration**
- **Pattern**: Components expose tools via MCP decorators
- **Found**: 197 integration points (MCP tools + WebSocket handlers)
- **Usage**: AI agents can interact with components through standardized MCP tools

### 6. **Error Handling**
- **Pattern**: Consistent try/except patterns with graceful degradation
- **Approach**: 
  - Primary action → Fallback → Error logging
  - Async context managers for resource cleanup
  - Structured error responses

### 7. **High Complexity Areas (Danger Zones)**
- **Found**: 513 high-complexity functions
- **Common in**:
  - Engram (memory management)
  - Apollo (orchestration logic)
  - Prometheus (LLM chain management)
- **Characteristics**:
  - Multiple branching logic
  - State management
  - Error recovery paths

## Component-Specific Insights

### Hermes (Message Bus)
- Central nervous system of Tekton
- WebSocket server for real-time communication
- Topic-based message routing
- Component registration and heartbeat monitoring

### Apollo (Orchestration)
- Complex action planning and coordination
- Token budget management
- Predictive engine for optimization
- Protocol enforcement between components

### Engram (Memory/State)
- Multiple storage backends (FAISS, LanceDB)
- Structured memory with semantic search
- Latent space interfaces
- Memory fusion and streaming capabilities

### Prometheus (LLM Adapter)
- Provider abstraction layer
- Fallback chains for reliability
- Token management and optimization
- Multiple LLM backend support

### Athena (Knowledge Graph)
- Entity and relationship management
- Query engine for graph traversal
- Integration with visualization tools
- Semantic knowledge representation

## Architectural Decisions

### 1. **Microservices with Shared Utilities**
- Each component is independently deployable
- Shared utilities in `shared/` for common patterns
- Standardized startup/shutdown procedures

### 2. **Event-Driven Over Direct Calls**
- Components communicate via Hermes events
- Loose coupling between services
- Enables dynamic component discovery

### 3. **Async-First Design**
- Non-blocking I/O throughout
- Concurrent request handling
- Efficient resource utilization

### 4. **AI-Native Architecture**
- MCP integration for AI tool exposure
- Structured prompts and templates
- LLM-friendly APIs and responses

## Recommended Landmark Placement Strategy

### Priority 1: Integration Points
- All API endpoints (already identified: 531)
- MCP tool definitions (part of 197 integration points)
- WebSocket handlers (part of 197 integration points)
- Component registration points

### Priority 2: Architectural Boundaries
- Singleton initialization points
- Service startup/shutdown sequences
- Inter-component communication interfaces
- State management checkpoints

### Priority 3: Complex Logic Areas
- High-complexity functions (513 identified)
- Error recovery paths
- Performance-critical sections
- Resource management code

### Priority 4: Developer Experience
- Public APIs and their contracts
- Configuration points
- Extension/plugin interfaces
- Common patterns that should be reused

## Next Steps

1. **Create Landmark Decorators**: Design Python decorators for marking landmarks
2. **Instrument Code**: Place landmarks at identified locations
3. **Build Retrieval System**: Create infrastructure for CI memory access
4. **Test with Numa**: Validate that landmarks provide useful context

This analysis provides the foundation for transforming Tekton into a self-aware system with persistent architectural memory.