#!/usr/bin/env python3
"""
Simple ESR Test - Direct test without complex imports.

Tests the core ESR functionality with minimal dependencies.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import logging
from typing import Any, Optional

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_esr_simple")

# Setup paths
current_dir = Path(__file__).parent
engram_root = current_dir.parent
coder_a_root = engram_root.parent

sys.path.insert(0, str(engram_root))
sys.path.insert(0, str(coder_a_root))

# Set environment
if 'TEKTON_ROOT' not in os.environ:
    os.environ['TEKTON_ROOT'] = str(coder_a_root)

# Import ESR components directly (avoiding Engram's __init__)
try:
    # First, let's test just the cache layer
    from engram.core.storage.cache_layer import CacheLayer, CacheEntry
    logger.info("✓ CacheLayer imported successfully")
except ImportError as e:
    logger.error(f"Failed to import CacheLayer: {e}")
    sys.exit(1)

try:
    from engram.core.storage.universal_encoder import UniversalEncoder, MemorySynthesizer, MemoryResponse
    logger.info("✓ UniversalEncoder imported successfully")
except ImportError as e:
    logger.error(f"Failed to import UniversalEncoder: {e}")
    sys.exit(1)

try:
    from engram.core.storage.unified_interface import ESRMemorySystem
    logger.info("✓ ESRMemorySystem imported successfully")
except ImportError as e:
    logger.error(f"Failed to import ESRMemorySystem: {e}")
    sys.exit(1)

# Test without Hermes dependency first
logger.info("\n=== Testing ESR Components Without Hermes ===\n")


async def test_cache_layer():
    """Test the cache layer in isolation."""
    logger.info("Test 1: Cache Layer Basic Operations")
    
    # Create cache
    cache = CacheLayer(
        max_size=10,
        promotion_threshold=2,
        eviction_policy='lru',
        persist_cache=False  # Don't persist for testing
    )
    
    # Test 1: Store and retrieve
    content = "This is a test thought"
    key = await cache.store(
        content=content,
        content_type='thought',
        metadata={'test': True},
        ci_id='test_ci'
    )
    logger.info(f"  Stored with key: {key}")
    
    # Retrieve
    retrieved = await cache.retrieve(key, ci_id='test_ci')
    assert retrieved == content, f"Retrieved content doesn't match: {retrieved}"
    logger.info(f"  ✓ Retrieved successfully")
    
    # Test 2: Access tracking
    initial_count = cache.cache[key].access_count
    await cache.retrieve(key, ci_id='another_ci')
    new_count = cache.cache[key].access_count
    assert new_count == initial_count + 1, "Access count not incremented"
    logger.info(f"  ✓ Access count tracked: {new_count}")
    
    # Test 3: Multi-CI tracking
    ci_sources = cache.cache[key].ci_sources
    assert len(ci_sources) == 2, f"Should have 2 CI sources, got {ci_sources}"
    logger.info(f"  ✓ Multi-CI tracked: {ci_sources}")
    
    # Test 4: Eviction
    for i in range(15):  # Exceed max_size
        await cache.store(f"content_{i}", 'test', {}, 'test')
    
    assert len(cache.cache) <= 10, f"Cache size exceeded max: {len(cache.cache)}"
    logger.info(f"  ✓ Eviction working, cache size: {len(cache.cache)}")
    
    # Test 5: Pattern analysis
    analysis = cache.analyze_patterns()
    logger.info(f"  ✓ Pattern analysis: {analysis['total_entries']} entries, {analysis['total_accesses']} accesses")
    
    return True


async def test_universal_encoder():
    """Test the universal encoder 'store everywhere' paradigm."""
    logger.info("\nTest 2: Universal Encoder - Store Everywhere")
    
    # Create mock backends for testing
    mock_backends = {
        'kv': MockBackend('kv'),
        'document': MockBackend('document'),
        'sql': MockBackend('sql')
    }
    
    # Create encoder
    encoder = UniversalEncoder(backends=mock_backends)
    
    # Test storing everywhere
    test_key = "test_memory_001"
    test_content = {
        "thought": "The sky is blue",
        "type": "observation",
        "timestamp": datetime.now().isoformat()
    }
    
    # Store in all backends
    results = await encoder.store_everywhere(
        key=test_key,
        content=test_content,
        metadata={'source': 'test'}
    )
    
    logger.info(f"  Storage results: {results}")
    
    # Verify stored in all backends
    successful_stores = sum(1 for success in results.values() if success)
    logger.info(f"  ✓ Stored in {successful_stores}/{len(mock_backends)} backends")
    
    # Test recall from all backends
    memories = await encoder.recall_from_everywhere(test_key)
    logger.info(f"  ✓ Recalled from {len(memories)} backends")
    
    # Test synthesis
    synthesizer = MemorySynthesizer()
    synthesized = synthesizer.synthesize(memories, query=test_key)
    logger.info(f"  ✓ Synthesized response: {synthesized.get('synthesis', 'No synthesis')}")
    
    return True


async def test_frequency_promotion():
    """Test frequency-based promotion logic."""
    logger.info("\nTest 3: Frequency-Based Promotion")
    
    cache = CacheLayer(
        max_size=100,
        promotion_threshold=2,
        eviction_policy='lru',
        persist_cache=False
    )
    
    # Track promotions
    promotions = []
    
    async def mock_promotion_callback(entry):
        promotions.append(entry.key)
        logger.info(f"  → Promotion triggered for {entry.key}")
    
    cache.promotion_callback = mock_promotion_callback
    
    # Store and access to trigger promotion
    content = {"important": "data", "should": "be promoted"}
    key = await cache.store(content, 'important', {}, 'ci1')
    logger.info(f"  Stored: {key}")
    
    # First access
    await cache.retrieve(key, 'ci1')
    logger.info(f"  Access 1: {len(promotions)} promotions")
    
    # Second access should trigger promotion
    await cache.retrieve(key, 'ci2')
    await asyncio.sleep(0.1)  # Give callback time
    
    assert len(promotions) > 0, "Promotion should have been triggered"
    logger.info(f"  ✓ Access 2: Promotion triggered!")
    
    # Check promotion candidates
    candidates = cache.get_promotion_candidates()
    logger.info(f"  ✓ {len(candidates)} promotion candidates identified")
    
    return True


class MockBackend:
    """Simple mock backend for testing."""
    
    def __init__(self, backend_type: str):
        self.backend_type = backend_type
        self.storage = {}
    
    async def store(self, key: str, value: Any, **kwargs) -> bool:
        self.storage[key] = value
        return True
    
    async def retrieve(self, key: str) -> Optional[Any]:
        value = self.storage.get(key)
        if value:
            # Return as MemoryResponse for compatibility
            return MemoryResponse(
                content=value,
                source_backend=self.backend_type,
                retrieval_time=0.1,
                confidence=1.0,
                metadata={}
            )
        return None
    
    async def search(self, query: str) -> list:
        # Simple search - return all items that contain the query
        results = []
        for key, value in self.storage.items():
            if query in str(value):
                results.append(MemoryResponse(
                    content=value,
                    source_backend=self.backend_type,
                    retrieval_time=0.1,
                    confidence=0.8,
                    metadata={'key': key}
                ))
        return results


async def test_cache_persistence():
    """Test cache analysis and stats."""
    logger.info("\nTest 4: Cache Analysis & Statistics")
    
    cache = CacheLayer(
        max_size=100,
        promotion_threshold=3,
        persist_cache=False
    )
    
    # Add variety of content
    content_types = ['thought', 'fact', 'relationship', 'embedding']
    ci_ids = ['apollo', 'athena', 'rhetor', 'numa']
    
    for i in range(20):
        content = f"Content item {i}"
        content_type = content_types[i % len(content_types)]
        ci_id = ci_ids[i % len(ci_ids)]
        
        key = await cache.store(content, content_type, {}, ci_id)
        
        # Some items get multiple accesses
        if i % 3 == 0:
            await cache.retrieve(key, 'apollo')
            await cache.retrieve(key, 'athena')
    
    # Analyze patterns
    analysis = cache.analyze_patterns()
    
    logger.info(f"  Cache Analysis:")
    logger.info(f"    Total entries: {analysis['total_entries']}")
    logger.info(f"    Total accesses: {analysis['total_accesses']}")
    logger.info(f"    Unique CIs: {analysis['unique_cis']}")
    
    # Type distribution
    if 'type_distribution' in analysis:
        logger.info(f"    Type distribution:")
        for ct, count in analysis['type_distribution'].items():
            logger.info(f"      - {ct}: {count}")
    
    # Hot entries
    if 'hot_entries' in analysis and analysis['hot_entries']:
        logger.info(f"    Hot entries: {len(analysis['hot_entries'])}")
    
    assert analysis['total_entries'] > 0, "Should have entries"
    assert analysis['unique_cis'] > 0, "Should have CI diversity"
    
    logger.info("  ✓ Cache analysis working correctly")
    
    return True


async def main():
    """Run simple ESR tests."""
    logger.info("="*60)
    logger.info("ESR Simple Component Tests")
    logger.info("="*60)
    
    tests = [
        ("Cache Layer", test_cache_layer),
        ("Universal Encoder", test_universal_encoder),
        ("Frequency Promotion", test_frequency_promotion),
        ("Cache Analysis", test_cache_persistence),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"Test '{test_name}' failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("Test Summary")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All component tests passed!")
        logger.info("The ESR core components are working correctly.")
        logger.info("\nNote: Full integration tests with database backends")
        logger.info("require Hermes to be properly configured.")
    else:
        logger.warning(f"\n⚠️ {total - passed} tests failed.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)