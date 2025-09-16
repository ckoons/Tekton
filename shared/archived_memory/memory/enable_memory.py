"""
Simple Memory Enabler for Tekton CIs
Allows CIs to opt-in to memory features with minimal overhead.
"""

import logging
from typing import Optional, Dict, Any
from .middleware import MemoryConfig, InjectionStyle, MemoryTier
from .memory_limiter import get_memory_limiter

logger = logging.getLogger(__name__)


def enable_minimal_memory(ci_name: str) -> MemoryConfig:
    """
    Enable minimal memory for a CI (< 500KB overhead).
    
    Only keeps last 3 interactions, no storage.
    
    Args:
        ci_name: Name of the CI
        
    Returns:
        Minimal memory configuration
    """
    logger.info(f"Enabling minimal memory for {ci_name}")
    
    # Get limiter with ultra-conservative limits
    limiter = get_memory_limiter(ci_name)
    limiter.limits = {
        'recent': 3,
        'session': 0,
        'domain': 0,
        'associations': 0,
        'collective': 0
    }
    
    return MemoryConfig(
        namespace=ci_name,
        enabled=True,
        injection_style=InjectionStyle.MINIMAL,
        memory_tiers=[MemoryTier.RECENT],
        store_inputs=False,
        store_outputs=False,
        inject_context=False,
        context_depth=3,
        max_context_size=200
    )


def enable_conversational_memory(ci_name: str) -> MemoryConfig:
    """
    Enable conversational memory for a CI (~1MB overhead).
    
    Suitable for CIs that handle conversations.
    
    Args:
        ci_name: Name of the CI
        
    Returns:
        Conversational memory configuration
    """
    logger.info(f"Enabling conversational memory for {ci_name}")
    
    # Get limiter with conservative limits
    limiter = get_memory_limiter(ci_name)
    limiter.limits = {
        'recent': 5,
        'session': 10,
        'domain': 0,
        'associations': 0,
        'collective': 0
    }
    
    return MemoryConfig(
        namespace=ci_name,
        enabled=True,
        injection_style=InjectionStyle.NATURAL,
        memory_tiers=[MemoryTier.RECENT, MemoryTier.SESSION],
        store_inputs=True,
        store_outputs=False,
        inject_context=True,
        context_depth=5,
        max_context_size=500
    )


def enable_analytical_memory(ci_name: str) -> MemoryConfig:
    """
    Enable analytical memory for a CI (~2MB overhead).
    
    Suitable for CIs that perform analysis.
    
    Args:
        ci_name: Name of the CI
        
    Returns:
        Analytical memory configuration
    """
    logger.info(f"Enabling analytical memory for {ci_name}")
    
    # Get limiter with moderate limits
    limiter = get_memory_limiter(ci_name)
    limiter.limits = {
        'recent': 5,
        'session': 10,
        'domain': 15,
        'associations': 5,
        'collective': 0
    }
    
    return MemoryConfig(
        namespace=ci_name,
        enabled=True,
        injection_style=InjectionStyle.STRUCTURED,
        memory_tiers=[
            MemoryTier.RECENT,
            MemoryTier.SESSION,
            MemoryTier.DOMAIN
        ],
        store_inputs=True,
        store_outputs=True,
        inject_context=True,
        context_depth=10,
        max_context_size=1000
    )


def disable_memory(ci_name: str):
    """
    Completely disable and clean up memory for a CI.
    
    Args:
        ci_name: Name of the CI
    """
    logger.info(f"Disabling memory for {ci_name}")
    
    # Clear all memory
    limiter = get_memory_limiter(ci_name)
    limiter.clear_all()
    
    # Return disabled config
    return MemoryConfig(
        namespace=ci_name,
        enabled=False
    )


def get_memory_usage(ci_name: str) -> Dict[str, Any]:
    """
    Get memory usage statistics for a CI.
    
    Args:
        ci_name: Name of the CI
        
    Returns:
        Memory usage statistics
    """
    limiter = get_memory_limiter(ci_name)
    stats = limiter.get_stats()
    
    # Estimate memory usage in KB
    estimated_kb = 0
    for tier, count in stats['tier_counts'].items():
        # Rough estimate: 1KB per item average
        estimated_kb += count
    
    stats['estimated_memory_kb'] = estimated_kb
    stats['estimated_memory_mb'] = estimated_kb / 1024
    
    return stats


# Example usage for CIs
"""
# In a CI that wants minimal memory:
from shared.memory.enable_memory import enable_minimal_memory

class MyCI:
    def __init__(self):
        self.memory_config = enable_minimal_memory("myci")
        # Now has minimal memory with < 500KB overhead


# In a CI that needs more memory:
from shared.memory.enable_memory import enable_analytical_memory

class AnalyticalCI:
    def __init__(self):
        self.memory_config = enable_analytical_memory("analytical")
        # Now has analytical memory with ~2MB overhead
        

# To check memory usage:
from shared.memory.enable_memory import get_memory_usage

stats = get_memory_usage("myci")
print(f"Memory usage: {stats['estimated_memory_mb']:.1f}MB")


# To disable memory:
from shared.memory.enable_memory import disable_memory

disable_memory("myci")
"""