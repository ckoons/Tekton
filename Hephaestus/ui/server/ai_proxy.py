"""
AI Proxy endpoint for Hephaestus UI to communicate with AI specialists.

This proxy allows the browser-based UI to communicate with AI specialists
that use socket connections, following the same pattern as aish.
"""

import asyncio
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Import the shared socket client that aish uses
import sys
import os
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.ai.socket_client import AISocketClient, MessageType

router = APIRouter()

class AIMessageRequest(BaseModel):
    """Request to send a message to an AI"""
    ai_name: str
    message: str
    host: Optional[str] = "localhost"
    port: Optional[int] = None

class AIMessageResponse(BaseModel):
    """Response from an AI"""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    ai_id: Optional[str] = None
    model: Optional[str] = None

# Create a shared socket client instance
socket_client = AISocketClient(default_timeout=30.0)

# Port mapping (same as aish)
AI_PORT_MAP = {
    'noesis-ai': 45015,
    'apollo-ai': 45007,
    'athena-ai': 45017,
    'sophia-ai': 45016,
    'hermes-ai': 45001,
    'engram-ai': 45008,
    'prometheus-ai': 45010,
    'metis-ai': 45009,
    'harmonia-ai': 45006,
    'synthesis-ai': 45018,
    'telos-ai': 45019,
    'ergon-ai': 45004,
    'rhetor-ai': 45003,
    'numa-ai': 45014,
    'penia-ai': 45002,
    'hephaestus-ai': 45005,
    'terma-ai': 45020,
    'tekton_core-ai': 45000
}

@router.post("/api/ai/proxy", response_model=AIMessageResponse)
async def proxy_ai_message(request: AIMessageRequest):
    """
    Proxy a message to an AI specialist using socket communication.
    This follows the same pattern as aish.
    """
    try:
        # Get port from request or lookup
        port = request.port
        if not port and request.ai_name in AI_PORT_MAP:
            port = AI_PORT_MAP[request.ai_name]
        
        if not port:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown AI specialist: {request.ai_name}"
            )
        
        # Send message using the same socket client as aish
        response = await socket_client.send_message_async(
            host=request.host,
            port=port,
            message=request.message,
            message_type=MessageType.CHAT
        )
        
        if response['success']:
            return AIMessageResponse(
                success=True,
                content=response.get('response', ''),
                ai_id=response.get('ai_id', request.ai_name),
                model=response.get('model')
            )
        else:
            return AIMessageResponse(
                success=False,
                error=response.get('error', 'Communication failed')
            )
            
    except Exception as e:
        return AIMessageResponse(
            success=False,
            error=str(e)
        )

@router.get("/api/ai/proxy/health")
async def proxy_health():
    """Health check for AI proxy"""
    return {"status": "healthy", "service": "ai-proxy"}