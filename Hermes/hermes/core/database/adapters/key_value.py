"""
Key-Value Database Adapter - Interface for key-value database interactions.

This module defines the interface for key-value database operations,
supporting basic CRUD operations and batch processing.
"""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Union

from hermes.core.database.database_types import DatabaseType
from hermes.core.database.adapters.base import DatabaseAdapter


class KeyValueDatabaseAdapter(DatabaseAdapter):
    """
    Adapter for key-value databases.
    
    This class provides methods for storing and retrieving key-value pairs,
    with support for expiration and batch operations.
    """
    
    @property
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.KEY_VALUE
    
    @abstractmethod
    async def set(self,
                key: str,
                value: Any,
                expiration: Optional[int] = None) -> bool:
        """
        Set a key-value pair.
        
        Args:
            key: The key
            value: The value
            expiration: Optional expiration time in seconds
            
        Returns:
            True if operation successful
        """
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value by key.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete a key-value pair.
        
        Args:
            key: The key to delete
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists.
        
        Args:
            key: The key to check
            
        Returns:
            True if the key exists
        """
        pass
    
    @abstractmethod
    async def set_batch(self,
                       items: Dict[str, Any],
                       expiration: Optional[int] = None) -> bool:
        """
        Set multiple key-value pairs.
        
        Args:
            items: Dictionary of key-value pairs
            expiration: Optional expiration time in seconds
            
        Returns:
            True if operation successful
        """
        pass
    
    @abstractmethod
    async def get_batch(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values by keys.
        
        Args:
            keys: List of keys to retrieve
            
        Returns:
            Dictionary of key-value pairs for found keys
        """
        pass
    
    @abstractmethod
    async def delete_batch(self, keys: List[str]) -> bool:
        """
        Delete multiple key-value pairs.
        
        Args:
            keys: List of keys to delete
            
        Returns:
            True if operation successful
        """
        pass