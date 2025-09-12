"""
Direct Backend Adapters for ESR - No complex imports needed.
"""

import os
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("engram.storage.direct_backends")


class DirectSQLiteBackend:
    """Direct SQLite backend without Hermes dependencies."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup the database and create table if needed."""
        os.makedirs(os.path.dirname(self.db_path) or '.', exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS esr_storage (
                key TEXT PRIMARY KEY,
                value TEXT,
                metadata TEXT,
                timestamp REAL
            )
        ''')
        self.conn.commit()
        logger.info(f"SQLite database ready at {self.db_path}")
    
    async def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """Store data in SQLite."""
        try:
            value_json = json.dumps(value) if not isinstance(value, str) else value
            metadata_json = json.dumps(metadata) if metadata else '{}'
            
            self.conn.execute('''
                INSERT OR REPLACE INTO esr_storage (key, value, metadata, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (key, value_json, metadata_json, datetime.now().timestamp()))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"SQLite store error: {e}")
            return False
    
    async def retrieve(self, key: str) -> Any:
        """Retrieve data from SQLite."""
        try:
            cursor = self.conn.execute(
                'SELECT value FROM esr_storage WHERE key = ?', (key,)
            )
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except:
                    return row[0]
            return None
        except Exception as e:
            logger.error(f"SQLite retrieve error: {e}")
            return None
    
    async def connect(self) -> bool:
        """Connect/reconnect to database."""
        if not self.conn:
            self._setup_database()
        return True
    
    async def disconnect(self) -> bool:
        """Close the connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
        return True
    
    def __del__(self):
        """Ensure connection is closed."""
        if self.conn:
            self.conn.close()


class DirectTinyDBBackend:
    """Direct TinyDB-like JSON document backend."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.data = {}
        self._load_database()
    
    def _load_database(self):
        """Load the JSON database."""
        os.makedirs(os.path.dirname(self.db_path) or '.', exist_ok=True)
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    self.data = json.load(f)
                logger.info(f"Loaded {len(self.data)} documents from {self.db_path}")
            except Exception as e:
                logger.warning(f"Could not load database: {e}")
                self.data = {}
        else:
            self.data = {}
            self._save_database()
    
    def _save_database(self):
        """Save the JSON database."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save database: {e}")
    
    async def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """Store document."""
        try:
            self.data[key] = {
                'value': value,
                'metadata': metadata or {},
                'timestamp': datetime.now().isoformat()
            }
            self._save_database()
            return True
        except Exception as e:
            logger.error(f"TinyDB store error: {e}")
            return False
    
    async def retrieve(self, key: str) -> Any:
        """Retrieve document."""
        doc = self.data.get(key)
        if doc:
            return doc.get('value')
        return None
    
    async def connect(self) -> bool:
        """Already connected."""
        return True
    
    async def disconnect(self) -> bool:
        """Save and close."""
        self._save_database()
        return True


class DirectRedisLikeBackend:
    """Direct Redis-like in-memory cache with optional persistence."""
    
    def __init__(self, cache_file: Optional[str] = None):
        self.cache = {}
        self.cache_file = cache_file
        self.ttl = {}  # Time-to-live tracking
        if cache_file:
            self._load_cache()
    
    def _load_cache(self):
        """Load cache from file if exists."""
        if self.cache_file and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.cache = data.get('cache', {})
                    self.ttl = data.get('ttl', {})
                logger.info(f"Loaded {len(self.cache)} items from cache")
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
    
    def _save_cache(self):
        """Save cache to file."""
        if self.cache_file:
            try:
                os.makedirs(os.path.dirname(self.cache_file) or '.', exist_ok=True)
                with open(self.cache_file, 'w') as f:
                    json.dump({
                        'cache': self.cache,
                        'ttl': self.ttl
                    }, f, indent=2, default=str)
            except Exception as e:
                logger.error(f"Could not save cache: {e}")
    
    async def store(self, key: str, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        """Store in cache with optional TTL."""
        try:
            self.cache[key] = value
            if ttl:
                self.ttl[key] = datetime.now().timestamp() + ttl
            if self.cache_file:
                self._save_cache()
            return True
        except Exception as e:
            logger.error(f"Cache store error: {e}")
            return False
    
    async def retrieve(self, key: str) -> Any:
        """Retrieve from cache."""
        # Check TTL
        if key in self.ttl:
            if datetime.now().timestamp() > self.ttl[key]:
                # Expired
                del self.cache[key]
                del self.ttl[key]
                return None
        return self.cache.get(key)
    
    async def connect(self) -> bool:
        return True
    
    async def disconnect(self) -> bool:
        if self.cache_file:
            self._save_cache()
        return True


def get_direct_backends(data_dir: str = None) -> Dict[str, Any]:
    """
    Get all direct backend adapters.
    
    Returns:
        Dictionary of backend_name -> adapter
    """
    data_dir = data_dir or os.path.join(
        os.environ.get('TEKTON_ROOT', '/tmp'),
        'tekton', 'engram', 'esr_data'
    )
    os.makedirs(data_dir, exist_ok=True)
    
    backends = {}
    
    # 1. SQLite backend
    try:
        backends['sql'] = DirectSQLiteBackend(
            db_path=os.path.join(data_dir, 'esr_sql.db')
        )
        logger.info("✓ SQLite backend initialized")
    except Exception as e:
        logger.error(f"Failed to setup SQLite: {e}")
    
    # 2. Document backend (TinyDB-like)
    try:
        backends['document'] = DirectTinyDBBackend(
            db_path=os.path.join(data_dir, 'esr_documents.json')
        )
        logger.info("✓ Document backend initialized")
    except Exception as e:
        logger.error(f"Failed to setup document backend: {e}")
    
    # 3. Cache backend (Redis-like)
    try:
        backends['cache'] = DirectRedisLikeBackend(
            cache_file=os.path.join(data_dir, 'esr_cache.json')
        )
        logger.info("✓ Cache backend initialized")
    except Exception as e:
        logger.error(f"Failed to setup cache: {e}")
    
    # 4. Key-value backend
    try:
        backends['kv'] = DirectTinyDBBackend(
            db_path=os.path.join(data_dir, 'esr_kv.json')
        )
        logger.info("✓ Key-value backend initialized")
    except Exception as e:
        logger.error(f"Failed to setup KV: {e}")
    
    # 5. Graph backend (simple)
    try:
        from real_backends import SimpleGraphStore
        backends['graph'] = SimpleGraphStore()
        logger.info("✓ Graph backend initialized")
    except Exception as e:
        logger.error(f"Failed to setup graph: {e}")
    
    # 6. Vector backend (simple)
    try:
        from real_backends import SimpleVectorStore
        backends['vector'] = SimpleVectorStore(
            index_path=os.path.join(data_dir, 'esr_vectors')
        )
        logger.info("✓ Vector backend initialized")
    except Exception as e:
        logger.error(f"Failed to setup vector: {e}")
    
    logger.info(f"Initialized {len(backends)} backends")
    return backends


async def test_direct_backends():
    """Test all direct backends."""
    print("\n" + "="*60)
    print("DIRECT BACKEND TEST")
    print("="*60)
    
    backends = get_direct_backends()
    
    print(f"\nInitialized {len(backends)} backends:")
    for name, backend in backends.items():
        print(f"  • {name}: {type(backend).__name__}")
    
    # Test each backend
    print("\nTesting backends...")
    test_data = {
        "message": "ESR test data",
        "timestamp": datetime.now().isoformat(),
        "nested": {"key": "value"}
    }
    
    for name, backend in backends.items():
        try:
            # Connect
            await backend.connect()
            
            # Store
            test_key = f"test_{name}_{datetime.now().timestamp()}"
            success = await backend.store(test_key, test_data)
            
            if success:
                # Retrieve
                retrieved = await backend.retrieve(test_key)
                
                if retrieved:
                    print(f"  ✓ {name}: Store and retrieve successful")
                else:
                    print(f"  ✗ {name}: Retrieve failed")
            else:
                print(f"  ✗ {name}: Store failed")
            
            # Disconnect
            await backend.disconnect()
            
        except Exception as e:
            print(f"  ✗ {name}: Test error - {e}")
    
    # Test persistence
    print("\nTesting persistence...")
    
    # Store something in SQL
    sql_backend = backends.get('sql')
    if sql_backend:
        persist_key = "persistent_test"
        persist_value = {"data": "This should persist", "time": datetime.now().isoformat()}
        
        await sql_backend.connect()
        await sql_backend.store(persist_key, persist_value)
        await sql_backend.disconnect()
        
        # Create new backend and check if data persists
        new_sql = DirectSQLiteBackend(
            db_path=os.path.join(
                os.environ.get('TEKTON_ROOT', '/tmp'),
                'tekton', 'engram', 'esr_data', 'esr_sql.db'
            )
        )
        await new_sql.connect()
        retrieved = await new_sql.retrieve(persist_key)
        await new_sql.disconnect()
        
        if retrieved:
            print(f"  ✓ SQLite persistence verified: {retrieved.get('data', 'N/A')}")
        else:
            print(f"  ✗ SQLite persistence failed")
    
    print("\n✅ Direct backend test complete!")
    return backends


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_direct_backends())