#!/usr/bin/env python3
"""
Tests for simple AI service
Testing: send_message_sync, send_message_async, send_to_all, collect_responses
"""

import asyncio
import json
import sys
sys.path.insert(0, '/Users/cskoons/projects/github/Tekton')

from shared.ai.ai_service_simple import CIService

# Mock socket for testing
class MockSocket:
    def __init__(self, ai_id, response_text):
        self.ai_id = ai_id
        self.response_text = response_text
        self.requests = []  # Track what was sent
        
    async def readline(self):
        """Return mock response"""
        response = {
            "type": "chat_response",
            "ai_id": self.ai_id,
            "content": self.response_text
        }
        return json.dumps(response).encode('utf-8') + b'\n'
    
    def write(self, data):
        """Track what was written"""
        self.requests.append(data)
    
    async def drain(self):
        """No-op for mock"""
        pass

def test_send_message_sync():
    """Test synchronous send and receive (without sockets)"""
    service = CIService(debug=True)
    
    # Don't register sockets - sync method will simulate
    # Just register AI with no socket to create the queue
    if "test-ci" not in service.queues:
        service.queues["test-ci"] = {}
    
    # Send message and get response
    try:
        response = service.send_message_sync("test-ci", "Hello AI")
        # Sync method returns mock response for testing
        assert "Mock response to: Hello AI" in response
        print("✓ test_send_message_sync")
        return True
    except Exception as e:
        print(f"✗ test_send_message_sync: {e}")
        return False

def test_send_message_async():
    """Test async send (fire and forget)"""
    service = CIService(debug=True)
    
    # Register AI (socket not used for this test)
    service.register_ai("test-ci", None, None)
    
    try:
        # Send async - should just return msg_id
        msg_id = service.send_message_async("test-ci", "Test message")
        assert msg_id is not None
        assert len(msg_id) > 0
        
        # Check message is queued
        assert "test-ci" in service.queues
        assert msg_id in service.queues["test-ci"]
        assert service.queues["test-ci"][msg_id].request == "Test message"
        
        print("✓ test_send_message_async")
        return True
    except Exception as e:
        print(f"✗ test_send_message_async: {e}")
        return False

def test_send_to_all():
    """Test sending to multiple AIs"""
    service = CIService(debug=True)
    
    # Register multiple AIs
    ai_ids = ["ai-1", "ai-2", "ai-3"]
    for ai_id in ai_ids:
        service.register_ai(ai_id, None, None)
    
    try:
        # Send to all
        msg_ids = service.send_to_all("Broadcast message", ai_ids)
        
        # Check all got queued
        assert len(msg_ids) == 3
        for ai_id in ai_ids:
            assert ai_id in msg_ids
            assert msg_ids[ai_id] in service.queues[ai_id]
            
        print("✓ test_send_to_all")
        return True
    except Exception as e:
        print(f"✗ test_send_to_all: {e}")
        return False

async def test_collect_responses():
    """Test collecting responses as they arrive"""
    service = CIService(debug=True)
    
    # Register AIs with mock sockets
    mocks = {
        "fast-ci": MockSocket("fast-ci", "Fast response"),
        "slow-ci": MockSocket("slow-ci", "Slow response")
    }
    
    for ai_id, mock in mocks.items():
        service.register_ai(ai_id, mock, mock)
    
    try:
        # Send to both
        msg_ids = service.send_to_all("Test", list(mocks.keys()))
        
        # Process messages
        await service.process_messages()
        
        # Collect responses
        responses = {}
        async for ai_id, response in service.collect_responses(msg_ids, timeout=5.0):
            responses[ai_id] = response
        
        # Check we got both
        assert len(responses) == 2
        assert responses["fast-ci"]["success"] == True
        assert responses["fast-ci"]["response"] == "Fast response"
        assert responses["slow-ci"]["success"] == True
        assert responses["slow-ci"]["response"] == "Slow response"
        
        print("✓ test_collect_responses")
        return True
    except Exception as e:
        print(f"✗ test_collect_responses: {e}")
        return False

def test_error_handling():
    """Test error propagation"""
    service = CIService(debug=True)
    
    try:
        # Try to send to unregistered AI
        try:
            service.send_message_sync("unknown-ci", "test")
            print("✗ test_error_handling: Should have raised error")
            return False
        except ValueError as e:
            assert "not registered" in str(e)
            print("✓ test_error_handling")
            return True
    except Exception as e:
        print(f"✗ test_error_handling: Wrong error type: {e}")
        return False

async def run_async_tests():
    """Run async tests"""
    return await test_collect_responses()

def run_all_tests():
    """Run all tests"""
    print("Testing AI Service Simple")
    print("-" * 40)
    
    # Sync tests
    passed = 0
    failed = 0
    
    tests = [
        test_send_message_sync,
        test_send_message_async,
        test_send_to_all,
        test_error_handling
    ]
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    # Async test
    if asyncio.run(run_async_tests()):
        passed += 1
    else:
        failed += 1
    
    print("-" * 40)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)