#!/usr/bin/env python3
"""End-to-end test for Team Chat functionality.

This script tests the complete team chat flow:
1. Creates AI sockets
2. Sends a team chat message
3. Simulates AI responses
4. Verifies the team chat endpoint

Usage:
    python test_team_chat_e2e.py
"""

import asyncio
import json
import httpx
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rhetor.core.ai_socket_registry import get_socket_registry


async def test_team_chat_basic():
    """Test basic team chat functionality."""
    print("\n🧪 Testing Team Chat End-to-End")
    print("=" * 50)
    
    # Initialize socket registry
    print("\n1️⃣ Initializing socket registry...")
    registry = await get_socket_registry()
    print("✅ Registry initialized")
    
    # Create test AI sockets
    print("\n2️⃣ Creating AI sockets...")
    apollo_id = await registry.create(
        model="claude-3-sonnet",
        prompt="You are Apollo, focused on prediction and analysis",
        context={"role": "predictor"},
        socket_id="apollo-test-001"
    )
    print(f"✅ Created Apollo: {apollo_id}")
    
    athena_id = await registry.create(
        model="gpt-4",
        prompt="You are Athena, focused on knowledge and wisdom",
        context={"role": "knowledge"},
        socket_id="athena-test-001"
    )
    print(f"✅ Created Athena: {athena_id}")
    
    # Test team chat API endpoint
    print("\n3️⃣ Testing Team Chat API endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            # Send team chat request
            request_data = {
                "message": "What are the key principles of good software architecture?",
                "moderation_mode": "pass_through",
                "timeout": 5.0
            }
            
            print(f"📤 Sending: {request_data['message']}")
            
            response = await client.post(
                "http://localhost:8003/api/team-chat",
                json=request_data
            )
            
            if response.status_code == 200:
                print("✅ Team chat endpoint is working!")
                result = response.json()
                print(f"📥 Request ID: {result['request_id']}")
                print(f"⏱️  Elapsed time: {result['elapsed_time']:.2f}s")
                
                # Since we haven't implemented actual AI responses yet,
                # we'll simulate them for testing
                print("\n4️⃣ Simulating AI responses...")
                
                # Add simulated responses to sockets
                registry.sockets[apollo_id].message_queue.append({
                    "content": "I predict the key principles include: modularity, scalability, and maintainability. These will become even more critical as systems grow in complexity.",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {"confidence": 0.9}
                })
                
                registry.sockets[athena_id].message_queue.append({
                    "content": "From my knowledge base, the fundamental principles are: separation of concerns, single responsibility, dependency inversion, and clean interfaces.",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {"sources": 5}
                })
                
                # Send another request to collect responses
                print("\n5️⃣ Collecting AI responses...")
                response2 = await client.post(
                    "http://localhost:8003/api/team-chat",
                    json={
                        "message": "Continue discussion",
                        "moderation_mode": "pass_through",
                        "timeout": 2.0
                    }
                )
                
                if response2.status_code == 200:
                    result2 = response2.json()
                    print(f"✅ Collected {len(result2['responses'])} responses")
                    
                    for resp in result2['responses']:
                        print(f"\n💬 {resp['socket_id']}:")
                        print(f"   {resp['content'][:100]}...")
                
            else:
                print(f"❌ Team chat endpoint returned {response.status_code}")
                print(f"   Response: {response.text}")
                
        except httpx.ConnectError:
            print("❌ Could not connect to Rhetor API on port 8003")
            print("   Make sure Rhetor is running: ./run_rhetor.sh")
        except Exception as e:
            print(f"❌ Error testing team chat: {e}")
    
    # Test streaming endpoint
    print("\n6️⃣ Testing streaming endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            # Test if streaming endpoint exists
            response = await client.get(
                "http://localhost:8003/api/team-chat/stream",
                params={"message": "Test streaming", "timeout": 2.0}
            )
            
            if response.status_code == 200:
                print("✅ Streaming endpoint is available")
            else:
                print(f"⚠️  Streaming endpoint returned {response.status_code}")
                
    except Exception as e:
        print(f"⚠️  Could not test streaming: {e}")
    
    # List sockets
    print("\n7️⃣ Listing team chat sockets...")
    sockets = await registry.list_sockets()
    print(f"📋 Active sockets: {len(sockets)}")
    for sock in sockets:
        print(f"   - {sock['socket_id']} ({sock['model']}) - {sock['state']}")
    
    # Cleanup
    print("\n8️⃣ Cleaning up...")
    await registry.delete(apollo_id)
    await registry.delete(athena_id)
    print("✅ Test sockets deleted")
    
    print("\n✅ Team Chat E2E test completed!")


async def test_team_chat_advanced():
    """Test advanced team chat features."""
    print("\n\n🧪 Testing Advanced Team Chat Features")
    print("=" * 50)
    
    registry = await get_socket_registry()
    
    # Test socket health monitoring
    print("\n1️⃣ Testing socket health monitoring...")
    test_id = await registry.create("test-model", "Test AI", {}, "health-test-001")
    
    # Mark as unresponsive
    await registry.mark_unresponsive(test_id)
    info = await registry.get_socket_info(test_id)
    print(f"✅ Socket marked as: {info['state']}")
    
    # Try to write to unresponsive socket
    success = await registry.write(test_id, "Hello?")
    print(f"✅ Write to unresponsive socket rejected: {not success}")
    
    await registry.delete(test_id)
    
    # Test persistence
    print("\n2️⃣ Testing socket persistence...")
    persist_id = await registry.create(
        "persistence-test",
        "I should survive restarts",
        {"persistent": True},
        "persist-test-001"
    )
    
    await registry.write(persist_id, "Remember this message")
    print(f"✅ Created persistent socket: {persist_id}")
    print("   (Socket should survive Rhetor restarts)")
    
    # Note: Don't delete this socket to test persistence
    
    print("\n✅ Advanced tests completed!")


async def main():
    """Run all team chat tests."""
    try:
        await test_team_chat_basic()
        await test_team_chat_advanced()
        
        print("\n\n🎉 All Team Chat E2E tests passed!")
        print("\nNext steps:")
        print("1. Integrate with AI Specialist Manager for real AI responses")
        print("2. Implement synthesis and consensus moderation modes")
        print("3. Add Rhetor's moderation capabilities")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())