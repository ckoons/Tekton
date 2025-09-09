# Rhetor Memory Catalog System - Architecture

## System Overview

The Rhetor Memory Catalog System replaces the current "memory bombing" approach with an intelligent, curated memory service that provides token-aware context injection to CIs.

## Architecture Principles

### 1. Separation of Concerns
- **Apollo**: Memory extraction and insight generation
- **Rhetor**: Memory storage, curation, and presentation
- **CIs**: Consume memory as a service, remain black boxes

### 2. Token Budget Management
- Strict enforcement of max_injection_size (2000 tokens default)
- Smart selection algorithm prioritizes relevant memories
- Progressive disclosure: summaries first, details on request

### 3. Hook-Based Integration
- Pre-message hooks inject relevant context
- Post-message hooks extract new insights
- No modifications to CI internals required

## Component Architecture

### Memory Catalog (Rhetor)
```
┌─────────────────────────────────────┐
│         Memory Catalog              │
├─────────────────────────────────────┤
│  Storage Layer (JSON/SQLite)        │
│  ├── catalog_{ci_name}.json         │
│  └── catalog_global.json            │
├─────────────────────────────────────┤
│  Catalog API                        │
│  ├── search(query, filters)         │
│  ├── get_relevant(ci, context)      │
│  ├── store(memory_item)             │
│  └── expire_old()                   │
├─────────────────────────────────────┤
│  Token Manager                      │
│  ├── count_tokens(text)             │
│  ├── optimize_selection(memories)   │
│  └── format_injection(memories)     │
└─────────────────────────────────────┘
```

### Memory Extractor (Apollo)
```
┌─────────────────────────────────────┐
│       Memory Extractor              │
├─────────────────────────────────────┤
│  Pattern Matchers                   │
│  ├── DecisionExtractor              │
│  ├── InsightExtractor               │
│  ├── ErrorExtractor                 │
│  └── PlanExtractor                  │
├─────────────────────────────────────┤
│  Tagging Engine                     │
│  ├── extract_keywords()             │
│  ├── identify_topics()              │
│  └── assign_relevance()             │
├─────────────────────────────────────┤
│  Summarizer                         │
│  ├── create_summary(content)        │
│  └── extract_key_points()           │
└─────────────────────────────────────┘
```

### Hook Integration Layer
```
┌─────────────────────────────────────┐
│      specialist_worker.py           │
├─────────────────────────────────────┤
│  pre_message_hook()                 │
│  ├── Get CI context                 │
│  ├── Query memory catalog           │
│  ├── Select relevant memories       │
│  └── Inject into message            │
├─────────────────────────────────────┤
│  post_message_hook()                │
│  ├── Analyze exchange               │
│  ├── Extract insights               │
│  ├── Create memory items            │
│  └── Store in catalog               │
└─────────────────────────────────────┘
```

## Data Flow

### Memory Injection Flow
```
User Message → CI Handler → pre_message_hook → Memory Catalog
                                ↓
                    Relevant Memories Selected
                                ↓
                    Token Budget Check
                                ↓
                    Format as Context
                                ↓
                    Inject into Message → Process Message
```

### Memory Extraction Flow
```
CI Response → post_message_hook → Apollo Extractor
                    ↓
            Identify Insights
                    ↓
            Create Memory Items
                    ↓
            Tag and Score
                    ↓
            Store in Catalog → Available for Future
```

## Memory Selection Algorithm

### Relevance Scoring
```python
def calculate_relevance(memory: MemoryItem, context: dict) -> float:
    score = 0.0
    
    # Recency factor (exponential decay)
    age_hours = (now - memory.timestamp).total_seconds() / 3600
    recency_score = math.exp(-age_hours / 168)  # 1 week half-life
    score += recency_score * 0.3
    
    # Tag match factor
    context_tags = extract_tags(context['message'])
    tag_overlap = len(set(memory.tags) & set(context_tags))
    tag_score = tag_overlap / max(len(memory.tags), 1)
    score += tag_score * 0.4
    
    # CI affinity factor
    if memory.ci_source == context['ci_name']:
        score += 0.2
    
    # Priority override
    score += (memory.priority / 10) * 0.1
    
    return min(score, 1.0)
```

### Token-Aware Packing
```python
def pack_memories(memories: List[MemoryItem], max_tokens: int) -> List[MemoryItem]:
    # Sort by relevance
    sorted_memories = sorted(memories, key=lambda m: m.relevance, reverse=True)
    
    selected = []
    token_count = 0
    
    for memory in sorted_memories:
        if token_count + memory.tokens <= max_tokens:
            selected.append(memory)
            token_count += memory.tokens
        elif token_count + len(memory.summary) <= max_tokens:
            # Include just summary if full content doesn't fit
            memory.content = memory.summary
            memory.tokens = len(memory.summary)
            selected.append(memory)
            token_count += memory.tokens
    
    return selected
```

## Storage Schema

### Memory Catalog File Structure
```json
{
  "version": "1.0.0",
  "ci_name": "ergon-ci",
  "last_updated": "2025-08-29T14:00:00Z",
  "memories": [
    {
      "id": "mem_1234567890_abc123",
      "timestamp": "2025-08-29T13:45:00Z",
      "ci_source": "ergon-ci",
      "type": "decision",
      "summary": "Chose Redux for state management",
      "content": "After evaluating options...",
      "tokens": 245,
      "relevance_tags": ["redux", "state", "architecture"],
      "priority": 7,
      "expires": "2025-09-05T13:45:00Z",
      "references": []
    }
  ],
  "statistics": {
    "total_memories": 42,
    "total_tokens": 15234,
    "oldest_memory": "2025-08-22T10:00:00Z",
    "last_cleanup": "2025-08-29T00:00:00Z"
  }
}
```

## API Endpoints

### REST API
```
GET  /api/memory/catalog
  Query params: ci, type, tags, search, limit, offset
  
GET  /api/memory/catalog/{memory_id}
  Returns specific memory item
  
POST /api/memory/catalog
  Body: MemoryItem
  Creates new memory
  
DELETE /api/memory/catalog/{memory_id}
  Removes memory item
  
GET  /api/memory/relevant
  Query params: ci, message, max_tokens
  Returns AI-selected relevant memories
  
POST /api/memory/cleanup
  Triggers expiration and cleanup
```

## Configuration

### Memory System Configuration
```python
MEMORY_CONFIG = {
    "max_injection_tokens": 2000,
    "max_memories_per_ci": 1000,
    "default_expiration_days": 7,
    "cleanup_interval_hours": 24,
    "min_priority_for_permanent": 8,
    "summary_max_length": 50,
    "extraction_patterns": {
        "decision": r"(decided|chose|selected|will use)",
        "insight": r"(learned|discovered|realized|found that)",
        "error": r"(error|failed|exception|bug)",
        "plan": r"(will|plan to|next step|todo)"
    }
}
```

## Migration Strategy

### Phase 1: Parallel Systems
- New memory catalog runs alongside EngramMemoryManager
- Feature flag to switch between systems
- Compare outputs for validation

### Phase 2: Gradual Migration
- Migrate one CI at a time
- Monitor token usage and relevance
- Gather feedback on memory quality

### Phase 3: Deprecation
- Disable EngramMemoryManager
- Archive old memory format
- Full cutover to catalog system

## Performance Considerations

### Caching
- Cache frequently accessed memories in Redis
- Cache relevance scores for 5 minutes
- Pre-compute token counts

### Async Processing
- Memory extraction happens async after response
- Batch cleanup operations
- Background indexing for search

### Scalability
- Shard by CI name for large deployments
- Consider PostgreSQL for >10K memories
- Implement memory compression for old items

## Security Considerations

### Access Control
- Memories are per-CI isolated
- Global memories require special permission
- No cross-CI memory access by default

### Sensitive Data
- Pattern matching to detect secrets
- Automatic redaction of API keys
- PII detection and masking

### Audit Trail
- Log all memory access
- Track memory modifications
- Monitor injection patterns

## Success Metrics

### Quantitative
- Token usage stays under limit 100% of time
- Memory relevance score >0.7 average
- Search response time <100ms
- Memory extraction time <500ms

### Qualitative
- CIs have appropriate context
- No more "prompt too long" errors
- Reduced hallucination from lack of context
- Improved task continuity across sessions