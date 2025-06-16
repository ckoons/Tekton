"""
Athena Knowledge Engine

Core knowledge graph engine and management capabilities.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from pathlib import Path

# Import FastMCP integration if available
try:
    from tekton.mcp.fastmcp import (
        mcp_tool,
        mcp_capability,
        MCPClient
    )
    fastmcp_available = True
except ImportError:
    fastmcp_available = False

from .entity import Entity
from .relationship import Relationship

try:
    # Attempt to import Neo4j adapter if available
    from .graph.neo4j_adapter import Neo4jAdapter as GraphAdapter
    USING_NEO4J = True
except ImportError:
    try:
        # Attempt to use Hermes database services
        from hermes.utils.database_helper import DatabaseClient
        # If import succeeds, we'll still set up Neo4jAdapter later
        USING_NEO4J = True
    except ImportError:
        # Fall back to in-memory adapter if neither Neo4j nor Hermes is available
        from .graph.memory_adapter import MemoryAdapter as GraphAdapter
        USING_NEO4J = False

logger = logging.getLogger("athena.engine")

class KnowledgeEngine:
    """
    Core knowledge graph engine for Athena.
    
    Manages entity and relationship creation, querying, and inference.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the knowledge engine.
        
        Args:
            data_path: Path to store graph data (if using file-based adapter)
        """
        if data_path:
            self.data_path = data_path
        else:
            # Use $TEKTON_DATA_DIR/athena by default
            self.data_path = os.path.join(
                os.environ.get('TEKTON_DATA_DIR', 
                              os.path.join(os.environ.get('TEKTON_ROOT', os.path.expanduser('~')), '.tekton', 'data')),
                'athena'
            )
        self.is_initialized = False
        self.adapter = None
        self.entity_manager = None
        self.query_engine = None
        
    async def initialize(self) -> bool:
        """
        Initialize the knowledge engine and database connection.
        
        Returns:
            True if successful
        """
        logger.info("Initializing Athena Knowledge Engine...")
        
        # Ensure data directory exists
        os.makedirs(self.data_path, exist_ok=True)
        
        # Initialize the graph adapter
        adapter_config = {
            "data_path": self.data_path,
            "component_id": "athena.knowledge",
            "namespace": "athena_knowledge"
        }
        
        if USING_NEO4J:
            # Import within function to handle both direct import and Hermes integration
            try:
                from .graph.neo4j_adapter import Neo4jAdapter as GraphAdapter
                logger.info("Using Neo4j graph database adapter")
            except ImportError:
                # Fall back to in-memory adapter if Neo4j adapter isn't available yet but Hermes is
                from .graph.memory_adapter import MemoryAdapter as GraphAdapter
                logger.info("Neo4j adapter not found, using in-memory adapter for now")
        else:
            from .graph.memory_adapter import MemoryAdapter as GraphAdapter
            logger.info("Using in-memory graph adapter with file persistence")
            
        try:
            self.adapter = GraphAdapter(**adapter_config)
            await self.adapter.connect()
            
            # Initialize schema if needed
            await self.adapter.initialize_schema()
            
            self.is_initialized = True
            logger.info("Athena Knowledge Engine initialized successfully")
            
            # Initialize MCP integration if available
            if fastmcp_available:
                try:
                    # Initialize entity manager and query engine for MCP integration
                    # We import them here to avoid circular imports
                    from .entity_manager import EntityManager
                    from .query_engine import QueryEngine
                    
                    # Create instances if they don't exist
                    if not self.entity_manager:
                        self.entity_manager = EntityManager(self)
                    if not self.query_engine:
                        self.query_engine = QueryEngine(self)
                    
                    # Initialize MCP integration
                    await self.entity_manager.initialize_mcp()
                    await self.query_engine.initialize_mcp()
                    
                    logger.info("Initialized FastMCP integration successfully")
                except Exception as e:
                    logger.error(f"Error initializing MCP integration: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize knowledge engine: {e}")
            return False
            
    async def shutdown(self) -> bool:
        """
        Shut down the knowledge engine and close connections.
        
        Returns:
            True if successful
        """
        logger.info("Shutting down Athena Knowledge Engine...")
        
        if self.adapter:
            try:
                await self.adapter.disconnect()
                logger.info("Athena Knowledge Engine shut down successfully")
                return True
            except Exception as e:
                logger.error(f"Error shutting down knowledge engine: {e}")
                return False
        return True
        
    async def add_entity(self, entity: Entity) -> str:
        """
        Add a new entity to the knowledge graph.
        
        Args:
            entity: Entity object to add
            
        Returns:
            Entity ID
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            entity_id = await self.adapter.create_entity(entity)
            logger.info(f"Added entity: {entity.name} (ID: {entity_id})")
            return entity_id
        except Exception as e:
            logger.error(f"Error adding entity: {e}")
            raise
            
    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Retrieve an entity by ID.
        
        Args:
            entity_id: Entity ID to retrieve
            
        Returns:
            Entity object or None if not found
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            entity = await self.adapter.get_entity(entity_id)
            return entity
        except Exception as e:
            logger.error(f"Error retrieving entity {entity_id}: {e}")
            return None
            
    async def update_entity(self, entity: Entity) -> bool:
        """
        Update an existing entity.
        
        Args:
            entity: Updated entity object
            
        Returns:
            True if successful
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            success = await self.adapter.update_entity(entity)
            if success:
                logger.info(f"Updated entity: {entity.name} (ID: {entity.entity_id})")
            return success
        except Exception as e:
            logger.error(f"Error updating entity {entity.entity_id}: {e}")
            return False
            
    async def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: Entity ID to delete
            
        Returns:
            True if successful
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            success = await self.adapter.delete_entity(entity_id)
            if success:
                logger.info(f"Deleted entity with ID: {entity_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting entity {entity_id}: {e}")
            return False
            
    async def add_relationship(self, relationship: Relationship) -> str:
        """
        Add a new relationship to the knowledge graph.
        
        Args:
            relationship: Relationship object to add
            
        Returns:
            Relationship ID
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            relationship_id = await self.adapter.create_relationship(relationship)
            logger.info(f"Added relationship: {relationship.relationship_type} (ID: {relationship_id})")
            return relationship_id
        except Exception as e:
            logger.error(f"Error adding relationship: {e}")
            raise
            
    async def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """
        Retrieve a relationship by ID.
        
        Args:
            relationship_id: Relationship ID to retrieve
            
        Returns:
            Relationship object or None if not found
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            relationship = await self.adapter.get_relationship(relationship_id)
            return relationship
        except Exception as e:
            logger.error(f"Error retrieving relationship {relationship_id}: {e}")
            return None
            
    async def update_relationship(self, relationship: Relationship) -> bool:
        """
        Update an existing relationship.
        
        Args:
            relationship: Updated relationship object
            
        Returns:
            True if successful
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            success = await self.adapter.update_relationship(relationship)
            if success:
                logger.info(f"Updated relationship: {relationship.relationship_type} (ID: {relationship.relationship_id})")
            return success
        except Exception as e:
            logger.error(f"Error updating relationship {relationship.relationship_id}: {e}")
            return False
            
    async def delete_relationship(self, relationship_id: str) -> bool:
        """
        Delete a relationship by ID.
        
        Args:
            relationship_id: Relationship ID to delete
            
        Returns:
            True if successful
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            success = await self.adapter.delete_relationship(relationship_id)
            if success:
                logger.info(f"Deleted relationship with ID: {relationship_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting relationship {relationship_id}: {e}")
            return False
            
    async def search_entities(self, query: str, entity_type: Optional[str] = None, limit: int = 10) -> List[Entity]:
        """
        Search for entities matching a query.
        
        Args:
            query: Search query
            entity_type: Optional entity type to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of matching entities
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            entities = await self.adapter.search_entities(query, entity_type, limit)
            return entities
        except Exception as e:
            logger.error(f"Error searching entities: {e}")
            return []
            
    async def get_entity_relationships(self, 
                                    entity_id: str, 
                                    relationship_type: Optional[str] = None,
                                    direction: str = "both") -> List[Tuple[Relationship, Entity]]:
        """
        Get all relationships for an entity.
        
        Args:
            entity_id: Entity ID to query
            relationship_type: Optional relationship type to filter by
            direction: Direction of relationships ('outgoing', 'incoming', or 'both')
            
        Returns:
            List of (relationship, connected entity) tuples
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            relationships = await self.adapter.get_entity_relationships(entity_id, relationship_type, direction)
            return relationships
        except Exception as e:
            logger.error(f"Error getting entity relationships for {entity_id}: {e}")
            return []
            
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a raw graph query.
        
        Args:
            query: Query string in the graph database language (e.g., Cypher for Neo4j)
            params: Query parameters
            
        Returns:
            Query results
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            results = await self.adapter.execute_query(query, params or {})
            return results
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
            
    async def find_path(self, 
                      source_id: str, 
                      target_id: str, 
                      max_depth: int = 3) -> List[List[Union[Entity, Relationship]]]:
        """
        Find paths between two entities.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            max_depth: Maximum path length
            
        Returns:
            List of paths, where each path is a list of alternating Entity and Relationship objects
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            paths = await self.adapter.find_paths(source_id, target_id, max_depth)
            return paths
        except Exception as e:
            logger.error(f"Error finding paths: {e}")
            return []
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the knowledge engine.
        
        Returns:
            Status information dictionary
        """
        if not self.is_initialized:
            return {
                "status": "not_initialized",
                "adapter_type": "none"
            }
            
        try:
            adapter_type = "neo4j" if USING_NEO4J else "memory"
            entity_count = await self.adapter.count_entities()
            relationship_count = await self.adapter.count_relationships()
            
            return {
                "status": "initialized",
                "adapter_type": adapter_type,
                "entity_count": entity_count,
                "relationship_count": relationship_count,
                "data_path": self.data_path
            }
        except Exception as e:
            logger.error(f"Error getting engine status: {e}")
            return {
                "status": "error",
                "adapter_type": "neo4j" if USING_NEO4J else "memory",
                "error": str(e)
            }

# Global singleton instance
_engine = KnowledgeEngine()

async def get_knowledge_engine() -> KnowledgeEngine:
    """
    Get the global knowledge engine instance.
    
    Returns:
        KnowledgeEngine instance
    """
    if not _engine.is_initialized:
        await _engine.initialize()
    return _engine