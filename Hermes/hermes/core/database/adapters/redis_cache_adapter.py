"""
Redis/Memory Cache Adapter - Implementation for cache database with Redis and memory fallback.

This module provides a concrete implementation of the CacheDatabaseAdapter
interface with Redis as primary backend and in-memory fallback.
"""

import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from collections import OrderedDict
from datetime import datetime, timedelta

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    
from hermes.core.database.adapters.cache import CacheDatabaseAdapter

logger = logging.getLogger("hermes.database.cache")


class MemoryCache:
    """Simple in-memory cache with expiration support."""
    
    def __init__(self, max_size: int = 10000):
        """
        Initialize memory cache.
        
        Args:
            max_size: Maximum number of items to store
        """
        self.cache = OrderedDict()
        self.expiry = {}
        self.max_size = max_size
        
    def set(self, key: str, value: Any, expiration: int):
        """Set a value with expiration."""
        # Remove oldest items if at capacity
        while len(self.cache) >= self.max_size:
            oldest = next(iter(self.cache))
            del self.cache[oldest]
            if oldest in self.expiry:
                del self.expiry[oldest]
        
        self.cache[key] = value
        if expiration > 0:
            self.expiry[key] = time.time() + expiration
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value if not expired."""
        if key not in self.cache:
            return None
        
        # Check expiration
        if key in self.expiry:
            if time.time() > self.expiry[key]:
                del self.cache[key]
                del self.expiry[key]
                return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def delete(self, key: str) -> bool:
        """Delete a value."""
        if key in self.cache:
            del self.cache[key]
            if key in self.expiry:
                del self.expiry[key]
            return True
        return False
    
    def flush(self):
        """Clear all values."""
        self.cache.clear()
        self.expiry.clear()
    
    def touch(self, key: str, expiration: int) -> bool:
        """Update expiration for a key."""
        if key in self.cache:
            if expiration > 0:
                self.expiry[key] = time.time() + expiration
            elif key in self.expiry:
                del self.expiry[key]
            return True
        return False
    
    def cleanup_expired(self):
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, exp_time in self.expiry.items()
            if current_time > exp_time
        ]
        for key in expired_keys:
            self.delete(key)


class RedisCacheAdapter(CacheDatabaseAdapter):
    """
    Cache adapter with Redis primary and memory fallback.
    
    Provides high-performance caching with automatic fallback
    to in-memory storage when Redis is unavailable.
    """
    
    def __init__(self, namespace: str = "default", config: Optional[Dict[str, Any]] = None):
        """
        Initialize cache adapter.
        
        Args:
            namespace: Namespace for data isolation
            config: Optional configuration (redis_url, max_memory_items, etc.)
        """
        self.namespace = namespace
        self.config = config or {}
        
        # Redis configuration
        self.redis_url = self.config.get('redis_url', 'redis://localhost:6379')
        self.redis_client = None
        self.use_redis = REDIS_AVAILABLE and self.config.get('use_redis', True)
        
        # Memory cache configuration
        max_memory_items = self.config.get('max_memory_items', 10000)
        self.memory_cache = MemoryCache(max_memory_items)
        
        # Stats tracking
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'backend': 'memory'
        }
        
        # Background cleanup task
        self.cleanup_task = None
        
        logger.info(f"Cache adapter initialized for namespace '{namespace}'")
        if self.use_redis:
            logger.info(f"Will attempt to use Redis at {self.redis_url}")
        else:
            logger.info("Using in-memory cache only")
    
    async def connect(self) -> bool:
        """
        Connect to cache backend.
        
        Returns:
            True if connection successful
        """
        # Start cleanup task for memory cache
        if not self.cleanup_task:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Try to connect to Redis if available
        if self.use_redis:
            try:
                self.redis_client = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self.redis_client.ping()
                self.stats['backend'] = 'redis'
                logger.info("Connected to Redis cache")
                return True
                
            except Exception as e:
                logger.warning(f"Failed to connect to Redis, using memory cache: {e}")
                self.redis_client = None
                self.stats['backend'] = 'memory'
        
        # Memory cache is always available
        return True
    
    async def disconnect(self) -> bool:
        """
        Disconnect from cache backend.
        
        Returns:
            True if disconnection successful
        """
        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            self.cleanup_task = None
        
        # Disconnect from Redis if connected
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
        
        logger.info("Disconnected from cache backend")
        return True
    
    def _make_key(self, key: str) -> str:
        """Create namespaced key."""
        return f"{self.namespace}:{key}"
    
    async def set(self, key: str, value: Any, expiration: int = 3600) -> bool:
        """
        Set a cached value with expiration.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expiration: Expiration time in seconds (default 1 hour)
            
        Returns:
            True if operation successful
        """
        full_key = self._make_key(key)
        self.stats['sets'] += 1
        
        # Serialize value to JSON
        try:
            json_value = json.dumps(value)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize value for key '{key}': {e}")
            return False
        
        # Try Redis first
        if self.redis_client:
            try:
                if expiration > 0:
                    await self.redis_client.setex(full_key, expiration, json_value)
                else:
                    await self.redis_client.set(full_key, json_value)
                return True
            except Exception as e:
                logger.warning(f"Redis set failed, falling back to memory: {e}")
        
        # Fall back to memory cache
        self.memory_cache.set(full_key, json_value, expiration)
        return True
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a cached value.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        full_key = self._make_key(key)
        
        # Try Redis first
        if self.redis_client:
            try:
                json_value = await self.redis_client.get(full_key)
                if json_value:
                    self.stats['hits'] += 1
                    return json.loads(json_value)
                else:
                    self.stats['misses'] += 1
                    return None
            except Exception as e:
                logger.warning(f"Redis get failed, falling back to memory: {e}")
        
        # Fall back to memory cache
        json_value = self.memory_cache.get(full_key)
        if json_value:
            self.stats['hits'] += 1
            return json.loads(json_value)
        else:
            self.stats['misses'] += 1
            return None
    
    async def delete(self, key: str) -> bool:
        """
        Delete a cached value.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if deletion successful
        """
        full_key = self._make_key(key)
        self.stats['deletes'] += 1
        
        success = False
        
        # Try Redis first
        if self.redis_client:
            try:
                deleted = await self.redis_client.delete(full_key)
                success = deleted > 0
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")
        
        # Also delete from memory cache
        memory_success = self.memory_cache.delete(full_key)
        
        return success or memory_success
    
    async def flush(self) -> bool:
        """
        Clear all cached values in this namespace.
        
        Returns:
            True if operation successful
        """
        pattern = f"{self.namespace}:*"
        
        # Clear Redis if available
        if self.redis_client:
            try:
                # Get all keys in namespace
                keys = []
                async for key in self.redis_client.scan_iter(match=pattern):
                    keys.append(key)
                
                # Delete all keys
                if keys:
                    await self.redis_client.delete(*keys)
                    
                logger.info(f"Flushed {len(keys)} keys from Redis")
            except Exception as e:
                logger.warning(f"Redis flush failed: {e}")
        
        # Clear memory cache (we'll clear all since we can't efficiently filter)
        self.memory_cache.flush()
        
        return True
    
    async def touch(self, key: str, expiration: int) -> bool:
        """
        Update expiration for a cached value.
        
        Args:
            key: Cache key
            expiration: New expiration time in seconds
            
        Returns:
            True if operation successful
        """
        full_key = self._make_key(key)
        
        success = False
        
        # Try Redis first
        if self.redis_client:
            try:
                if expiration > 0:
                    success = await self.redis_client.expire(full_key, expiration)
                else:
                    success = await self.redis_client.persist(full_key)
            except Exception as e:
                logger.warning(f"Redis touch failed: {e}")
        
        # Also update memory cache
        memory_success = self.memory_cache.touch(full_key, expiration)
        
        return success or memory_success
    
    # Additional utility methods
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists.
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists
        """
        full_key = self._make_key(key)
        
        # Try Redis first
        if self.redis_client:
            try:
                return await self.redis_client.exists(full_key) > 0
            except Exception as e:
                logger.warning(f"Redis exists check failed: {e}")
        
        # Fall back to memory cache
        return self.memory_cache.get(full_key) is not None
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary of cache stats
        """
        stats = self.stats.copy()
        
        # Calculate hit rate
        total_requests = stats['hits'] + stats['misses']
        if total_requests > 0:
            stats['hit_rate'] = stats['hits'] / total_requests
        else:
            stats['hit_rate'] = 0.0
        
        # Add memory cache info
        stats['memory_items'] = len(self.memory_cache.cache)
        stats['memory_max_items'] = self.memory_cache.max_size
        
        # Add Redis info if available
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                stats['redis_connected'] = True
                stats['redis_memory_used'] = info.get('used_memory_human', 'unknown')
            except:
                stats['redis_connected'] = False
        
        return stats
    
    async def _cleanup_loop(self):
        """Background task to clean up expired entries in memory cache."""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                self.memory_cache.cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")