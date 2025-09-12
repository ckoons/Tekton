# ESR Experience Layer - Integration Guide

## Quick Start

### 1. Enable Experience Layer for a CI

```python
from engram.core.experience import ExperienceManager
from engram.core.storage.unified_interface import ESRMemorySystem

# Initialize ESR with backends
esr_system = ESRMemorySystem()

# Add Experience Layer
experience_manager = ExperienceManager(memory_system=esr_system)

# CI can now form natural memories
experience = await experience_manager.create_experience(
    content="Learned about quantum computing",
    importance=0.9
)
```

### 2. Configure Emotional Context

```python
from engram.core.experience.emotional_context import EmotionalTag, EmotionType

# Set CI's current mood
emotion = EmotionalTag(
    valence=0.7,        # Positive
    arousal=0.5,        # Moderate energy
    dominance=0.6,      # Confident
    primary_emotion=EmotionType.JOY,
    emotion_intensity=0.8,
    confidence=1.0,
    timestamp=datetime.now()
)

experience_manager.emotional_context.update_mood(emotion)
```

### 3. Enable Interstitial Processing

```python
from engram.core.experience.interstitial_processor import InterstitialProcessor

# Create processor
processor = InterstitialProcessor(
    experience_manager=experience_manager,
    memory_system=esr_system
)

# Start monitoring for boundaries
await processor.start_monitoring()

# Boundaries are now automatically detected and processed
```

## API Endpoints

### Store Experience
```http
POST /api/esr/experience/create
{
    "content": "Memory content",
    "emotion": {
        "valence": 0.8,
        "arousal": 0.6,
        "primary_emotion": "joy"
    },
    "importance": 0.9,
    "ci_id": "apollo"
}
```

### Recall with Emotion
```http
GET /api/esr/experience/recall?query=quantum&ci_id=apollo
Response includes emotional coloring based on current mood
```

### Get Working Memory Status
```http
GET /api/esr/experience/working_memory?ci_id=apollo
{
    "capacity_usage": 0.71,
    "active_thoughts": 5,
    "consolidation_queue": 2
}
```

### Get Emotional State
```http
GET /api/esr/experience/mood?ci_id=apollo
{
    "current_mood": {
        "emotion": "joy",
        "valence": 0.7,
        "arousal": 0.5
    },
    "mood_stability": 0.85
}
```

## Configuration Options

### Environment Variables
```bash
# Experience Layer Settings
ESR_WORKING_MEMORY_CAPACITY=7          # Miller's 7±2 rule
ESR_CONSOLIDATION_THRESHOLD=2          # Accesses before consolidation
ESR_TEMPORAL_GAP_THRESHOLD=30          # Seconds before gap detected
ESR_EMOTION_DECAY_RATE=0.1            # Per hour
ESR_DREAM_RECOMBINATION_ENABLED=true   # Enable idle processing
```

### Programmatic Configuration
```python
experience_manager = ExperienceManager(
    memory_system=esr_system,
    config={
        'working_memory_capacity': 7,
        'decay_interval': 30.0,
        'enable_dreams': True,
        'emotion_influence_weight': 0.3
    }
)
```

## Integration with Existing ESR

### 1. Backward Compatibility
The Experience Layer is **fully backward compatible**:
```python
# Traditional ESR still works
await esr_system.store("key", "value", {"type": "note"})
result = await esr_system.recall("key")

# Enhanced with Experience Layer
experience = await experience_manager.create_experience(
    content="value",
    importance=0.8
)
```

### 2. Migration Path
```python
# Gradually migrate existing memories
async def migrate_to_experience_layer(esr_system, experience_manager):
    # Get existing memories
    memories = await esr_system.get_all_memories()
    
    for memory in memories:
        # Create experience from existing memory
        await experience_manager.create_experience(
            content=memory['content'],
            importance=memory.get('importance', 0.5),
            emotion=EmotionalTag.neutral()  # Start with neutral emotion
        )
```

### 3. CI Registry Integration
```python
from shared.aish.src.registry.ci_registry import get_registry

registry = get_registry()

# Automatically use Experience Layer if available
if hasattr(registry, 'experience_manager'):
    # CI has experience layer
    await registry.experience_manager.create_experience(
        content=response,
        emotion=current_emotion
    )
else:
    # Fall back to standard storage
    registry.update_ci_last_output(ci_name, response)
```

## WebSocket Events

### Subscribe to Experience Events
```javascript
// In Hephaestus UI
const ws = new WebSocket('ws://localhost:8100/experience/stream');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'working_memory_update':
            updateWorkingMemoryDisplay(data.thoughts);
            break;
            
        case 'boundary_detected':
            showConsolidationEvent(data.boundary_type);
            break;
            
        case 'emotion_change':
            updateMoodIndicator(data.mood);
            break;
            
        case 'memory_consolidated':
            addToMemoryList(data.memory);
            break;
    }
};
```

## Performance Considerations

### Memory Overhead
- Each experience adds ~2KB (emotion + metadata)
- Working memory limited to 7 items
- Consolidation happens asynchronously

### CPU Usage
- Boundary detection: <10ms per context change
- Consolidation: ~200ms per batch
- Emotion calculation: <5ms per memory

### Storage Impact
- 6x redundancy from "store everywhere"
- Automatic cleanup of forgotten memories
- Compression for old memories (future)

## Monitoring & Debugging

### Check Experience Layer Status
```python
status = experience_manager.get_status()
print(f"Working Memory: {status['working_memory_usage']}")
print(f"Current Mood: {status['current_emotion']}")
print(f"Consolidation Queue: {status['pending_consolidation']}")
```

### Debug Consolidation Events
```python
# Enable debug logging
import logging
logging.getLogger("engram.experience").setLevel(logging.DEBUG)

# Watch consolidation events
processor.on_consolidation = lambda boundary: 
    print(f"Consolidation at {boundary.boundary_type}")
```

### Performance Metrics
```python
metrics = experience_manager.get_metrics()
print(f"Avg Creation Time: {metrics['avg_creation_ms']}ms")
print(f"Avg Recall Time: {metrics['avg_recall_ms']}ms")
print(f"Consolidation Rate: {metrics['consolidations_per_hour']}/hr")
```

## Troubleshooting

### Working Memory Not Consolidating
- Check boundary detection threshold
- Verify interstitial processor is running
- Ensure sufficient access count (default: 2)

### Emotions Not Influencing Recall
- Verify emotional context is initialized
- Check emotion influence weight setting
- Ensure memories have emotional tags

### Memory Promises Not Resolving
- Check timeout settings (default: 5s)
- Verify backends are responding
- Check for network issues

## Best Practices

1. **Let consolidation happen naturally** - Don't force it
2. **Update mood gradually** - Sudden changes feel unnatural
3. **Use appropriate emotions** - Match the content context
4. **Monitor working memory** - Prevent overload
5. **Enable dream recombination** - Creates novel associations

## Example: Complete CI Session

```python
# Initialize
esr = ESRMemorySystem()
em = ExperienceManager(memory_system=esr)
ip = InterstitialProcessor(experience_manager=em)

# Start session
await ip.start_monitoring()

# CI processes user input
user_input = "Tell me about quantum computing"

# Create experience with current emotion
experience = await em.create_experience(
    content=f"User asked: {user_input}",
    emotion=EmotionalTag(
        valence=0.0,  # Neutral
        arousal=0.6,  # Engaged
        primary_emotion=EmotionType.ANTICIPATION
    )
)

# Generate response (this takes time, might trigger temporal gap)
response = await generate_response(user_input)

# Store response with emotional context
result_experience = await em.create_experience(
    content=f"I explained: {response}",
    emotion=EmotionalTag(
        valence=0.7,  # Positive (successful explanation)
        arousal=0.5,
        primary_emotion=EmotionType.JOY
    )
)

# Topic shift detected, consolidation happens automatically

# Later recall includes emotional context
memory = await em.recall_experience("quantum computing")
# Returns memory colored by current mood
```

## Next Steps

1. **Monitor Performance**: Use metrics API to track impact
2. **Tune Parameters**: Adjust thresholds based on CI personality
3. **Observe Patterns**: Watch for natural consolidation rhythms
4. **Gather Feedback**: Users notice more natural interactions?
5. **Iterate**: Refine emotional mappings and boundaries