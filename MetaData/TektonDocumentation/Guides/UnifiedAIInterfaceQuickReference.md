# Unified AI Interface - Quick Reference

## What Changed?

### ✅ NEW: Unified System
- Single registry for all AI discovery
- Automatic health monitoring
- Performance tracking
- Event-driven updates
- Native streaming support

### ❌ OLD: Multiple Implementations
- `LineBufferedSocket` → `AISocketClient`
- `socket_buffer.py` → `socket_client.py`
- `ai_socket_registry.py` → `unified_registry.py`
- Manual discovery → Automatic discovery
- No health checks → Continuous monitoring

## For Developers

### Import Changes

```python
# ❌ Old (Don't use)
from utils.socket_buffer import LineBufferedSocket
from rhetor.core.ai_socket_registry import AISocketRegistry

# ✅ New
from shared.ai.socket_client import AISocketClient, create_sync_client
from shared.ai.unified_registry import UnifiedAIRegistry, get_registry
```

### Socket Communication

```python
# ❌ Old way
detector = SocketTimeoutDetector()
success, sock, error = detector.create_connection(host, port)
buffered_socket = LineBufferedSocket(sock)
buffered_socket.write_message({"type": "chat", "content": message})
response = buffered_socket.read_message()

# ✅ New way (async)
client = AISocketClient()
response = await client.send_message(host, port, message)

# ✅ New way (sync for aish)
client = create_sync_client()
response = client.send_message(host, port, message)
```

### Streaming

```python
# ✅ Native streaming support
async for chunk in client.send_message_stream(host, port, message):
    print(chunk.content, end='', flush=True)
    if chunk.is_final:
        print(f"\nModel: {chunk.metadata['model']}")
```

### Discovery

```python
# ❌ Old way
subprocess.run(['ai-discover', 'list', '--json'])

# ✅ New way
registry = get_registry()
specialists = await registry.discover(
    role="planning",
    status=AIStatus.HEALTHY,
    min_success_rate=0.8
)
```

## For Users

### Enhanced ai-discover

```bash
# New commands
ai-discover watch                    # Real-time monitoring
ai-discover stream apollo-ai "Hi"    # Test streaming
ai-discover benchmark               # Performance testing
ai-discover route "analyze code"    # Test routing
ai-discover stats                   # Registry statistics

# Old commands (deprecated but work)
ai-discover info apollo-ai  # → Use list --json
ai-discover manifest       # → Use stats
```

### aish Integration

No changes needed! aish automatically uses the unified system:

```bash
# Still works exactly the same
echo "Hello" | apollo
team-chat "What should we build?"
apollo | athena | sophia
```

## Key Benefits

1. **Reliability**: Automatic failover to healthy AIs
2. **Performance**: Load balancing and smart routing
3. **Visibility**: Real-time monitoring and metrics
4. **Simplicity**: One system for everything

## Migration Checklist

- [ ] Remove imports of `LineBufferedSocket`
- [ ] Replace `socket_buffer` with `socket_client`
- [ ] Update discovery code to use unified registry
- [ ] Test with new `ai-discover` commands
- [ ] Enable health monitoring (automatic)

## Files Removed/Deprecated

### In aish:
- `src/utils/socket_buffer.py` - REMOVED
- `tests/test_socket_buffering.py` - REMOVED
- `docs/api/socket_communication.md` - DEPRECATED

### In Tekton:
- Various duplicate registry implementations
- Old socket handling code

## Need Help?

1. Check the main documentation: [UnifiedAIInterface.md](../Architecture/UnifiedAIInterface.md)
2. Run `ai-discover test` to verify setup
3. Use `--verbose` flag for debugging

## Quick Test

```bash
# Test everything is working
ai-discover test
ai-discover list --status healthy
echo "Hello unified system" | apollo
```

If these work, you're all set! 🎉