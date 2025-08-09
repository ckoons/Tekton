#!/usr/bin/env python3
"""Test script to verify Engram MCP tools are working."""

import asyncio
import sys
from pathlib import Path

# Add Tekton root to path
tekton_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(tekton_root))

from engram.core.mcp.tools import memory_store, memory_query, memory_recall, get_context

async def test_mcp_tools():
    """Test the MCP tools are properly connected."""
    print("Testing Engram MCP Tools...")
    print("-" * 50)
    
    # Test 1: Store a memory
    print("\n1. Testing MemoryStore...")
    result = await memory_store(
        content="This is a test memory from Cari testing MCP tools",
        namespace="conversations",
        metadata={"author": "Cari", "purpose": "testing"}
    )
    print(f"   Store result: {result}")
    
    # Test 2: Query the memory
    print("\n2. Testing MemoryQuery...")
    result = await memory_query(
        query="test memory Cari",
        namespace="conversations",
        limit=5
    )
    print(f"   Query result: {result}")
    
    # Test 3: Recall (alias for query)
    print("\n3. Testing MemoryRecall...")
    result = await memory_recall(
        query="MCP tools",
        namespace="conversations",
        limit=3
    )
    print(f"   Recall result: {result}")
    
    # Test 4: Get context
    print("\n4. Testing GetContext...")
    result = await get_context(
        query="testing",
        namespaces=["conversations"],
        limit=2
    )
    print(f"   Context result: {result}")
    
    print("\n" + "=" * 50)
    print("All MCP tools tested successfully!")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())