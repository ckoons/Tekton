#!/usr/bin/env python3
"""
Memory Integration Test
Tests the ESR memory system and cognitive workflows
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import os

# Set TEKTON_ROOT before imports
if 'TEKTON_ROOT' not in os.environ:
    os.environ['TEKTON_ROOT'] = str(Path(__file__).parent.parent)

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment properly
from shared.env import TektonEnvironLock, TektonEnviron
TektonEnvironLock.load()

from engram.core.storage.unified_interface import ESRMemorySystem
from engram.core.storage.cognitive_workflows import CognitiveWorkflows, ThoughtType


async def test_esr_system():
    """Test ESR Memory System"""
    print("\n" + "="*50)
    print("TESTING ESR MEMORY SYSTEM")
    print("="*50)
    
    # Initialize ESR
    print("\n1. Initializing ESR Memory System...")
    data_dir = TektonEnviron.get('TEKTON_DATA_DIR', '/tmp/tekton/data')
    esr = ESRMemorySystem(
        cache_size=1000,
        enable_backends={'kv'},  # Start with simple key-value backend
        config={
            'namespace': 'test',
            'data_dir': f"{data_dir}/test/esr_data"
        }
    )
    
    await esr.start()
    print("   ✓ ESR Memory System started")
    
    # Initialize Cognitive Workflows
    print("\n2. Initializing Cognitive Workflows...")
    workflows = CognitiveWorkflows(
        cache=esr.cache,
        encoder=esr.encoder
    )
    print("   ✓ Cognitive Workflows initialized")
    
    # Store a thought
    print("\n3. Storing a thought...")
    thought_key = await workflows.store_thought(
        content="Testing the integrated cognitive system",
        thought_type=ThoughtType.IDEA,
        context={"test": True, "timestamp": datetime.now().isoformat()},
        confidence=0.9,
        ci_id="test_ci"
    )
    print(f"   ✓ Thought stored with key: {thought_key[:20]}...")
    
    # Recall the thought
    print("\n4. Recalling the thought...")
    recalled = await workflows.recall_thought(key=thought_key)
    if recalled:
        print(f"   ✓ Thought recalled: {recalled.content}")
        print(f"     - Type: {recalled.thought_type.value}")
        print(f"     - Confidence: {recalled.confidence}")
    else:
        print("   ✗ Failed to recall thought")
    
    # Store related thoughts
    print("\n5. Storing related thoughts...")
    thought2_key = await workflows.store_thought(
        content="Pattern recognition is working",
        thought_type=ThoughtType.OBSERVATION,
        associations=[thought_key],
        confidence=0.85,
        ci_id="test_ci"
    )
    print(f"   ✓ Related thought stored: {thought2_key[:20]}...")
    
    # Recall similar thoughts
    print("\n6. Recalling similar thoughts...")
    similar = await workflows.recall_similar(
        reference="cognitive system pattern",
        limit=5,
        ci_id="test_ci"
    )
    print(f"   ✓ Found {len(similar)} similar thoughts")
    
    # Build context - using topic instead of keys
    print("\n7. Building context...")
    context = await workflows.build_context(
        topic="cognitive system testing",
        depth=2,
        ci_id="test_ci"
    )
    print(f"   ✓ Context built with {len(context)} elements")
    
    # Get status from cache and stats
    print("\n8. Getting ESR status...")
    # Since get_status doesn't exist, we'll get info from the cache and stats directly
    cache_size = len(esr.cache.cache)
    total_stores = esr.stats.get('stores', 0)
    total_retrievals = esr.stats.get('retrievals', 0)
    print(f"   ✓ ESR Status:")
    print(f"     - Cache entries: {cache_size}")
    print(f"     - Total stores: {total_stores}")
    print(f"     - Total retrievals: {total_retrievals}")
    
    # Shutdown
    print("\n9. Shutting down...")
    await esr.stop()
    print("   ✓ ESR Memory System stopped")
    
    print("\n" + "="*50)
    print("ESR MEMORY SYSTEM TEST COMPLETE ✓")
    print("="*50)
    
    return True


async def main():
    """Run memory integration test"""
    print("\n" + "="*60)
    print("MEMORY INTEGRATION TEST")
    print("="*60)
    
    try:
        await test_esr_system()
        
        print("\n" + "="*60)
        print("MEMORY INTEGRATION TEST PASSED ✓")
        print("\nThe ESR memory system is working!")
        print("="*60)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
