"""
Test script for AI Specialist functionality.

This script tests the basic AI specialist features including:
- Specialist creation and activation
- AI-to-AI messaging
- Team chat orchestration
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
RHETOR_URL = "http://localhost:8003"
RHETOR_WS_URL = "ws://localhost:8003/ws"

async def test_list_specialists():
    """Test listing AI specialists."""
    print("\n=== Testing List Specialists ===")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{RHETOR_URL}/api/ai/specialists") as response:
            data = await response.json()
            print(f"Total specialists: {data['count']}")
            for specialist in data['specialists']:
                print(f"- {specialist['id']}: {specialist['type']} ({specialist['status']})")
            return data['specialists']

async def test_activate_specialist(specialist_id: str):
    """Test activating a specialist."""
    print(f"\n=== Testing Activate Specialist: {specialist_id} ===")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{RHETOR_URL}/api/ai/specialists/{specialist_id}/activate") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ Specialist {specialist_id} activated: {data}")
                return True
            else:
                print(f"✗ Failed to activate specialist: {response.status}")
                return False

async def test_specialist_message(specialist_id: str, message: str):
    """Test sending a message to a specialist."""
    print(f"\n=== Testing Message to {specialist_id} ===")
    
    payload = {
        "specialist_id": specialist_id,
        "message": message,
        "context_id": "test-context",
        "task_type": "chat"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{RHETOR_URL}/api/ai/specialists/{specialist_id}/message",
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ Response received: {data.get('message', 'No message in response')[:100]}...")
                return data
            else:
                print(f"✗ Failed to send message: {response.status}")
                error = await response.text()
                print(f"Error: {error}")
                return None

async def test_websocket_specialist_chat():
    """Test WebSocket communication with AI specialist."""
    print("\n=== Testing WebSocket AI Specialist Chat ===")
    
    import websockets
    
    try:
        async with websockets.connect(RHETOR_WS_URL) as websocket:
            # Send AI specialist request
            request = {
                "type": "AI_SPECIALIST_REQUEST",
                "source": "TEST",
                "payload": {
                    "specialist_id": "rhetor-orchestrator",
                    "message": "Hello Rhetor, what is your role in the Tekton ecosystem?",
                    "context": "test-ws-context",
                    "streaming": False
                }
            }
            
            await websocket.send(json.dumps(request))
            print("✓ Sent AI specialist request via WebSocket")
            
            # Wait for response
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✓ Received response: {data['type']}")
            
            if data['type'] == 'AI_SPECIALIST_RESPONSE':
                print(f"Specialist response: {data['payload'].get('message', 'No message')[:100]}...")
            
            return data
            
    except Exception as e:
        print(f"✗ WebSocket error: {e}")
        return None

async def test_team_chat():
    """Test team chat orchestration."""
    print("\n=== Testing Team Chat ===")
    
    payload = {
        "topic": "Planning Tekton's AI integration strategy",
        "specialists": ["rhetor-orchestrator", "engram-memory"],
        "initial_prompt": "How should we approach integrating AI specialists into Tekton?",
        "max_rounds": 2
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{RHETOR_URL}/api/ai/team-chat", json=payload) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ Team chat completed with {data['message_count']} messages")
                
                for i, msg in enumerate(data['messages']):
                    print(f"\nMessage {i+1} from {msg['sender']}:")
                    print(f"  {msg['content'][:150]}...")
                    
                return data
            else:
                print(f"✗ Failed to run team chat: {response.status}")
                return None

async def test_status_with_ai_specialists():
    """Test status endpoint with AI specialist information."""
    print("\n=== Testing Status with AI Specialists ===")
    
    import websockets
    
    try:
        async with websockets.connect(RHETOR_WS_URL) as websocket:
            # Send status request
            request = {
                "type": "STATUS",
                "source": "TEST"
            }
            
            await websocket.send(json.dumps(request))
            print("✓ Sent STATUS request")
            
            # Wait for response
            response = await websocket.recv()
            data = json.loads(response)
            
            if data['type'] == 'RESPONSE' and data['payload'].get('status') == 'ok':
                payload = data['payload']
                print(f"✓ Rhetor status: {payload['message']}")
                
                # Check AI specialists
                if 'ai_specialists' in payload:
                    ai_status = payload['ai_specialists']
                    print(f"✓ Active AI specialists: {ai_status.get('active_count', 0)}")
                    
                    for specialist in ai_status.get('specialists', []):
                        print(f"  - {specialist['id']}: {specialist['status']}")
                        
                return payload
            else:
                print("✗ Unexpected status response")
                return None
                
    except Exception as e:
        print(f"✗ WebSocket error: {e}")
        return None

async def main():
    """Run all tests."""
    print("=" * 60)
    print("AI Specialist Integration Tests")
    print("=" * 60)
    print(f"Testing against: {RHETOR_URL}")
    print(f"Started at: {datetime.now().isoformat()}")
    
    # Give Rhetor time to initialize
    print("\nWaiting for Rhetor to initialize...")
    await asyncio.sleep(2)
    
    try:
        # Test 1: List specialists
        specialists = await test_list_specialists()
        
        # Test 2: Check status via WebSocket
        await test_status_with_ai_specialists()
        
        # Test 3: Activate core specialists
        for specialist_id in ["rhetor-orchestrator", "engram-memory"]:
            await test_activate_specialist(specialist_id)
            await asyncio.sleep(1)  # Give time between activations
        
        # Test 4: Send message to specialist (Note: This will use simulated responses for now)
        await test_specialist_message(
            "rhetor-orchestrator",
            "What is your role in managing AI specialists?"
        )
        
        # Test 5: WebSocket specialist chat
        await test_websocket_specialist_chat()
        
        # Test 6: Team chat (Note: This will use simulated responses for now)
        await test_team_chat()
        
        print("\n" + "=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test suite error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())