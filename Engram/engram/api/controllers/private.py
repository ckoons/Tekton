"""
Private Memory Controllers - Endpoints for handling private memories

This module provides HTTP endpoints for managing private memories.
"""

import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from engram.core.memory import MemoryService
from engram.api.dependencies import get_memory_service

# Configure logging
logger = logging.getLogger("engram.api.controllers.private")

# Create router
router = APIRouter(prefix="/http", tags=["Private Memory API"])


@router.get("/keep")
async def keep_memory(
    memory_id: str, 
    days: int = 30,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Keep a memory for a specified number of days."""
    try:
        success = await memory_service.keep_memory(memory_id, days)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error keeping memory: {e}")
        return {"status": "error", "message": f"Failed to keep memory: {str(e)}"}


@router.get("/private")
async def store_private(
    content: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Store a private memory."""
    try:
        memory_id, success = await memory_service.add_private(content)
        if success:
            return {"success": True, "memory_id": memory_id}
        else:
            return {"success": False, "message": "Failed to store private memory"}
    except Exception as e:
        logger.error(f"Error storing private memory: {e}")
        return {"status": "error", "message": f"Failed to store private memory: {str(e)}"}


@router.get("/private/get")
async def get_private(
    memory_id: str, 
    use_emergency: bool = False,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get a specific private memory."""
    try:
        memory = await memory_service.get_private(memory_id, use_emergency)
        if memory:
            return {"success": True, "memory": memory}
        else:
            return {"success": False, "message": "Failed to retrieve private memory"}
    except Exception as e:
        logger.error(f"Error retrieving private memory: {e}")
        return {"status": "error", "message": f"Failed to retrieve private memory: {str(e)}"}


@router.get("/private/list")
async def list_private(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """List all private memories."""
    try:
        memories = await memory_service.list_private()
        return {"success": True, "memories": memories}
    except Exception as e:
        logger.error(f"Error listing private memories: {e}")
        return {"status": "error", "message": f"Failed to list private memories: {str(e)}"}


@router.get("/private/delete")
async def delete_private(
    memory_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Delete a private memory."""
    try:
        success = await memory_service.delete_private(memory_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error deleting private memory: {e}")
        return {"status": "error", "message": f"Failed to delete private memory: {str(e)}"}