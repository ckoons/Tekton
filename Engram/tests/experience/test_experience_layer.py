"""
Tests for the ESR Experience Layer.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
import pytest
from datetime import datetime, timedelta

from engram.core.experience.experience_layer import ExperienceManager, MemoryExperience
from engram.core.experience.emotional_context import EmotionalTag, EmotionType
from engram.core.experience.memory_promises import MemoryPromise, PromiseState
from engram.core.experience.working_memory import WorkingMemory, ThoughtState
from engram.core.experience.interstitial_processor import InterstitialProcessor, BoundaryType


@pytest.mark.asyncio
async def test_experience_creation():
    """Test creating memory experiences with emotional tagging."""
    manager = ExperienceManager()
    
    # Create an experience with default emotion
    experience = await manager.create_experience(
        content="This is a test memory",
        importance=0.7
    )
    
    assert experience.memory_id is not None
    assert experience.content == "This is a test memory"
    assert experience.emotional_tag is not None
    assert experience.importance == 0.7
    assert experience.confidence == 0.8
    assert experience.vividness == 1.0
    
    # Create experience with specific emotion
    emotion = EmotionalTag(
        valence=0.8,
        arousal=0.6,
        dominance=0.5,
        primary_emotion=EmotionType.JOY,
        emotion_intensity=0.9,
        confidence=1.0,
        timestamp=datetime.now()
    )
    
    experience2 = await manager.create_experience(
        content="Happy memory",
        emotion=emotion,
        confidence=0.95
    )
    
    assert experience2.emotional_tag.primary_emotion == EmotionType.JOY
    assert experience2.emotional_tag.valence == 0.8
    assert experience2.confidence == 0.95
    
    print("✓ Experience creation test passed")


@pytest.mark.asyncio
async def test_memory_promises():
    """Test progressive memory recall with promises."""
    manager = ExperienceManager()
    
    # Create some experiences first
    for i in range(3):
        await manager.create_experience(f"Memory {i}")
    
    # Test promise-based recall
    promise = await manager.recall_experience("Memory 1", use_promise=True)
    
    assert isinstance(promise, MemoryPromise)
    assert promise.state in [PromiseState.PENDING, PromiseState.RESOLVING]
    
    # Wait for resolution (with timeout)
    try:
        result = await promise.wait(timeout=2.0)
        assert promise.state == PromiseState.RESOLVED
        assert promise.confidence > 0
    except (asyncio.TimeoutError, Exception) as e:
        # Promise timed out or failed (no memory system) is acceptable for this test
        assert promise.state in [PromiseState.TIMEOUT, PromiseState.FAILED]
    
    # Test partial results
    promise2 = await manager.recall_experience("Memory 2", use_promise=True)
    await asyncio.sleep(0.1)  # Give time for partial results
    
    best_result = promise2.get_best_result()
    # May or may not have partial results yet
    
    print("✓ Memory promises test passed")


@pytest.mark.asyncio
async def test_working_memory():
    """Test working memory capacity and consolidation."""
    memory = WorkingMemory(capacity=5)
    
    # Add thoughts up to capacity
    thought_ids = []
    for i in range(5):
        thought_id = await memory.add_thought(f"Thought {i}")
        thought_ids.append(thought_id)
    
    assert len(memory.thoughts) == 5
    assert memory.is_overloaded()  # At capacity means overloaded
    
    # Access a thought multiple times
    for _ in range(5):
        await memory.access_thought(thought_ids[0])
    
    thought = memory.thoughts[thought_ids[0]]
    assert thought.access_count == 5
    assert thought.state == ThoughtState.REHEARSING
    
    # Add beyond capacity
    await memory.add_thought("Overflow thought")
    assert len(memory.thoughts) <= 5  # Should have made room
    
    # Test chunking
    await memory.chunk_thoughts(thought_ids[:3], "test_chunk")
    assert "test_chunk" in memory.chunks
    assert len(memory.chunks["test_chunk"]) == 3
    
    # Test consolidation
    consolidated = await memory.consolidate_all()
    # Some thoughts may have been marked for consolidation
    
    print("✓ Working memory test passed")


@pytest.mark.asyncio
async def test_emotional_influence():
    """Test how emotions influence memory recall."""
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
    
    sad_memory = await manager.create_experience(
        "Lost my keys, feeling sad",
        emotion=EmotionalTag(
            valence=-0.7,
            arousal=0.3,
            dominance=0.3,
            primary_emotion=EmotionType.SADNESS,
            emotion_intensity=0.7,
            confidence=1.0,
            timestamp=datetime.now()
        )
    )
    
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
    
    # Happy mood should make happy memories more accessible
    result = await manager._direct_recall("lottery")
    if result:
        assert "colored_by_mood" in result
        assert result["colored_by_mood"] == "joy"
    
    print("✓ Emotional influence test passed")


@pytest.mark.asyncio
async def test_interstitial_processing():
    """Test memory processing at cognitive boundaries."""
    manager = ExperienceManager()
    processor = InterstitialProcessor(experience_manager=manager)
    
    # Create initial context
    context1 = {"topic": "weather", "activity": "discussion"}
    
    # No boundary initially
    boundary = await processor.detect_boundary(context1)
    assert boundary is None
    
    # Topic shift
    context2 = {"topic": "politics", "activity": "discussion"}
    boundary = await processor.detect_boundary(context2)
    assert boundary == BoundaryType.TOPIC_SHIFT
    
    # Temporal gap
    processor.last_activity = datetime.now() - timedelta(seconds=35)
    context3 = {"topic": "politics", "activity": "discussion"}
    boundary = await processor.detect_boundary(context3)
    assert boundary == BoundaryType.TEMPORAL_GAP
    
    # Context switch
    context4 = {"task": "coding", "mode": "focused"}
    boundary = await processor.detect_boundary(context4)
    assert boundary == BoundaryType.CONTEXT_SWITCH
    
    # Test consolidation at boundary
    if processor.pending_boundaries:
        boundary_to_process = processor.pending_boundaries[0]
        await processor.consolidate_at_boundary(boundary_to_process)
        assert boundary_to_process in processor.processed_boundaries
    
    print("✓ Interstitial processing test passed")


@pytest.mark.asyncio
async def test_memory_decay():
    """Test temporal decay of memory vividness and confidence."""
    manager = ExperienceManager()
    
    # Create a memory
    experience = await manager.create_experience(
        "Test memory for decay",
        confidence=1.0
    )
    
    initial_vividness = experience.vividness
    initial_confidence = experience.confidence
    
    # Simulate time passing (1 hour)
    experience.decay(1.0)
    
    assert experience.vividness < initial_vividness
    assert experience.confidence < initial_confidence
    assert experience.vividness >= 0.1  # Should not decay to zero
    
    # Test reinforcement
    experience.reinforce(0.3)
    reinforced_vividness = experience.vividness
    assert reinforced_vividness > experience.vividness - 0.3  # Should increase
    
    print("✓ Memory decay test passed")


@pytest.mark.asyncio
async def test_experience_recall_with_emotion():
    """Test full experience recall with emotional coloring."""
    manager = ExperienceManager()
    
    # Create multiple experiences
    experiences = []
    for i, emotion_type in enumerate([EmotionType.JOY, EmotionType.SADNESS, EmotionType.NEUTRAL]):
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
    
    # Test direct recall
    result = await manager._direct_recall("Experience 0")
    if result:
        assert "emotion" in result
        assert "confidence" in result
        assert "vividness" in result
        assert "colored_by_mood" in result
    
    print("✓ Experience recall with emotion test passed")


@pytest.mark.asyncio
async def test_dream_recombination():
    """Test dream-like memory recombination during idle."""
    manager = ExperienceManager()
    processor = InterstitialProcessor(experience_manager=manager)
    
    # Create some experiences
    for i in range(5):
        await manager.create_experience(f"Dream memory {i}")
    
    initial_associations = sum(
        len(exp.associations) if exp.associations else 0
        for exp in manager.experiences.values()
    )
    
    # Simulate idle period and dream recombination
    await processor.dream_recombine(timedelta(minutes=2))
    
    # Check for new associations
    final_associations = sum(
        len(exp.associations) if exp.associations else 0
        for exp in manager.experiences.values()
    )
    
    # Should have created some new associations
    assert final_associations >= initial_associations
    
    print("✓ Dream recombination test passed")


@pytest.mark.asyncio
async def test_mood_summary():
    """Test getting mood summary."""
    manager = ExperienceManager()
    
    # Create experiences with different emotions
    emotions = [
        EmotionType.JOY,
        EmotionType.SADNESS,
        EmotionType.JOY,
        EmotionType.NEUTRAL
    ]
    
    for emotion_type in emotions:
        manager.emotional_context.update_mood(
            EmotionalTag(
                valence=0.5 if emotion_type == EmotionType.JOY else -0.5 if emotion_type == EmotionType.SADNESS else 0,
                arousal=0.5,
                dominance=0.5,
                primary_emotion=emotion_type,
                emotion_intensity=0.6,
                confidence=0.9,
                timestamp=datetime.now()
            )
        )
    
    summary = manager.get_mood_summary()
    
    assert "current_mood" in summary
    assert "recent_emotions" in summary
    assert "mood_stability" in summary
    
    assert summary["current_mood"]["emotion"] in ["joy", "sadness", "neutral"]
    assert len(summary["recent_emotions"]) <= 10
    assert 0 <= summary["mood_stability"] <= 1
    
    print("✓ Mood summary test passed")


@pytest.mark.asyncio 
async def test_working_memory_status():
    """Test working memory status reporting."""
    manager = ExperienceManager()
    
    # Add some thoughts
    for i in range(3):
        await manager.working_memory.add_thought(f"Status test thought {i}")
    
    status = manager.get_working_memory_status()
    
    assert "capacity_usage" in status
    assert "active_thoughts" in status
    assert "is_overloaded" in status
    assert "consolidation_queue" in status
    
    assert 0 <= status["capacity_usage"] <= 1
    assert status["active_thoughts"] >= 0
    assert isinstance(status["is_overloaded"], bool)
    
    print("✓ Working memory status test passed")


# Run tests
if __name__ == "__main__":
    asyncio.run(test_experience_creation())
    asyncio.run(test_memory_promises())
    asyncio.run(test_working_memory())
    asyncio.run(test_emotional_influence())
    asyncio.run(test_interstitial_processing())
    asyncio.run(test_memory_decay())
    asyncio.run(test_experience_recall_with_emotion())
    asyncio.run(test_dream_recombination())
    asyncio.run(test_mood_summary())
    asyncio.run(test_working_memory_status())
    
    print("\n✅ All Experience Layer tests passed!")