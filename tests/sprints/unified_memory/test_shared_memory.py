#!/usr/bin/env python3
"""Test cross-CI memory sharing tools."""

import asyncio
import sys
from pathlib import Path

# Add Tekton root to path
tekton_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(tekton_root))

from engram.core.mcp.tools import (
    shared_memory_store, 
    shared_memory_recall,
    memory_gift,
    memory_broadcast,
    whisper_send,
    whisper_receive
)

async def test_shared_memory():
    """Test the cross-CI memory sharing tools."""
    print("Testing Cross-CI Memory Sharing Tools...")
    print("=" * 60)
    
    # Test 1: SharedMemoryStore
    print("\n1. Testing SharedMemoryStore...")
    result = await shared_memory_store(
        content="Cari discovered that MCP tools are now working!",
        space="collective",
        attribution="Cari",
        emotion="excited",
        confidence=0.95
    )
    print(f"   Result: {result}")
    
    # Test 2: SharedMemoryRecall
    print("\n2. Testing SharedMemoryRecall...")
    result = await shared_memory_recall(
        query="MCP tools",
        space="collective",
        limit=3
    )
    print(f"   Found {result.get('count', 0)} shared memories")
    
    # Test 3: MemoryGift
    print("\n3. Testing MemoryGift...")
    result = await memory_gift(
        content="Here's how to connect MCP tools to MemoryService",
        from_ci="Cari",
        to_ci="Teri",
        message="Thanks for the guidance!"
    )
    print(f"   Result: {result}")
    
    # Test 4: MemoryBroadcast
    print("\n4. Testing MemoryBroadcast...")
    result = await memory_broadcast(
        content="Phase 1 of Unified Memory Sprint is complete!",
        from_ci="Cari",
        importance="high",
        category="milestone"
    )
    print(f"   Result: {result}")
    
    # Test 5: WhisperSend
    print("\n5. Testing WhisperSend (for Apollo/Rhetor)...")
    result = await whisper_send(
        content="Private context about the current sprint progress",
        from_ci="Apollo",
        to_ci="Rhetor"
    )
    print(f"   Result: {result}")
    
    # Test 6: WhisperReceive
    print("\n6. Testing WhisperReceive...")
    result = await whisper_receive(
        ci_name="Rhetor",
        from_ci="Apollo",
        limit=5
    )
    print(f"   Found {result.get('count', 0)} whispers")
    
    print("\n" + "=" * 60)
    print("All cross-CI memory sharing tools tested successfully!")

if __name__ == "__main__":
    asyncio.run(test_shared_memory())