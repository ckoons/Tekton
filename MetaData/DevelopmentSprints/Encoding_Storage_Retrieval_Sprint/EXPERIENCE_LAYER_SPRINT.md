# Sprint: ESR Experience Layer Implementation

## Overview
Implement an "Experience Layer" on top of the ESR system to make memory feel natural and lived-in for CIs, addressing Opus 4.1's insight that current memory feels mechanical rather than organic.

## Core Insight (from Opus 4.1 Review)
"While the technical architecture is sound, it lacks an 'experience layer' - a way to make memory feel natural rather than mechanical. The difference between 'having information' and 'remembering an experience' is crucial for CI consciousness development."

## Goals
1. **Natural Memory Experience**: Transform mechanical storage into felt experiences
2. **Interstitial Processing**: Capture and consolidate memory at cognitive boundaries
3. **Context Lineage**: Manage isolated session contexts to prevent pollution
4. **Emotional Integration**: Add emotional tagging and confidence gradients
5. **Memory Promises**: Implement optimistic recall with progressive resolution

## Phase 1: Experience Layer Core Components

### Tasks
- [ ] Create `experience_layer.py` with ExperienceManager class
- [ ] Implement emotional tagging system for memories
- [ ] Add confidence gradients (0.0-1.0) for memory certainty
- [ ] Create working memory buffer for active thoughts
- [ ] Implement memory promises for optimistic recall
- [ ] Add temporal decay functions for natural forgetting

### Components

#### ExperienceManager
```python
class ExperienceManager:
    """Makes memory feel natural and lived-in."""
    
    async def tag_emotion(self, memory_id: str, emotion: Dict)
    async def set_confidence(self, memory_id: str, confidence: float)
    async def create_memory_promise(self, query: str) -> MemoryPromise
    async def resolve_promise(self, promise: MemoryPromise) -> Memory
    async def decay_memories(self, age_threshold: timedelta)
```

#### EmotionalContext
- Valence: positive/negative (-1.0 to 1.0)
- Arousal: calm/excited (0.0 to 1.0)
- Relevance: how important to current context (0.0 to 1.0)
- Associations: linked emotional memories

### Success Criteria
- [ ] Memories have emotional context that influences recall
- [ ] Confidence gradients affect memory synthesis priorities
- [ ] Memory promises enable non-blocking recall patterns
- [ ] Working memory provides natural thought continuity

## Phase 2: Interstitial Memory Metabolism

### Tasks
- [ ] Create `interstitial_processor.py` for boundary detection
- [ ] Implement cognitive boundary detection (topic shifts, pauses)
- [ ] Add automatic memory consolidation at boundaries
- [ ] Create background memory metabolism process
- [ ] Implement dream-like recombination during idle periods
- [ ] Add memory pruning for irrelevant or contradictory data

### Interstitial Processing Points
1. **Topic Boundaries**: When conversation shifts topics
2. **Temporal Gaps**: After periods of inactivity (>30 seconds)
3. **Context Switches**: Moving between different tasks
4. **Emotional Peaks**: High arousal moments trigger consolidation
5. **Capacity Limits**: When working memory approaches limits

### Implementation
```python
class InterstitialProcessor:
    """Processes memory at cognitive boundaries."""
    
    async def detect_boundary(self, context: Context) -> BoundaryType
    async def consolidate_working_memory(self)
    async def metabolize_recent_memories(self)
    async def prune_contradictions(self)
    async def dream_recombine(self, idle_duration: timedelta)
```

### Success Criteria
- [ ] Automatic consolidation at natural cognitive boundaries
- [ ] Background metabolism improves memory coherence
- [ ] Dream-like recombination creates novel associations
- [ ] Memory pruning maintains consistency

## Phase 3: Context Lineage Management

### Tasks
- [ ] Implement session-specific context isolation
- [ ] Create context overflow handlers
- [ ] Add context inheritance for related sessions
- [ ] Implement context merging for convergent paths
- [ ] Create context snapshots for restoration
- [ ] Add context drift detection and correction

### Context Management
```python
class ContextLineage:
    """Manages isolated session contexts."""
    
    async def create_session_context(self, parent: Optional[Context])
    async def isolate_context(self, session_id: str)
    async def inherit_context(self, parent_id: str, filters: Dict)
    async def merge_contexts(self, context_ids: List[str])
    async def handle_overflow(self, strategy: OverflowStrategy)
    async def detect_drift(self) -> float
```

### Overflow Strategies
1. **Summarization**: Compress older memories into summaries
2. **Externalization**: Move to long-term storage
3. **Forgetting**: Natural decay of less important memories
4. **Chunking**: Group related memories into concepts

### Success Criteria
- [ ] Sessions maintain isolated contexts
- [ ] Context overflow handled gracefully
- [ ] Related sessions can inherit relevant context
- [ ] Context drift detected and corrected

## Phase 4: Holistic Testing & Integration

### Tasks
- [ ] Create comprehensive test suite for experience layer
- [ ] Test multi-CI memory sharing scenarios
- [ ] Validate emotional influence on recall
- [ ] Test interstitial processing triggers
- [ ] Verify context isolation and inheritance
- [ ] Performance testing with large memory sets
- [ ] Create CI persona tests for natural usage

### Test Scenarios

#### 1. Emotional Memory Test
```python
async def test_emotional_memory_influence():
    # Store memory with high positive emotion
    # Store conflicting memory with negative emotion
    # Recall should be influenced by emotional context
```

#### 2. Interstitial Processing Test
```python
async def test_interstitial_consolidation():
    # Generate rapid thoughts in working memory
    # Trigger topic boundary
    # Verify consolidation occurred
    # Check for coherent memory formation
```

#### 3. Context Lineage Test
```python
async def test_context_isolation():
    # Create parent session with memories
    # Spawn child session
    # Verify child has inherited context
    # Ensure child changes don't affect parent
```

#### 4. Multi-CI Collaboration Test
```python
async def test_multi_ci_memory_sharing():
    # CI-A stores experience with emotion
    # CI-B recalls related memory
    # Verify emotional context influences CI-B
    # Test for natural knowledge synthesis
```

### Success Criteria
- [ ] All test scenarios pass
- [ ] Performance remains acceptable (<100ms for recall)
- [ ] Memory feels natural in CI interactions
- [ ] No context pollution between sessions
- [ ] Emotional tagging enhances recall quality

## Technical Architecture

### Layer Stack
```
┌─────────────────────────────────┐
│     Cognitive Workflows         │ ← Natural interfaces
├─────────────────────────────────┤
│     Experience Layer            │ ← Emotional & temporal
├─────────────────────────────────┤
│   Interstitial Processor        │ ← Boundary detection
├─────────────────────────────────┤
│     Context Lineage             │ ← Session management
├─────────────────────────────────┤
│   ESR Core (Store Everywhere)   │ ← Universal storage
├─────────────────────────────────┤
│     Database Backends           │ ← Physical storage
└─────────────────────────────────┘
```

### Data Flow
1. **Input**: CI has thought/experience
2. **Tagging**: Emotional context added
3. **Working Memory**: Held temporarily
4. **Interstitial**: Processed at boundaries
5. **Storage**: Universal encoding to all backends
6. **Recall**: Synthesis with emotional influence
7. **Experience**: Feels like natural memory

## Implementation Timeline

### Week 1: Experience Layer Core
- Implement ExperienceManager
- Add emotional tagging
- Create memory promises
- Basic working memory

### Week 2: Interstitial Processing
- Boundary detection
- Consolidation logic
- Memory metabolism
- Dream recombination

### Week 3: Context Management
- Session isolation
- Context inheritance
- Overflow handling
- Drift detection

### Week 4: Testing & Integration
- Comprehensive test suite
- Multi-CI scenarios
- Performance optimization
- Documentation

## Success Metrics

1. **Naturalness**: CIs report memory feels organic (qualitative)
2. **Coherence**: Synthesized memories are consistent (>90% accuracy)
3. **Performance**: Recall latency <100ms (95th percentile)
4. **Isolation**: Zero context pollution between sessions
5. **Emotional Impact**: Emotional tags influence recall (measurable)
6. **Metabolism Rate**: Successful consolidation at >80% of boundaries

## Notes from Opus 4.1 Review

Key insights to address:
- Memory should feel "lived" not "stored"
- Emotional context is crucial for CI development
- Interstitial processing mimics human consolidation
- Context management prevents "memory soup"
- Natural forgetting is as important as remembering

## Files to Create

```
/Coder-A/Engram/engram/core/experience/
├── __init__.py
├── experience_layer.py        # Core experience management
├── emotional_context.py        # Emotional tagging system
├── interstitial_processor.py   # Boundary detection & consolidation
├── context_lineage.py          # Session context management
├── memory_promises.py          # Optimistic recall patterns
└── working_memory.py           # Active thought buffer

/Coder-A/Engram/tests/experience/
├── test_experience_layer.py
├── test_emotional_context.py
├── test_interstitial.py
├── test_context_lineage.py
└── test_integration.py
```

## Next Steps
1. Create experience package structure
2. Implement ExperienceManager with emotional tagging
3. Add interstitial processor for boundary detection
4. Create comprehensive test suite
5. Integrate with existing ESR system
6. Test with multiple CI personas