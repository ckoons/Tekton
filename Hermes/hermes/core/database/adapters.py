"""
Database Adapters - Abstract interface definitions for database interactions.

This module defines the interfaces that all database adapters must implement,
providing a consistent API regardless of the underlying database technology.

Note: This module is maintained for backward compatibility.
For new code, please import directly from hermes.core.database.adapters.
"""

# Re-export all adapter interfaces for backward compatibility
from hermes.core.database.adapters import (
    DatabaseAdapter,
    VectorDatabaseAdapter,
    GraphDatabaseAdapter,
    KeyValueDatabaseAdapter,
    DocumentDatabaseAdapter,
    CacheDatabaseAdapter,
    RelationalDatabaseAdapter
)

__all__ = [
    "DatabaseAdapter",
    "VectorDatabaseAdapter",
    "GraphDatabaseAdapter",
    "KeyValueDatabaseAdapter",
    "DocumentDatabaseAdapter",
    "CacheDatabaseAdapter",
    "RelationalDatabaseAdapter"
]