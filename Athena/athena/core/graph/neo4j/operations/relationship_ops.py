"""
Neo4j Relationship Operations

Basic relationship CRUD operations for Neo4j in Athena.
"""

import logging
from typing import Dict, Any, Optional, Type, TypeVar

# Type variable for generic relationship type
R = TypeVar('R')

logger = logging.getLogger("athena.graph.neo4j.operations.relationship")

async def create_relationship(client, source_id: str, target_id: str, rel_type: str, properties: Dict[str, Any]) -> str:
    """Create a new relationship."""
    try:
        relationship_id = properties.get("relationship_id")
        
        # Create relationship using Hermes client or direct client
        if hasattr(client, "add_relationship"):
            await client.add_relationship(
                source_id=source_id,
                target_id=target_id,
                type=rel_type,
                properties=properties
            )
            return relationship_id
        else:
            # Direct Neo4j client
            query = f"""
            MATCH (source:Entity {{entity_id: $source_id}})
            MATCH (target:Entity {{entity_id: $target_id}})
            MERGE (source)-[r:{rel_type}]->(target)
            SET r = $properties
            RETURN r
            """
            
            async with client.session() as session:
                result = await session.run(
                    query,
                    source_id=source_id,
                    target_id=target_id,
                    properties=properties
                )
                await result.consume()
                return relationship_id
                
    except Exception as e:
        logger.error(f"Error creating relationship: {e}")
        raise

async def get_relationship(client, relationship_id: str, relationship_class: Type[R]) -> Optional[R]:
    """Get a relationship by ID."""
    try:
        # Query to get a relationship by ID
        query = """
        MATCH ()-[r {relationship_id: $relationship_id}]->()
        RETURN r
        """
        
        # Execute query
        if hasattr(client, "query"):
            result = await client.query(
                query,
                params={"relationship_id": relationship_id}
            )
            
            if not result or len(result) == 0:
                return None
                
            # Extract relationship data
            rel_data = result[0].get("r", {})
            
            # Create and return relationship
            return relationship_class.from_dict(rel_data)
        else:
            # Direct Neo4j client
            async with client.session() as session:
                result = await session.run(query, relationship_id=relationship_id)
                record = await result.single()
                
                if not record:
                    return None
                    
                # Extract relationship data
                rel = record["r"]
                rel_data = dict(rel.items())
                
                # Create and return relationship
                return relationship_class.from_dict(rel_data)
                
    except Exception as e:
        logger.error(f"Error getting relationship: {e}")
        return None

async def update_relationship(client, relationship) -> bool:
    """Update an existing relationship."""
    try:
        # Convert relationship to properties
        properties = relationship.to_dict()
        
        # Create query to update relationship
        query = """
        MATCH ()-[r {relationship_id: $relationship_id}]->()
        SET r = $properties
        RETURN r
        """
        
        # Execute query
        if hasattr(client, "query"):
            result = await client.query(
                query,
                params={
                    "relationship_id": relationship.relationship_id,
                    "properties": properties
                }
            )
            
            return len(result) > 0
        else:
            # Direct Neo4j client
            async with client.session() as session:
                result = await session.run(
                    query,
                    relationship_id=relationship.relationship_id,
                    properties=properties
                )
                summary = await result.consume()
                return summary.counters.properties_set > 0
                
    except Exception as e:
        logger.error(f"Error updating relationship: {e}")
        return False

async def delete_relationship(client, relationship_id: str) -> bool:
    """Delete a relationship by ID."""
    try:
        # Create query to delete relationship
        query = """
        MATCH ()-[r {relationship_id: $relationship_id}]->()
        DELETE r
        """
        
        # Execute query
        if hasattr(client, "query"):
            result = await client.query(
                query,
                params={"relationship_id": relationship_id}
            )
            
            # Check result - this is approximate since we don't have direct access to counters
            return True
        else:
            # Direct Neo4j client
            async with client.session() as session:
                result = await session.run(query, relationship_id=relationship_id)
                summary = await result.consume()
                return summary.counters.relationships_deleted > 0
                
    except Exception as e:
        logger.error(f"Error deleting relationship: {e}")
        return False