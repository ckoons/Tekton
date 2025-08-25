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

class CIMessageRequest(BaseModel):
    """Request to send a message to a CI"""
    ai_name: str
    message: str
    host: Optional[str] = "localhost"
    port: Optional[int] = None

class CIMessageResponse(BaseModel):
    """Response from a CI"""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    ai_id: Optional[str] = None
    model: Optional[str] = None

# Create a shared socket client instance
socket_client = AISocketClient(default_timeout=30.0)

# Port mapping (same as aish)
AI_PORT_MAP = {
    'noesis-ci': 45015,
    'apollo-ci': 45007,
    'athena-ci': 45017,
    'sophia-ci': 45016,
    'hermes-ci': 45001,
    'engram-ci': 45008,
    'prometheus-ci': 45010,
    'metis-ci': 45009,
    'harmonia-ci': 45006,
    'synthesis-ci': 45018,
    'telos-ci': 45019,
    'ergon-ci': 45004,
    'rhetor-ci': 45003,
    'numa-ci': 45014,
    'penia-ci': 45002,
    'hephaestus-ci': 45005,
    'terma-ci': 45020,
    'tekton_core-ci': 45000
}

@router.post("/api/ai/proxy", response_model=CIMessageResponse)
async def proxy_ai_message(request: CIMessageRequest):
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
            return CIMessageResponse(
                success=True,
                content=response.get('response', ''),
                ai_id=response.get('ai_id', request.ai_name),
                model=response.get('model')
            )
        else:
            return CIMessageResponse(
                success=False,
                error=response.get('error', 'Communication failed')
            )
            
    except Exception as e:
        return CIMessageResponse(
            success=False,
            error=str(e)
        )

@router.get("/api/ai/proxy/health")
async def proxy_health():
    """Health check for AI proxy"""
    return {"status": "healthy", "service": "ai-proxy"}