"""
Athena API Endpoints for Graph Visualization

Provides REST API endpoints for visualization of the knowledge graph.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Body

from athena.api.models.visualization import (
    GraphVisualizationRequest,
    GraphVisualizationResponse,
    SubgraphRequest,
    SubgraphResponse,
    VisualizationLayout
)
from athena.core.engine import get_knowledge_engine

logger = logging.getLogger("athena.api.visualization")

router = APIRouter(prefix="/visualization", tags=["visualization"])

@router.get("/graph", response_model=GraphVisualizationResponse)
async def get_visualization_data(
    limit: int = Query(100, description="Maximum number of entities to include"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    min_confidence: float = Query(0.0, description="Minimum confidence threshold"),
    center_node: Optional[str] = Query(None, description="ID of node to center graph around"),
    depth: int = Query(1, description="Depth of relationships from center node"),
    layout: VisualizationLayout = Query(VisualizationLayout.force_directed, description="Graph layout algorithm")
):
    """
    Get visualization data for the knowledge graph.
    
    This endpoint provides data structured for visualization in D3.js or similar tools.
    """
    engine = await get_knowledge_engine()
    
    try:
        if center_node:
            # Get subgraph around a specific node
            graph_data = await get_node_subgraph(
                center_node=center_node,
                depth=depth,
                relationship_type=relationship_type,
                min_confidence=min_confidence
            )
        else:
            # Get general graph data with specified filters
            entities = []
            relationships = []
            
            # Get entities with filters
            query = ""
            if entity_type:
                query_parts = []
                if entity_type:
                    query_parts.append(f"entity_type:{entity_type}")
                if query_parts:
                    query = " ".join(query_parts)
            
            # Execute search
            entities = await engine.search_entities(
                query=query,
                entity_type=entity_type,
                limit=limit
            )
            
            # Get relationships between these entities
            entity_ids = [e.entity_id for e in entities]
            
            # For each entity, get relationships within our entity set
            for entity_id in entity_ids:
                entity_relationships = await engine.get_entity_relationships(
                    entity_id=entity_id,
                    relationship_type=relationship_type,
                    direction="both"
                )
                
                # Only include relationships between our entities
                for rel, connected_entity in entity_relationships:
                    if connected_entity.entity_id in entity_ids and rel.confidence >= min_confidence:
                        if rel not in relationships:
                            relationships.append(rel)
            
            graph_data = {
                "entities": entities,
                "relationships": relationships
            }
        
        return GraphVisualizationResponse(
            entities=graph_data["entities"],
            relationships=graph_data["relationships"],
            layout=layout
        )
    
    except Exception as e:
        logger.error(f"Error getting visualization data: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving visualization data: {str(e)}")

@router.get("/subgraph/{entity_id}", response_model=SubgraphResponse)
async def get_subgraph(
    entity_id: str,
    depth: int = Query(1, description="Depth of relationships to include"),
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    min_confidence: float = Query(0.0, description="Minimum confidence threshold"),
    layout: VisualizationLayout = Query(VisualizationLayout.force_directed, description="Graph layout algorithm")
):
    """
    Get a subgraph around a specific entity.
    
    This endpoint retrieves a subgraph centered on the specified entity,
    including all connected entities up to the specified depth.
    """
    try:
        graph_data = await get_node_subgraph(
            center_node=entity_id,
            depth=depth,
            relationship_type=relationship_type,
            min_confidence=min_confidence
        )
        
        return SubgraphResponse(
            center_entity_id=entity_id,
            depth=depth,
            entities=graph_data["entities"],
            relationships=graph_data["relationships"],
            layout=layout
        )
    
    except Exception as e:
        logger.error(f"Error getting subgraph data: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving subgraph data: {str(e)}")

@router.post("/custom", response_model=GraphVisualizationResponse)
async def create_custom_visualization(request: GraphVisualizationRequest):
    """
    Create a custom visualization based on specific requirements.
    
    This endpoint allows for more complex filtering and customization
    of the graph visualization.
    """
    engine = await get_knowledge_engine()
    
    try:
        # Custom query logic would go here
        # For now, we'll use the same logic as get_visualization_data
        
        if request.center_node_id:
            # Get subgraph around a specific node
            graph_data = await get_node_subgraph(
                center_node=request.center_node_id,
                depth=request.depth or 1,
                relationship_type=request.relationship_type,
                min_confidence=request.min_confidence or 0.0
            )
        else:
            # Get entities with filters
            query = ""
            if request.query:
                query = request.query
            
            # Execute search
            entities = await engine.search_entities(
                query=query,
                entity_type=request.entity_type,
                limit=request.limit or 100
            )
            
            # Get relationships between these entities
            entity_ids = [e.entity_id for e in entities]
            relationships = []
            
            # For each entity, get relationships within our entity set
            for entity_id in entity_ids:
                entity_relationships = await engine.get_entity_relationships(
                    entity_id=entity_id,
                    relationship_type=request.relationship_type,
                    direction="both"
                )
                
                # Only include relationships between our entities
                for rel, connected_entity in entity_relationships:
                    if connected_entity.entity_id in entity_ids and rel.confidence >= (request.min_confidence or 0.0):
                        if rel not in relationships:
                            relationships.append(rel)
            
            graph_data = {
                "entities": entities,
                "relationships": relationships
            }
        
        return GraphVisualizationResponse(
            entities=graph_data["entities"],
            relationships=graph_data["relationships"],
            layout=request.layout or VisualizationLayout.force_directed
        )
    
    except Exception as e:
        logger.error(f"Error creating custom visualization: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating visualization: {str(e)}")

@router.get("/layouts")
async def get_available_layouts():
    """
    Get a list of available graph layout algorithms.
    """
    return {
        "layouts": [layout.value for layout in VisualizationLayout]
    }

async def get_node_subgraph(
    center_node: str,
    depth: int = 1,
    relationship_type: Optional[str] = None,
    min_confidence: float = 0.0
):
    """
    Helper function to get a subgraph around a center node.
    
    Args:
        center_node: ID of the central entity
        depth: How many relationship hops to include
        relationship_type: Filter relationships by type
        min_confidence: Minimum confidence threshold for relationships
        
    Returns:
        Dictionary with entities and relationships lists
    """
    engine = await get_knowledge_engine()
    
    # Get the center entity
    center_entity = await engine.get_entity(center_node)
    if not center_entity:
        raise HTTPException(status_code=404, detail=f"Entity with ID {center_node} not found")
    
    # Collect entities and relationships
    entities = [center_entity]
    relationships = []
    entity_ids = {center_entity.entity_id}
    
    # Queue of nodes to process with their current depth
    queue = [(center_entity.entity_id, 0)]
    processed = set()
    
    while queue:
        current_id, current_depth = queue.pop(0)
        
        if current_id in processed:
            continue
            
        processed.add(current_id)
        
        if current_depth >= depth:
            continue
        
        # Get relationships for this entity
        entity_relationships = await engine.get_entity_relationships(
            entity_id=current_id,
            relationship_type=relationship_type,
            direction="both"
        )
        
        for rel, connected_entity in entity_relationships:
            if rel.confidence < min_confidence:
                continue
                
            # Add relationship if it meets criteria
            if rel not in relationships:
                relationships.append(rel)
            
            # Add connected entity if not already included
            if connected_entity.entity_id not in entity_ids:
                entities.append(connected_entity)
                entity_ids.add(connected_entity.entity_id)
                
                # Add to queue for next level processing
                queue.append((connected_entity.entity_id, current_depth + 1))
    
    return {
        "entities": entities,
        "relationships": relationships
    }