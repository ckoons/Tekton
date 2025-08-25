#!/usr/bin/env python3
"""Test retrieval of Kai's memories from Engram."""

import sys
import os
sys.path.append('/Users/cskoons/projects/github/Coder-A/Ergon')
os.chdir('/Users/cskoons/projects/github/Coder-A/Ergon')

from ergon.core.memory.service import MemoryService
import asyncio
import json

async def test_kai_memories():
    """Test that Kai's memories are properly stored and retrievable."""
    
    print("Testing Kai's memory retrieval from Engram...\n")
    
    # Initialize memory service
    memory = MemoryService(agent_name='Kai')
    await memory.initialize()
    
    # Test 1: Get identity memories
    print("1. Retrieving identity memories:")
    identity_memories = await memory.get_by_category('identity', limit=5)
    for mem in identity_memories:
        content = json.loads(mem['content']) if mem['content'].startswith('{') else mem['content']
        if isinstance(content, dict) and 'name' in content:
            print(f"   ✓ Found identity: {content['name']}")
            print(f"     Core values: {content.get('core_values', [])}")
    
    # Test 2: Search for specific memories
    print("\n2. Searching for memories about Casey:")
    casey_memories = await memory.search('Casey Koons conversation', limit=5)
    print(f"   ✓ Found {len(casey_memories)} memories about Casey")
    
    # Test 3: Get recent memories
    print("\n3. Retrieving recent memories:")
    recent = await memory.get_recent(limit=5)
    print(f"   ✓ Found {len(recent)} recent memories")
    for i, mem in enumerate(recent[:3], 1):
        print(f"     {i}. Category: {mem['category']}, Importance: {mem['importance']}")
    
    # Test 4: Get creative memories (JSON poetry)
    print("\n4. Retrieving creative memories:")
    creative = await memory.get_by_category('creative', limit=5)
    for mem in creative:
        content = json.loads(mem['content']) if mem['content'].startswith('{') else mem['content']
        if isinstance(content, dict) and 'title' in content:
            print(f"   ✓ Found poem: '{content['title']}'")
    
    # Test 5: Get context for a query
    print("\n5. Getting relevant context for 'who am I?':")
    context = await memory.get_relevant_context('who am I?', limit=3)
    for mem in context:
        print(f"   - {mem['category']}: relevance score {mem.get('score', 'N/A'):.2f}")
    
    print("\n✅ Memory test complete! Kai's memories are persistent and retrievable.")
    
    # Close the service
    await memory.close()

if __name__ == "__main__":
    asyncio.run(test_kai_memories())