"""
In-memory graph store implementation.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from datetime import datetime

from tekton.core.storage.base import BaseGraphStorage, StorageNamespace
from tekton.core.storage.graph.memory.storage import GraphStorage
from tekton.core.storage.graph.memory.path_finder import PathFinder
from tekton.core.storage.graph.memory.utils import create_deep_copy, generate_edge_id

# Configure logger
logger = logging.getLogger(__name__)

class MemoryGraphStore(BaseGraphStorage):
    """
    In-memory implementation of BaseGraphStorage.
    
    Provides graph storage capabilities using in-memory dictionaries.
    Useful for testing or small datasets where persistence is not required.
    """
    
    def __init__(
        self,
        namespace: str = "default",
        data_path: Optional[str] = None,
        persist: bool = False,
        **kwargs
    ):
        """
        Initialize the in-memory graph store.
        
        Args:
            namespace: Namespace for the graph
            data_path: Directory to store persistent data (if persist=True)
            persist: Whether to persist data to disk
            **kwargs: Additional configuration parameters
        """
        self.namespace = StorageNamespace(namespace)
        self.persist = persist
        
        # Define data path for persistence
        self.data_path = data_path or os.environ.get(
            "TEKTON_GRAPH_DB_PATH", 
            os.path.expanduser(f"~/.tekton/graph_stores/{namespace}")
        )
        
        # Create storage
        self.storage = GraphStorage(self.data_path, self.persist)
        
        # State
        self._initialized = False
        
    async def initialize(self) -> None:
        """
        Initialize the memory graph storage backend.
        
        This method handles loading data if persistence is enabled.
        """
        if self._initialized:
            return
            
        logger.info(f"Initializing memory graph store with namespace: {self.namespace.namespace}")
        
        try:
            # Create directory if persistence is enabled
            if self.persist:
                os.makedirs(self.data_path, exist_ok=True)
                
                # Try to load data
                self.storage.load()
                
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing memory graph store: {e}")
            raise
    
    async def finalize(self) -> None:
        """
        Finalize and clean up the memory graph storage backend.
        
        This method handles saving data if persistence is enabled.
        """
        logger.info("Finalizing memory graph store")
        
        if self._initialized and self.persist:
            self.storage.save()
            
        self._initialized = False
        logger.info("Memory graph store finalized")
    
    async def drop(self) -> Dict[str, str]:
        """
        Drop all data from storage.
        
        Returns:
            Dictionary with status and message
        """
        logger.warning(f"Dropping all data for namespace: {self.namespace.namespace}")
        
        try:
            # Clear data
            self.storage.clear()
            
            return {
                "status": "success",
                "message": f"All data for namespace {self.namespace.namespace} has been dropped"
            }
        except Exception as e:
            logger.error(f"Error dropping memory graph store: {e}")
            return {
                "status": "error",
                "message": f"Failed to drop data: {str(e)}"
            }
    
    async def index_done_callback(self) -> None:
        """
        Callback invoked when indexing operations are complete.
        
        For memory graph store, save data if persistence is enabled.
        """
        if self.persist:
            self.storage.save()
    
    async def has_node(self, node_id: str) -> bool:
        """
        Check if a node exists in the graph.
        
        Args:
            node_id: Node ID to check
            
        Returns:
            True if the node exists, False otherwise
        """
        if not self._initialized:
            logger.error("Memory graph store not initialized")
            return False
            
        return self.storage.has_node(node_id)
    
    async def has_edge(self, source_id: str, target_id: str) -> bool:
        """
        Check if an edge exists between nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            
        Returns:
            True if any edge exists, False otherwise
        """
        if not self._initialized:
            logger.error("Memory graph store not initialized")
            return False
            
        return self.storage.has_edge(source_id, target_id)
    
    async def upsert_node(self, node_id: str, node_data: Dict[str, Any]) -> None:
        """
        Insert or update a node in the graph.
        
        Args:
            node_id: Node ID
            node_data: Node data dictionary
        """
        if not self._initialized:
            logger.error("Memory graph store not initialized")
            raise RuntimeError("Memory graph store not initialized")
            
        # Add or update node
        if not self.storage.add_node(node_id, node_data):
            raise ValueError(f"Failed to add node {node_id}")
            
        # Save data if persistence is enabled
        if self.persist:
            self.storage.save()
    
    async def upsert_edge(self, source_id: str, target_id: str, edge_data: Dict[str, Any]) -> None:
        """
        Insert or update an edge in the graph.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_data: Edge data dictionary
        """
        if not self._initialized:
            logger.error("Memory graph store not initialized")
            raise RuntimeError("Memory graph store not initialized")
            
        # Get edge type
        edge_type = edge_data.get("type", "RELATED_TO")
        
        # Generate a deterministic edge ID if not provided
        if "id" not in edge_data:
            edge_data["id"] = generate_edge_id(source_id, edge_type, target_id)
        
        # Add or update edge
        if not self.storage.add_edge(source_id, target_id, edge_type, edge_data):
            raise ValueError(f"Failed to add edge from {source_id} to {target_id}")
            
        # Save data if persistence is enabled
        if self.persist:
            self.storage.save()
    
    async def delete_node(self, node_id: str) -> None:
        """
        Delete a node from the graph.
        
        Args:
            node_id: ID of the node to delete
        """
        if not self._initialized:
            logger.error("Memory graph store not initialized")
            raise RuntimeError("Memory graph store not initialized")
            
        # Delete node
        if not self.storage.delete_node(node_id):
            raise ValueError(f"Failed to delete node {node_id}")
            
        # Save data if persistence is enabled
        if self.persist:
            self.storage.save()
    
    async def delete_edge(self, source_id: str, target_id: str) -> None:
        """
        Delete an edge from the graph.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
        """
        if not self._initialized:
            logger.error("Memory graph store not initialized")
            raise RuntimeError("Memory graph store not initialized")
            
        # Delete edge
        if not self.storage.delete_edge(source_id, target_id):
            raise ValueError(f"Failed to delete edge from {source_id} to {target_id}")
            
        # Save data if persistence is enabled
        if self.persist:
            self.storage.save()
    
    async def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.
        
        Args:
            node_id: Node ID to retrieve
            
        Returns:
            Node data dictionary or None if not found
        """
        if not self._initialized:
            logger.error("Memory graph store not initialized")
            return None
            
        return self.storage.get_node(node_id)
    
    async def get_edge(self, source_id: str, target_id: str) -> Optional[Dict[str, Any]]:
        """
        Get edge data between two nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            
        Returns:
            Edge data dictionary or None if not found
        """
        if not self._initialized:
            logger.error("Memory graph store not initialized")
            return None
            
        return self.storage.get_edge(source_id, target_id)
    
    async def get_node_edges(self, 
                          node_id: str, 
                          direction: str = "both") -> List[Tuple[str, Dict[str, Any]]]:
        """
        Get all edges connected to a node.
        
        Args:
            node_id: Node ID
            direction: Edge direction ("outgoing", "incoming", or "both")
            
        Returns:
            List of (connected_node_id, edge_data) tuples
        """
        if not self._initialized:
            logger.error("Memory graph store not initialized")
            return []
            
        return self.storage.get_node_edges(node_id, direction)
    
    async def find_paths(self, 
                     source_id: str, 
                     target_id: str, 
                     max_depth: int = 3) -> List[List[Dict[str, Any]]]:
        """
        Find paths between two nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            max_depth: Maximum path length
            
        Returns:
            List of paths, where each path is a list of alternating node and edge dictionaries
        """
        if not self._initialized:
            logger.error("Memory graph store not initialized")
            return []
            
        # Create path finder
        path_finder = PathFinder(
            self.storage.nodes,
            self.storage.edges,
            self.storage.node_edges
        )
        
        return path_finder.find_paths(source_id, target_id, max_depth)
    
    async def execute_query(self, 
                         query: str, 
                         params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a native graph query.
        
        For memory graph store, supports simple query language with:
        - MATCH (n) RETURN n - return all nodes
        - MATCH (n {id: "123"}) RETURN n - return node by ID
        - MATCH (a)-[r]->(b) RETURN a, r, b - return all connections
        
        Args:
            query: Query string in simplified query language
            params: Query parameters
            
        Returns:
            Query results as a list of dictionaries
        """
        if not self._initialized:
            logger.error("Memory graph store not initialized")
            return []
            
        # Create path finder
        path_finder = PathFinder(
            self.storage.nodes,
            self.storage.edges,
            self.storage.node_edges
        )
        
        return path_finder.execute_query(query, params)