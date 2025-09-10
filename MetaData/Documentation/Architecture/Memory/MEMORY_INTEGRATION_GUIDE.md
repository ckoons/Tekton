# Tekton Memory Integration Guide

## Quick Start

The Tekton memory system is now fully integrated and automatic. All CI exchanges are stored in memory, reflections happen automatically, and sunrise contexts include relevant memories.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     CI Registry                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  update_ci_last_output()                         │   │
│  │  ├── Store exchange in registry                  │   │
│  │  ├── Auto-store in ESR memory ───────────┐      │   │
│  │  ├── Check reflection triggers           │      │   │
│  │  └── Detect sunset → trigger reflection  │      │   │
│  └──────────────────────────────────────────┼──────┘   │
│                                              │          │
│  ┌──────────────────────────────────────────▼──────┐   │
│  │  get_sunrise_context()                          │   │
│  │  ├── Get base context                           │   │
│  │  ├── Fetch recent memories from ESR ────────┐   │   │
│  │  └── Return enriched context                │   │   │
│  └──────────────────────────────────────────┼──┘   │
└─────────────────────────────────────────────┼──────────┘
                                               │
┌──────────────────────────────────────────────▼──────────┐
│                    Engram ESR                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  HTTP API (/api/esr/*)                          │   │
│  │  ├── /store    - Store thoughts                 │   │
│  │  ├── /recall   - Recall by ID                   │   │
│  │  ├── /search   - Search similar                 │   │
│  │  ├── /context  - Build context                  │   │
│  │  └── /reflect  - Trigger reflection             │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Cognitive Workflows                             │   │
│  │  ├── Natural memory operations                   │   │
│  │  ├── Thought types (IDEA, MEMORY, FACT...)      │   │
│  │  └── Memory metabolism                          │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Universal Encoder                               │   │
│  │  ├── Vector DB  - Semantic search                │   │
│  │  ├── Document   - Full fidelity                  │   │
│  │  ├── Key-Value  - Fast access                    │   │
│  │  └── SQL        - Complex queries                │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

## For Component Developers

### Automatic Memory Integration

Your component gets memory services automatically if it uses the CI Registry:

```python
from shared.aish.src.registry.ci_registry import get_registry

registry = get_registry()

# This automatically stores the exchange in memory
registry.update_ci_last_output("your-ci", {
    "user_message": "User's question",
    "content": "Your CI's response"
})

# This automatically includes recent memories
sunrise_context = registry.get_sunrise_context("your-ci")
```

### Manual Memory Operations

For custom memory operations:

```python
import asyncio

# Store a specific insight
memory_id = asyncio.run(
    registry.store_ci_memory(
        ci_name="your-ci",
        content="Important observation",
        thought_type="OBSERVATION"
    )
)

# Search memories
memories = asyncio.run(
    registry.recall_ci_memories(
        ci_name="your-ci",
        query="user preferences"
    )
)
```

## For CI Developers

### Using ESR in Your CI

CIs can directly interact with ESR for advanced memory operations:

```python
import httpx

async def store_insight(content: str, ci_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8100/api/esr/store",
            json={
                "content": content,
                "thought_type": "INSIGHT",
                "ci_id": ci_name,
                "confidence": 0.95
            }
        )
        return response.json()["memory_id"]

async def get_context(topic: str, ci_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8100/api/esr/context",
            json={
                "topic": topic,
                "depth": 3,
                "ci_id": ci_name
            }
        )
        return response.json()["context"]
```

### Memory Reflection in CIs

CIs can implement custom reflection logic:

```python
async def reflect_on_memories(ci_name: str):
    # Trigger reflection
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8100/api/esr/reflect",
            json={
                "ci_id": ci_name,
                "reason": "scheduled_reflection"
            }
        )
    
    # Get metabolism status
    response = await client.get(
        f"http://localhost:8100/api/esr/metabolism/status?ci_id={ci_name}"
    )
    status = response.json()
    
    print(f"Memories: {status['metabolism']['total_memories']}")
    print(f"Promoted: {status['metabolism']['promoted']}")
    print(f"Forgotten: {status['metabolism']['forgotten']}")
```

## For System Integrators

### Configuring Memory Services

1. **Ensure Engram is running**:
   ```bash
   cd Engram && python3 -m engram
   ```

2. **Verify ESR endpoints**:
   ```bash
   curl http://localhost:8100/api/esr/status
   ```

3. **Check memory metadata**:
   ```bash
   cat .tekton/registry/memory_metadata.json
   ```

### Monitoring Memory Health

```python
# Check memory statistics for all CIs
from shared.aish.src.registry.ci_registry import get_registry

registry = get_registry()
metadata = registry._memory_metadata

for ci_name, stats in metadata.items():
    print(f"{ci_name}:")
    print(f"  Memories: {stats['memory_count']}")
    print(f"  Last stored: {stats['last_stored']}")
    print(f"  Last reflection: {stats['last_reflection']}")
```

## Best Practices

### 1. Thought Type Selection
Choose appropriate thought types for better organization:
- `IDEA` - New concepts or proposals
- `MEMORY` - General recollections
- `FACT` - Verified information
- `OPINION` - Subjective assessments
- `QUESTION` - Unanswered queries
- `ANSWER` - Responses to questions
- `PLAN` - Future actions
- `REFLECTION` - Meta-thoughts about thoughts
- `FEELING` - Emotional states
- `OBSERVATION` - Noticed patterns

### 2. Confidence Levels
Set appropriate confidence:
- `1.0` - Certain facts
- `0.8-0.9` - High confidence observations
- `0.5-0.7` - Moderate confidence
- `0.3-0.5` - Uncertain/speculative
- `< 0.3` - Very uncertain (may be forgotten)

### 3. Context Metadata
Include useful context:
```python
context = {
    "source": "user_interaction",
    "session_id": "abc123",
    "timestamp": datetime.now().isoformat(),
    "tags": ["preference", "configuration"]
}
```

### 4. Reflection Triggers
Configure appropriate triggers:
- Time-based for regular CIs (hourly)
- Event-based for reactive CIs (sunset)
- Threshold-based for active CIs (50 memories)

## Troubleshooting

### Issue: Memories not being stored

**Check Engram is running**:
```bash
ps aux | grep engram
lsof -i :8100
```

**Verify ESR is available**:
```bash
curl -X GET http://localhost:8100/api/esr/status
```

**Check async operations**:
```python
# Ensure event loop is available
import asyncio
try:
    loop = asyncio.get_event_loop()
    print("Event loop available")
except:
    print("No event loop - async operations may fail")
```

### Issue: Sunrise context missing memories

**Check memories exist**:
```bash
curl -X POST http://localhost:8100/api/esr/search \
  -H "Content-Type: application/json" \
  -d '{"query": "apollo", "ci_id": "apollo", "limit": 5}'
```

**Verify retrieval timeout**:
- Default timeout is 30 seconds
- Network delays may cause timeouts
- Check Engram logs for errors

### Issue: Reflection not triggering

**Check metadata**:
```python
import json
with open('.tekton/registry/memory_metadata.json') as f:
    metadata = json.load(f)
    print(json.dumps(metadata, indent=2))
```

**Manual trigger**:
```bash
curl -X POST http://localhost:8100/api/esr/reflect \
  -H "Content-Type: application/json" \
  -d '{"ci_id": "apollo", "reason": "manual"}'
```

## Advanced Topics

### Custom Memory Backends

Add custom storage backends to the Universal Encoder:

```python
class CustomBackend:
    async def store(self, key: str, value: Any, metadata: Dict):
        # Custom storage logic
        pass
    
    async def retrieve(self, key: str) -> Any:
        # Custom retrieval logic
        pass
```

### Memory Visualization

Build memory graphs:

```python
import networkx as nx

# Get memories and build graph
memories = await registry.recall_ci_memories("apollo", limit=100)

G = nx.Graph()
for memory in memories:
    G.add_node(memory['id'], **memory)
    for assoc in memory.get('associations', []):
        G.add_edge(memory['id'], assoc)

# Analyze memory structure
print(f"Memory clusters: {nx.number_connected_components(G)}")
print(f"Central memories: {nx.degree_centrality(G)}")
```

### Cross-CI Memory Sharing

Enable controlled memory sharing:

```python
async def share_memory(from_ci: str, to_ci: str, memory_id: str):
    # Get memory from source CI
    memory = await recall_specific_memory(from_ci, memory_id)
    
    # Store in target CI with attribution
    await store_ci_memory(
        ci_name=to_ci,
        content=memory['content'],
        thought_type="SHARED",
        context={"shared_from": from_ci}
    )
```

## Summary

The Tekton memory system provides:
1. **Automatic integration** - No code changes needed
2. **Natural operations** - Human-like memory patterns
3. **Universal encoding** - Store everywhere, synthesize on recall
4. **Namespace isolation** - Each CI has private memories
5. **Reflection & metabolism** - Memories evolve naturally
6. **Sunrise enrichment** - Context includes relevant memories

The system is designed to be transparent, automatic, and natural - enabling CIs to maintain coherent, evolving memories without explicit memory management code.