"""
Entity Operations for Memory Graph

Provides functions for entity CRUD operations in the memory graph.
"""

import logging
from typing import Optional

from ...entity import Entity

logger = logging.getLogger("athena.graph.memory.entity_ops")

async def create_entity(adapter, entity: Entity) -> str:
    """
    Create a new entity in the graph.
    
    Args:
        adapter: The memory adapter instance
        entity: Entity to create
        
    Returns:
        Entity ID
    """
    adapter.graph.add_node(entity.entity_id, entity=entity)
    logger.debug(f"Created entity: {entity.name} ({entity.entity_id})")
    return entity.entity_id

async def get_entity(adapter, entity_id: str) -> Optional[Entity]:
    """
    Get an entity by ID.
    
    Args:
        adapter: The memory adapter instance
        entity_id: Entity ID
        
    Returns:
        Entity or None if not found
    """
    if entity_id in adapter.graph.nodes:
        entity = adapter.graph.nodes[entity_id].get('entity')
        if entity:
            logger.debug(f"Retrieved entity: {entity.name} ({entity.entity_id})")
        else:
            logger.warning(f"Entity node exists but has no entity data: {entity_id}")
        return entity
    logger.debug(f"Entity not found: {entity_id}")
    return None

async def update_entity(adapter, entity: Entity) -> bool:
    """
    Update an entity.
    
    Args:
        adapter: The memory adapter instance
        entity: Updated entity
        
    Returns:
        True if successful
    """
    if entity.entity_id in adapter.graph.nodes:
        adapter.graph.nodes[entity.entity_id]['entity'] = entity
        logger.debug(f"Updated entity: {entity.name} ({entity.entity_id})")
        return True
    logger.warning(f"Cannot update entity: {entity.entity_id} - not found")
    return False

async def delete_entity(adapter, entity_id: str) -> bool:
    """
    Delete an entity.
    
    Args:
        adapter: The memory adapter instance
        entity_id: Entity ID to delete
        
    Returns:
        True if successful
    """
    if entity_id in adapter.graph.nodes:
        adapter.graph.remove_node(entity_id)
        logger.debug(f"Deleted entity: {entity_id}")
        return True
    logger.warning(f"Cannot delete entity: {entity_id} - not found")
    return False