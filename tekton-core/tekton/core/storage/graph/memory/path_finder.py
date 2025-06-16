"""
Path finding algorithms for memory graph store.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from collections import deque

from tekton.core.storage.graph.memory.utils import create_deep_copy

# Configure logger
logger = logging.getLogger(__name__)

class PathFinder:
    """
    Implements path finding algorithms for graph traversal.
    """
    
    def __init__(self, nodes: Dict[str, Dict[str, Any]], edges: Dict[tuple, Dict[str, Any]], node_edges: Dict[str, Dict[str, List]]):
        """
        Initialize path finder.
        
        Args:
            nodes: Node data dictionary
            edges: Edge data dictionary
            node_edges: Node edges index
        """
        self.nodes = nodes
        self.edges = edges
        self.node_edges = node_edges
        
    def find_paths(self, source_id: str, target_id: str, max_depth: int = 3) -> List[List[Dict[str, Any]]]:
        """
        Find paths between two nodes using breadth-first search.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            max_depth: Maximum path length
            
        Returns:
            List of paths, where each path is a list of alternating node and edge dictionaries
        """
        # Check if source and target nodes exist
        if source_id not in self.nodes or target_id not in self.nodes:
            return []
            
        # Limit max depth for performance
        if max_depth > 5:
            max_depth = 5
            logger.warning("Limiting max_depth to 5 for path finding")
            
        # Breadth-first search for paths
        paths = []
        visited = set()
        queue = deque([[(source_id, None)]])  # List of paths, each path is a list of (node_id, edge_key) tuples
        
        while queue and len(paths) < 10:  # Limit to 10 paths
            path = queue.popleft()
            node_id, _ = path[-1]
            
            if node_id == target_id:
                # Convert path to alternating nodes and edges
                result_path = []
                for i, (node_id, edge_key) in enumerate(path):
                    # Add node
                    result_path.append(create_deep_copy(self.nodes[node_id]))
                    
                    # Add edge if not the last node
                    if i < len(path) - 1 and edge_key is not None:
                        result_path.append(create_deep_copy(self.edges[edge_key]))
                        
                paths.append(result_path)
                continue
                
            if len(path) > max_depth:
                continue
                
            visited.add(node_id)
            
            # Get outgoing edges
            for target, edge_key in self.node_edges.get(node_id, {}).get("outgoing", []):
                if target not in visited:
                    new_path = list(path) + [(target, edge_key)]
                    queue.append(new_path)
                    
        return paths
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a simplified query language.
        
        Args:
            query: Query string
            params: Query parameters
            
        Returns:
            Query results
        """
        if params is None:
            params = {}
            
        query = query.strip().lower()
        
        try:
            # Very simple query parser - handle a few basic patterns
            if "match (n) return n" in query:
                # Return all nodes
                return [{"n": create_deep_copy(node_data)} for node_data in self.nodes.values()]
                
            elif "match (n {id:" in query or "match (n {\"id\":" in query:
                # Return node by ID
                node_id = None
                for key, value in params.items():
                    if key == "id" or "id" in query:
                        node_id = value
                        break
                        
                if not node_id and "{id:" in query:
                    # Try to extract ID from query
                    try:
                        start = query.find("{id:") + 5
                        end = query.find("}", start)
                        id_str = query[start:end].strip()
                        if id_str.startswith('"') and id_str.endswith('"'):
                            node_id = id_str[1:-1]
                        elif id_str.startswith("'") and id_str.endswith("'"):
                            node_id = id_str[1:-1]
                        else:
                            node_id = id_str
                    except:
                        pass
                        
                if node_id and node_id in self.nodes:
                    return [{"n": create_deep_copy(self.nodes[node_id])}]
                return []
                
            elif "match (a)-[r]->(b) return" in query:
                # Return all connections
                results = []
                for (source_id, target_id, _), edge_data in self.edges.items():
                    if source_id in self.nodes and target_id in self.nodes:
                        results.append({
                            "a": create_deep_copy(self.nodes[source_id]),
                            "r": create_deep_copy(edge_data),
                            "b": create_deep_copy(self.nodes[target_id])
                        })
                return results
                
            else:
                logger.error(f"Unsupported query: {query}")
                return []
                
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []