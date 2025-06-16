"""
Athena API Endpoints for Querying Knowledge Graph

Provides REST API endpoints for different query modes.
"""

from typing import Dict, List, Any, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Body

from tekton.core.query.modes import QueryMode, QueryParameters

from athena.api.models.query import (
    QueryRequest,
    QueryResponse
)
from athena.core.engine import get_knowledge_engine
from athena.core.query_engine import QueryEngine

router = APIRouter(prefix="/query", tags=["query"])

@router.post("/", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """
    Execute a query using the specified retrieval mode.
    
    Supports multiple query modes:
    - naive: Simple keyword-based search without advanced knowledge graph integration
    - local: Entity-focused retrieval that prioritizes relevant entities
    - global: Relationship-focused retrieval for understanding connections
    - hybrid: Combined entity and relationship retrieval
    - mix: Integrated graph and vector retrieval (most advanced)
    """
    engine = await get_knowledge_engine()
    query_engine = QueryEngine(engine)
    
    # Convert API request to internal params
    parameters = QueryParameters(
        mode=request.mode,
        response_type=request.response_type,
        max_results=request.max_results,
        similarity_threshold=request.similarity_threshold,
        max_tokens_per_chunk=request.max_tokens_per_chunk,
        max_tokens_entity_context=request.max_tokens_entity_context,
        max_tokens_relationship_context=request.max_tokens_relationship_context,
        relationship_depth=request.relationship_depth,
        conversation_history=request.conversation_history,
        only_return_context=request.only_return_context
    )
    
    try:
        result = await query_engine.query(request.question, parameters)
        
        return QueryResponse(
            question=request.question,
            mode=str(request.mode),
            answer=result.get("answer", ""),
            context=result.get("context_text", ""),
            results_count=result.get("results_count", 0),
            raw_results=result if request.include_raw_results else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

@router.get("/modes", response_model=List[Dict[str, str]])
async def get_available_query_modes():
    """
    Get information about available query modes.
    """
    mode_info = [
        {
            "id": "naive",
            "name": "Basic Search",
            "description": "Simple keyword-based search without advanced knowledge graph integration."
        },
        {
            "id": "local", 
            "name": "Entity-Focused",
            "description": "Entity-focused retrieval that prioritizes relevant entities and their properties."
        },
        {
            "id": "global",
            "name": "Relationship-Focused",
            "description": "Relationship-focused retrieval for understanding connections between entities."
        },
        {
            "id": "hybrid",
            "name": "Comprehensive",
            "description": "Combined entity and relationship retrieval for a balanced approach."
        },
        {
            "id": "mix",
            "name": "Advanced Integration",
            "description": "Integrated graph and vector retrieval using both knowledge graph and semantic search."
        }
    ]
    
    return mode_info