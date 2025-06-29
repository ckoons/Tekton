"""
AI Specialist HTTP endpoints for Rhetor.

This module provides REST API endpoints for AI specialist management,
including specialist listing, activation, messaging, and configuration.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from pydantic import BaseModel, Field

import logging

logger = logging.getLogger(__name__)

# Pydantic models for requests/responses
class SpecialistResponse(BaseModel):
    """AI Specialist information"""
    id: str
    name: str
    type: str
    component_id: str
    active: bool
    status: str
    model: str
    capabilities: List[str]
    personality: Dict[str, Any]
    messages: int = 0
    sessions: int = 0

class SpecialistListResponse(BaseModel):
    """List of AI specialists"""
    count: int
    specialists: List[SpecialistResponse]

class SpecialistActivateRequest(BaseModel):
    """Request to activate a specialist"""
    force: bool = Field(False, description="Force activation even if another instance is running")

class SpecialistMessageRequest(BaseModel):
    """Request to send a message to a specialist"""
    message: str
    context_id: Optional[str] = "default"
    streaming: bool = True
    options: Optional[Dict[str, Any]] = None

class TeamChatRequest(BaseModel):
    """Request to orchestrate team chat"""
    topic: str
    specialists: List[str]
    initial_prompt: str
    max_rounds: int = Field(5, description="Maximum rounds of conversation")

class ConversationCreateRequest(BaseModel):
    """Request to create an AI conversation"""
    topic: str
    participants: List[str]
    moderator: Optional[str] = "rhetor-orchestrator"
    turn_taking_mode: str = "moderated"
    settings: Optional[Dict[str, Any]] = None

class AnthropicMaxToggleRequest(BaseModel):
    """Request to toggle Anthropic Max mode"""
    enabled: bool
    
class ConfigurationUpdateRequest(BaseModel):
    """Request to update AI configuration"""
    anthropic_max: Optional[bool] = None
    model_overrides: Optional[Dict[str, str]] = None
    rate_limits: Optional[Dict[str, Any]] = None

# Create router
router = APIRouter(prefix="/api/ai", tags=["AI Specialists"])

def get_managers():
    """Get AI specialist managers from app state"""
    from ..api.app import component
    
    # Get managers from the component instance
    ai_specialist_manager = getattr(component, 'ai_specialist_manager', None)
    ai_messaging_integration = getattr(component, 'ai_messaging_integration', None)
    anthropic_max_config = getattr(component, 'anthropic_max_config', None)
    
    return ai_specialist_manager, ai_messaging_integration, anthropic_max_config

# Endpoints
@router.get("/specialists", response_model=SpecialistListResponse)
async def list_specialists(
    active_only: bool = Query(False, description="Only show active specialists"),
    type_filter: Optional[str] = Query(None, description="Filter by specialist type")
):
    """List all AI specialists"""
    specialist_manager, _, _ = get_managers()
    
    if not specialist_manager:
        raise HTTPException(status_code=503, detail="AI specialist manager not initialized")
    
    try:
        all_specialists = specialist_manager.specialists
        specialists = []
        
        for spec_id, config in all_specialists.items():
            # Apply filters
            if active_only and config.status != "active":
                continue
            if type_filter and type_filter not in config.specialist_type:
                continue
                
            # Get specialist stats
            stats = await specialist_manager.get_specialist_status(spec_id)
            
            specialists.append(SpecialistResponse(
                id=spec_id,
                name=config.personality.get("role", spec_id),
                type=config.specialist_type,
                component_id=config.component_id,
                active=config.status == "active",
                status=config.status,
                model=config.model_config.get("model", "unknown"),
                capabilities=config.capabilities,
                personality=config.personality,
                messages=stats.get("message_count", 0),
                sessions=stats.get("session_count", 0)
            ))
        
        return SpecialistListResponse(
            count=len(specialists),
            specialists=specialists
        )
        
    except Exception as e:
        logger.error(f"Error listing specialists: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/specialists/{specialist_id}", response_model=SpecialistResponse)
async def get_specialist(specialist_id: str = Path(..., description="Specialist ID")):
    """Get details of a specific AI specialist"""
    specialist_manager, _, _ = get_managers()
    
    if not specialist_manager:
        raise HTTPException(status_code=503, detail="AI specialist manager not initialized")
        
    if specialist_id not in specialist_manager.specialists:
        raise HTTPException(status_code=404, detail=f"Specialist {specialist_id} not found")
    
    try:
        config = specialist_manager.specialists[specialist_id]
        stats = await specialist_manager.get_specialist_status(specialist_id)
        
        return SpecialistResponse(
            id=specialist_id,
            name=config.personality.get("role", specialist_id),
            type=config.specialist_type,
            component_id=config.component_id,
            active=config.status == "active",
            status=config.status,
            model=config.model_config.get("model", "unknown"),
            capabilities=config.capabilities,
            personality=config.personality,
            messages=stats.get("message_count", 0),
            sessions=stats.get("session_count", 0)
        )
        
    except Exception as e:
        logger.error(f"Error getting specialist {specialist_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/specialists/{specialist_id}/activate")
async def activate_specialist(
    specialist_id: str = Path(..., description="Specialist ID"),
    request: SpecialistActivateRequest = None
):
    """Activate an AI specialist"""
    specialist_manager, _, _ = get_managers()
    
    if not specialist_manager:
        raise HTTPException(status_code=503, detail="AI specialist manager not initialized")
        
    if specialist_id not in specialist_manager.specialists:
        raise HTTPException(status_code=404, detail=f"Specialist {specialist_id} not found")
    
    try:
        success = await specialist_manager.create_specialist(specialist_id)
        
        if success:
            config = specialist_manager.specialists[specialist_id]
            return {
                "success": True,
                "specialist_id": specialist_id,
                "name": config.personality.get("role", specialist_id),
                "status": "active",
                "message": f"Specialist {specialist_id} activated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to activate specialist {specialist_id}")
            
    except Exception as e:
        logger.error(f"Error activating specialist {specialist_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/specialists/{specialist_id}/deactivate")
async def deactivate_specialist(specialist_id: str = Path(..., description="Specialist ID")):
    """Deactivate an AI specialist"""
    specialist_manager, _, _ = get_managers()
    
    if not specialist_manager:
        raise HTTPException(status_code=503, detail="AI specialist manager not initialized")
        
    if specialist_id not in specialist_manager.specialists:
        raise HTTPException(status_code=404, detail=f"Specialist {specialist_id} not found")
    
    try:
        # TODO: Implement specialist deactivation
        return {
            "success": False,
            "specialist_id": specialist_id,
            "message": "Deactivation not yet implemented"
        }
        
    except Exception as e:
        logger.error(f"Error deactivating specialist {specialist_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/specialists/{specialist_id}/message")
async def message_specialist(
    request: SpecialistMessageRequest,
    specialist_id: str = Path(..., description="Specialist ID")
):
    """Send a message to an AI specialist"""
    specialist_manager, _, _ = get_managers()
    
    if not specialist_manager:
        raise HTTPException(status_code=503, detail="AI specialist manager not initialized")
        
    if specialist_id not in specialist_manager.specialists:
        raise HTTPException(status_code=404, detail=f"Specialist {specialist_id} not found")
    
    try:
        # Ensure specialist is active
        config = specialist_manager.specialists[specialist_id]
        if config.status != "active":
            # Try to activate the specialist
            await specialist_manager.create_specialist(specialist_id)
            config = specialist_manager.specialists[specialist_id]
            if config.status != "active":
                raise HTTPException(status_code=400, detail=f"Specialist {specialist_id} could not be activated")
        
        # Get the component instance to access specialist router
        from ..api.app import component
        if not hasattr(component, 'specialist_router'):
            raise HTTPException(status_code=503, detail="Specialist router not initialized")
            
        specialist_router = component.specialist_router
        
        # Route the message to the specialist
        response = await specialist_router.route_to_specialist(
            specialist_id=specialist_id,
            message=request.message,
            context_id=request.context_id,
            streaming=False,  # For now, return full response
            options=request.options
        )
        
        # Extract the response content
        if isinstance(response, dict):
            content = response.get("content", response.get("message", response.get("response", "No response")))
        else:
            content = str(response)
            
        # Return the response
        return {
            "success": True,
            "specialist_id": specialist_id,
            "response": content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error messaging specialist {specialist_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/specialists/create")
async def create_dynamic_specialist(
    specialist_type: str = Query(..., description="Type of specialist to create"),
    requirements: List[str] = Query(..., description="Required capabilities"),
    name: Optional[str] = Query(None, description="Custom name for specialist")
):
    """Create a new dynamic AI specialist"""
    specialist_manager, _, _ = get_managers()
    
    if not specialist_manager:
        raise HTTPException(status_code=503, detail="AI specialist manager not initialized")
    
    try:
        # TODO: Implement dynamic specialist creation
        return {
            "success": False,
            "message": "Dynamic specialist creation not yet implemented"
        }
        
    except Exception as e:
        logger.error(f"Error creating dynamic specialist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversations/create")
async def create_conversation(request: ConversationCreateRequest):
    """Create a new AI-to-AI conversation"""
    _, messaging_integration, _ = get_managers()
    
    if not messaging_integration:
        raise HTTPException(status_code=503, detail="AI messaging integration not initialized")
    
    try:
        conversation_id = await messaging_integration.create_ai_conversation(
            topic=request.topic,
            initial_specialists=request.participants
        )
        
        if not conversation_id:
            raise HTTPException(status_code=500, detail="Failed to create conversation")
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "topic": request.topic,
            "participants": request.participants,
            "moderator": request.moderator
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/team-chat")
async def orchestrate_team_chat(request: TeamChatRequest):
    """Orchestrate a team chat between AI specialists"""
    _, messaging_integration, _ = get_managers()
    
    if not messaging_integration:
        raise HTTPException(status_code=503, detail="AI messaging integration not initialized")
    
    try:
        messages = await messaging_integration.orchestrate_team_chat(
            topic=request.topic,
            specialists=request.specialists,
            initial_prompt=request.initial_prompt
        )
        
        return {
            "success": True,
            "topic": request.topic,
            "participants": request.specialists,
            "message_count": len(messages),
            "messages": messages
        }
        
    except Exception as e:
        logger.error(f"Error orchestrating team chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configuration")
async def get_configuration():
    """Get current AI configuration including Anthropic Max status"""
    _, _, anthropic_max = get_managers()
    
    try:
        config = {
            "anthropic_max": anthropic_max.to_dict() if anthropic_max else {"enabled": False},
            "environment": {
                "ANTHROPIC_MAX_ACCOUNT": os.environ.get("ANTHROPIC_MAX_ACCOUNT", "false"),
                "ANTHROPIC_API_KEY": "***" if os.environ.get("ANTHROPIC_API_KEY") else None
            }
        }
        
        return config
        
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configuration/anthropic-max")
async def toggle_anthropic_max(request: AnthropicMaxToggleRequest):
    """Toggle Anthropic Max mode"""
    _, _, anthropic_max = get_managers()
    
    if not anthropic_max:
        raise HTTPException(status_code=503, detail="Anthropic Max configuration not initialized")
    
    try:
        if request.enabled:
            anthropic_max.enable()
        else:
            anthropic_max.disable()
            
        return {
            "success": True,
            "enabled": anthropic_max.enabled,
            "message": f"Anthropic Max {'enabled' if request.enabled else 'disabled'}"
        }
        
    except Exception as e:
        logger.error(f"Error toggling Anthropic Max: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/configuration")
async def update_configuration(request: ConfigurationUpdateRequest):
    """Update AI configuration"""
    specialist_manager, _, anthropic_max = get_managers()
    
    try:
        updated = {}
        
        # Update Anthropic Max if provided
        if request.anthropic_max is not None and anthropic_max:
            if request.anthropic_max:
                anthropic_max.enable()
            else:
                anthropic_max.disable()
            updated["anthropic_max"] = anthropic_max.enabled
            
        # Update model overrides if provided
        if request.model_overrides and specialist_manager:
            # TODO: Implement model override updates
            updated["model_overrides"] = "Not yet implemented"
            
        # Update rate limits if provided
        if request.rate_limits:
            # TODO: Implement rate limit updates
            updated["rate_limits"] = "Not yet implemented"
            
        return {
            "success": True,
            "updated": updated,
            "message": "Configuration updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Import os for environment checks
import os