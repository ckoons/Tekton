"""
Neo4j Entity Operations

Basic entity CRUD operations for Neo4j in Athena.
"""

import logging
from typing import Dict, Any, List, Optional, Type, TypeVar

# Type variable for generic entity type
E = TypeVar('E')

logger = logging.getLogger("athena.graph.neo4j.operations.entity")

async def create_entity(client, entity_id: str, labels: List[str], properties: Dict[str, Any]) -> bool:
    """Create a new entity in Neo4j."""
    try:
        # Format labels for Cypher
        labels_str = ":".join(labels)
        
        # Merge the entity - avoids duplicates but creates if not exists
        query = f"""
        MERGE (n:{labels_str} {{entity_id: $entity_id}})
        SET n = $properties
        RETURN n
        """
        
        # Execute query directly if using Hermes client
        if hasattr(client, "query"):
            await client.query(query, {"entity_id": entity_id, "properties": properties})
            return True
            
        # Execute query through Neo4j client
        async with client.session() as session:
            result = await session.run(
                query,
                entity_id=entity_id,
                properties=properties
            )
            await result.consume()
            return True
            
    except Exception as e:
        logger.error(f"Error creating entity: {e}")
        return False

async def get_entity(client, entity_id: str, entity_class: Type[E]) -> Optional[E]:
    """Get an entity by ID."""
    try:
        # Query to get an entity by ID
        query = """
        MATCH (n:Entity {entity_id: $entity_id})
        RETURN n
        """
        
        # Handle Hermes client or direct client
        if hasattr(client, "get_node"):
            node = await client.get_node(id=entity_id)
            if not node:
                return None
                
            # Get entity data
            entity_data = node.get("properties", {})
            
            # Create and return entity
            return entity_class.from_dict(entity_data)
        else:
            # Direct Neo4j client
            async with client.session() as session:
                result = await session.run(query, entity_id=entity_id)
                record = await result.single()
                
                if not record:
                    return None
                    
                # Extract entity data
                node = record["n"]
                entity_data = dict(node.items())
                
                # Create and return entity
                return entity_class.from_dict(entity_data)
                
    except Exception as e:
        logger.error(f"Error getting entity: {e}")
        return None

async def update_entity(client, entity) -> bool:
    """Update an existing entity."""
    try:
        # Convert entity to properties
        properties = entity.to_dict()
        
        # Create query to update entity
        query = """
        MATCH (n:Entity {entity_id: $entity_id})
        SET n = $properties
        RETURN n
        """
        
        # Execute query
        if hasattr(client, "query"):
            result = await client.query(
                query,
                params={
                    "entity_id": entity.entity_id,
                    "properties": properties
                }
            )
            
            return len(result) > 0
        else:
            # Direct Neo4j client
            async with client.session() as session:
                result = await session.run(
                    query,
                    entity_id=entity.entity_id,
                    properties=properties
                )
                summary = await result.consume()
                return summary.counters.properties_set > 0
                
    except Exception as e:
        logger.error(f"Error updating entity: {e}")
        return False

async def delete_entity(client, entity_id: str) -> bool:
    """Delete an entity by ID."""
    try:
        # Delete node using Hermes client or direct client
        if hasattr(client, "delete_node"):
            return await client.delete_node(id=entity_id)
        else:
            # Direct Neo4j client - detach delete to remove relationships too
            query = """
            MATCH (n:Entity {entity_id: $entity_id})
            DETACH DELETE n
            """
            
            async with client.session() as session:
                result = await session.run(query, entity_id=entity_id)
                summary = await result.consume()
                return summary.counters.nodes_deleted > 0
                
    except Exception as e:
        logger.error(f"Error deleting entity: {e}")
        return False