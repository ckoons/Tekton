# Memory System Migration Notice

## Memory System Moved to Apollo

As of the latest update, all memory and Context Brief functionality has been migrated from Rhetor to Apollo.

### What Changed

**Removed from Rhetor:**
- `/api/memory/*` endpoints
- `memory_catalog.py`
- `memory_presenter.py`
- `memory_endpoints.py`
- All memory middleware components

**Now Handled by Apollo:**
- Memory storage and retrieval
- Context Brief preparation
- Memory extraction from exchanges
- Landmark creation in knowledge graph
- Memory relationship analysis

### How Rhetor Gets Context

Rhetor now uses the `ApolloClient` to request Context Briefs via MCP:

```python
from rhetor.core.apollo_client import get_apollo_client

apollo = get_apollo_client()
context_brief = await apollo.get_context_brief(
    ci_name="ergon-ci",
    message="Current task context",
    max_tokens=500
)
```

### For API Users

If you were using Rhetor's memory endpoints, migrate to Apollo's MCP tools:

**Old (Rhetor):**
```
POST /api/memory/catalog
GET /api/memory/relevant
```

**New (Apollo MCP):**
```python
# Via MCP tools
await apollo.mcp.invoke("store_memory", {...})
await apollo.mcp.invoke("get_context_brief", {...})
```

Or use Apollo's REST API:
```
POST /apollo/api/preparation/memory
POST /apollo/api/preparation/brief
```

### Benefits of Migration

1. **Separation of Concerns**: Rhetor focuses on LLM orchestration, Apollo on preparation
2. **Better Architecture**: Apollo is the "library god" - natural fit for memory/context
3. **Knowledge Graph Integration**: Memories become landmarks in Athena's graph
4. **Token Management**: Apollo's existing CI registry handles token budgets
5. **MCP-First Design**: CIs communicate via MCP, not HTTP

### Configuration

Set the Apollo URL in your environment:
```bash
export APOLLO_URL=http://localhost:8200
```

### Backward Compatibility

The memory endpoints have been removed from Rhetor. If you need memory functionality, use Apollo directly.

### Support

For questions about the migration, see the Apollo Preparation Sprint documentation in:
`/MetaData/DevelopmentSprints/Apollo_Preparation_Sprint/`