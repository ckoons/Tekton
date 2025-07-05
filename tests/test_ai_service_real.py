#!/usr/bin/env python3
"""
Test AI service with real sockets
"""

import asyncio
import sys
sys.path.insert(0, '/Users/cskoons/projects/github/Tekton')

from shared.ai.ai_service_simple import AIService

async def test_with_real_ai():
    """Test with real AI connection"""
    service = AIService(debug=True)
    
    # Connect to Apollo
    try:
        reader, writer = await asyncio.open_connection('localhost', 45012)
        service.register_ai("apollo-ai", reader, writer)
        
        # Test async send
        msg_id = service.send_message_async("apollo-ai", "What is code quality?")
        
        # Process the message
        await service.process_one_message("apollo-ai", msg_id)
        
        # Get response
        result = service.get_response("apollo-ai", msg_id)
        if result and result['success']:
            response = result['response']
            print(f"Apollo response: {response[:100]}...")
            assert len(response) > 0
        else:
            raise Exception(f"Failed: {result}")
        
        # Cleanup
        writer.close()
        await writer.wait_closed()
        
        print("✓ test_with_real_ai")
        return True
    except Exception as e:
        print(f"✗ test_with_real_ai: {e}")
        return False

async def test_multiple_real_ais():
    """Test with multiple real AIs"""
    service = AIService(debug=True)
    
    # List of AIs to test
    ais = [
        ("apollo-ai", 45012),
        ("numa-ai", 45016),
        ("athena-ai", 45005)
    ]
    
    connections = []
    
    try:
        # Connect to all AIs
        for ai_id, port in ais:
            try:
                reader, writer = await asyncio.open_connection('localhost', port)
                service.register_ai(ai_id, reader, writer)
                connections.append(writer)
                print(f"Connected to {ai_id}")
            except Exception as e:
                print(f"Failed to connect to {ai_id}: {e}")
        
        if len(connections) == 0:
            print("No AIs connected")
            return False
        
        # Send to all
        ai_ids = [ai[0] for ai in ais[:len(connections)]]
        msg_ids = service.send_to_all("Hello from test", ai_ids)
        print(f"Sent to {len(msg_ids)} AIs")
        
        # Process all messages
        await service.process_messages()
        
        # Collect responses
        responses = {}
        async for ai_id, response in service.collect_responses(msg_ids, timeout=10.0):
            if response['success']:
                responses[ai_id] = response['response']
                print(f"{ai_id}: {response['response'][:50]}...")
        
        # Cleanup
        for writer in connections:
            writer.close()
            await writer.wait_closed()
        
        success = len(responses) > 0
        if success:
            print(f"✓ test_multiple_real_ais - Got {len(responses)} responses")
        else:
            print("✗ test_multiple_real_ais - No responses")
        
        return success
        
    except Exception as e:
        print(f"✗ test_multiple_real_ais: {e}")
        # Cleanup on error
        for writer in connections:
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
        return False

async def run_all_tests():
    """Run all real AI tests"""
    print("Testing AI Service with Real Connections")
    print("-" * 40)
    
    passed = 0
    failed = 0
    
    # Test 1: Single AI
    if await test_with_real_ai():
        passed += 1
    else:
        failed += 1
    
    # Test 2: Multiple AIs
    if await test_multiple_real_ais():
        passed += 1
    else:
        failed += 1
    
    print("-" * 40)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)