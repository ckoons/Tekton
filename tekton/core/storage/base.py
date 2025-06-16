"""
Base storage interfaces for Tekton components.

These interfaces define the standard contract for storage implementations
across the Tekton ecosystem, allowing for interchangeable backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Set, Tuple, TypeVar, Generic
import numpy as np

@dataclass
class StorageNamespace:
    """
    Namespace for storage backends.
    
    Provides isolation between different storage instances
    to avoid key collisions.
    """
    namespace: str
    """Unique namespace identifier for the storage instance."""
    
    global_config: Dict[str, Any] = field(default_factory=dict)
    """Global configuration parameters for the storage backend."""

class BaseStorage(ABC):
    """
    Base interface for all storage backends.
    
    Defines common lifecycle and management methods that all
    storage implementations must support.
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the storage backend.
        
        This method should handle:
        - Connection establishment
        - Schema creation/verification
        - Index initialization
        - Resource allocation
        """
        pass
        
    @abstractmethod
    async def finalize(self) -> None:
        """
        Finalize and clean up the storage backend.
        
        This method should handle:
        - Connection closure
        - Resource cleanup
        - Persistence of unsaved changes
        """
        pass
        
    @abstractmethod
    async def drop(self) -> Dict[str, str]:
        """
        Drop all data from storage.
        
        Returns:
            Dictionary with status and message:
            {
                "status": "success" | "error" | "unsupported",
                "message": "Description of result"
            }
        """
        pass
        
    @abstractmethod
    async def index_done_callback(self) -> None:
        """
        Callback invoked when indexing operations are complete.
        
        This method should handle:
        - Persistence of changes
        - Index optimization
        - Notification of other processes
        """
        pass

T = TypeVar('T')

class BaseVectorStorage(BaseStorage):
    """
    Interface for vector database storage.
    
    Defines methods for storing and querying vector embeddings,
    including metadata and similarity search.
    """
    
    @abstractmethod
    async def query(self, 
                  query_vector: np.ndarray, 
                  top_k: int = 10,
                  filter_ids: Optional[List[str]] = None,
                  similarity_threshold: float = 0.2) -> List[Dict[str, Any]]:
        """
        Query vector database for similar vectors.
        
        Args:
            query_vector: The query vector to search for
            top_k: Maximum number of results to return
            filter_ids: Optional list of IDs to filter results
            similarity_threshold: Minimum similarity score threshold
            
        Returns:
            List of dictionaries with vector data and metadata
        """
        pass
        
    @abstractmethod
    async def upsert(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Insert or update vectors in storage.
        
        Args:
            data: Dictionary mapping IDs to vector data and metadata
        """
        pass
        
    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """
        Delete vectors with specified IDs.
        
        Args:
            ids: List of vector IDs to delete
        """
        pass
        
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get vector data by ID.
        
        Args:
            id: The vector ID to retrieve
            
        Returns:
            Dictionary with vector data and metadata, or None if not found
        """
        pass
        
    @abstractmethod
    async def get_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple vector data by their IDs.
        
        Args:
            ids: List of vector IDs to retrieve
            
        Returns:
            List of dictionaries with vector data and metadata
        """
        pass

class BaseGraphStorage(BaseStorage):
    """
    Interface for graph database storage.
    
    Defines methods for storing and querying graph data,
    including nodes, edges, and traversal operations.
    """
    
    @abstractmethod
    async def has_node(self, node_id: str) -> bool:
        """
        Check if a node exists in the graph.
        
        Args:
            node_id: Node ID to check
            
        Returns:
            True if the node exists, False otherwise
        """
        pass
        
    @abstractmethod
    async def has_edge(self, source_id: str, target_id: str) -> bool:
        """
        Check if an edge exists between nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            
        Returns:
            True if the edge exists, False otherwise
        """
        pass
        
    @abstractmethod
    async def upsert_node(self, node_id: str, node_data: Dict[str, Any]) -> None:
        """
        Insert or update a node in the graph.
        
        Args:
            node_id: Node ID
            node_data: Node data dictionary
        """
        pass
        
    @abstractmethod
    async def upsert_edge(self, 
                       source_id: str, 
                       target_id: str, 
                       edge_data: Dict[str, Any]) -> None:
        """
        Insert or update an edge in the graph.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_data: Edge data dictionary
        """
        pass
        
    @abstractmethod
    async def delete_node(self, node_id: str) -> None:
        """
        Delete a node from the graph.
        
        Args:
            node_id: ID of the node to delete
        """
        pass
        
    @abstractmethod
    async def delete_edge(self, source_id: str, target_id: str) -> None:
        """
        Delete an edge from the graph.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
        """
        pass
        
    @abstractmethod
    async def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.
        
        Args:
            node_id: Node ID to retrieve
            
        Returns:
            Node data dictionary or None if not found
        """
        pass
        
    @abstractmethod
    async def get_edge(self, 
                    source_id: str, 
                    target_id: str) -> Optional[Dict[str, Any]]:
        """
        Get edge data between two nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            
        Returns:
            Edge data dictionary or None if not found
        """
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
    async def execute_query(self, 
                         query: str, 
                         params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a native graph query.
        
        Args:
            query: Query string in the native graph database language
            params: Query parameters
            
        Returns:
            Query results as a list of dictionaries
        """
        pass

class BaseKVStorage(BaseStorage):
    """
    Interface for key-value storage.
    
    Defines methods for storing and retrieving arbitrary
    data by key.
    """
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get value by ID.
        
        Args:
            id: The key to retrieve
            
        Returns:
            Value dictionary or None if not found
        """
        pass
        
    @abstractmethod
    async def get_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple values by IDs.
        
        Args:
            ids: List of keys to retrieve
            
        Returns:
            List of value dictionaries that were found
        """
        pass
        
    @abstractmethod
    async def filter_keys(self, keys: Set[str]) -> Set[str]:
        """
        Find which keys don't exist in storage.
        
        Args:
            keys: Set of keys to check
            
        Returns:
            Set of keys that don't exist in storage
        """
        pass
        
    @abstractmethod
    async def upsert(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Insert or update data.
        
        Args:
            data: Dictionary mapping keys to value dictionaries
        """
        pass
        
    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """
        Delete data by IDs.
        
        Args:
            ids: List of keys to delete
        """
        pass
        
    @abstractmethod
    async def clear_cache(self, cache_types: Optional[List[str]] = None) -> bool:
        """
        Clear cached data.
        
        Args:
            cache_types: Optional list of cache types to clear
            
        Returns:
            True if cache was cleared successfully, False otherwise
        """
        pass