# Team Chat Performance Optimization Guide

## Problem Statement

Team chat responses are slow despite AIs being capable of 0.1 second responses. The issue is not with the AIs themselves but with connection management and timeout configurations.

## Root Causes

1. **Connection Overhead**: Opening 18 new TCP connections per request
2. **High Timeouts**: 10-second default timeout blocks fast responses
3. **No Connection Pooling**: Every request creates fresh connections
4. **Sequential Discovery**: Lists all specialists on every request

## Optimization Strategy

### 1. Implement Connection Pooling

```python
class AIConnectionPool:
    def __init__(self, max_connections_per_host=5):
        self._pools = {}  # {(host, port): [connections]}
        self._lock = asyncio.Lock()
    
    async def get_connection(self, host, port):
        key = (host, port)
        async with self._lock:
            if key not in self._pools:
                self._pools[key] = []
            
            # Reuse existing connection if available
            if self._pools[key]:
                return self._pools[key].pop()
            
            # Create new connection
            return await self._create_connection(host, port)
```

### 2. Reduce Timeouts for Team Chat

```python
# For team chat specifically
TEAM_CHAT_TIMEOUT = 2.0  # 2 seconds max per AI
TEAM_CHAT_CONNECTION_TIMEOUT = 0.5  # 500ms to connect
```

### 3. Cache Specialist Discovery

```python
class SpecialistCache:
    def __init__(self, ttl=60):  # 1 minute cache
        self._cache = {}
        self._timestamps = {}
        self.ttl = ttl
    
    async def get_specialists(self):
        if self._is_cache_valid():
            return self._cache['specialists']
        
        # Refresh cache
        specialists = await self._discover_specialists()
        self._cache['specialists'] = specialists
        self._timestamps['specialists'] = time.time()
        return specialists
```

### 4. Implement Fast-Fail Pattern

```python
async def send_with_fast_timeout(specialist_id, message, timeout=2.0):
    try:
        # Use aggressive timeout for team chat
        return await asyncio.wait_for(
            send_message(specialist_id, message),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        # Return timeout indicator immediately
        return {
            "success": False,
            "error": f"Timeout after {timeout}s",
            "specialist_id": specialist_id
        }
```

### 5. Parallel Connection Warming

```python
async def warm_connections(specialists):
    """Pre-establish connections to all specialists"""
    tasks = []
    for spec in specialists:
        task = asyncio.create_task(
            connection_pool.warm_connection(
                spec['connection']['host'],
                spec['connection']['port']
            )
        )
        tasks.append(task)
    
    # Don't wait for all - just fire and forget
    asyncio.gather(*tasks, return_exceptions=True)
```

## Quick Wins (Immediate Implementation)

1. **Reduce team chat timeout to 2 seconds**:
   ```python
   # In team_chat_endpoints.py
   timeout: float = Field(2.0, description="Timeout in seconds")
   ```

2. **Remove retry logic for team chat**:
   ```python
   # In socket_client.py for team chat
   max_retries=0  # No retries
   ```

3. **Add specialist caching**:
   - Cache the specialist list for 60 seconds
   - Refresh in background, don't block requests

## Expected Results

With these optimizations:
- First request: 2-3 seconds (connection establishment)
- Subsequent requests: 0.1-0.5 seconds (reused connections)
- Timeout failures: Return immediately after 2 seconds
- All 18 AIs can respond in parallel

## Testing the Optimizations

```bash
# Test with reduced timeout
curl -X POST http://localhost:8003/api/team-chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quick test", "timeout": 2.0}'

# Monitor connection count
netstat -an | grep 4[5-9][0-9][0-9][0-9] | wc -l
```

## Long-term Improvements

1. **WebSocket connections**: Keep persistent connections to all AIs
2. **Message queuing**: Use Redis/RabbitMQ for async messaging
3. **Circuit breakers**: Automatically skip unresponsive AIs
4. **Response streaming**: Start showing responses as they arrive

---

*Created by Jill on July 5, 2025 during performance investigation with Casey*