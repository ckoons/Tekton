"""Debug failing tests in detail."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
import logging
logging.basicConfig(level=logging.WARNING)

from engram.core.experience.experience_layer import ExperienceManager, MemoryExperience
from engram.core.experience.emotional_context import EmotionalTag, EmotionType
from engram.core.experience.memory_promises import MemoryPromise, PromiseState
from engram.core.experience.working_memory import WorkingMemory, ThoughtState
from engram.core.experience.interstitial_processor import InterstitialProcessor, BoundaryType
from datetime import datetime, timedelta

async def debug_working_memory():
    """Debug working memory test."""
    print("\n=== DEBUGGING WORKING MEMORY ===")
    memory = WorkingMemory(capacity=5)
    
    # Add thoughts up to capacity
    thought_ids = []
    for i in range(5):
        thought_id = await memory.add_thought(f"Thought {i}")
        thought_ids.append(thought_id)
        print(f"Added thought {i}: {thought_id}")
    
    print(f"Total thoughts: {len(memory.thoughts)}")
    print(f"Is overloaded: {memory.is_overloaded()}")
    
    # Access a thought multiple times
    target_id = thought_ids[0]
    print(f"\nAccessing thought {target_id} multiple times...")
    
    for i in range(5):
        result = await memory.access_thought(target_id)
        thought = memory.thoughts[target_id]
        print(f"Access {i+1}: count={thought.access_count}, state={thought.state.value}")
    
    thought = memory.thoughts[target_id]
    print(f"\nFinal state: {thought.state.value}")
    print(f"Expected: {ThoughtState.REHEARSING.value}")
    print(f"Match: {thought.state == ThoughtState.REHEARSING}")
    
    return thought.state == ThoughtState.REHEARSING

async def debug_emotional_influence():
    """Debug emotional influence test."""
    print("\n=== DEBUGGING EMOTIONAL INFLUENCE ===")
    manager = ExperienceManager()
    
    # Create memories with different emotions
    happy_memory = await manager.create_experience(
        "I won the lottery! So happy!",
        emotion=EmotionalTag(
            valence=0.9,
            arousal=0.8,
            dominance=0.7,
            primary_emotion=EmotionType.JOY,
            emotion_intensity=0.9,
            confidence=1.0,
            timestamp=datetime.now()
        )
    )
    print(f"Created happy memory: {happy_memory.memory_id}")
    
    # Set current mood to happy
    manager.emotional_context.update_mood(EmotionalTag(
        valence=0.8,
        arousal=0.6,
        dominance=0.5,
        primary_emotion=EmotionType.JOY,
        emotion_intensity=0.7,
        confidence=1.0,
        timestamp=datetime.now()
    ))
    print(f"Set mood to: {manager.emotional_context.current_mood.primary_emotion.value}")
    
    # Try to recall
    result = await manager._direct_recall("lottery")
    print(f"Recall result: {result}")
    
    if result:
        print(f"Has colored_by_mood: {'colored_by_mood' in result}")
        if 'colored_by_mood' in result:
            print(f"Mood color: {result['colored_by_mood']}")
        return True
    else:
        print("No result from recall")
        return False

async def debug_interstitial():
    """Debug interstitial processing test."""
    print("\n=== DEBUGGING INTERSTITIAL PROCESSING ===")
    manager = ExperienceManager()
    processor = InterstitialProcessor(experience_manager=manager)
    
    # Create initial context
    context1 = {"topic": "weather", "activity": "discussion"}
    boundary = await processor.detect_boundary(context1)
    print(f"First context: {boundary}")
    
    # Topic shift
    context2 = {"topic": "politics", "activity": "discussion"}
    boundary = await processor.detect_boundary(context2)
    print(f"Topic shift detected: {boundary}")
    
    # Force temporal gap
    processor.last_activity = datetime.now() - timedelta(seconds=35)
    context3 = {"topic": "politics", "activity": "discussion"}
    boundary = await processor.detect_boundary(context3)
    print(f"Temporal gap detected: {boundary}")
    
    # Context switch
    context4 = {"task": "coding", "mode": "focused"}
    boundary = await processor.detect_boundary(context4)
    print(f"Context switch detected: {boundary}")
    
    print(f"Pending boundaries: {len(processor.pending_boundaries)}")
    
    # Test consolidation
    if processor.pending_boundaries:
        boundary_to_process = processor.pending_boundaries[0]
        print(f"Processing boundary: {boundary_to_process.boundary_type.value}")
        await processor.consolidate_at_boundary(boundary_to_process)
        print(f"Processed boundaries: {len(processor.processed_boundaries)}")
        return True
    else:
        print("No boundaries to process")
        return False

async def debug_experience_recall():
    """Debug experience recall with emotion."""
    print("\n=== DEBUGGING EXPERIENCE RECALL ===")
    manager = ExperienceManager()
    
    # Create multiple experiences
    experiences = []
    for i, emotion_type in enumerate([EmotionType.JOY, EmotionType.SADNESS, EmotionType.NEUTRAL]):
        print(f"Creating experience {i} with {emotion_type.value}")
        exp = await manager.create_experience(
            f"Experience {i} with {emotion_type.value}",
            emotion=EmotionalTag(
                valence=0.5 if emotion_type == EmotionType.JOY else -0.5 if emotion_type == EmotionType.SADNESS else 0,
                arousal=0.5,
                dominance=0.5,
                primary_emotion=emotion_type,
                emotion_intensity=0.6,
                confidence=0.9,
                timestamp=datetime.now()
            )
        )
        experiences.append(exp)
        print(f"  Created: {exp.memory_id}")
    
    # Test direct recall
    print("\nTrying to recall 'Experience 0'...")
    result = await manager._direct_recall("Experience 0")
    
    if result:
        print(f"Result keys: {list(result.keys())}")
        print(f"Has emotion: {'emotion' in result}")
        print(f"Has confidence: {'confidence' in result}")
        print(f"Has vividness: {'vividness' in result}")
        print(f"Has colored_by_mood: {'colored_by_mood' in result}")
        return all(key in result for key in ['emotion', 'confidence', 'vividness', 'colored_by_mood'])
    else:
        print("No result from recall")
        return False

async def main():
    """Run all debug tests."""
    results = {}
    
    # Debug each test
    results['working_memory'] = await debug_working_memory()
    results['emotional_influence'] = await debug_emotional_influence()
    results['interstitial'] = await debug_interstitial()
    results['experience_recall'] = await debug_experience_recall()
    
    print("\n" + "="*50)
    print("DEBUG RESULTS:")
    for test, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test}: {status}")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())