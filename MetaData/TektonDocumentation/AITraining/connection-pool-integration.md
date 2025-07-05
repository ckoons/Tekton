# AI Connection Pool Integration Guide

## Overview

The new connection pool architecture enables instant AI communication by maintaining persistent socket connections to all AI specialists. This solves the performance issue where team chat was slow despite AIs being capable of 0.1 second responses.

## Key Benefits

1. **Connection Reuse**: One persistent connection per AI, shared across all Tekton components
2. **Instant Responses**: No connection overhead - messages sent immediately
3. **Automatic Reconnection**: Failed connections automatically reconnect
4. **Multiplexing**: Multiple components can use the same connection concurrently
5. **Health Monitoring**: Periodic pings ensure connections stay alive

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Connection Pool (Singleton)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    Persistent    ┌─────────────────────┐    │
│  │  aish    │ ───Connection───▶│  Apollo AI Socket   │    │
│  │  proxy   │                   │  (port 45001)       │    │
│  └──────────┘                   └─────────────────────┘    │
│                                                             │
│  ┌──────────┐    Persistent    ┌─────────────────────┐    │
│  │ Noesis   │ ───Connection───▶│  Athena AI Socket   │    │
│  │   UI     │                   │  (port 45002)       │    │
│  └──────────┘                   └─────────────────────┘    │
│                                                             │
│  ┌──────────┐    Persistent    ┌─────────────────────┐    │
│  │  Team    │ ───Connection───▶│  Sophia AI Socket   │    │
│  │  Chat    │                   │  (port 45003)       │    │
│  └──────────┘                   └─────────────────────┘    │
│                                 │        ...          │    │
│                                 └─────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Usage Examples

### 1. Basic Usage - Send to Single AI

```python
from shared.ai.connection_pool import send_to_ai

# Send message to Apollo
response = await send_to_ai(
    ai_id="apollo-ai",
    host="localhost", 
    port=45001,
    message="What patterns do you see?",
    timeout=2.0  # Fast timeout
)
```

### 2. Team Chat - Send to All AIs

```python
from Rhetor.rhetor.core.mcp.tools_integration_unified_optimized import send_team_message

# Send to all AIs with 2 second timeout
result = await send_team_message(
    message="What are the key principles of good software architecture?",
    timeout=2.0
)

# Responses arrive in parallel
for response in result['responses']:
    print(f"{response['socket_id']}: {response['content']}")
```

### 3. Using Connection Pool Directly

```python
from shared.ai.connection_pool import get_connection_pool

# Get the singleton pool
pool = await get_connection_pool()

# Pre-connect to an AI
conn = await pool.get_connection("noesis-ai", "localhost", 45015)
print(f"Connection state: {conn.state}")
print(f"Requests handled: {conn.request_count}")

# Send multiple messages on same connection
for i in range(10):
    result = await pool.send_message(
        "noesis-ai", "localhost", 45015,
        f"Message {i}"
    )
    print(f"Reused connection: {result.get('connection_reused')}")
```

### 4. Integration with aish

```python
# In aish proxy, use connection pool instead of creating new connections
async def send_to_ai_socket(self, ai_name, message):
    # Resolve AI info from registry
    ai_info = self.registry.get_ai_info(ai_name)
    
    # Use connection pool
    return await send_to_ai(
        ai_id=ai_info['id'],
        host=ai_info['host'],
        port=ai_info['port'], 
        message=message,
        timeout=5.0
    )
```

## Performance Improvements

### Before (New Connection Each Time)
- Connection establishment: 100-500ms
- Send message: 10ms
- Wait for response: 100-1000ms
- Close connection: 10ms
- **Total: 220-1520ms per message**

### After (Connection Pool)
- Connection establishment: 0ms (reused)
- Send message: 1ms
- Wait for response: 100-1000ms
- Close connection: 0ms (kept alive)
- **Total: 101-1001ms per message**

### Team Chat (18 AIs)
- **Before**: 18 × 220ms = 3.96 seconds minimum
- **After**: Parallel on existing connections = 100-1000ms total

## Implementation Checklist

- [x] Create connection pool module
- [x] Implement connection reuse
- [x] Add health monitoring
- [x] Create optimized team chat
- [ ] Update aish proxy to use pool
- [ ] Update Noesis UI to use pool
- [ ] Update other UI components
- [ ] Add connection pool metrics
- [ ] Test with all 18 AIs

## Configuration

Environment variables:
```bash
# Connection pool settings
TEKTON_POOL_HEALTH_INTERVAL=30    # Health check interval in seconds
TEKTON_POOL_RECONNECT_DELAY=5     # Reconnection delay in seconds
TEKTON_POOL_CONNECTION_TIMEOUT=2  # Connection timeout in seconds
TEKTON_POOL_REQUEST_TIMEOUT=30    # Default request timeout
```

## Monitoring

Check connection pool status:
```python
pool = await get_connection_pool()
for conn_key, conn in pool._connections.items():
    print(f"{conn.ai_id}: {conn.state} (requests: {conn.request_count})")
```

## Troubleshooting

1. **Connections fail to establish**
   - Check if AI specialists are running
   - Verify ports are correct in registry
   - Check for firewall/network issues

2. **Slow responses despite pool**
   - Reduce timeout to fail fast (2 seconds recommended)
   - Check Ollama performance
   - Monitor which AIs are slow

3. **Connection drops**
   - Health monitoring will auto-reconnect
   - Check AI specialist logs for crashes
   - Increase health check frequency if needed

---

*Created by Jill on July 5, 2025 for optimizing Tekton AI communication*