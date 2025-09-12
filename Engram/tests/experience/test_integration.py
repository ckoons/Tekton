"""
Integration tests for ESR Experience Layer with full system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
import pytest
from datetime import datetime, timedelta

# Import ESR core components
from engram.core.storage.unified_interface import ESRMemorySystem
from engram.core.storage.direct_backends import get_direct_backends

# Import Experience Layer
from engram.core.experience.experience_layer import ExperienceManager
from engram.core.experience.emotional_context import EmotionalTag, EmotionType
from engram.core.experience.interstitial_processor import InterstitialProcessor


@pytest.mark.asyncio
async def test_full_integration_with_backends():
    """Test Experience Layer with real ESR backends."""
    
    # Initialize real backends
    backends = get_direct_backends()
    
    # Create ESR system with backends
    esr_system = ESRMemorySystem(backends=backends)
    
    # Create Experience Manager with ESR system
    experience_manager = ExperienceManager(memory_system=esr_system)
    
    # Test 1: Create experience that gets stored everywhere
    experience = await experience_manager.create_experience(
        content="Integration test memory",
        importance=0.9
    )
    
    # Let it consolidate
    await experience_manager.working_memory.consolidate_all()
    
    # Verify it was stored in ESR
    recalled = await esr_system.recall("Integration test memory")
    assert recalled is not None
    
    print("✓ Full integration with backends test passed")


@pytest.mark.asyncio
async def test_multi_ci_memory_sharing():
    """Test memory sharing between multiple CI instances."""
    
    # Simulate two CI instances with shared backend
    backends = get_direct_backends()
    esr_system = ESRMemorySystem(backends=backends)
    
    # CI-A creates an emotional memory
    ci_a = ExperienceManager(memory_system=esr_system)
    await ci_a.create_experience(
        "Discovered a beautiful algorithm",
        emotion=EmotionalTag(
            valence=0.8,
            arousal=0.7,
            dominance=0.6,
            primary_emotion=EmotionType.JOY,
            emotion_intensity=0.8,
            confidence=1.0,
            timestamp=datetime.now()
        )
    )
    
    # Consolidate to shared storage
    await ci_a.working_memory.consolidate_all()
    
    # CI-B recalls the memory with its own emotional context
    ci_b = ExperienceManager(memory_system=esr_system)
    ci_b.emotional_context.update_mood(EmotionalTag(
        valence=-0.3,
        arousal=0.4,
        dominance=0.5,
        primary_emotion=EmotionType.SADNESS,
        emotion_intensity=0.5,
        confidence=1.0,
        timestamp=datetime.now()
    ))
    
    # CI-B's sad mood should influence how it perceives CI-A's happy memory
    result = await ci_b._direct_recall("algorithm")
    
    # The memory exists but is colored by CI-B's mood
    if result:
        assert result['colored_by_mood'] == 'sadness'
    
    print("✓ Multi-CI memory sharing test passed")


@pytest.mark.asyncio
async def test_session_workflow():
    """Test a complete session workflow with boundaries."""
    
    backends = get_direct_backends()
    esr_system = ESRMemorySystem(backends=backends)
    manager = ExperienceManager(memory_system=esr_system)
    processor = InterstitialProcessor(
        experience_manager=manager,
        memory_system=esr_system
    )
    
    # Simulate a conversation with topic shifts
    contexts = [
        {"topic": "weather", "user": "Tell me about the weather"},
        {"topic": "weather", "user": "Is it going to rain?"},
        {"topic": "coding", "user": "How do I write a Python function?"},  # Topic shift
        {"topic": "coding", "user": "What about error handling?"},
        {"topic": "philosophy", "user": "What is consciousness?"}  # Another shift
    ]
    
    memories_created = []
    boundaries_detected = []
    
    for i, context in enumerate(contexts):
        # Create memory for each interaction
        exp = await manager.create_experience(
            f"Response to: {context['user']}",
            importance=0.5 + (i * 0.1)
        )
        memories_created.append(exp)
        
        # Detect boundaries
        boundary = await processor.detect_boundary(context)
        if boundary:
            boundaries_detected.append(boundary)
            # Process boundary (consolidate memories)
            if processor.pending_boundaries:
                await processor.consolidate_at_boundary(
                    processor.pending_boundaries[-1]
                )
    
    # Should have detected topic shifts
    assert len(boundaries_detected) >= 2
    
    # Memories should be consolidated
    assert len(manager.working_memory.thoughts) < len(memories_created)
    
    print("✓ Session workflow test passed")


@pytest.mark.asyncio
async def test_emotional_contagion():
    """Test how emotions spread across related memories."""
    
    manager = ExperienceManager()
    
    # Create a cluster of related memories
    memories = []
    for i in range(3):
        exp = await manager.create_experience(
            f"Part {i} of a happy story",
            emotion=EmotionalTag(
                valence=0.7,
                arousal=0.6,
                dominance=0.5,
                primary_emotion=EmotionType.JOY,
                emotion_intensity=0.7,
                confidence=1.0,
                timestamp=datetime.now()
            )
        )
        memories.append(exp)
    
    # Create associations between them
    for i in range(len(memories) - 1):
        memories[i].associations = [memories[i+1].memory_id]
        memories[i+1].associations = [memories[i].memory_id]
    
    # Now create a sad memory related to the story
    sad_memory = await manager.create_experience(
        "But then something sad happened",
        emotion=EmotionalTag(
            valence=-0.8,
            arousal=0.7,
            dominance=0.3,
            primary_emotion=EmotionType.SADNESS,
            emotion_intensity=0.9,
            confidence=1.0,
            timestamp=datetime.now()
        )
    )
    
    # Associate it with the happy memories
    sad_memory.associations = [m.memory_id for m in memories]
    
    # The emotional context should be influenced
    mood = manager.get_mood_summary()
    
    # Mood should have shifted toward sadness
    assert mood['current_mood']['valence'] < 0.5
    
    print("✓ Emotional contagion test passed")


@pytest.mark.asyncio
async def test_memory_overflow_handling():
    """Test how system handles memory overflow."""
    
    manager = ExperienceManager()
    manager.working_memory.capacity = 3  # Small capacity for testing
    
    # Overflow the working memory
    overflow_thoughts = []
    for i in range(10):
        exp = await manager.create_experience(
            f"Overflow thought {i}",
            importance=0.1 if i < 5 else 0.9  # Later thoughts more important
        )
        overflow_thoughts.append(exp)
    
    # Working memory should be at capacity
    assert len(manager.working_memory.thoughts) <= 3
    
    # Important thoughts should be retained or consolidated
    remaining_ids = set(manager.working_memory.thoughts.keys())
    consolidated = manager.working_memory.consolidation_queue
    
    # Higher importance thoughts should be preserved
    important_count = sum(
        1 for t in overflow_thoughts[5:]
        if t.memory_id in remaining_ids or t.memory_id in consolidated
    )
    
    assert important_count >= 2  # Most important thoughts preserved
    
    print("✓ Memory overflow handling test passed")


@pytest.mark.asyncio
async def test_long_term_memory_persistence():
    """Test that consolidated memories persist across sessions."""
    
    import tempfile
    import json
    
    # Use temporary directory for test data
    with tempfile.TemporaryDirectory() as tmpdir:
        # Session 1: Create and consolidate memories
        backends1 = get_direct_backends(data_dir=tmpdir)
        esr1 = ESRMemorySystem(backends=backends1)
        manager1 = ExperienceManager(memory_system=esr1)
        
        exp1 = await manager1.create_experience(
            "Persistent memory from session 1",
            importance=1.0
        )
        
        # Force consolidation
        await manager1.working_memory.consolidate_all()
        
        # Store the memory ID
        memory_id = exp1.memory_id
        
        # Clean up session 1
        await manager1.cleanup()
        
        # Session 2: New manager with same backends
        backends2 = get_direct_backends(data_dir=tmpdir)
        esr2 = ESRMemorySystem(backends=backends2)
        manager2 = ExperienceManager(memory_system=esr2)
        
        # Should be able to recall the memory
        recalled = await esr2.recall("Persistent memory from session 1")
        
        assert recalled is not None
        assert "Persistent memory" in str(recalled)
        
        print("✓ Long-term memory persistence test passed")


# Run integration tests
if __name__ == "__main__":
    async def run_all():
        tests = [
            ("Full Integration", test_full_integration_with_backends),
            ("Multi-CI Sharing", test_multi_ci_memory_sharing),
            ("Session Workflow", test_session_workflow),
            ("Emotional Contagion", test_emotional_contagion),
            ("Memory Overflow", test_memory_overflow_handling),
            ("Persistence", test_long_term_memory_persistence)
        ]
        
        print("\n" + "="*60)
        print("ESR EXPERIENCE LAYER INTEGRATION TESTS")
        print("="*60)
        
        for name, test_func in tests:
            try:
                await test_func()
                print(f"✓ {name}: PASSED")
            except Exception as e:
                print(f"✗ {name}: FAILED - {e}")
        
        print("="*60)
        print("Integration testing complete!")
    
    asyncio.run(run_all())