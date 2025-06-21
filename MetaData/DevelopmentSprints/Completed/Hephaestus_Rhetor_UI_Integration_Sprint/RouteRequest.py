"""
Route Request Model for Rhetor Chat Routing

This file defines the request model for the new /chat/route endpoint
that will handle routing messages to component AIs or team chat.
"""

from typing import Optional
from pydantic import Field
from tekton.models import TektonBaseModel


class RouteRequest(TektonBaseModel):
    """Request model for routing chat messages through Rhetor"""
    
    component: str = Field(
        ..., 
        description="Component name (e.g., 'apollo', 'engram') or 'team' for team chat"
    )
    message: str = Field(
        ..., 
        description="The message content to route"
    )
    context_id: str = Field(
        ..., 
        description="Context identifier for maintaining conversation state"
    )
    user_id: Optional[str] = Field(
        None, 
        description="Optional user identifier for tracking"
    )


class RouteResponse(TektonBaseModel):
    """Response model for routed chat messages"""
    
    success: bool
    component: str
    message: str
    speaker: Optional[str] = Field(
        None, 
        description="For team chat, identifies which AI is speaking"
    )
    model: Optional[str] = Field(
        None, 
        description="The model used for the response"
    )
    provider: Optional[str] = Field(
        None, 
        description="The provider used for the response"
    )
    participants: Optional[list[str]] = Field(
        None, 
        description="For team chat, list of participating AIs"
    )