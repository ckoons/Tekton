"""
Database Types - Type definitions for Tekton database components.

This module defines the enum types used throughout the database management system,
providing a centralized location for database type definitions.
"""

import os
from enum import Enum
from typing import List


class DatabaseType(Enum):
    """Types of databases supported by the Database Manager."""
    
    VECTOR = "vector"       # Vector database for embeddings and similarity search
    GRAPH = "graph"         # Graph database for knowledge representation
    KEY_VALUE = "key_value" # Key-value store for simple data
    DOCUMENT = "document"   # Document database for structured data
    CACHE = "cache"         # In-memory cache for temporary data
    RELATION = "relation"   # Relational database for structured data
    
    @classmethod
    def from_string(cls, type_str: str) -> 'DatabaseType':
        """Convert string to DatabaseType."""
        try:
            return cls[type_str.upper()]
        except KeyError:
            raise ValueError(f"Unknown database type: {type_str}")


class DatabaseBackend(Enum):
    """Specific database backends supported for each type."""
    
    # Vector database backends
    FAISS = "faiss"         # Facebook CI Similarity Search
    QDRANT = "qdrant"       # Qdrant vector database
    CHROMADB = "chromadb"   # ChromaDB vector database
    LANCEDB = "lancedb"     # LanceDB vector database
    
    # Graph database backends
    NEO4J = "neo4j"         # Neo4j graph database
    NETWORKX = "networkx"   # NetworkX in-memory graph
    
    # Key-value database backends
    REDIS = "redis"         # Redis key-value store
    LEVELDB = "leveldb"     # LevelDB key-value store
    ROCKSDB = "rocksdb"     # RocksDB key-value store
    
    # Document database backends
    MONGODB = "mongodb"     # MongoDB document database
    TINYDB = "tinydb"       # TinyDB lightweight document database
    JSONDB = "jsondb"       # Simple JSON file-based database
    
    # Cache backends
    MEMORY = "memory"       # In-memory cache
    MEMCACHED = "memcached" # Memcached distributed cache
    
    # Relational database backends
    SQLITE = "sqlite"       # SQLite database
    POSTGRES = "postgres"   # PostgreSQL database
    
    @classmethod
    def from_string(cls, backend_str: str) -> 'DatabaseBackend':
        """Convert string to DatabaseBackend."""
        try:
            return cls[backend_str.upper()]
        except KeyError:
            raise ValueError(f"Unknown database backend: {backend_str}")
    
    @classmethod
    def for_type(cls, db_type: DatabaseType) -> List['DatabaseBackend']:
        """Get available backends for a database type."""
        if db_type == DatabaseType.VECTOR:
            return [cls.FAISS, cls.QDRANT, cls.CHROMADB, cls.LANCEDB]
        elif db_type == DatabaseType.GRAPH:
            return [cls.NEO4J, cls.NETWORKX]
        elif db_type == DatabaseType.KEY_VALUE:
            return [cls.REDIS, cls.LEVELDB, cls.ROCKSDB]
        elif db_type == DatabaseType.DOCUMENT:
            return [cls.MONGODB, cls.JSONDB]
        elif db_type == DatabaseType.CACHE:
            return [cls.MEMORY, cls.MEMCACHED]
        elif db_type == DatabaseType.RELATION:
            return [cls.SQLITE, cls.POSTGRES]
        else:
            return []