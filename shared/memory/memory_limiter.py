"""
Memory Limiter for Tekton Memory System
Prevents excessive memory usage by enforcing limits and cleanup.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import deque
import sys
import gc

logger = logging.getLogger(__name__)


class MemoryLimiter:
    """
    Enforces memory limits to prevent excessive RAM usage.
    
    Features:
    - Size limits per tier
    - Automatic cleanup
    - LRU eviction
    - Memory pressure monitoring
    """
    
    # VERY conservative defaults - ~1-2MB total memory overhead
    DEFAULT_LIMITS = {
        'recent': 5,         # Only keep last 5 recent items (~50KB)
        'session': 10,       # Very limited session context (~100KB)
        'domain': 20,        # Minimal domain knowledge (~200KB)
        'associations': 10,  # Minimal associations (~100KB)
        'collective': 5      # Minimal collective memory (~50KB)
    }
    
    # Maximum total items across all tiers (target ~1MB total)
    MAX_TOTAL_ITEMS = 50
    
    # Maximum size per item (characters) - ~10KB per item
    MAX_ITEM_SIZE = 1000
    
    def __init__(self, ci_name: str, custom_limits: Optional[Dict[str, int]] = None):
        """
        Initialize memory limiter.
        
        Args:
            ci_name: Name of the CI
            custom_limits: Optional custom tier limits
        """
        self.ci_name = ci_name
        self.limits = {**self.DEFAULT_LIMITS, **(custom_limits or {})}
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(minutes=5)
        
        # Use deques for automatic size limiting
        self.memory_stores = {
            tier: deque(maxlen=limit)
            for tier, limit in self.limits.items()
        }
        
        logger.info(f"Memory limiter initialized for {ci_name} with limits: {self.limits}")
    
    def add_memory(self, tier: str, item: Dict[str, Any]) -> bool:
        """
        Add memory item with size enforcement.
        
        Args:
            tier: Memory tier
            item: Memory item to add
            
        Returns:
            True if added, False if rejected
        """
        # Check tier exists
        if tier not in self.memory_stores:
            logger.warning(f"Unknown memory tier: {tier}")
            return False
        
        # Truncate large items
        item = self._truncate_item(item)
        
        # Check total memory pressure
        if self._check_memory_pressure():
            self._emergency_cleanup()
        
        # Add to deque (automatically removes oldest if at limit)
        self.memory_stores[tier].append(item)
        
        # Periodic cleanup
        if datetime.now() - self.last_cleanup > self.cleanup_interval:
            self._periodic_cleanup()
        
        return True
    
    def get_memories(self, tier: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get memories from a tier.
        
        Args:
            tier: Memory tier
            limit: Optional limit on returned items
            
        Returns:
            List of memory items
        """
        if tier not in self.memory_stores:
            return []
        
        memories = list(self.memory_stores[tier])
        
        if limit:
            # Return most recent items
            return memories[-limit:]
        
        return memories
    
    def _truncate_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Truncate large memory items."""
        # Convert to string to check size
        item_str = str(item)
        
        if len(item_str) > self.MAX_ITEM_SIZE:
            # Truncate content field if it exists
            if 'content' in item and isinstance(item['content'], str):
                max_content = self.MAX_ITEM_SIZE - 200  # Leave room for metadata
                item['content'] = item['content'][:max_content] + '... [truncated]'
            
            # Truncate other string fields
            for key, value in item.items():
                if isinstance(value, str) and len(value) > 1000:
                    item[key] = value[:1000] + '... [truncated]'
        
        return item
    
    def _check_memory_pressure(self) -> bool:
        """Check if memory usage is high."""
        total_items = sum(len(store) for store in self.memory_stores.values())
        
        # Check total item count
        if total_items > self.MAX_TOTAL_ITEMS:
            return True
        
        # Try to check process memory if available
        try:
            import psutil
            process = psutil.Process()
            memory_percent = process.memory_percent()
            
            # If using more than 50% of system memory, trigger cleanup
            if memory_percent > 50:
                logger.warning(f"High memory usage detected: {memory_percent:.1f}%")
                return True
        except ImportError:
            pass  # psutil not available
        except Exception as e:
            logger.debug(f"Could not check memory pressure: {e}")
        
        return False
    
    def _emergency_cleanup(self):
        """Emergency cleanup when memory pressure is high."""
        logger.warning(f"Emergency memory cleanup for {self.ci_name}")
        
        # Reduce all stores to half their limit
        for tier, store in self.memory_stores.items():
            target_size = self.limits[tier] // 2
            while len(store) > target_size:
                store.popleft()  # Remove oldest
        
        # Force garbage collection
        gc.collect()
        
        self.last_cleanup = datetime.now()
    
    def _periodic_cleanup(self):
        """Regular cleanup of old items."""
        now = datetime.now()
        
        for tier, store in self.memory_stores.items():
            # Remove items older than threshold
            if tier == 'recent':
                threshold = timedelta(minutes=30)
            elif tier == 'session':
                threshold = timedelta(hours=2)
            else:
                threshold = timedelta(days=1)
            
            # Check timestamps and remove old items
            temp_list = list(store)
            store.clear()
            
            for item in temp_list:
                # Check if item has timestamp
                if 'timestamp' in item:
                    try:
                        item_time = datetime.fromisoformat(item['timestamp'])
                        if now - item_time < threshold:
                            store.append(item)
                    except:
                        store.append(item)  # Keep if can't parse timestamp
                else:
                    store.append(item)  # Keep items without timestamp
            
            # Ensure we don't exceed limit
            while len(store) > self.limits[tier]:
                store.popleft()
        
        self.last_cleanup = now
    
    def clear_tier(self, tier: str):
        """Clear all memories in a tier."""
        if tier in self.memory_stores:
            self.memory_stores[tier].clear()
            logger.info(f"Cleared memory tier '{tier}' for {self.ci_name}")
    
    def clear_all(self):
        """Clear all memory stores."""
        for store in self.memory_stores.values():
            store.clear()
        
        # Force garbage collection
        gc.collect()
        
        logger.info(f"Cleared all memory for {self.ci_name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        stats = {
            'ci_name': self.ci_name,
            'tier_counts': {
                tier: len(store)
                for tier, store in self.memory_stores.items()
            },
            'total_items': sum(len(store) for store in self.memory_stores.values()),
            'tier_limits': self.limits,
            'last_cleanup': self.last_cleanup.isoformat()
        }
        
        # Add memory info if available
        try:
            import psutil
            process = psutil.Process()
            stats['process_memory_mb'] = process.memory_info().rss / 1024 / 1024
            stats['process_memory_percent'] = process.memory_percent()
        except:
            pass
        
        return stats


# Global limiters per CI
_limiters: Dict[str, MemoryLimiter] = {}


def get_memory_limiter(ci_name: str) -> MemoryLimiter:
    """
    Get or create memory limiter for a CI.
    
    Args:
        ci_name: Name of the CI
        
    Returns:
        MemoryLimiter instance
    """
    if ci_name not in _limiters:
        _limiters[ci_name] = MemoryLimiter(ci_name)
    return _limiters[ci_name]


def cleanup_all_memory():
    """Emergency cleanup of all CI memory."""
    logger.warning("Performing global memory cleanup")
    
    for ci_name, limiter in _limiters.items():
        limiter.clear_all()
    
    # Clear the limiters themselves
    _limiters.clear()
    
    # Force garbage collection
    gc.collect()
    
    logger.info("Global memory cleanup complete")