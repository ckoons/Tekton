"""
Clients Controllers - Endpoints for client management

This module provides HTTP endpoints for managing clients.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from engram.api.dependencies import get_memory_manager

# Configure logging
logger = logging.getLogger("engram.api.controllers.clients")

# Create router
router = APIRouter(prefix="/clients", tags=["Client Management API"])


@router.get("/list")
async def list_clients(memory_manager = Depends(get_memory_manager)):
    """List all active clients."""
    if memory_manager is None:
        raise HTTPException(status_code=500, detail="Memory manager not initialized")
    
    try:
        clients = await memory_manager.list_clients()
        return {"clients": clients}
    except Exception as e:
        logger.error(f"Error listing clients: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list clients: {str(e)}")


@router.get("/status/{client_id}")
async def client_status(client_id: str, memory_manager = Depends(get_memory_manager)):
    """Get status for a specific client."""
    if memory_manager is None:
        raise HTTPException(status_code=500, detail="Memory manager not initialized")
    
    try:
        clients = await memory_manager.list_clients()
        for client in clients:
            if client["client_id"] == client_id:
                return client
        
        raise HTTPException(status_code=404, detail=f"Client '{client_id}' not found")
    except Exception as e:
        logger.error(f"Error getting client status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get client status: {str(e)}")


@router.post("/cleanup")
async def cleanup_idle_clients(
    idle_threshold: int = 3600,
    memory_manager = Depends(get_memory_manager)
):
    """Clean up clients that have been idle for a specified time."""
    if memory_manager is None:
        raise HTTPException(status_code=500, detail="Memory manager not initialized")
    
    try:
        count = await memory_manager.cleanup_idle_clients(idle_threshold)
        return {"cleaned_clients": count}
    except Exception as e:
        logger.error(f"Error cleaning up idle clients: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clean up idle clients: {str(e)}")