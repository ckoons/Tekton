#!/usr/bin/env python3
"""
Test suite for unified AI communication system.
Tests the "one queue, one socket, one AI" architecture.
"""

import asyncio
import sys
import time
import json
from typing import Dict, List

# Add Tekton to path
sys.path.insert(0, '/Users/cskoons/projects/github/Tekton')

from shared.ai.simple_ai import ai_send, ai_send_sync
from shared.ai.ai_service_simple import get_service

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"✓ {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"✗ {test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Test Results: {self.passed}/{total} passed")
        if self.errors:
            print("\nFailures:")
            for test, error in self.errors:
                print(f"  - {test}: {error}")
        print(f"{'='*60}")
        return self.failed == 0

results = TestResults()

def test_sync_direct_message():
    """Test synchronous direct message to a single AI"""
    test_name = "test_sync_direct_message"
    try:
        # Test with apollo
        response = ai_send_sync("apollo-ai", "test message", "localhost", 45012)
        if response and len(response) > 0:
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, "Empty response")
    except Exception as e:
        results.add_fail(test_name, str(e))

async def test_async_direct_message():
    """Test asynchronous direct message to a single AI"""
    test_name = "test_async_direct_message"
    try:
        # Test with numa
        response = await ai_send("numa-ai", "test message", "localhost", 45016)
        if response and len(response) > 0:
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, "Empty response")
    except Exception as e:
        results.add_fail(test_name, str(e))

def test_service_registration():
    """Test that AIs are properly registered in the service"""
    test_name = "test_service_registration"
    try:
        service = get_service()
        
        # Check if apollo is registered
        if "apollo-ai" in service.connections:
            results.add_pass(test_name)
        else:
            # Try to register it
            service.register_ai("apollo-ai", "localhost", 45012)
            if "apollo-ai" in service.connections:
                results.add_pass(test_name)
            else:
                results.add_fail(test_name, "Failed to register AI")
    except Exception as e:
        results.add_fail(test_name, str(e))

def test_queue_management():
    """Test that messages are properly queued"""
    test_name = "test_queue_management"
    try:
        service = get_service()
        
        # Queue a message
        msg_id = service.send_request("apollo-ai", "test queue")
        
        # Check if message is in queue
        if "apollo-ai" in service.queues and msg_id in service.queues["apollo-ai"]:
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, "Message not found in queue")
    except Exception as e:
        results.add_fail(test_name, str(e))

async def test_multiple_ai_communication():
    """Test communication with multiple AIs"""
    test_name = "test_multiple_ai_communication"
    try:
        service = get_service()
        
        # Test with 3 AIs
        test_ais = [
            ("apollo-ai", "localhost", 45012),
            ("numa-ai", "localhost", 45016),
            ("athena-ai", "localhost", 45005)
        ]
        
        # Register all
        for ai_id, host, port in test_ais:
            service.register_ai(ai_id, host, port)
        
        # Send messages
        msg_ids = {}
        for ai_id, _, _ in test_ais:
            msg_ids[ai_id] = service.send_request(ai_id, "multi-ai test")
        
        # Process all
        await service.process_all_messages()
        
        # Check responses
        success_count = 0
        for ai_id, msg_id in msg_ids.items():
            response = service.get_response(ai_id, msg_id)
            if response and response.get('success'):
                success_count += 1
        
        if success_count >= 2:  # At least 2 out of 3 should work
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, f"Only {success_count}/3 AIs responded")
    except Exception as e:
        results.add_fail(test_name, str(e))

def test_one_socket_per_ai():
    """Test that only one socket is created per AI"""
    test_name = "test_one_socket_per_ai"
    try:
        service = get_service()
        
        # Get initial connection count
        initial_count = len(service.connections)
        
        # Send multiple messages to same AI
        for i in range(3):
            ai_send_sync("apollo-ai", f"test {i}", "localhost", 45012)
        
        # Check connection count didn't increase
        final_count = len(service.connections)
        
        if final_count == initial_count or final_count == initial_count + 1:
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, f"Expected 1 connection, got {final_count - initial_count}")
    except Exception as e:
        results.add_fail(test_name, str(e))

async def test_team_chat_broadcast():
    """Test team chat broadcast functionality"""
    test_name = "test_team_chat_broadcast"
    try:
        service = get_service()
        
        # Get all registered AIs
        ai_ids = list(service.connections.keys())[:5]  # Test with up to 5 AIs
        
        if len(ai_ids) < 2:
            results.add_fail(test_name, "Not enough AIs registered")
            return
        
        # Broadcast message
        msg_ids = service.broadcast("team broadcast test", ai_ids)
        
        # Process messages
        await service.process_all_messages()
        
        # Count responses
        response_count = 0
        for ai_id, msg_id in msg_ids.items():
            response = service.get_response(ai_id, msg_id)
            if response and response.get('success'):
                response_count += 1
        
        if response_count >= len(ai_ids) // 2:  # At least half should respond
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, f"Only {response_count}/{len(ai_ids)} responded")
    except Exception as e:
        results.add_fail(test_name, str(e))

def test_error_handling():
    """Test error handling for non-existent AI"""
    test_name = "test_error_handling"
    try:
        # Try to send to non-existent AI
        try:
            ai_send_sync("non-existent-ai", "test", "localhost", 99999)
            results.add_fail(test_name, "Should have raised an exception")
        except Exception:
            # Expected to fail
            results.add_pass(test_name)
    except Exception as e:
        results.add_fail(test_name, f"Unexpected error: {e}")

async def test_response_collection():
    """Test async response collection"""
    test_name = "test_response_collection"
    try:
        service = get_service()
        
        # Send to multiple AIs
        ai_ids = ["apollo-ai", "numa-ai"]
        msg_ids = service.broadcast("collection test", ai_ids)
        
        # Process
        await service.process_all_messages()
        
        # Collect responses
        responses = []
        async for ai_id, response in service.collect_responses(msg_ids, timeout=5.0):
            responses.append((ai_id, response))
        
        if len(responses) > 0:
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, "No responses collected")
    except Exception as e:
        results.add_fail(test_name, str(e))

async def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("Unified AI Communication Test Suite")
    print("Testing: One Queue, One Socket, One AI")
    print("="*60)
    print()
    
    # Define all tests
    sync_tests = {
        "test_sync_direct_message": test_sync_direct_message,
        "test_service_registration": test_service_registration,
        "test_queue_management": test_queue_management,
        "test_one_socket_per_ai": test_one_socket_per_ai,
        "test_error_handling": test_error_handling,
    }
    
    async_tests = {
        "test_async_direct_message": test_async_direct_message,
        "test_multiple_ai_communication": test_multiple_ai_communication,
        "test_team_chat_broadcast": test_team_chat_broadcast,
        "test_response_collection": test_response_collection,
    }
    
    # Run sync tests
    for test_name, test_func in sync_tests.items():
        test_func()
    
    # Run async tests
    for test_name, test_func in async_tests.items():
        await test_func()
    
    # Summary
    return results.summary()

async def run_single_test(test_name: str):
    """Run a single test by name"""
    print(f"Running single test: {test_name}")
    print("="*60)
    
    # Define all tests
    sync_tests = {
        "test_sync_direct_message": test_sync_direct_message,
        "test_service_registration": test_service_registration,
        "test_queue_management": test_queue_management,
        "test_one_socket_per_ai": test_one_socket_per_ai,
        "test_error_handling": test_error_handling,
    }
    
    async_tests = {
        "test_async_direct_message": test_async_direct_message,
        "test_multiple_ai_communication": test_multiple_ai_communication,
        "test_team_chat_broadcast": test_team_chat_broadcast,
        "test_response_collection": test_response_collection,
    }
    
    # Run the specific test
    if test_name in sync_tests:
        sync_tests[test_name]()
    elif test_name in async_tests:
        await async_tests[test_name]()
    else:
        print(f"Test '{test_name}' not found!")
        print("\nAvailable tests:")
        for name in sync_tests:
            print(f"  - {name}")
        for name in async_tests:
            print(f"  - {name}")
        return False
    
    return results.summary()

def list_tests():
    """List all available tests"""
    print("Available tests:")
    print("\nSynchronous tests:")
    print("  - test_sync_direct_message")
    print("  - test_service_registration")
    print("  - test_queue_management")
    print("  - test_one_socket_per_ai")
    print("  - test_error_handling")
    print("\nAsynchronous tests:")
    print("  - test_async_direct_message")
    print("  - test_multiple_ai_communication")
    print("  - test_team_chat_broadcast")
    print("  - test_response_collection")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test unified AI communication')
    parser.add_argument('test', nargs='?', help='Specific test to run (omit for all tests)')
    parser.add_argument('--list', '-l', action='store_true', help='List available tests')
    
    args = parser.parse_args()
    
    if args.list:
        list_tests()
        sys.exit(0)
    
    # Run tests
    if args.test:
        success = asyncio.run(run_single_test(args.test))
    else:
        success = asyncio.run(run_all_tests())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)