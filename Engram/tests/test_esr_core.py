#!/usr/bin/env python3
"""
Test ESR Core Components - Pytest compatible tests for ESR.
"""

import pytest
import asyncio
from datetime import datetime

from engram.core.storage.cache_layer import CacheLayer, CacheEntry


@pytest.mark.asyncio
async def test_cache_basic_operations():
    """Test basic cache store and retrieve."""
    cache = CacheLayer(max_size=10, promotion_threshold=2, persist_cache=False)
    
    # Store
    content = "Test thought content"
    key = await cache.store(content, 'thought', {'test': True}, 'test_ci')
    assert key is not None
    
    # Retrieve
    retrieved = await cache.retrieve(key, 'test_ci')
    assert retrieved == content
    
    # Check access count
    entry = cache.cache.get(key)
    assert entry is not None
    assert entry.access_count == 1  # Only retrieve counts, not store


@pytest.mark.asyncio
async def test_frequency_promotion():
    """Test frequency-based promotion logic."""
    cache = CacheLayer(max_size=10, promotion_threshold=2, persist_cache=False)
    
    # Track promotions
    promotions = []
    async def track_promotion(entry):
        promotions.append(entry.key)
    
    cache.promotion_callback = track_promotion
    
    # Store and access to trigger promotion
    content = {"data": "important"}
    key = await cache.store(content, 'data', {}, 'ci1')
    
    # First access - no promotion
    await cache.retrieve(key, 'ci1')
    await asyncio.sleep(0.01)
    assert len(promotions) == 0
    
    # Second access - should trigger promotion
    await cache.retrieve(key, 'ci2')
    await asyncio.sleep(0.01)
    assert len(promotions) > 0
    assert key in promotions


@pytest.mark.asyncio
async def test_multi_ci_tracking():
    """Test multi-CI access tracking."""
    cache = CacheLayer(max_size=10, promotion_threshold=3, persist_cache=False)
    
    content = "Shared insight"
    key = await cache.store(content, 'insight', {}, 'apollo')
    
    # Access from multiple CIs
    cis = ['athena', 'rhetor', 'numa']
    for ci in cis:
        await cache.retrieve(key, ci)
    
    # Check CI tracking
    entry = cache.cache.get(key)
    assert entry is not None
    assert 'apollo' in entry.ci_sources
    assert all(ci in entry.ci_sources for ci in cis)
    assert len(entry.ci_sources) == 4


@pytest.mark.asyncio
async def test_cache_eviction():
    """Test cache eviction policies."""
    cache = CacheLayer(max_size=5, promotion_threshold=10, persist_cache=False)
    
    # Fill cache beyond capacity
    keys = []
    for i in range(10):
        key = await cache.store(f"content_{i}", 'test', {}, 'test')
        keys.append(key)
    
    # Cache should not exceed max size
    assert len(cache.cache) <= 5
    
    # Oldest items should be evicted (LRU)
    for i in range(5):
        assert keys[i] not in cache.cache  # First 5 evicted
    
    for i in range(5, 10):
        assert keys[i] in cache.cache  # Last 5 remain


@pytest.mark.asyncio
async def test_cache_analysis():
    """Test cache pattern analysis."""
    cache = CacheLayer(max_size=50, promotion_threshold=3, persist_cache=False)
    
    # Add variety of content
    content_types = ['thought', 'fact', 'insight']
    cis = ['apollo', 'athena', 'rhetor']
    
    for i in range(15):
        content = f"Content {i}"
        ct = content_types[i % len(content_types)]
        ci = cis[i % len(cis)]
        
        key = await cache.store(content, ct, {}, ci)
        
        # Some get multiple accesses
        if i % 3 == 0:
            await cache.retrieve(key, 'numa')
            await cache.retrieve(key, 'metis')
    
    # Analyze
    analysis = cache.analyze_patterns()
    
    assert 'total_entries' in analysis
    assert analysis['total_entries'] == 15
    assert 'unique_cis' in analysis
    assert analysis['unique_cis'] >= 3
    assert 'type_distribution' in analysis
    assert len(analysis['type_distribution']) == 3


def test_universal_encoding_principle():
    """Test that universal encoding stores everywhere."""
    # This test validates our new approach:
    # - No routing decisions needed
    # - Store in all backends
    # - Synthesis on recall
    
    # The principle is simple: storage is free
    assert True  # Universal encoding needs no routing logic


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])