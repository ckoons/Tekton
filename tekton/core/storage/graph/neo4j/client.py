"""
Neo4j client management for graph store.
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple, Union, List

try:
    from neo4j import AsyncGraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    from hermes.core.database_manager import DatabaseBackend
    from hermes.utils.database_helper import DatabaseClient
    HERMES_AVAILABLE = True
except ImportError:
    HERMES_AVAILABLE = False

from tekton.core.storage.graph.neo4j.utils import parse_cypher_result

# Configure logger
logger = logging.getLogger(__name__)

class Neo4jClient:
    """
    Manages Neo4j connections and queries.
    Supports both direct connections and Hermes-managed connections.
    """
    
    def __init__(
        self,
        use_hermes: bool = False,
        hermes_service_name: str = "neo4j",
        namespace: str = "default",
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: str = "neo4j",
        max_connection_lifetime: int = 3600,
        max_connection_pool_size: int = 50
    ):
        """
        Initialize Neo4j client.
        
        Args:
            use_hermes: Whether to use Hermes for database connection
            hermes_service_name: Hermes service name for the database
            namespace: Namespace for the database
            uri: Neo4j connection URI (e.g., neo4j://localhost:7687)
            username: Neo4j username
            password: Neo4j password
            database: Neo4j database name
            max_connection_lifetime: Maximum connection lifetime in seconds
            max_connection_pool_size: Maximum connection pool size
        """
        self.use_hermes = use_hermes and HERMES_AVAILABLE
        self.hermes_service_name = hermes_service_name
        self.namespace = namespace
        
        # Connection parameters
        self.uri = uri or os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
        self.username = username or os.environ.get("NEO4J_USERNAME", "neo4j")
        self.password = password or os.environ.get("NEO4J_PASSWORD", "password")
        self.database = database
        self.max_connection_lifetime = max_connection_lifetime
        self.max_connection_pool_size = max_connection_pool_size
        
        # State
        self._driver = None
        self._hermes_client = None
        self._graph_db = None
        self._initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize the Neo4j client.
        
        Returns:
            True if successful
        """
        if self._initialized:
            return True
            
        try:
            if self.use_hermes:
                # Create Hermes client
                self._hermes_client = DatabaseClient(
                    service_name=self.hermes_service_name,
                    namespace=self.namespace
                )
                
                # Get graph database from Hermes
                self._graph_db = await self._hermes_client.get_graph_db()
                
                if not self._graph_db:
                    logger.error("Failed to get graph database from Hermes")
                    self.use_hermes = False
                else:
                    logger.info("Using Neo4j via Hermes database services")
                    self._initialized = True
                    return True
            
            # Direct connection if not using Hermes or Hermes unavailable
            if not self.use_hermes:
                if not NEO4J_AVAILABLE:
                    logger.error("Neo4j driver not available")
                    return False
                    
                self._driver = AsyncGraphDatabase.driver(
                    self.uri,
                    auth=(self.username, self.password),
                    max_connection_lifetime=self.max_connection_lifetime,
                    max_connection_pool_size=self.max_connection_pool_size
                )
                
                # Test connection
                if await self._test_connection():
                    logger.info(f"Connected to Neo4j at {self.uri}")
                    self._initialized = True
                    return True
                    
            return False
                
        except Exception as e:
            logger.error(f"Error initializing Neo4j client: {e}")
            if self._driver:
                await self._driver.close()
                self._driver = None
            return False
    
    async def _test_connection(self) -> bool:
        """
        Test Neo4j connection.
        
        Returns:
            True if successful
        """
        if not self._driver:
            return False
            
        try:
            async with self._driver.session(database=self.database) as session:
                result = await session.run("RETURN 1 AS test")
                record = await result.single()
                return record and record.get("test") == 1
        except Exception as e:
            logger.error(f"Neo4j connection test failed: {e}")
            return False
    
    async def close(self) -> None:
        """Close Neo4j connection."""
        if self._driver:
            await self._driver.close()
            self._driver = None
            
        self._initialized = False
        logger.info("Neo4j client closed")
    
    async def execute_query(
        self, 
        query: str, 
        params: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query.
        
        Args:
            query: Cypher query
            params: Query parameters
            
        Returns:
            List of result records
        """
        if not self._initialized:
            raise RuntimeError("Neo4j client not initialized")
            
        if params is None:
            params = {}
            
        try:
            if self.use_hermes and self._graph_db:
                # Execute through Hermes
                result = await self._graph_db.query(query, params)
                return [parse_cypher_result(record) for record in result]
            else:
                # Execute directly
                results = []
                async with self._driver.session(database=self.database) as session:
                    result = await session.run(query, params)
                    async for record in result:
                        results.append(parse_cypher_result(dict(record)))
                return results
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    async def add_node(
        self, 
        id: str, 
        labels: List[str], 
        properties: Dict[str, Any]
    ) -> bool:
        """
        Add a node to the graph.
        
        Args:
            id: Node ID
            labels: Node labels
            properties: Node properties
            
        Returns:
            True if successful
        """
        if not self._initialized:
            raise RuntimeError("Neo4j client not initialized")
            
        # Ensure ID is in properties
        properties = dict(properties)
        properties["id"] = id
        
        # Create label string
        label_str = ":".join(labels)
        
        query = f"""
        MERGE (n:{label_str} {{id: $id}})
        SET n = $properties
        RETURN n
        """
        
        try:
            result = await self.execute_query(query, {
                "id": id,
                "properties": properties
            })
            return len(result) > 0
        except Exception as e:
            logger.error(f"Error adding node: {e}")
            return False
    
    async def get_node(self, id: str, labels: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.
        
        Args:
            id: Node ID
            labels: Optional node labels to filter by
            
        Returns:
            Node properties or None if not found
        """
        if not self._initialized:
            raise RuntimeError("Neo4j client not initialized")
            
        label_str = ":".join(labels) if labels else ""
        
        query = f"""
        MATCH (n{f':{label_str}' if label_str else ''} {{id: $id}})
        RETURN n
        """
        
        try:
            result = await self.execute_query(query, {"id": id})
            return result[0]["n"] if result else None
        except Exception as e:
            logger.error(f"Error getting node: {e}")
            return None
    
    async def delete_node(self, id: str) -> bool:
        """
        Delete a node by ID.
        
        Args:
            id: Node ID
            
        Returns:
            True if successful
        """
        if not self._initialized:
            raise RuntimeError("Neo4j client not initialized")
            
        query = """
        MATCH (n {id: $id})
        DETACH DELETE n
        """
        
        try:
            await self.execute_query(query, {"id": id})
            return True
        except Exception as e:
            logger.error(f"Error deleting node: {e}")
            return False
    
    async def add_relationship(
        self, 
        source_id: str, 
        target_id: str, 
        rel_type: str, 
        properties: Dict[str, Any]
    ) -> bool:
        """
        Add a relationship between nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            rel_type: Relationship type
            properties: Relationship properties
            
        Returns:
            True if successful
        """
        if not self._initialized:
            raise RuntimeError("Neo4j client not initialized")
            
        query = f"""
        MATCH (a {{id: $source_id}})
        MATCH (b {{id: $target_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r = $properties
        RETURN r
        """
        
        try:
            result = await self.execute_query(query, {
                "source_id": source_id,
                "target_id": target_id,
                "properties": properties
            })
            return len(result) > 0
        except Exception as e:
            logger.error(f"Error adding relationship: {e}")
            return False