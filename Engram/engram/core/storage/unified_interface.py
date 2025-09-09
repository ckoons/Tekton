"""
ESR Unified Interface - Orchestrates cache, decision engine, and storage backends.

This module provides the core ESR memory system that implements the cognitive
pattern of cache-first storage with automatic promotion to appropriate backends.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from pathlib import Path
import sys
import os

# Add Hermes to path for database factory
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "Hermes"))

from engram.core.storage.cache_layer import CacheLayer, CacheEntry
from engram.core.storage.storage_decision_engine import StorageDecisionEngine, StorageType
from engram.core.storage.universal_encoder import UniversalEncoder

try:
    from hermes.core.database.factory import DatabaseFactory
    from hermes.core.database.database_types import DatabaseType
    HERMES_AVAILABLE = True
except ImportError:
    HERMES_AVAILABLE = False
    logging.warning("Hermes not available - using mock storage backends")

logger = logging.getLogger("engram.storage.unified")


class MockBackend:
    """Mock backend for testing when Hermes isn't available."""
    
    def __init__(self, backend_type: str):
        self.backend_type = backend_type
        self.storage = {}
        
    async def connect(self) -> bool:
        return True
    
    async def disconnect(self) -> bool:
        return True
    
    async def store(self, key: str, value: Any) -> bool:
        self.storage[key] = value
        logger.debug(f"Mock {self.backend_type} stored: {key}")
        return True
    
    async def retrieve(self, key: str) -> Optional[Any]:
        return self.storage.get(key)


class HashIndex:
    """Simple hash index for O(1) lookups across backends."""
    
    def __init__(self, index_file: str = "/tmp/tekton/esr/hash_index.json"):
        self.index = {}  # key -> (backend_type, location_info)
        self.index_file = index_file
        self.load_index()
    
    def add(self, key: str, backend_type: str, location_info: Dict[str, Any] = None):
        """Add entry to index."""
        self.index[key] = {
            'backend': backend_type,
            'location': location_info or {},
            'indexed_at': datetime.now().isoformat()
        }
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get location info for key."""
        return self.index.get(key)
    
    def remove(self, key: str):
        """Remove entry from index."""
        self.index.pop(key, None)
    
    def save_index(self):
        """Persist index to disk."""
        try:
            os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f)
        except Exception as e:
            logger.error(f"Failed to save hash index: {e}")
    
    def load_index(self):
        """Load index from disk."""
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r') as f:
                    self.index = json.load(f)
                logger.info(f"Loaded {len(self.index)} entries from hash index")
        except Exception as e:
            logger.warning(f"Failed to load hash index: {e}")


class ESRMemorySystem:
    """
    Unified ESR Memory System - The cognitive memory architecture.
    
    Implements the pattern: Have idea → Think about it → Decide important → Store appropriately
    """
    
    def __init__(self,
                 cache_size: int = 100000,
                 promotion_threshold: int = 2,
                 enable_backends: Optional[Set[str]] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize ESR memory system.
        
        Args:
            cache_size: Maximum cache entries
            promotion_threshold: Accesses before promotion
            enable_backends: Set of backend types to enable
            config: Additional configuration
        """
        self.config = config or {}
        
        # Initialize cache layer
        self.cache = CacheLayer(
            max_size=cache_size,
            promotion_threshold=promotion_threshold,
            eviction_policy=self.config.get('eviction_policy', 'adaptive')
        )
        
        # Set promotion callback
        self.cache.promotion_callback = self._handle_promotion
        
        # Initialize decision engine (kept for compatibility, but using universal encoder)
        enabled = enable_backends or {'vector', 'graph', 'sql', 'document', 'kv'}
        available_types = set()
        for backend in enabled:
            try:
                available_types.add(StorageType(backend))
            except ValueError:
                logger.warning(f"Unknown backend type: {backend}")
        
        self.decision_engine = StorageDecisionEngine(available_types)
        
        # Initialize universal encoder for store-everywhere approach
        self.universal_encoder = None  # Will be initialized after backends are ready
        
        # Initialize hash index for O(1) lookups
        self.hash_index = HashIndex()
        
        # Initialize storage backends
        self.backends = {}
        self._initialize_backends(enabled)
        
        # Track statistics
        self.stats = {
            'stores': 0,
            'retrievals': 0,
            'promotions': 0,
            'cache_hits': 0,
            'backend_hits': 0,
            'misses': 0,
            'errors': 0
        }
        
        # Promotion queue for batch processing
        self.promotion_queue = asyncio.Queue()
        self.promotion_task = None
        
        logger.info(f"ESR Memory System initialized with {len(self.backends)} backends")
    
    def _initialize_backends(self, enable_backends: Set[str]):
        """Initialize storage backends through Hermes or mocks."""
        
        if HERMES_AVAILABLE:
            # Use Hermes database factory
            factory = DatabaseFactory()
            
            backend_mapping = {
                'vector': DatabaseType.VECTOR,
                'graph': DatabaseType.GRAPH,
                'sql': DatabaseType.RELATION,
                'document': DatabaseType.DOCUMENT,
                'kv': DatabaseType.KEY_VALUE,
                'cache': DatabaseType.CACHE
            }
            
            for backend_name, db_type in backend_mapping.items():
                if backend_name in enable_backends:
                    try:
                        adapter = factory.create_adapter(
                            db_type,
                            namespace=self.config.get('namespace', 'esr'),
                            config=self.config.get(f'{backend_name}_config', {})
                        )
                        self.backends[backend_name] = adapter
                        logger.info(f"Initialized {backend_name} backend via Hermes")
                    except Exception as e:
                        logger.error(f"Failed to initialize {backend_name}: {e}")
                        self.backends[backend_name] = MockBackend(backend_name)
        else:
            # Use mock backends for testing
            for backend_name in enable_backends:
                self.backends[backend_name] = MockBackend(backend_name)
                logger.info(f"Initialized mock {backend_name} backend")
    
    async def start(self):
        """Start the ESR system and connect backends."""
        # Connect all backends
        for name, backend in self.backends.items():
            try:
                await backend.connect()
                logger.info(f"Connected to {name} backend")
            except Exception as e:
                logger.error(f"Failed to connect to {name}: {e}")
        
        # Initialize universal encoder with connected backends
        self.universal_encoder = UniversalEncoder(self.backends, recall_timeout=3.0)
        
        # Start promotion processor
        self.promotion_task = asyncio.create_task(self._process_promotions())
        
        logger.info("ESR Memory System started with universal encoding")
    
    async def stop(self):
        """Stop the ESR system and disconnect backends."""
        # Stop promotion processor
        if self.promotion_task:
            self.promotion_task.cancel()
            try:
                await self.promotion_task
            except asyncio.CancelledError:
                pass
        
        # Save cache
        await self.cache.shutdown()
        
        # Save hash index
        self.hash_index.save_index()
        
        # Disconnect backends
        for name, backend in self.backends.items():
            try:
                await backend.disconnect()
                logger.info(f"Disconnected from {name} backend")
            except Exception as e:
                logger.error(f"Error disconnecting from {name}: {e}")
        
        logger.info("ESR Memory System stopped")
    
    async def store(self,
                   content: Any,
                   content_type: str = 'thought',
                   metadata: Optional[Dict[str, Any]] = None,
                   ci_id: str = None) -> str:
        """
        Store content in memory system.
        
        Args:
            content: Content to store
            content_type: Type of content
            metadata: Optional metadata
            ci_id: ID of CI storing content
            
        Returns:
            Key for stored content
        """
        self.stats['stores'] += 1
        
        try:
            # Always starts in cache
            key = await self.cache.store(content, content_type, metadata, ci_id)
            
            # Add to hash index (initially in cache)
            self.hash_index.add(key, 'cache')
            
            logger.debug(f"Stored {content_type} with key {key} in cache")
            return key
            
        except Exception as e:
            logger.error(f"Error storing content: {e}")
            self.stats['errors'] += 1
            raise
    
    async def retrieve(self,
                      key: str,
                      ci_id: str = None) -> Optional[Any]:
        """
        Retrieve content from memory system with synthesis.
        
        Args:
            key: Key to retrieve
            ci_id: ID of CI retrieving content
            
        Returns:
            Content if found (synthesized if from multiple sources), None otherwise
        """
        self.stats['retrievals'] += 1
        
        try:
            # Check cache first
            content = await self.cache.retrieve(key, ci_id)
            if content is not None:
                self.stats['cache_hits'] += 1
                return content
            
            # Use universal encoder to recall from all backends with synthesis
            if self.universal_encoder:
                synthesis = await self.universal_encoder.recall_from_everywhere(key=key)
                
                if synthesis and synthesis.get('primary'):
                    self.stats['backend_hits'] += 1
                    
                    # Cache the synthesized result for next time
                    await self.cache.store(
                        synthesis['primary'], 
                        'recalled_memory',
                        {'synthesis': True},
                        ci_id
                    )
                    
                    # Return the primary memory (or full synthesis if requested)
                    return synthesis['primary']
                
                self.stats['misses'] += 1
                return None
            
            # Check hash index for backend location
            location = self.hash_index.get(key)
            if not location:
                self.stats['misses'] += 1
                return None
            
            # Retrieve from backend
            backend_type = location['backend']
            if backend_type in self.backends:
                backend = self.backends[backend_type]
                
                # Backend-specific retrieval
                if backend_type == 'sql':
                    # SQL query
                    result = await backend.execute(
                        "SELECT content FROM memories WHERE key = ?", [key]
                    )
                    if result:
                        content = json.loads(result[0]['content'])
                
                elif backend_type == 'document':
                    # Document query
                    result = await backend.find_one({'_id': key})
                    if result:
                        content = result.get('content')
                
                elif backend_type == 'kv':
                    # Simple key-value get
                    content = await backend.get(key)
                
                elif backend_type == 'vector':
                    # Vector retrieval (would need proper implementation)
                    content = await backend.retrieve(key)
                
                elif backend_type == 'graph':
                    # Graph retrieval (would need proper implementation)
                    content = await backend.retrieve(key)
                
                else:
                    # Fallback to generic retrieve if available
                    if hasattr(backend, 'retrieve'):
                        content = await backend.retrieve(key)
                
                if content is not None:
                    self.stats['backend_hits'] += 1
                    
                    # Optionally cache frequently accessed backend data
                    # await self.cache.store(content, 'cached_backend', {}, ci_id)
                    
                    return content
            
            self.stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving content: {e}")
            self.stats['errors'] += 1
            return None
    
    async def _handle_promotion(self, entry: CacheEntry):
        """
        Handle promotion of cache entry to persistent storage.
        
        Args:
            entry: Cache entry to promote
        """
        await self.promotion_queue.put(entry)
    
    async def _process_promotions(self):
        """Background task to process promotion queue."""
        while True:
            try:
                # Get entry from queue
                entry = await self.promotion_queue.get()
                
                # Universal encoding - store everywhere!
                # No routing decisions needed - storage is free
                if self.universal_encoder:
                    metadata = {
                        'content_type': entry.content_type,
                        'first_access': entry.first_access.isoformat(),
                        'access_count': entry.access_count,
                        'ci_sources': list(entry.ci_sources)
                    }
                    metadata.update(entry.metadata)
                    
                    # Store in ALL backends that can handle it
                    results = await self.universal_encoder.store_everywhere(
                        entry.key,
                        entry.content,
                        metadata
                    )
                    
                    # Update hash index with all successful backends
                    for backend_name, success in results.items():
                        if success:
                            self.hash_index.add(entry.key, backend_name)
                    
                    successful = sum(1 for s in results.values() if s)
                    self.stats['promotions'] += 1
                    logger.info(f"Promoted {entry.content_type} to {successful} backends")
                    
                else:
                    # Fallback to old routing approach if universal encoder not available
                    storage_type = self.decision_engine.decide_storage(
                        entry.content,
                        entry.content_type,
                        entry.metadata,
                        entry.access_pattern
                    )
                    
                    routes = self.decision_engine.route_to_backends(
                        storage_type,
                        entry.content,
                        entry.key
                    )
                    
                    for backend_name, prepared_content in routes:
                        if backend_name in self.backends:
                            backend = self.backends[backend_name]
                            
                            try:
                                # Backend-specific storage
                                if backend_name == 'sql':
                                    # Create table if needed
                                    await backend.create_table(
                                        'memories',
                                        {
                                            'key': 'TEXT PRIMARY KEY',
                                            'content': 'TEXT',
                                            'content_type': 'TEXT',
                                            'created_at': 'TIMESTAMP',
                                            'access_count': 'INTEGER'
                                        }
                                    )
                                    
                                    # Insert memory
                                    await backend.execute(
                                        """INSERT OR REPLACE INTO memories 
                                           (key, content, content_type, created_at, access_count)
                                           VALUES (?, ?, ?, ?, ?)""",
                                        [entry.key, json.dumps(entry.content), entry.content_type,
                                         entry.first_access, entry.access_count]
                                    )
                                
                                elif backend_name == 'document':
                                    # Store as document
                                    doc = {
                                        '_id': entry.key,
                                        'content': entry.content,
                                        'content_type': entry.content_type,
                                        'metadata': entry.metadata,
                                        'access_count': entry.access_count,
                                        'ci_sources': list(entry.ci_sources)
                                    }
                                    await backend.insert(doc)
                                
                                elif backend_name == 'kv':
                                    # Simple key-value store
                                    await backend.set(entry.key, entry.content, 0)
                                
                                else:
                                    # Generic store if available
                                    if hasattr(backend, 'store'):
                                        await backend.store(entry.key, prepared_content)
                                
                                # Update hash index
                                self.hash_index.add(entry.key, backend_name)
                                
                                self.stats['promotions'] += 1
                                logger.info(f"Promoted {entry.content_type} {entry.key} to {backend_name}")
                                
                            except Exception as e:
                                logger.error(f"Failed to promote to {backend_name}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in promotion processor: {e}")
    
    async def search(self,
                    query: str,
                    search_type: str = 'semantic',
                    limit: int = 10,
                    ci_id: str = None) -> List[Dict[str, Any]]:
        """
        Search across memory system.
        
        Args:
            query: Search query
            search_type: Type of search ('semantic', 'exact', 'pattern')
            limit: Maximum results
            ci_id: ID of CI searching
            
        Returns:
            List of matching memories
        """
        results = []
        
        # Search cache first
        cache_results = self._search_cache(query, search_type)
        results.extend(cache_results[:limit])
        
        if len(results) >= limit:
            return results
        
        # Search backends
        remaining = limit - len(results)
        
        # Vector search for semantic
        if search_type == 'semantic' and 'vector' in self.backends:
            # Would need proper vector search implementation
            pass
        
        # SQL search for structured
        if 'sql' in self.backends:
            backend = self.backends['sql']
            try:
                sql_results = await backend.execute(
                    "SELECT * FROM memories WHERE content LIKE ? LIMIT ?",
                    [f"%{query}%", remaining]
                )
                for row in sql_results:
                    results.append({
                        'key': row['key'],
                        'content': json.loads(row['content']),
                        'source': 'sql'
                    })
            except Exception as e:
                logger.error(f"SQL search error: {e}")
        
        # Document search
        if 'document' in self.backends and len(results) < limit:
            backend = self.backends['document']
            remaining = limit - len(results)
            try:
                doc_results = await backend.find(
                    {'content': {'$regex': query}},
                    limit=remaining
                )
                for doc in doc_results:
                    results.append({
                        'key': doc['_id'],
                        'content': doc['content'],
                        'source': 'document'
                    })
            except Exception as e:
                logger.error(f"Document search error: {e}")
        
        return results[:limit]
    
    def _search_cache(self, query: str, search_type: str) -> List[Dict[str, Any]]:
        """Search cache entries."""
        results = []
        query_lower = query.lower()
        
        for key, entry in self.cache.cache.items():
            content_str = json.dumps(entry.content) if isinstance(entry.content, dict) else str(entry.content)
            
            if search_type == 'exact':
                if query in content_str:
                    results.append({
                        'key': key,
                        'content': entry.content,
                        'source': 'cache'
                    })
            else:  # pattern or semantic (simplified)
                if query_lower in content_str.lower():
                    results.append({
                        'key': key,
                        'content': entry.content,
                        'source': 'cache'
                    })
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about memory system.
        
        Returns:
            System statistics
        """
        cache_stats = self.cache.analyze_patterns()
        routing_stats = self.decision_engine.get_routing_stats()
        
        return {
            'system_stats': self.stats,
            'cache_analysis': cache_stats,
            'routing_analysis': routing_stats,
            'hash_index_size': len(self.hash_index.index),
            'backends_connected': list(self.backends.keys()),
            'promotion_queue_size': self.promotion_queue.qsize()
        }