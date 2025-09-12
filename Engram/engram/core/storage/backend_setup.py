"""
ESR Backend Setup - Configure and initialize real database backends.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Set
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger("engram.storage.backends")

# Import DatabaseFactory and types
try:
    from hermes.core.database.factory import DatabaseFactory
    from hermes.core.database.database_types import DatabaseType
    HERMES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Hermes not available: {e}")
    HERMES_AVAILABLE = False


class BackendManager:
    """Manages ESR backend connections."""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize backend manager.
        
        Args:
            data_dir: Directory for persistent storage
        """
        self.data_dir = data_dir or os.path.join(
            os.environ.get('TEKTON_ROOT', '/tmp'),
            'tekton', 'engram', 'esr_data'
        )
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.backends = {}
        self.factory = DatabaseFactory() if HERMES_AVAILABLE else None
        
        logger.info(f"Backend manager initialized with data_dir: {self.data_dir}")
    
    def setup_all_backends(self, 
                          enable_backends: Optional[Set[str]] = None) -> Dict[str, Any]:
        """
        Setup all requested backends with real connections.
        
        Args:
            enable_backends: Set of backend types to enable
            
        Returns:
            Dictionary of backend_name -> adapter
        """
        if not HERMES_AVAILABLE:
            logger.error("Hermes not available, cannot setup real backends")
            return {}
        
        enabled = enable_backends or {'sql', 'document', 'kv', 'cache', 'vector'}
        
        # Backend configuration
        backend_configs = {
            'sql': {
                'type': DatabaseType.RELATION,
                'config': {
                    'db_path': os.path.join(self.data_dir, 'esr_sql.db'),
                    'echo': False
                }
            },
            'document': {
                'type': DatabaseType.DOCUMENT,
                'config': {
                    'db_path': os.path.join(self.data_dir, 'esr_documents.json'),
                    'indent': 2
                }
            },
            'kv': {
                'type': DatabaseType.KEY_VALUE,
                'config': {
                    'db_path': os.path.join(self.data_dir, 'esr_kv.db'),
                    'create_if_missing': True
                }
            },
            'cache': {
                'type': DatabaseType.CACHE,
                'config': {
                    'max_size': 10000,
                    'ttl': 3600  # 1 hour TTL
                }
            },
            'vector': {
                'type': DatabaseType.VECTOR,
                'config': {
                    'index_path': os.path.join(self.data_dir, 'esr_vectors'),
                    'dimension': 768,  # Standard BERT dimension
                    'metric': 'cosine'
                }
            }
        }
        
        # Setup each backend
        for backend_name in enabled:
            if backend_name not in backend_configs:
                logger.warning(f"Unknown backend type: {backend_name}")
                continue
            
            config = backend_configs[backend_name]
            try:
                adapter = self.factory.create_adapter(
                    db_type=config['type'],
                    namespace='esr',
                    config=config['config']
                )
                self.backends[backend_name] = adapter
                logger.info(f"✓ Setup {backend_name} backend: {type(adapter).__name__}")
                
            except Exception as e:
                logger.error(f"✗ Failed to setup {backend_name}: {e}")
                # Create fallback adapter
                self.backends[backend_name] = self._create_fallback(backend_name)
        
        return self.backends
    
    def _create_fallback(self, backend_name: str):
        """Create a fallback adapter when real backend fails."""
        logger.info(f"Creating fallback adapter for {backend_name}")
        
        # Import the fallback adapters
        if backend_name == 'sql':
            from hermes.core.database.adapters.sqlite_adapter import SQLiteAdapter
            return SQLiteAdapter(
                namespace='esr',
                config={'db_path': os.path.join(self.data_dir, f'esr_{backend_name}.db')}
            )
        elif backend_name == 'document':
            from hermes.core.database.adapters.tinydb_document_adapter import TinyDBDocumentAdapter
            return TinyDBDocumentAdapter(
                namespace='esr',
                config={'db_path': os.path.join(self.data_dir, f'esr_{backend_name}.json')}
            )
        else:
            # Return a simple in-memory fallback
            return InMemoryAdapter(backend_name)
    
    async def connect_all(self) -> bool:
        """
        Connect all backends.
        
        Returns:
            True if all backends connected successfully
        """
        all_connected = True
        
        for name, backend in self.backends.items():
            try:
                if hasattr(backend, 'connect'):
                    await backend.connect()
                    logger.info(f"✓ Connected to {name} backend")
                else:
                    logger.info(f"✓ {name} backend ready (no connect method)")
                    
            except Exception as e:
                logger.error(f"✗ Failed to connect {name}: {e}")
                all_connected = False
        
        return all_connected
    
    async def disconnect_all(self):
        """Disconnect all backends."""
        for name, backend in self.backends.items():
            try:
                if hasattr(backend, 'disconnect'):
                    await backend.disconnect()
                    logger.info(f"Disconnected from {name} backend")
            except Exception as e:
                logger.error(f"Error disconnecting {name}: {e}")
    
    async def test_backends(self) -> Dict[str, bool]:
        """
        Test all backends with simple operations.
        
        Returns:
            Dictionary of backend_name -> test_passed
        """
        results = {}
        test_key = f"test_key_{datetime.now().timestamp()}"
        test_value = {"test": "data", "timestamp": datetime.now().isoformat()}
        
        for name, backend in self.backends.items():
            try:
                # Test store
                if hasattr(backend, 'store'):
                    await backend.store(test_key, test_value)
                elif hasattr(backend, 'set'):
                    await backend.set(test_key, test_value)
                elif hasattr(backend, 'insert'):
                    await backend.insert({'_id': test_key, 'data': test_value})
                else:
                    logger.warning(f"{name} has no store method")
                    results[name] = False
                    continue
                
                # Test retrieve
                if hasattr(backend, 'retrieve'):
                    retrieved = await backend.retrieve(test_key)
                elif hasattr(backend, 'get'):
                    retrieved = await backend.get(test_key)
                elif hasattr(backend, 'find'):
                    retrieved = await backend.find({'_id': test_key})
                else:
                    logger.warning(f"{name} has no retrieve method")
                    results[name] = False
                    continue
                
                # Check if retrieval worked
                if retrieved:
                    logger.info(f"✓ {name} backend test passed")
                    results[name] = True
                else:
                    logger.warning(f"✗ {name} backend test failed: no data retrieved")
                    results[name] = False
                    
            except Exception as e:
                logger.error(f"✗ {name} backend test error: {e}")
                results[name] = False
        
        return results


class InMemoryAdapter:
    """Simple in-memory adapter for fallback."""
    
    def __init__(self, name: str):
        self.name = name
        self.data = {}
        logger.info(f"Created in-memory adapter for {name}")
    
    async def store(self, key: str, value: Any, **kwargs) -> bool:
        """Store data in memory."""
        self.data[key] = value
        return True
    
    async def retrieve(self, key: str) -> Any:
        """Retrieve data from memory."""
        return self.data.get(key)
    
    async def connect(self) -> bool:
        """No connection needed for in-memory."""
        return True
    
    async def disconnect(self) -> bool:
        """No disconnection needed for in-memory."""
        return True


async def setup_esr_backends(enable_backends: Optional[Set[str]] = None) -> Dict[str, Any]:
    """
    Convenience function to setup ESR backends.
    
    Args:
        enable_backends: Set of backend types to enable
        
    Returns:
        Dictionary of configured backends
    """
    manager = BackendManager()
    backends = manager.setup_all_backends(enable_backends)
    
    if await manager.connect_all():
        logger.info("✅ All backends connected successfully")
    else:
        logger.warning("⚠️ Some backends failed to connect")
    
    # Test backends
    test_results = await manager.test_backends()
    successful = sum(1 for passed in test_results.values() if passed)
    logger.info(f"Backend tests: {successful}/{len(test_results)} passed")
    
    return backends


if __name__ == "__main__":
    # Test backend setup
    import asyncio
    
    async def test():
        print("\n" + "="*60)
        print("ESR BACKEND SETUP TEST")
        print("="*60)
        
        backends = await setup_esr_backends({'sql', 'document', 'kv', 'cache'})
        
        print(f"\nSetup {len(backends)} backends:")
        for name, backend in backends.items():
            print(f"  • {name}: {type(backend).__name__}")
        
        print("\n✅ Backend setup complete!")
    
    asyncio.run(test())