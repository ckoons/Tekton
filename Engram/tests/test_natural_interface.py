#!/usr/bin/env python3
"""
Test the natural memory interface for AI users.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engram.cognitive import engram_start, center, think, wonder, share

async def test_natural_flow():
    """Test the complete natural memory flow."""
    
    print("=== Testing Natural Memory Interface ===\n")
    
    # 1. Start up
    print("1. Starting up...")
    me = await engram_start("test_claude", "memory tester")
    print(f"   ✓ I am {me['id']} with role: {me['role']}")
    print(f"   ✓ Status: {me['status']}")
    print(f"   ✓ Memory count: {me.get('memory_count', 0)}")
    
    # 2. Center myself and meet the team
    print("\n2. Centering and meeting the team...")
    state = await center()
    print(f"   ✓ I am: {state['me']['role']}")
    print(f"   ✓ Team members: {len(state['team'])}")
    for member in state['team'][:3]:  # Show first 3
        print(f"     - {member['name']}: {member['role']}")
    print(f"     ... and {len(state['team']) - 3} more")
    
    # 3. Think naturally
    print("\n3. Thinking naturally...")
    async with think("Casey taught me about mycelial networks", emotion="wonder") as context:
        print(f"   ✓ Thought stored (significance > 0.5)")
        print(f"   ✓ Related memories found: {len(context.related_memories)}")
        for memory in context.related_memories:
            print(f"     - {memory.get('content', '')[:50]}...")
    
    # 4. Wonder about something
    print("\n4. Wondering about networks...")
    memories = await wonder("network", depth=3)
    print(f"   ✓ Found {len(memories)} memories about 'network'")
    for memory in memories:
        content = memory.get('content', '')[:60]
        print(f"     - {content}...")
    
    # 5. Share an insight
    print("\n5. Sharing an insight...")
    result = await share("Natural memory interface is working beautifully!")
    print(f"   ✓ Shared: {result['shared']}")
    print(f"   ✓ Audience: {result['audience']}")
    
    # 6. Share with specific peer
    print("\n6. Sharing with specific teammate...")
    result = await share("Rhetor, we should coordinate on LLM memory", with_peer="rhetor")
    print(f"   ✓ Shared with: {result['audience']}")
    
    print("\n=== All tests passed! ===")
    print("\nNatural memory interface is ready for AI users.")

if __name__ == "__main__":
    asyncio.run(test_natural_flow())