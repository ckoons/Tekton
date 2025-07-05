#!/usr/bin/env python3
"""
Simple tests for AI communication.
No event loops. Just function calls and results.
"""

import sys
sys.path.insert(0, '/Users/cskoons/projects/github/Tekton')

from shared.ai.simple_ai import ai_send_sync

def test_apollo_responds():
    """Test that Apollo AI responds to a message"""
    try:
        response = ai_send_sync("apollo-ai", "hello", "localhost", 45012)
        assert response is not None
        assert len(response) > 0
        print("✓ test_apollo_responds")
        return True
    except Exception as e:
        print(f"✗ test_apollo_responds: {e}")
        return False

def test_numa_responds():
    """Test that Numa AI responds to a message"""
    try:
        response = ai_send_sync("numa-ai", "hello", "localhost", 45016) 
        assert response is not None
        assert len(response) > 0
        print("✓ test_numa_responds")
        return True
    except Exception as e:
        print(f"✗ test_numa_responds: {e}")
        return False

def test_multiple_calls_same_ai():
    """Test multiple calls to same AI work"""
    try:
        # Make 3 calls
        response1 = ai_send_sync("apollo-ai", "first", "localhost", 45012)
        response2 = ai_send_sync("apollo-ai", "second", "localhost", 45012)
        response3 = ai_send_sync("apollo-ai", "third", "localhost", 45012)
        
        # All should have responses
        assert response1 is not None
        assert response2 is not None  
        assert response3 is not None
        
        print("✓ test_multiple_calls_same_ai")
        return True
    except Exception as e:
        print(f"✗ test_multiple_calls_same_ai: {e}")
        return False

def test_invalid_ai_fails():
    """Test that invalid AI fails appropriately"""
    try:
        response = ai_send_sync("fake-ai", "hello", "localhost", 99999)
        print("✗ test_invalid_ai_fails: Should have failed but didn't")
        return False
    except Exception:
        print("✓ test_invalid_ai_fails")
        return True

def run_all_tests():
    """Run all tests and return success"""
    tests = [
        test_apollo_responds,
        test_numa_responds,
        test_multiple_calls_same_ai,
        test_invalid_ai_fails
    ]
    
    passed = 0
    failed = 0
    
    print("Running simple AI tests...")
    print("-" * 40)
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("-" * 40)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)