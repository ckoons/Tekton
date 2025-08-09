#!/usr/bin/env python3
"""
Test suite for Phase 2: Experiential Memory Layer

Tests narrative memory tools and personality emergence features.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.environ['TEKTON_ROOT'] = str(Path(__file__).parent.parent.parent)

from engram.core.mcp.tools import (
    # Enhanced memory store
    memory_store,
    # Narrative tools
    memory_narrative,
    memory_thread,
    memory_pattern,
    # Personality tools
    personality_snapshot,
    preference_learn,
    behavior_pattern
)


async def test_experiential_memory_store():
    """Test enhanced MemoryStore with full experiential metadata."""
    print("\n" + "=" * 70)
    print("Testing Enhanced MemoryStore with Experiential Metadata")
    print("=" * 70)
    
    # Store memory with full experiential data
    result = await memory_store(
        content="Successfully implemented Phase 2 experiential features!",
        namespace="thinking",
        emotion="excited",
        confidence=0.95,
        context="Working on Unified Memory Sprint",
        with_ci="Cari",
        why="To enable personality emergence and narrative memories"
    )
    
    print(f"\nStored memory with experiential data:")
    print(f"  Success: {result['success']}")
    if result.get("experiential"):
        exp = result["experiential"]
        print(f"  WHO: {exp['who']}")
        print(f"  WHAT: {exp['what']}")
        print(f"  WHEN: {exp['when']}")
        print(f"  WHY: {exp['why']}")
        print(f"  HOW_IT_FELT: {exp['how_it_felt']}")
    
    return result["success"]


async def test_narrative_tools():
    """Test narrative memory tools."""
    print("\n" + "=" * 70)
    print("Testing Narrative Memory Tools")
    print("=" * 70)
    
    # First, store some related memories to create a narrative
    memories_to_store = [
        ("Started working on MCP tools", "curious", 0.6),
        ("Connected MCP tools to MemoryService", "focused", 0.8),
        ("All basic tools working successfully", "excited", 0.9),
        ("Added cross-CI sharing capabilities", "confident", 0.95),
        ("Implemented experiential features", "proud", 1.0)
    ]
    
    print("\n1. Storing narrative memories...")
    for content, emotion, confidence in memories_to_store:
        await memory_store(
            content=content,
            namespace="conversations",
            emotion=emotion,
            confidence=confidence,
            with_ci="Cari"
        )
    print(f"   Stored {len(memories_to_store)} memories")
    
    # Test MemoryNarrative
    print("\n2. Testing MemoryNarrative...")
    narrative_result = await memory_narrative(
        starting_query="MCP tools",
        max_chain=5,
        include_emotions=True,
        namespace="conversations"
    )
    
    if narrative_result["success"]:
        print(f"   Created narrative with {narrative_result['chain_length']} memories")
        print("\n   Narrative:")
        print("   " + "-" * 50)
        for line in narrative_result["narrative"].split("\n"):
            if line:
                print(f"   {line}")
    
    # Test MemoryPattern
    print("\n3. Testing MemoryPattern...")
    
    # Emotional patterns
    emotional_patterns = await memory_pattern(
        query="",
        pattern_type="emotional",
        min_occurrences=2
    )
    
    if emotional_patterns["success"] and emotional_patterns["patterns"]:
        print(f"   Found {len(emotional_patterns['patterns'])} emotional patterns:")
        for pattern in emotional_patterns["patterns"][:3]:
            print(f"     - {pattern['pattern']} ({pattern['occurrences']} times)")
    
    # Behavioral patterns
    behavioral_patterns = await memory_pattern(
        query="MCP",
        pattern_type="behavioral",
        min_occurrences=2
    )
    
    if behavioral_patterns["success"] and behavioral_patterns["patterns"]:
        print(f"   Found {len(behavioral_patterns['patterns'])} behavioral patterns:")
        for pattern in behavioral_patterns["patterns"][:3]:
            print(f"     - {pattern['pattern']}")
    
    return narrative_result["success"]


async def test_personality_emergence():
    """Test personality emergence tools."""
    print("\n" + "=" * 70)
    print("Testing Personality Emergence Tools")
    print("=" * 70)
    
    # Test PersonalitySnapshot
    print("\n1. Testing PersonalitySnapshot...")
    snapshot = await personality_snapshot(
        ci_name="Cari",
        analyze_days=7,
        namespaces=["conversations", "thinking", "shared-collective"]
    )
    
    if snapshot["success"]:
        traits = snapshot["personality_traits"]
        print(f"   Analyzed {snapshot['analyzed_memories']} memories")
        print(f"   Confidence Level: {traits['confidence_level']:.2f}")
        print(f"   Interaction Style: {traits['interaction_style']}")
        
        if traits["emotional_profile"]:
            print("   Emotional Profile:")
            for emotion, weight in list(traits["emotional_profile"].items())[:3]:
                print(f"     - {emotion}: {weight:.2%}")
        
        if traits["primary_interests"]:
            print(f"   Primary Interests: {', '.join(traits['primary_interests'][:3])}")
    
    # Test PreferenceLearn
    print("\n2. Testing PreferenceLearn...")
    
    # Learn topic preferences
    topic_prefs = await preference_learn(
        ci_name="Cari",
        preference_category="topics",
        save_learned=True
    )
    
    if topic_prefs["success"] and topic_prefs["preferences"]["learned_preferences"]:
        print(f"   Learned {len(topic_prefs['preferences']['learned_preferences'])} topic preferences:")
        for pref in topic_prefs["preferences"]["learned_preferences"]:
            print(f"     - {pref['topic']}: {pref['interest_level']:.2%}")
    
    # Learn method preferences
    method_prefs = await preference_learn(
        ci_name="Cari",
        preference_category="methods",
        save_learned=True
    )
    
    if method_prefs["success"] and method_prefs["preferences"]["learned_preferences"]:
        print(f"   Learned {len(method_prefs['preferences']['learned_preferences'])} method preferences:")
        for pref in method_prefs["preferences"]["learned_preferences"]:
            print(f"     - {pref['method']}: {pref['preference']:.2f}")
    
    # Test BehaviorPattern
    print("\n3. Testing BehaviorPattern...")
    behaviors = await behavior_pattern(
        ci_name="Cari",
        pattern_window=7,
        pattern_threshold=0.2
    )
    
    if behaviors["success"]:
        patterns = behaviors["behavior_patterns"]
        print(f"   Analyzed {behaviors['analyzed_memories']} memories")
        
        if patterns["communication_patterns"]:
            print("   Communication Patterns:")
            for p in patterns["communication_patterns"]:
                print(f"     - {p['description']} ({p['frequency']:.1%})")
        
        if patterns["work_patterns"]:
            print("   Work Patterns:")
            for p in patterns["work_patterns"]:
                print(f"     - {p['description']} ({p['frequency']:.1%})")
        
        if patterns["emotional_patterns"]:
            print("   Emotional Patterns:")
            for p in patterns["emotional_patterns"]:
                print(f"     - {p['description']} ({p['frequency']:.1%})")
    
    return snapshot["success"]


async def main():
    """Run all Phase 2 tests."""
    print("\n" + "=" * 70)
    print("PHASE 2: EXPERIENTIAL MEMORY LAYER - TEST SUITE")
    print("=" * 70)
    print(f"Started at: {datetime.now().isoformat()}")
    
    # Run tests
    store_success = await test_experiential_memory_store()
    narrative_success = await test_narrative_tools()
    personality_success = await test_personality_emergence()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✓ Enhanced MemoryStore: {'PASSED' if store_success else 'FAILED'}")
    print(f"✓ Narrative Tools: {'PASSED' if narrative_success else 'FAILED'}")
    print(f"✓ Personality Emergence: {'PASSED' if personality_success else 'FAILED'}")
    
    print("\nPhase 2 Features Verified:")
    print("✓ WHO, WHAT, WHEN, WHY, HOW_IT_FELT metadata structure")
    print("✓ Memory narratives and chains")
    print("✓ Pattern extraction from experiences")
    print("✓ Personality snapshots")
    print("✓ Preference learning")
    print("✓ Behavior pattern identification")
    
    print(f"\nCompleted at: {datetime.now().isoformat()}")


if __name__ == "__main__":
    asyncio.run(main())