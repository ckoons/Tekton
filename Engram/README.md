# Engram - Memory and Persistence Service

## Overview

Engram is Tekton's memory and persistence service, providing both traditional data storage and the advanced ESR (Encoding Storage Retrieval) system for natural, human-like memory operations for Companion Intelligences.

## Features

### ESR Memory System
- **Universal Encoding**: Store everywhere, synthesize on recall
- **Cognitive Workflows**: Natural memory operations (store, recall, associate, reflect)
- **Memory Metabolism**: Automatic promotion and forgetting
- **Multi-CI Support**: Isolated namespaces for each CI
- **Reflection Triggers**: Time-based, event-based, and threshold-based

### ESR Experience Layer (New!)
- **Emotional Context**: Memories tagged with emotions that influence recall
- **Working Memory**: 7±2 capacity with natural overflow handling
- **Interstitial Processing**: Automatic consolidation at cognitive boundaries
- **Memory Promises**: Non-blocking progressive recall with confidence gradients
- **Natural Forgetting**: Temporal decay and memory metabolism
- **Dream Recombination**: Novel associations during idle periods

### Traditional Storage
- **Nexus Processing**: Advanced data transformation
- **Structured Memory**: Key-value storage with metadata
- **Context Management**: Hierarchical context storage
- **Query Interface**: Flexible memory querying

### Integration
- **MCP Tools**: Model Context Protocol for AI/CI access
- **HTTP API**: RESTful endpoints for external access
- **CI Registry**: Automatic memory management for all CIs
- **Apollo Integration**: Memory reflection and context building

## Quick Start

### Installation
```bash
cd Engram
pip install -r requirements.txt
```

### Running Engram
```bash
python3 -m engram
```

Engram runs on port 8100 by default.

### Testing ESR
```bash
python3 test_esr_complete.py
```

## ESR API Reference

### Store Thought
```bash
POST /api/esr/store
{
  "content": "Memory content",
  "thought_type": "IDEA",
  "context": {},
  "confidence": 0.95,
  "ci_id": "apollo"
}
```

### Recall Memory
```bash
GET /api/esr/recall/{memory_id}?ci_id=apollo
```

### Search Similar
```bash
POST /api/esr/search
{
  "query": "search terms",
  "limit": 10,
  "ci_id": "apollo"
}
```

### Build Context
```bash
POST /api/esr/context
{
  "topic": "topic name",
  "depth": 3,
  "ci_id": "apollo"
}
```

### Trigger Reflection
```bash
POST /api/esr/reflect
{
  "ci_id": "apollo",
  "reason": "scheduled"
}
```

### Get Metabolism Status
```bash
GET /api/esr/metabolism/status?ci_id=apollo
```

### Get Namespaces
```bash
GET /api/esr/namespaces
```

### Check ESR Status
```bash
GET /api/esr/status
```

## MCP Tools

Engram provides the following MCP tools for CI access:

### Memory Tools
- `engram_MemoryStore` - Store memories
- `engram_MemoryQuery` - Query memories
- `engram_GetContext` - Get context

### Structured Memory
- `engram_StructuredMemoryAdd` - Add structured data
- `engram_StructuredMemoryGet` - Get by key
- `engram_StructuredMemoryUpdate` - Update existing
- `engram_StructuredMemoryDelete` - Delete by key
- `engram_StructuredMemorySearch` - Search with filters

### ESR Tools
- `esr_store_thought` - Store a thought
- `esr_recall_thought` - Recall by ID
- `esr_search_similar` - Find similar thoughts
- `esr_build_context` - Build topic context
- `esr_create_association` - Link memories
- `esr_get_metabolism_status` - Check memory health
- `esr_trigger_reflection` - Initiate reflection
- `esr_get_namespaces` - List CI namespaces

### Utility Tools
- `engram_NexusProcess` - Advanced data processing
- `engram_health_check` - Service health check
- `engram_component_info` - Component information

## Architecture

### Core Components

```
Engram/
├── engram/
│   ├── __main__.py              # Entry point
│   ├── api/
│   │   ├── server.py            # FastAPI server
│   │   └── controllers/
│   │       └── esr.py           # ESR HTTP endpoints
│   ├── core/
│   │   ├── engram_component.py  # Main component
│   │   ├── mcp/
│   │   │   ├── esr_tools.py     # ESR MCP tools
│   │   │   └── hermes_bridge.py # MCP registration
│   │   └── storage/
│   │       ├── cognitive_workflows.py  # Natural memory ops
│   │       ├── universal_encoder.py    # Store everywhere
│   │       └── unified_interface.py    # ESR system
│   └── storage/
│       ├── cache.py             # Cache layer
│       ├── context.py           # Context management
│       └── nexus.py             # Nexus processing
```

### Storage Backends

1. **Vector Database** - Semantic similarity search
2. **Document Store** - Full fidelity storage
3. **Key-Value Store** - Fast access
4. **SQL Database** - Complex queries

### Memory Flow

```
User/CI → HTTP/MCP → Cognitive Workflows → Universal Encoder → All Backends
                                         ↓
                                    Cache Layer
                                         ↓
                                  Memory Metabolism
                                         ↓
                                     Reflection
```

## Configuration

### Environment Variables
```bash
ENGRAM_PORT=8100              # Service port
TEKTON_ROOT=/path/to/tekton   # Tekton root
ENGRAM_AI_PORT=41000          # AI specialist port
```

### Memory Settings
- Cache size: 100,000 entries
- Reflection interval: 1 hour
- Reflection threshold: 50 memories
- Confidence threshold: 0.5
- Context depth: 3 levels

## Integration with CI Registry

The CI Registry automatically integrates with Engram:

```python
from shared.aish.src.registry.ci_registry import get_registry

registry = get_registry()

# Automatic memory storage on every exchange
registry.update_ci_last_output("apollo", {
    "user_message": "Question",
    "content": "Response"
})

# Sunrise context includes memories
context = registry.get_sunrise_context("apollo")
```

## Development

### Running Tests
```bash
# Unit tests
pytest tests/

# ESR integration test
python3 test_esr_complete.py

# Cognitive workflows test
pytest tests/test_cognitive_workflows.py
```

### Adding New Thought Types
```python
class ThoughtType(Enum):
    YOUR_TYPE = "YOUR_TYPE"
```

### Custom Memory Backends
```python
class CustomBackend:
    async def store(self, key, value, metadata):
        # Implementation
    
    async def retrieve(self, key):
        # Implementation
```

## Troubleshooting

### Service Not Starting
- Check port 8100 is available
- Verify Python dependencies installed
- Check logs in `.tekton/logs/engram.log`

### ESR Not Working
- Verify all backends are connected
- Check ESR status endpoint
- Review error logs for import issues

### Memory Not Persisting
- Check file permissions in `/tmp/tekton/`
- Verify backends are initialized
- Check memory metadata file

## Documentation

- [ESR System Documentation](docs/ESR_SYSTEM.md)
- [Experience Layer Documentation](engram/core/experience/README.md)
- [Experience Layer Executive Summary](../MetaData/DevelopmentSprints/Encoding_Storage_Retrieval_Sprint/EXPERIENCE_LAYER_EXECUTIVE_SUMMARY.md)
- [Integration Guide](../MetaData/DevelopmentSprints/Encoding_Storage_Retrieval_Sprint/INTEGRATION_GUIDE.md)
- [CI Registry Memory Integration](../shared/aish/docs/CI_REGISTRY_MEMORY.md)
- [Memory Integration Guide](../docs/MEMORY_INTEGRATION_GUIDE.md)

## Future Enhancements

1. **Memory Consolidation** - Merge similar memories over time
2. **Cross-CI Sharing** - Controlled memory exchange between CIs
3. **Memory Analytics** - Insights from memory patterns
4. **Temporal Queries** - Time-based memory retrieval
5. **Memory Visualization** - Graph-based exploration

## Contributing

Engram is part of the Tekton project. Contributions should follow Tekton's development guidelines and maintain compatibility with the CI Registry integration.

## License

Part of the Tekton project - see main project license.