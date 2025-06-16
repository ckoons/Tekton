"""
Relationship Operations for Memory Graph

Provides functions for relationship CRUD operations in the memory graph.
"""

import logging
from typing import Optional

from ...relationship import Relationship

logger = logging.getLogger("athena.graph.memory.relationship_ops")

async def create_relationship(adapter, relationship: Relationship) -> str:
    """
    Create a new relationship in the graph.
    
    Args:
        adapter: The memory adapter instance
        relationship: Relationship to create
        
    Returns:
        Relationship ID
    """
    adapter.graph.add_edge(
        relationship.source_id,
        relationship.target_id,
        key=relationship.relationship_id,
        relationship=relationship
    )
    logger.debug(f"Created relationship: {relationship.relationship_type} ({relationship.relationship_id})")
    return relationship.relationship_id

async def get_relationship(adapter, relationship_id: str) -> Optional[Relationship]:
    """
    Get a relationship by ID.
    
    Args:
        adapter: The memory adapter instance
        relationship_id: Relationship ID
        
    Returns:
        Relationship or None if not found
    """
    for source_id, target_id, rel_id in adapter.graph.edges(keys=True):
        if rel_id == relationship_id:
            relationship = adapter.graph[source_id][target_id][rel_id].get('relationship')
            if relationship:
                logger.debug(f"Retrieved relationship: {relationship.relationship_type} ({relationship_id})")
            else:
                logger.warning(f"Relationship exists but has no relationship data: {relationship_id}")
            return relationship
    logger.debug(f"Relationship not found: {relationship_id}")
    return None

async def update_relationship(adapter, relationship: Relationship) -> bool:
    """
    Update a relationship.
    
    Args:
        adapter: The memory adapter instance
        relationship: Updated relationship
        
    Returns:
        True if successful
    """
    for source_id, target_id, rel_id in adapter.graph.edges(keys=True):
        if rel_id == relationship.relationship_id:
            adapter.graph[source_id][target_id][rel_id]['relationship'] = relationship
            logger.debug(f"Updated relationship: {relationship.relationship_type} ({relationship.relationship_id})")
            return True
    logger.warning(f"Cannot update relationship: {relationship.relationship_id} - not found")
    return False

async def delete_relationship(adapter, relationship_id: str) -> bool:
    """
    Delete a relationship.
    
    Args:
        adapter: The memory adapter instance
        relationship_id: Relationship ID to delete
        
    Returns:
        True if successful
    """
    for source_id, target_id, rel_id in list(adapter.graph.edges(keys=True)):
        if rel_id == relationship_id:
            adapter.graph.remove_edge(source_id, target_id, rel_id)
            logger.debug(f"Deleted relationship: {relationship_id}")
            return True
    logger.warning(f"Cannot delete relationship: {relationship_id} - not found")
    return False