#!/usr/bin/env python3
"""
Test Universal Encoding - Validates the "store everywhere, synthesize on recall" approach.

Casey's principle: "Don't try to be perfect, or even efficient, 
just be comprehensive and useful and that's enough."
"""

import pytest
import asyncio
import json
from datetime import datetime
from typing import Any

from engram.core.storage.universal_encoder import UniversalEncoder, MemoryResponse, MemorySynthesizer


class MockBackend:
    """Mock backend that simulates different database behaviors."""
    
    def __init__(self, name: str, delay: float = 0.1, fail_rate: float = 0.0):
        self.name = name
        self.delay = delay
        self.fail_rate = fail_rate
        self.storage = {}
    
    async def store(self, key: str, content: Any):
        """Store with simulated delay."""
        await asyncio.sleep(self.delay)
        
        import random
        if random.random() < self.fail_rate:
            raise Exception(f"{self.name} failed to store")
        
        self.storage[key] = content
        return True
    
    async def retrieve(self, key: str):
        """Retrieve with simulated delay."""
        await asyncio.sleep(self.delay)
        return self.storage.get(key)


@pytest.mark.asyncio
async def test_store_everywhere():
    """Test that content is stored in all backends."""
    
    # Create mock backends
    backends = {
        'vector': MockBackend('vector', delay=0.01),
        'graph': MockBackend('graph', delay=0.02),
        'sql': MockBackend('sql', delay=0.01),
        'document': MockBackend('document', delay=0.015),
        'kv': MockBackend('kv', delay=0.005)
    }
    
    encoder = UniversalEncoder(backends, recall_timeout=1.0)
    
    # Store content everywhere
    content = {"insight": "User prefers Python", "confidence": 0.9}
    results = await encoder.store_everywhere('key1', content, {'source': 'test'})
    
    # Should succeed in all backends
    assert all(results.values()), f"Some stores failed: {results}"
    
    # Verify content in each backend
    for backend in backends.values():
        assert 'key1' in backend.storage
        assert backend.storage['key1'] == content


@pytest.mark.asyncio
async def test_recall_with_synthesis():
    """Test recall from multiple backends with synthesis."""
    
    # Create backends with different response times
    backends = {
        'fast': MockBackend('fast', delay=0.01),
        'medium': MockBackend('medium', delay=0.05),
        'slow': MockBackend('slow', delay=0.1)
    }
    
    # Store slightly different versions (simulating real-world variance)
    await backends['fast'].store('key1', "Python is great")
    await backends['medium'].store('key1', "Python is great")  # Same
    await backends['slow'].store('key1', "Python is excellent")  # Different phrasing
    
    encoder = UniversalEncoder(backends, recall_timeout=0.5)
    
    # Recall and synthesize
    synthesis = await encoder.recall_from_everywhere(key='key1')
    
    assert synthesis is not None
    assert 'primary' in synthesis
    assert synthesis['primary'] in ["Python is great", "Python is excellent"]
    
    # Check that we got responses from all backends
    assert synthesis['metadata']['backends_responded'] == 3


@pytest.mark.asyncio
async def test_timeout_handling():
    """Test that slow backends are handled gracefully."""
    
    backends = {
        'fast': MockBackend('fast', delay=0.01),
        'very_slow': MockBackend('very_slow', delay=5.0)  # Will timeout
    }
    
    # Store in both
    await backends['fast'].store('key1', "Quick response")
    await backends['very_slow'].store('key1', "Slow response")
    
    encoder = UniversalEncoder(backends, recall_timeout=0.1)  # 100ms timeout
    
    # Recall - should get fast response, timeout on slow
    synthesis = await encoder.recall_from_everywhere(key='key1')
    
    assert synthesis is not None
    assert synthesis['primary'] == "Quick response"
    
    # Check timeout was recorded
    stats = encoder.get_statistics()
    assert stats['stats']['recall_timeouts']['very_slow'] > 0


@pytest.mark.asyncio
async def test_contradiction_detection():
    """Test that contradictions are identified."""
    
    backends = {
        'optimist': MockBackend('optimist', delay=0.01),
        'pessimist': MockBackend('pessimist', delay=0.01)
    }
    
    # Store contradictory information
    await backends['optimist'].store('key1', "Python is the best language")
    await backends['pessimist'].store('key1', "Python is not the best language")
    
    encoder = UniversalEncoder(backends, recall_timeout=1.0)
    
    # Create mock responses for synthesis
    responses = [
        MemoryResponse(
            content="Python is the best language",
            source_backend='optimist',
            retrieval_time=0.01,
            confidence=1.0,
            metadata={}
        ),
        MemoryResponse(
            content="Python is not the best language",
            source_backend='pessimist',
            retrieval_time=0.01,
            confidence=1.0,
            metadata={}
        )
    ]
    
    synthesizer = MemorySynthesizer()
    synthesis = synthesizer.synthesize(responses)
    
    # Should identify potential contradiction
    assert len(synthesis['contradictions']) > 0
    assert 'potential_negation' in synthesis['contradictions'][0]['nature']


@pytest.mark.asyncio
async def test_graceful_degradation():
    """Test that system works even when some backends fail."""
    
    backends = {
        'reliable': MockBackend('reliable', delay=0.01, fail_rate=0.0),
        'flaky': MockBackend('flaky', delay=0.01, fail_rate=0.5),
        'broken': MockBackend('broken', delay=0.01, fail_rate=1.0)
    }
    
    encoder = UniversalEncoder(backends, recall_timeout=1.0)
    
    # Store - should succeed in at least reliable backend
    results = await encoder.store_everywhere('key1', "Important data")
    
    assert results['reliable'] == True
    assert results['broken'] == False
    # 'flaky' might be True or False
    
    # Should still be able to recall
    synthesis = await encoder.recall_from_everywhere(key='key1')
    assert synthesis is not None
    assert synthesis['primary'] == "Important data"


def test_synthesis_grouping():
    """Test that similar memories are grouped."""
    
    responses = [
        MemoryResponse("Python is great", 'backend1', 0.1, 1.0, {}),
        MemoryResponse("Python is great", 'backend2', 0.1, 1.0, {}),
        MemoryResponse("Python is excellent", 'backend3', 0.1, 1.0, {}),
        MemoryResponse("JavaScript is different", 'backend4', 0.1, 1.0, {})
    ]
    
    synthesizer = MemorySynthesizer()
    synthesis = synthesizer.synthesize(responses)
    
    # Primary should be most common
    assert synthesis['primary'] == "Python is great"
    
    # Should have found consensus
    assert synthesis['consensus'] == "Python is great"
    
    # Should identify outlier
    assert len(synthesis['outliers']) > 0


@pytest.mark.asyncio
async def test_comprehensive_storage_stats():
    """Test that statistics track all operations."""
    
    backends = {
        'backend1': MockBackend('backend1', delay=0.01),
        'backend2': MockBackend('backend2', delay=0.01)
    }
    
    encoder = UniversalEncoder(backends, recall_timeout=1.0)
    
    # Perform operations
    await encoder.store_everywhere('key1', "Data 1")
    await encoder.store_everywhere('key2', "Data 2")
    await encoder.recall_from_everywhere(key='key1')
    await encoder.recall_from_everywhere(key='key2')
    await encoder.recall_from_everywhere(key='missing')  # Will miss
    
    stats = encoder.get_statistics()
    
    assert stats['stats']['total_stores'] == 2
    assert stats['stats']['total_recalls'] == 3
    assert stats['stats']['stores']['backend1'] == 2
    assert stats['stats']['stores']['backend2'] == 2
    assert stats['stats']['recalls']['backend1'] >= 2
    assert stats['stats']['recalls']['backend2'] >= 2


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])