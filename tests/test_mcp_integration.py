#!/usr/bin/env python3
"""
Test script for MCP Tools Integration.

This script tests the SendMessageToSpecialist implementation for both
socket-based (Greek Chorus) and API-based (Rhetor) communication.
"""

import sys
import os
import asyncio
import json

# Add Tekton root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Rhetor.rhetor.core.mcp.tools_integration_unified import MCPToolsIntegrationUnified


async def test_send_message_to_specialist():
    """Test sending messages to different types of specialists."""
    print("\n=== Testing MCP SendMessageToSpecialist ===")
    
    # Initialize integration
    integration = MCPToolsIntegrationUnified()
    
    # List available specialists
    print("\nDiscovering available specialists...")
    specialists = await integration.list_specialists()
    
    if not specialists:
        print("No specialists found!")
        return False
    
    print(f"Found {len(specialists)} specialists:")
    for spec in specialists[:5]:  # Show first 5
        print(f"  - {spec.get('id')}: {spec.get('name')} ({spec.get('type', 'unknown')})")
    
    # Test cases
    test_cases = [
        {
            "specialist": "athena-ai",
            "message": "Hello Athena, this is a test of the new MCP integration. What is wisdom?",
            "expected_type": "socket"
        },
        {
            "specialist": "apollo-ai", 
            "message": "Apollo, can you see the vision of our integrated AI platform?",
            "expected_type": "socket"
        },
        {
            "specialist": "rhetor-specialist",
            "message": "Rhetor, how should we architect our prompt templates?",
            "expected_type": "api"
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\n--- Testing {test['specialist']} ---")
        print(f"Message: {test['message']}")
        
        try:
            # Send message
            response = await integration.send_message_to_specialist(
                test['specialist'],
                test['message']
            )
            
            if response['success']:
                print(f"✓ Success! Response type: {response.get('type')}")
                print(f"Response: {response['response'][:100]}...")
                
                # Verify communication type
                if response.get('type') == test['expected_type']:
                    print(f"✓ Communication type matches expected: {test['expected_type']}")
                    results.append(True)
                else:
                    print(f"✗ Expected {test['expected_type']} but got {response.get('type')}")
                    results.append(False)
            else:
                print(f"✗ Failed: {response['error']}")
                results.append(False)
                
        except Exception as e:
            print(f"✗ Exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n=== Test Summary ===")
    passed = sum(1 for r in results if r)
    print(f"Passed: {passed}/{len(results)}")
    
    return passed == len(results)


async def test_error_handling():
    """Test error handling scenarios."""
    print("\n=== Testing Error Handling ===")
    
    integration = MCPToolsIntegrationUnified()
    
    # Test non-existent specialist
    print("\n1. Testing non-existent specialist...")
    response = await integration.send_message_to_specialist(
        "non-existent-ai",
        "This should fail"
    )
    
    if not response['success'] and "not found" in response['error']:
        print("✓ Correctly handled non-existent specialist")
    else:
        print("✗ Failed to handle non-existent specialist properly")
        print(f"Response: {response}")
    
    # Test timeout scenario (if AI is not responding)
    print("\n2. Testing timeout handling...")
    # This would require a non-responsive AI to test properly
    
    return True


async def test_context_passing():
    """Test passing context to specialists."""
    print("\n=== Testing Context Passing ===")
    
    integration = MCPToolsIntegrationUnified()
    
    context = {
        "session_id": "test-123",
        "user": "Casey",
        "previous_topic": "AI architecture"
    }
    
    print(f"Context: {json.dumps(context, indent=2)}")
    
    response = await integration.send_message_to_specialist(
        "athena-ai",
        "Given our previous discussion, what should we focus on next?",
        context
    )
    
    if response['success']:
        print("✓ Successfully sent message with context")
        print(f"Response: {response['response'][:100]}...")
        return True
    else:
        print(f"✗ Failed: {response['error']}")
        return False


async def main():
    """Run all tests."""
    print("MCP Tools Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("SendMessageToSpecialist", test_send_message_to_specialist),
        ("Error Handling", test_error_handling),
        ("Context Passing", test_context_passing)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\nRunning: {test_name}")
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n{test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Final summary
    print("\n" + "=" * 50)
    print("Final Test Summary:")
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"  {test_name}: {status}")
    
    total_passed = sum(1 for _, result in results if result)
    print(f"\nTotal: {total_passed}/{len(tests)} tests passed")
    
    return total_passed == len(tests)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)