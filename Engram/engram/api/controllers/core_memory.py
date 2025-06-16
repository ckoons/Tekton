"""
Core Memory Controllers - Handles main memory operations

This module provides the API routes for core memory operations.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any

from fastapi import APIRouter, Body, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from engram.core.memory import MemoryService
from engram.api.models import MemoryQuery, MemoryStore, MemoryMultiQuery
from engram.api.dependencies import get_memory_service

# Configure logging
logger = logging.getLogger("engram.api.controllers.core_memory")

# Create router
router = APIRouter(prefix="/memory", tags=["Core Memory API"])


@router.post("/query")
async def query_memory(
    query_data: MemoryQuery,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Query memory for relevant information."""
    try:
        results = await memory_service.search(
            query=query_data.query, 
            namespace=query_data.namespace, 
            limit=query_data.limit
        )
        
        # Add query timestamp
        return {
            **results,
            "query": query_data.query,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error querying memory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to query memory: {str(e)}")


@router.post("/store")
async def store_memory(
    memory_data: MemoryStore,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Store a new memory."""
    try:
        # Store the memory
        success = await memory_service.add(
            content=memory_data.value,
            namespace=memory_data.namespace,
            metadata=memory_data.metadata or {"key": memory_data.key}
        )
        
        return {
            "success": success,
            "key": memory_data.key,
            "namespace": memory_data.namespace,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store memory: {str(e)}")


@router.post("/store_conversation")
async def store_conversation(
    conversation: List[Dict[str, str]] = Body(...),
    namespace: str = Query("conversations"),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Store a complete conversation."""
    try:
        # Generate a unique conversation ID
        conversation_id = f"conversation_{int(datetime.now().timestamp())}"
        
        # Store the conversation
        success = await memory_service.add(
            content=conversation,
            namespace=namespace,
            metadata={"conversation_id": conversation_id}
        )
        
        return {
            "success": success,
            "conversation_id": conversation_id,
            "message_count": len(conversation),
            "namespace": namespace,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error storing conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store conversation: {str(e)}")


@router.post("/context")
async def get_context(
    query_data: MemoryMultiQuery,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get formatted memory context across multiple namespaces."""
    try:
        # Get formatted context
        context = await memory_service.get_relevant_context(
            query=query_data.query,
            namespaces=query_data.namespaces,
            limit=query_data.limit
        )
        
        return {
            "context": context,
            "query": query_data.query,
            "namespaces": query_data.namespaces,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get context: {str(e)}")


@router.post("/clear/{namespace}")
async def clear_namespace(
    namespace: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Clear all memories in a namespace."""
    try:
        success = await memory_service.clear_namespace(namespace)
        
        return {
            "success": success,
            "namespace": namespace,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing namespace: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear namespace: {str(e)}")