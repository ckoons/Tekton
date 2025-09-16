#!/usr/bin/env python3
"""
Comprehensive Test Suite for Memory System
Tests all memory components, decorators, templates, and integrations.
"""

import asyncio
import unittest
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys
from pathlib import Path

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.memory.middleware import (
    MemoryMiddleware,
    MemoryConfig,
    MemoryContext,
    InjectionStyle,
    MemoryTier,
    create_memory_middleware
)
from shared.memory.injection import (
    MemoryInjector,
    InjectionPattern,
    ConversationalInjector,
    AnalyticalInjector,
    select_pattern_for_task
)
from shared.memory.decorators import (
    with_memory,
    memory_aware,
    memory_trigger,
    collective_memory,
    memory_context,
    get_memory_functions
)
from shared.memory.collective import (
    CollectiveMemoryProtocol,
    ShareType,
    PermissionLevel,
    MemoryType,
    SharedMemory,
    MemorySharingRequest,
    get_collective_memory
)
from shared.memory.metrics import (
    MemoryMetrics,
    MetricType,
    get_memory_metrics
)


class TestMemoryMiddleware(unittest.TestCase):
    """Test memory middleware functionality."""
    
    def setUp(self):
        """Set up test middleware."""
        self.config = MemoryConfig(
            namespace="test_ci",
            injection_style=InjectionStyle.NATURAL,
            memory_tiers=[MemoryTier.RECENT, MemoryTier.SESSION],
            context_depth=10
        )
        self.middleware = MemoryMiddleware(self.config)
    
    async def test_memory_context_retrieval(self):
        """Test retrieving memory context."""
        context = await self.middleware.get_memory_context("test query")
        
        self.assertIsInstance(context, MemoryContext)
        self.assertIsNotNone(context.recent)
        self.assertIsNotNone(context.session)
    
    async def test_memory_injection_natural(self):
        """Test natural style memory injection."""
        prompt = "What is the status?"
        context = MemoryContext(
            recent=[{'content': 'System running normally'}],
            session=[{'content': 'User logged in 10 minutes ago'}]
        )
        
        enriched = await self.middleware.inject_memories(prompt, context)
        
        self.assertIn(prompt, enriched)
        self.assertNotEqual(prompt, enriched)
    
    async def test_memory_injection_structured(self):
        """Test structured style memory injection."""
        self.middleware.config.injection_style = InjectionStyle.STRUCTURED
        prompt = "Analyze the data"
        context = MemoryContext(
            domain=[{'content': 'Domain knowledge item'}]
        )
        
        enriched = await self.middleware.inject_memories(prompt, context)
        
        self.assertIn("## Domain Knowledge", enriched)
        self.assertIn("## Current Request", enriched)
    
    async def test_memory_storage(self):
        """Test storing interactions."""
        interaction = {
            'type': 'test',
            'message': 'Test message',
            'timestamp': datetime.now().isoformat()
        }
        
        success = await self.middleware.store_interaction(interaction)
        
        # Will be False without Engram, but should not error
        self.assertIsInstance(success, bool)
    
    async def test_performance_sla(self):
        """Test performance within SLA."""
        start = time.time()
        context = await self.middleware.get_memory_context("performance test")
        duration = (time.time() - start) * 1000
        
        self.assertLess(duration, self.config.performance_sla_ms)


class TestMemoryInjection(unittest.TestCase):
    """Test memory injection patterns."""
    
    def setUp(self):
        """Set up test injectors."""
        self.injector = MemoryInjector("test_ci")
        self.conv_injector = ConversationalInjector("conv_ci")
        self.anal_injector = AnalyticalInjector("anal_ci")
    
    async def test_pattern_selection(self):
        """Test automatic pattern selection."""
        patterns = {
            "Let's chat about this": InjectionPattern.CONVERSATION,
            "Analyze these metrics": InjectionPattern.ANALYSIS,
            "Create a new design": InjectionPattern.CREATIVE,
            "Debug this error": InjectionPattern.TECHNICAL,
            "Coordinate the team": InjectionPattern.COORDINATION,
            "Learn from examples": InjectionPattern.LEARNING
        }
        
        for task, expected in patterns.items():
            pattern = select_pattern_for_task(task)
            self.assertEqual(pattern, expected)
    
    async def test_conversational_injection(self):
        """Test conversational injection pattern."""
        message = "Hello, how are you?"
        enriched = await self.conv_injector.inject(message)
        
        self.assertIsInstance(enriched, str)
        self.assertIn(message, enriched)
    
    async def test_analytical_injection(self):
        """Test analytical injection pattern."""
        data = {'metrics': [1, 2, 3]}
        enriched = await self.anal_injector.inject_for_analysis(
            data, "performance"
        )
        
        self.assertIn("Analyze performance", enriched)


class TestMemoryDecorators(unittest.TestCase):
    """Test memory decorator functionality."""
    
    async def test_with_memory_decorator(self):
        """Test @with_memory decorator."""
        
        @with_memory(namespace="test", store_inputs=True, store_outputs=True)
        async def test_function(message: str) -> str:
            return f"Response to: {message}"
        
        result = await test_function("test message")
        
        self.assertEqual(result, "Response to: test message")
        
        # Check function was registered
        functions = get_memory_functions()
        self.assertIn("test.test_function", functions)
    
    async def test_memory_aware_decorator(self):
        """Test @memory_aware decorator."""
        
        @memory_aware(namespace="test", context_depth=5)
        async def analyze_data(data: dict) -> dict:
            return {'analyzed': data}
        
        result = await analyze_data({'test': 'data'})
        
        self.assertEqual(result['analyzed']['test'], 'data')
    
    async def test_collective_memory_decorator(self):
        """Test @collective_memory decorator."""
        
        @collective_memory(
            share_with=["ci1", "ci2"],
            memory_type="test",
            visibility="team"
        )
        async def share_insight(insight: dict) -> dict:
            return insight
        
        result = await share_insight({'insight': 'test'})
        
        self.assertEqual(result['insight'], 'test')
    
    async def test_memory_trigger_decorator(self):
        """Test @memory_trigger decorator."""
        
        @memory_trigger(
            on_event="test_event",
            consolidation_type="immediate"
        )
        async def on_event(data: dict) -> dict:
            return {'processed': data}
        
        result = await on_event({'event': 'test'})
        
        self.assertEqual(result['processed']['event'], 'test')


class TestCollectiveMemory(unittest.TestCase):
    """Test collective memory protocols."""
    
    def setUp(self):
        """Set up collective memory."""
        self.collective = CollectiveMemoryProtocol()
    
    async def test_share_memory_broadcast(self):
        """Test broadcasting memory to multiple CIs."""
        memory_id = await self.collective.share_memory(
            memory_item={'data': 'test'},
            owner="ci1",
            recipients=["ci2", "ci3"],
            share_type=ShareType.BROADCAST,
            memory_type=MemoryType.EXPERIENCE
        )
        
        self.assertIsNotNone(memory_id)
        self.assertIn(memory_id, self.collective.shared_memories)
    
    async def test_share_memory_whisper(self):
        """Test whispering memory to specific CI."""
        memory_id = await self.collective.whisper_memory(
            memory_item={'secret': 'data'},
            from_ci="ci1",
            to_ci="ci2",
            expires_in=timedelta(minutes=5)
        )
        
        self.assertIsNotNone(memory_id)
        
        # Check expiration is set
        memory = self.collective.shared_memories[memory_id]
        self.assertTrue(any(
            perm.expires_at is not None 
            for perm in memory.permissions
        ))
    
    async def test_memory_permissions(self):
        """Test memory access permissions."""
        memory_id = await self.collective.share_memory(
            memory_item={'data': 'restricted'},
            owner="ci1",
            recipients=["ci2"],
            share_type=ShareType.WHISPER,
            memory_type=MemoryType.EXPERIENCE
        )
        
        memory = self.collective.shared_memories[memory_id]
        
        # Owner can access
        self.assertTrue(memory.can_access("ci1"))
        
        # Recipient can access
        self.assertTrue(memory.can_access("ci2"))
        
        # Others cannot access
        self.assertFalse(memory.can_access("ci3"))
    
    async def test_memory_channels(self):
        """Test memory channel creation and broadcasting."""
        # Create channel
        success = await self.collective.create_memory_channel(
            "test_channel",
            ["ci1", "ci2", "ci3"],
            MemoryType.COLLABORATION
        )
        
        self.assertTrue(success)
        self.assertIn("test_channel", self.collective.memory_channels)
        
        # Broadcast to channel
        memory_id = await self.collective.broadcast_to_channel(
            "test_channel",
            {'message': 'channel test'},
            "ci1"
        )
        
        self.assertIsNotNone(memory_id)
    
    async def test_memory_sync(self):
        """Test memory synchronization between CIs."""
        # Create some memories
        await self.collective.share_memory(
            {'data': 'from_ci1'},
            "ci1",
            [],
            ShareType.SYNC,
            MemoryType.EXPERIENCE
        )
        
        # Sync memories
        synced = await self.collective.sync_memories(
            "ci1",
            "ci2"
        )
        
        self.assertGreaterEqual(synced, 0)
        self.assertIn(("ci1", "ci2"), self.collective.sync_pairs)
    
    async def test_gift_memory(self):
        """Test gifting memory ownership."""
        # Create memory
        memory_id = await self.collective.share_memory(
            {'data': 'gift'},
            "ci1",
            [],
            ShareType.BROADCAST,
            MemoryType.EXPERIENCE
        )
        
        # Gift to another CI
        success = await self.collective.gift_memory(
            memory_id,
            "ci1",
            "ci2"
        )
        
        self.assertTrue(success)
        
        # Check ownership changed
        memory = self.collective.shared_memories[memory_id]
        self.assertEqual(memory.owner, "ci2")


class TestMemoryMetrics(unittest.TestCase):
    """Test memory metrics system."""
    
    def setUp(self):
        """Set up metrics."""
        self.metrics = MemoryMetrics()
    
    async def test_record_storage_metrics(self):
        """Test recording storage metrics."""
        await self.metrics.record_storage(
            ci_name="test_ci",
            size=1024,
            latency_ms=50,
            success=True
        )
        
        # Check metrics were recorded
        self.assertIn(MetricType.STORAGE_COUNT, self.metrics.metrics)
        self.assertIn(MetricType.STORAGE_SIZE, self.metrics.metrics)
        self.assertIn(MetricType.STORAGE_LATENCY, self.metrics.metrics)
    
    async def test_record_retrieval_metrics(self):
        """Test recording retrieval metrics."""
        await self.metrics.record_retrieval(
            ci_name="test_ci",
            query="test query",
            results_count=10,
            relevant_count=8,
            total_possible=12,
            latency_ms=30
        )
        
        # Check precision and recall calculated
        self.assertIn(MetricType.RETRIEVAL_PRECISION, self.metrics.metrics)
        self.assertIn(MetricType.RETRIEVAL_RECALL, self.metrics.metrics)
    
    async def test_health_score_calculation(self):
        """Test health score calculation."""
        # Record some metrics
        await self.metrics.record_storage("test_ci", 100, 20)
        await self.metrics.record_retrieval(
            "test_ci", "query", 10, 9, 10, 15
        )
        await self.metrics.record_cache_hit("test_ci", True)
        
        health = self.metrics.get_health_score()
        
        self.assertIsNotNone(health)
        self.assertGreaterEqual(health.overall_score, 0)
        self.assertLessEqual(health.overall_score, 100)
    
    async def test_metric_aggregation(self):
        """Test metric aggregation."""
        # Record multiple metrics
        for i in range(10):
            await self.metrics.record_storage(
                "test_ci",
                100 + i * 10,
                20 + i,
                True
            )
        
        # Aggregate
        aggregation = self.metrics.aggregate_metrics(
            MetricType.STORAGE_LATENCY,
            timedelta(hours=1)
        )
        
        self.assertIsNotNone(aggregation)
        self.assertEqual(aggregation.count, 10)
        self.assertGreater(aggregation.mean, 0)
    
    async def test_optimization_suggestions(self):
        """Test optimization suggestion generation."""
        # Create poor metrics
        for i in range(20):
            await self.metrics.record_storage("test_ci", 1000, 150)  # High latency
            await self.metrics.record_cache_hit("test_ci", False)  # Low cache hits
        
        suggestions = self.metrics.get_optimization_suggestions()
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)


class TestMemoryIntegration(unittest.TestCase):
    """Test integration with CIs."""
    
    async def test_apollo_integration(self):
        """Test Apollo memory integration."""
        from Apollo.apollo.core.memory_integration import ApolloWithMemory
        
        apollo = ApolloWithMemory()
        
        # Test prediction with memory
        result = await apollo.predict_and_coordinate(
            context={'type': 'test'},
            team=['athena', 'metis']
        )
        
        self.assertIn('prediction', result)
        self.assertIn('coordination', result)
        self.assertIn('confidence', result)
    
    async def test_athena_integration(self):
        """Test Athena memory integration."""
        from Athena.athena.core.memory_integration import AthenaWithMemory
        
        athena = AthenaWithMemory()
        
        # Test strategic analysis
        result = await athena.analyze_strategy(
            situation={'context': 'test'},
            objectives=['obj1', 'obj2'],
            constraints={'time': 'limited'}
        )
        
        self.assertIn('analysis', result)
        self.assertIn('recommendations', result)
        self.assertIn('confidence', result)


class TestEndToEnd(unittest.TestCase):
    """End-to-end memory system tests."""
    
    async def test_full_memory_flow(self):
        """Test complete memory flow from storage to retrieval."""
        # Create CI with memory
        config = MemoryConfig(
            namespace="e2e_test",
            injection_style=InjectionStyle.NATURAL,
            memory_tiers=[MemoryTier.RECENT, MemoryTier.SESSION]
        )
        middleware = MemoryMiddleware(config)
        
        # Store interaction
        await middleware.store_interaction({
            'type': 'message',
            'content': 'Test message',
            'timestamp': datetime.now().isoformat()
        })
        
        # Retrieve and inject
        prompt = "What was the last message?"
        enriched = await middleware.inject_memories(prompt)
        
        self.assertIn(prompt, enriched)
    
    async def test_collective_learning(self):
        """Test collective learning between CIs."""
        collective = CollectiveMemoryProtocol()
        
        # CI1 discovers something
        discovery_id = await collective.share_memory(
            {'discovery': 'New pattern found'},
            "ci1",
            ["ci2", "ci3"],
            ShareType.BROADCAST,
            MemoryType.BREAKTHROUGH
        )
        
        # CI2 retrieves it
        memories = await collective.retrieve_shared_memory(
            "ci2",
            memory_type=MemoryType.BREAKTHROUGH
        )
        
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].id, discovery_id)
        
        # CI2 builds on it
        enhancement_id = await collective.share_memory(
            {'enhanced': 'Pattern improved', 'based_on': discovery_id},
            "ci2",
            ["ci1", "ci3"],
            ShareType.BROADCAST,
            MemoryType.BREAKTHROUGH
        )
        
        # Check collective learning
        all_breakthroughs = await collective.retrieve_shared_memory(
            "ci3",
            memory_type=MemoryType.BREAKTHROUGH
        )
        
        self.assertEqual(len(all_breakthroughs), 2)


# Test runner
async def run_all_tests():
    """Run all async tests."""
    test_classes = [
        TestMemoryMiddleware,
        TestMemoryInjection,
        TestMemoryDecorators,
        TestCollectiveMemory,
        TestMemoryMetrics,
        TestMemoryIntegration,
        TestEndToEnd
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run async tests
    for test in suite:
        if hasattr(test, '_testMethodName'):
            method = getattr(test, test._testMethodName)
            if asyncio.iscoroutinefunction(method):
                try:
                    await method()
                    print(f"✓ {test._testMethodName}")
                except Exception as e:
                    print(f"✗ {test._testMethodName}: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("MEMORY SYSTEM COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    asyncio.run(run_all_tests())
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)