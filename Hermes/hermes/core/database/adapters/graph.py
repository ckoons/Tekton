"""
Graph Database Adapter - Interface for graph database interactions.

This module defines the interface for graph database operations,
supporting nodes, relationships, and graph queries.
"""

from abc import abstractmethod
from typing import Dict, List, Any, Optional, Union

from hermes.core.database.database_types import DatabaseType
from hermes.core.database.adapters.base import DatabaseAdapter


class GraphDatabaseAdapter(DatabaseAdapter):
    """
    Adapter for graph databases.
    
    This class provides methods for storing and retrieving graph data,
    with support for nodes, relationships, and graph queries.
    """
    
    @property
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.GRAPH
    
    @abstractmethod
    async def add_node(self,
                      id: str,
                      labels: List[str],
                      properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a node to the graph.
        
        Args:
            id: Unique identifier for the node
            labels: List of labels for the node
            properties: Optional node properties
            
        Returns:
            True if operation successful
        """
        pass
    
    @abstractmethod
    async def add_relationship(self,
                             source_id: str,
                             target_id: str,
                             type: str,
                             properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a relationship between nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            type: Relationship type
            properties: Optional relationship properties
            
        Returns:
            True if operation successful
        """
        pass
    
    @abstractmethod
    async def get_node(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.
        
        Args:
            id: Node ID to retrieve
            
        Returns:
            Node with properties if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_relationships(self,
                              node_id: str,
                              types: Optional[List[str]] = None,
                              direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get relationships for a node.
        
        Args:
            node_id: Node ID to get relationships for
            types: Optional list of relationship types to filter by
            direction: Relationship direction ("incoming", "outgoing", or "both")
            
        Returns:
            List of relationships
        """
        pass
    
    @abstractmethod
    async def query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a graph query.
        
        Args:
            query: Query string in the database's query language
            params: Optional query parameters
            
        Returns:
            Query results
        """
        pass
    
    @abstractmethod
    async def delete_node(self, id: str) -> bool:
        """
        Delete a node.
        
        Args:
            id: Node ID to delete
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def delete_relationship(self, 
                                source_id: str, 
                                target_id: str,
                                type: Optional[str] = None) -> bool:
        """
        Delete a relationship.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            type: Optional relationship type
            
        Returns:
            True if deletion successful
        """
        pass