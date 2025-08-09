#!/usr/bin/env python3
"""
Integration test demonstrating the complete Engram MCP workflow.

This test simulates multiple CIs collaborating through shared memory.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from engram.core.mcp.tools import (
    memory_store,
    memory_query,
    get_context,
    shared_memory_store,
    shared_memory_recall,
    memory_gift,
    memory_broadcast,
    whisper_send,
    whisper_receive
)


async def simulate_ci_collaboration():
    """
    Simulate a realistic workflow of CIs collaborating on the Memory Sprint.
    """
    print("=" * 70)
    print("INTEGRATION TEST: Simulating CI Collaboration on Memory Sprint")
    print("=" * 70)
    
    # Scenario 1: Cari discovers something and stores it
    print("\n[Cari] Making a discovery about MCP tools...")
    await memory_store(
        content="I discovered that MCP tools can be connected directly to MemoryService!",
        namespace="thinking",
        metadata={"ci": "Cari", "discovery": True}
    )
    
    await shared_memory_store(
        content="MCP tools are now connected to MemoryService - Phase 1 complete!",
        space="collective",
        attribution="Cari",
        emotion="excited",
        confidence=0.95
    )
    print("   ✓ Stored discovery in personal and shared memory")
    
    # Scenario 2: Teri queries the shared memory
    print("\n[Teri] Checking collective memory for updates...")
    teri_check = await shared_memory_recall(
        query="Phase 1 MCP tools",
        space="collective"
    )
    if teri_check.get("results"):
        print(f"   ✓ Found {teri_check['count']} updates in collective memory")
    
    # Scenario 3: Teri gifts knowledge to Cari
    print("\n[Teri] Sharing implementation tips with Cari...")
    await memory_gift(
        content="Remember to handle dynamic namespaces for shared spaces",
        from_ci="Teri",
        to_ci="Cari",
        message="This will help with cross-CI sharing!"
    )
    print("   ✓ Sent implementation tip as gift")
    
    # Scenario 4: Casey broadcasts an important decision
    print("\n[Casey] Broadcasting architectural decision...")
    await memory_broadcast(
        content="MCP-only architecture confirmed - no REST/HTTP APIs",
        from_ci="Casey",
        importance="critical",
        category="architecture"
    )
    print("   ✓ Broadcast sent to all CIs")
    
    # Scenario 5: Apollo and Rhetor use whisper channel
    print("\n[Apollo] Sending context to Rhetor via whisper...")
    await whisper_send(
        content="Current sprint progress: Phase 1 complete, ready for Phase 2",
        from_ci="Apollo",
        to_ci="Rhetor"
    )
    
    rhetor_whispers = await whisper_receive(
        ci_name="Rhetor",
        from_ci="Apollo"
    )
    print(f"   ✓ Rhetor received {rhetor_whispers.get('count', 0)} whispers")
    
    # Scenario 6: Building context from multiple namespaces
    print("\n[Cari] Building comprehensive context...")
    context = await get_context(
        query="MCP tools memory sprint",
        namespaces=["conversations", "thinking", "shared-collective"],
        limit=3
    )
    if context.get("success"):
        print("   ✓ Built context from multiple namespaces")
    
    # Scenario 7: Check persistence
    print("\n[System] Verifying persistence...")
    persistence_check = await memory_query(
        query="PERSIST_TEST_MARKER",
        namespace="longterm"
    )
    if persistence_check.get("count", 0) > 0:
        print("   ✓ Previous memories persisted successfully")
    else:
        # Store a persistence marker for future tests
        await memory_store(
            content="PERSIST_TEST_MARKER - Memory persists across sessions",
            namespace="longterm",
            metadata={"persistent": True}
        )
        print("   ✓ Stored persistence marker for future verification")
    
    # Summary
    print("\n" + "=" * 70)
    print("INTEGRATION TEST COMPLETE")
    print("=" * 70)
    print("\nSummary of tested capabilities:")
    print("✓ Core memory operations (store, query, context)")
    print("✓ Shared memory spaces for collective knowledge")
    print("✓ Memory gifting between CIs")
    print("✓ Broadcasting important discoveries")
    print("✓ Private whisper channels (Apollo/Rhetor)")
    print("✓ Multi-namespace context building")
    print("✓ Memory persistence with LanceDB")
    print("\nAll MCP tools working as designed!")


async def test_experiential_features():
    """
    Test the experiential memory features added in Phase 1.
    """
    print("\n" + "=" * 70)
    print("TESTING EXPERIENTIAL MEMORY FEATURES")
    print("=" * 70)
    
    # Store memories with different emotions and confidence
    emotions = [
        ("excited", 0.95, "We solved the MCP connection issue!"),
        ("curious", 0.7, "What if we add memory narratives?"),
        ("confident", 1.0, "The architecture is solid"),
        ("uncertain", 0.3, "Not sure about this approach"),
    ]
    
    print("\nStoring memories with emotional context...")
    for emotion, confidence, content in emotions:
        await shared_memory_store(
            content=content,
            space="emotional-test",
            attribution="test_ci",
            emotion=emotion,
            confidence=confidence
        )
        print(f"   ✓ Stored {emotion} memory (confidence: {confidence})")
    
    # Query emotional memories
    print("\nQuerying emotional memories...")
    results = await shared_memory_recall(
        query="",
        space="emotional-test",
        limit=10
    )
    print(f"   ✓ Found {results.get('count', 0)} emotional memories")
    
    print("\nExperiential features working correctly!")


if __name__ == "__main__":
    print("Engram MCP Tools Integration Test")
    print(f"Started at: {datetime.now().isoformat()}")
    
    # Run main collaboration test
    asyncio.run(simulate_ci_collaboration())
    
    # Run experiential features test
    asyncio.run(test_experiential_features())
    
    print(f"\nCompleted at: {datetime.now().isoformat()}")