"""
Real Backend Setup for ESR - Direct adapter initialization.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Setup paths
tekton_root = os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Coder-A')
sys.path.insert(0, tekton_root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger("engram.storage.real_backends")


def get_real_backends(data_dir: str = None) -> Dict[str, Any]:
    """
    Get real backend adapters directly.
    
    Args:
        data_dir: Directory for persistent storage
        
    Returns:
        Dictionary of backend_name -> adapter instance
    """
    data_dir = data_dir or os.path.join(
        os.environ.get('TEKTON_ROOT', '/tmp'),
        'tekton', 'engram', 'esr_data'
    )
    os.makedirs(data_dir, exist_ok=True)
    
    backends = {}
    
    # 1. SQLite adapter for SQL backend
    try:
        from Hermes.hermes.core.database.adapters.sqlite_adapter import SQLiteAdapter
        backends['sql'] = SQLiteAdapter(
            namespace='esr',
            config={'db_path': os.path.join(data_dir, 'esr_sql.db')}
        )
        logger.info("✓ SQLite backend initialized")
    except Exception as e:
        logger.error(f"Failed to setup SQLite: {e}")
    
    # 2. TinyDB adapter for document backend
    try:
        from Hermes.hermes.core.database.adapters.tinydb_document_adapter import TinyDBDocumentAdapter
        backends['document'] = TinyDBDocumentAdapter(
            namespace='esr',
            config={'db_path': os.path.join(data_dir, 'esr_documents.json')}
        )
        logger.info("✓ TinyDB document backend initialized")
    except Exception as e:
        logger.error(f"Failed to setup TinyDB: {e}")
    
    # 3. Simple in-memory cache backend
    try:
        backends['cache'] = InMemoryCache('cache')
        logger.info("✓ In-memory cache backend initialized")
    except Exception as e:
        logger.error(f"Failed to setup cache: {e}")
    
    # 4. Simple key-value backend (using dict for now, could use LevelDB)
    try:
        backends['kv'] = SimpleKVStore(
            db_path=os.path.join(data_dir, 'esr_kv.json')
        )
        logger.info("✓ Key-value backend initialized")
    except Exception as e:
        logger.error(f"Failed to setup KV store: {e}")
    
    # 5. Graph backend from Athena (if available)
    try:
        from Athena.athena.core.graph.memory_adapter import MemoryGraphAdapter
        backends['graph'] = MemoryGraphAdapter()
        logger.info("✓ Graph backend initialized from Athena")
    except Exception as e:
        # Try alternate import
        try:
            from Athena.athena.core.graph.neo4j_adapter import Neo4jAdapter
            backends['graph'] = Neo4jAdapter()
            logger.info("✓ Neo4j graph backend initialized from Athena")
        except:
            logger.warning(f"Graph backend not available: {e}")
            # Use simple in-memory graph
            backends['graph'] = SimpleGraphStore()
            logger.info("✓ Simple graph backend initialized")
    
    # 6. Vector backend (simple for now, could use FAISS)
    try:
        backends['vector'] = SimpleVectorStore(
            index_path=os.path.join(data_dir, 'esr_vectors')
        )
        logger.info("✓ Vector backend initialized")
    except Exception as e:
        logger.error(f"Failed to setup vector store: {e}")
    
    logger.info(f"Initialized {len(backends)} backends")
    return backends


class InMemoryCache:
    """Simple in-memory cache backend."""
    
    def __init__(self, name: str):
        self.name = name
        self.cache = {}
        self.max_size = 10000
    
    async def store(self, key: str, value: Any, **kwargs) -> bool:
        """Store in cache."""
        if len(self.cache) >= self.max_size:
            # Simple LRU - remove first item
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        self.cache[key] = value
        return True
    
    async def retrieve(self, key: str) -> Any:
        """Retrieve from cache."""
        return self.cache.get(key)
    
    async def connect(self) -> bool:
        return True
    
    async def disconnect(self) -> bool:
        return True


class SimpleKVStore:
    """Simple key-value store with JSON persistence."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.data = {}
        self._load()
    
    def _load(self):
        """Load data from disk."""
        if os.path.exists(self.db_path):
            try:
                import json
                with open(self.db_path, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load KV data: {e}")
    
    def _save(self):
        """Save data to disk."""
        try:
            import json
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save KV data: {e}")
    
    async def store(self, key: str, value: Any, **kwargs) -> bool:
        """Store key-value pair."""
        self.data[key] = value
        self._save()
        return True
    
    async def retrieve(self, key: str) -> Any:
        """Retrieve value by key."""
        return self.data.get(key)
    
    async def connect(self) -> bool:
        return True
    
    async def disconnect(self) -> bool:
        self._save()
        return True


class SimpleGraphStore:
    """Simple graph store for relationships."""
    
    def __init__(self):
        self.nodes = {}
        self.edges = []
    
    async def store(self, key: str, value: Any, **kwargs) -> bool:
        """Store as node or edge."""
        if isinstance(value, dict):
            if 'source' in value and 'target' in value:
                # It's an edge
                self.edges.append({
                    'id': key,
                    'source': value['source'],
                    'target': value['target'],
                    'data': value
                })
            else:
                # It's a node
                self.nodes[key] = value
        else:
            self.nodes[key] = value
        return True
    
    async def retrieve(self, key: str) -> Any:
        """Retrieve node or edge."""
        if key in self.nodes:
            return self.nodes[key]
        for edge in self.edges:
            if edge['id'] == key:
                return edge['data']
        return None
    
    async def connect(self) -> bool:
        return True
    
    async def disconnect(self) -> bool:
        return True


class SimpleVectorStore:
    """Simple vector store for embeddings."""
    
    def __init__(self, index_path: str):
        self.index_path = index_path
        self.vectors = {}
        self.metadata = {}
        os.makedirs(index_path, exist_ok=True)
    
    async def store(self, key: str, value: Any, **kwargs) -> bool:
        """Store vector with metadata."""
        if isinstance(value, dict) and 'embedding' in value:
            self.vectors[key] = value['embedding']
            self.metadata[key] = value.get('metadata', {})
        else:
            # Store as metadata only
            self.metadata[key] = value
        return True
    
    async def retrieve(self, key: str) -> Any:
        """Retrieve vector and metadata."""
        if key in self.vectors:
            return {
                'embedding': self.vectors[key],
                'metadata': self.metadata.get(key, {})
            }
        elif key in self.metadata:
            return self.metadata[key]
        return None
    
    async def search(self, query_vector: list, k: int = 5) -> list:
        """Simple similarity search (would use FAISS in production)."""
        # For now, just return random k items
        import random
        keys = list(self.vectors.keys())
        results = []
        for key in random.sample(keys, min(k, len(keys))):
            results.append({
                'key': key,
                'score': random.random(),
                'metadata': self.metadata.get(key, {})
            })
        return results
    
    async def connect(self) -> bool:
        return True
    
    async def disconnect(self) -> bool:
        return True


async def test_real_backends():
    """Test the real backend setup."""
    print("\n" + "="*60)
    print("REAL BACKEND TEST")
    print("="*60)
    
    backends = get_real_backends()
    
    print(f"\nInitialized {len(backends)} backends:")
    for name, backend in backends.items():
        print(f"  • {name}: {type(backend).__name__}")
    
    # Test each backend
    print("\nTesting backends...")
    test_key = f"test_{datetime.now().timestamp()}"
    test_value = {"data": "test", "timestamp": datetime.now().isoformat()}
    
    for name, backend in backends.items():
        try:
            # Connect
            if hasattr(backend, 'connect'):
                await backend.connect()
            
            # Store
            await backend.store(test_key, test_value)
            
            # Retrieve
            retrieved = await backend.retrieve(test_key)
            
            if retrieved:
                print(f"  ✓ {name}: Store and retrieve successful")
            else:
                print(f"  ✗ {name}: Retrieve failed")
            
            # Disconnect
            if hasattr(backend, 'disconnect'):
                await backend.disconnect()
                
        except Exception as e:
            print(f"  ✗ {name}: Test failed - {e}")
    
    print("\n✅ Backend test complete!")
    return backends


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_real_backends())