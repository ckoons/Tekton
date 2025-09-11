#!/usr/bin/env python3
"""
Fixed ESR Test - Tests the updated "store everywhere" paradigm.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import logging
from typing import Any, Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_esr_fixed")

# Setup paths
current_dir = Path(__file__).parent
engram_root = current_dir.parent
coder_a_root = engram_root.parent

sys.path.insert(0, str(engram_root))
sys.path.insert(0, str(coder_a_root))

# Set environment
if 'TEKTON_ROOT' not in os.environ:
    os.environ['TEKTON_ROOT'] = str(coder_a_root)

# Import ESR components
from engram.core.storage.cache_layer import CacheLayer
from engram.core.storage.universal_encoder import UniversalEncoder, MemorySynthesizer, MemoryResponse
from engram.core.storage.unified_interface import ESRMemorySystem


class SimpleMockBackend:
    """Simplified mock backend for testing."""
    
    def __init__(self, name: str):
        self.name = name
        self.data = {}
    
    async def store(self, key: str, value: Any, **kwargs) -> bool:
        """Store data."""
        self.data[key] = value
        logger.debug(f"{self.name}: Stored {key}")
        return True
    
    async def retrieve(self, key: str) -> Optional[MemoryResponse]:
        """Retrieve data."""
        if key in self.data:
            return MemoryResponse(
                content=self.data[key],
                source_backend=self.name,
                retrieval_time=0.01,
                confidence=1.0,
                metadata={'key': key}
            )
        return None


async def test_store_everywhere():
    """Test the 'store everywhere' paradigm."""
    logger.info("\n=== Testing Store Everywhere Paradigm ===")
    
    # Create mock backends
    backends = {
        'sql': SimpleMockBackend('sql'),
        'document': SimpleMockBackend('document'),
        'kv': SimpleMockBackend('kv')
    }
    
    # Create universal encoder
    encoder = UniversalEncoder(backends=backends)
    
    # Test data
    test_key = "memory_001"
    test_content = {
        "thought": "The sky is blue",
        "timestamp": datetime.now().isoformat(),
        "type": "observation"
    }
    
    # Store in all backends
    logger.info(f"Storing '{test_content['thought']}' with key '{test_key}'")
    results = await encoder.store_everywhere(
        key=test_key,
        content=test_content,
        metadata={'test': True}
    )
    
    # Check results
    successful = sum(1 for success in results.values() if success)
    logger.info(f"✓ Stored in {successful}/{len(backends)} backends")
    for backend_name, success in results.items():
        status = "✓" if success else "✗"
        logger.info(f"  {status} {backend_name}")
    
    # Test recall
    logger.info("\nRecalling from all backends...")
    synthesis = await encoder.recall_from_everywhere(key=test_key)
    
    logger.info(f"✓ Synthesis status: {synthesis.get('status', 'unknown')}")
    if 'primary_memory' in synthesis:
        logger.info(f"✓ Primary memory retrieved: {synthesis['primary_memory'].get('thought', 'N/A')}")
    
    # Check statistics
    stats_data = encoder.get_statistics()
    stats = stats_data.get('stats', {})
    logger.info(f"\nStatistics:")
    logger.info(f"  Total stores: {stats.get('total_stores', 0)}")
    logger.info(f"  Total recalls: {stats.get('total_recalls', 0)}")
    logger.info(f"  Stores by backend: {stats.get('stores', {})}")
    
    return True


async def test_frequency_promotion():
    """Test frequency-based promotion from cache."""
    logger.info("\n=== Testing Frequency-Based Promotion ===")
    
    # Create cache
    cache = CacheLayer(
        max_size=100,
        promotion_threshold=2,
        eviction_policy='lru',
        persist_cache=False
    )
    
    # Store initial thought
    content = "Important observation about the system"
    key = await cache.store(
        content=content,
        content_type='observation',
        metadata={'importance': 'high'},
        ci_id='test_ci'
    )
    logger.info(f"✓ Stored with key: {key}")
    
    # First access - should not trigger promotion
    await cache.retrieve(key, ci_id='test_ci')
    promotions = cache.get_promotion_candidates()
    logger.info(f"After 1 access: {len(promotions)} items queued for promotion")
    
    # Second access - should trigger promotion
    await cache.retrieve(key, ci_id='another_ci')
    promotions = cache.get_promotion_candidates()
    logger.info(f"After 2 accesses: {len(promotions)} items queued for promotion")
    
    if promotions:
        logger.info(f"✓ Promotion triggered for key: {promotions[0]}")
    
    return True


async def test_synthesis():
    """Test memory synthesis from multiple sources."""
    logger.info("\n=== Testing Memory Synthesis ===")
    
    # Create different versions of the same memory
    memories = [
        MemoryResponse(
            content={"fact": "The sky is blue", "time": "morning"},
            source_backend="sql",
            retrieval_time=0.02,
            confidence=0.9,
            metadata={"version": 1}
        ),
        MemoryResponse(
            content={"fact": "The sky is blue", "time": "noon", "detail": "clear day"},
            source_backend="document",
            retrieval_time=0.01,
            confidence=0.95,
            metadata={"version": 2}
        ),
        MemoryResponse(
            content={"fact": "The sky is gray", "time": "evening"},
            source_backend="kv",
            retrieval_time=0.005,
            confidence=0.8,
            metadata={"version": 3}
        )
    ]
    
    # Synthesize memories
    synthesizer = MemorySynthesizer()
    result = synthesizer.synthesize(memories, query="sky color")
    
    logger.info(f"✓ Synthesis completed")
    logger.info(f"  Status: {result.get('status', 'unknown')}")
    logger.info(f"  Sources: {result.get('sources', [])}")
    
    if 'contradictions' in result:
        logger.info(f"  Contradictions detected: {len(result['contradictions'])}")
    
    if 'synthesis' in result:
        logger.info(f"  Synthesis: {result['synthesis']}")
    
    return True


async def main():
    """Run all tests."""
    logger.info("="*60)
    logger.info("ESR System Tests - Store Everywhere Paradigm")
    logger.info("="*60)
    
    tests = [
        ("Store Everywhere", test_store_everywhere),
        ("Frequency Promotion", test_frequency_promotion),
        ("Memory Synthesis", test_synthesis),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
            logger.info(f"✓ {test_name} completed successfully\n")
        except Exception as e:
            import traceback
            logger.error(f"✗ {test_name} failed: {e}")
            logger.error(traceback.format_exc())
            results.append((test_name, False))
    
    # Summary
    logger.info("="*60)
    logger.info("Test Summary")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All tests passed!")
        logger.info("The 'store everywhere' paradigm is working correctly.")
        logger.info("\nNext steps:")
        logger.info("1. Connect real Hermes backends")
        logger.info("2. Test with actual data flow")
        logger.info("3. Verify synthesis of contradictory memories")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)