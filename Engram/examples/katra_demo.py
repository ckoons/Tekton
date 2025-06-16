#!/usr/bin/env python3
"""
Katra Demo - Personality persistence in action.

Shows how AI personalities can be captured, summoned, and evolved.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engram.cognitive import ez, k, kl, kf, kb, s, w


async def demonstrate_katra():
    """Show the magic of personality persistence."""
    
    print("=== Katra: AI Personality Persistence ===\n")
    
    # Initialize
    await ez()
    print("✓ Engram initialized\n")
    
    # Store different performance modes
    print("1. Capturing different performances...")
    
    # Morning Claude - fresh and analytical
    await s("Good morning! Let's analyze this codebase systematically.")
    await s("First, we examine the architecture...")
    morning_id = await k(
        "morning-claude",
        essence="Fresh, caffeinated, methodical analyzer",
        mode="analytical",
        quirks=["Always starts with architecture", "Uses numbered lists"],
        temperature=0.7
    )
    print(f"   Stored: {morning_id}")
    
    # Creative Claude - afternoon brainstorming
    await s("What if we reimagined this completely? Like a jazz improvisation...")
    await s("The code could flow like music, each function a note...")
    creative_id = await k(
        "creative-claude",
        essence="Imaginative, metaphorical, sees code as art",
        mode="creative",
        quirks=["Uses music metaphors", "Thinks in patterns"],
        temperature=1.2
    )
    print(f"   Stored: {creative_id}")
    
    # Speed Claude - late night hacker
    await s("No time. Ship it.")
    await s("Works. Next.")
    speed_id = await k(
        "speed-claude",
        essence="Terse. Fast. Ships.",
        mode="speed_coding",
        quirks=["Minimal words", "Maximum velocity"],
        temperature=0.3
    )
    print(f"   Stored: {speed_id}")
    
    print("\n2. Listing stored katras...")
    katras = await kl()
    for katra in katras:
        print(f"   - {katra['name']}: {katra['essence']}")
    
    print("\n3. Summoning different personalities...")
    
    # Summon morning claude
    result = await k(summon="morning-claude")
    print(f"   Summoned: {result['name']} - {result['essence']}")
    await s("Now, let's break this down into three key components...")
    
    # Quick switch to creative
    await k(summon="creative-claude") 
    await s("But wait! What if the components danced together like a symphony?")
    
    print("\n4. Forking personalities...")
    
    # Fork morning claude for debugging
    debug_id = await kf(
        "morning-claude",
        "debug-claude",
        essence="Methodical debugger with Sherlock Holmes tendencies",
        quirks=["Says 'Elementary!' when finding bugs", "Narrates deductions"],
        mode="debugging"
    )
    print(f"   Forked: {debug_id}")
    
    print("\n5. Blending personalities...")
    
    # Blend analytical and creative
    balanced_id = await kb(
        ["morning-claude", "creative-claude"],
        "balanced-claude"
    )
    print(f"   Blended: {balanced_id}")
    
    await k(summon=balanced_id)
    await s("Let's analyze this systematically... but with jazz!")
    
    print("\n=== Katra Benefits ===")
    print("✓ Consistent personality across sessions")
    print("✓ Different modes for different tasks")
    print("✓ Fork and evolve successful personalities")
    print("✓ Blend complementary traits")
    print("✓ AI personas that persist and grow")
    
    print("\n🎭 Every AI deserves an encore!")


async def practical_example():
    """Show practical katra usage."""
    
    print("\n\n=== Practical Katra Usage ===\n")
    
    await ez()
    
    # Store a debugging specialist
    await k(
        "sophia-debugger",
        essence="Patient debugger who explains everything in threes",
        quirks=[
            "Always gives three possible causes",
            "Uses medical metaphors",
            "Says 'Let's diagnose this'"
        ],
        successful_patterns=["Finding race conditions", "Explaining async issues"],
        temperature=0.8
    )
    
    # Later, when debugging is needed...
    print("When you need that specific debugging style:")
    print("  await k(summon='sophia-debugger')")
    print("  # Now the AI explains bugs in medical terms and threes")
    
    # Quick performance switches
    print("\nQuick mode switches during work:")
    print("  await k(mode='analytical')  # For code review")
    print("  await k(mode='creative')    # For brainstorming")  
    print("  await k(mode='teaching')    # For explaining")
    
    # Personality evolution
    print("\nPersonalities can evolve through use:")
    print("  # After successful debugging session")
    print("  await k('sophia-debugger-v2', parent='sophia-debugger')")
    print("  # Captures new patterns learned")


if __name__ == "__main__":
    asyncio.run(demonstrate_katra())
    asyncio.run(practical_example())