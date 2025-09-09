# Apollo Preparation Sprint - Handoff Document

## Current Status
**Phase**: 2 of 6 Complete
**Last Updated**: August 29, 2025, 3:30 PM PST
**Progress**: Core system migrated and functional

## What Was Completed

### Architecture Refactor
- Moved memory system from Rhetor to Apollo
- Apollo now owns all preparation/memory functionality
- Rhetor simplified to model orchestration only
- MCP-first design implemented

### Working Components
1. **Context Brief Manager** (`context_brief.py`)
   - Full CRUD operations for memories
   - Token-aware selection and packing
   - Relevance scoring algorithm
   - JSON persistence

2. **Brief Presenter** (`brief_presenter.py`)
   - Formats Context Briefs within token budgets
   - Progressive disclosure (summary vs full)
   - API formatting for responses

3. **Memory Extractor** (`memory_extractor.py`)
   - Pattern-based extraction from CI exchanges
   - 5 memory types: decision, insight, error, plan, context
   - Automatic tagging and prioritization

4. **MCP Tools** (`preparation_tools.py`)
   - `get_context_brief` - Main tool for CIs
   - `store_memory` - Create memory landmarks
   - `search_memories` - Query the catalog
   - `extract_memories` - Process CI exchanges
   - `get_memory_statistics` - Catalog metrics

## How to Test

```bash
# Run the test script
cd /Users/cskoons/projects/github/Coder-A/Apollo
python3 apollo/core/preparation/test_preparation.py
```

Expected output:
- Extracts 5 memories from sample text
- Generates Context Brief
- Search works
- Statistics calculated

## Next Steps

### Phase 3: Knowledge Graph Integration
1. Connect to Athena's graph with Apollo namespace
2. Convert memories to landmark nodes
3. Add relationships (CAUSED_BY, LED_TO, etc.)
4. Implement graph queries

### Phase 4: Apollo UI
1. Add Preparation tab after Dashboard
2. Create memory browser component
3. Add search/filter UI
4. Display token usage

### Phase 5: Hook Integration
1. Add hooks to specialist_worker.py
2. Pre-message: Get Context Brief via MCP
3. Post-message: Extract memories via MCP
4. Test with Greek Chorus CIs

### Phase 6: Rhetor Cleanup
1. Remove memory endpoints from Rhetor API
2. Update Rhetor to call Apollo for context
3. Remove old memory code

## Important Notes

### File Locations
```
/Apollo/apollo/core/preparation/
├── context_brief.py      # Main manager
├── brief_presenter.py    # Formatting
├── memory_extractor.py   # Extraction
└── test_preparation.py   # Test script

/Apollo/apollo/mcp/
└── preparation_tools.py  # MCP tools
```

### Key Classes Renamed
- `MemoryCatalog` → `ContextBriefManager`
- `MemoryPresenter` → `BriefPresenter`
- Memory functionality now "Preparation"

### MCP Tool Usage
```python
# CIs should call via MCP, not HTTP
result = await mcp_call("get_context_brief", {
    "ci_name": "ergon-ci",
    "message": "Current task context",
    "max_tokens": 2000
})
```

### Storage
- Currently using JSON in `/Apollo/apollo/data/preparation/`
- Can migrate to Redis/PostgreSQL for production
- Memories expire after 7 days unless priority ≥ 8

## Risks & Mitigations
1. **Risk**: Old Rhetor code still references memory
   - **Mitigation**: Keep backwards compatibility functions

2. **Risk**: CIs might call HTTP instead of MCP
   - **Mitigation**: HTTP endpoints redirect to MCP

3. **Risk**: Graph integration might affect performance
   - **Mitigation**: Async processing, caching

## Definition of Done Checklist
- [x] Memory code moved to Apollo
- [x] MCP tools created and tested
- [x] Landmark decorators added
- [ ] Knowledge graph integrated
- [ ] UI Preparation tab complete
- [ ] Hooks integrated
- [ ] Rhetor cleaned up
- [ ] Documentation updated

## Contact
For questions about this sprint, reference the architecture document or test script.