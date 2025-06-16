"""
Core functionality for Hermes centralized database services and messaging.
"""

from hermes.core.vector_engine import VectorEngine
from hermes.core.message_bus import MessageBus
from hermes.core.service_discovery import ServiceRegistry
from hermes.core.registration import RegistrationManager, RegistrationClient, RegistrationToken
from hermes.core.logging import (
    LogLevel, LogEntry, LogManager, Logger, 
    init_logging, get_logger
)

# Import database types and core components
from hermes.core.database_manager import (
    DatabaseType, DatabaseBackend, DatabaseManager, DatabaseFactory
)

# Import database adapters
try:
    from hermes.core.database.adapters import (
        DatabaseAdapter, VectorDatabaseAdapter, GraphDatabaseAdapter,
        KeyValueDatabaseAdapter, DocumentDatabaseAdapter, CacheDatabaseAdapter,
        RelationalDatabaseAdapter
    )
except ImportError as e:
    # Create stub classes for compatibility
    import logging
    logging.warning(f"Unable to import database adapters: {e}")
    from abc import ABC
    
    class DatabaseAdapter(ABC):
        """Stub for DatabaseAdapter"""
        pass
    
    class VectorDatabaseAdapter(DatabaseAdapter):
        """Stub for VectorDatabaseAdapter"""
        pass
    
    class GraphDatabaseAdapter(DatabaseAdapter):
        """Stub for GraphDatabaseAdapter"""
        pass
    
    class KeyValueDatabaseAdapter(DatabaseAdapter):
        """Stub for KeyValueDatabaseAdapter"""
        pass
    
    class DocumentDatabaseAdapter(DatabaseAdapter):
        """Stub for DocumentDatabaseAdapter"""
        pass
    
    class CacheDatabaseAdapter(DatabaseAdapter):
        """Stub for CacheDatabaseAdapter"""
        pass
    
    class RelationalDatabaseAdapter(DatabaseAdapter):
        """Stub for RelationalDatabaseAdapter"""
        pass

__all__ = [
    # Vector operations
    "VectorEngine", 
    
    # Messaging and discovery
    "MessageBus", 
    "ServiceRegistry", 
    
    # Registration
    "RegistrationManager",
    "RegistrationClient",
    "RegistrationToken",
    
    # Logging
    "LogLevel",
    "LogEntry",
    "LogManager",
    "Logger",
    "init_logging",
    "get_logger",
    
    # Database Management
    "DatabaseType",
    "DatabaseBackend",
    "DatabaseManager",
    "DatabaseFactory",
    
    # Database Adapters
    "DatabaseAdapter",
    "VectorDatabaseAdapter",
    "GraphDatabaseAdapter",
    "KeyValueDatabaseAdapter",
    "DocumentDatabaseAdapter",
    "CacheDatabaseAdapter",
    "RelationalDatabaseAdapter"
]