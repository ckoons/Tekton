"""
Database Factory - Creates and configures appropriate database adapters.

This module provides a factory for creating database adapters based on
the database type and backend, with hardware-specific optimization.
"""

import logging
import platform
from typing import Dict, List, Any, Optional, Union

from hermes.core.database.database_types import DatabaseType, DatabaseBackend
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
logger = logging.getLogger("hermes.core.database.factory")


class DatabaseFactory:
    """
    Factory for creating database adapters.
    
    This class provides methods for creating database adapters based on
    the database type and backend, with hardware-specific optimization.
    """
    
    @staticmethod
    def create_adapter(db_type: Union[DatabaseType, str],
                     backend: Optional[Union[DatabaseBackend, str]] = None,
                     namespace: str = "default",
                     config: Optional[Dict[str, Any]] = None) -> DatabaseAdapter:
        """
        Create a database adapter.
        
        Args:
            db_type: Type of database
            backend: Optional specific backend (auto-detected if not provided)
            namespace: Namespace for data isolation
            config: Optional configuration parameters
            
        Returns:
            Database adapter instance
        """
        # Convert string to enum if needed
        if isinstance(db_type, str):
            db_type = DatabaseType.from_string(db_type)
        
        # Auto-detect optimal backend if not specified
        if backend is None:
            backend = DatabaseFactory._detect_optimal_backend(db_type)
        elif isinstance(backend, str):
            backend = DatabaseBackend.from_string(backend)
        
        # Create appropriate adapter based on type and backend
        if db_type == DatabaseType.VECTOR:
            return DatabaseFactory._create_vector_adapter(backend, namespace, config)
        elif db_type == DatabaseType.GRAPH:
            return DatabaseFactory._create_graph_adapter(backend, namespace, config)
        elif db_type == DatabaseType.KEY_VALUE:
            return DatabaseFactory._create_key_value_adapter(backend, namespace, config)
        elif db_type == DatabaseType.DOCUMENT:
            return DatabaseFactory._create_document_adapter(backend, namespace, config)
        elif db_type == DatabaseType.CACHE:
            return DatabaseFactory._create_cache_adapter(backend, namespace, config)
        elif db_type == DatabaseType.RELATION:
            return DatabaseFactory._create_relational_adapter(backend, namespace, config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @staticmethod
    def _detect_optimal_backend(db_type: DatabaseType) -> DatabaseBackend:
        """
        Detect the optimal backend for a database type based on hardware.
        
        Args:
            db_type: Database type
            
        Returns:
            Optimal backend for the current hardware
        """
        if db_type == DatabaseType.VECTOR:
            # Check for Apple Silicon
            if platform.processor() == 'arm':
                logger.info("Detected Apple Silicon, using Qdrant for vector database")
                return DatabaseBackend.QDRANT
            
            # Check for NVIDIA GPU
            try:
                import torch
                if torch.cuda.is_available():
                    logger.info("Detected NVIDIA GPU, using FAISS for vector database")
                    return DatabaseBackend.FAISS
            except ImportError:
                pass
            
            # Default to FAISS
            logger.info("Using FAISS as default vector database")
            return DatabaseBackend.FAISS
        
        elif db_type == DatabaseType.GRAPH:
            # Check if Neo4j is available
            try:
                import neo4j
                logger.info("Neo4j is available, using Neo4j for graph database")
                return DatabaseBackend.NEO4J
            except ImportError:
                logger.info("Neo4j not available, using NetworkX for graph database")
                return DatabaseBackend.NETWORKX
        
        elif db_type == DatabaseType.KEY_VALUE:
            # Check if Redis is available
            try:
                import redis
                logger.info("Redis is available, using Redis for key-value database")
                return DatabaseBackend.REDIS
            except ImportError:
                logger.info("Redis not available, using LevelDB for key-value database")
                return DatabaseBackend.LEVELDB
        
        elif db_type == DatabaseType.DOCUMENT:
            # Check if MongoDB is available
            try:
                import pymongo
                logger.info("MongoDB is available, using MongoDB for document database")
                return DatabaseBackend.MONGODB
            except ImportError:
                logger.info("MongoDB not available, using JSONDB for document database")
                return DatabaseBackend.JSONDB
        
        elif db_type == DatabaseType.CACHE:
            # Simple in-memory cache is always available
            return DatabaseBackend.MEMORY
        
        elif db_type == DatabaseType.RELATION:
            # SQLite is always available
            return DatabaseBackend.SQLITE
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @staticmethod
    def _create_vector_adapter(backend: DatabaseBackend,
                             namespace: str,
                             config: Optional[Dict[str, Any]]) -> VectorDatabaseAdapter:
        """Create a vector database adapter."""
        # Import implementations dynamically
        if backend == DatabaseBackend.FAISS:
            from hermes.adapters.vector.faiss_adapter import FAISSVectorAdapter
            return FAISSVectorAdapter(namespace, config)
        elif backend == DatabaseBackend.QDRANT:
            from hermes.adapters.vector.qdrant_adapter import QdrantVectorAdapter
            return QdrantVectorAdapter(namespace, config)
        elif backend == DatabaseBackend.CHROMADB:
            from hermes.adapters.vector.chromadb_adapter import ChromaDBVectorAdapter
            return ChromaDBVectorAdapter(namespace, config)
        elif backend == DatabaseBackend.LANCEDB:
            from hermes.adapters.vector.lancedb_adapter import LanceDBVectorAdapter
            return LanceDBVectorAdapter(namespace, config)
        else:
            # Default to fallback adapter
            from hermes.adapters.vector.fallback_adapter import FallbackVectorAdapter
            logger.warning(f"Using fallback vector adapter for backend {backend}")
            return FallbackVectorAdapter(namespace, config)
    
    @staticmethod
    def _create_graph_adapter(backend: DatabaseBackend,
                           namespace: str,
                           config: Optional[Dict[str, Any]]) -> GraphDatabaseAdapter:
        """Create a graph database adapter."""
        # Import implementations dynamically
        if backend == DatabaseBackend.NEO4J:
            from hermes.adapters.graph.neo4j_adapter import Neo4jGraphAdapter
            return Neo4jGraphAdapter(namespace, config)
        elif backend == DatabaseBackend.NETWORKX:
            from hermes.adapters.graph.networkx_adapter import NetworkXGraphAdapter
            return NetworkXGraphAdapter(namespace, config)
        else:
            # Default to fallback adapter
            from hermes.adapters.graph.fallback_adapter import FallbackGraphAdapter
            logger.warning(f"Using fallback graph adapter for backend {backend}")
            return FallbackGraphAdapter(namespace, config)
    
    @staticmethod
    def _create_key_value_adapter(backend: DatabaseBackend,
                               namespace: str,
                               config: Optional[Dict[str, Any]]) -> KeyValueDatabaseAdapter:
        """Create a key-value database adapter."""
        # Import implementations dynamically
        if backend == DatabaseBackend.REDIS:
            from hermes.adapters.key_value.redis_adapter import RedisKeyValueAdapter
            return RedisKeyValueAdapter(namespace, config)
        elif backend == DatabaseBackend.LEVELDB:
            from hermes.adapters.key_value.leveldb_adapter import LevelDBKeyValueAdapter
            return LevelDBKeyValueAdapter(namespace, config)
        elif backend == DatabaseBackend.ROCKSDB:
            from hermes.adapters.key_value.rocksdb_adapter import RocksDBKeyValueAdapter
            return RocksDBKeyValueAdapter(namespace, config)
        else:
            # Default to fallback adapter
            from hermes.adapters.key_value.fallback_adapter import FallbackKeyValueAdapter
            logger.warning(f"Using fallback key-value adapter for backend {backend}")
            return FallbackKeyValueAdapter(namespace, config)
    
    @staticmethod
    def _create_document_adapter(backend: DatabaseBackend,
                              namespace: str,
                              config: Optional[Dict[str, Any]]) -> DocumentDatabaseAdapter:
        """Create a document database adapter."""
        # Import implementations dynamically
        if backend == DatabaseBackend.MONGODB:
            from hermes.adapters.document.mongodb_adapter import MongoDBDocumentAdapter
            return MongoDBDocumentAdapter(namespace, config)
        elif backend == DatabaseBackend.JSONDB:
            from hermes.adapters.document.jsondb_adapter import JSONDBDocumentAdapter
            return JSONDBDocumentAdapter(namespace, config)
        else:
            # Default to fallback adapter
            from hermes.adapters.document.fallback_adapter import FallbackDocumentAdapter
            logger.warning(f"Using fallback document adapter for backend {backend}")
            return FallbackDocumentAdapter(namespace, config)
    
    @staticmethod
    def _create_cache_adapter(backend: DatabaseBackend,
                           namespace: str,
                           config: Optional[Dict[str, Any]]) -> CacheDatabaseAdapter:
        """Create a cache database adapter."""
        # Import implementations dynamically
        if backend == DatabaseBackend.MEMORY:
            from hermes.adapters.cache.memory_adapter import MemoryCacheAdapter
            return MemoryCacheAdapter(namespace, config)
        elif backend == DatabaseBackend.MEMCACHED:
            from hermes.adapters.cache.memcached_adapter import MemcachedCacheAdapter
            return MemcachedCacheAdapter(namespace, config)
        else:
            # Default to fallback adapter
            from hermes.adapters.cache.fallback_adapter import FallbackCacheAdapter
            logger.warning(f"Using fallback cache adapter for backend {backend}")
            return FallbackCacheAdapter(namespace, config)
    
    @staticmethod
    def _create_relational_adapter(backend: DatabaseBackend,
                                namespace: str,
                                config: Optional[Dict[str, Any]]) -> RelationalDatabaseAdapter:
        """Create a relational database adapter."""
        # Import implementations dynamically
        if backend == DatabaseBackend.SQLITE:
            from hermes.adapters.relation.sqlite_adapter import SQLiteRelationalAdapter
            return SQLiteRelationalAdapter(namespace, config)
        elif backend == DatabaseBackend.POSTGRES:
            from hermes.adapters.relation.postgres_adapter import PostgresRelationalAdapter
            return PostgresRelationalAdapter(namespace, config)
        else:
            # Default to fallback adapter
            from hermes.adapters.relation.fallback_adapter import FallbackRelationalAdapter
            logger.warning(f"Using fallback relational adapter for backend {backend}")
            return FallbackRelationalAdapter(namespace, config)