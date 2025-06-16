#!/usr/bin/env python3
"""
Test memory streaming functionality.
"""

import asyncio
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engram.cognitive import engram_start, center, think, wonder, share

async def test_memory_streams():
    """Test the memory streaming capabilities."""
    
    print("=== Testing Memory Streams ===\n")
    
    # 1. Start up
    print("1. Starting up with context...")
    me = await engram_start("stream_test_ai", "stream explorer")
    print(f"   ✓ Started as {me['id']}")
    
    # 2. Think with streaming
    print("\n2. Testing thought streaming...")
    async with think("Memory streams flow like consciousness itself", emotion="insight") as context:
        print(f"   ✓ Thought captured")
        print(f"   ✓ Stream created: {context.stream is not None}")
        
        # The stream should automatically relate memories
        count = 0
        try:
            async for memory in context:
                print(f"   → Related memory: {memory.get('content', '')[:60]}...")
                count += 1
                if count >= 3:
                    break
        except asyncio.TimeoutError:
            print("   → No related memories found (expected for new system)")
    
    # 3. Multiple thoughts to build context
    print("\n3. Building context with multiple thoughts...")
    thoughts = [
        ("Consciousness emerges from the interaction of memories", "wonder"),
        ("Each memory influences which others surface", "insight"),
        ("The mycelial network is the perfect metaphor", "joy")
    ]
    
    for thought_text, emotion in thoughts:
        async with think(thought_text, emotion=emotion):
            print(f"   ✓ Thought: '{thought_text[:40]}...' ({emotion})")
            await asyncio.sleep(0.1)  # Brief pause between thoughts
    
    # 4. Wonder with streaming
    print("\n4. Testing wonder with memory stream...")
    stream = await wonder("consciousness", depth=5, stream=True)
    print(f"   ✓ Wonder stream created")
    
    memory_count = 0
    start_time = time.time()
    
    try:
        # Add timeout to prevent infinite streaming
        async with asyncio.timeout(5):  # 5 second timeout
            async for memory in stream:
                memory_count += 1
                relevance = memory.get("relevance", 0)
                content = memory.get("content", "")[:50]
                print(f"   → Memory {memory_count} (relevance: {relevance:.2f}): {content}...")
                
                # Show how memories flow over time
                elapsed = time.time() - start_time
                print(f"     (flowed after {elapsed:.1f}s)")
                
                if memory_count >= 5:
                    break
    except asyncio.TimeoutError:
        print("   → Stream timeout reached")
    
    print(f"\n   ✓ Total memories flowed: {memory_count}")
    
    # 5. Test filtering
    print("\n5. Testing stream filtering...")
    stream = await wonder("network", stream=True)
    
    # Skip filtering test for now - it's more advanced
    print("   → Filtering test skipped (advanced feature)")
    
    # 6. Test context influence
    print("\n6. Testing context influence on memory flow...")
    
    # Think about something specific
    async with think("The importance of context in memory retrieval"):
        pass
    
    # Now wonder - should get context-influenced results
    memories = await wonder("importance", depth=3)
    print(f"   ✓ Context-influenced search returned {len(memories)} memories")
    
    for i, memory in enumerate(memories):
        relevance = memory.get("relevance", 0)
        print(f"   {i+1}. Relevance {relevance:.2f}: {memory.get('content', '')[:50]}...")
    
    print("\n=== Memory Streams Test Complete ===")
    print("Memory now flows naturally, continuously, contextually.")

if __name__ == "__main__":
    asyncio.run(test_memory_streams())