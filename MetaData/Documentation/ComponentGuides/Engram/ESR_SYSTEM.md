# ESR (Encoding Storage Retrieval) System Documentation

## Overview

The ESR system provides natural, human-like memory operations for Tekton's Companion Intelligences (CIs). Built on the principle of "universal encoding" - store everywhere, synthesize on recall - ESR enables CIs to maintain coherent, evolving memories across conversations and sessions.

## Architecture

### Core Components

1. **Universal Encoder** (`engram/core/storage/universal_encoder.py`)
   - Stores memories across multiple backends simultaneously
   - Synthesizes coherent memories on recall
   - Backends: Vector DB, Document Store, Key-Value, SQL

2. **Cognitive Workflows** (`engram/core/storage/cognitive_workflows.py`)
   - Natural memory operations replacing mechanical database operations
   - Thought types: IDEA, MEMORY, FACT, OPINION, QUESTION, ANSWER, PLAN, REFLECTION, FEELING, OBSERVATION
   - Memory metabolism: promotion and natural forgetting

3. **MCP Tools** (`engram/core/mcp/esr_tools.py`)
   - Model Context Protocol tools for AI/CI interactions
   - 8 specialized tools for memory operations
   - Namespace isolation for multi-CI support

4. **HTTP API** (`engram/api/controllers/esr.py`)
   - RESTful endpoints for external access
   - Pydantic models for request/response validation
   - Wraps MCP tools for HTTP access

## Memory Operations

### Store Thought
```python
POST /api/esr/store
{
  "content": "Testing ESR system",
  "thought_type": "IDEA",
  "context": {"test": true},
  "confidence": 0.95,
  "ci_id": "apollo"
}
```

### Recall Thought
```python
GET /api/esr/recall/{memory_id}?ci_id=apollo
```

### Search Similar
```python
POST /api/esr/search
{
  "query": "ESR system",
  "limit": 10,
  "min_confidence": 0.5,
  "ci_id": "apollo"
}
```

### Build Context
```python
POST /api/esr/context
{
  "topic": "Apollo integration",
  "depth": 3,
  "ci_id": "apollo"
}
```

### Trigger Reflection
```python
POST /api/esr/reflect
{
  "ci_id": "apollo",
  "reason": "sunset_protocol"
}
```

## CI Registry Integration

The ESR system is deeply integrated with the CI Registry for automatic memory management:

### Automatic Memory Storage
- Every CI exchange is automatically stored in ESR
- User messages and CI responses are combined as memories
- Thought types are automatically determined (ANSWER for Q&A, MEMORY for statements)

### Memory Reflection Triggers
- **Time-based**: Every hour
- **Threshold-based**: Every 50 memories
- **Event-based**: Sunset protocol detection
- **Explicit**: Manual trigger via API

### Sunrise Context Enrichment
- Recent memories are automatically included in sunrise context
- Top 3 most relevant memories are summarized
- Provides continuity across CI sessions

## Memory Metabolism

The system implements natural memory processes:

### Promotion
- Frequently accessed memories gain strength
- Important patterns are consolidated
- Cross-referenced memories form associations

### Forgetting
- Unused memories gradually decay
- Low-confidence memories are pruned
- Maintains optimal memory pool size

### Reflection
- Periodic synthesis of memory patterns
- Extraction of key insights
- Memory reorganization for efficiency

## Namespace Isolation

Each CI maintains its own memory namespace:
- `apollo` - Attention and prediction memories
- `athena` - Strategy and wisdom memories
- `rhetor` - Communication optimization memories
- `metis` - Analysis and insight memories
- etc.

## MCP Tools Reference

### esr_store_thought
Store a new thought/memory

### esr_recall_thought
Recall a specific memory by ID

### esr_search_similar
Search for similar thoughts

### esr_build_context
Build context around a topic

### esr_create_association
Link related memories

### esr_get_metabolism_status
Check memory health metrics

### esr_trigger_reflection
Initiate memory reflection

### esr_get_namespaces
List active CI namespaces

## Configuration

### Environment Variables
```bash
ENGRAM_PORT=8100           # Engram service port
TEKTON_ROOT=/path/to/tekton # Tekton root directory
```

### Memory Limits
- Cache size: 100,000 entries
- Reflection interval: 1 hour
- Reflection threshold: 50 memories
- Context depth: 3 levels

## Usage Examples

### Python Client
```python
import httpx

# Store a memory
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8100/api/esr/store",
        json={
            "content": "Important insight about user preferences",
            "thought_type": "OBSERVATION",
            "ci_id": "apollo"
        }
    )
    memory_id = response.json()["memory_id"]
```

### Via CI Registry
```python
from shared.aish.src.registry.ci_registry import get_registry

registry = get_registry()

# Automatic storage happens in update_ci_last_output
registry.update_ci_last_output("apollo", {
    "user_message": "How does ESR work?",
    "content": "ESR uses universal encoding..."
})

# Memories are automatically included in sunrise context
context = registry.get_sunrise_context("apollo")
```

## Testing

Run the comprehensive test:
```bash
python3 test_esr_complete.py
```

This tests:
- All ESR API endpoints
- Multi-CI namespace support
- Memory reflection triggers
- Apollo integration
- MCP tool registration

## Performance Considerations

- Memories are stored asynchronously to avoid blocking
- Cache layer provides fast frequency-based access
- Vector search enables semantic similarity matching
- SQL backend allows complex queries
- Document store preserves full fidelity

## Future Enhancements

1. **Memory Consolidation**: Periodic merging of similar memories
2. **Cross-CI Memory Sharing**: Controlled memory exchange between CIs
3. **Memory Visualization**: Graph-based memory exploration
4. **Temporal Queries**: Time-based memory retrieval
5. **Memory Export/Import**: Backup and migration capabilities