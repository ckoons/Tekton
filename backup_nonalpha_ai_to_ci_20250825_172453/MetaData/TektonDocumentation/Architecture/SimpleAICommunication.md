# Simple CI Communication Architecture

## Overview

As of July 2025, Tekton uses a simplified "One Queue, One Socket, One AI" architecture for all CI communication. This replaces the previous complex unified system with registry-based discovery, connection pooling, and routing engines.

## Core Principle: One Queue, One Socket, One AI

Each CI specialist has:
- **One Queue**: A single message queue for request/response handling
- **One Socket**: A dedicated socket on a fixed port
- **One AI**: Direct 1:1 mapping between components and their CI specialists

## Architecture Components

### 1. Simple CI Interface (`shared/ai/simple_ai.py`)
The main entry point for all CI communication:

```python
# Synchronous communication
from shared.ai.simple_ai import ai_send_sync
response = ai_send_sync("apollo-ai", "Hello", "localhost", 45012)

# Asynchronous communication  
from shared.ai.simple_ai import ai_send
response = await ai_send("apollo-ai", "Hello", "localhost", 45012)
```

### 2. CI Service Simple (`shared/ai/ai_service_simple.py`)
Core service managing message queues and socket connections:
- Maintains one queue per AI
- Handles socket lifecycle
- Provides message tracking with UUIDs
- Auto-registers 18 Greek Chorus CIs on import

### 3. Message Handler (`shared/aish/src/message_handler.py`)
Simplified message handling for aish commands:
- Direct socket communication
- Fixed port lookups
- 30-second timeout for CI responses
- No connection pooling or retries

## Port Assignment Formula

AI ports are deterministically calculated from component ports:

```
AI Port = 45000 + (Component Port - 8000)
```

Examples:
- Engram (8000) → CI Port 45000
- Hermes (8001) → CI Port 45001
- Rhetor (8003) → CI Port 45003
- Apollo (8012) → CI Port 45012

## Communication Flow

```
User Request
    ↓
Component (e.g., Rhetor)
    ↓
simple_ai.ai_send()
    ↓
Direct Socket Connection (localhost:45xxx)
    ↓
AI Specialist
    ↓
Response via same socket
```

## What Was Removed

The following complex components were eliminated:
- **UnifiedAIRegistry**: No dynamic discovery needed with fixed ports
- **RoutingEngine**: No routing needed - direct connections only
- **Connection Pooling**: Each request uses a fresh socket
- **Load Balancing**: No distribution across multiple CIs
- **Event System**: No registry updates or notifications
- **Fallback Chains**: Simple error propagation instead

## Configuration

Port bases are configured in `.env.tekton`:
```
TEKTON_PORT_BASE=8000      # Base port for components
TEKTON_AI_PORT_BASE=45000  # Base port for CI specialists
```

## Testing

The simplified system has comprehensive test coverage:
- `tests/test_ai_service_simple.py` - Core service tests
- `tests/test_integration_simple.py` - Integration tests
- `tests/test_unified_ai_communication.py` - Full communication tests
- `tests/test_message_handler.py` - Message handler tests

All 18 Greek Chorus CIs are tested and verified working.

## Benefits of Simplification

1. **Predictability**: Fixed ports eliminate discovery issues
2. **Reliability**: No complex state management or synchronization
3. **Performance**: Direct connections without routing overhead
4. **Maintainability**: Minimal code surface area
5. **Debuggability**: Simple to trace communication flow

## Migration Notes

When migrating from the old unified system:
1. Replace `socket_client` imports with `simple_ai`
2. Remove any registry or routing logic
3. Use fixed port calculations instead of discovery
4. Eliminate connection pooling code
5. Update landmarks to reflect direct communication

## Example Usage

### Direct CI Communication
```python
from shared.ai.simple_ai import ai_send_sync

# Talk to Apollo AI
response = ai_send_sync("apollo-ai", "Analyze this code", "localhost", 45012)

# Talk to Athena CI  
response = ai_send_sync("athena-ai", "What is the meaning?", "localhost", 45005)
```

### Team Chat
```python
# Via aish
$ aish team-chat "What should we build today?"

# All 17 CIs respond with their perspectives
```

### Error Handling
```python
try:
    response = ai_send_sync("apollo-ai", message, "localhost", 45012)
except Exception as e:
    # Simple error - no fallback chains or retries
    print(f"AI communication failed: {e}")
```

## Summary

The simple CI architecture embodies Casey's principle: "no need for a fucking registry waste of time". With fixed ports and direct connections, the system is now truly "brain dead simple" - exactly as intended.