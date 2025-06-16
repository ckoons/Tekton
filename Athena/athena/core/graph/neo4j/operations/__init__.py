"""
Neo4j Operations Package

Contains all database operations for Neo4j in Athena, organized by functionality.
"""

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

from .count_ops import (
    count_entities,
    count_relationships
)

# Export all operations
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