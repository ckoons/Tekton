"""
Compartment Controllers - Endpoints for memory compartment operations

This module provides HTTP endpoints for managing memory compartments.
"""

import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from engram.core.memory import MemoryService
from engram.api.dependencies import get_memory_service

# Configure logging
logger = logging.getLogger("engram.api.controllers.compartments")

# Create router
router = APIRouter(prefix="/http", tags=["Compartment API"])


@router.get("/compartment/create")
async def create_compartment(
    name: str, 
    description: str = None, 
    parent: str = None,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Create a new memory compartment."""
    try:
        compartment_id = await memory_service.create_compartment(name, description, parent)
        if compartment_id:
            return {"success": True, "compartment_id": compartment_id}
        else:
            return {"success": False, "message": "Failed to create compartment"}
    except Exception as e:
        logger.error(f"Error creating compartment: {e}")
        return {"status": "error", "message": f"Failed to create compartment: {str(e)}"}


@router.get("/compartment/store")
async def store_in_compartment(
    compartment: str, 
    content: str, 
    key: str = "memory",
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Store content in a specific compartment."""
    try:
        # Find compartment ID if a name was provided
        compartment_id = None
        
        # First check if it's already an ID
        if compartment in memory_service.compartments:
            compartment_id = compartment
        else:
            # Look for compartment by name
            for c_id, c_data in memory_service.compartments.items():
                if c_data.get("name", "").lower() == compartment.lower():
                    compartment_id = c_id
                    break
        
        if not compartment_id:
            return {"success": False, "message": f"Compartment '{compartment}' not found"}
        
        # Store in compartment namespace
        namespace = f"compartment-{compartment_id}"
        success = await memory_service.add(
            content=content,
            namespace=namespace,
            metadata={"key": key}
        )
        
        # Also activate the compartment
        await memory_service.activate_compartment(compartment_id)
        
        return {"success": success, "compartment_id": compartment_id}
    except Exception as e:
        logger.error(f"Error storing in compartment: {e}")
        return {"status": "error", "message": f"Failed to store in compartment: {str(e)}"}


@router.get("/compartment/activate")
async def activate_compartment(
    compartment: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Activate a compartment to include in automatic context retrieval."""
    try:
        success = await memory_service.activate_compartment(compartment)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error activating compartment: {e}")
        return {"status": "error", "message": f"Failed to activate compartment: {str(e)}"}


@router.get("/compartment/deactivate")
async def deactivate_compartment(
    compartment: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Deactivate a compartment to exclude from automatic context retrieval."""
    try:
        success = await memory_service.deactivate_compartment(compartment)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error deactivating compartment: {e}")
        return {"status": "error", "message": f"Failed to deactivate compartment: {str(e)}"}


@router.get("/compartment/list")
async def list_compartments(
    include_expired: bool = False,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """List all compartments."""
    try:
        compartments = await memory_service.list_compartments(include_expired)
        return {"compartments": compartments, "count": len(compartments)}
    except Exception as e:
        logger.error(f"Error listing compartments: {e}")
        return {"status": "error", "message": f"Failed to list compartments: {str(e)}"}


@router.get("/compartment/expire")
async def set_compartment_expiration(
    compartment_id: str, 
    days: int = None,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Set expiration for a compartment in days."""
    try:
        success = await memory_service.set_compartment_expiration(compartment_id, days)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error setting compartment expiration: {e}")
        return {"status": "error", "message": f"Failed to set compartment expiration: {str(e)}"}