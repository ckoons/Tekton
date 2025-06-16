"""
Storage management for memory graph store.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Set, Tuple, Union

from tekton.core.storage.graph.memory.utils import (
    save_to_json,
    load_from_json,
    get_edge_key,
    create_deep_copy
)

# Configure logger
logger = logging.getLogger(__name__)

class GraphStorage:
    """
    In-memory graph storage with optional persistence.
    """
    
    def __init__(self, data_path: Optional[str] = None, persist: bool = False):
        """
        Initialize the graph storage.
        
        Args:
            data_path: Path to store persistent data
            persist: Whether to persist data to disk
        """
        self.data_path = data_path
        self.persist = persist
        
        # Define state
        self.nodes = {}  # id -> node data
        self.edges = {}  # (source_id, target_id, type) -> edge data
        self.node_edges = {}  # node_id -> {outgoing: [(target_id, edge_key)], incoming: [(source_id, edge_key)]}
        
    def load(self) -> bool:
        """
        Load data from disk if persistence is enabled.
        
        Returns:
            True if successful
        """
        if not self.persist:
            return True
            
        nodes_path = os.path.join(self.data_path, "nodes.json")
        edges_path = os.path.join(self.data_path, "edges.json")
        
        try:
            # Load nodes
            nodes_data = load_from_json(nodes_path)
            if nodes_data:
                self.nodes = nodes_data
                logger.info(f"Loaded {len(self.nodes)} nodes from disk")
                
            # Load edges
            edges_data = load_from_json(edges_path)
            if edges_data:
                # Convert string keys back to tuples
                self.edges = {}
                for key_str, edge_data in edges_data.items():
                    key_parts = json.loads(key_str)
                    self.edges[tuple(key_parts)] = edge_data
                logger.info(f"Loaded {len(self.edges)} edges from disk")
                
            # Rebuild node_edges index
            self._rebuild_node_edges_index()
            
            return True
        except Exception as e:
            logger.error(f"Error loading data from disk: {e}")
            self.nodes = {}
            self.edges = {}
            self.node_edges = {}
            return False
            
    def save(self) -> bool:
        """
        Save data to disk if persistence is enabled.
        
        Returns:
            True if successful
        """
        if not self.persist:
            return True
            
        try:
            nodes_path = os.path.join(self.data_path, "nodes.json")
            edges_path = os.path.join(self.data_path, "edges.json")
            
            # Save nodes
            if not save_to_json(self.nodes, nodes_path):
                return False
                
            # Save edges - convert tuple keys to strings
            edges_data = {}
            for key, edge_data in self.edges.items():
                key_str = json.dumps(key)
                edges_data[key_str] = edge_data
                
            if not save_to_json(edges_data, edges_path):
                return False
                
            logger.info(f"Saved {len(self.nodes)} nodes and {len(self.edges)} edges to disk")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data to disk: {e}")
            return False
            
    def _rebuild_node_edges_index(self) -> None:
        """Rebuild the node_edges index from edges data."""
        self.node_edges = {}
        
        for (source_id, target_id, edge_type) in self.edges.keys():
            # Initialize if needed
            if source_id not in self.node_edges:
                self.node_edges[source_id] = {"outgoing": [], "incoming": []}
            if target_id not in self.node_edges:
                self.node_edges[target_id] = {"outgoing": [], "incoming": []}
                
            # Add edge to index
            edge_key = (source_id, target_id, edge_type)
            self.node_edges[source_id]["outgoing"].append((target_id, edge_key))
            self.node_edges[target_id]["incoming"].append((source_id, edge_key))
    
    def clear(self) -> None:
        """Clear all data."""
        self.nodes = {}
        self.edges = {}
        self.node_edges = {}
        
        # Delete files if persistence is enabled
        if self.persist:
            nodes_path = os.path.join(self.data_path, "nodes.json")
            edges_path = os.path.join(self.data_path, "edges.json")
            
            if os.path.exists(nodes_path):
                os.remove(nodes_path)
            if os.path.exists(edges_path):
                os.remove(edges_path)
    
    def has_node(self, node_id: str) -> bool:
        """
        Check if a node exists.
        
        Args:
            node_id: Node ID to check
            
        Returns:
            True if the node exists
        """
        return node_id in self.nodes
    
    def has_edge(self, source_id: str, target_id: str) -> bool:
        """
        Check if any edge exists between nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            
        Returns:
            True if any edge exists
        """
        # Check if source and target nodes exist
        if source_id not in self.nodes or target_id not in self.nodes:
            return False
            
        # Check if source node has outgoing edge to target
        source_edges = self.node_edges.get(source_id, {}).get("outgoing", [])
        for target, _ in source_edges:
            if target == target_id:
                return True
                
        return False
    
    def add_node(self, node_id: str, node_data: Dict[str, Any]) -> bool:
        """
        Add or update a node.
        
        Args:
            node_id: Node ID
            node_data: Node data
            
        Returns:
            True if successful
        """
        # Add or update node
        is_new = node_id not in self.nodes
        
        # Deep copy to avoid reference issues
        self.nodes[node_id] = create_deep_copy(node_data)
        
        # Initialize edges structure if new node
        if is_new:
            self.node_edges[node_id] = {
                "outgoing": [],
                "incoming": []
            }
            
        return True
    
    def add_edge(self, source_id: str, target_id: str, edge_type: str, edge_data: Dict[str, Any]) -> bool:
        """
        Add or update an edge.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Edge type
            edge_data: Edge data
            
        Returns:
            True if successful
        """
        # Check if source and target nodes exist
        if source_id not in self.nodes:
            logger.error(f"Source node {source_id} does not exist")
            return False
        if target_id not in self.nodes:
            logger.error(f"Target node {target_id} does not exist")
            return False
            
        # Create edge key
        edge_key = get_edge_key(source_id, target_id, edge_type)
        
        # Add or update edge
        is_new = edge_key not in self.edges
        
        # Deep copy to avoid reference issues
        data_copy = create_deep_copy(edge_data)
        data_copy["type"] = edge_type
        self.edges[edge_key] = data_copy
        
        # Update node_edges index if new edge
        if is_new:
            # Initialize if needed
            if source_id not in self.node_edges:
                self.node_edges[source_id] = {"outgoing": [], "incoming": []}
            if target_id not in self.node_edges:
                self.node_edges[target_id] = {"outgoing": [], "incoming": []}
                
            # Add edge to index
            self.node_edges[source_id]["outgoing"].append((target_id, edge_key))
            self.node_edges[target_id]["incoming"].append((source_id, edge_key))
            
        return True
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node and all connected edges.
        
        Args:
            node_id: Node ID
            
        Returns:
            True if successful
        """
        # Check if node exists
        if node_id not in self.nodes:
            return True
            
        # Get all connected edges
        edges_to_delete = []
        
        # Get outgoing edges
        for target, edge_key in self.node_edges.get(node_id, {}).get("outgoing", []):
            edges_to_delete.append(edge_key)
            
            # Remove from target's incoming edges
            if target in self.node_edges:
                self.node_edges[target]["incoming"] = [
                    (src, key) for src, key in self.node_edges[target]["incoming"]
                    if src != node_id
                ]
                
        # Get incoming edges
        for source, edge_key in self.node_edges.get(node_id, {}).get("incoming", []):
            edges_to_delete.append(edge_key)
            
            # Remove from source's outgoing edges
            if source in self.node_edges:
                self.node_edges[source]["outgoing"] = [
                    (tgt, key) for tgt, key in self.node_edges[source]["outgoing"]
                    if tgt != node_id
                ]
                
        # Delete edges
        for edge_key in edges_to_delete:
            if edge_key in self.edges:
                del self.edges[edge_key]
                
        # Delete node
        del self.nodes[node_id]
        if node_id in self.node_edges:
            del self.node_edges[node_id]
            
        return True
    
    def delete_edge(self, source_id: str, target_id: str) -> bool:
        """
        Delete all edges between two nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            
        Returns:
            True if successful
        """
        # Find edge keys that match source and target
        edge_keys_to_delete = []
        for edge_key in self.edges.keys():
            if edge_key[0] == source_id and edge_key[1] == target_id:
                edge_keys_to_delete.append(edge_key)
                
        if not edge_keys_to_delete:
            return True
            
        # Delete edges
        for edge_key in edge_keys_to_delete:
            del self.edges[edge_key]
            
        # Update node_edges index
        if source_id in self.node_edges:
            self.node_edges[source_id]["outgoing"] = [
                (tgt, key) for tgt, key in self.node_edges[source_id]["outgoing"]
                if tgt != target_id
            ]
            
        if target_id in self.node_edges:
            self.node_edges[target_id]["incoming"] = [
                (src, key) for src, key in self.node_edges[target_id]["incoming"]
                if src != source_id
            ]
            
        return True
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node data or None if not found
        """
        # Return a copy to avoid modifying internal state
        node_data = self.nodes.get(node_id)
        return create_deep_copy(node_data) if node_data else None
    
    def get_edge(self, source_id: str, target_id: str) -> Optional[Dict[str, Any]]:
        """
        Get first edge between nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            
        Returns:
            Edge data or None if not found
        """
        # Find first edge that matches source and target
        for edge_key, edge_data in self.edges.items():
            if edge_key[0] == source_id and edge_key[1] == target_id:
                # Return a copy to avoid modifying internal state
                return create_deep_copy(edge_data)
                
        return None
    
    def get_node_edges(self, node_id: str, direction: str = "both") -> List[Tuple[str, Dict[str, Any]]]:
        """
        Get all edges connected to a node.
        
        Args:
            node_id: Node ID
            direction: Edge direction ("outgoing", "incoming", or "both")
            
        Returns:
            List of (connected_node_id, edge_data) tuples
        """
        result = []
        
        # Check if node exists
        if node_id not in self.nodes:
            return []
            
        # Get edges based on direction
        if direction.lower() == "outgoing" or direction.lower() == "both":
            for target_id, edge_key in self.node_edges.get(node_id, {}).get("outgoing", []):
                if edge_key in self.edges:
                    result.append((target_id, create_deep_copy(self.edges[edge_key])))
                    
        if direction.lower() == "incoming" or direction.lower() == "both":
            for source_id, edge_key in self.node_edges.get(node_id, {}).get("incoming", []):
                if edge_key in self.edges:
                    result.append((source_id, create_deep_copy(self.edges[edge_key])))
                    
        return result