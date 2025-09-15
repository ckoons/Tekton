#!/usr/bin/env python3
"""
Basic Component Test
Tests that basic components can be imported and initialized
"""

import sys
from pathlib import Path
import os

# Set TEKTON_ROOT before imports
if 'TEKTON_ROOT' not in os.environ:
    os.environ['TEKTON_ROOT'] = str(Path(__file__).parent.parent)

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment properly
from shared.env import TektonEnvironLock
TektonEnvironLock.load()


def test_imports():
    """Test that we can import the main components"""
    print("\n" + "="*50)
    print("TESTING BASIC IMPORTS")
    print("="*50)
    
    success = True
    
    # Test Engram imports
    try:
        from engram.core.storage.cognitive_workflows import CognitiveWorkflows, ThoughtType
        print("✓ Engram cognitive workflows imported")
    except Exception as e:
        print(f"✗ Failed to import Engram: {e}")
        success = False
    
    # Test ESR imports
    try:
        from engram.core.storage.unified_interface import ESRMemorySystem
        print("✓ ESR Memory System imported")
    except Exception as e:
        print(f"✗ Failed to import ESR: {e}")
        success = False
    
    # Test bridge imports
    try:
        from shared.integration.engram_cognitive_bridge import CognitiveEventType, CognitivePattern
        print("✓ Engram Cognitive Bridge types imported")
    except Exception as e:
        print(f"✗ Failed to import bridge types: {e}")
        success = False
    
    print("\n" + "="*50)
    if success:
        print("ALL IMPORTS SUCCESSFUL ✓")
    else:
        print("SOME IMPORTS FAILED ✗")
    print("="*50)
    
    return success


def test_basic_structures():
    """Test basic data structures"""
    print("\n" + "="*50)
    print("TESTING BASIC STRUCTURES")
    print("="*50)
    
    success = True
    
    # Test creating a cognitive pattern
    try:
        from shared.integration.engram_cognitive_bridge import CognitivePattern
        from datetime import datetime
        
        pattern = CognitivePattern(
            id="test_001",
            name="Test Pattern",
            type="cognitive",
            state="emerging",
            strength=0.5,
            confidence=0.7,
            novelty="moderate",
            description="A test pattern"
        )
        print(f"✓ Created CognitivePattern: {pattern.name}")
    except Exception as e:
        print(f"✗ Failed to create CognitivePattern: {e}")
        success = False
    
    # Test creating a thought type
    try:
        from engram.core.storage.cognitive_workflows import ThoughtType
        
        thought = ThoughtType.IDEA
        print(f"✓ Created ThoughtType: {thought.value}")
    except Exception as e:
        print(f"✗ Failed to create ThoughtType: {e}")
        success = False
    
    print("\n" + "="*50)
    if success:
        print("ALL STRUCTURES CREATED ✓")
    else:
        print("SOME STRUCTURES FAILED ✗")
    print("="*50)
    
    return success


def main():
    """Run all basic tests"""
    print("\n" + "="*60)
    print("BASIC COMPONENT TESTS")
    print("="*60)
    
    all_success = True
    
    # Test imports
    if not test_imports():
        all_success = False
    
    # Test structures
    if not test_basic_structures():
        all_success = False
    
    print("\n" + "="*60)
    if all_success:
        print("ALL BASIC TESTS PASSED ✓")
        print("The core integration structure is working!")
        print("\nNext steps to test:")
        print("1. Initialize ESR Memory System")
        print("2. Test pattern storage in knowledge graph")
        print("3. Test discovery and learning engines separately")
    else:
        print("SOME BASIC TESTS FAILED ✗")
    print("="*60)
    
    return 0 if all_success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())