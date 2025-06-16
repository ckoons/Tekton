"""
Cache Database Adapter - Interface for cache database interactions.

This module defines the interface for cache database operations,
supporting temporary storage with expiration.
"""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Union

from hermes.core.database.database_types import DatabaseType
from hermes.core.database.adapters.base import DatabaseAdapter


class CacheDatabaseAdapter(DatabaseAdapter):
    """
    Adapter for cache databases.
    
    This class provides methods for caching data with expiration,
    supporting both simple values and structured data.
    """
    
    @property
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.CACHE
    
    @abstractmethod
    async def set(self,
                key: str,
                value: Any,
                expiration: int) -> bool:
        """
        Set a cached value with expiration.
        
        Args:
            key: Cache key
            value: Value to cache
            expiration: Expiration time in seconds
            
        Returns:
            True if operation successful
        """
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a cached value.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete a cached value.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def flush(self) -> bool:
        """
        Clear all cached values.
        
        Returns:
            True if operation successful
        """
        pass
    
    @abstractmethod
    async def touch(self,
                  key: str,
                  expiration: int) -> bool:
        """
        Update expiration for a cached value.
        
        Args:
            key: Cache key
            expiration: New expiration time in seconds
            
        Returns:
            True if operation successful
        """
        pass