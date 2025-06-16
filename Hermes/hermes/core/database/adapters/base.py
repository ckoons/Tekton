"""
Base Database Adapter - Abstract interface definition for database interactions.

This module defines the base interface that all database adapters must implement,
providing a consistent API regardless of the underlying database technology.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

from hermes.core.database.database_types import DatabaseType, DatabaseBackend


class DatabaseAdapter(ABC):
    """
    Abstract base class for database adapters.
    
    This class defines the interface that all database adapters must implement,
    providing a consistent API regardless of the underlying database.
    """
    
    def __init__(self, 
                namespace: str,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the database adapter.
        
        Args:
            namespace: Namespace for data isolation
            config: Optional configuration parameters
        """
        self.namespace = namespace
        self.config = config or {}
        self.client = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the database.
        
        Returns:
            True if connection successful
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the database.
        
        Returns:
            True if disconnection successful
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if connected to the database.
        
        Returns:
            True if connected
        """
        pass
    
    @property
    @abstractmethod
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        pass
    
    @property
    @abstractmethod
    def backend(self) -> DatabaseBackend:
        """Get the database backend."""
        pass