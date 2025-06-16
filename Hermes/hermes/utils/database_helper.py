"""
Database Helper - Simplified interface for using Hermes database services.

This module provides helper functions and a client class for components to easily
access Hermes's centralized database services with minimal boilerplate.
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable, Type

from hermes.core.database_manager import (
    DatabaseManager, 
    DatabaseAdapter,
    DatabaseType,
    DatabaseBackend,
    VectorDatabaseAdapter,
    GraphDatabaseAdapter,
    KeyValueDatabaseAdapter,
    DocumentDatabaseAdapter,
    CacheDatabaseAdapter,
    RelationalDatabaseAdapter
)
from hermes.core.logging import get_logger

# Logger for this module
logger = get_logger("hermes.utils.database_helper")

# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


async def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    
    if _db_manager is None:
        _db_manager = DatabaseManager()
    
    return _db_manager


async def get_vector_db(
    namespace: str = "default",
    backend: Optional[Union[DatabaseBackend, str]] = None,
    config: Optional[Dict[str, Any]] = None
) -> VectorDatabaseAdapter:
    """
    Get a vector database connection.
    
    Args:
        namespace: Namespace for data isolation
        backend: Optional specific backend (auto-detected if not provided)
        config: Optional configuration parameters
        
    Returns:
        Vector database adapter instance
    """
    manager = await get_database_manager()
    return await manager.get_vector_db(namespace, backend, config)


async def get_graph_db(
    namespace: str = "default",
    backend: Optional[Union[DatabaseBackend, str]] = None,
    config: Optional[Dict[str, Any]] = None
) -> GraphDatabaseAdapter:
    """
    Get a graph database connection.
    
    Args:
        namespace: Namespace for data isolation
        backend: Optional specific backend (auto-detected if not provided)
        config: Optional configuration parameters
        
    Returns:
        Graph database adapter instance
    """
    manager = await get_database_manager()
    return await manager.get_graph_db(namespace, backend, config)


async def get_key_value_db(
    namespace: str = "default",
    backend: Optional[Union[DatabaseBackend, str]] = None,
    config: Optional[Dict[str, Any]] = None
) -> KeyValueDatabaseAdapter:
    """
    Get a key-value database connection.
    
    Args:
        namespace: Namespace for data isolation
        backend: Optional specific backend (auto-detected if not provided)
        config: Optional configuration parameters
        
    Returns:
        Key-value database adapter instance
    """
    manager = await get_database_manager()
    return await manager.get_key_value_db(namespace, backend, config)


async def get_document_db(
    namespace: str = "default",
    backend: Optional[Union[DatabaseBackend, str]] = None,
    config: Optional[Dict[str, Any]] = None
) -> DocumentDatabaseAdapter:
    """
    Get a document database connection.
    
    Args:
        namespace: Namespace for data isolation
        backend: Optional specific backend (auto-detected if not provided)
        config: Optional configuration parameters
        
    Returns:
        Document database adapter instance
    """
    manager = await get_database_manager()
    return await manager.get_document_db(namespace, backend, config)


async def get_cache_db(
    namespace: str = "default",
    backend: Optional[Union[DatabaseBackend, str]] = None,
    config: Optional[Dict[str, Any]] = None
) -> CacheDatabaseAdapter:
    """
    Get a cache database connection.
    
    Args:
        namespace: Namespace for data isolation
        backend: Optional specific backend (auto-detected if not provided)
        config: Optional configuration parameters
        
    Returns:
        Cache database adapter instance
    """
    manager = await get_database_manager()
    return await manager.get_cache_db(namespace, backend, config)


async def get_relational_db(
    namespace: str = "default",
    backend: Optional[Union[DatabaseBackend, str]] = None,
    config: Optional[Dict[str, Any]] = None
) -> RelationalDatabaseAdapter:
    """
    Get a relational database connection.
    
    Args:
        namespace: Namespace for data isolation
        backend: Optional specific backend (auto-detected if not provided)
        config: Optional configuration parameters
        
    Returns:
        Relational database adapter instance
    """
    manager = await get_database_manager()
    return await manager.get_relational_db(namespace, backend, config)


class DatabaseClient:
    """
    Client for accessing database services.
    
    This class provides a simplified interface for accessing database services
    with automatic connection management and namespace handling.
    """
    
    def __init__(self, 
                component_id: str,
                data_path: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the database client.
        
        Args:
            component_id: Component identifier (used as namespace prefix)
            data_path: Optional path for database storage
            config: Optional configuration parameters
        """
        self.component_id = component_id
        self.data_path = data_path
        self.config = config or {}
        
        # Namespace prefix
        self.namespace_prefix = f"{component_id}."
        
        # Database manager
        self._db_manager = None
        
        # Active connections
        self._connections: Dict[str, DatabaseAdapter] = {}
    
    async def _get_manager(self) -> DatabaseManager:
        """Get the database manager."""
        if self._db_manager is None:
            self._db_manager = DatabaseManager(
                base_path=self.data_path,
                config=self.config
            )
        
        return self._db_manager
    
    def _get_namespace(self, namespace: str) -> str:
        """Get prefixed namespace."""
        if namespace == "default":
            return self.component_id
        else:
            return f"{self.component_id}.{namespace}"
    
    async def get_vector_db(self,
                          namespace: str = "default",
                          backend: Optional[Union[DatabaseBackend, str]] = None,
                          config: Optional[Dict[str, Any]] = None) -> VectorDatabaseAdapter:
        """
        Get a vector database connection.
        
        Args:
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Vector database adapter instance
        """
        # Get prefixed namespace
        prefixed_namespace = self._get_namespace(namespace)
        
        # Create connection key
        connection_key = f"vector:{prefixed_namespace}"
        if backend:
            if isinstance(backend, str):
                connection_key += f":{backend.upper()}"
            else:
                connection_key += f":{backend.value}"
        
        # Check if connection already exists
        if connection_key in self._connections:
            adapter = self._connections[connection_key]
            if await adapter.is_connected():
                return adapter
        
        # Get database manager
        manager = await self._get_manager()
        
        # Get connection
        adapter = await manager.get_vector_db(
            namespace=prefixed_namespace,
            backend=backend,
            config=config
        )
        
        # Store connection
        self._connections[connection_key] = adapter
        
        return adapter
    
    async def get_graph_db(self,
                         namespace: str = "default",
                         backend: Optional[Union[DatabaseBackend, str]] = None,
                         config: Optional[Dict[str, Any]] = None) -> GraphDatabaseAdapter:
        """
        Get a graph database connection.
        
        Args:
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Graph database adapter instance
        """
        # Get prefixed namespace
        prefixed_namespace = self._get_namespace(namespace)
        
        # Create connection key
        connection_key = f"graph:{prefixed_namespace}"
        if backend:
            if isinstance(backend, str):
                connection_key += f":{backend.upper()}"
            else:
                connection_key += f":{backend.value}"
        
        # Check if connection already exists
        if connection_key in self._connections:
            adapter = self._connections[connection_key]
            if await adapter.is_connected():
                return adapter
        
        # Get database manager
        manager = await self._get_manager()
        
        # Get connection
        adapter = await manager.get_graph_db(
            namespace=prefixed_namespace,
            backend=backend,
            config=config
        )
        
        # Store connection
        self._connections[connection_key] = adapter
        
        return adapter
    
    async def get_key_value_db(self,
                             namespace: str = "default",
                             backend: Optional[Union[DatabaseBackend, str]] = None,
                             config: Optional[Dict[str, Any]] = None) -> KeyValueDatabaseAdapter:
        """
        Get a key-value database connection.
        
        Args:
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Key-value database adapter instance
        """
        # Get prefixed namespace
        prefixed_namespace = self._get_namespace(namespace)
        
        # Create connection key
        connection_key = f"key_value:{prefixed_namespace}"
        if backend:
            if isinstance(backend, str):
                connection_key += f":{backend.upper()}"
            else:
                connection_key += f":{backend.value}"
        
        # Check if connection already exists
        if connection_key in self._connections:
            adapter = self._connections[connection_key]
            if await adapter.is_connected():
                return adapter
        
        # Get database manager
        manager = await self._get_manager()
        
        # Get connection
        adapter = await manager.get_key_value_db(
            namespace=prefixed_namespace,
            backend=backend,
            config=config
        )
        
        # Store connection
        self._connections[connection_key] = adapter
        
        return adapter
    
    async def get_document_db(self,
                            namespace: str = "default",
                            backend: Optional[Union[DatabaseBackend, str]] = None,
                            config: Optional[Dict[str, Any]] = None) -> DocumentDatabaseAdapter:
        """
        Get a document database connection.
        
        Args:
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Document database adapter instance
        """
        # Get prefixed namespace
        prefixed_namespace = self._get_namespace(namespace)
        
        # Create connection key
        connection_key = f"document:{prefixed_namespace}"
        if backend:
            if isinstance(backend, str):
                connection_key += f":{backend.upper()}"
            else:
                connection_key += f":{backend.value}"
        
        # Check if connection already exists
        if connection_key in self._connections:
            adapter = self._connections[connection_key]
            if await adapter.is_connected():
                return adapter
        
        # Get database manager
        manager = await self._get_manager()
        
        # Get connection
        adapter = await manager.get_document_db(
            namespace=prefixed_namespace,
            backend=backend,
            config=config
        )
        
        # Store connection
        self._connections[connection_key] = adapter
        
        return adapter
    
    async def get_cache_db(self,
                         namespace: str = "default",
                         backend: Optional[Union[DatabaseBackend, str]] = None,
                         config: Optional[Dict[str, Any]] = None) -> CacheDatabaseAdapter:
        """
        Get a cache database connection.
        
        Args:
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Cache database adapter instance
        """
        # Get prefixed namespace
        prefixed_namespace = self._get_namespace(namespace)
        
        # Create connection key
        connection_key = f"cache:{prefixed_namespace}"
        if backend:
            if isinstance(backend, str):
                connection_key += f":{backend.upper()}"
            else:
                connection_key += f":{backend.value}"
        
        # Check if connection already exists
        if connection_key in self._connections:
            adapter = self._connections[connection_key]
            if await adapter.is_connected():
                return adapter
        
        # Get database manager
        manager = await self._get_manager()
        
        # Get connection
        adapter = await manager.get_cache_db(
            namespace=prefixed_namespace,
            backend=backend,
            config=config
        )
        
        # Store connection
        self._connections[connection_key] = adapter
        
        return adapter
    
    async def get_relational_db(self,
                              namespace: str = "default",
                              backend: Optional[Union[DatabaseBackend, str]] = None,
                              config: Optional[Dict[str, Any]] = None) -> RelationalDatabaseAdapter:
        """
        Get a relational database connection.
        
        Args:
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Relational database adapter instance
        """
        # Get prefixed namespace
        prefixed_namespace = self._get_namespace(namespace)
        
        # Create connection key
        connection_key = f"relation:{prefixed_namespace}"
        if backend:
            if isinstance(backend, str):
                connection_key += f":{backend.upper()}"
            else:
                connection_key += f":{backend.value}"
        
        # Check if connection already exists
        if connection_key in self._connections:
            adapter = self._connections[connection_key]
            if await adapter.is_connected():
                return adapter
        
        # Get database manager
        manager = await self._get_manager()
        
        # Get connection
        adapter = await manager.get_relational_db(
            namespace=prefixed_namespace,
            backend=backend,
            config=config
        )
        
        # Store connection
        self._connections[connection_key] = adapter
        
        return adapter
    
    async def close_connections(self) -> bool:
        """
        Close all connections.
        
        Returns:
            True if all connections closed successfully
        """
        success = True
        
        for key, adapter in list(self._connections.items()):
            try:
                await adapter.disconnect()
                del self._connections[key]
            except Exception as e:
                logger.error(f"Error closing connection {key}: {e}")
                success = False
        
        return success
    
    async def __aenter__(self) -> 'DatabaseClient':
        """Enter context manager."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        await self.close_connections()