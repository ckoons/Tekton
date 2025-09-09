# Apollo Preparation System - Architecture

## System Overview

Apollo is the "library god" of Tekton, responsible for preparing, curating, and delivering Context Briefs to CIs. The Preparation system replaces the scattered memory management with a centralized, graph-integrated service that treats memories as navigable landmarks.

## Core Concepts

### Context Brief
A Context Brief is a token-aware, curated package of relevant information prepared for a CI before processing a message. It includes:
- Relevant memories (decisions, insights, errors, plans, context)
- Landmark references from the knowledge graph
- Latent space configurations
- Token-optimized formatting

### Memory as Landmarks
Memories are not just stored data but navigable landmarks in the knowledge graph:
- Each memory becomes a node with properties
- Relationships connect cause-effect chains
- Temporal edges show progression
- Cross-references link related concepts

### MCP-First Architecture
- **Primary**: MCP tools for CI-to-CI communication
- **Secondary**: HTTP endpoints for UI access only
- **No Direct HTTP**: CIs never call HTTP endpoints directly

## Component Architecture

### Apollo Preparation Module
```
/Apollo/apollo/core/preparation/
├── context_brief.py         # Main Context Brief manager
├── brief_presenter.py       # Formats briefs for consumption
├── memory_extractor.py      # Extracts memories from exchanges
├── landmark_manager.py      # Manages memory landmarks
└── token_optimizer.py       # Token-aware selection
```

### MCP Tools
```
/Apollo/apollo/mcp/
├── preparation_tools.py     # MCP tool definitions
├── __init__.py             # Tool registration
└── schemas.py              # Request/response schemas
```

### Knowledge Graph Integration
```
Apollo Namespace
├── Entities
│   ├── Decision Landmarks
│   ├── Insight Landmarks
│   ├── Error Landmarks
│   ├── Plan Landmarks
│   └── Context Landmarks
└── Relationships
    ├── CAUSED_BY
    ├── LED_TO
    ├── RESOLVED_BY
    ├── REFERENCES
    ├── CONTRADICTS
    ├── SUPPORTS
    ├── BEFORE
    ├── AFTER
    └── DURING
```

## Data Flow

### Context Brief Request Flow
```
CI Request → MCP Tool Call → Apollo
                ↓
        Load CI Registry Info
                ↓
        Query Memory Catalog
                ↓
        Score Relevance
                ↓
        Query Knowledge Graph
                ↓
        Pack Within Token Budget
                ↓
        Format Context Brief
                ↓
CI ← MCP Response ← Apollo
```

### Memory Extraction Flow
```
CI Exchange → Post-Message Hook → Apollo MCP Tool
                    ↓
            Extract Patterns
                    ↓
            Create Memory Item
                    ↓
            Generate Landmark
                    ↓
            Store in Catalog
                    ↓
            Add to Graph → Athena
```

## MCP Tool Specifications

### get_context_brief
```python
Input:
{
    "ci_name": "ergon-ci",
    "message": "Current message content",
    "max_tokens": 2000,
    "include_landmarks": true
}

Output:
{
    "brief": "Formatted context text",
    "memories": [...],
    "landmarks": [...],
    "token_count": 1850
}
```

### store_memory
```python
Input:
{
    "ci_source": "ergon-ci",
    "type": "decision",
    "summary": "Chose Redux for state",
    "content": "Full decision details...",
    "tags": ["redux", "architecture"],
    "priority": 8
}

Output:
{
    "memory_id": "mem_20250829_abc123",
    "landmark_id": "lmk_decision_redux",
    "status": "stored"
}
```

### search_memories
```python
Input:
{
    "query": "redux performance",
    "ci_filter": "ergon-ci",
    "type_filter": ["decision", "insight"],
    "limit": 10
}

Output:
{
    "memories": [...],
    "total_count": 42,
    "landmarks": [...]
}
```

## Landmark Schema

### Memory Landmark Node
```python
{
    "entity_id": "lmk_decision_20250829_redux",
    "entity_type": "memory_landmark",
    "name": "Redux State Management Decision",
    "properties": {
        "memory_type": "decision",
        "summary": "Chose Redux for state management",
        "ci_source": "ergon-ci",
        "timestamp": "2025-08-29T14:00:00Z",
        "priority": 8,
        "tags": ["redux", "architecture", "state"],
        "token_count": 245,
        "expires": "2025-09-05T14:00:00Z"
    },
    "namespace": "apollo",
    "confidence": 0.9
}
```

### Landmark Relationships
```python
{
    "relationship_id": "rel_001",
    "source_id": "lmk_error_import",
    "target_id": "lmk_decision_refactor",
    "relationship_type": "LED_TO",
    "properties": {
        "timestamp": "2025-08-29T15:00:00Z",
        "confidence": 0.85,
        "extracted_by": "apollo"
    }
}
```

## Storage Architecture

### Catalog Storage
```
/Apollo/apollo/data/preparation/
├── catalog.json           # Main memory catalog
├── briefs/                # Cached Context Briefs
│   └── {ci_name}.json
└── landmarks/             # Landmark definitions
    └── landmarks.json
```

### Graph Storage
- Apollo namespace in Athena's graph
- NetworkX in-memory with JSON persistence
- Separate from codebase knowledge graph
- Can query across namespaces if needed

## Token Management

### Token Budget Allocation
```python
MAX_CONTEXT_TOKENS = 2000  # Default

# Allocation strategy
MEMORY_TOKENS = 1500      # 75% for memories
LANDMARK_TOKENS = 300      # 15% for landmark refs
METADATA_TOKENS = 200      # 10% for formatting
```

### Progressive Disclosure
1. **Full Content**: When tokens available
2. **Summary Only**: When near limit
3. **Reference Only**: When over limit
4. **Omit**: When not relevant enough

## UI Integration

### Preparation Tab Components
```
Preparation Tab
├── Memory Catalog Browser
│   ├── Search Bar
│   ├── Type Filters
│   ├── CI Filters
│   └── Memory List
├── Context Brief Builder
│   ├── CI Selector
│   ├── Brief Preview
│   └── Token Counter
├── Landmark Visualizer
│   ├── Graph View
│   ├── Timeline View
│   └── Relationship Explorer
└── Latent Space Config
    ├── Embedding Settings
    └── Vector Configs
```

## Performance Considerations

### Caching Strategy
- Cache Context Briefs for 5 minutes
- Cache relevance scores per context
- Pre-compute token counts
- Lazy load landmark relationships

### Async Processing
- Memory extraction happens async
- Graph updates are queued
- Brief generation is parallelized
- Batch landmark creation

### Scalability
- Shard by CI name for large deployments
- Consider Redis for production caching
- Graph queries optimized with indexes
- Memory pagination for large catalogs

## Security Considerations

### Access Control
- Memories are per-CI isolated by default
- Global memories require permission
- Landmark creation requires authentication
- Graph queries respect namespaces

### Sensitive Data
- Pattern matching detects secrets
- Automatic redaction of API keys
- PII detection and masking
- Audit trail for all access

## Migration Path

### Phase 1: Code Movement
1. Move files to Apollo
2. Update imports
3. Run existing tests

### Phase 2: MCP Addition
1. Add MCP tools alongside HTTP
2. Test with one CI
3. Gradually migrate all CIs

### Phase 3: Graph Integration
1. Create Apollo namespace
2. Mirror memories as landmarks
3. Build relationships gradually

### Phase 4: Rhetor Cleanup
1. Deprecate memory endpoints
2. Update to use Apollo MCP
3. Remove memory code

## Success Metrics

### Quantitative
- Token usage under limit 100% of time
- Context Brief generation <100ms
- Memory extraction <500ms
- Graph queries <50ms

### Qualitative
- CIs have appropriate context
- Memories form useful landmarks
- Relationships reveal patterns
- UI provides clear insights