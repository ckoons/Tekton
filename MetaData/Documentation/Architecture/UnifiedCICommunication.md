# Unified CI Communication Architecture

## Overview

**July 2025** - Tekton now implements a unified "One Queue, One Socket, One AI" communication architecture that simplifies and standardizes all CI interactions across the platform.

## Architecture Principle

### "One Queue, One Socket, One AI"

Every CI has exactly:
- **One message queue** for request/response tracking
- **One socket connection** for communication
- **One unified interface** for access

```
All Components → simple_ai → ai_service_simple → Direct Socket
```

## Core Components

### 1. `shared/ai/simple_ai.py`
**Main Interface** - Provides both sync and async methods:

```python
# Synchronous communication
from shared.ai.simple_ai import ai_send_sync
response = ai_send_sync("apollo-ai", "Hello", "localhost", 45012)

# Asynchronous communication
from shared.ai.simple_ai import ai_send  
response = await ai_send("apollo-ai", "Hello", "localhost", 45012)
```

### 2. `shared/ai/ai_service_simple.py`
**Core Service** - Manages queues and sockets:

```python
from shared.ai.ai_service_simple import get_service

service = get_service()
# Service has 18 CI queues pre-registered
# Manages message routing and socket connections
```

### 3. Integration Points
- **aish**: `shared/aish/src/registry/socket_registry.py` uses unified system
- **Tekton**: All components route through unified service
- **Tests**: Comprehensive test coverage validates the architecture

## Key Benefits

### ✅ Simplified Architecture
- Removed complex connection pooling
- Eliminated multiple communication pathways
- Single point of truth for CI communication

### ✅ Reliable Messaging
- UUID-based message tracking
- Proper error handling and propagation
- Graceful degradation when CIs unavailable

### ✅ Developer Experience
- Consistent API across sync/async contexts
- Auto-registration of all 18 Tekton CIs
- Clear error messages and debugging tools

### ✅ Test Coverage
All test suites passing:
- **Core Service**: 5/5 tests passed
- **Integration**: 4/4 tests passed  
- **Unified Communication**: 9/9 tests passed

## Message Flow

### Request/Response Cycle
1. **Request**: Component calls `ai_send_sync()` or `ai_send()`
2. **Queue**: Message assigned UUID and queued for target AI
3. **Process**: Service sends message through AI's socket
4. **Response**: CI response received and matched to request UUID
5. **Return**: Response returned to calling component

### Auto-Registration
```python
# 18 CIs automatically registered on import:
ais = [
    ("engram-ai", "localhost", 45000),
    ("hermes-ai", "localhost", 45001),
    ("ergon-ai", "localhost", 45002),
    # ... all 18 CIs
]
```

## Migration from Legacy System

### What Changed
- **Before**: Complex `ai_service.py` with connection pooling
- **After**: Simple `ai_service_simple.py` with direct socket management
- **Compatibility**: Legacy service still exists for gradual migration

### Import Updates
```python
# OLD (deprecated but still works)
from shared.ai.ai_service import get_service

# NEW (recommended)  
from shared.ai.ai_service_simple import get_service
from shared.ai.simple_ai import ai_send_sync, ai_send
```

## Testing and Validation

### Test Files
- `tests/test_ai_service_simple.py` - Core service functionality
- `tests/test_integration_simple.py` - Component integration  
- `tests/test_unified_ai_communication.py` - Full communication suite

### Running Tests
```bash
# Test core service
python tests/test_ai_service_simple.py

# Test integration
python tests/test_integration_simple.py

# Test full communication
python tests/test_unified_ai_communication.py
```

### Validation Commands
```python
# Quick health check
from shared.ai.simple_ai import ai_send_sync
response = ai_send_sync("apollo-ai", "ping", "localhost", 45012)

# Service status
from shared.ai.ai_service_simple import get_service
service = get_service()
print(f"Queues: {len(service.queues)}, Sockets: {len(service.sockets)}")
```

## Design Decisions

### Why "One Queue, One Socket, One AI"?
1. **Simplicity**: Eliminates complex state management
2. **Reliability**: Clear ownership and responsibility
3. **Debugging**: Easy to trace message flow
4. **Performance**: Direct socket communication without overhead

### Why Keep Legacy Service?
- **Gradual Migration**: Allows components to migrate incrementally
- **Compatibility**: Existing code continues to work
- **Risk Mitigation**: Can rollback if issues discovered

## Future Considerations

### Potential Simplifications
1. **Remove connection pooling** from `socket_client.py` (no longer needed)
2. **Simplify socket_registry** to be a thin wrapper around `simple_ai`
3. **Remove complex MCPToolsIntegrationUnified** patterns
4. **Deprecate legacy `ai_service.py`** after full migration

### Monitoring
- All 18 CIs auto-registered and ready
- Test coverage validates architecture reliability
- Error handling provides clear diagnostics

---

**Status**: ✅ **FULLY IMPLEMENTED AND TESTED** (July 2025)
**Test Results**: 18/18 tests passing across all suites
**Migration**: Complete for all core components