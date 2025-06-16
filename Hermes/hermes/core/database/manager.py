"""
Database Manager - Central interface for all database operations.

This module provides a unified interface for accessing different types
of databases, with support for namespace isolation and connection pooling.
"""

import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from hermes.core.logging import get_logger
from hermes.core.database.database_types import DatabaseType, DatabaseBackend
from hermes.core.database.factory import DatabaseFactory
from hermes.core.database.adapters import (
    DatabaseAdapter, 
    VectorDatabaseAdapter, 
    GraphDatabaseAdapter,
    KeyValueDatabaseAdapter,
    DocumentDatabaseAdapter,
    CacheDatabaseAdapter,
    RelationalDatabaseAdapter
)

# Logger for this module
logger = get_logger("hermes.core.database.manager")


class DatabaseManager:
    """
    Centralized manager for all database operations.
    
    This class provides a unified interface for accessing different types
    of databases, with support for namespace isolation and connection pooling.
    """
    
    def __init__(self, 
                base_path: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the database manager.
        
        Args:
            base_path: Base path for database storage (default: ~/.tekton/data)
            config: Optional configuration parameters
        """
        # Set up base path
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = Path(os.path.expanduser("~/.tekton/data"))
        
        # Ensure base path exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.config = config or {}
        
        # Dictionary to store active database connections
        self.connections: Dict[str, Dict[str, DatabaseAdapter]] = {
            db_type.value: {} for db_type in DatabaseType
        }
        
        # Connection lock to prevent race conditions
        self.lock = threading.RLock()
        
        logger.normal("Database manager initialized", context={"base_path": str(self.base_path)})
    
    async def get_connection(self,
                           db_type: Union[DatabaseType, str],
                           namespace: str = "default",
                           backend: Optional[Union[DatabaseBackend, str]] = None,
                           config: Optional[Dict[str, Any]] = None) -> DatabaseAdapter:
        """
        Get a database connection for a specific type and namespace.
        
        Args:
            db_type: Type of database
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Database adapter instance
        """
        # Convert string to enum if needed
        if isinstance(db_type, str):
            db_type = DatabaseType.from_string(db_type)
        
        # Create unique connection ID
        connection_id = f"{namespace}"
        if backend:
            if isinstance(backend, str):
                backend_str = backend.upper()
            else:
                backend_str = backend.value
            connection_id += f":{backend_str}"
        
        # Check if connection already exists
        with self.lock:
            if connection_id in self.connections[db_type.value]:
                adapter = self.connections[db_type.value][connection_id]
                
                # Check if connected
                if await adapter.is_connected():
                    return adapter
                
                # Try to reconnect
                try:
                    await adapter.connect()
                    return adapter
                except Exception as e:
                    logger.error(f"Failed to reconnect to {db_type.value} database for namespace {namespace}: {e}")
                    # Remove the failed connection
                    del self.connections[db_type.value][connection_id]
            
            # Create new connection
            merged_config = self.config.copy()
            if config:
                merged_config.update(config)
            
            # Add base path to config
            merged_config["base_path"] = str(self.base_path / db_type.value / namespace)
            
            try:
                # Create adapter
                adapter = DatabaseFactory.create_adapter(
                    db_type=db_type,
                    backend=backend,
                    namespace=namespace,
                    config=merged_config
                )
                
                # Connect to database
                await adapter.connect()
                
                # Store connection
                self.connections[db_type.value][connection_id] = adapter
                
                logger.info(f"Connected to {db_type.value} database for namespace {namespace} using {adapter.backend.value}")
                return adapter
                
            except Exception as e:
                logger.error(f"Failed to connect to {db_type.value} database for namespace {namespace}: {e}")
                raise
    
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
        adapter = await self.get_connection(
            db_type=DatabaseType.VECTOR,
            namespace=namespace,
            backend=backend,
            config=config
        )
        
        if not isinstance(adapter, VectorDatabaseAdapter):
            raise TypeError(f"Expected VectorDatabaseAdapter, got {type(adapter)}")
        
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
        adapter = await self.get_connection(
            db_type=DatabaseType.GRAPH,
            namespace=namespace,
            backend=backend,
            config=config
        )
        
        if not isinstance(adapter, GraphDatabaseAdapter):
            raise TypeError(f"Expected GraphDatabaseAdapter, got {type(adapter)}")
        
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
        adapter = await self.get_connection(
            db_type=DatabaseType.KEY_VALUE,
            namespace=namespace,
            backend=backend,
            config=config
        )
        
        if not isinstance(adapter, KeyValueDatabaseAdapter):
            raise TypeError(f"Expected KeyValueDatabaseAdapter, got {type(adapter)}")
        
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
        adapter = await self.get_connection(
            db_type=DatabaseType.DOCUMENT,
            namespace=namespace,
            backend=backend,
            config=config
        )
        
        if not isinstance(adapter, DocumentDatabaseAdapter):
            raise TypeError(f"Expected DocumentDatabaseAdapter, got {type(adapter)}")
        
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
        adapter = await self.get_connection(
            db_type=DatabaseType.CACHE,
            namespace=namespace,
            backend=backend,
            config=config
        )
        
        if not isinstance(adapter, CacheDatabaseAdapter):
            raise TypeError(f"Expected CacheDatabaseAdapter, got {type(adapter)}")
        
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
        adapter = await self.get_connection(
            db_type=DatabaseType.RELATION,
            namespace=namespace,
            backend=backend,
            config=config
        )
        
        if not isinstance(adapter, RelationalDatabaseAdapter):
            raise TypeError(f"Expected RelationalDatabaseAdapter, got {type(adapter)}")
        
        return adapter
    
    async def close_connection(self,
                             db_type: Union[DatabaseType, str],
                             namespace: str = "default",
                             backend: Optional[Union[DatabaseBackend, str]] = None) -> bool:
        """
        Close a database connection.
        
        Args:
            db_type: Type of database
            namespace: Namespace for data isolation
            backend: Optional specific backend
            
        Returns:
            True if connection closed successfully
        """
        # Convert string to enum if needed
        if isinstance(db_type, str):
            db_type = DatabaseType.from_string(db_type)
        
        # Create unique connection ID
        connection_id = f"{namespace}"
        if backend:
            if isinstance(backend, str):
                backend_str = backend.upper()
            else:
                backend_str = backend.value
            connection_id += f":{backend_str}"
        
        # Check if connection exists
        with self.lock:
            if connection_id in self.connections[db_type.value]:
                adapter = self.connections[db_type.value][connection_id]
                
                try:
                    # Disconnect from database
                    await adapter.disconnect()
                    
                    # Remove connection
                    del self.connections[db_type.value][connection_id]
                    
                    logger.info(f"Closed {db_type.value} database connection for namespace {namespace}")
                    return True
                except Exception as e:
                    logger.error(f"Error closing {db_type.value} database connection for namespace {namespace}: {e}")
                    return False
            
            # Connection doesn't exist
            return True
    
    async def close_all_connections(self) -> bool:
        """
        Close all database connections.
        
        Returns:
            True if all connections closed successfully
        """
        success = True
        
        with self.lock:
            for db_type, connections in self.connections.items():
                for connection_id, adapter in list(connections.items()):
                    try:
                        # Disconnect from database
                        await adapter.disconnect()
                        
                        # Remove connection
                        del connections[connection_id]
                        
                        logger.info(f"Closed {db_type} database connection {connection_id}")
                    except Exception as e:
                        logger.error(f"Error closing {db_type} database connection {connection_id}: {e}")
                        success = False
        
        return success
    
    def get_namespaces(self, db_type: Union[DatabaseType, str]) -> List[str]:
        """
        Get list of available namespaces for a database type.
        
        Args:
            db_type: Type of database
            
        Returns:
            List of namespace names
        """
        # Convert string to enum if needed
        if isinstance(db_type, str):
            db_type = DatabaseType.from_string(db_type)
        
        # Get path for this database type
        db_path = self.base_path / db_type.value
        
        if not db_path.exists():
            return []
        
        # List directories (each is a namespace)
        try:
            return [d.name for d in db_path.iterdir() if d.is_dir()]
        except Exception as e:
            logger.error(f"Error getting namespaces for {db_type.value}: {e}")
            return []