"""
Database Manager - Centralized database services for Tekton components.

This module provides a unified interface for all database operations in the Tekton
ecosystem, supporting different database types with namespace isolation.
"""

# Import key components for easy access
from hermes.core.database.database_types import DatabaseType, DatabaseBackend
from hermes.core.database.factory import DatabaseFactory
from hermes.core.database.manager import DatabaseManager

# Export the main classes
__all__ = [
    "DatabaseType",
    "DatabaseBackend", 
    "DatabaseFactory",
    "DatabaseManager"
]