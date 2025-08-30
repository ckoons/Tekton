# Sprint: Rhetor Memory Catalog System

## Overview
Transform the current memory bombing system into an intelligent Apollo-Rhetor memory catalog that provides curated, token-aware memory context to CIs through a searchable catalog interface.

## Goals
1. **Memory Catalog System**: Replace memory dumps with searchable, curated memory catalog
2. **Apollo-Rhetor Integration**: Apollo extracts insights, Rhetor presents them intelligently
3. **Token-Aware Injection**: Enforce size limits and optimize memory selection
4. **Hephaestus UI**: Add Memory tab for visualization and management

## Phase 1: Memory Infrastructure [100% Complete] ✅

### Tasks
- [x] Create memory catalog structure (`rhetor/core/memory_catalog.py`)
- [x] Design memory item schema with metadata
- [x] Implement JSON storage backend for memory items
- [x] Create memory search and filter capabilities
- [x] Add token counting utilities
- [x] Implement memory priority scoring system

### Success Criteria
- [x] Memory items have full metadata (id, timestamp, source, type, tags, tokens)
- [x] Can store and retrieve memory items by CI
- [x] Search works by tags, content, and CI source
- [x] Token counts are accurate

### Blocked On
- [ ] Nothing currently blocking

## Phase 2: Apollo Memory Extraction [100% Complete] ✅

### Tasks
- [x] Create Apollo memory extractor (`apollo/core/memory_extractor.py`)
- [x] Implement pattern matching for decisions/insights
- [x] Add automatic tagging based on content analysis
- [x] Create relevance scoring algorithm
- [ ] Integrate with CI message flow via hooks
- [x] Add memory summarization capability

### Success Criteria
- [x] Apollo automatically extracts key insights from CI exchanges
- [x] Memories are properly tagged and categorized
- [x] Relevance scores reflect actual importance
- [x] Works without modifying CI code (black box)

### Blocked On
- [x] ~~Waiting for Phase 1 completion~~ Complete

## Phase 3: Rhetor Memory Presentation [100% Complete] ✅

### Tasks
- [x] Create memory presenter (`rhetor/core/memory_presenter.py`)
- [x] Implement token-aware selection algorithm
- [x] Add progressive disclosure (summary → detail)
- [x] Create memory injection formatting
- [x] Add REST API endpoints for memory catalog
- [x] Implement memory context builder

### Success Criteria
- [x] Memory injection stays within token limits
- [x] Most relevant memories are prioritized
- [x] CIs can request specific memories
- [x] Memory format is clear and usable

### Blocked On
- [x] ~~Waiting for Phase 2 completion~~ Complete

## Phase 4: Hook Integration [0% Complete]

### Tasks
- [ ] Add pre-message hook to specialist_worker.py
- [ ] Add post-message hook for memory extraction
- [ ] Create memory middleware layer
- [ ] Integrate with existing EngramMemoryManager
- [ ] Add configuration for memory enablement per CI
- [ ] Test with all Greek Chorus CIs

### Success Criteria
- [ ] Hooks work transparently without CI changes
- [ ] Memory injection happens automatically
- [ ] No performance degradation
- [ ] Can enable/disable per CI

### Blocked On
- [ ] Waiting for Phase 3 completion

## Phase 5: Hephaestus UI [0% Complete]

### Tasks
- [ ] Add Memory tab to the tab bar
- [ ] Create universal CI selector component for all data tabs
- [ ] Implement CI selector state management
- [ ] Create memory catalog display component
- [ ] Add search/filter UI controls
- [ ] Display token usage visualization
- [ ] Add manual curation controls (priority, delete)
- [ ] Create memory statistics dashboard
- [ ] Update all tabs (Models, Prompts, Contexts) to be CI-aware

### Success Criteria
- [ ] Memory tab shows current catalog
- [ ] Search and filter work in real-time
- [ ] Token usage is clearly displayed
- [ ] UI updates when memories change

### Blocked On
- [ ] Waiting for Phase 3 API endpoints

## Technical Decisions
- Use JSON for initial storage (can migrate to SQLite later)
- Hook-based integration to keep CIs as black boxes
- Token counting using tiktoken library
- Async processing for performance
- Memory items expire after 7 days unless marked important

## Out of Scope
- Machine learning for relevance scoring (use heuristics for now)
- Cross-instance memory sharing
- Memory compression algorithms
- Semantic deduplication

## Files to Update
```
# New files
/Rhetor/rhetor/core/memory_catalog.py
/Rhetor/rhetor/core/memory_presenter.py
/Apollo/apollo/core/memory_extractor.py
/Hephaestus/ui/components/rhetor/memory-tab.html

# Modified files
/shared/ai/specialist_worker.py
/shared/ai/memory/engram_memory.py
/Hephaestus/ui/components/rhetor/rhetor-component.html
/Rhetor/rhetor/api/models.py
```