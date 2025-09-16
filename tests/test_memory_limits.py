#!/usr/bin/env python3
"""
Test memory limits to ensure low overhead.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.memory.memory_limiter import MemoryLimiter, get_memory_limiter
from shared.memory.enable_memory import (
    enable_minimal_memory,
    enable_conversational_memory,
    enable_analytical_memory,
    get_memory_usage
)


def test_memory_limits():
    """Test that memory limits are enforced."""
    print("Testing memory limits...")
    
    # Create limiter
    limiter = MemoryLimiter("test_ci")
    
    # Try to add many items
    for i in range(100):
        limiter.add_memory('recent', {
            'content': f'Item {i}',
            'index': i
        })
    
    # Check that only 5 recent items are kept (the limit)
    recent = limiter.get_memories('recent')
    assert len(recent) <= 5, f"Too many recent items: {len(recent)}"
    
    # Check that we have the most recent items
    assert recent[-1]['index'] == 99, "Should have most recent item"
    
    print(f"✓ Memory limits enforced: {len(recent)} items in 'recent'")
    
    # Check total items
    stats = limiter.get_stats()
    total = stats['total_items']
    assert total <= 50, f"Too many total items: {total}"
    
    print(f"✓ Total items limited: {total} items")


def test_item_truncation():
    """Test that large items are truncated."""
    print("\nTesting item truncation...")
    
    limiter = MemoryLimiter("test_truncate")
    
    # Create large item
    large_content = "x" * 10000
    item = {
        'content': large_content,
        'metadata': 'test'
    }
    
    # Add it
    limiter.add_memory('recent', item)
    
    # Retrieve and check it was truncated
    recent = limiter.get_memories('recent')
    assert len(recent) > 0
    
    retrieved = recent[0]
    assert len(retrieved['content']) < 2000, f"Content not truncated: {len(retrieved['content'])}"
    assert '... [truncated]' in retrieved['content'], "Should show truncation"
    
    print(f"✓ Large items truncated: {len(retrieved['content'])} chars")


def test_memory_configurations():
    """Test different memory configurations."""
    print("\nTesting memory configurations...")
    
    # Test minimal memory
    config = enable_minimal_memory("minimal_test")
    assert config.enabled == True
    assert len(config.memory_tiers) == 1
    assert config.context_depth == 3
    print("✓ Minimal memory config created")
    
    # Test conversational memory
    config = enable_conversational_memory("conv_test")
    assert config.enabled == True
    assert len(config.memory_tiers) == 2
    assert config.context_depth == 5
    print("✓ Conversational memory config created")
    
    # Test analytical memory
    config = enable_analytical_memory("anal_test")
    assert config.enabled == True
    assert len(config.memory_tiers) == 3
    assert config.context_depth == 10
    print("✓ Analytical memory config created")


def test_memory_usage_stats():
    """Test memory usage reporting."""
    print("\nTesting memory usage stats...")
    
    # Create CI with some memories
    limiter = get_memory_limiter("stats_test")
    
    for i in range(10):
        limiter.add_memory('recent', {'item': i})
        limiter.add_memory('session', {'session': i})
    
    # Get stats
    stats = get_memory_usage("stats_test")
    
    print(f"Memory stats: {stats['tier_counts']}")
    print(f"Estimated memory: {stats['estimated_memory_kb']}KB")
    
    assert stats['estimated_memory_kb'] > 0
    assert stats['estimated_memory_mb'] < 1.0  # Should be under 1MB
    
    print(f"✓ Memory usage tracked: {stats['estimated_memory_mb']:.2f}MB")


def test_memory_cleanup():
    """Test memory cleanup."""
    print("\nTesting memory cleanup...")
    
    limiter = get_memory_limiter("cleanup_test")
    
    # Add some items
    for i in range(20):
        limiter.add_memory('recent', {'item': i})
    
    stats_before = limiter.get_stats()
    print(f"Before cleanup: {stats_before['total_items']} items")
    
    # Clear all
    limiter.clear_all()
    
    stats_after = limiter.get_stats()
    print(f"After cleanup: {stats_after['total_items']} items")
    
    assert stats_after['total_items'] == 0
    print("✓ Memory cleanup works")


if __name__ == "__main__":
    print("=" * 50)
    print("MEMORY LIMIT TESTS")
    print("=" * 50)
    
    test_memory_limits()
    test_item_truncation()
    test_memory_configurations()
    test_memory_usage_stats()
    test_memory_cleanup()
    
    print("\n" + "=" * 50)
    print("ALL TESTS PASSED")
    print("Memory overhead is properly limited")
    print("=" * 50)