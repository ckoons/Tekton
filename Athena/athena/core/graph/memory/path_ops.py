"""
Path Operations for Memory Graph

Provides functions for finding paths in the memory graph.
"""

import logging
import networkx as nx
from typing import List, Union

from ...entity import Entity
from ...relationship import Relationship

logger = logging.getLogger("athena.graph.memory.path_ops")

async def find_paths(adapter, source_id: str, target_id: str, max_depth: int = 3) -> List[List[Union[Entity, Relationship]]]:
    """
    Find paths between two entities.
    
    Args:
        adapter: The memory adapter instance
        source_id: Source entity ID
        target_id: Target entity ID
        max_depth: Maximum path length
        
    Returns:
        List of paths, where each path is a list of alternating Entity and Relationship objects
    """
    if source_id not in adapter.graph.nodes or target_id not in adapter.graph.nodes:
        logger.debug(f"Cannot find path: source {source_id} or target {target_id} not found")
        return []
        
    # Use NetworkX to find simple paths
    try:
        # Find all simple paths up to length 2*max_depth (edges + nodes)
        # This accounts for the fact that we're counting relationship hops, not graph hops
        simple_paths = list(nx.all_simple_paths(
            adapter.graph, source_id, target_id, cutoff=max_depth*2-1
        ))
    except nx.NetworkXNoPath:
        logger.debug(f"No path found between {source_id} and {target_id}")
        return []
        
    # Convert simple paths to entity/relationship sequences
    result_paths = []
    for path in simple_paths:
        entity_rel_path = []
        
        # Add the source entity
        entity_rel_path.append(adapter.graph.nodes[path[0]].get('entity'))
        
        # Add relationships and entities along the path
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            
            # Find the relationship between these nodes
            # (there could be multiple, take the first one)
            rel_id = list(adapter.graph[source][target].keys())[0]
            relationship = adapter.graph[source][target][rel_id].get('relationship')
            entity_rel_path.append(relationship)
            
            # Add the target entity
            entity_rel_path.append(adapter.graph.nodes[target].get('entity'))
            
        result_paths.append(entity_rel_path)
    
    logger.debug(f"Found {len(result_paths)} paths between {source_id} and {target_id}")
    return result_paths