"""
In-Memory Graph Adapter for Athena

Provides the main adapter class with common operations.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import networkx as nx

from ...entity import Entity
from ...relationship import Relationship
from .persistence import load_data, save_data
from .entity_ops import (
    create_entity, 
    get_entity, 
    update_entity, 
    delete_entity
)
from .relationship_ops import (
    create_relationship, 
    get_relationship, 
    update_relationship, 
    delete_relationship
)
from .query_ops import (
    search_entities, 
    get_entity_relationships, 
    execute_query
)
from .path_ops import find_paths

logger = logging.getLogger("athena.graph.memory.adapter")

class MemoryAdapter:
    """
    In-memory graph database adapter using NetworkX.
    
    Provides a simple implementation of the graph database interface
    with optional file persistence for testing and development.
    """
    
    def __init__(self, data_path: str, **kwargs):
        """
        Initialize the memory adapter.
        
        Args:
            data_path: Path to store persistence files
            **kwargs: Additional configuration options
        """
        self.data_path = data_path
        self.entity_file = os.path.join(data_path, "entities.json")
        self.relationship_file = os.path.join(data_path, "relationships.json")
        self.graph = nx.MultiDiGraph()
        self.is_connected = False
        
    async def connect(self) -> bool:
        """
        Connect to the graph database.
        
        Returns:
            True if successful
        """
        logger.info("Connecting to in-memory graph database")
        
        # Ensure data directory exists
        os.makedirs(self.data_path, exist_ok=True)
        
        # Load data from files if they exist
        await load_data(self)
        
        self.is_connected = True
        logger.info("Connected to in-memory graph database")
        return True
        
    async def disconnect(self) -> bool:
        """
        Disconnect from the graph database.
        
        Returns:
            True if successful
        """
        logger.info("Disconnecting from in-memory graph database")
        
        # Save data to files
        await save_data(self)
        
        self.is_connected = False
        logger.info("Disconnected from in-memory graph database")
        return True
        
    async def initialize_schema(self) -> bool:
        """
        Initialize the graph schema.
        
        Returns:
            True if successful
        """
        # No schema initialization needed for in-memory graph
        return True

    # Entity operations
    async def create_entity(self, entity: Entity) -> str:
        return await create_entity(self, entity)
        
    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        return await get_entity(self, entity_id)
        
    async def update_entity(self, entity: Entity) -> bool:
        return await update_entity(self, entity)
        
    async def delete_entity(self, entity_id: str) -> bool:
        return await delete_entity(self, entity_id)
        
    # Relationship operations
    async def create_relationship(self, relationship: Relationship) -> str:
        return await create_relationship(self, relationship)
        
    async def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        return await get_relationship(self, relationship_id)
        
    async def update_relationship(self, relationship: Relationship) -> bool:
        return await update_relationship(self, relationship)
        
    async def delete_relationship(self, relationship_id: str) -> bool:
        return await delete_relationship(self, relationship_id)
        
    # Query operations
    async def search_entities(self, query: str, entity_type: Optional[str] = None, limit: int = 10) -> List[Entity]:
        return await search_entities(self, query, entity_type, limit)
        
    async def get_entity_relationships(self, entity_id: str, relationship_type: Optional[str] = None, direction: str = "both"):
        return await get_entity_relationships(self, entity_id, relationship_type, direction)
        
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return await execute_query(query, params)
        
    # Path operations
    async def find_paths(self, source_id: str, target_id: str, max_depth: int = 3):
        return await find_paths(self, source_id, target_id, max_depth)
        
    # Count operations
    async def count_entities(self) -> int:
        return len(self.graph.nodes)
        
    async def count_relationships(self) -> int:
        return len(self.graph.edges)