"""
HTTP Wrapper Controllers - Simple HTTP endpoints for memory operations

This module provides simplified HTTP GET endpoints for memory operations.
"""

import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from engram.core.memory import MemoryService
from engram.api.dependencies import get_memory_service

# Configure logging
logger = logging.getLogger("engram.api.controllers.http_wrapper")

# Create router
router = APIRouter(prefix="/http", tags=["HTTP Wrapper API"])


@router.get("/store")
async def http_store_memory(
    key: str,
    value: str,
    namespace: str = "conversations",
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Store a memory in the specified namespace."""
    try:
        # Store the memory
        success = await memory_service.add(
            content=value,
            namespace=namespace,
            metadata={"key": key}
        )
        
        return {
            "success": success,
            "key": key,
            "namespace": namespace,
        }
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        return {"status": "error", "message": f"Failed to store memory: {str(e)}"}


@router.get("/thinking")
async def http_store_thinking(
    thought: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Store a thought in the thinking namespace."""
    try:
        success = await memory_service.add(
            content=thought,
            namespace="thinking",
            metadata={"key": "thought"}
        )
        return {
            "success": success,
            "key": "thought",
            "namespace": "thinking",
        }
    except Exception as e:
        logger.error(f"Error storing thought: {e}")
        return {"status": "error", "message": f"Failed to store thought: {str(e)}"}


@router.get("/longterm")
async def http_store_longterm(
    info: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Store important information in the longterm namespace."""
    try:
        success = await memory_service.add(
            content=info,
            namespace="longterm", 
            metadata={"key": "important"}
        )
        return {
            "success": success,
            "key": "important",
            "namespace": "longterm",
        }
    except Exception as e:
        logger.error(f"Error storing longterm memory: {e}")
        return {"status": "error", "message": f"Failed to store longterm memory: {str(e)}"}


@router.get("/query")
async def http_query_memory(
    query: str,
    namespace: str = "conversations",
    limit: int = 5,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Query memory for relevant information."""
    try:
        # Search for memories
        results = await memory_service.search(
            query=query,
            namespace=namespace,
            limit=limit
        )
        
        return results
    except Exception as e:
        logger.error(f"Error querying memory: {e}")
        return {"status": "error", "message": f"Failed to query memory: {str(e)}"}


@router.get("/context")
async def http_get_context(
    query: str,
    include_thinking: bool = True,
    limit: int = 3,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get formatted context from multiple namespaces."""
    try:
        # Determine which namespaces to include
        namespaces = ["conversations", "longterm"]
        if include_thinking:
            namespaces.append("thinking")
        
        # Get formatted context
        context = await memory_service.get_relevant_context(
            query=query,
            namespaces=namespaces,
            limit=limit
        )
        
        return {"context": context}
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        return {"status": "error", "message": f"Failed to get context: {str(e)}"}


@router.get("/clear/{namespace}")
async def http_clear_namespace(
    namespace: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Clear all memories in a namespace."""
    try:
        success = await memory_service.clear_namespace(namespace)
        return {"success": success, "namespace": namespace}
    except Exception as e:
        logger.error(f"Error clearing namespace: {e}")
        return {"status": "error", "message": f"Failed to clear namespace: {str(e)}"}


@router.get("/write")
async def write_session_memory(
    content: str, 
    metadata: str = None,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Write a memory to the session namespace for persistence."""
    try:
        # Parse metadata if provided
        meta_dict = json.loads(metadata) if metadata else None
        
        success = await memory_service.write_session_memory(content, meta_dict)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error writing session memory: {e}")
        return {"status": "error", "message": f"Failed to write session memory: {str(e)}"}


@router.get("/load")
async def load_session_memory(
    limit: int = 1,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Load previous session memory."""
    try:
        # Search for the most recent session memories
        results = await memory_service.search(
            query="",
            namespace="session",
            limit=limit
        )
        
        if results.get("count", 0) > 0:
            return {
                "success": True,
                "content": [r.get("content", "") for r in results.get("results", [])],
                "metadata": [r.get("metadata", {}) for r in results.get("results", [])]
            }
        else:
            return {"success": False, "message": "No session memory found"}
    except Exception as e:
        logger.error(f"Error loading session memory: {e}")
        return {"status": "error", "message": f"Failed to load session memory: {str(e)}"}