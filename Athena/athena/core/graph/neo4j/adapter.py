"""
Neo4j Graph Adapter for Athena Knowledge Graph

Provides integration with Neo4j graph database through Hermes database services.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from pathlib import Path

from py2neo import Graph
from neo4j import AsyncGraphDatabase

try:
    from hermes.core.database_manager import DatabaseBackend
    from hermes.utils.database_helper import DatabaseClient
    HERMES_AVAILABLE = True
except ImportError:
    HERMES_AVAILABLE = False

from ...entity import Entity
from ...relationship import Relationship
from .config import Neo4jConfig
from .operations import create_entity, get_entity, update_entity, delete_entity
from .operations import create_relationship, get_relationship, update_relationship, delete_relationship
from .operations import search_entities, get_entity_relationships, execute_query, find_paths
from .operations import count_entities, count_relationships

logger = logging.getLogger("athena.graph.neo4j.adapter")

class Neo4jAdapter:
    """
    Neo4j graph database adapter for Athena.
    
    Provides integration with Neo4j through the Hermes database services.
    Implements the same interface as the memory adapter for consistency.
    """
    
    def __init__(self, data_path: str, **kwargs):
        """
        Initialize the Neo4j adapter.
        
        Args:
            data_path: Path for configuration (not used with Neo4j, but kept for interface compatibility)
            **kwargs: Additional configuration options including Hermes integration settings
        """
        self.data_path = data_path
        
        # Load configuration
        if "config" in kwargs:
            self.config = kwargs["config"]
        else:
            config_dict = {k: v for k, v in kwargs.items() if k not in ["data_path"]}
            self.config = Neo4jConfig.from_dict(config_dict)
            
        self.is_connected = False
        self.client = None
        self.graph_db = None
        
        # Create Hermes database client if Hermes is available and enabled
        if HERMES_AVAILABLE and self.config.use_hermes:
            self.db_client = DatabaseClient(**self.config.get_hermes_config())
            logger.info("Using Hermes database services for Neo4j integration")
        else:
            self.db_client = None
            logger.info("Using direct Neo4j connection (Hermes not available or disabled)")
        
    async def connect(self) -> bool:
        """
        Connect to the Neo4j graph database.
        
        Returns:
            True if successful
        """
        logger.info("Connecting to Neo4j graph database")
        
        try:
            if self.db_client:
                # Get graph database from Hermes
                self.graph_db = await self.db_client.get_graph_db(namespace=self.config.namespace)
                
                if not self.graph_db:
                    logger.error("Failed to get graph database from Hermes")
                    return False
            else:
                # Direct connection to Neo4j
                conn_config = self.config.get_connection_config()
                self.client = AsyncGraphDatabase.driver(
                    conn_config["uri"],
                    auth=(conn_config["username"], conn_config["password"])
                )
                
                # Create a wrapper that mimics the Hermes interface
                self.graph_db = self._create_graph_db_wrapper()
            
            # Initialize schema
            await self.initialize_schema()
            
            self.is_connected = True
            logger.info("Connected to Neo4j graph database")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Neo4j graph database: {e}")
            self.is_connected = False
            return False
    
    def _create_graph_db_wrapper(self):
        """Create a wrapper for direct Neo4j connection that mimics the Hermes interface."""
        client = self.client
        
        class GraphDBWrapper:
            async def add_node(self, id, labels, properties):
                return await create_entity(client, id, labels, properties)
                
            async def get_node(self, id):
                return await get_entity(client, id)
                
            async def delete_node(self, id):
                return await delete_entity(client, id)
                
            async def add_relationship(self, source_id, target_id, type, properties):
                return await create_relationship(client, source_id, target_id, type, properties)
                
            async def query(self, query, params=None):
                return await execute_query(client, query, params or {})
        
        return GraphDBWrapper()
        
    async def disconnect(self) -> bool:
        """
        Disconnect from the Neo4j graph database.
        
        Returns:
            True if successful
        """
        logger.info("Disconnecting from Neo4j graph database")
        
        try:
            # The Hermes client handles disconnection for managed connections
            if self.client:
                await self.client.close()
                
            self.client = None
            self.graph_db = None
            self.is_connected = False
            
            logger.info("Disconnected from Neo4j graph database")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Neo4j graph database: {e}")
            return False
        
    async def initialize_schema(self) -> bool:
        """
        Initialize the graph schema with constraints.
        
        Returns:
            True if successful
        """
        try:
            # Create constraint for entity IDs
            await self.graph_db.query("""
            CREATE CONSTRAINT IF NOT EXISTS FOR (n:Entity)
            WHERE n.entity_id IS UNIQUE
            """)
            
            # Create constraint for relationship IDs
            await self.graph_db.query("""
            CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r]-()
            WHERE r.relationship_id IS UNIQUE
            """)
            
            logger.info("Initialized Neo4j schema")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Neo4j schema: {e}")
            return False
    
    # Methods delegate to operations module but provide the adapter interface
    async def create_entity(self, entity: Entity) -> str:
        """Create a new entity in Neo4j."""
        if not self.is_connected:
            logger.error("Not connected to database")
            raise ConnectionError("Not connected to database")
            
        # Convert entity to Neo4j properties and add
        properties = entity.to_dict()
        labels = ["Entity", entity.entity_type]
            
        await self.graph_db.add_node(
            id=entity.entity_id,
            labels=labels,
            properties=properties
        )
            
        logger.debug(f"Created entity: {entity.name} ({entity.entity_id})")
        return entity.entity_id
        
    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID."""
        return await get_entity(self.graph_db, entity_id, Entity)
        
    async def update_entity(self, entity: Entity) -> bool:
        """Update an existing entity."""
        return await update_entity(self.graph_db, entity)
        
    async def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity by ID."""
        return await delete_entity(self.graph_db, entity_id)
        
    async def create_relationship(self, relationship: Relationship) -> str:
        """Create a new relationship."""
        return await create_relationship(
            self.graph_db, 
            relationship.source_id,
            relationship.target_id,
            relationship.relationship_type,
            relationship.to_dict()
        )
        
    async def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """Get a relationship by ID."""
        return await get_relationship(self.graph_db, relationship_id, Relationship)
        
    async def update_relationship(self, relationship: Relationship) -> bool:
        """Update an existing relationship."""
        return await update_relationship(self.graph_db, relationship)
        
    async def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship by ID."""
        return await delete_relationship(self.graph_db, relationship_id)
        
    async def search_entities(self, query: str, entity_type: Optional[str] = None, limit: int = 10) -> List[Entity]:
        """Search for entities matching a query."""
        return await search_entities(self.graph_db, query, entity_type, limit, Entity)
        
    async def get_entity_relationships(self, entity_id: str, relationship_type: Optional[str] = None, direction: str = "both") -> List[Tuple[Relationship, Entity]]:
        """Get relationships for an entity."""
        return await get_entity_relationships(self.graph_db, entity_id, relationship_type, direction, Relationship, Entity)
        
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a raw Cypher query."""
        return await execute_query(self.graph_db, query, params or {})
        
    async def find_paths(self, source_id: str, target_id: str, max_depth: int = 3) -> List[List[Union[Entity, Relationship]]]:
        """Find paths between two entities."""
        return await find_paths(self.graph_db, source_id, target_id, max_depth, Entity, Relationship)
        
    async def count_entities(self) -> int:
        """Count the number of entities in the graph."""
        return await count_entities(self.graph_db)
        
    async def count_relationships(self) -> int:
        """Count the number of relationships in the graph."""
        return await count_relationships(self.graph_db)