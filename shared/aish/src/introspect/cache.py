#!/usr/bin/env python3
"""
IntrospectionCache - Performance caching for introspection results.

Caches introspection results to avoid repeated analysis while ensuring
the cache stays fresh when files change.
"""

import os
import time
import json
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path

# Import landmarks with fallback
try:
    from landmarks import (
        state_checkpoint,
        performance_boundary
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator


@state_checkpoint(
    title="Introspection Cache",
    state_type="cache",
    description="Two-tier cache (memory + disk) for introspection results",
    persistence=True,
    consistency_requirements="File modification time aware",
    rationale="First introspection takes ~200ms due to imports, cached access is <5ms"
)
class IntrospectionCache:
    """Cache for introspection results with file change detection."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the cache.
        
        Args:
            cache_dir: Directory to store cache files. Defaults to ~/.aish/cache
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.aish/cache/introspection")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for current session
        self.memory_cache = {}
        
        # Track file modification times
        self.file_mtimes = {}
    
    def get(self, key: str, file_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached introspection result.
        
        Args:
            key: Cache key (usually class name or file path)
            file_path: Optional source file to check for modifications
            
        Returns:
            Cached data if valid, None if stale or missing
        """
        # Check memory cache first
        if key in self.memory_cache:
            if self._is_cache_valid(key, file_path):
                return self.memory_cache[key]['data']
        
        # Check disk cache
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache_entry = json.load(f)
                
                if self._is_cache_valid(key, file_path, cache_entry):
                    # Load into memory cache
                    self.memory_cache[key] = cache_entry
                    return cache_entry['data']
            except (json.JSONDecodeError, KeyError):
                # Invalid cache file, remove it
                cache_file.unlink(missing_ok=True)
        
        return None
    
    def set(self, key: str, data: Dict[str, Any], file_path: Optional[str] = None):
        """
        Cache introspection result.
        
        Args:
            key: Cache key
            data: Data to cache
            file_path: Optional source file for modification tracking
        """
        cache_entry = {
            'data': data,
            'timestamp': time.time(),
            'file_path': file_path
        }
        
        if file_path and os.path.exists(file_path):
            cache_entry['file_mtime'] = os.path.getmtime(file_path)
        
        # Update memory cache
        self.memory_cache[key] = cache_entry
        
        # Write to disk cache
        cache_file = self._get_cache_file(key)
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_entry, f, indent=2)
        except Exception:
            # Don't fail if we can't write cache
            pass
    
    def invalidate(self, key: str):
        """Remove a specific cache entry."""
        # Remove from memory
        self.memory_cache.pop(key, None)
        
        # Remove from disk
        cache_file = self._get_cache_file(key)
        cache_file.unlink(missing_ok=True)
    
    def clear(self):
        """Clear all cache entries."""
        self.memory_cache.clear()
        
        # Remove all cache files
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink(missing_ok=True)
    
    @performance_boundary(
        title="Cache Invalidation Check",
        description="Validates cache entries against file modification times",
        sla="<1ms validation time",
        optimization_notes="mtime comparison avoids expensive re-introspection",
        measured_impact="Enables <5ms cached responses while ensuring freshness"
    )
    def _is_cache_valid(self, key: str, file_path: Optional[str] = None, 
                        cache_entry: Optional[Dict] = None) -> bool:
        """
        Check if cache entry is still valid.
        
        Args:
            key: Cache key
            file_path: Current file path to check
            cache_entry: Cache entry to validate (uses memory cache if None)
            
        Returns:
            True if cache is valid, False otherwise
        """
        if cache_entry is None:
            cache_entry = self.memory_cache.get(key)
            if not cache_entry:
                return False
        
        # Check age (expire after 1 hour)
        age = time.time() - cache_entry.get('timestamp', 0)
        if age > 3600:
            return False
        
        # Check file modification time if available
        cached_file = cache_entry.get('file_path')
        if cached_file and os.path.exists(cached_file):
            current_mtime = os.path.getmtime(cached_file)
            cached_mtime = cache_entry.get('file_mtime', 0)
            if current_mtime > cached_mtime:
                return False
        
        # If different file path provided, invalidate
        if file_path and file_path != cached_file:
            return False
        
        return True
    
    def _get_cache_file(self, key: str) -> Path:
        """Get path to cache file for a key."""
        # Create safe filename from key
        safe_key = hashlib.md5(key.encode()).hexdigest()[:16]
        clean_key = "".join(c if c.isalnum() or c in '-_' else '_' for c in key)[:32]
        filename = f"{clean_key}_{safe_key}.json"
        return self.cache_dir / filename
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        disk_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in disk_files)
        
        return {
            'memory_entries': len(self.memory_cache),
            'disk_entries': len(disk_files),
            'disk_size_bytes': total_size,
            'disk_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }