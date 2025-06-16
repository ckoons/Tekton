"""
Neo4j graph store implementation.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from datetime import datetime

from tekton.core.storage.base import BaseGraphStorage, StorageNamespace
from tekton.core.storage.graph.neo4j.client import Neo4jClient
from tekton.core.storage.graph.neo4j.utils import node_to_dict, relationship_to_dict

# Configure logger
logger = logging.getLogger(__name__)

class Neo4jGraphStore(BaseGraphStorage):
    """
    Neo4j implementation of BaseGraphStorage.
    
    Provides graph storage capabilities using Neo4j, supporting both
    standalone connections and integration with Hermes database services.
    """
    
    def __init__(
        self,
        namespace: str = "default",
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: str = "neo4j",
        node_label: str = "TektonNode",
        use_hermes: bool = False,
        hermes_service_name: str = "neo4j",
        **kwargs
    ):
        """
        Initialize the Neo4j graph store.
        
        Args:
            namespace: Namespace for node and relationship labels
            uri: Neo4j connection URI (e.g., neo4j://localhost:7687)
            username: Neo4j username
            password: Neo4j password
            database: Neo4j database name
            node_label: Base label for all nodes
            use_hermes: Whether to use Hermes for database connection
            hermes_service_name: Hermes service name for the database
            **kwargs: Additional configuration parameters
        """
        self.namespace = StorageNamespace(namespace)
        self._node_label = f"{node_label}_{namespace}"
        
        # Create Neo4j client
        self.client = Neo4jClient(
            use_hermes=use_hermes,
            hermes_service_name=hermes_service_name,
            namespace=namespace,
            uri=uri,
            username=username,
            password=password,
            database=database
        )
        
        # State
        self._initialized = False
        
    async def initialize(self) -> None:
        """
        Initialize the Neo4j storage backend.
        
        This method handles connection establishment and schema creation.
        """
        if self._initialized:
            return
            
        logger.info(f"Initializing Neo4j graph store with namespace: {self.namespace.namespace}")
        
        try:
            # Initialize client
            if not await self.client.initialize():
                raise RuntimeError("Failed to initialize Neo4j client")
            
            # Initialize schema
            await self._create_constraints()
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing Neo4j graph store: {e}")
            raise
    
    async def _create_constraints(self) -> None:
        """Create necessary constraints in Neo4j."""
        constraints_query = f"""
        CREATE CONSTRAINT IF NOT EXISTS FOR (n:{self._node_label})
        WHERE n.id IS NOT NULL AND n.id IS UNIQUE
        """
        
        try:
            await self.client.execute_query(constraints_query)
            logger.debug("Neo4j constraints created successfully")
        except Exception as e:
            logger.error(f"Error creating Neo4j constraints: {e}")
            raise
    
    async def finalize(self) -> None:
        """
        Finalize and clean up the Neo4j storage backend.
        
        This method handles connection closure and resource cleanup.
        """
        logger.info("Finalizing Neo4j graph store")
        
        if self.client:
            await self.client.close()
            
        self._initialized = False
        logger.info("Neo4j graph store finalized")
    
    async def drop(self) -> Dict[str, str]:
        """
        Drop all data from the Neo4j storage.
        
        Returns:
            Dictionary with status and message
        """
        logger.warning(f"Dropping all data for namespace: {self.namespace.namespace}")
        
        try:
            # Delete all nodes and relationships in the namespace
            delete_query = f"""
            MATCH (n:{self._node_label})
            DETACH DELETE n
            """
            
            await self.client.execute_query(delete_query)
                    
            return {
                "status": "success",
                "message": f"All data for namespace {self.namespace.namespace} has been dropped"
            }
        except Exception as e:
            logger.error(f"Error dropping Neo4j data: {e}")
            return {
                "status": "error",
                "message": f"Failed to drop data: {str(e)}"
            }
    
    async def index_done_callback(self) -> None:
        """
        Callback invoked when indexing operations are complete.
        
        For Neo4j, this is a no-op as indexing is handled automatically.
        """
        pass
    
    async def has_node(self, node_id: str) -> bool:
        """
        Check if a node exists in the graph.
        
        Args:
            node_id: Node ID to check
            
        Returns:
            True if the node exists, False otherwise
        """
        check_query = f"""
        MATCH (n:{self._node_label} {{id: $id}})
        RETURN COUNT(n) > 0 AS exists
        """
        
        try:
            result = await self.client.execute_query(check_query, {"id": node_id})
            return result[0]["exists"] if result else False
        except Exception as e:
            logger.error(f"Error checking if node exists: {e}")
            return False
    
    async def has_edge(self, source_id: str, target_id: str) -> bool:
        """
        Check if an edge exists between nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            
        Returns:
            True if any edge exists, False otherwise
        """
        check_query = f"""
        MATCH (a:{self._node_label} {{id: $source_id}})-[r]->(b:{self._node_label} {{id: $target_id}})
        RETURN COUNT(r) > 0 AS exists
        """
        
        try:
            result = await self.client.execute_query(
                check_query, 
                {"source_id": source_id, "target_id": target_id}
            )
            return result[0]["exists"] if result else False
        except Exception as e:
            logger.error(f"Error checking if edge exists: {e}")
            return False
    
    async def upsert_node(self, node_id: str, node_data: Dict[str, Any]) -> None:
        """
        Insert or update a node in the graph.
        
        Args:
            node_id: Node ID
            node_data: Node data dictionary
        """
        # Make a copy of the data to avoid modifying the original
        data = dict(node_data)
        data["id"] = node_id
        
        await self.client.add_node(
            id=node_id,
            labels=[self._node_label],
            properties=data
        )
    
    async def upsert_edge(self, source_id: str, target_id: str, edge_data: Dict[str, Any]) -> None:
        """
        Insert or update an edge in the graph.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_data: Edge data dictionary
        """
        # Make a copy of the data to avoid modifying the original
        data = dict(edge_data)
        relationship_type = data.pop("type", "RELATED_TO")
        
        # Generate a deterministic edge ID if not provided
        if "id" not in data:
            data["id"] = f"{source_id}__{relationship_type}__{target_id}"
        
        await self.client.add_relationship(
            source_id=source_id,
            target_id=target_id,
            rel_type=relationship_type,
            properties=data
        )
    
    async def delete_node(self, node_id: str) -> None:
        """
        Delete a node from the graph.
        
        Args:
            node_id: ID of the node to delete
        """
        await self.client.delete_node(node_id)
    
    async def delete_edge(self, source_id: str, target_id: str) -> None:
        """
        Delete an edge from the graph.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
        """
        delete_query = f"""
        MATCH (a:{self._node_label} {{id: $source_id}})-[r]->(b:{self._node_label} {{id: $target_id}})
        DELETE r
        """
        
        await self.client.execute_query(
            delete_query, 
            {"source_id": source_id, "target_id": target_id}
        )
    
    async def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.
        
        Args:
            node_id: Node ID to retrieve
            
        Returns:
            Node data dictionary or None if not found
        """
        return await self.client.get_node(node_id, [self._node_label])
    
    async def get_edge(self, source_id: str, target_id: str) -> Optional[Dict[str, Any]]:
        """
        Get edge data between two nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            
        Returns:
            Edge data dictionary or None if not found
        """
        get_query = f"""
        MATCH (a:{self._node_label} {{id: $source_id}})-[r]->(b:{self._node_label} {{id: $target_id}})
        RETURN r
        LIMIT 1
        """
        
        result = await self.client.execute_query(
            get_query, 
            {"source_id": source_id, "target_id": target_id}
        )
        
        return result[0]["r"] if result else None
    
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
        results = []
        
        # Get edges based on direction
        if direction.lower() == "outgoing" or direction.lower() == "both":
            query = f"""
            MATCH (a:{self._node_label} {{id: $node_id}})-[r]->(b:{self._node_label})
            RETURN b.id AS connected_id, r, TYPE(r) AS relationship_type
            """
            
            outgoing_results = await self.client.execute_query(query, {"node_id": node_id})
            for record in outgoing_results:
                results.append((record["connected_id"], record["r"]))
                    
        if direction.lower() == "incoming" or direction.lower() == "both":
            query = f"""
            MATCH (a:{self._node_label})-[r]->(b:{self._node_label} {{id: $node_id}})
            RETURN a.id AS connected_id, r, TYPE(r) AS relationship_type
            """
            
            incoming_results = await self.client.execute_query(query, {"node_id": node_id})
            for record in incoming_results:
                results.append((record["connected_id"], record["r"]))
                        
        return results
    
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
        # Limit max_depth to prevent expensive queries
        if max_depth > 5:
            max_depth = 5
            logger.warning("Limiting max_depth to 5 for path finding")
            
        # Use variable length path with max length
        query = f"""
        MATCH path = (a:{self._node_label} {{id: $source_id}})-[*1..{max_depth}]->(b:{self._node_label} {{id: $target_id}})
        RETURN path
        LIMIT 10
        """
        
        paths = []
        path_results = await self.client.execute_query(
            query, 
            {"source_id": source_id, "target_id": target_id}
        )
        
        # Neo4j returns paths as a complex structure
        # Parse them into alternating node and edge dictionaries
        for record in path_results:
            if "path" in record:
                path = record["path"]
                
                # For now, just return the raw path object
                # In a real implementation, we would parse this into
                # alternating nodes and edges
                paths.append(path)
                        
        return paths
    
    async def execute_query(self, 
                         query: str, 
                         params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a native graph query.
        
        Args:
            query: Query string in the native graph database language (Cypher)
            params: Query parameters
            
        Returns:
            Query results as a list of dictionaries
        """
        return await self.client.execute_query(query, params)