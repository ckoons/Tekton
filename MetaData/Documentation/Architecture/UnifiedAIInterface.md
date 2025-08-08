# [DEPRECATED] Unified AI Interface Architecture

> **⚠️ DEPRECATED**: This document describes the old complex unified AI system that has been replaced by the Simple AI Communication Architecture. See [SimpleAICommunication.md](./SimpleAICommunication.md) for the current architecture.
>
> **Status**: This architecture was replaced in July 2025 with a much simpler "One Queue, One Socket, One AI" approach using fixed ports and direct socket communication.

---

# Unified AI Interface Architecture

## Overview

The Unified AI Interface provides a single, consistent way to discover, manage, and communicate with AI specialists across the Tekton platform. This document describes the new architecture that replaces multiple disparate implementations with a unified system.

## Key Components

### 1. Enhanced Socket Client (`shared/ai/socket_client.py`)

The foundation of all AI communication, featuring:

- **Native Streaming Support**: Built-in streaming capabilities for progressive responses
- **Async/Await First**: Primary async interface with sync wrappers for compatibility
- **Robust Error Handling**: Automatic retries, connection pooling, and timeout management
- **Protocol Support**: Newline-delimited JSON with message type enumeration

#### Key Features:

```python
# Standard message
response = await client.send_message(host, port, "Hello AI")

# Streaming response
async for chunk in client.send_message_stream(host, port, "Tell me a story"):
    print(chunk.content, end='', flush=True)
    if chunk.is_final:
        print(f"\nModel: {chunk.metadata['model']}")

# Persistent connections
async with client.persistent_connection(host, port) as conn:
    response1 = await conn.send("First message")
    response2 = await conn.send("Second message")
```

### 2. Unified Registry (`shared/ai/unified_registry.py`)

Central registry for all AI specialists with:

- **Event-Driven Architecture**: Real-time updates via event bus
- **Health Monitoring**: Automatic background health checks
- **Performance Tracking**: Response time metrics and success rates
- **Multiple Backend Support**: File-based (default), Memory, Engram (future)
- **Smart Discovery**: Filter by role, capabilities, status, and performance

#### Event System:

```python
registry = UnifiedAIRegistry()

# Subscribe to events
registry.on("status_changed", lambda data: 
    print(f"{data['specialist'].id} changed from {data['old_status']} to {data['new_status']}")
)

# Events emitted:
# - registered: New AI registered
# - deregistered: AI removed  
# - status_changed: Health status changed
# - discovered: Discovery completed
# - metrics_updated: Performance metrics updated
```

### 3. Intelligent Routing Engine (`shared/ai/routing_engine.py`)

Smart routing with load balancing and fallback chains:

- **Rule-Based Routing**: Define routing rules based on message content
- **Capability Matching**: Route to AIs with required capabilities
- **Load Balancing**: Distribute requests across multiple AIs
- **Fallback Chains**: Automatic fallback to alternative AIs
- **Team Routing**: Route to multiple AIs for collaborative work

#### Example Rules:

```python
# Route code analysis to specialized AIs
code_rule = RoutingRule(
    name="code_analysis",
    condition=lambda ctx: "analyze" in ctx.get("message", "").lower(),
    preferred_ais=["apollo-ai", "minerva-ai"],
    required_capabilities=["code_analysis"],
    fallback_chain=["athena-ai"],
    load_balance=True
)
```

### 4. Enhanced ai-discover Tool

Comprehensive AI management tool with:

- **Real-time Monitoring**: `ai-discover watch` for live status updates
- **Performance Testing**: Benchmark AIs with varying workloads
- **Streaming Tests**: Verify streaming capabilities
- **Routing Tests**: Test routing engine decisions
- **Rich Output**: Beautiful tables and charts (when rich is installed)

#### New Commands:

```bash
# Watch AI status in real-time
ai-discover watch

# Test streaming
ai-discover stream apollo-ai "Tell me a story"

# Benchmark performance
ai-discover benchmark --iterations 10

# Test routing
ai-discover route "analyze this code" --execute

# View statistics
ai-discover stats
```

## Architecture Benefits

### 1. Single Source of Truth

- All AI registrations go through the unified registry
- Consistent discovery across all components
- No more duplicate or conflicting data

### 2. Performance Optimization

- Health monitoring ensures requests go to healthy AIs
- Load balancing distributes work evenly
- Performance metrics enable smart routing decisions

### 3. Event-Driven Updates

- Real-time status updates across all components
- No more polling for changes
- Reactive UI updates possible

### 4. Backward Compatibility

- Sync wrappers for legacy code (aish)
- Existing ai-discover commands still work
- Gradual migration path

## Migration Guide

### For aish

```python
# Old way
from utils.socket_buffer import LineBufferedSocket
# ... complex socket handling ...

# New way
from shared.ai.socket_client import create_sync_client
client = create_sync_client()
response = client.send_message(host, port, message)
```

### For Rhetor

```python
# Old way
from rhetor.core.ai_socket_registry import AISocketRegistry
# ... Engram-backed registry ...

# New way
from shared.ai.unified_registry import UnifiedAIRegistry
registry = UnifiedAIRegistry()
await registry.start()
```

### For ai-discover

The tool has been completely rewritten but maintains backward compatibility:

```bash
# Legacy commands still work (with deprecation notices)
ai-discover info apollo-ai  # Use 'list --json' instead
ai-discover manifest        # Use 'stats' instead

# New powerful commands
ai-discover watch          # Real-time monitoring
ai-discover benchmark      # Performance testing
```

## Protocol Standards

### Message Types

```python
class MessageType(Enum):
    MESSAGE = "message"    # Standard request/response
    PING = "ping"         # Health check
    STREAM = "stream"     # Request streaming response
    CHUNK = "chunk"       # Streaming chunk
    COMPLETE = "complete" # End of stream
    ERROR = "error"       # Error response
```

### Standard Request Format

```json
{
    "type": "message",
    "content": "User message",
    "context": {},           // Optional
    "temperature": 0.7,      // Optional
    "max_tokens": 1000,      // Optional
    "stream": true          // Request streaming
}
```

### Standard Response Format

```json
{
    "type": "message",
    "content": "AI response",
    "ai_id": "apollo-ai",
    "model": "gpt-oss:20b",
    "thinking_level": "Quick Response",
    "elapsed_time": 2.5,
    "total_tokens": 150
}
```

## Performance Considerations

### Connection Pooling

The socket client maintains connection pools for frequently accessed AIs, reducing connection overhead.

### Caching

- Discovery results cached for 60 seconds
- AI status cached with TTL
- Performance metrics use rolling windows

### Health Monitoring

- Background health checks every 30 seconds
- Automatic status updates based on response times
- Graceful degradation for slow AIs

## Future Enhancements

### Planned Features

1. **WebSocket Support**: For browser-based clients
2. **gRPC Transport**: For high-performance scenarios
3. **Distributed Registry**: Multi-node registry support
4. **Advanced Analytics**: ML-based routing optimization
5. **Circuit Breakers**: Automatic failure recovery

### Extensibility Points

1. **Custom Backends**: Implement `AIRegistryBackend` for custom storage
2. **Custom Routing Rules**: Define complex routing logic
3. **Event Handlers**: React to registry events
4. **Protocol Extensions**: Add custom message types

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```
   ImportError: No module named 'shared.ai.unified_registry'
   ```
   Solution: Ensure Tekton is in Python path or set TEKTON_ROOT

2. **No AIs Found**
   ```
   No suitable AI specialists available for routing
   ```
   Solution: Check if AIs are running, use `ai-discover test`

3. **Timeout Errors**
   ```
   Timeout after 30s
   ```
   Solution: Increase timeout or check AI health

### Debug Mode

Enable debug output:
```python
# In code
client = AISocketClient(debug=True)
registry = UnifiedAIRegistry()

# Command line
ai-discover list -v
ai-discover test apollo-ai --verbose
```

## API Reference

See individual module documentation:
- [Socket Client API](./api/socket_client.md)
- [Unified Registry API](./api/unified_registry.md)
- [Routing Engine API](./api/routing_engine.md)

## Conclusion

The Unified AI Interface provides a robust, scalable foundation for AI communication across the Tekton platform. With native streaming support, intelligent routing, and real-time monitoring, it enables powerful AI-driven applications while maintaining simplicity and backward compatibility.