"""
Neo4j Query Operations

Query operations for Neo4j in Athena.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Type, TypeVar

# Type variables for generic entity and relationship types
E = TypeVar('E')
R = TypeVar('R')

logger = logging.getLogger("athena.graph.neo4j.operations.query")

async def search_entities(client, query: str, entity_type: Optional[str] = None, limit: int = 10, entity_class: Type[E] = None) -> List[E]:
    """Search for entities matching a query."""
    try:
        # Build Cypher query for entity search
        cypher_query = """
        MATCH (n:Entity)
        WHERE (n.name CONTAINS $query OR any(alias IN n.aliases WHERE alias CONTAINS $query))
        """
        
        # Add entity type filter
        if entity_type:
            cypher_query += f" AND n:{entity_type}"
            
        # Add limit and return
        cypher_query += " RETURN n LIMIT $limit"
        
        # Parameters
        params = {"query": query.lower(), "limit": limit}
        
        # Execute query
        if hasattr(client, "query"):
            result = await client.query(cypher_query, params=params)
            
            # Convert results to entities
            entities = []
            for record in result:
                entity_data = record.get("n", {})
                entity = entity_class.from_dict(entity_data)
                entities.append(entity)
                
            return entities
        else:
            # Direct Neo4j client
            async with client.session() as session:
                result = await session.run(cypher_query, **params)
                
                # Process results
                entities = []
                async for record in result:
                    node = record["n"]
                    entity_data = dict(node.items())
                    entity = entity_class.from_dict(entity_data)
                    entities.append(entity)
                    
                return entities
                
    except Exception as e:
        logger.error(f"Error searching entities: {e}")
        return []

async def get_entity_relationships(client, entity_id: str, relationship_type: Optional[str] = None, direction: str = "both", relationship_class: Type[R] = None, entity_class: Type[E] = None) -> List[Tuple[R, E]]:
    """Get relationships for an entity."""
    try:
        results = []
        
        # Handle outgoing relationships
        if direction in ["outgoing", "both"]:
            # Build query for outgoing relationships
            query = """
            MATCH (source:Entity {entity_id: $entity_id})-[r]->(target:Entity)
            """
            
            # Add relationship type filter
            if relationship_type:
                query += f" WHERE type(r) = $rel_type"
                
            query += " RETURN r, target"
            
            # Execute query
            if hasattr(client, "query"):
                params = {
                    "entity_id": entity_id,
                    "rel_type": relationship_type
                } if relationship_type else {"entity_id": entity_id}
                
                result = await client.query(query, params=params)
                
                # Process results
                for record in result:
                    rel_data = record.get("r", {})
                    target_data = record.get("target", {})
                    
                    relationship = relationship_class.from_dict(rel_data)
                    target_entity = entity_class.from_dict(target_data)
                    
                    results.append((relationship, target_entity))
            else:
                # Direct Neo4j client
                async with client.session() as session:
                    params = {"entity_id": entity_id}
                    if relationship_type:
                        params["rel_type"] = relationship_type
                        
                    result = await session.run(query, **params)
                    
                    # Process results
                    async for record in result:
                        rel = record["r"]
                        target = record["target"]
                        
                        relationship = relationship_class.from_dict(dict(rel.items()))
                        target_entity = entity_class.from_dict(dict(target.items()))
                        
                        results.append((relationship, target_entity))
        
        # Handle incoming relationships
        if direction in ["incoming", "both"]:
            # Similar logic for incoming relationships
            query = """
            MATCH (source:Entity)-[r]->(target:Entity {entity_id: $entity_id})
            """
            
            if relationship_type:
                query += f" WHERE type(r) = $rel_type"
                
            query += " RETURN r, source"
            
            # Execute query - similar to above with source/target swapped
            if hasattr(client, "query"):
                params = {
                    "entity_id": entity_id,
                    "rel_type": relationship_type
                } if relationship_type else {"entity_id": entity_id}
                
                result = await client.query(query, params=params)
                
                for record in result:
                    rel_data = record.get("r", {})
                    source_data = record.get("source", {})
                    
                    relationship = relationship_class.from_dict(rel_data)
                    source_entity = entity_class.from_dict(source_data)
                    
                    results.append((relationship, source_entity))
            else:
                # Direct Neo4j client
                async with client.session() as session:
                    params = {"entity_id": entity_id}
                    if relationship_type:
                        params["rel_type"] = relationship_type
                        
                    result = await session.run(query, **params)
                    
                    async for record in result:
                        rel = record["r"]
                        source = record["source"]
                        
                        relationship = relationship_class.from_dict(dict(rel.items()))
                        source_entity = entity_class.from_dict(dict(source.items()))
                        
                        results.append((relationship, source_entity))
                        
        return results
                
    except Exception as e:
        logger.error(f"Error getting entity relationships: {e}")
        return []

async def execute_query(client, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Execute a raw Cypher query."""
    try:
        if hasattr(client, "query"):
            return await client.query(query, params=params)
        else:
            # Direct Neo4j client
            async with client.session() as session:
                result = await session.run(query, **(params or {}))
                
                # Convert result to list of dictionaries
                records = []
                async for record in result:
                    # Convert record to dict
                    record_dict = {}
                    
                    for key, value in record.items():
                        # Handle Neo4j types
                        if hasattr(value, "items"):  # Node or Relationship
                            record_dict[key] = dict(value.items())
                        elif isinstance(value, list) and value and all(hasattr(item, "items") for item in value):
                            # List of nodes or relationships
                            record_dict[key] = [dict(item.items()) for item in value]
                        else:
                            record_dict[key] = value
                    
                    records.append(record_dict)
                    
                return records
                
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return []