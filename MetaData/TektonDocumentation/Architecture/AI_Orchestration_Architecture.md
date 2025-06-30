# AI Orchestration Architecture

## Overview

This document describes the AI orchestration architecture implemented in Tekton through the Rhetor AI Integration Sprint (Phase 3/4). The architecture enables sophisticated AI-powered workflows through MCP tools, live component integration, and dynamic specialist management.

**Updated June 2025**: This architecture now uses the unified AI system in `/Tekton/shared/ai/` that connects to real Greek Chorus AI specialists on ports 45000-50000.

## Core Concepts

### AI Specialists

AI Specialists are dedicated AI instances that handle specific domains or tasks within the Tekton ecosystem. Each specialist has:

- **Identity**: Unique ID and role (e.g., "code-reviewer", "data-analyst")
- **Model Configuration**: Specific LLM model and parameters
- **Personality**: System prompts and behavioral traits
- **Capabilities**: List of tasks the specialist can perform
- **State**: Active/inactive status and conversation history

### MCP Tools Integration

The Model Context Protocol (MCP) serves as the primary interface for AI orchestration:

```
User/Component → MCP Tool → AI Specialist Manager → AI Specialist → Response
                    ↓                                      ↓
                 Hermes ←──────── Cross-Component ─────────┘
```

### Live Component Integration

MCP tools can interact with live component instances, enabling real-time data access and manipulation:

```python
# Example: Live integration pattern
@mcp_tool(name="AnalyzeComponentHealth")
async def analyze_health(component_id: str):
    # Access live component state
    component = await get_live_component(component_id)
    metrics = await component.get_metrics()
    
    # Use AI for analysis
    specialist = await get_specialist("performance-optimizer")
    analysis = await specialist.analyze(metrics)
    
    return analysis
```

## Architecture Components

### 1. AISpecialistManager

Central manager for all AI specialists in Rhetor:

```python
class AISpecialistManager:
    specialists: Dict[str, AISpecialistConfig]
    message_queue: asyncio.Queue
    active_conversations: Dict[str, List[AIMessage]]
    
    async def create_specialist(specialist_id: str) -> bool
    async def send_message(...) -> str
    async def orchestrate_team_chat(...) -> List[AIMessage]
```

### 2. MCPToolsIntegrationUnified

Bridge between MCP tools and the unified AI system:

```python
class MCPToolsIntegrationUnified:
    unified_client: UnifiedAIClient  # Uses shared/ai components
    messaging_integration: AIMessagingIntegration
    message_bus: Optional[MessageBus]
    
    async def list_ai_specialists(...) -> Dict
    async def send_message_to_specialist(...) -> Dict
    async def orchestrate_team_chat(...) -> Dict
```

The unified system provides:
- **AISocketClient**: Direct socket communication with streaming
- **UnifiedAIRegistry**: Discovery and management of AI specialists
- **RoutingEngine**: Intelligent message routing based on capabilities

### 3. Dynamic Specialist System

Runtime creation and management of AI specialists:

- **Templates**: Pre-defined specialist configurations
- **Customization**: Runtime parameter adjustment
- **Cloning**: Create variants of existing specialists
- **Lifecycle**: Activation, modification, deactivation

## Communication Patterns

### Direct Communication

Within Rhetor component:
```
MCP Tool → AISpecialistManager → AI Specialist
```

### Cross-Component Communication

Through Hermes message bus:
```
Rhetor MCP Tool → Hermes → Target Component → AI Specialist
```

### Team Chat Orchestration

Multi-specialist conversations:
```
Orchestrator → Specialist A ─┐
     ↓                       ├→ Conversation Flow
     └────→ Specialist B ────┘
```

## MCP Tools Categories

### Model Management (6 tools)
- Configuration and selection of LLM models
- Performance monitoring and optimization
- Provider management and failover

### Prompt Engineering (6 tools)
- Template creation and management
- Prompt optimization and validation
- Performance analysis

### Context Management (4 tools)
- Context window optimization
- Token usage tracking
- Context compression

### AI Orchestration (6 tools)
- Specialist listing and activation
- Message routing and team chat
- Configuration management

### Dynamic Specialists (6 tools)
- Template-based creation
- Runtime modification
- Lifecycle management

### Streaming Tools (2 tools)
- Real-time response streaming
- Progress indicators

## Data Flow

### Standard Tool Execution

1. Client calls MCP tool via HTTP/WebSocket
2. FastMCP validates parameters
3. Tool function executes with live component access
4. Response returned synchronously

### Streaming Tool Execution

1. Client initiates streaming request
2. SSE connection established
3. Tool executes with progress callbacks
4. Events streamed to client
5. Final result sent on completion

### AI Specialist Communication

1. Message sent to specialist via tool
2. Rhetor filters/translates if needed
3. Specialist processes with LLM
4. Response routed back through system

## Security Considerations

### Access Control
- Tools require proper authentication
- Component state access is controlled
- AI specialists have scoped permissions

### Token Management
- Budget tracking per specialist
- Rate limiting on AI operations
- Token optimization strategies

### Data Privacy
- Conversation history management
- Sensitive data filtering
- Cross-component data isolation

## Performance Optimization

### Caching
- Model response caching
- Template caching
- Connection pooling

### Async Operations
- All AI operations are async
- Queue-based message handling
- Concurrent specialist execution

### Resource Management
- Specialist lifecycle management
- Memory usage optimization
- Connection cleanup

## Integration Points

### Hermes Integration
- Automatic tool registration
- Cross-component messaging
- Service discovery

### Component Integration
- Direct state access
- Event subscriptions
- Metric collection

### UI Integration
- WebSocket connections
- Streaming responses
- Progress indicators

## Best Practices

### Tool Design
1. Keep tools focused and single-purpose
2. Provide clear descriptions and parameters
3. Handle errors gracefully
4. Support both sync and async patterns

### AI Specialist Usage
1. Choose appropriate specialist for task
2. Provide clear, structured prompts
3. Monitor token usage
4. Cache responses when possible

### Live Integration
1. Always check component availability
2. Handle state changes gracefully
3. Use proper error boundaries
4. Clean up resources

## Future Enhancements

### Planned Features
- Multi-modal AI support
- Advanced caching strategies
- Distributed specialist execution
- Enhanced monitoring and analytics

### Experimental Features
- Autonomous specialist collaboration
- Self-optimizing prompts
- Predictive resource allocation
- Cross-platform specialist sharing

## References

- [MCP Implementation Guide](../DeveloperGuides/MCP_IMPLEMENTATION_GUIDE.md)
- [Rhetor Technical Documentation](../../ComponentDocumentation/Rhetor/TECHNICAL_DOCUMENTATION.md)
- [Building New Components](../Building_New_Tekton_Components/Step_By_Step_Tutorial.md)