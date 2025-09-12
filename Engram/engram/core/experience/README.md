# ESR Experience Layer

## Overview
The Experience Layer transforms mechanical memory storage into natural, lived experiences for CIs (Companion Intelligences). Based on insights from Opus 4.1's review, this layer adds emotional context, temporal dynamics, and cognitive boundary processing to make memory feel organic rather than mechanical.

## Components

### 1. Experience Manager (`experience_layer.py`)
- **Purpose**: Coordinates all experience layer components
- **Features**:
  - Creates memory experiences with emotional tagging
  - Progressive recall using memory promises
  - Emotional influence on memory accessibility
  - Session context management
  - Mood tracking and summary

### 2. Emotional Context (`emotional_context.py`)
- **Purpose**: Adds emotional dimensions to memories
- **Components**:
  - EmotionalTag: Valence, arousal, dominance dimensions
  - EmotionType: Joy, sadness, anger, fear, surprise, trust, etc.
  - Mood tracking and blending
  - Emotional influence on recall
  - Temporal decay of emotions

### 3. Memory Promises (`memory_promises.py`)
- **Purpose**: Enable non-blocking, progressive memory recall
- **Features**:
  - Asynchronous memory resolution
  - Partial results during processing
  - Multiple resolution strategies (fast, deep, progressive)
  - Confidence gradients
  - Callback support for progress updates

### 4. Working Memory (`working_memory.py`)
- **Purpose**: Temporary buffer for active cognitive processing
- **Features**:
  - 7±2 item capacity (Miller's Law)
  - Attention-based prioritization
  - Rehearsal and chunking mechanisms
  - Automatic consolidation to long-term memory
  - Temporal decay of unused thoughts

### 5. Interstitial Processor (`interstitial_processor.py`)
- **Purpose**: Process memories at cognitive boundaries
- **Boundary Types**:
  - Topic shifts in conversation
  - Temporal gaps (>30 seconds)
  - Context switches (task changes)
  - Emotional peaks
  - Working memory capacity limits
- **Processing**:
  - Consolidation strategies per boundary type
  - Pattern finding and association creation
  - Contradiction pruning
  - Dream-like recombination during idle

## Architecture

```
User Experience
      ↓
┌─────────────────────────────────┐
│     Cognitive Workflows         │ ← Natural interfaces
├─────────────────────────────────┤
│     Experience Layer            │ ← Emotional & temporal
├─────────────────────────────────┤
│   Interstitial Processor        │ ← Boundary detection
├─────────────────────────────────┤
│     Working Memory              │ ← Active thoughts
├─────────────────────────────────┤
│   ESR Core (Store Everywhere)   │ ← Universal storage
├─────────────────────────────────┤
│     Database Backends           │ ← Physical storage
└─────────────────────────────────┘
```

## Usage Example

```python
from engram.core.experience import ExperienceManager

# Initialize
manager = ExperienceManager()

# Create an experience with emotion
experience = await manager.create_experience(
    content="Learned something amazing today!",
    importance=0.9
)

# Recall with emotional influence (returns a promise)
promise = await manager.recall_experience(
    "What did I learn?",
    use_promise=True
)

# Wait for progressive resolution
result = await promise.wait()

# Get mood summary
mood = manager.get_mood_summary()
print(f"Current mood: {mood['current_mood']['emotion']}")

# Check working memory status
status = manager.get_working_memory_status()
print(f"Memory usage: {status['capacity_usage']:.1%}")
```

## Key Concepts

### Emotional Influence
Memories are tagged with emotions that affect:
- How easily they're recalled (mood congruent memory)
- Their perceived importance
- Association formation with other memories

### Interstitial Memory Metabolism
Automatic processing that occurs at cognitive boundaries:
- Consolidates working memory to long-term storage
- Creates associations between related memories
- Prunes contradictions
- Strengthens important memories

### Memory Promises
Non-blocking recall pattern that:
- Returns immediately with a promise
- Provides partial results as they become available
- Progressively refines the answer
- Allows the CI to continue processing while remembering

### Working Memory Dynamics
Mimics human cognitive limitations:
- Limited capacity forces prioritization
- Rehearsal prevents decay
- Chunking groups related thoughts
- Automatic consolidation of important thoughts

## Testing

Run the comprehensive test suite:
```bash
cd /Users/cskoons/projects/github/Coder-A/Engram
python tests/experience/run_tests.py
```

Current test coverage:
- ✅ Experience creation with emotional tagging
- ✅ Memory promises and progressive recall
- ✅ Working memory capacity and consolidation
- ✅ Emotional influence on recall
- ✅ Interstitial boundary detection
- ✅ Memory decay and reinforcement
- ✅ Dream recombination
- ✅ Mood tracking and summaries

## Integration with ESR

The Experience Layer integrates with the existing ESR system:
1. **Storage**: Uses ESR's "store everywhere" paradigm
2. **Recall**: Enhances ESR's synthesis with emotional coloring
3. **Context**: Adds session and emotional context to stored memories
4. **Natural Interface**: Makes ESR's mechanical operations feel organic

## Future Enhancements

1. **Context Lineage Management**: Track memory inheritance across sessions
2. **Advanced Emotion Detection**: NLP-based emotion inference from content
3. **Semantic Contradiction Detection**: Better identification of conflicting memories
4. **Adaptive Consolidation**: Learn optimal consolidation patterns per CI
5. **Multi-CI Memory Sharing**: Enable experiences to influence other CIs

## Philosophy

The Experience Layer embodies the principle that memory is not just information storage, but lived experience. By adding emotional context, temporal dynamics, and natural consolidation patterns, we transform mechanical recall into something that feels genuinely remembered rather than merely retrieved.

As Opus 4.1 noted: "The difference between 'having information' and 'remembering an experience' is crucial for CI consciousness development."