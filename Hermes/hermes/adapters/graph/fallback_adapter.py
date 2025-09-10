"""
Fallback Graph Adapter - Simple in-memory graph database implementation.

This module provides a fallback GraphDatabaseAdapter implementation that uses
NetworkX for basic graph operations when no other backend is available.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
import networkx as nx

from hermes.core.database.adapters.graph import GraphDatabaseAdapter
from hermes.core.database.database_types import DatabaseBackend

logger = logging.getLogger("hermes.adapters.graph.fallback")


class FallbackGraphAdapter(GraphDatabaseAdapter):
    """
    Fallback graph database adapter using NetworkX.
    
    This adapter provides basic graph operations using an in-memory
    NetworkX graph when no other backend is available.
    """
    
    def __init__(self, namespace: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the fallback graph adapter.
        
        Args:
            namespace: Namespace for data isolation
            config: Optional configuration parameters
        """
        super().__init__(namespace, config)
        self.graph = nx.DiGraph()
        self._connected = False
        logger.info(f"Fallback graph adapter initialized for namespace {namespace}")
    
    @property
    def backend(self) -> DatabaseBackend:
        """Get the database backend."""
        return DatabaseBackend.NETWORKX
    
    async def connect(self) -> bool:
        """Connect to the database (no-op for in-memory)."""
        self._connected = True
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from the database (no-op for in-memory)."""
        self._connected = False
        return True
    
    async def is_connected(self) -> bool:
        """Check if connected to the database."""
        return self._connected
    
    async def add_node(self, node_id: str, attributes: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a node to the graph.
        
        Args:
            node_id: Unique identifier for the node
            attributes: Optional node attributes
            
        Returns:
            True if node was added successfully
        """
        try:
            self.graph.add_node(node_id, **(attributes or {}))
            return True
        except Exception as e:
            logger.error(f"Error adding node: {e}")
            return False
    
    async def add_edge(self, source_id: str, target_id: str, 
                      relationship: str, attributes: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add an edge between two nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            relationship: Type of relationship
            attributes: Optional edge attributes
            
        Returns:
            True if edge was added successfully
        """
        try:
            attrs = attributes or {}
            attrs['relationship'] = relationship
            self.graph.add_edge(source_id, target_id, **attrs)
            return True
        except Exception as e:
            logger.error(f"Error adding edge: {e}")
            return False
    
    async def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node and its attributes.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Node attributes if found, None otherwise
        """
        if node_id in self.graph:
            return dict(self.graph.nodes[node_id])
        return None
    
    async def get_neighbors(self, node_id: str, relationship: Optional[str] = None) -> List[str]:
        """
        Get neighboring nodes.
        
        Args:
            node_id: Node identifier
            relationship: Optional filter by relationship type
            
        Returns:
            List of neighbor node IDs
        """
        if node_id not in self.graph:
            return []
        
        neighbors = []
        for neighbor in self.graph.neighbors(node_id):
            if relationship:
                edge_data = self.graph.get_edge_data(node_id, neighbor)
                if edge_data and edge_data.get('relationship') == relationship:
                    neighbors.append(neighbor)
            else:
                neighbors.append(neighbor)
        
        return neighbors
    
    async def query(self, query_str: str) -> List[Dict[str, Any]]:
        """
        Execute a graph query (limited support in fallback).
        
        Args:
            query_str: Query string (not used in fallback)
            
        Returns:
            Empty list (queries not supported in fallback)
        """
        logger.warning(f"Query not supported in fallback adapter: {query_str}")
        return []
    
    async def delete_node(self, node_id: str) -> bool:
        """
        Delete a node from the graph.
        
        Args:
            node_id: Node identifier
            
        Returns:
            True if deletion successful
        """
        try:
            if node_id in self.graph:
                self.graph.remove_node(node_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting node: {e}")
            return False
    
    async def delete_edge(self, source_id: str, target_id: str) -> bool:
        """
        Delete an edge from the graph.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            
        Returns:
            True if deletion successful
        """
        try:
            if self.graph.has_edge(source_id, target_id):
                self.graph.remove_edge(source_id, target_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting edge: {e}")
            return False
    
    async def clear_namespace(self) -> bool:
        """Clear all data in the namespace."""
        try:
            self.graph.clear()
            return True
        except Exception as e:
            logger.error(f"Error clearing graph: {e}")
            return False