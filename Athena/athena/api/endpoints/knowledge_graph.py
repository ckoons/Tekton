"""
Knowledge Graph REST API

Provides endpoints for Athena's knowledge graph functionality including:
- Entity management
- Relationship management
- Graph querying
- Path finding
"""

from typing import Dict, Any, List, Optional, Union
from fastapi import APIRouter, HTTPException, Depends

from ...core.engine import get_knowledge_engine, KnowledgeEngine
from ...core.entity import Entity
from ...core.relationship import Relationship

# Create router
router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"],
    responses={404: {"description": "Not found"}},
)

async def get_engine() -> KnowledgeEngine:
    """Dependency to get the knowledge engine."""
    return await get_knowledge_engine()

@router.get("/status")
async def get_status(engine: KnowledgeEngine = Depends(get_engine)) -> Dict[str, Any]:
    """Get the status of the knowledge graph."""
    return await engine.get_status()

# Entity endpoints

@router.post("/entities", response_model=Dict[str, str])
async def create_entity(
    entity_data: Dict[str, Any],
    engine: KnowledgeEngine = Depends(get_engine)
) -> Dict[str, str]:
    """Create a new entity in the knowledge graph."""
    try:
        entity = Entity(**entity_data)
        entity_id = await engine.add_entity(entity)
        return {"entity_id": entity_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating entity: {str(e)}")

@router.get("/entities/{entity_id}")
async def get_entity(
    entity_id: str,
    engine: KnowledgeEngine = Depends(get_engine)
) -> Dict[str, Any]:
    """Get an entity by ID."""
    entity = await engine.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    return entity.to_dict()

@router.put("/entities/{entity_id}")
async def update_entity(
    entity_id: str,
    entity_data: Dict[str, Any],
    engine: KnowledgeEngine = Depends(get_engine)
) -> Dict[str, str]:
    """Update an existing entity."""
    try:
        # Create entity with updated data but preserve ID
        entity_data["entity_id"] = entity_id
        entity = Entity.from_dict(entity_data)
        
        success = await engine.update_entity(entity)
        if not success:
            raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
            
        return {"entity_id": entity_id, "status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating entity: {str(e)}")

@router.delete("/entities/{entity_id}")
async def delete_entity(
    entity_id: str,
    engine: KnowledgeEngine = Depends(get_engine)
) -> Dict[str, str]:
    """Delete an entity."""
    success = await engine.delete_entity(entity_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    return {"entity_id": entity_id, "status": "deleted"}

@router.get("/entities")
async def search_entities(
    query: str,
    entity_type: Optional[str] = None,
    limit: int = 10,
    engine: KnowledgeEngine = Depends(get_engine)
) -> List[Dict[str, Any]]:
    """Search for entities matching a query."""
    entities = await engine.search_entities(query, entity_type, limit)
    return [entity.to_dict() for entity in entities]

# Relationship endpoints

@router.post("/relationships", response_model=Dict[str, str])
async def create_relationship(
    relationship_data: Dict[str, Any],
    engine: KnowledgeEngine = Depends(get_engine)
) -> Dict[str, str]:
    """Create a new relationship between entities."""
    try:
        relationship = Relationship(**relationship_data)
        relationship_id = await engine.add_relationship(relationship)
        return {"relationship_id": relationship_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating relationship: {str(e)}")

@router.get("/relationships/{relationship_id}")
async def get_relationship(
    relationship_id: str,
    engine: KnowledgeEngine = Depends(get_engine)
) -> Dict[str, Any]:
    """Get a relationship by ID."""
    relationship = await engine.get_relationship(relationship_id)
    if not relationship:
        raise HTTPException(status_code=404, detail=f"Relationship {relationship_id} not found")
    return relationship.to_dict()

@router.put("/relationships/{relationship_id}")
async def update_relationship(
    relationship_id: str,
    relationship_data: Dict[str, Any],
    engine: KnowledgeEngine = Depends(get_engine)
) -> Dict[str, str]:
    """Update an existing relationship."""
    try:
        # Create relationship with updated data but preserve ID
        relationship_data["relationship_id"] = relationship_id
        relationship = Relationship.from_dict(relationship_data)
        
        success = await engine.update_relationship(relationship)
        if not success:
            raise HTTPException(status_code=404, detail=f"Relationship {relationship_id} not found")
            
        return {"relationship_id": relationship_id, "status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating relationship: {str(e)}")

@router.delete("/relationships/{relationship_id}")
async def delete_relationship(
    relationship_id: str,
    engine: KnowledgeEngine = Depends(get_engine)
) -> Dict[str, str]:
    """Delete a relationship."""
    success = await engine.delete_relationship(relationship_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Relationship {relationship_id} not found")
    return {"relationship_id": relationship_id, "status": "deleted"}

@router.get("/entities/{entity_id}/relationships")
async def get_entity_relationships(
    entity_id: str,
    relationship_type: Optional[str] = None,
    direction: str = "both",
    engine: KnowledgeEngine = Depends(get_engine)
) -> List[Dict[str, Any]]:
    """Get relationships for an entity."""
    relationships = await engine.get_entity_relationships(entity_id, relationship_type, direction)
    
    if not relationships:
        return []
        
    # Convert to serializable format
    result = []
    for rel, entity in relationships:
        result.append({
            "relationship": rel.to_dict(),
            "entity": entity.to_dict()
        })
        
    return result

# Query endpoints

@router.post("/query")
async def execute_query(
    query_data: Dict[str, Any],
    engine: KnowledgeEngine = Depends(get_engine)
) -> List[Dict[str, Any]]:
    """Execute a raw Cypher query."""
    try:
        query = query_data.get("query", "")
        params = query_data.get("params", {})
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
            
        results = await engine.execute_query(query, params)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {str(e)}")

@router.get("/path")
async def find_path(
    source_id: str,
    target_id: str,
    max_depth: int = 3,
    engine: KnowledgeEngine = Depends(get_engine)
) -> List[List[Dict[str, Any]]]:
    """Find paths between two entities."""
    try:
        paths = await engine.find_path(source_id, target_id, max_depth)
        
        # Convert to serializable format
        result = []
        for path in paths:
            serialized_path = []
            for item in path:
                if isinstance(item, Entity):
                    serialized_path.append({"type": "entity", "data": item.to_dict()})
                elif isinstance(item, Relationship):
                    serialized_path.append({"type": "relationship", "data": item.to_dict()})
            result.append(serialized_path)
            
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error finding path: {str(e)}")

# Statistics endpoints

@router.get("/stats")
async def get_stats(
    engine: KnowledgeEngine = Depends(get_engine)
) -> Dict[str, Any]:
    """Get statistics about the knowledge graph."""
    entity_count = await engine.adapter.count_entities()
    relationship_count = await engine.adapter.count_relationships()
    
    return {
        "entity_count": entity_count,
        "relationship_count": relationship_count,
        "adapter_type": "neo4j" if hasattr(engine.adapter, "graph_db") else "memory"
    }