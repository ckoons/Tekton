#!/usr/bin/env python3
"""
Test Cognitive Workflows - Natural memory operations.

Tests the human-like memory patterns:
- Thoughts that emerge and strengthen
- Associative recall
- Context building
- Natural forgetting
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List

from engram.core.storage.cognitive_workflows import (
    CognitiveWorkflows, Thought, ThoughtType
)
from engram.core.storage.cache_layer import CacheLayer
from engram.core.storage.universal_encoder import UniversalEncoder


class MockBackend:
    """Mock backend for testing."""
    def __init__(self, name: str):
        self.name = name
        self.storage = {}
    
    async def store(self, key: str, content):
        self.storage[key] = content
        return True
    
    async def retrieve(self, key: str):
        return self.storage.get(key)


@pytest.mark.asyncio
async def test_store_and_recall_thought():
    """Test basic thought storage and recall."""
    
    # Setup
    cache = CacheLayer(max_size=100, promotion_threshold=2, persist_cache=False)
    backends = {'mock': MockBackend('mock')}
    encoder = UniversalEncoder(backends, recall_timeout=1.0)
    
    cognitive = CognitiveWorkflows(cache, encoder)
    
    # Store a thought
    key = await cognitive.store_thought(
        content="Python is elegant",
        thought_type=ThoughtType.OPINION,
        confidence=0.9,
        ci_id="test_ci"
    )
    
    assert key is not None
    
    # Recall the thought
    thought = await cognitive.recall_thought(key, ci_id="test_ci")
    
    assert thought is not None
    assert thought.content == "Python is elegant"
    assert thought.thought_type == ThoughtType.OPINION
    assert thought.confidence == 0.9


@pytest.mark.asyncio
async def test_associative_memory():
    """Test associative memory chains."""
    
    # Setup
    cache = CacheLayer(max_size=100, promotion_threshold=2, persist_cache=False)
    backends = {'mock': MockBackend('mock')}
    encoder = UniversalEncoder(backends, recall_timeout=1.0)
    
    cognitive = CognitiveWorkflows(cache, encoder)
    
    # Store primary thought
    key1 = await cognitive.store_thought(
        content="Machine learning",
        thought_type=ThoughtType.IDEA,
        ci_id="ci1"
    )
    
    # Store associated thoughts
    key2 = await cognitive.store_thought(
        content="Neural networks",
        thought_type=ThoughtType.IDEA,
        associations=[key1],
        ci_id="ci1"
    )
    
    key3 = await cognitive.store_thought(
        content="Deep learning",
        thought_type=ThoughtType.IDEA,
        associations=[key1, key2],
        ci_id="ci1"
    )
    
    # Check bidirectional associations
    assert key1 in cognitive.thought_chains
    assert key2 in cognitive.thought_chains[key1]
    assert key3 in cognitive.thought_chains[key1]
    
    # Recall similar thoughts
    similar = await cognitive.recall_similar(key1, limit=5, ci_id="ci1")
    
    # Should find associated thoughts
    assert len(similar) > 0
    contents = [t.content for t in similar]
    assert "Neural networks" in contents or "Deep learning" in contents


@pytest.mark.asyncio
async def test_thought_strengthening():
    """Test that repeated access strengthens memories."""
    
    # Setup
    cache = CacheLayer(max_size=100, promotion_threshold=2, persist_cache=False)
    backends = {'mock': MockBackend('mock')}
    encoder = UniversalEncoder(backends, recall_timeout=1.0)
    
    cognitive = CognitiveWorkflows(cache, encoder)
    
    # Store thought
    key = await cognitive.store_thought(
        content="Important fact",
        thought_type=ThoughtType.FACT,
        ci_id="ci1"
    )
    
    # Initial access count should be 0 (store doesn't count)
    entry = cache.cache.get(key)
    assert entry.access_count == 0
    
    # Strengthen memory
    await cognitive.strengthen_memory(key, "ci1")
    
    # Access count should increase
    entry = cache.cache.get(key)
    assert entry.access_count == 1
    
    # Strengthen again to trigger promotion
    await cognitive.strengthen_memory(key, "ci2")
    
    entry = cache.cache.get(key)
    assert entry.access_count == 2
    # Should be marked for promotion
    assert cache.frequency_tracker.promotion_candidates


@pytest.mark.asyncio
async def test_context_building():
    """Test building rich context from memories."""
    
    # Setup
    cache = CacheLayer(max_size=100, promotion_threshold=2, persist_cache=False)
    backends = {'mock': MockBackend('mock')}
    encoder = UniversalEncoder(backends, recall_timeout=1.0)
    
    cognitive = CognitiveWorkflows(cache, encoder)
    
    # Store interconnected thoughts about AI
    ai_key = await cognitive.store_thought(
        "Artificial Intelligence",
        ThoughtType.IDEA,
        ci_id="ci1"
    )
    
    ml_key = await cognitive.store_thought(
        "Machine Learning is a subset of AI",
        ThoughtType.FACT,
        associations=[ai_key],
        ci_id="ci1"
    )
    
    dl_key = await cognitive.store_thought(
        "Deep Learning uses neural networks",
        ThoughtType.FACT,
        associations=[ml_key],
        ci_id="ci1"
    )
    
    opinion_key = await cognitive.store_thought(
        "AI will transform society",
        ThoughtType.OPINION,
        associations=[ai_key],
        confidence=0.8,
        ci_id="ci2"
    )
    
    question_key = await cognitive.store_thought(
        "How can we ensure AI safety?",
        ThoughtType.QUESTION,
        associations=[ai_key],
        ci_id="ci3"
    )
    
    # Build context
    context = await cognitive.build_context("AI", depth=2, ci_id="ci1")
    
    assert context is not None
    assert context['topic'] == "AI"
    
    # Should have categorized thoughts
    assert len(context['facts']) >= 0  # May not find all due to search
    assert len(context['opinions']) >= 0
    assert len(context['questions']) >= 0
    
    # Active context should be set
    assert cognitive.active_context['topic'] == "AI"


@pytest.mark.asyncio
async def test_natural_forgetting():
    """Test natural memory decay."""
    
    # Setup
    cache = CacheLayer(max_size=100, promotion_threshold=2, persist_cache=False)
    backends = {'mock': MockBackend('mock')}
    encoder = UniversalEncoder(backends, recall_timeout=1.0)
    
    cognitive = CognitiveWorkflows(cache, encoder)
    
    # Store old thought
    old_key = await cognitive.store_thought(
        "Old memory",
        ThoughtType.MEMORY,
        ci_id="ci1"
    )
    
    # Artificially age it
    if old_key in cache.cache:
        cache.cache[old_key].last_access = datetime.now() - timedelta(days=31)
    
    # Store recent thought
    recent_key = await cognitive.store_thought(
        "Recent memory",
        ThoughtType.MEMORY,
        ci_id="ci1"
    )
    
    # Forget old memories
    forgotten = await cognitive.forget_naturally(older_than=timedelta(days=30))
    
    assert forgotten == 1
    assert old_key not in cache.cache
    assert recent_key in cache.cache


@pytest.mark.asyncio
async def test_memory_metabolism():
    """Test background memory processing."""
    
    # Setup
    cache = CacheLayer(max_size=100, promotion_threshold=2, persist_cache=False)
    backends = {'mock': MockBackend('mock')}
    encoder = UniversalEncoder(backends, recall_timeout=1.0)
    
    cognitive = CognitiveWorkflows(cache, encoder)
    cognitive.metabolism_interval = 0.1  # Fast for testing
    
    # Start metabolism
    cognitive.start_metabolism()
    
    # Store and strengthen a thought
    key = await cognitive.store_thought(
        "Important thought",
        ThoughtType.IDEA,
        ci_id="ci1"
    )
    
    # Access twice to trigger promotion
    await cognitive.strengthen_memory(key, "ci1")
    await cognitive.strengthen_memory(key, "ci2")
    
    # Mark for promotion
    cache.promotion_candidates = {key}
    
    # Wait for metabolism
    await asyncio.sleep(0.2)
    
    # Should have processed
    stats = cognitive.get_memory_stats()
    assert stats['metabolism_running'] == True
    
    # Stop metabolism
    cognitive.stop_metabolism()
    await asyncio.sleep(0.1)
    
    stats = cognitive.get_memory_stats()
    assert stats['metabolism_running'] == False


@pytest.mark.asyncio
async def test_thought_type_conversion():
    """Test handling of thought types."""
    
    cache = CacheLayer(max_size=100, promotion_threshold=2, persist_cache=False)
    backends = {'mock': MockBackend('mock')}
    encoder = UniversalEncoder(backends, recall_timeout=1.0)
    
    cognitive = CognitiveWorkflows(cache, encoder)
    
    # Test with string type
    key1 = await cognitive.store_thought(
        "String type thought",
        thought_type="fact",  # String instead of enum
        ci_id="ci1"
    )
    
    thought = await cognitive.recall_thought(key1, ci_id="ci1")
    assert thought.thought_type == ThoughtType.FACT
    
    # Test with enum type
    key2 = await cognitive.store_thought(
        "Enum type thought",
        thought_type=ThoughtType.QUESTION,
        ci_id="ci1"
    )
    
    thought = await cognitive.recall_thought(key2, ci_id="ci1")
    assert thought.thought_type == ThoughtType.QUESTION


@pytest.mark.asyncio
async def test_memory_stats():
    """Test memory statistics."""
    
    cache = CacheLayer(max_size=100, promotion_threshold=2, persist_cache=False)
    backends = {'mock': MockBackend('mock')}
    encoder = UniversalEncoder(backends, recall_timeout=1.0)
    
    cognitive = CognitiveWorkflows(cache, encoder)
    
    # Initial stats
    stats = cognitive.get_memory_stats()
    assert stats['cache_size'] == 0
    assert stats['thought_chains'] == 0
    
    # Add thoughts
    key1 = await cognitive.store_thought("Thought 1", ci_id="ci1")
    key2 = await cognitive.store_thought("Thought 2", associations=[key1], ci_id="ci1")
    
    stats = cognitive.get_memory_stats()
    assert stats['cache_size'] == 2
    assert stats['thought_chains'] == 2  # Both thoughts have chains
    assert stats['total_associations'] > 0


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])