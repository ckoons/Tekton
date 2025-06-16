"""
Database Adapters Package - Interface definitions for database interactions.

This package defines the interfaces that all database adapters must implement,
providing a consistent API regardless of the underlying database technology.
"""

# Re-export all adapter interfaces for backward compatibility
from .base import DatabaseAdapter
from .vector import VectorDatabaseAdapter
from .graph import GraphDatabaseAdapter
from .key_value import KeyValueDatabaseAdapter
from .document import DocumentDatabaseAdapter
from .cache import CacheDatabaseAdapter
from .relational import RelationalDatabaseAdapter

__all__ = [
    "DatabaseAdapter",
    "VectorDatabaseAdapter",
    "GraphDatabaseAdapter",
    "KeyValueDatabaseAdapter",
    "DocumentDatabaseAdapter",
    "CacheDatabaseAdapter",
    "RelationalDatabaseAdapter"
]