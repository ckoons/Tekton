"""
Query Operations for Memory Graph

Provides functions for querying the memory graph.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from ...entity import Entity
from ...relationship import Relationship

logger = logging.getLogger("athena.graph.memory.query_ops")

async def search_entities(adapter, query: str, entity_type: Optional[str] = None, limit: int = 10) -> List[Entity]:
    """
    Search for entities matching a query.
    
    Args:
        adapter: The memory adapter instance
        query: Search query
        entity_type: Optional entity type filter
        limit: Maximum number of results
        
    Returns:
        List of matching entities
    """
    query = query.lower()
    results = []
    
    for node_id in adapter.graph.nodes():
        entity = adapter.graph.nodes[node_id].get('entity')
        if not entity:
            continue
            
        # Filter by entity type if specified
        if entity_type and entity.entity_type != entity_type:
            continue
            
        # Check for matches in name or aliases
        if (query in entity.name.lower() or 
            any(query in alias.lower() for alias in entity.aliases)):
            results.append(entity)
            
        # Check for matches in properties
        for key, prop in entity.properties.items():
            value = prop.get('value')
            if isinstance(value, str) and query in value.lower():
                if entity not in results:
                    results.append(entity)
                break
                
        if len(results) >= limit:
            break
            
    logger.debug(f"Search for '{query}' found {len(results)} entities")
    return results[:limit]

async def get_entity_relationships(adapter, entity_id: str, 
                         relationship_type: Optional[str] = None,
                         direction: str = "both") -> List[Tuple[Relationship, Entity]]:
    """
    Get relationships for an entity.
    
    Args:
        adapter: The memory adapter instance
        entity_id: Entity ID
        relationship_type: Optional relationship type filter
        direction: Relationship direction ('outgoing', 'incoming', or 'both')
        
    Returns:
        List of (relationship, connected entity) tuples
    """
    results = []
    
    # Get outgoing relationships
    if direction in ["outgoing", "both"]:
        for _, target_id, rel_id in adapter.graph.out_edges(entity_id, keys=True):
            relationship = adapter.graph[entity_id][target_id][rel_id].get('relationship')
            target_entity = adapter.graph.nodes[target_id].get('entity')
            
            if not relationship or not target_entity:
                continue
                
            if relationship_type and relationship.relationship_type != relationship_type:
                continue
                
            results.append((relationship, target_entity))
            
    # Get incoming relationships
    if direction in ["incoming", "both"]:
        for source_id, _, rel_id in adapter.graph.in_edges(entity_id, keys=True):
            relationship = adapter.graph[source_id][entity_id][rel_id].get('relationship')
            source_entity = adapter.graph.nodes[source_id].get('entity')
            
            if not relationship or not source_entity:
                continue
                
            if relationship_type and relationship.relationship_type != relationship_type:
                continue
                
            results.append((relationship, source_entity))
    
    logger.debug(f"Found {len(results)} relationships for entity {entity_id}")
    return results

async def execute_query(query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Execute a raw query.
    
    Note: For the in-memory adapter, this is a stub that logs the query and returns an empty result.
    
    Args:
        query: Query string
        params: Query parameters
        
    Returns:
        Query results
    """
    logger.warning(f"Raw query execution not supported in memory adapter. Query: {query}")
    return []