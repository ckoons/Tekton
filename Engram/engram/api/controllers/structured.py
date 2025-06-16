"""
Structured Memory Controllers - Endpoints for structured memory operations

This module provides HTTP endpoints for managing structured memories.
"""

import json
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from engram.core.structured_memory import StructuredMemory
from engram.api.dependencies import get_structured_memory

# Configure logging
logger = logging.getLogger("engram.api.controllers.structured")

# Create router
router = APIRouter(prefix="/structured", tags=["Structured Memory API"])


@router.get("/add")
async def add_structured_memory(
    content: str,
    category: str = "session",
    importance: int = None,
    tags: str = None,
    metadata: str = None,
    structured_memory: StructuredMemory = Depends(get_structured_memory)
):
    """Add a memory to the structured memory system."""
    if structured_memory is None:
        return {"status": "error", "message": "Structured memory service not initialized"}
    
    try:
        # Parse metadata and tags if provided
        meta_dict = json.loads(metadata) if metadata else None
        tags_list = json.loads(tags) if tags else None
        
        # Add memory
        memory_id = await structured_memory.add_memory(
            content=content,
            category=category,
            importance=importance,
            metadata=meta_dict,
            tags=tags_list
        )
        
        if memory_id:
            return {"success": True, "memory_id": memory_id}
        else:
            return {"success": False, "message": "Failed to add memory"}
    except Exception as e:
        logger.error(f"Error adding structured memory: {e}")
        return {"status": "error", "message": f"Failed to add structured memory: {str(e)}"}


@router.get("/auto")
async def add_auto_categorized_memory(
    content: str,
    manual_category: str = None,
    manual_importance: int = None,
    manual_tags: str = None,
    metadata: str = None,
    structured_memory: StructuredMemory = Depends(get_structured_memory)
):
    """Add a memory with automatic categorization."""
    if structured_memory is None:
        return {"status": "error", "message": "Structured memory service not initialized"}
    
    try:
        # Parse metadata and tags if provided
        meta_dict = json.loads(metadata) if metadata else None
        tags_list = json.loads(manual_tags) if manual_tags else None
        
        # Parse importance if provided
        importance = int(manual_importance) if manual_importance is not None else None
        
        # Add auto-categorized memory
        memory_id = await structured_memory.add_auto_categorized_memory(
            content=content,
            manual_category=manual_category,
            manual_importance=importance,
            manual_tags=tags_list,
            metadata=meta_dict
        )
        
        if memory_id:
            return {"success": True, "memory_id": memory_id}
        else:
            return {"success": False, "message": "Failed to add memory"}
    except Exception as e:
        logger.error(f"Error adding auto-categorized memory: {e}")
        return {"status": "error", "message": f"Failed to add auto-categorized memory: {str(e)}"}


@router.get("/get")
async def get_structured_memory(
    memory_id: str,
    structured_memory: StructuredMemory = Depends(get_structured_memory)
):
    """Get a specific memory by ID."""
    if structured_memory is None:
        return {"status": "error", "message": "Structured memory service not initialized"}
    
    try:
        memory = await structured_memory.get_memory(memory_id)
        if memory:
            return {"success": True, "memory": memory}
        else:
            return {"success": False, "message": "Memory not found"}
    except Exception as e:
        logger.error(f"Error getting structured memory: {e}")
        return {"status": "error", "message": f"Failed to get structured memory: {str(e)}"}


@router.get("/search")
async def search_structured_memory(
    query: str = None,
    categories: str = None,
    tags: str = None,
    min_importance: int = 1,
    limit: int = 10,
    sort_by: str = "importance",
    structured_memory: StructuredMemory = Depends(get_structured_memory)
):
    """Search for memories."""
    if structured_memory is None:
        return {"status": "error", "message": "Structured memory service not initialized"}
    
    try:
        # Parse categories and tags
        categories_list = json.loads(categories) if categories else None
        tags_list = json.loads(tags) if tags else None
        
        # Search memories
        memories = await structured_memory.search_memories(
            query=query,
            categories=categories_list,
            tags=tags_list,
            min_importance=min_importance,
            limit=limit,
            sort_by=sort_by
        )
        
        return {"success": True, "results": memories, "count": len(memories)}
    except Exception as e:
        logger.error(f"Error searching structured memories: {e}")
        return {"status": "error", "message": f"Failed to search structured memories: {str(e)}"}


@router.get("/digest")
async def get_memory_digest(
    max_memories: int = 10,
    include_private: bool = False,
    categories: str = None,
    structured_memory: StructuredMemory = Depends(get_structured_memory)
):
    """Get a memory digest."""
    if structured_memory is None:
        return {"status": "error", "message": "Structured memory service not initialized"}
    
    try:
        # Parse categories
        categories_list = json.loads(categories) if categories else None
        
        # Get digest
        digest = await structured_memory.get_memory_digest(
            categories=categories_list,
            max_memories=max_memories,
            include_private=include_private
        )
        
        return {"success": True, "digest": digest}
    except Exception as e:
        logger.error(f"Error getting memory digest: {e}")
        return {"status": "error", "message": f"Failed to get memory digest: {str(e)}"}


@router.get("/delete")
async def delete_structured_memory(
    memory_id: str,
    structured_memory: StructuredMemory = Depends(get_structured_memory)
):
    """Delete a memory."""
    if structured_memory is None:
        return {"status": "error", "message": "Structured memory service not initialized"}
    
    try:
        success = await structured_memory.delete_memory(memory_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error deleting structured memory: {e}")
        return {"status": "error", "message": f"Failed to delete structured memory: {str(e)}"}


@router.get("/importance")
async def set_memory_importance(
    memory_id: str, 
    importance: int,
    structured_memory: StructuredMemory = Depends(get_structured_memory)
):
    """Update the importance of a memory."""
    if structured_memory is None:
        return {"status": "error", "message": "Structured memory service not initialized"}
    
    try:
        success = await structured_memory.set_memory_importance(memory_id, importance)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error updating memory importance: {e}")
        return {"status": "error", "message": f"Failed to update memory importance: {str(e)}"}


@router.get("/context")
async def get_context_memories(
    text: str, 
    max_memories: int = 5,
    structured_memory: StructuredMemory = Depends(get_structured_memory)
):
    """Get memories relevant to context."""
    if structured_memory is None:
        return {"status": "error", "message": "Structured memory service not initialized"}
    
    try:
        memories = await structured_memory.get_context_memories(text, max_memories)
        return {"success": True, "memories": memories, "count": len(memories)}
    except Exception as e:
        logger.error(f"Error getting context memories: {e}")
        return {"status": "error", "message": f"Failed to get context memories: {str(e)}"}