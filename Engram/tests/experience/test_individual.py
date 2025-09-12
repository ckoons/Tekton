"""Debug individual tests."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
import logging
logging.basicConfig(level=logging.WARNING)

from test_experience_layer import *

async def test_with_details():
    """Run tests with detailed error reporting."""
    
    # Test working memory
    print("\nTesting Working Memory...")
    try:
        await test_working_memory()
        print("Working Memory: PASSED")
    except Exception as e:
        print(f"Working Memory: FAILED - {e}")
        import traceback
        traceback.print_exc()
    
    # Test emotional influence
    print("\nTesting Emotional Influence...")
    try:
        await test_emotional_influence()
        print("Emotional Influence: PASSED")
    except Exception as e:
        print(f"Emotional Influence: FAILED - {e}")
    
    # Test interstitial
    print("\nTesting Interstitial Processing...")
    try:
        await test_interstitial_processing()
        print("Interstitial Processing: PASSED")
    except Exception as e:
        print(f"Interstitial Processing: FAILED - {e}")
    
    # Test experience recall
    print("\nTesting Experience Recall...")
    try:
        await test_experience_recall_with_emotion()
        print("Experience Recall: PASSED")
    except Exception as e:
        print(f"Experience Recall: FAILED - {e}")

if __name__ == "__main__":
    asyncio.run(test_with_details())