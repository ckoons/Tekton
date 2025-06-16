# Engram - Simple Memory for AI

Engram provides persistent memory for AI assistants with just 3 methods.

## Installation

```bash
pip install engram
```

## Quick Start

```python
from engram import Memory

# Create memory instance
mem = Memory()

# Store a thought
await mem.store("The user prefers dark mode")

# Recall memories
results = await mem.recall("user preferences")

# Get context for a task  
context = await mem.context("building a settings page")
```

That's it. No configuration, no complexity.

## API Reference

### Memory Class

#### `Memory(namespace="default")`
Create a memory instance with optional namespace.

#### `await store(content, **metadata)`
Store content with optional metadata.

**Parameters:**
- `content` (str): Text to remember
- `**metadata`: Optional tags, category, importance, etc.

**Returns:** Memory ID (str)

#### `await recall(query, limit=5)`
Find memories similar to query.

**Parameters:**
- `query` (str): What to search for
- `limit` (int): Max results (default: 5)

**Returns:** List of MemoryItem objects with:
- `id`: Unique identifier
- `content`: The stored text
- `timestamp`: When stored
- `metadata`: Any metadata
- `relevance`: Match score

#### `await context(query, limit=10)`
Get formatted context for prompts.

**Parameters:**
- `query` (str): Topic needing context
- `limit` (int): Max memories to include

**Returns:** Formatted string with relevant memories

## Examples

### Basic Usage

```python
from engram import Memory

mem = Memory()

# Store memories with metadata
await mem.store("User's API key: sk-...", importance=1.0, category="secrets")
await mem.store("Project uses React", tags=["tech-stack"])

# Find specific memories
secrets = await mem.recall("API key")
tech_stack = await mem.recall("technologies", limit=10)
```

### Using Context in Prompts

```python
# Get background for an LLM prompt
context = await mem.context("debugging React errors")

prompt = f"""
{context}

User: My React app shows a white screen
Assistant: Based on the context...
"""
```

### Multiple Namespaces

```python
# Separate memories by purpose
personal = Memory("personal")
await personal.store("User's name is Alice")

technical = Memory("technical") 
await technical.store("Prefers Python type hints")
```

## Storage

Engram automatically uses the best available storage:
- **Vector search** (FAISS) for semantic similarity
- **File storage** fallback if vectors unavailable
- Data stored in `~/.engram/`

## Migration from Old APIs

See [migration_example.py](examples/migration_example.py) for moving from older Engram APIs.

## Debugging

Set `ENGRAM_DEBUG=true` for verbose logging:

```bash
ENGRAM_DEBUG=true python your_script.py
```

## Requirements

- Python 3.8+
- asyncio support

Optional for better performance:
- faiss-cpu or faiss-gpu
- sentence-transformers

## License

MIT

## Philosophy

> "The best interface is no interface. The best code is no code. The best memory system is one that just remembers."

Engram v0.7.0 - Simplified for clarity.