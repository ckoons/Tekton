"""
Construct API router for Ergon.

Provides endpoints for the Construct CI-native composition system.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Body, Path, Query
from pydantic import Field
from tekton.models.base import TektonBaseModel

# Import the integrated Construct system
from ergon.construct.integration import get_construct_system

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/ergon/construct", tags=["Construct"])


class ConstructProcessRequest(TektonBaseModel):
    """Request model for Construct process endpoint."""
    message: str = Field(..., description="Message to process (JSON or natural language)")
    sender_id: str = Field("ui", description="Sender identifier")


class ConstructProcessResponse(TektonBaseModel):
    """Response model for Construct process endpoint."""
    status: str = Field(..., description="Response status")
    response: str = Field(..., description="Construct system response")
    sender_id: str = Field(..., description="Sender identifier")


@router.post("/process", response_model=ConstructProcessResponse)
async def process_construct_message(request: ConstructProcessRequest):
    """
    Process a message through the Construct system.
    
    Handles both JSON (from CIs) and natural language (from humans).
    """
    try:
        # Get the Construct system instance
        construct_system = get_construct_system()
        
        # Process the message
        response = await construct_system.process(request.message, request.sender_id)
        
        return ConstructProcessResponse(
            status="success",
            response=response,
            sender_id=request.sender_id
        )
        
    except Exception as e:
        logger.error(f"Error processing Construct message: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/workspaces")
async def list_workspaces(ci_id: Optional[str] = Query(None, description="Filter by CI ID")):
    """List workspaces, optionally filtered by CI."""
    try:
        construct_system = get_construct_system()
        workspaces = construct_system.list_workspaces(ci_id=ci_id)
        
        return {
            "status": "success",
            "workspaces": workspaces,
            "count": len(workspaces)
        }
        
    except Exception as e:
        logger.error(f"Error listing workspaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workspaces/{workspace_id}")
async def get_workspace(workspace_id: str = Path(..., description="Workspace ID")):
    """Get workspace state."""
    try:
        construct_system = get_construct_system()
        workspace = construct_system.get_workspace(workspace_id)
        
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        return {
            "status": "success",
            "workspace": workspace
        }
        
    except Exception as e:
        logger.error(f"Error getting workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class SuggestRequest(TektonBaseModel):
    """Request model for component suggestions."""
    requirements: str = Field(..., description="Natural language requirements")


@router.post("/suggest")
async def suggest_components(request: SuggestRequest):
    """Get AI-powered component suggestions."""
    try:
        construct_system = get_construct_system()
        suggestions = await construct_system.suggest_components(request.requirements)
        
        return {
            "status": "success",
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Error getting component suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/protocol")
async def get_protocol():
    """Get the Construct protocol definition."""
    try:
        construct_system = get_construct_system()
        protocol = construct_system.get_protocol()
        
        return {
            "status": "success",
            "protocol": protocol
        }
        
    except Exception as e:
        logger.error(f"Error getting protocol: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def construct_status():
    """Get Construct system status."""
    try:
        construct_system = get_construct_system()
        
        # Get system status
        status = {
            "status": "healthy",
            "components": {
                "engine": "active",
                "resolver": "active", 
                "state": "active",
                "publisher": "active",
                "chat_handler": "active"
            },
            "version": "1.0.0",
            "capabilities": [
                "ci_native_composition",
                "bilingual_interface",
                "persistent_state",
                "component_resolution",
                "sandbox_testing",
                "registry_publishing"
            ]
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting Construct status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }