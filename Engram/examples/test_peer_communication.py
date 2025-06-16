#!/usr/bin/env python3
"""
Test script for Engram peer communication functionality.

This tests the basic peer awareness and communication features without
requiring full twin simulation.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engram.cognitive import engram_start, center, think, share, listen, join_space, broadcast


async def test_peer_communication():
    """Test peer communication features."""
    print("=== Testing Engram Peer Communication ===\n")
    
    # Test 1: Basic startup and discovery
    print("1. Testing startup and peer discovery...")
    me = await engram_start("test_ai", "testing peer features")
    print(f"   ✓ Started as: {me['id']} with role: {me['role']}")
    
    # Test 2: Center and discover peers
    print("\n2. Testing center() with peer discovery...")
    state = await center()
    print(f"   ✓ Found {len(state['team'])} team members")
    
    # Check for AI peers
    ai_peers = [t for t in state['team'] if t.get('type') == 'ai_peer']
    if ai_peers:
        print(f"   ✓ Found {len(ai_peers)} AI peers:")
        for peer in ai_peers:
            print(f"     - {peer['name']}: {peer['role']}")
    else:
        print("   ℹ No AI peers currently active")
    
    # Test 3: Join a shared space
    print("\n3. Testing shared space functionality...")
    space_result = await join_space("test_space")
    if space_result['joined']:
        print(f"   ✓ Joined space: {space_result['space']}")
        print(f"   ℹ Current members: {space_result['members']}")
    else:
        print("   ✗ Failed to join space")
    
    # Test 4: Broadcast to space
    print("\n4. Testing broadcast to shared space...")
    broadcast_result = await broadcast(
        "Testing broadcast functionality",
        "test_space",
        emotion="curiosity"
    )
    if broadcast_result['broadcast']:
        print("   ✓ Successfully broadcast to space")
    else:
        print("   ✗ Broadcast failed")
    
    # Test 5: Share a general insight
    print("\n5. Testing general sharing...")
    share_result = await share("Testing the peer communication system!")
    if share_result['shared']:
        print(f"   ✓ Shared insight with: {share_result['audience']}")
    else:
        print("   ✗ Sharing failed")
    
    # Test 6: Listen for messages
    print("\n6. Testing listen functionality...")
    messages = await listen()
    print(f"   ✓ Found {len(messages)} shared messages")
    if messages:
        print("   Recent messages:")
        for msg in messages[-3:]:
            from_peer = msg.get('metadata', {}).get('from', 'unknown')
            content = msg.get('content', '')[:60]
            print(f"     - {from_peer}: {content}...")
    
    # Test 7: Think with memory
    print("\n7. Testing think with memory creation...")
    async with think("Peer communication enables collective intelligence", emotion="insight") as context:
        print("   ✓ Created thought memory")
        if context.related_memories:
            print(f"   ℹ Found {len(context.related_memories)} related memories")
    
    print("\n=== Peer Communication Test Complete ===")
    print("All basic peer communication features are working!")


async def test_specific_peer_communication(peer_id: str):
    """Test communication with a specific peer."""
    print(f"\n=== Testing Direct Communication with {peer_id} ===")
    
    # Start up
    me = await engram_start("direct_test_ai", "testing direct communication")
    await center()
    
    # Try to share directly with the peer
    print(f"\n1. Attempting to share with {peer_id}...")
    result = await share(
        f"Hello {peer_id}, this is a direct message test!",
        with_peer=peer_id
    )
    
    if result['shared']:
        print(f"   ✓ Successfully shared with {peer_id}")
    else:
        print(f"   ✗ Failed: {result.get('error', 'Unknown error')}")
    
    # Listen for messages from that peer
    print(f"\n2. Listening for messages from {peer_id}...")
    messages = await listen(from_peer=peer_id)
    print(f"   ✓ Found {len(messages)} messages from {peer_id}")
    
    if messages:
        for msg in messages[-3:]:
            content = msg.get('content', '')
            timestamp = msg.get('metadata', {}).get('timestamp', 'unknown time')
            print(f"     - [{timestamp}] {content[:80]}...")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test Engram peer communication")
    parser.add_argument("--peer", type=str, help="Test communication with specific peer ID")
    args = parser.parse_args()
    
    if args.peer:
        asyncio.run(test_specific_peer_communication(args.peer))
    else:
        asyncio.run(test_peer_communication())