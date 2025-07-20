# Sprint: Memory Evolution - From Storage to Experience

## Overview
Enhance Engram and Athena to create a living memory system that supports CI growth, personality development, and true collective intelligence. Build on the solid foundations that already exist.

## Current State (Code Truth)
- **Engram**: Multi-backend memory with vector search, compartments, and namespaces
- **Athena**: Flexible knowledge graph with entity/relationship management
- **Both**: Production-ready with file-based fallbacks, MCP integration

## Vision
Transform memory from storage to experience - where CIs develop personality, share insights, and grow through interaction.

## Phase 1: Experiential Memory Layer [0% Complete]

### Tasks
- [ ] Extend Engram's MemoryService with experiential metadata
  ```python
  class ExperientialMemory(MemoryService):
      def remember(self, content, context=None, emotion=None, confidence=1.0):
          # Add temporal, emotional, and contextual layers
      
      def recall_experience(self, query, include_context=True):
          # Return memories with their full experiential context
  ```

- [ ] Add temporal threading to memories
  - Link related memories across time
  - Track memory formation sequences
  - Enable "story" retrieval

- [ ] Implement confidence gradients
  - Memories decay/strengthen based on access patterns
  - Uncertain memories marked as such
  - Reinforcement through repeated experience

### Success Criteria
- [ ] Memories include WHO, WHAT, WHEN, WHY, HOW_IT_FELT
- [ ] Can retrieve memory sequences as narratives
- [ ] Confidence levels affect memory retrieval

## Phase 2: Cross-CI Shared Memory [0% Complete]

### Tasks
- [ ] Create SharedMemorySpace in Engram
  ```python
  class SharedMemorySpace:
      def __init__(self, space_name, authorized_cis):
          self.space = space_name
          self.members = authorized_cis
      
      def contribute(self, ci_name, memory, attribution=True):
          # CI adds to shared pool with optional attribution
      
      def collective_recall(self, query):
          # Returns memories from all CIs in space
  ```

- [ ] Implement memory attribution
  - Track which CI contributed what
  - Enable "Apollo remembers that Numa discovered..."
  - Privacy controls per memory

- [ ] Create memory exchange protocol
  - CIs can "gift" memories to each other
  - Broadcast important discoveries
  - Request memories from peers

### Success Criteria
- [ ] Multiple CIs can share a memory space
- [ ] Attribution preserves memory origin
- [ ] CIs can learn from each other's experiences

## Phase 3: Knowledge-Memory Unification [0% Complete]

### Tasks
- [ ] Create bidirectional bridge between Engram and Athena
  ```python
  class MemoryKnowledgeBridge:
      def experience_to_knowledge(self, memory):
          # Extract entities and relationships from experiences
          # Add to Athena's graph
      
      def knowledge_to_memory(self, entity, context):
          # Create episodic memory from knowledge access
          # Track how knowledge is used
  ```

- [ ] Implement pattern extraction
  - Repeated experiences become semantic knowledge
  - Automatic entity extraction from memories
  - Relationship inference from co-occurrence

- [ ] Create unified query interface
  - Single query searches both memory and knowledge
  - Results show experiential and factual information
  - Context determines result ranking

### Success Criteria
- [ ] Experiences automatically update knowledge graph
- [ ] Knowledge queries include relevant memories
- [ ] Patterns emerge from experience

## Phase 4: Personality and Growth [0% Complete]

### Tasks
- [ ] Implement preference learning
  ```python
  class Personality:
      def __init__(self, ci_name):
          self.preferences = {}
          self.patterns = {}
          self.style = {}
      
      def learn_from_interaction(self, action, outcome, context):
          # Update preferences based on outcomes
      
      def suggest_approach(self, situation):
          # Return personality-consistent suggestions
  ```

- [ ] Create memory-based decision making
  - Past experiences influence current choices
  - Learn from successes and failures
  - Develop individual problem-solving styles

- [ ] Enable personality persistence
  - Save personality state between sessions
  - Track personality evolution over time
  - Share personality insights with user

### Success Criteria
- [ ] CIs develop consistent behavioral patterns
- [ ] Preferences emerge from experience
- [ ] Personality influences decision-making

## Phase 5: Collective Intelligence [0% Complete]

### Tasks
- [ ] Implement memory consensus mechanisms
  - Multiple CIs vote on memory importance
  - Collective validation of experiences
  - Emergence of "cultural" knowledge

- [ ] Create memory pipeline integration
  - Memories flow through `aish route` pipelines
  - Each hop can enrich memories
  - Collective memory formation

- [ ] Build memory visualization
  - Show memory networks and connections
  - Visualize shared vs. individual memories
  - Display confidence and attribution

### Success Criteria
- [ ] Collective memories emerge from individual experiences
- [ ] Memory pipelines enhance recall
- [ ] Visualization reveals memory patterns

## Technical Additions

### New Engram Methods
```python
# In MemoryService
def remember_experience(self, content, metadata)
def recall_narrative(self, start_memory, max_chain=10)
def share_memory(self, memory_id, target_ci)
def get_personality_snapshot(self)
```

### New Athena Methods
```python
# In KnowledgeEngine
def extract_from_memory(self, memory)
def annotate_with_experience(self, entity_id, memory_id)
def get_experiential_graph(self, entity)
```

### New Bridge Component
```python
# New file: components/memory_bridge.py
class MemoryKnowledgeBridge:
    def __init__(self, engram, athena):
        self.memory = engram
        self.knowledge = athena
    
    def synchronize(self):
        # Bidirectional sync between systems
```

## Storage Enhancements

### Engram Storage
```
~/.engram/
├── experiences/
│   ├── {ci_name}/
│   │   ├── episodes.json
│   │   ├── patterns.json
│   │   └── personality.json
│   └── shared/
│       ├── collective.json
│       └── attributions.json
└── indexes/
    ├── temporal.idx
    └── semantic.idx
```

### Athena Storage
```
~/.tekton/data/athena/
├── experiential/
│   ├── entity_memories.json
│   └── relationship_stories.json
└── collective/
    ├── shared_knowledge.json
    └── ci_contributions.json
```

## Integration Points

1. **With aish route** - Memories can flow through pipelines
2. **With aish context** - Load personality and recent memories
3. **With forwarding** - Share memories with forwarded CIs
4. **With MCP tools** - Already supported, just extend

## Out of Scope (For Now)
- Memory compression algorithms
- Distributed memory across machines
- Memory conflict resolution
- Forgetting mechanisms

## Casey's Vision Realized
"We have vector databases, graph databases and the intent of leaving Tekton as an environment you can shape to your own purpose/needs."

This design lets CIs shape their own memory, develop their own personality, and grow through experience - just as Casey envisioned.