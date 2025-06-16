# Engram Migration Guide

Moving from Engram v0.6.x to v0.7.0 (Simplified API)

## What Changed

### Before (v0.6.x)
- 5+ different APIs (MemoryService, StructuredMemory, ez(), cognitive layer, etc.)
- Complex initialization
- Confusing namespace management
- Verbose logging by default
- Many experimental features

### After (v0.7.0)
- 1 simple Memory class
- 3 methods: store(), recall(), context()
- Clean imports
- Silent by default
- Just the essentials

## Migration Examples

### Basic Memory Storage

**Old Way:**
```python
from engram.core.memory import MemoryService

memory = MemoryService(client_id="my_app")
await memory.add(
    content="Important note",
    namespace="conversations",
    metadata={"tags": ["important"]}
)
```

**New Way:**
```python
from engram import Memory

mem = Memory()
await mem.store("Important note", tags=["important"])
```

### Memory Search

**Old Way:**
```python
results = await memory.search(
    query="important",
    namespace="conversations", 
    limit=5
)
for r in results:
    print(r.text)
```

**New Way:**
```python
results = await mem.recall("important", limit=5)
for r in results:
    print(r.content)
```

### Getting Context

**Old Way:**
```python
context = await memory.get_relevant_context(
    query="project setup",
    namespaces=["conversations", "thinking"],
    limit=10
)
```

**New Way:**
```python
context = await mem.context("project setup", limit=10)
```

### Structured Memory

**Old Way:**
```python
from engram.core.structured_memory import StructuredMemory

structured = StructuredMemory()
await structured.add_memory(
    content="User feedback",
    category="feedback",
    importance=0.8,
    tags=["ui", "improvement"]
)

results = await structured.search_memories(
    query="feedback",
    category="feedback",
    min_importance=0.5
)
```

**New Way:**
```python
# All in one API now!
await mem.store(
    "User feedback",
    category="feedback",
    importance=0.8,
    tags=["ui", "improvement"]
)

# Metadata is preserved in results
results = await mem.recall("feedback")
for r in results:
    if r.metadata.get("importance", 0) >= 0.5:
        print(r.content)
```

### Cognitive Layer (ez, think, etc.)

**Old Way:**
```python
from engram.cognitive import ez, s, w, l

await ez()
await s("Store this thought")
memories = await w("search for thoughts")
```

**New Way:**
```python
# Just use the Memory class directly
await mem.store("Store this thought")
memories = await mem.recall("search for thoughts")
```

### Memory Manager

**Old Way:**
```python
from engram.core.memory_manager import MemoryManager

manager = MemoryManager()
service = await manager.get_memory_service("client_123")
await service.add("Memory for client 123")
```

**New Way:**
```python
# Use namespace for client separation
client_mem = Memory(namespace="client_123")
await client_mem.store("Memory for client 123")
```

### MCP Tools

The MCP tools continue to work unchanged! The compatibility layer handles the translation automatically.

If you're implementing new MCP tools:

```python
from engram.api.mcp_compat import memory_store, memory_query, get_context

# These functions provide MCP-compatible interfaces
```

## Removed Features

The following experimental features have been removed:

1. **Katra System** - Memory provenance tracking
2. **Dream States** - Background memory processing  
3. **Emotional Memory** - Emotion-tagged memories
4. **Peer Awareness** - Multi-AI communication
5. **Memory Streams** - Stream-based memory interface
6. **Complex Context Management** - Auto-switching contexts

If you were using these features, they'll need to be reimplemented with the simple API or found in alternative solutions.

## Namespace Changes

**Old Way:**
```python
# Fixed namespaces
memory.add(content, namespace="conversations")  # Required
memory.add(content, namespace="thinking")       # Different namespace
```

**New Way:**
```python
# Namespace in constructor
conv_mem = Memory("conversations")
think_mem = Memory("thinking")

# Or just use default
mem = Memory()  # Uses "default" namespace
```

## Configuration Changes

### Logging

**Old Way:**
```python
# Always verbose
# 40+ lines of initialization output
```

**New Way:**
```python
# Silent by default
# Set ENGRAM_DEBUG=true for verbose output
```

### Data Directory

Both versions use `~/.engram/` by default. Override with:
```bash
ENGRAM_DATA_DIR=/custom/path python script.py
```

## Common Patterns

### Initialize Once
```python
# At module level or in __init__
memory = Memory()

# Use throughout your application
async def process_message(msg):
    await memory.store(msg)
```

### Separate Concerns
```python
# Different memory spaces for different purposes
user_prefs = Memory("preferences")
conversation = Memory("conversation")
technical = Memory("technical")
```

### Metadata is Your Friend
```python
# Rich metadata helps with organization
await mem.store(
    "Design decision: Use REST API",
    category="architecture",
    tags=["api", "design", "decision"],
    date="2024-01-15",
    author="team",
    importance=0.9
)
```

## Troubleshooting

### Import Errors
```python
# Old imports won't work
from engram.cognitive import ez  # ImportError

# Use new import
from engram import Memory
```

### Missing Methods
```python
# These don't exist anymore
memory.add_to_session()  # AttributeError
memory.get_compartments()  # AttributeError

# Use the simple API
await mem.store("content")
```

### Different Result Format
```python
# Old: results have .text attribute
for r in results:
    print(r.text)

# New: results have .content attribute  
for r in results:
    print(r.content)
```

## Step-by-Step Migration

1. **Update imports**
   ```python
   # from engram.core.memory import MemoryService
   from engram import Memory
   ```

2. **Replace initialization**
   ```python
   # memory = MemoryService(client_id="app")
   memory = Memory()
   ```

3. **Update method calls**
   - `add()` → `store()`
   - `search()` → `recall()`
   - `get_relevant_context()` → `context()`

4. **Adjust result handling**
   - `.text` → `.content`
   - Check metadata format

5. **Remove experimental features**
   - No more cognitive imports
   - No more provenance tracking

6. **Test thoroughly**
   - Verify storage works
   - Check search returns results
   - Ensure metadata preserved

## Need Help?

The new API is designed to be self-explanatory. If you're unsure:

1. Check the [examples/](examples/) directory
2. Read the [API Reference](API_REFERENCE.md)
3. Look at [simple_usage.py](examples/simple_usage.py)

Remember: If it seems complicated, you're probably overthinking it. The new API really is just three methods!