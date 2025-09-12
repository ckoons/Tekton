"""
Run Experience Layer tests individually.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
import logging

# Suppress verbose logging for cleaner test output
logging.basicConfig(level=logging.WARNING)

from test_experience_layer import (
    test_experience_creation,
    test_memory_promises,
    test_working_memory,
    test_emotional_influence,
    test_interstitial_processing,
    test_memory_decay,
    test_experience_recall_with_emotion,
    test_dream_recombination,
    test_mood_summary,
    test_working_memory_status
)

async def run_all_tests():
    """Run all tests and report results."""
    tests = [
        ("Experience Creation", test_experience_creation),
        ("Memory Promises", test_memory_promises),
        ("Working Memory", test_working_memory),
        ("Emotional Influence", test_emotional_influence),
        ("Interstitial Processing", test_interstitial_processing),
        ("Memory Decay", test_memory_decay),
        ("Experience Recall", test_experience_recall_with_emotion),
        ("Dream Recombination", test_dream_recombination),
        ("Mood Summary", test_mood_summary),
        ("Working Memory Status", test_working_memory_status)
    ]
    
    passed = 0
    failed = 0
    
    print("=" * 60)
    print("EXPERIENCE LAYER TEST SUITE")
    print("=" * 60)
    
    for test_name, test_func in tests:
        try:
            await test_func()
            print(f"✓ {test_name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"✗ {test_name}: FAILED - {str(e)[:50]}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All Experience Layer tests passed!")
    else:
        print(f"⚠️ {failed} tests failed")
    
    return passed, failed

if __name__ == "__main__":
    passed, failed = asyncio.run(run_all_tests())