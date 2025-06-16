"""
Neo4j Path Operations

Path finding operations for Neo4j in Athena.
"""

import logging
from typing import List, Union, Type, TypeVar

# Type variables for generic entity and relationship types
E = TypeVar('E')
R = TypeVar('R')

logger = logging.getLogger("athena.graph.neo4j.operations.path")

async def find_paths(client, source_id: str, target_id: str, max_depth: int = 3, entity_class: Type[E] = None, relationship_class: Type[R] = None) -> List[List[Union[E, R]]]:
    """Find paths between two entities."""
    try:
        # Build Cypher query for path finding
        query = """
        MATCH path = (source:Entity {entity_id: $source_id})-[*1..$max_depth]->
                    (target:Entity {entity_id: $target_id})
        RETURN path
        LIMIT 10
        """
        
        params = {
            "source_id": source_id,
            "target_id": target_id,
            "max_depth": max_depth
        }
        
        if hasattr(client, "query"):
            result = await client.query(query, params=params)
            
            # Process paths
            paths = []
            for record in result:
                path_data = record.get("path", [])
                
                # Skip empty paths
                if not path_data:
                    continue
                    
                # Process path into alternating Entity and Relationship objects
                processed_path = []
                
                # Add each node and relationship to the path
                for i, item in enumerate(path_data):
                    if i % 2 == 0:  # Entity
                        processed_path.append(entity_class.from_dict(item))
                    else:  # Relationship
                        processed_path.append(relationship_class.from_dict(item))
                        
                paths.append(processed_path)
                
            return paths
        else:
            # Direct Neo4j client
            async with client.session() as session:
                result = await session.run(query, **params)
                
                paths = []
                async for record in result:
                    path = record["path"]
                    
                    # Process path
                    processed_path = []
                    
                    # Extract nodes and relationships
                    nodes = path.nodes
                    relationships = path.relationships
                    
                    # Add source node
                    processed_path.append(entity_class.from_dict(dict(nodes[0].items())))
                    
                    # Add alternating relationships and nodes
                    for i in range(len(relationships)):
                        processed_path.append(relationship_class.from_dict(dict(relationships[i].items())))
                        processed_path.append(entity_class.from_dict(dict(nodes[i+1].items())))
                        
                    paths.append(processed_path)
                    
                return paths
                
    except Exception as e:
        logger.error(f"Error finding paths: {e}")
        return []