"""
Document Database Adapter - Interface for document database interactions.

This module defines the interface for document database operations,
supporting CRUD operations on structured documents.
"""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Union

from hermes.core.database.database_types import DatabaseType
from hermes.core.database.adapters.base import DatabaseAdapter


class DocumentDatabaseAdapter(DatabaseAdapter):
    """
    Adapter for document databases.
    
    This class provides methods for storing and retrieving structured documents,
    with support for queries and indexing.
    """
    
    @property
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.DOCUMENT
    
    @abstractmethod
    async def insert(self,
                    collection: str,
                    document: Dict[str, Any],
                    id: Optional[str] = None) -> str:
        """
        Insert a document.
        
        Args:
            collection: Collection name
            document: Document to insert
            id: Optional document ID (generated if not provided)
            
        Returns:
            Document ID
        """
        pass
    
    @abstractmethod
    async def find(self,
                 collection: str,
                 query: Dict[str, Any],
                 projection: Optional[Dict[str, bool]] = None,
                 limit: int = 100,
                 offset: int = 0) -> List[Dict[str, Any]]:
        """
        Find documents matching a query.
        
        Args:
            collection: Collection name
            query: Query to match documents
            projection: Optional fields to include or exclude
            limit: Maximum number of results
            offset: Starting offset for pagination
            
        Returns:
            List of matching documents
        """
        pass
    
    @abstractmethod
    async def find_one(self,
                     collection: str,
                     query: Dict[str, Any],
                     projection: Optional[Dict[str, bool]] = None) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching a query.
        
        Args:
            collection: Collection name
            query: Query to match documents
            projection: Optional fields to include or exclude
            
        Returns:
            Matching document if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update(self,
                   collection: str,
                   query: Dict[str, Any],
                   update: Dict[str, Any],
                   upsert: bool = False) -> int:
        """
        Update documents matching a query.
        
        Args:
            collection: Collection name
            query: Query to match documents
            update: Update operations
            upsert: Whether to insert if no matching document exists
            
        Returns:
            Number of documents updated
        """
        pass
    
    @abstractmethod
    async def delete(self,
                   collection: str,
                   query: Dict[str, Any]) -> int:
        """
        Delete documents matching a query.
        
        Args:
            collection: Collection name
            query: Query to match documents
            
        Returns:
            Number of documents deleted
        """
        pass
    
    @abstractmethod
    async def count(self,
                  collection: str,
                  query: Dict[str, Any]) -> int:
        """
        Count documents matching a query.
        
        Args:
            collection: Collection name
            query: Query to match documents
            
        Returns:
            Number of matching documents
        """
        pass