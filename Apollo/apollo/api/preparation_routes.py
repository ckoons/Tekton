"""
API Routes for Apollo Preparation System.

This module implements the HTTP routes for the Apollo Preparation API,
handling Context Brief management, memory operations, and landmark queries.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

# Add parent directory to path for imports
import sys
import os
apollo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(apollo_root))

from apollo.core.preparation.context_brief import (
    ContextBriefManager, MemoryItem, MemoryType, CIType
)
from apollo.core.preparation.brief_presenter import BriefPresenter
from apollo.core.preparation.memory_extractor import MemoryExtractor

# Configure logging
logger = logging.getLogger("apollo.api.preparation_routes")

# Create API router
preparation_router = APIRouter(prefix="/api/preparation", tags=["preparation"])

# Global instance
brief_manager: Optional[ContextBriefManager] = None


def get_brief_manager():
    """Get or create the Context Brief Manager instance."""
    global brief_manager
    if brief_manager is None:
        storage_dir = Path("/Apollo/apollo/data/preparation")
        storage_dir.mkdir(parents=True, exist_ok=True)
        brief_manager = ContextBriefManager(storage_dir=storage_dir, enable_landmarks=True)
        logger.info("Created Context Brief Manager instance")
    return brief_manager


# Request/Response Models
class MemorySearchRequest(BaseModel):
    """Request model for memory search"""
    query: str = Field(..., description="Search query string")
    ci_name: Optional[str] = Field(None, description="Filter by CI name")
    memory_type: Optional[str] = Field(None, description="Filter by memory type")
    max_results: int = Field(20, description="Maximum results to return")


class BriefGenerationRequest(BaseModel):
    """Request model for Context Brief generation"""
    ci_name: str = Field(..., description="CI requesting the brief")
    message: str = Field("General context", description="Context message for relevance")
    max_tokens: int = Field(2000, description="Maximum tokens for brief")


class MemoryResponse(BaseModel):
    """Response model for memory data"""
    memories: List[Dict[str, Any]]
    total: int
    total_tokens: int


class LandmarkAnalysisResponse(BaseModel):
    """Response model for landmark analysis"""
    landmarks: Dict[str, Any]
    relationships_created: int


# Memory Routes

@preparation_router.get("/memories", response_model=MemoryResponse)
async def get_memories(
    ci_name: Optional[str] = Query(None, description="Filter by CI name"),
    memory_type: Optional[str] = Query(None, description="Filter by memory type"),
    limit: int = Query(50, description="Maximum memories to return"),
    manager: ContextBriefManager = Depends(get_brief_manager)
):
    """
    Get memories from the catalog.
    
    Returns memories with optional filtering by CI and type.
    """
    try:
        # Get all memories
        all_memories = manager.get_all_memories()
        
        # Filter by CI if specified
        if ci_name:
            all_memories = [m for m in all_memories if m.ci_source == ci_name]
        
        # Filter by type if specified
        if memory_type:
            try:
                mem_type = MemoryType(memory_type.lower())
                all_memories = [m for m in all_memories if m.type == mem_type]
            except ValueError:
                logger.warning(f"Invalid memory type: {memory_type}")
        
        # Limit results
        memories = all_memories[:limit]
        
        # Calculate total tokens
        total_tokens = sum(m.tokens for m in memories)
        
        # Convert to dict format
        memory_data = [m.to_dict() for m in memories]
        
        return MemoryResponse(
            memories=memory_data,
            total=len(memories),
            total_tokens=total_tokens
        )
        
    except Exception as e:
        logger.error(f"Error retrieving memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@preparation_router.post("/search")
async def search_memories(
    request: MemorySearchRequest,
    manager: ContextBriefManager = Depends(get_brief_manager)
):
    """
    Search memories by query.
    
    Returns memories matching the search query.
    """
    try:
        # Parse memory type if provided
        memory_type = None
        if request.memory_type:
            try:
                memory_type = MemoryType(request.memory_type.lower())
            except ValueError:
                logger.warning(f"Invalid memory type: {request.memory_type}")
        
        # Search memories
        results = manager.search_memories(
            query=request.query,
            ci_name=request.ci_name,
            memory_type=memory_type,
            max_results=request.max_results
        )
        
        # Convert to dict format
        memory_data = [m.to_dict() for m in results]
        
        return memory_data
        
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@preparation_router.post("/brief")
async def generate_brief(
    request: BriefGenerationRequest,
    manager: ContextBriefManager = Depends(get_brief_manager)
):
    """
    Generate a Context Brief for a CI.
    
    Returns a formatted Context Brief with relevant memories.
    """
    try:
        # Generate the brief
        brief = manager.prepare_context_brief(
            ci_name=request.ci_name,
            message=request.message,
            max_tokens=request.max_tokens
        )
        
        # Get token usage
        tokens_used = brief.get("tokens_used", 0)
        
        return {
            "content": brief.get("brief", ""),
            "tokens_used": tokens_used,
            "memory_count": brief.get("memory_count", 0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating brief: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@preparation_router.post("/analyze", response_model=LandmarkAnalysisResponse)
async def analyze_relationships(
    manager: ContextBriefManager = Depends(get_brief_manager)
):
    """
    Analyze and create memory relationships.
    
    Creates landmark relationships between memories in the knowledge graph.
    """
    try:
        # Analyze relationships
        relationships_created = manager.analyze_relationships()
        
        # Get landmark stats
        landmarks = manager.get_landmarks()
        
        # Count nodes and relationships
        node_count = len(landmarks)
        
        # Get relationship count from landmark manager
        relationship_count = 0
        if manager.landmark_manager:
            relationships = manager.landmark_manager.relationships
            relationship_count = len(relationships)
        
        return LandmarkAnalysisResponse(
            landmarks={
                "nodes": node_count,
                "relationships": relationship_count
            },
            relationships_created=relationships_created
        )
        
    except Exception as e:
        logger.error(f"Error analyzing relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@preparation_router.post("/memory")
async def store_memory(
    memory_data: Dict[str, Any] = Body(...),
    manager: ContextBriefManager = Depends(get_brief_manager)
):
    """
    Store a new memory.
    
    Adds a memory to the catalog and creates a landmark.
    """
    try:
        # Create MemoryItem from data
        memory = MemoryItem(
            id=memory_data.get("id", f"mem_{datetime.now().timestamp()}"),
            timestamp=datetime.fromisoformat(memory_data.get("timestamp", datetime.now().isoformat())),
            ci_source=memory_data.get("ci_source", "unknown"),
            ci_type=CIType(memory_data.get("ci_type", "greek")),
            type=MemoryType(memory_data.get("type", "insight")),
            summary=memory_data.get("summary", ""),
            content=memory_data.get("content", ""),
            tokens=memory_data.get("tokens", 0),
            relevance_tags=memory_data.get("relevance_tags", []),
            priority=memory_data.get("priority", 5)
        )
        
        # Add memory
        manager.add_memory(memory)
        
        # Save
        manager.save()
        
        return {"message": f"Memory {memory.id} stored successfully"}
        
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@preparation_router.get("/landmarks")
async def get_landmarks(
    ci_name: Optional[str] = Query(None, description="Filter by CI name"),
    include_relationships: bool = Query(False, description="Include relationships"),
    manager: ContextBriefManager = Depends(get_brief_manager)
):
    """
    Get memory landmarks from the knowledge graph.
    
    Returns landmark nodes with optional relationships.
    """
    try:
        # Get landmarks
        landmarks = manager.get_landmarks(
            ci_name=ci_name,
            include_relationships=include_relationships
        )
        
        return landmarks
        
    except Exception as e:
        logger.error(f"Error retrieving landmarks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@preparation_router.get("/statistics")
async def get_statistics(
    manager: ContextBriefManager = Depends(get_brief_manager)
):
    """
    Get memory catalog statistics.
    
    Returns statistics about the memory catalog.
    """
    try:
        stats = manager.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))