"""
Neo4j Operations

Core database operations for Neo4j in Athena.
This file re-exports all operations from the operations/ package for backward compatibility.
"""

from .operations import (
    # Entity operations
    create_entity,
    get_entity,
    update_entity,
    delete_entity,
    
    # Relationship operations
    create_relationship,
    get_relationship,
    update_relationship,
    delete_relationship,
    
    # Query operations
    search_entities,
    get_entity_relationships,
    execute_query,
    
    # Path operations
    find_paths,
    
    # Count operations
    count_entities,
    count_relationships
)

__all__ = [
    # Entity operations
    'create_entity',
    'get_entity',
    'update_entity',
    'delete_entity',
    
    # Relationship operations
    'create_relationship',
    'get_relationship',
    'update_relationship',
    'delete_relationship',
    
    # Query operations
    'search_entities',
    'get_entity_relationships',
    'execute_query',
    
    # Path operations
    'find_paths',
    
    # Count operations
    'count_entities',
    'count_relationships'
]