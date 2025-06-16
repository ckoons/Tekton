"""
Graph Database Client - Client interface for graph database operations.

This module provides a client for accessing graph database services.
"""

from typing import Dict, List, Any, Optional, Union
from hermes.api.database.client_base import BaseRequest


class GraphDatabaseClient:
    """
    Client for interacting with graph database services.
    
    This class provides methods for graph operations like adding nodes,
    creating relationships, and executing queries.
    """
    
    def __init__(self, request_handler: BaseRequest):
        """
        Initialize the graph database client.
        
        Args:
            request_handler: Base request handler for API communication
        """
        self.request_handler = request_handler
    
    async def add_node(self,
                     node_id: str,
                     labels: List[str],
                     properties: Dict[str, Any],
                     namespace: str = "default",
                     backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a node to the graph.
        
        Args:
            node_id: ID for the node
            labels: List of labels/types for the node
            properties: Node properties
            namespace: Namespace for the data
            backend: Optional specific backend to use
            
        Returns:
            Result of the node addition
        """
        parameters = {
            "node_id": node_id,
            "labels": labels,
            "properties": properties,
            "namespace": namespace
        }
        
        if backend:
            parameters["backend"] = backend
        
        return await self.request_handler.execute_request(
            capability="graph_add_node",
            api_path=f"graph/{namespace}/node",
            parameters=parameters
        )
    
    async def add_relationship(self,
                             source_id: str,
                             target_id: str,
                             rel_type: str,
                             properties: Optional[Dict[str, Any]] = None,
                             namespace: str = "default",
                             backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a relationship between nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            rel_type: Relationship type
            properties: Optional relationship properties
            namespace: Namespace for the data
            backend: Optional specific backend to use
            
        Returns:
            Result of the relationship addition
        """
        parameters = {
            "source_id": source_id,
            "target_id": target_id,
            "type": rel_type,
            "namespace": namespace
        }
        
        if properties:
            parameters["properties"] = properties
        if backend:
            parameters["backend"] = backend
        
        return await self.request_handler.execute_request(
            capability="graph_add_relationship",
            api_path=f"graph/{namespace}/relationship",
            parameters=parameters
        )
    
    async def query(self,
                  query: str,
                  query_params: Optional[Dict[str, Any]] = None,
                  namespace: str = "default",
                  backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a graph query.
        
        Args:
            query: Query string (e.g., Cypher for Neo4j)
            query_params: Optional query parameters
            namespace: Namespace for the data
            backend: Optional specific backend to use
            
        Returns:
            Query results
        """
        parameters = {
            "query": query,
            "namespace": namespace
        }
        
        if query_params:
            parameters["parameters"] = query_params
        if backend:
            parameters["backend"] = backend
        
        return await self.request_handler.execute_request(
            capability="graph_query",
            api_path=f"graph/{namespace}/query",
            parameters=parameters
        )