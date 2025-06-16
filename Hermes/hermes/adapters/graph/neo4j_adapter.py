"""
Neo4j Graph Adapter - Graph database adapter using Neo4j.

This module provides a GraphDatabaseAdapter implementation that uses Neo4j
for storing and querying graph data with full Cypher query support.
"""

import os
import json
import time
import uuid
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple

from neo4j import GraphDatabase, AsyncGraphDatabase, basic_auth

from hermes.core.logging import get_logger
from hermes.core.database_manager import GraphDatabaseAdapter, DatabaseBackend

# Logger for this module
logger = get_logger("hermes.adapters.graph.neo4j")


class Neo4jGraphAdapter(GraphDatabaseAdapter):
    """
    Neo4j graph database adapter.
    
    This adapter provides a Neo4j implementation of the GraphDatabaseAdapter
    interface, supporting nodes, relationships, and Cypher queries.
    """
    
    def __init__(self, 
                namespace: str,
                config: Optional[Dict[str, Any]] = None):
        """Initialize the Neo4j graph adapter."""
        super().__init__(namespace, config)
        
        # Neo4j connection settings
        self.uri = self.config.get("uri", "bolt://localhost:7687")
        self.username = self.config.get("username", "neo4j")
        self.password = self.config.get("password", "password")
        
        # Initialize client
        self.client = None
        self._connected = False
        
        # Namespace will be used as a prefix for all node labels
        self.namespace_prefix = f"{namespace}__"
    
    @property
    def backend(self) -> DatabaseBackend:
        """Get the database backend."""
        return DatabaseBackend.NEO4J
    
    async def connect(self) -> bool:
        """Connect to the database."""
        try:
            # Create client with auth
            self.client = AsyncGraphDatabase.driver(
                self.uri,
                auth=basic_auth(self.username, self.password)
            )
            
            # Verify connection
            await self.client.verify_connectivity()
            
            # Initialize namespace if needed
            await self._init_namespace()
            
            self._connected = True
            
            logger.info(f"Connected to Neo4j graph database for namespace {self.namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Neo4j graph database: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from the database."""
        try:
            if self.client:
                await self.client.close()
                self.client = None
            
            self._connected = False
            
            logger.info(f"Disconnected from Neo4j graph database for namespace {self.namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Neo4j graph database: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """Check if connected to the database."""
        if not self._connected or not self.client:
            return False
        
        try:
            # Check connection
            await self.client.verify_connectivity()
            return True
        except:
            self._connected = False
            return False
    
    async def add_node(self,
                      id: str,
                      labels: List[str],
                      properties: Optional[Dict[str, Any]] = None) -> bool:
        """Add a node to the graph."""
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        try:
            # Add namespace prefix to labels
            prefixed_labels = [f"{self.namespace_prefix}{label}" for label in labels]
            
            # Create properties dict with ID
            node_props = properties.copy() if properties else {}
            node_props["id"] = id
            node_props["namespace"] = self.namespace
            
            # Format labels for Cypher
            labels_str = ":".join(prefixed_labels)
            
            # Create Cypher query
            query = f"""
            MERGE (n:{labels_str} {{id: $id, namespace: $namespace}})
            SET n = $properties
            RETURN n
            """
            
            # Execute query
            async with self.client.session() as session:
                result = await session.run(
                    query,
                    id=id,
                    namespace=self.namespace,
                    properties=node_props
                )
                
                # Consume result
                summary = await result.consume()
                
                if summary.counters.nodes_created > 0 or summary.counters.properties_set > 0:
                    logger.debug(f"Added node with ID {id} and labels {labels}")
                    return True
                else:
                    logger.warning(f"Node with ID {id} already exists")
                    return True  # Still considered successful
            
        except Exception as e:
            logger.error(f"Error adding node: {e}")
            return False
    
    async def add_relationship(self,
                             source_id: str,
                             target_id: str,
                             type: str,
                             properties: Optional[Dict[str, Any]] = None) -> bool:
        """Add a relationship between nodes."""
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        try:
            # Add namespace prefix to relationship type
            prefixed_type = f"{self.namespace_prefix}{type}"
            
            # Create properties dict
            rel_props = properties.copy() if properties else {}
            rel_props["namespace"] = self.namespace
            
            # Create Cypher query
            query = f"""
            MATCH (source {{id: $source_id, namespace: $namespace}})
            MATCH (target {{id: $target_id, namespace: $namespace}})
            MERGE (source)-[r:{prefixed_type}]->(target)
            SET r = $properties
            RETURN r
            """
            
            # Execute query
            async with self.client.session() as session:
                result = await session.run(
                    query,
                    source_id=source_id,
                    target_id=target_id,
                    namespace=self.namespace,
                    properties=rel_props
                )
                
                # Consume result
                summary = await result.consume()
                
                if summary.counters.relationships_created > 0 or summary.counters.properties_set > 0:
                    logger.debug(f"Added relationship of type {type} from {source_id} to {target_id}")
                    return True
                else:
                    logger.warning(f"Relationship not created, nodes may not exist")
                    return False
            
        except Exception as e:
            logger.error(f"Error adding relationship: {e}")
            return False
    
    async def get_node(self, id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID."""
        if not self._connected:
            logger.error("Not connected to database")
            return None
        
        try:
            # Create Cypher query
            query = """
            MATCH (n {id: $id, namespace: $namespace})
            RETURN n, labels(n) AS labels
            """
            
            # Execute query
            async with self.client.session() as session:
                result = await session.run(
                    query,
                    id=id,
                    namespace=self.namespace
                )
                
                # Get result
                record = await result.single()
                
                if not record:
                    logger.debug(f"Node with ID {id} not found")
                    return None
                
                # Extract node and labels
                node = record["n"]
                labels = record["labels"]
                
                # Remove namespace prefix from labels
                clean_labels = [label[len(self.namespace_prefix):] for label in labels 
                               if label.startswith(self.namespace_prefix)]
                
                # Convert node to dict
                node_dict = dict(node.items())
                
                # Remove internal properties
                if "namespace" in node_dict:
                    del node_dict["namespace"]
                
                return {
                    "id": id,
                    "labels": clean_labels,
                    "properties": node_dict
                }
            
        except Exception as e:
            logger.error(f"Error getting node: {e}")
            return None
    
    async def get_relationships(self,
                              node_id: str,
                              types: Optional[List[str]] = None,
                              direction: str = "both") -> List[Dict[str, Any]]:
        """Get relationships for a node."""
        if not self._connected:
            logger.error("Not connected to database")
            return []
        
        try:
            # Add namespace prefix to relationship types
            rel_filter = ""
            if types:
                prefixed_types = [f"{self.namespace_prefix}{t}" for t in types]
                rel_filter = "|".join(f":{t}" for t in prefixed_types)
            
            # Create Cypher query based on direction
            if direction == "outgoing":
                query = f"""
                MATCH (n {{id: $id, namespace: $namespace}})-[r{rel_filter}]->(target)
                RETURN r, type(r) AS type, target.id AS target_id
                """
            elif direction == "incoming":
                query = f"""
                MATCH (source)-[r{rel_filter}]->(n {{id: $id, namespace: $namespace}})
                RETURN r, type(r) AS type, source.id AS source_id
                """
            else:  # both
                query = f"""
                MATCH (n {{id: $id, namespace: $namespace}})-[r{rel_filter}]-(other)
                RETURN r, type(r) AS type, 
                       CASE WHEN startNode(r) = n THEN other.id ELSE null END AS target_id,
                       CASE WHEN endNode(r) = n THEN other.id ELSE null END AS source_id
                """
            
            # Execute query
            async with self.client.session() as session:
                result = await session.run(
                    query,
                    id=node_id,
                    namespace=self.namespace
                )
                
                # Process results
                relationships = []
                
                async for record in result:
                    rel = record["r"]
                    rel_type = record["type"]
                    
                    # Remove namespace prefix from type
                    clean_type = rel_type
                    if rel_type.startswith(self.namespace_prefix):
                        clean_type = rel_type[len(self.namespace_prefix):]
                    
                    # Convert relationship to dict
                    rel_dict = dict(rel.items())
                    
                    # Remove internal properties
                    if "namespace" in rel_dict:
                        del rel_dict["namespace"]
                    
                    # Create relationship dict
                    relationship = {
                        "type": clean_type,
                        "properties": rel_dict,
                    }
                    
                    # Add source/target IDs based on direction
                    if direction == "outgoing":
                        relationship["source_id"] = node_id
                        relationship["target_id"] = record["target_id"]
                    elif direction == "incoming":
                        relationship["source_id"] = record["source_id"]
                        relationship["target_id"] = node_id
                    else:  # both
                        if record["target_id"]:
                            relationship["source_id"] = node_id
                            relationship["target_id"] = record["target_id"]
                        else:
                            relationship["source_id"] = record["source_id"]
                            relationship["target_id"] = node_id
                    
                    relationships.append(relationship)
                
                logger.debug(f"Found {len(relationships)} relationships for node {node_id}")
                return relationships
            
        except Exception as e:
            logger.error(f"Error getting relationships: {e}")
            return []
    
    async def query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a graph query in Cypher."""
        if not self._connected:
            logger.error("Not connected to database")
            return []
        
        try:
            # Add namespace parameter
            params = params or {}
            if "namespace" not in params:
                params["namespace"] = self.namespace
            
            # Execute query
            async with self.client.session() as session:
                result = await session.run(query, **params)
                
                # Process results
                records = []
                
                async for record in result:
                    # Convert record to dict
                    record_dict = {}
                    
                    for key, value in record.items():
                        # Handle Neo4j types
                        if hasattr(value, "items"):  # Node or Relationship
                            record_dict[key] = dict(value.items())
                        elif isinstance(value, list) and all(hasattr(item, "items") for item in value):
                            # List of nodes or relationships
                            record_dict[key] = [dict(item.items()) for item in value]
                        else:
                            record_dict[key] = value
                    
                    records.append(record_dict)
                
                logger.debug(f"Query returned {len(records)} records")
                return records
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    async def delete_node(self, id: str) -> bool:
        """Delete a node."""
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        try:
            # Create Cypher query to delete node and all its relationships
            query = """
            MATCH (n {id: $id, namespace: $namespace})
            DETACH DELETE n
            """
            
            # Execute query
            async with self.client.session() as session:
                result = await session.run(
                    query,
                    id=id,
                    namespace=self.namespace
                )
                
                # Consume result
                summary = await result.consume()
                
                if summary.counters.nodes_deleted > 0:
                    logger.debug(f"Deleted node with ID {id}")
                    return True
                else:
                    logger.warning(f"Node with ID {id} not found")
                    return False
            
        except Exception as e:
            logger.error(f"Error deleting node: {e}")
            return False
    
    async def delete_relationship(self, 
                                source_id: str, 
                                target_id: str,
                                type: Optional[str] = None) -> bool:
        """Delete a relationship."""
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        try:
            # Add namespace prefix to relationship type
            rel_type = ""
            if type:
                prefixed_type = f"{self.namespace_prefix}{type}"
                rel_type = f":{prefixed_type}"
            
            # Create Cypher query
            query = f"""
            MATCH (source {{id: $source_id, namespace: $namespace}})-[r{rel_type}]->(target {{id: $target_id, namespace: $namespace}})
            DELETE r
            """
            
            # Execute query
            async with self.client.session() as session:
                result = await session.run(
                    query,
                    source_id=source_id,
                    target_id=target_id,
                    namespace=self.namespace
                )
                
                # Consume result
                summary = await result.consume()
                
                if summary.counters.relationships_deleted > 0:
                    logger.debug(f"Deleted relationship from {source_id} to {target_id}")
                    return True
                else:
                    logger.warning(f"Relationship not found")
                    return False
            
        except Exception as e:
            logger.error(f"Error deleting relationship: {e}")
            return False
    
    async def _init_namespace(self) -> None:
        """Initialize namespace constraints."""
        try:
            # Create constraint to ensure node IDs are unique within namespace
            query = """
            CREATE CONSTRAINT IF NOT EXISTS FOR (n)
            WHERE n.namespace = $namespace
            REQUIRE n.id IS UNIQUE
            """
            
            # Execute query
            async with self.client.session() as session:
                await session.run(query, namespace=self.namespace)
                
                logger.debug(f"Initialized namespace {self.namespace}")
        except Exception as e:
            logger.error(f"Error initializing namespace: {e}")
            # Continue even if constraint creation fails