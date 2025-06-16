"""
Neo4j Count Operations

Count operations for Neo4j in Athena.
"""

import logging

logger = logging.getLogger("athena.graph.neo4j.operations.count")

async def count_entities(client) -> int:
    """Count the number of entities in the graph."""
    try:
        # Query to count entities
        query = "MATCH (n:Entity) RETURN COUNT(n) AS count"
        
        if hasattr(client, "query"):
            result = await client.query(query)
            count = result[0].get("count", 0) if result else 0
            return count
        else:
            # Direct Neo4j client
            async with client.session() as session:
                result = await session.run(query)
                record = await result.single()
                return record["count"] if record else 0
                
    except Exception as e:
        logger.error(f"Error counting entities: {e}")
        return 0

async def count_relationships(client) -> int:
    """Count the number of relationships in the graph."""
    try:
        # Query to count relationships
        query = "MATCH ()-[r]->() RETURN COUNT(r) AS count"
        
        if hasattr(client, "query"):
            result = await client.query(query)
            count = result[0].get("count", 0) if result else 0
            return count
        else:
            # Direct Neo4j client
            async with client.session() as session:
                result = await session.run(query)
                record = await result.single()
                return record["count"] if record else 0
                
    except Exception as e:
        logger.error(f"Error counting relationships: {e}")
        return 0