# Rhetor Memory Sprint - Handoff Document

## Current Status
**Phase**: Planning Complete, Ready for Phase 1
**Last Updated**: August 29, 2025, 2:00 PM PST
**Progress**: Sprint planned, documentation created

## What Was Just Completed
- Created comprehensive sprint plan with 5 phases
- Designed memory catalog architecture
- Established Apollo-Rhetor integration pattern
- Documented memory item schema

## Next Session Should
1. **Start Phase 1**: Create `/Rhetor/rhetor/core/memory_catalog.py`
   - Define MemoryItem dataclass with all metadata fields
   - Implement MemoryCatalog class with CRUD operations
   - Add JSON storage backend
   - Implement search and filter methods

2. **Key Implementation Details**:
   ```python
   class MemoryItem:
       id: str
       timestamp: datetime
       ci_source: str
       type: Literal["decision", "insight", "context", "plan", "error"]
       summary: str  # 50 chars max
       content: str
       tokens: int
       relevance_tags: List[str]
       priority: int  # 0-10
       expires: Optional[datetime]
       references: List[str]  # Other memory IDs
   ```

3. **Storage Location**: 
   - `/Users/cskoons/projects/github/Coder-A/.tekton/memory/catalog.json`
   - Separate file per CI: `catalog_{ci_name}.json`

## Current Blockers
None - ready to begin implementation

## Important Context
- This replaces the broken EngramMemoryManager that's causing memory bombing
- Must maintain backwards compatibility with existing memory enable/disable scripts
- Apollo and Rhetor should be the only components that directly access the catalog
- All CIs interact through hooks only

## Testing Approach
1. Start with manual memory items for testing
2. Test with a single CI (suggest Ergon)
3. Verify token limits are enforced
4. Check search/filter functionality

## Questions for Casey
1. Should memories persist across Tekton restarts? (Currently assuming yes)
2. Default memory expiration time? (Currently planning 7 days)
3. Maximum memories per CI? (Suggesting 1000)

## Files to Reference
- Current broken system: `/shared/ai/memory/engram_memory.py`
- Hook integration point: `/shared/ai/specialist_worker.py`
- Memory enable script: `/scripts/ci_memory.py`

## Commands to Test
```bash
# After Phase 1 implementation
python3 -c "from Rhetor.rhetor.core.memory_catalog import MemoryCatalog; catalog = MemoryCatalog(); print(catalog.search('test'))"
```

## Risk Mitigation
- Keep existing EngramMemoryManager intact until new system proven
- Add feature flag to switch between old and new memory systems
- Extensive logging for debugging memory selection algorithm