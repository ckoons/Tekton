"""
Athena API Endpoints for Entity Management

Provides REST API endpoints for entity management and operations.
"""

from typing import Dict, List, Any, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Body

from tekton.core.query.modes import QueryMode, QueryParameters

from athena.api.models.entity import (
    EntityCreate,
    EntityResponse,
    EntityMergeRequest,
    EntityMergeResponse,
    EntitySearchResult
)
from athena.core.engine import get_knowledge_engine
from athena.core.entity_manager import EntityManager

# Try to import landmarks - handle gracefully if not available
try:
    from landmarks import api_contract, integration_point, danger_zone
except ImportError:
    # Create no-op decorators
    def api_contract(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def danger_zone(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

router = APIRouter(tags=["entities"])

@router.post("/", response_model=EntityResponse)
@api_contract(
    title="Entity Creation API",
    endpoint="/api/v1/entities",
    method="POST",
    request_schema={"name": "string", "type": "string", "properties": "object", "relationships": "list"}
)
@integration_point(
    title="Knowledge Engine Integration",
    target_component="Knowledge Engine, Graph Store",
    protocol="Internal Python API",
    data_flow="API Request -> Entity Manager -> Knowledge Engine -> Graph Storage"
)
async def create_entity(entity: EntityCreate):
    """
    Create a new entity in the knowledge graph.
    """
    engine = await get_knowledge_engine()
    
    # Convert to domain entity
    domain_entity = entity.to_domain_entity()
    
    # Add to knowledge graph
    entity_id = await engine.add_entity(domain_entity)
    
    # Retrieve created entity
    created_entity = await engine.get_entity(entity_id)
    if not created_entity:
        raise HTTPException(status_code=500, detail="Failed to retrieve created entity")
    
    return EntityResponse.from_domain_entity(created_entity)

@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: str):
    """
    Get an entity by ID.
    """
    engine = await get_knowledge_engine()
    
    entity = await engine.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity with ID {entity_id} not found")
    
    return EntityResponse.from_domain_entity(entity)

@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(entity_id: str, entity_update: EntityCreate):
    """
    Update an existing entity.
    """
    engine = await get_knowledge_engine()
    
    # Check if entity exists
    existing = await engine.get_entity(entity_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Entity with ID {entity_id} not found")
    
    # Convert to domain entity
    domain_entity = entity_update.to_domain_entity(entity_id=entity_id)
    
    # Update entity
    success = await engine.update_entity(domain_entity)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update entity")
    
    # Get updated entity
    updated = await engine.get_entity(entity_id)
    return EntityResponse.from_domain_entity(updated)

@router.delete("/{entity_id}", response_model=Dict[str, Any])
async def delete_entity(entity_id: str):
    """
    Delete an entity by ID.
    """
    engine = await get_knowledge_engine()
    
    # Check if entity exists
    existing = await engine.get_entity(entity_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Entity with ID {entity_id} not found")
    
    # Delete entity
    success = await engine.delete_entity(entity_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete entity")
    
    return {"status": "success", "message": f"Entity {entity_id} deleted"}

@router.get("/", response_model=List[EntityResponse])
async def search_entities(
    query: str = Query(None, description="Search query"),
    entity_type: str = Query(None, description="Filter by entity type"),
    limit: int = Query(10, description="Maximum number of results to return")
):
    """
    Search for entities matching the query.
    """
    engine = await get_knowledge_engine()
    
    entities = await engine.search_entities(query, entity_type=entity_type, limit=limit)
    
    return [EntityResponse.from_domain_entity(entity) for entity in entities]

@router.post("/merge", response_model=EntityResponse)
@api_contract(
    title="Entity Merge API",
    endpoint="/api/v1/entities/merge",
    method="POST",
    request_schema={"source_entities": "list", "target_entity_name": "string", "merge_strategies": "object"}
)
@danger_zone(
    title="Entity Merging Operation",
    risk_level="medium",
    risks=["Data loss from merged entities", "Relationship conflicts", "Property conflicts"],
    mitigations=["Merge strategies", "Backup before merge", "Conflict resolution rules"],
    review_required=False
)
async def merge_entities(request: EntityMergeRequest):
    """
    Merge multiple entities into a single entity.
    
    This endpoint allows merging multiple entities with various strategies
    for handling field conflicts.
    """
    engine = await get_knowledge_engine()
    entity_manager = EntityManager(engine)
    
    merged_entity = await entity_manager.merge_entities(
        source_entities=request.source_entities,
        target_entity_name=request.target_entity_name,
        target_entity_type=request.target_entity_type,
        merge_strategies=request.merge_strategies
    )
    
    if not merged_entity:
        raise HTTPException(status_code=400, detail="Failed to merge entities")
    
    return EntityResponse.from_domain_entity(merged_entity)

@router.get("/duplicates", response_model=List[List[EntityResponse]])
async def find_duplicates(
    entity_type: str = Query(None, description="Filter by entity type"),
    confidence_threshold: float = Query(0.7, description="Minimum confidence threshold"),
    limit: int = Query(20, description="Maximum number of duplicate groups to return")
):
    """
    Find potential duplicate entities in the knowledge graph.
    """
    engine = await get_knowledge_engine()
    entity_manager = EntityManager(engine)
    
    duplicate_groups = await entity_manager.find_duplicate_entities(
        entity_type=entity_type,
        confidence_threshold=confidence_threshold,
        max_results=limit
    )
    
    return [
        [EntityResponse.from_domain_entity(entity) for entity in group]
        for group in duplicate_groups
    ]