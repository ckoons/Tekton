"""
In-Memory Graph Persistence

Provides functions for loading and saving graph data to disk.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

from ...entity import Entity
from ...relationship import Relationship

logger = logging.getLogger("athena.graph.memory.persistence")

async def load_data(adapter) -> None:
    """
    Load graph data from persistence files.
    
    Args:
        adapter: The memory adapter instance
    """
    # Load entities
    if os.path.exists(adapter.entity_file):
        try:
            with open(adapter.entity_file, 'r') as f:
                entities_data = json.load(f)
                
            for entity_data in entities_data:
                entity = Entity.from_dict(entity_data)
                adapter.graph.add_node(entity.entity_id, entity=entity)
                
            logger.info(f"Loaded {len(entities_data)} entities from {adapter.entity_file}")
        except Exception as e:
            logger.error(f"Error loading entities: {e}")
            
    # Load relationships
    if os.path.exists(adapter.relationship_file):
        try:
            with open(adapter.relationship_file, 'r') as f:
                relationships_data = json.load(f)
                
            for rel_data in relationships_data:
                relationship = Relationship.from_dict(rel_data)
                adapter.graph.add_edge(
                    relationship.source_id,
                    relationship.target_id,
                    key=relationship.relationship_id,
                    relationship=relationship
                )
                
            logger.info(f"Loaded {len(relationships_data)} relationships from {adapter.relationship_file}")
        except Exception as e:
            logger.error(f"Error loading relationships: {e}")

async def save_data(adapter) -> None:
    """
    Save graph data to persistence files.
    
    Args:
        adapter: The memory adapter instance
    """
    # Save entities
    try:
        entities_data = []
        for node_id in adapter.graph.nodes():
            entity = adapter.graph.nodes[node_id].get('entity')
            if entity:
                entities_data.append(entity.to_dict())
                
        with open(adapter.entity_file, 'w') as f:
            json.dump(entities_data, f, indent=2)
            
        logger.info(f"Saved {len(entities_data)} entities to {adapter.entity_file}")
    except Exception as e:
        logger.error(f"Error saving entities: {e}")
        
    # Save relationships
    try:
        relationships_data = []
        for source_id, target_id, rel_id in adapter.graph.edges(keys=True):
            relationship = adapter.graph[source_id][target_id][rel_id].get('relationship')
            if relationship:
                relationships_data.append(relationship.to_dict())
                
        with open(adapter.relationship_file, 'w') as f:
            json.dump(relationships_data, f, indent=2)
            
        logger.info(f"Saved {len(relationships_data)} relationships to {adapter.relationship_file}")
    except Exception as e:
        logger.error(f"Error saving relationships: {e}")