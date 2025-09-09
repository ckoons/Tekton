#!/usr/bin/env python3
"""
Test ESR Memory System - Validates the cognitive memory architecture.

This script tests the core ESR functionality:
1. Cache-first storage with frequency tracking
2. Automatic promotion to appropriate backends
3. Associative retrieval across backends
4. Natural memory patterns
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
import logging

# Add paths for imports
import os
current_dir = Path(__file__).parent
engram_root = current_dir.parent
coder_a_root = engram_root.parent

# Add necessary paths
sys.path.insert(0, str(engram_root))
sys.path.insert(0, str(coder_a_root))
sys.path.insert(0, str(coder_a_root / "shared"))

# Set TEKTON_ROOT if not set
if 'TEKTON_ROOT' not in os.environ:
    os.environ['TEKTON_ROOT'] = str(coder_a_root)

from engram.core.storage.unified_interface import ESRMemorySystem
from engram.core.storage.associative_retrieval import AssociativeRetrieval

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_esr")


class ESRTester:
    """Test harness for ESR memory system."""
    
    def __init__(self):
        self.memory = None
        self.associative = None
        self.test_results = []
    
    async def setup(self):
        """Initialize ESR system for testing."""
        logger.info("=== Setting up ESR Memory System ===")
        
        # Create memory system with small cache for testing
        self.memory = ESRMemorySystem(
            cache_size=100,
            promotion_threshold=2,  # Promote after 2 accesses
            enable_backends={'sql', 'document', 'kv'},  # Start with simple backends
            config={
                'namespace': 'test_esr',
                'eviction_policy': 'lru'
            }
        )
        
        # Start the system
        await self.memory.start()
        
        # Create associative retrieval
        self.associative = AssociativeRetrieval(self.memory.backends)
        
        logger.info("ESR system initialized and started")
    
    async def teardown(self):
        """Clean up ESR system."""
        logger.info("=== Tearing down ESR Memory System ===")
        if self.memory:
            await self.memory.stop()
        logger.info("ESR system stopped")
    
    async def test_basic_storage(self):
        """Test basic store and retrieve."""
        logger.info("\n=== Test 1: Basic Storage ===")
        
        # Store a thought
        thought = "The user prefers detailed explanations"
        key = await self.memory.store(
            thought,
            content_type='insight',
            metadata={'source': 'conversation'},
            ci_id='test_ci'
        )
        
        logger.info(f"Stored thought with key: {key}")
        
        # Retrieve it
        retrieved = await self.memory.retrieve(key, ci_id='test_ci')
        
        success = retrieved == thought
        self.test_results.append(('basic_storage', success))
        
        if success:
            logger.info("✓ Basic storage test passed")
        else:
            logger.error(f"✗ Basic storage test failed: {retrieved} != {thought}")
        
        return success
    
    async def test_frequency_promotion(self):
        """Test frequency-based promotion to backend."""
        logger.info("\n=== Test 2: Frequency-Based Promotion ===")
        
        # Store a memory
        memory_content = {
            'type': 'user_preference',
            'detail': 'Likes Python examples',
            'confidence': 0.9
        }
        
        key = await self.memory.store(
            memory_content,
            content_type='preference',
            ci_id='apollo'
        )
        
        logger.info(f"Stored preference with key: {key}")
        
        # Access once (should stay in cache)
        await self.memory.retrieve(key, ci_id='apollo')
        logger.info("First access - should remain in cache")
        
        # Check promotion queue (should be empty)
        initial_queue_size = self.memory.promotion_queue.qsize()
        logger.info(f"Promotion queue size after 1 access: {initial_queue_size}")
        
        # Access second time (should trigger promotion)
        await self.memory.retrieve(key, ci_id='rhetor')
        logger.info("Second access - should trigger promotion")
        
        # Give promotion processor time to work
        await asyncio.sleep(0.5)
        
        # Check if promoted
        stats = self.memory.get_statistics()
        promoted = stats['system_stats']['promotions'] > 0
        
        self.test_results.append(('frequency_promotion', promoted))
        
        if promoted:
            logger.info(f"✓ Frequency promotion test passed - {stats['system_stats']['promotions']} promotions")
        else:
            logger.error("✗ Frequency promotion test failed - no promotions detected")
        
        return promoted
    
    async def test_content_routing(self):
        """Test content routing to appropriate backends."""
        logger.info("\n=== Test 3: Content-Based Routing ===")
        
        test_cases = [
            # (content, expected_backend)
            ("Simple key value", 'kv'),  # Simple text -> KV
            ({"name": "John", "age": 30, "city": "NYC"}, 'sql'),  # Structured -> SQL
            ({"nested": {"data": {"structure": "complex"}}, "arrays": [1, 2, 3]}, 'document'),  # Nested -> Document
        ]
        
        results = []
        
        for content, expected in test_cases:
            # Determine storage type
            storage_type = self.memory.decision_engine.decide_storage(
                content,
                content_type='test',
                metadata=None
            )
            
            logger.info(f"Content: {str(content)[:50]}... -> {storage_type.value}")
            
            # Simplified check (storage type name contains expected)
            success = expected in storage_type.value or storage_type.value in expected
            results.append(success)
        
        all_passed = all(results)
        self.test_results.append(('content_routing', all_passed))
        
        if all_passed:
            logger.info("✓ Content routing test passed")
        else:
            logger.error(f"✗ Content routing test failed: {results}")
        
        return all_passed
    
    async def test_multi_ci_access(self):
        """Test multi-CI access triggering promotion."""
        logger.info("\n=== Test 4: Multi-CI Access Pattern ===")
        
        # Store a shared insight
        shared_insight = "System performance degrades after 1000 concurrent connections"
        key = await self.memory.store(
            shared_insight,
            content_type='system_insight',
            ci_id='metis'
        )
        
        logger.info(f"Stored system insight with key: {key}")
        
        # Access from different CIs
        cis = ['apollo', 'athena', 'numa']
        for ci in cis:
            retrieved = await self.memory.retrieve(key, ci_id=ci)
            logger.info(f"CI '{ci}' accessed the insight")
        
        # Give promotion processor time
        await asyncio.sleep(0.5)
        
        # Check cache entry
        cache_entry = self.memory.cache.cache.get(key)
        multi_ci = len(cache_entry.ci_sources) > 2 if cache_entry else False
        
        self.test_results.append(('multi_ci_access', multi_ci))
        
        if multi_ci:
            logger.info(f"✓ Multi-CI access test passed - accessed by {cache_entry.ci_sources}")
        else:
            logger.error("✗ Multi-CI access test failed")
        
        return multi_ci
    
    async def test_associative_search(self):
        """Test associative search across backends."""
        logger.info("\n=== Test 5: Associative Search ===")
        
        # Store related memories
        memories = [
            ("Python is a great language for data science", 'fact'),
            ({"language": "Python", "use_case": "machine learning"}, 'structured'),
            ("The user mentioned Python in the last conversation", 'context'),
        ]
        
        keys = []
        for content, content_type in memories:
            key = await self.memory.store(content, content_type, ci_id='test')
            keys.append(key)
            # Access twice to promote
            await self.memory.retrieve(key)
            await self.memory.retrieve(key)
        
        # Give time for promotion
        await asyncio.sleep(0.5)
        
        # Search for Python-related memories
        results = await self.memory.search("Python", search_type='pattern', limit=10)
        
        found_count = len(results)
        success = found_count >= 2  # Should find at least 2 Python mentions
        
        self.test_results.append(('associative_search', success))
        
        if success:
            logger.info(f"✓ Associative search test passed - found {found_count} memories")
            for result in results:
                logger.info(f"  - From {result['source']}: {str(result['content'])[:50]}...")
        else:
            logger.error(f"✗ Associative search test failed - only found {found_count}")
        
        return success
    
    async def test_cache_analysis(self):
        """Test cache pattern analysis."""
        logger.info("\n=== Test 6: Cache Pattern Analysis ===")
        
        # Analyze patterns
        analysis = self.memory.cache.analyze_patterns()
        
        logger.info("Cache Analysis:")
        logger.info(f"  Total entries: {analysis.get('total_entries', 0)}")
        logger.info(f"  Total accesses: {analysis.get('total_accesses', 0)}")
        logger.info(f"  Unique CIs: {analysis.get('unique_cis', 0)}")
        logger.info(f"  Promotions pending: {analysis.get('promotion_pending', 0)}")
        
        # Check type distribution
        if 'type_distribution' in analysis:
            logger.info("  Content type distribution:")
            for content_type, count in analysis['type_distribution'].items():
                logger.info(f"    - {content_type}: {count}")
        
        # Check hot entries
        if 'hot_entries' in analysis and analysis['hot_entries']:
            logger.info("  Hot entries (by access velocity):")
            for entry in analysis['hot_entries'][:3]:
                logger.info(f"    - {entry['type']}: {entry['accesses']} accesses, velocity: {entry['velocity']:.2f}")
        
        success = 'total_entries' in analysis
        self.test_results.append(('cache_analysis', success))
        
        if success:
            logger.info("✓ Cache analysis test passed")
        else:
            logger.error("✗ Cache analysis test failed")
        
        return success
    
    async def test_system_statistics(self):
        """Test system statistics gathering."""
        logger.info("\n=== Test 7: System Statistics ===")
        
        stats = self.memory.get_statistics()
        
        logger.info("System Statistics:")
        logger.info(f"  Stores: {stats['system_stats']['stores']}")
        logger.info(f"  Retrievals: {stats['system_stats']['retrievals']}")
        logger.info(f"  Cache hits: {stats['system_stats']['cache_hits']}")
        logger.info(f"  Backend hits: {stats['system_stats']['backend_hits']}")
        logger.info(f"  Promotions: {stats['system_stats']['promotions']}")
        logger.info(f"  Misses: {stats['system_stats']['misses']}")
        logger.info(f"  Errors: {stats['system_stats']['errors']}")
        
        # Check routing statistics
        if 'routing_analysis' in stats:
            routing = stats['routing_analysis']
            if 'decision_distribution' in routing:
                logger.info("  Routing decisions:")
                for decision, count in routing['decision_distribution'].items():
                    logger.info(f"    - {decision}: {count}")
        
        success = stats['system_stats']['stores'] > 0
        self.test_results.append(('system_statistics', success))
        
        if success:
            logger.info("✓ System statistics test passed")
        else:
            logger.error("✗ System statistics test failed")
        
        return success
    
    async def run_all_tests(self):
        """Run all tests."""
        logger.info("\n" + "="*60)
        logger.info("Starting ESR System Tests")
        logger.info("="*60)
        
        try:
            await self.setup()
            
            # Run tests
            await self.test_basic_storage()
            await self.test_frequency_promotion()
            await self.test_content_routing()
            await self.test_multi_ci_access()
            await self.test_associative_search()
            await self.test_cache_analysis()
            await self.test_system_statistics()
            
            # Summary
            logger.info("\n" + "="*60)
            logger.info("Test Summary")
            logger.info("="*60)
            
            passed = sum(1 for _, result in self.test_results if result)
            total = len(self.test_results)
            
            for test_name, result in self.test_results:
                status = "✓ PASS" if result else "✗ FAIL"
                logger.info(f"{status}: {test_name}")
            
            logger.info(f"\nResults: {passed}/{total} tests passed")
            
            if passed == total:
                logger.info("🎉 All tests passed! ESR system is working correctly.")
            else:
                logger.warning(f"⚠️  {total - passed} tests failed. Review the logs above.")
            
        finally:
            await self.teardown()
        
        return passed == total


async def main():
    """Main test runner."""
    tester = ESRTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())