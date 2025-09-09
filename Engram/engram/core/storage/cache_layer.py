"""
ESR Cache Layer - Frequency-based promotion cache for cognitive memory.

This module implements the cache-first architecture that tracks access patterns
and automatically promotes frequently accessed memories to persistent storage.
"""

import time
import json
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, asdict
import asyncio

logger = logging.getLogger("engram.storage.cache")


@dataclass
class CacheEntry:
    """Represents a single entry in the cache."""
    key: str
    content: Any
    content_type: str  # 'thought', 'fact', 'relationship', 'embedding', etc.
    metadata: Dict[str, Any]
    first_access: datetime
    last_access: datetime
    access_count: int
    access_pattern: List[datetime]  # Track access times for pattern analysis
    size_bytes: int
    ci_sources: Set[str]  # Which CIs have accessed this
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['first_access'] = self.first_access.isoformat()
        data['last_access'] = self.last_access.isoformat()
        data['access_pattern'] = [dt.isoformat() for dt in self.access_pattern]
        data['ci_sources'] = list(self.ci_sources)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary."""
        data['first_access'] = datetime.fromisoformat(data['first_access'])
        data['last_access'] = datetime.fromisoformat(data['last_access'])
        data['access_pattern'] = [datetime.fromisoformat(dt) for dt in data['access_pattern']]
        data['ci_sources'] = set(data['ci_sources'])
        return cls(**data)


class FrequencyTracker:
    """Tracks access patterns and determines promotion eligibility."""
    
    def __init__(self, 
                 promotion_threshold: int = 2,
                 time_window: timedelta = timedelta(hours=1),
                 pattern_analysis: bool = True):
        """
        Initialize frequency tracker.
        
        Args:
            promotion_threshold: Number of accesses before promotion
            time_window: Time window for frequency analysis
            pattern_analysis: Whether to analyze access patterns
        """
        self.promotion_threshold = promotion_threshold
        self.time_window = time_window
        self.pattern_analysis = pattern_analysis
        
        # Track patterns
        self.access_patterns = defaultdict(list)
        self.promotion_candidates = set()
    
    def track_access(self, entry: CacheEntry, ci_id: str = None) -> bool:
        """
        Track an access and determine if promotion is needed.
        
        Args:
            entry: Cache entry being accessed
            ci_id: ID of CI accessing the entry
            
        Returns:
            True if entry should be promoted to persistent storage
        """
        now = datetime.now()
        
        # Update entry
        entry.last_access = now
        entry.access_count += 1
        entry.access_pattern.append(now)
        
        if ci_id:
            entry.ci_sources.add(ci_id)
        
        # Keep access pattern reasonable size
        if len(entry.access_pattern) > 100:
            entry.access_pattern = entry.access_pattern[-100:]
        
        # Check promotion eligibility
        should_promote = self._check_promotion(entry)
        
        if should_promote:
            self.promotion_candidates.add(entry.key)
            logger.info(f"Entry '{entry.key}' marked for promotion (accessed {entry.access_count} times)")
        
        return should_promote
    
    def _check_promotion(self, entry: CacheEntry) -> bool:
        """
        Check if entry should be promoted.
        
        Args:
            entry: Cache entry to check
            
        Returns:
            True if should be promoted
        """
        # Simple threshold check
        if entry.access_count >= self.promotion_threshold:
            return True
        
        # Pattern-based promotion (rapid repeated access)
        if self.pattern_analysis and len(entry.access_pattern) >= 2:
            recent_accesses = [
                dt for dt in entry.access_pattern
                if datetime.now() - dt < self.time_window
            ]
            
            # Promote if accessed multiple times in time window
            if len(recent_accesses) >= self.promotion_threshold:
                return True
        
        # Multi-CI access promotion (important if multiple CIs need it)
        if len(entry.ci_sources) >= 2:
            return True
        
        return False
    
    def get_access_velocity(self, entry: CacheEntry) -> float:
        """
        Calculate access velocity (accesses per hour).
        
        Args:
            entry: Cache entry
            
        Returns:
            Access velocity
        """
        if entry.access_count <= 1:
            return 0.0
        
        time_span = (entry.last_access - entry.first_access).total_seconds() / 3600
        if time_span <= 0:
            return float(entry.access_count)
        
        return entry.access_count / time_span


class CacheLayer:
    """
    ESR Cache Layer - First stop for all memory operations.
    
    Implements frequency-based promotion and natural forgetting.
    """
    
    def __init__(self,
                 max_size: int = 100000,
                 promotion_threshold: int = 2,
                 eviction_policy: str = 'lru',
                 persist_cache: bool = True,
                 cache_file: str = '/tmp/tekton/esr/cache.json'):
        """
        Initialize cache layer.
        
        Args:
            max_size: Maximum number of entries
            promotion_threshold: Accesses before promotion
            eviction_policy: 'lru', 'lfu', or 'adaptive'
            persist_cache: Whether to persist cache to disk
            cache_file: Path to cache persistence file
        """
        self.max_size = max_size
        self.eviction_policy = eviction_policy
        self.persist_cache = persist_cache
        self.cache_file = cache_file
        
        # Core structures
        self.cache = OrderedDict()  # key -> CacheEntry
        self.frequency_tracker = FrequencyTracker(promotion_threshold)
        
        # Stats
        self.stats = {
            'hits': 0,
            'misses': 0,
            'stores': 0,
            'evictions': 0,
            'promotions': 0,
            'total_size_bytes': 0
        }
        
        # Promotion callback (set by ESR system)
        self.promotion_callback = None
        
        # Load persisted cache if exists
        if self.persist_cache:
            self._load_cache()
        
        logger.info(f"Cache layer initialized (max_size={max_size}, policy={eviction_policy})")
    
    def generate_key(self, content: Any, content_type: str = None) -> str:
        """
        Generate a unique key for content.
        
        Args:
            content: Content to generate key for
            content_type: Optional type hint
            
        Returns:
            Unique key string
        """
        # Create hash from content
        if isinstance(content, dict):
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)
        
        if content_type:
            content_str = f"{content_type}:{content_str}"
        
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]
    
    async def store(self, 
                   content: Any,
                   content_type: str = 'thought',
                   metadata: Optional[Dict[str, Any]] = None,
                   ci_id: str = None) -> str:
        """
        Store content in cache.
        
        Args:
            content: Content to store
            content_type: Type of content
            metadata: Optional metadata
            ci_id: ID of CI storing content
            
        Returns:
            Key for stored content
        """
        # Generate key
        key = self.generate_key(content, content_type)
        
        # Check if already exists
        if key in self.cache:
            # Don't increment access count on store, just update CI source
            entry = self.cache[key]
            if ci_id:
                entry.ci_sources.add(ci_id)
            
            # Move to end (LRU)
            self.cache.move_to_end(key)
            self.stats['hits'] += 1
            return key
        
        # Calculate size
        content_str = json.dumps(content) if isinstance(content, dict) else str(content)
        size_bytes = len(content_str.encode())
        
        # Evict if needed
        while len(self.cache) >= self.max_size:
            self._evict()
        
        # Create new entry
        now = datetime.now()
        entry = CacheEntry(
            key=key,
            content=content,
            content_type=content_type,
            metadata=metadata or {},
            first_access=now,
            last_access=now,
            access_count=0,  # Start at 0, only increment on retrieve
            access_pattern=[],  # Don't include store as an access
            size_bytes=size_bytes,
            ci_sources={ci_id} if ci_id else set()
        )
        
        # Store
        self.cache[key] = entry
        self.stats['stores'] += 1
        self.stats['total_size_bytes'] += size_bytes
        
        logger.debug(f"Stored {content_type} with key {key} ({size_bytes} bytes)")
        
        return key
    
    async def retrieve(self, key: str, ci_id: str = None) -> Optional[Any]:
        """
        Retrieve content from cache.
        
        Args:
            key: Key to retrieve
            ci_id: ID of CI retrieving content
            
        Returns:
            Content if found, None otherwise
        """
        if key not in self.cache:
            self.stats['misses'] += 1
            return None
        
        entry = self.cache[key]
        
        # Track access
        should_promote = self.frequency_tracker.track_access(entry, ci_id)
        
        if should_promote and self.promotion_callback:
            await self.promotion_callback(entry)
            self.stats['promotions'] += 1
        
        # Move to end (LRU)
        self.cache.move_to_end(key)
        self.stats['hits'] += 1
        
        return entry.content
    
    def _evict(self) -> Optional[str]:
        """
        Evict an entry based on eviction policy.
        
        Returns:
            Key of evicted entry
        """
        if not self.cache:
            return None
        
        if self.eviction_policy == 'lru':
            # Evict least recently used
            key = next(iter(self.cache))
        
        elif self.eviction_policy == 'lfu':
            # Evict least frequently used
            key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k].access_count)
        
        elif self.eviction_policy == 'adaptive':
            # Adaptive: consider both recency and frequency
            # Score = access_count * recency_factor
            now = datetime.now()
            
            def score(k):
                entry = self.cache[k]
                recency = 1.0 / (1 + (now - entry.last_access).total_seconds())
                return entry.access_count * recency
            
            key = min(self.cache.keys(), key=score)
        
        else:
            key = next(iter(self.cache))
        
        # Remove entry
        entry = self.cache.pop(key)
        self.stats['evictions'] += 1
        self.stats['total_size_bytes'] -= entry.size_bytes
        
        logger.debug(f"Evicted {entry.content_type} with key {key}")
        
        return key
    
    def get_promotion_candidates(self) -> List[CacheEntry]:
        """
        Get entries ready for promotion.
        
        Returns:
            List of entries to promote
        """
        candidates = []
        for key in self.frequency_tracker.promotion_candidates:
            if key in self.cache:
                candidates.append(self.cache[key])
        
        return candidates
    
    def clear_promoted(self, keys: List[str]):
        """
        Clear promoted entries from promotion candidates.
        
        Args:
            keys: Keys that have been promoted
        """
        for key in keys:
            self.frequency_tracker.promotion_candidates.discard(key)
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """
        Analyze access patterns in cache.
        
        Returns:
            Pattern analysis results
        """
        if not self.cache:
            return {'status': 'empty'}
        
        # Collect statistics
        total_accesses = sum(e.access_count for e in self.cache.values())
        unique_cis = set()
        for entry in self.cache.values():
            unique_cis.update(entry.ci_sources)
        
        # Find hot entries
        hot_entries = sorted(
            self.cache.values(),
            key=lambda e: self.frequency_tracker.get_access_velocity(e),
            reverse=True
        )[:10]
        
        # Content type distribution
        type_dist = defaultdict(int)
        for entry in self.cache.values():
            type_dist[entry.content_type] += 1
        
        return {
            'total_entries': len(self.cache),
            'total_accesses': total_accesses,
            'unique_cis': len(unique_cis),
            'promotion_pending': len(self.frequency_tracker.promotion_candidates),
            'hot_entries': [
                {
                    'key': e.key,
                    'type': e.content_type,
                    'accesses': e.access_count,
                    'velocity': self.frequency_tracker.get_access_velocity(e)
                }
                for e in hot_entries
            ],
            'type_distribution': dict(type_dist),
            'cache_stats': self.stats
        }
    
    def _load_cache(self):
        """Load cache from disk if exists."""
        try:
            import os
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    for key, entry_data in data.items():
                        self.cache[key] = CacheEntry.from_dict(entry_data)
                logger.info(f"Loaded {len(self.cache)} entries from cache file")
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
    
    def _save_cache(self):
        """Save cache to disk."""
        if not self.persist_cache:
            return
        
        try:
            import os
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            data = {
                key: entry.to_dict() 
                for key, entry in self.cache.items()
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved {len(self.cache)} entries to cache file")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    async def shutdown(self):
        """Graceful shutdown - save cache to disk."""
        if self.persist_cache:
            self._save_cache()
        logger.info("Cache layer shutdown complete")