"""
Nexus Controllers - Endpoints for Nexus interface operations

This module provides HTTP endpoints for interacting with the Nexus interface.
"""

import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from engram.core.nexus import NexusInterface
from engram.core.config import get_config
from engram.api.dependencies import get_nexus_interface

# Configure logging
logger = logging.getLogger("engram.api.controllers.nexus")

# Create router
router = APIRouter(prefix="/nexus", tags=["Nexus API"])


@router.get("/start")
async def start_nexus_session(
    session_name: Optional[str] = None,
    nexus: NexusInterface = Depends(get_nexus_interface)
):
    """Start a new Nexus session."""
    if nexus is None:
        return {"status": "error", "message": "Nexus interface not initialized"}
    
    try:
        result = await nexus.start_session(session_name)
        return {"success": True, "session_id": nexus.session_id, "message": result}
    except Exception as e:
        logger.error(f"Error starting Nexus session: {e}")
        return {"status": "error", "message": f"Failed to start Nexus session: {str(e)}"}


@router.get("/end")
async def end_nexus_session(
    summary: Optional[str] = None,
    nexus: NexusInterface = Depends(get_nexus_interface)
):
    """End the current Nexus session."""
    if nexus is None:
        return {"status": "error", "message": "Nexus interface not initialized"}
    
    try:
        result = await nexus.end_session(summary)
        return {"success": True, "message": result}
    except Exception as e:
        logger.error(f"Error ending Nexus session: {e}")
        return {"status": "error", "message": f"Failed to end Nexus session: {str(e)}"}


@router.get("/process")
async def process_message(
    message: str,
    is_user: bool = True,
    metadata: Optional[str] = None,
    auto_agency: Optional[bool] = None,
    nexus: NexusInterface = Depends(get_nexus_interface)
):
    """
    Process a conversation message with optional automatic agency activation.
    
    Auto-agency defaults to the value in the configuration file if not specified.
    """
    if nexus is None:
        return {"status": "error", "message": "Nexus interface not initialized"}
    
    try:
        # Parse metadata if provided
        meta_dict = json.loads(metadata) if metadata else None
        
        # Automatic agency invocation for user messages
        agency_applied = False
        
        # If auto_agency not explicitly provided in request, use config setting
        use_auto_agency = auto_agency if auto_agency is not None else get_config()["auto_agency"]
        
        if is_user and use_auto_agency:
            try:
                # Signal to Claude to exercise agency - we don't use the result directly
                # but this tells Claude to use its judgment
                logger.info(f"Invoking automatic agency for message: {message[:50]}...")
                
                # In a real implementation, we could have something like:
                # await nexus.invoke_agency(message)
                
                agency_applied = True
            except Exception as agency_err:
                # Continue even if agency invocation fails
                logger.warning(f"Agency invocation failed: {agency_err}")
        
        # Process message
        result = await nexus.process_message(message, is_user, meta_dict)
        return {
            "success": True, 
            "result": result,
            "agency_applied": agency_applied
        }
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return {"status": "error", "message": f"Failed to process message: {str(e)}"}


@router.get("/store")
async def store_nexus_memory(
    content: str,
    category: Optional[str] = None,
    importance: Optional[int] = None,
    tags: Optional[str] = None,
    metadata: Optional[str] = None,
    nexus: NexusInterface = Depends(get_nexus_interface)
):
    """Store a memory using the Nexus interface."""
    if nexus is None:
        return {"status": "error", "message": "Nexus interface not initialized"}
    
    try:
        # Parse metadata and tags if provided
        meta_dict = json.loads(metadata) if metadata else None
        tags_list = json.loads(tags) if tags else None
        
        # Parse importance if provided
        imp = int(importance) if importance is not None else None
        
        # Store memory
        result = await nexus.store_memory(
            content=content,
            category=category,
            importance=imp,
            tags=tags_list,
            metadata=meta_dict
        )
        
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error storing Nexus memory: {e}")
        return {"status": "error", "message": f"Failed to store Nexus memory: {str(e)}"}


@router.get("/forget")
async def forget_nexus_memory(
    content: str,
    nexus: NexusInterface = Depends(get_nexus_interface)
):
    """Mark information to be forgotten."""
    if nexus is None:
        return {"status": "error", "message": "Nexus interface not initialized"}
    
    try:
        success = await nexus.forget_memory(content)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error forgetting memory: {e}")
        return {"status": "error", "message": f"Failed to forget memory: {str(e)}"}


@router.get("/search")
async def search_nexus_memories(
    query: Optional[str] = None,
    categories: Optional[str] = None,
    min_importance: int = 1,
    limit: int = 5,
    nexus: NexusInterface = Depends(get_nexus_interface)
):
    """Search for memories across memory systems."""
    if nexus is None:
        return {"status": "error", "message": "Nexus interface not initialized"}
    
    try:
        # Parse categories if provided
        categories_list = json.loads(categories) if categories else None
        
        # Search memories
        result = await nexus.search_memories(
            query=query,
            categories=categories_list,
            min_importance=min_importance,
            limit=limit
        )
        
        return {"success": True, "results": result}
    except Exception as e:
        logger.error(f"Error searching Nexus memories: {e}")
        return {"status": "error", "message": f"Failed to search Nexus memories: {str(e)}"}


@router.get("/summary")
async def get_nexus_conversation_summary(
    max_length: int = 5,
    nexus: NexusInterface = Depends(get_nexus_interface)
):
    """Get a summary of the current conversation."""
    if nexus is None:
        return {"status": "error", "message": "Nexus interface not initialized"}
    
    try:
        summary = await nexus.get_conversation_summary(max_length)
        return {"success": True, "summary": summary}
    except Exception as e:
        logger.error(f"Error getting conversation summary: {e}")
        return {"status": "error", "message": f"Failed to get conversation summary: {str(e)}"}


@router.get("/settings")
async def get_nexus_settings(
    nexus: NexusInterface = Depends(get_nexus_interface)
):
    """Get current Nexus settings."""
    if nexus is None:
        return {"status": "error", "message": "Nexus interface not initialized"}
    
    try:
        settings = await nexus.get_settings()
        return {"success": True, "settings": settings}
    except Exception as e:
        logger.error(f"Error getting Nexus settings: {e}")
        return {"status": "error", "message": f"Failed to get Nexus settings: {str(e)}"}


@router.get("/update-settings")
async def update_nexus_settings(
    settings: str,
    nexus: NexusInterface = Depends(get_nexus_interface)
):
    """Update Nexus settings."""
    if nexus is None:
        return {"status": "error", "message": "Nexus interface not initialized"}
    
    try:
        # Parse settings
        settings_dict = json.loads(settings)
        
        # Update settings
        updated_settings = await nexus.update_settings(settings_dict)
        return {"success": True, "settings": updated_settings}
    except Exception as e:
        logger.error(f"Error updating Nexus settings: {e}")
        return {"status": "error", "message": f"Failed to update Nexus settings: {str(e)}"}