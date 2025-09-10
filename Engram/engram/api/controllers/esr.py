"""
ESR (Encoding Storage Retrieval) HTTP API Controllers.

This module provides HTTP endpoints for ESR memory operations,
wrapping the MCP tools for REST access.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

# Import ESR MCP tools
try:
    from engram.core.mcp.esr_tools import (
        esr_store_thought,
        esr_recall_thought,
        esr_search_similar,
        esr_build_context,
        esr_create_association,
        esr_get_metabolism_status,
        esr_trigger_reflection,
        esr_get_namespaces
    )
    ESR_AVAILABLE = True
except ImportError as e:
    ESR_AVAILABLE = False
    logger = logging.getLogger("engram.api.esr")
    logger.warning(f"ESR tools not available: {e}")

logger = logging.getLogger("engram.api.esr")

# Create router
router = APIRouter(prefix="/api/esr", tags=["ESR Memory"])


# Pydantic models for requests/responses

class StoreThoughtRequest(BaseModel):
    """Request model for storing a thought."""
    content: str = Field(..., description="The thought content to store")
    thought_type: str = Field("IDEA", description="Type of thought")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context metadata")
    associations: Optional[List[str]] = Field(None, description="Associated memory IDs")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence level")
    ci_id: str = Field("system", description="CI identifier")


class RecallThoughtRequest(BaseModel):
    """Request model for recalling a thought."""
    memory_id: str = Field(..., description="The memory ID to recall")
    ci_id: str = Field("system", description="CI identifier")


class SearchSimilarRequest(BaseModel):
    """Request model for searching similar thoughts."""
    query: str = Field(..., description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum results")
    thought_type: Optional[str] = Field(None, description="Filter by thought type")
    min_confidence: float = Field(0.5, ge=0.0, le=1.0, description="Minimum confidence")
    ci_id: str = Field("system", description="CI identifier")


class BuildContextRequest(BaseModel):
    """Request model for building context."""
    topic: str = Field(..., description="Topic to build context for")
    depth: int = Field(3, ge=1, le=10, description="Depth of context")
    max_items: int = Field(20, ge=1, le=100, description="Maximum items")
    ci_id: str = Field("system", description="CI identifier")


class CreateAssociationRequest(BaseModel):
    """Request model for creating associations."""
    from_memory: str = Field(..., description="Source memory ID")
    to_memory: str = Field(..., description="Target memory ID")
    association_type: str = Field("related", description="Type of association")
    strength: float = Field(1.0, ge=0.0, le=1.0, description="Association strength")
    ci_id: str = Field("system", description="CI identifier")


class TriggerReflectionRequest(BaseModel):
    """Request model for triggering reflection."""
    ci_id: str = Field("system", description="CI identifier")
    reason: str = Field("explicit_request", description="Reason for reflection")


# API Endpoints

@router.post("/store")
async def store_thought(request: StoreThoughtRequest):
    """Store a thought in the ESR memory system."""
    if not ESR_AVAILABLE:
        raise HTTPException(status_code=503, detail="ESR system not available")
    
    try:
        result = await esr_store_thought(
            content=request.content,
            thought_type=request.thought_type,
            context=request.context,
            associations=request.associations,
            confidence=request.confidence,
            ci_id=request.ci_id
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Error storing thought: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recall/{memory_id}")
async def recall_thought(
    memory_id: str,
    ci_id: str = Query("system", description="CI identifier")
):
    """Recall a specific thought from memory."""
    if not ESR_AVAILABLE:
        raise HTTPException(status_code=503, detail="ESR system not available")
    
    try:
        result = await esr_recall_thought(memory_id=memory_id, ci_id=ci_id)
        
        if result["status"] == "not_found":
            raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")
        elif result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recalling thought: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_similar(request: SearchSimilarRequest):
    """Search for similar thoughts in memory."""
    if not ESR_AVAILABLE:
        raise HTTPException(status_code=503, detail="ESR system not available")
    
    try:
        result = await esr_search_similar(
            query=request.query,
            limit=request.limit,
            thought_type=request.thought_type,
            min_confidence=request.min_confidence,
            ci_id=request.ci_id
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching thoughts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/context")
async def build_context(request: BuildContextRequest):
    """Build context around a topic."""
    if not ESR_AVAILABLE:
        raise HTTPException(status_code=503, detail="ESR system not available")
    
    try:
        result = await esr_build_context(
            topic=request.topic,
            depth=request.depth,
            max_items=request.max_items,
            ci_id=request.ci_id
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Error building context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/associate")
async def create_association(request: CreateAssociationRequest):
    """Create an association between memories."""
    if not ESR_AVAILABLE:
        raise HTTPException(status_code=503, detail="ESR system not available")
    
    try:
        result = await esr_create_association(
            from_memory=request.from_memory,
            to_memory=request.to_memory,
            association_type=request.association_type,
            strength=request.strength,
            ci_id=request.ci_id
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating association: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metabolism/status")
async def get_metabolism_status(
    ci_id: str = Query("system", description="CI identifier")
):
    """Get the status of memory metabolism."""
    if not ESR_AVAILABLE:
        raise HTTPException(status_code=503, detail="ESR system not available")
    
    try:
        result = await esr_get_metabolism_status(ci_id=ci_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting metabolism status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reflect")
async def trigger_reflection(request: TriggerReflectionRequest):
    """Trigger memory reflection for a CI."""
    if not ESR_AVAILABLE:
        raise HTTPException(status_code=503, detail="ESR system not available")
    
    try:
        result = await esr_trigger_reflection(
            ci_id=request.ci_id,
            reason=request.reason
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Error triggering reflection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/namespaces")
async def get_namespaces():
    """Get list of available namespaces."""
    if not ESR_AVAILABLE:
        raise HTTPException(status_code=503, detail="ESR system not available")
    
    try:
        result = await esr_get_namespaces()
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting namespaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_esr_status():
    """Get ESR system status."""
    return {
        "status": "available" if ESR_AVAILABLE else "unavailable",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/store",
            "/recall/{memory_id}",
            "/search",
            "/context",
            "/associate",
            "/metabolism/status",
            "/reflect",
            "/namespaces"
        ]
    }