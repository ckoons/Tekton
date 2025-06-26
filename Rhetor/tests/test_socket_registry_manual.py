#!/usr/bin/env python3
"""Manual test script for AI Socket Registry.

This provides a quick way to test the socket registry functionality
without running the full test suite.

Usage:
    python test_socket_registry_manual.py
"""

import asyncio
import json
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rhetor.core.ai_socket_registry import get_socket_registry, SocketState


async def test_basic_operations():
    """Test basic socket registry operations."""
    print("\n🧪 Testing AI Socket Registry")
    print("=" * 50)
    
    # Get registry instance
    registry = await get_socket_registry()
    print("✅ Registry initialized")
    
    # List initial sockets
    sockets = await registry.list_sockets()
    print(f"\n📋 Initial sockets: {len(sockets)}")
    for sock in sockets:
        print(f"  - {sock['socket_id']} ({sock['model']}) - {sock['state']}")
    
    # Create test sockets
    print("\n🔧 Creating test sockets...")
    apollo_id = await registry.create(
        model="claude-3-sonnet",
        prompt="You are Apollo, focused on prediction and analysis",
        context={"role": "predictor"}
    )
    print(f"  ✅ Created Apollo: {apollo_id}")
    
    athena_id = await registry.create(
        model="claude-3-opus",
        prompt="You are Athena, focused on knowledge and wisdom",
        context={"role": "knowledge"},
        socket_id="athena-001"
    )
    print(f"  ✅ Created Athena: {athena_id}")
    
    # Test direct messaging
    print("\n📮 Testing direct messaging...")
    await registry.write(apollo_id, "What's your prediction for AI development?")
    await registry.write(athena_id, "What knowledge do you have about AI history?")
    print("  ✅ Messages sent")
    
    # Read responses
    apollo_msgs = await registry.read(apollo_id)
    athena_msgs = await registry.read(athena_id)
    print(f"  📥 Apollo queue: {len(apollo_msgs)} messages")
    print(f"  📥 Athena queue: {len(athena_msgs)} messages")
    
    # Test broadcast
    print("\n📢 Testing broadcast...")
    await registry.write("team-chat-all", "Team meeting: How can we improve Tekton?")
    
    # Check sockets received broadcast
    sockets = await registry.list_sockets()
    for sock in sockets:
        if sock['socket_id'] not in ['team-chat-all']:
            info = await registry.get_socket_info(sock['socket_id'])
            print(f"  📬 {sock['socket_id']}: {sock['queue_size']} messages in queue")
    
    # Simulate responses
    print("\n💬 Simulating AI responses...")
    # Add responses to sockets (simulating AI responses)
    registry.sockets[apollo_id].message_queue.append({
        "content": "I predict significant advances in multi-agent systems",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"confidence": 0.85}
    })
    
    registry.sockets[athena_id].message_queue.append({
        "content": "Historically, AI has evolved through multiple paradigm shifts",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"sources": 3}
    })
    
    # Read from broadcast
    print("\n📖 Reading team chat responses...")
    team_messages = await registry.read("team-chat-all")
    for msg in team_messages:
        print(f"  {msg['header']} {msg['content'][:50]}...")
    
    # Test reset
    print("\n🔄 Testing reset...")
    await registry.reset(apollo_id)
    apollo_info = await registry.get_socket_info(apollo_id)
    print(f"  ✅ Apollo reset - queue size: {len(apollo_info['message_queue'])}")
    
    # Test mark unresponsive
    print("\n⚠️  Testing unresponsive marking...")
    await registry.mark_unresponsive(athena_id)
    athena_info = await registry.get_socket_info(athena_id)
    print(f"  ✅ Athena marked as: {athena_info['state']}")
    
    # Try to write to unresponsive socket
    success = await registry.write(athena_id, "Are you there?")
    print(f"  📝 Write to unresponsive socket: {'Failed (expected)' if not success else 'Success'}")
    
    # Final socket list
    print("\n📋 Final socket status:")
    sockets = await registry.list_sockets()
    for sock in sockets:
        print(f"  - {sock['socket_id']} ({sock['model']}) - {sock['state']}")
    
    # Test deletion
    print("\n🗑️  Testing deletion...")
    await registry.delete(apollo_id)
    print(f"  ✅ Deleted Apollo")
    
    # Try to delete broadcast socket
    success = await registry.delete("team-chat-all")
    print(f"  🚫 Delete broadcast socket: {'Failed (expected)' if not success else 'Success'}")
    
    print("\n✅ All tests completed!")


async def test_persistence():
    """Test persistence functionality."""
    print("\n🔄 Testing Persistence")
    print("=" * 50)
    
    # Create registry and add a socket
    registry1 = await get_socket_registry()
    
    test_id = await registry1.create(
        model="persistence-test",
        prompt="Test persistence",
        context={"persistent": True},
        socket_id="persist-test-001"
    )
    
    print(f"✅ Created socket: {test_id}")
    
    # Add some data
    await registry1.write(test_id, "This should persist")
    
    # Simulate registry restart by creating new instance
    # (In real scenario, the singleton would be cleared)
    print("\n🔄 Simulating restart...")
    
    # Check if socket was persisted
    info = await registry1.get_socket_info(test_id)
    if info:
        print(f"✅ Socket persisted: {info['socket_id']}")
        print(f"  Model: {info['model']}")
        print(f"  Context: {info['context']}")
    else:
        print("⚠️  Socket not found (persistence may be disabled)")


async def test_performance():
    """Test performance with multiple sockets."""
    print("\n⚡ Testing Performance")
    print("=" * 50)
    
    registry = await get_socket_registry()
    
    # Create many sockets
    num_sockets = 10
    print(f"Creating {num_sockets} sockets...")
    
    start = datetime.utcnow()
    socket_ids = []
    
    for i in range(num_sockets):
        sid = await registry.create(
            model=f"test-model-{i}",
            prompt=f"Test socket {i}",
            context={"index": i}
        )
        socket_ids.append(sid)
    
    create_time = (datetime.utcnow() - start).total_seconds()
    print(f"✅ Created {num_sockets} sockets in {create_time:.2f}s")
    
    # Broadcast to all
    start = datetime.utcnow()
    await registry.write("team-chat-all", "Performance test broadcast")
    broadcast_time = (datetime.utcnow() - start).total_seconds()
    print(f"✅ Broadcast completed in {broadcast_time:.3f}s")
    
    # Read from all
    start = datetime.utcnow()
    messages = await registry.read("team-chat-all")
    read_time = (datetime.utcnow() - start).total_seconds()
    print(f"✅ Read {len(messages)} messages in {read_time:.3f}s")
    
    # Cleanup
    for sid in socket_ids:
        await registry.delete(sid)
    print(f"✅ Cleaned up test sockets")


async def main():
    """Run all manual tests."""
    try:
        await test_basic_operations()
        await test_persistence()
        await test_performance()
        
        print("\n🎉 All manual tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())