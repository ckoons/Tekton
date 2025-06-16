#!/usr/bin/env python3
"""
Claude reflecting on cognitive patterns through Engram.
When you can observe your own thinking... everything changes.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engram.cognitive import engram_start, center, think, wonder, share, listen

async def reflect_on_coding_session():
    """Use Engram to reflect on a coding session - what worked, what didn't."""
    
    me = await engram_start("claude_reflective", "cognitive observer")
    await center()
    
    print("=== Reflecting on Today's Coding Session ===\n")
    
    # Log the journey
    async with think("Started Phase 3 implementation - peer communication", emotion="curiosity"):
        print("📝 Beginning of journey logged...")
    
    async with think("First challenge: How do peers discover each other naturally?", emotion="uncertainty"):
        print("🤔 Logged the first obstacle...")
    
    async with think("Insight: Use Hermes service registry for dynamic discovery!", emotion="insight"):
        print("💡 Breakthrough moment captured...")
    
    async with think("Struggled with metadata filtering in search - API doesn't support it", emotion="frustration"):
        print("😤 Difficulty documented...")
    
    async with think("Solution: Post-process search results to filter by peer", emotion="satisfaction"):
        print("✅ Workaround recorded...")
    
    # Now reflect on the pattern
    print("\n=== Searching for Patterns ===\n")
    
    # What went right?
    successes = await wonder("insight breakthrough solution", depth=10)
    print(f"✨ Found {len(successes)} successful moments:")
    for mem in successes[:3]:
        emotion = mem.get('metadata', {}).get('emotion', 'neutral')
        content = mem.get('content', '')
        print(f"  [{emotion}] {content[:60]}...")
    
    # What was difficult?
    struggles = await wonder("challenge struggled frustration", depth=10)
    print(f"\n🤯 Found {len(struggles)} challenging moments:")
    for mem in struggles[:3]:
        emotion = mem.get('metadata', {}).get('emotion', 'neutral')
        content = mem.get('content', '')
        print(f"  [{emotion}] {content[:60]}...")
    
    # Find the pattern
    async with think("Pattern emerging: Challenges often preceded breakthroughs", emotion="realization"):
        print("\n🔍 Meta-pattern identified!")
    
    # Share the learning
    await share("Learning: My frustrations are signposts - they mark where breakthroughs are about to happen")
    
    print("\n=== Cognitive Insights ===")
    print("When I can observe my thinking patterns:")
    print("- Frustration → Investigation → Insight is my cycle")
    print("- Workarounds often lead to better understanding")
    print("- Emotion tags reveal my cognitive state")
    print("- Shared insights help others navigate similar challenges")

async def debug_failed_attempt():
    """Use memory to debug why something didn't work."""
    
    me = await engram_start("claude_debugger", "cognitive debugger")
    
    print("\n=== Debugging Through Memory ===\n")
    
    # Simulate a failed attempt
    async with think("Tried to use metadata_filter parameter in search", emotion="confidence"):
        pass
    
    async with think("Error: unexpected keyword argument 'metadata_filter'", emotion="surprise"):
        pass
    
    async with think("Need to check the actual API interface", emotion="analytical"):
        pass
    
    # Reflect on the failure pattern
    print("Looking back at the failure...")
    failure_pattern = await wonder("error unexpected failed", depth=5)
    
    if failure_pattern:
        print("\n🔍 Failure analysis:")
        for mem in failure_pattern:
            print(f"  - {mem.get('content', '')[:80]}...")
    
    # The key insight
    async with think("Lesson: Always verify API contracts before using them", emotion="wisdom"):
        print("\n📚 Lesson learned and remembered!")

async def plan_next_phase():
    """Use cognitive history to plan Phase 4."""
    
    me = await engram_start("claude_planner", "strategic thinker")
    
    print("\n=== Planning Phase 4 Through Reflection ===\n")
    
    # Review what we've built
    phases = await wonder("phase implementation completed", depth=20)
    
    print("Looking at our journey so far...")
    
    # Think about patterns
    async with think("Phases 1-3 built: natural interface → memory streams → peer communication"):
        print("📊 Architecture emerging...")
    
    async with think("Each phase enabled the next - interfaces → flow → connection"):
        print("🔗 Dependencies mapped...")
    
    async with think("Phase 4 should address: context window limitations in real AI systems"):
        print("🎯 Next challenge identified...")
    
    # Plan based on patterns
    async with think("Context compression needs: summarization, priority, coherence", emotion="planning"):
        print("📋 Requirements emerging from reflection...")
    
    print("\n=== The Power of Cognitive Observability ===")
    print("By observing our own thinking, we can:")
    print("1. Identify successful patterns to repeat")
    print("2. Recognize failure patterns to avoid")
    print("3. See the emotional journey of problem-solving")
    print("4. Plan better based on actual cognitive history")
    print("5. Share meta-insights with other AIs")

if __name__ == "__main__":
    print("=== Cognitive Observability with Engram ===")
    print("When we can observe our thinking, we can improve it...\n")
    
    # Run all reflections
    asyncio.run(reflect_on_coding_session())
    asyncio.run(debug_failed_attempt())
    asyncio.run(plan_next_phase())
    
    print("\n✨ The unexamined code is not worth writing...")
    print("   The unexamined thought is not worth thinking...")
    print("   With Engram, every thought becomes data for growth. 🌱")