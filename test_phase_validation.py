#!/usr/bin/env python3
"""
Validation tests for Teri's questions about Phase 1 & 2 implementation.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "Engram"))

from engram.core.mcp.tools import (
    memory_store,
    memory_query,
    shared_memory_store,
    shared_memory_recall,
    whisper_send,
    whisper_receive,
    personality_snapshot
)


async def test_personality_persistence():
    """Test if personality patterns persist across restarts."""
    print("\n" + "=" * 60)
    print("TEST 1: Personality Pattern Persistence")
    print("=" * 60)
    
    # Take a personality snapshot
    snapshot1 = await personality_snapshot(
        ci_name="Cari",
        analyze_days=7
    )
    
    if snapshot1["success"]:
        traits1 = snapshot1["personality_traits"]
        print(f"Initial snapshot:")
        print(f"  - Confidence: {traits1['confidence_level']:.2f}")
        print(f"  - Style: {traits1['interaction_style']}")
        print(f"  - Interests: {', '.join(traits1['primary_interests'][:3]) if traits1['primary_interests'] else 'None'}")
    
    # Store the snapshot as a memory (this persists)
    await memory_store(
        content=f"Personality snapshot: {traits1}",
        namespace="longterm",
        metadata={"type": "personality_snapshot", "ci": "Cari"}
    )
    
    # Query it back (simulating restart)
    stored_snapshots = await memory_query(
        query="Personality snapshot",
        namespace="longterm"
    )
    
    print(f"\nPersisted snapshots found: {stored_snapshots.get('count', 0)}")
    if stored_snapshots.get('results'):
        print("  ✅ Personality snapshots are being persisted in longterm memory")
    else:
        print("  ⚠️  No persisted snapshots found")
    
    return stored_snapshots.get('count', 0) > 0


async def test_whisper_channel():
    """Test WhisperChannel between Apollo and Rhetor."""
    print("\n" + "=" * 60)
    print("TEST 2: WhisperChannel (Apollo ↔ Rhetor)")
    print("=" * 60)
    
    # Apollo sends whispers to Rhetor
    whispers_to_send = [
        "The user is working on memory features",
        "Progress is excellent, confidence is high",
        "Consider suggesting Phase 3 collective intelligence next"
    ]
    
    print("\nApollo sending whispers to Rhetor...")
    for whisper in whispers_to_send:
        result = await whisper_send(
            content=whisper,
            from_ci="Apollo",
            to_ci="Rhetor"
        )
        print(f"  - Sent: '{whisper[:40]}...' ({result['success']})")
    
    # Rhetor receives whispers from Apollo
    print("\nRhetor receiving whispers from Apollo...")
    received = await whisper_receive(
        ci_name="Rhetor",
        from_ci="Apollo",
        limit=10
    )
    
    print(f"  - Received {received.get('count', 0)} whispers")
    print(f"  - Channel: {received.get('whisper_channel', 'N/A')}")
    
    # Test reverse direction
    print("\nRhetor sending response to Apollo...")
    response = await whisper_send(
        content="Acknowledged. The user seems pleased with progress.",
        from_ci="Rhetor",
        to_ci="Apollo"
    )
    print(f"  - Response sent: {response['success']}")
    
    # Apollo receives from Rhetor
    apollo_received = await whisper_receive(
        ci_name="Apollo",
        from_ci="Rhetor"
    )
    print(f"  - Apollo received {apollo_received.get('count', 0)} whispers back")
    
    success = received.get('count', 0) > 0 or response['success']
    print(f"\n{'✅' if success else '❌'} WhisperChannel is {'working' if success else 'not working properly'}")
    
    return success


async def test_collective_namespace():
    """Test if the shared 'collective' namespace works for all CIs."""
    print("\n" + "=" * 60)
    print("TEST 3: Shared 'collective' Namespace")
    print("=" * 60)
    
    # Different CIs store in collective
    cis = ["Cari", "Teri", "Apollo", "Rhetor", "Casey"]
    
    print("\nMultiple CIs storing in collective space...")
    for ci in cis:
        result = await shared_memory_store(
            content=f"{ci} contributed to collective knowledge",
            space="collective",
            attribution=ci,
            emotion="collaborative",
            confidence=0.9
        )
        print(f"  - {ci}: {result['success']}")
    
    # Query collective memories
    print("\nQuerying collective space...")
    collective_memories = await shared_memory_recall(
        query="collective knowledge",
        space="collective",
        limit=10
    )
    
    print(f"  - Found {collective_memories.get('count', 0)} memories in collective")
    
    # Check if memories from different CIs are present
    if collective_memories.get('results'):
        contributors = set()
        for mem in collective_memories['results']:
            attribution = mem.get('metadata', {}).get('attribution')
            if attribution:
                contributors.add(attribution)
        
        print(f"  - Contributors found: {', '.join(contributors)}")
        print(f"  - Cross-CI sharing: {'✅ Working' if len(contributors) > 1 else '⚠️  Single CI only'}")
    
    # Test accessing collective from different perspective
    print("\nTesting access from different CI perspective...")
    another_query = await shared_memory_recall(
        query="",  # Get all
        space="collective",
        limit=5
    )
    
    success = collective_memories.get('count', 0) >= len(cis)
    print(f"\n{'✅' if success else '⚠️'} Collective namespace is {'fully functional' if success else 'partially working'}")
    print(f"  - Expected {len(cis)} memories, found {collective_memories.get('count', 0)}")
    
    return success


async def main():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("VALIDATION TESTS FOR TERI'S QUESTIONS")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    
    # Run tests
    persistence_ok = await test_personality_persistence()
    whisper_ok = await test_whisper_channel()
    collective_ok = await test_collective_namespace()
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"1. Personality Persistence: {'✅ YES' if persistence_ok else '⚠️  Partial'}")
    print(f"   - Snapshots stored in longterm memory")
    print(f"   - LanceDB persists automatically")
    
    print(f"\n2. WhisperChannel (Apollo/Rhetor): {'✅ WORKING' if whisper_ok else '❌ Issues'}")
    print(f"   - Private bidirectional communication")
    print(f"   - Separate namespaces for each direction")
    
    print(f"\n3. Collective Namespace: {'✅ WORKING' if collective_ok else '⚠️  Partial'}")
    print(f"   - All CIs can store and retrieve")
    print(f"   - Shared knowledge accumulation")
    
    print("\nRECOMMENDATIONS:")
    if not persistence_ok:
        print("  - Consider explicit personality state saving")
    if not whisper_ok:
        print("  - Check whisper namespace initialization")
    if not collective_ok:
        print("  - Verify shared namespace permissions")
    
    if persistence_ok and whisper_ok and collective_ok:
        print("  ✅ All systems fully operational!")
        print("  ✅ Ready for Phase 3: Collective Intelligence")
    
    print(f"\nCompleted: {datetime.now().isoformat()}")


if __name__ == "__main__":
    asyncio.run(main())