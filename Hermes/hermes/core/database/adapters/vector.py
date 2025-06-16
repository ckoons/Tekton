"""
Vector Database Adapter - Interface for vector database interactions.

This module defines the interface for vector database operations,
supporting vector storage, retrieval, and similarity search.
"""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Union

from hermes.core.database.database_types import DatabaseType
from hermes.core.database.adapters.base import DatabaseAdapter


class VectorDatabaseAdapter(DatabaseAdapter):
    """
    Adapter for vector databases.
    
    This class provides methods for storing and retrieving vector embeddings,
    with support for similarity search and metadata filtering.
    """
    
    @property
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.VECTOR
    
    @abstractmethod
    async def store(self,
                   id: str,
                   vector: List[float],
                   metadata: Optional[Dict[str, Any]] = None,
                   text: Optional[str] = None) -> bool:
        """
        Store a vector in the database.
        
        Args:
            id: Unique identifier for the vector
            vector: The vector embedding
            metadata: Optional metadata to store with the vector
            text: Optional text content associated with the vector
            
        Returns:
            True if storage successful
        """
        pass
    
    @abstractmethod
    async def search(self,
                    query_vector: List[float],
                    limit: int = 10,
                    filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: The query vector
            limit: Maximum number of results
            filter: Optional metadata filter
            
        Returns:
            List of matching vectors with metadata and similarity scores
        """
        pass
    
    @abstractmethod
    async def delete(self,
                    id: Optional[str] = None,
                    filter: Optional[Dict[str, Any]] = None) -> bool:
        """
        Delete vectors from the database.
        
        Args:
            id: Optional specific vector ID to delete
            filter: Optional metadata filter for bulk deletion
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def get(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific vector by ID.
        
        Args:
            id: Vector ID to retrieve
            
        Returns:
            Vector with metadata if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list(self,
                  limit: int = 100,
                  offset: int = 0,
                  filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List vectors in the database.
        
        Args:
            limit: Maximum number of results
            offset: Starting offset for pagination
            filter: Optional metadata filter
            
        Returns:
            List of vectors with metadata
        """
        pass