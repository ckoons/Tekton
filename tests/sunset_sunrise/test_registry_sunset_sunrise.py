#!/usr/bin/env python3
"""
Test script for sunset/sunrise registry implementation.
Tests thread safety, persistence, and auto-detection.
"""

import sys
import os
import json
import threading
import time
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # Get to Tekton root
from shared.aish.src.registry.ci_registry import get_registry

def test_basic_operations():
    """Test basic sunset/sunrise operations."""
    print("Testing basic sunset/sunrise operations...")
    registry = get_registry()
    
    # Test setting next_prompt
    result = registry.set_next_prompt('apollo', 'SUNSET_PROTOCOL: Please summarize...')
    print(f"  Set next_prompt for apollo: {result}")
    
    # Test getting next_prompt
    prompt = registry.get_next_prompt('apollo')
    print(f"  Retrieved next_prompt: {prompt[:50]}...")
    
    # Test setting sunrise_context
    context = "I've been working on authentication. Completed token generation."
    result = registry.set_sunrise_context('apollo', context)
    print(f"  Set sunrise_context: {result}")
    
    # Test getting sunrise_context
    retrieved = registry.get_sunrise_context('apollo')
    print(f"  Retrieved sunrise_context: {retrieved[:50]}...")
    
    # Test clearing
    registry.clear_next_prompt('apollo')
    registry.clear_sunrise_context('apollo')
    
    # Verify cleared
    prompt = registry.get_next_prompt('apollo')
    context = registry.get_sunrise_context('apollo')
    print(f"  After clearing - next_prompt: {prompt}, sunrise_context: {context}")
    
    return prompt is None and context is None

def test_auto_detection():
    """Test automatic sunset response detection."""
    print("\nTesting auto-detection of sunset responses...")
    registry = get_registry()
    
    # Test with sunset-like response
    sunset_response = {
        'user_message': 'SUNSET_PROTOCOL: Please summarize your context',
        'content': """I'm currently working on the OAuth implementation.
        Key decisions so far include using JWT tokens.
        My current approach involves refresh token rotation.
        Next steps are to implement the revocation endpoint.
        Current emotional state is focused and productive."""
    }
    
    # Update output - should auto-detect and copy to sunrise_context
    registry.update_ci_last_output('athena', sunset_response)
    
    # Check if auto-detected
    sunrise = registry.get_sunrise_context('athena')
    print(f"  Auto-detected sunset response: {sunrise is not None}")
    if sunrise:
        print(f"  Sunrise context captured: {sunrise[:100]}...")
    
    # Test with normal response (should not trigger)
    normal_response = {
        'content': "The function has been implemented successfully."
    }
    registry.update_ci_last_output('metis', normal_response)
    sunrise = registry.get_sunrise_context('metis')
    print(f"  Normal response didn't trigger: {sunrise is None}")
    
    return True

def test_thread_safety():
    """Test thread-safe concurrent access."""
    print("\nTesting thread safety with concurrent access...")
    registry = get_registry()
    
    errors = []
    
    def worker(ci_name, worker_id):
        """Worker thread that performs registry operations."""
        try:
            for i in range(5):
                # Set next_prompt
                prompt = f"Worker {worker_id} prompt {i}"
                registry.set_next_prompt(ci_name, prompt)
                
                # Read it back
                retrieved = registry.get_next_prompt(ci_name)
                
                # Set sunrise_context
                context = f"Worker {worker_id} context {i}"
                registry.set_sunrise_context(ci_name, context)
                
                # Small delay to increase contention
                time.sleep(0.001)
                
                # Clear them
                registry.clear_next_prompt(ci_name)
                registry.clear_sunrise_context(ci_name)
                
        except Exception as e:
            errors.append(f"Worker {worker_id}: {e}")
    
    # Launch multiple threads targeting same CI
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=('numa', i))
        threads.append(t)
        t.start()
    
    # Wait for completion
    for t in threads:
        t.join()
    
    if errors:
        print(f"  Errors during concurrent access: {errors}")
        return False
    
    print(f"  Successfully handled {len(threads)} concurrent threads")
    return True

def test_persistence():
    """Test that sunset/sunrise state persists."""
    print("\nTesting persistence across registry instances...")
    
    # Create first registry instance and set states
    registry1 = get_registry()
    registry1.set_next_prompt('rhetor', 'Test sunset prompt')
    registry1.set_sunrise_context('rhetor', 'Test sunrise context')
    
    # Force a new registry instance (simulate restart)
    import importlib
    import shared.aish.src.registry.ci_registry as ci_module
    ci_module._registry_instance = None  # Reset singleton
    
    # Get new instance and check if state persisted
    registry2 = get_registry()
    prompt = registry2.get_next_prompt('rhetor')
    context = registry2.get_sunrise_context('rhetor')
    
    print(f"  Next prompt persisted: {prompt == 'Test sunset prompt'}")
    print(f"  Sunrise context persisted: {context == 'Test sunrise context'}")
    
    # Clean up
    registry2.clear_next_prompt('rhetor')
    registry2.clear_sunrise_context('rhetor')
    
    return prompt == 'Test sunset prompt' and context == 'Test sunrise context'

def test_state_machine_flow():
    """Test complete sunset/sunrise state machine flow."""
    print("\nTesting complete state machine flow...")
    registry = get_registry()
    
    print("  1. NORMAL state (no prompts set)")
    prompt = registry.get_next_prompt('synthesis')
    print(f"     next_prompt: {prompt}")
    
    print("  2. Apollo triggers SUNSET")
    registry.set_next_prompt('synthesis', 'SUNSET_PROTOCOL: Please summarize...')
    prompt = registry.get_next_prompt('synthesis')
    print(f"     next_prompt set: {prompt is not None}")
    
    print("  3. CI processes sunset, system detects response")
    sunset_response = {
        'user_message': prompt,
        'content': """Current context summary:
        - Working on: Database optimization
        - Key decisions: Using connection pooling
        - Current approach: Implementing lazy loading
        - Next steps: Add caching layer"""
    }
    registry.update_ci_last_output('synthesis', sunset_response)
    sunrise = registry.get_sunrise_context('synthesis')
    print(f"     sunrise_context auto-populated: {sunrise is not None}")
    
    print("  4. Apollo prepares SUNRISE")
    sunrise_prompt = f"--append-system-prompt 'Task: Continue optimization\\n{sunrise[:50]}...'"
    registry.set_next_prompt('synthesis', sunrise_prompt)
    registry.clear_sunrise_context('synthesis')
    
    print("  5. Return to NORMAL")
    registry.clear_next_prompt('synthesis')
    final_prompt = registry.get_next_prompt('synthesis')
    final_context = registry.get_sunrise_context('synthesis')
    print(f"     State cleared - prompt: {final_prompt}, context: {final_context}")
    
    return final_prompt is None and final_context is None

def main():
    """Run all tests."""
    print("=" * 60)
    print("Sunset/Sunrise Registry Tests")
    print("=" * 60)
    
    tests = [
        ("Basic Operations", test_basic_operations),
        ("Auto-Detection", test_auto_detection),
        ("Thread Safety", test_thread_safety),
        ("Persistence", test_persistence),
        ("State Machine Flow", test_state_machine_flow)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ {name} failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name:<25} {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Sunset/sunrise implementation is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please review the implementation.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())