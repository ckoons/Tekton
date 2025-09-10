# CI Registry Memory Integration

## Overview

The CI Registry now includes integrated memory services powered by Engram's ESR (Encoding Storage Retrieval) system. This enables automatic memory management for all Companion Intelligences without requiring code changes to individual CIs.

## Features

### Automatic Memory Storage
Every CI exchange is automatically stored in the ESR memory system when `update_ci_last_output()` is called. No additional code is required in CI implementations.

### Memory Reflection
The system automatically triggers memory reflection based on:
- **Time intervals**: Every hour
- **Memory count**: Every 50 new memories
- **Events**: Sunset protocol detection
- **Manual triggers**: Via API calls

### Sunrise Context Enrichment
When a CI starts a new session, its sunrise context automatically includes relevant recent memories, providing continuity across conversations.

## API Reference

### Memory Storage
```python
async def store_ci_memory(
    ci_name: str, 
    content: str,
    thought_type: str = "MEMORY",
    context: Optional[Dict[str, Any]] = None,
    confidence: float = 1.0
) -> Optional[str]
```
Store a memory for a CI. Returns memory ID if successful.

### Memory Recall
```python
async def recall_ci_memories(
    ci_name: str,
    query: str = None,
    limit: int = 10
) -> List[Dict[str, Any]]
```
Recall memories for a CI, optionally filtered by a search query.

### Memory Reflection
```python
async def trigger_ci_reflection(
    ci_name: str,
    reason: str = "scheduled"
) -> bool
```
Trigger memory reflection process for a CI.

### Memory Context
```python
async def get_ci_memory_context(
    ci_name: str,
    topic: str,
    depth: int = 3
) -> Optional[Dict[str, Any]]
```
Build memory context around a specific topic.

### Reflection Check
```python
def should_trigger_reflection(ci_name: str) -> bool
```
Check if a CI should trigger memory reflection based on configured thresholds.

## Automatic Integration

### Exchange Storage
When `update_ci_last_output()` is called:
1. The exchange is stored in registry state (as before)
2. The exchange is automatically stored in ESR memory
3. Reflection is triggered if thresholds are met
4. Sunset responses trigger immediate reflection

### Memory-Enhanced Sunrise
When `get_sunrise_context()` is called:
1. Base sunrise context is retrieved (as before)
2. Recent memories are fetched from ESR
3. Top 3 most relevant memories are summarized
4. Enhanced context is returned

## Configuration

### Memory Metadata
The registry tracks memory metadata in `memory_metadata`:
```json
{
  "apollo": {
    "memory_count": 150,
    "last_stored": "2025-09-10T10:30:00",
    "last_reflection": "2025-09-10T09:30:00"
  }
}
```

### Reflection Settings
- Default interval: 1 hour
- Count threshold: 50 memories
- Sunset detection: Automatic trigger

## Usage Examples

### Manual Memory Storage
```python
from shared.aish.src.registry.ci_registry import get_registry
import asyncio

registry = get_registry()

# Store a specific memory
memory_id = asyncio.run(
    registry.store_ci_memory(
        ci_name="apollo",
        content="User prefers concise responses",
        thought_type="OBSERVATION",
        confidence=0.9
    )
)
```

### Manual Memory Recall
```python
# Recall recent memories
memories = asyncio.run(
    registry.recall_ci_memories(
        ci_name="apollo",
        query="user preferences",
        limit=5
    )
)

for memory in memories:
    print(f"- {memory['content'][:100]}...")
```

### Manual Reflection Trigger
```python
# Trigger reflection
success = asyncio.run(
    registry.trigger_ci_reflection(
        ci_name="apollo",
        reason="manual_request"
    )
)
```

### Checking Reflection Status
```python
# Check if reflection is needed
if registry.should_trigger_reflection("apollo"):
    asyncio.run(
        registry.trigger_ci_reflection("apollo", "threshold_reached")
    )
```

## Integration with Existing Features

### Sunset/Sunrise Protocol
- Sunset responses automatically trigger memory reflection
- Sunrise context includes recent memory summary
- Memory continuity across CI sessions

### Apollo-Rhetor Coordination
- Apollo can access CI memories for better planning
- Rhetor can use memory context for prompt optimization
- Shared memory enables better coordination

### Project CIs
- Each project CI gets its own memory namespace
- Project-specific memories are isolated
- Cross-project memory sharing controlled

## Memory Namespaces

Each CI maintains an isolated memory namespace:
- Greek Chorus CIs: `apollo`, `athena`, `rhetor`, etc.
- Project CIs: `project-name-ci`
- Terminals: `terminal-name`
- Tools: `tool-name`

## Performance Considerations

- Memory operations are asynchronous (non-blocking)
- Failures in memory storage don't affect normal operation
- Memory retrieval has timeouts to prevent hanging
- Reflection runs in background tasks

## Troubleshooting

### Memory Not Storing
- Check Engram is running on port 8100
- Verify ESR endpoints are registered
- Check `.tekton/registry/memory_metadata.json`

### Reflection Not Triggering
- Check last_reflection timestamp
- Verify memory_count threshold
- Look for reflection logs in Engram

### Sunrise Context Missing Memories
- Ensure memories exist for the CI
- Check ESR search is working
- Verify async operations are completing

## Future Enhancements

1. **Configurable Reflection Intervals**: Per-CI reflection settings
2. **Memory Sharing Controls**: Fine-grained access between CIs
3. **Memory Analytics**: Insights from memory patterns
4. **Memory Pruning Policies**: Automatic cleanup strategies
5. **Cross-Session Memory**: Persistent memories across Tekton restarts