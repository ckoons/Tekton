#!/usr/bin/env python3
"""Test memory persistence across restarts."""

import asyncio
import sys
from pathlib import Path

# Add Tekton root to path
tekton_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(tekton_root))

from engram.core.mcp.tools import memory_store, memory_query

async def test_persistence():
    """Test if memories persist."""
    
    # Store a unique memory
    print("Storing test memory with unique ID...")
    result = await memory_store(
        content="PERSISTENCE_TEST_12345: This memory should survive restarts",
        namespace="longterm",
        metadata={"test": "persistence", "id": "12345"}
    )
    print(f"Store result: {result}")
    
    # Query it back
    print("\nQuerying for the memory...")
    result = await memory_query(
        query="PERSISTENCE_TEST_12345",
        namespace="longterm"
    )
    print(f"Found {result.get('count', 0)} memories")
    if result.get('results'):
        print(f"Memory content: {result['results'][0]['content']}")

if __name__ == "__main__":
    asyncio.run(test_persistence())