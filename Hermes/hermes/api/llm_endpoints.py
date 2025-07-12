"""
LLM Chat Endpoints - REST API for interacting with LLMs via tekton-llm-client.

This module provides FastAPI endpoints for LLM-powered chat and analysis
using the standardized tekton-llm-client library which connects to Rhetor.
"""

import logging
import time
import json
import os
import sys
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import Field
from tekton.models import TektonBaseModel
from shared.env import TektonEnviron
from shared.urls import tekton_url

from landmarks import api_contract, integration_point, performance_boundary

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config
from hermes.core.llm_client import LLMClient

# Configure logger
logger = logging.getLogger(__name__)

# Create API router
llm_router = APIRouter(prefix="/llm", tags=["llm"])

# Initialize LLM client with Rhetor endpoint
config = get_component_config()
rhetor_port_str = TektonEnviron.get('RHETOR_PORT')
rhetor_port = config.rhetor.port if hasattr(config, 'rhetor') else int(rhetor_port_str) if rhetor_port_str else 8003
llm_client = LLMClient(
    adapter_url=tekton_url("rhetor")
)

# Pydantic models for request/response validation

class ChatMessage(TektonBaseModel):
    """Model for chat messages."""
    role: str
    content: str
    timestamp: Optional[float] = None

class ChatRequest(TektonBaseModel):
    """Model for chat requests."""
    message: str
    history: Optional[List[ChatMessage]] = []
    stream: bool = False
    model: Optional[str] = None
    provider: Optional[str] = None

class ChatResponse(TektonBaseModel):
    """Model for chat responses."""
    message: str
    model: str
    provider: str
    timestamp: float

class AnalyzeMessageRequest(TektonBaseModel):
    """Model for message analysis requests."""
    message: Dict[str, Any]
    context: Optional[Dict[str, Any]] = {}

class AnalyzeServiceRequest(TektonBaseModel):
    """Model for service analysis requests."""
    service_data: Dict[str, Any]

class ProviderInfo(TektonBaseModel):
    """Model for provider information."""
    providers: List[str]
    current_provider: str
    current_model: str

@llm_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat with the LLM.
    
    Args:
        request: Chat request with message and optional history
        
    Returns:
        Chat response with LLM's reply
    """
    try:
        # Convert chat history to format expected by LLM client
        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.history
        ]
        
        # Set provider and model if specified
        if request.provider or request.model:
            # Update client settings
            llm_client.client.set_model(request.model)
            llm_client.client.set_provider(request.provider)
        
        # Get current settings
        settings = llm_client.client.get_settings()
        
        # Make chat request
        response = await llm_client.chat(request.message, chat_history)
        
        return ChatResponse(
            message=response,
            model=settings.get('model', 'unknown'),
            provider=settings.get('provider', 'unknown'),
            timestamp=time.time()
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@llm_router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses from the LLM.
    
    Args:
        request: Chat request with streaming enabled
        
    Returns:
        Server-sent event stream with chat chunks
    """
    try:
        # Convert chat history
        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.history
        ]
        
        # Set provider and model if specified
        if request.provider or request.model:
            llm_client.client.set_model(request.model)
            llm_client.client.set_provider(request.provider)
        
        async def generate():
            """Generate SSE events from LLM stream."""
            try:
                async for chunk in llm_client.streaming_chat(
                    request.message,
                    chat_history
                ):
                    # Format as SSE
                    event = f"data: {json.dumps({'chunk': chunk})}\n\n"
                    yield event
                    
                # Send completion event
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                logger.error(f"Streaming error: {str(e)}")
                error_event = f"data: {json.dumps({'error': str(e)})}\n\n"
                yield error_event
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        logger.error(f"Stream setup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stream failed: {str(e)}")

@llm_router.post("/analyze/message")
async def analyze_message(request: AnalyzeMessageRequest) -> Dict[str, Any]:
    """
    Analyze a message using the LLM.
    
    Args:
        request: Message and context for analysis
        
    Returns:
        Analysis results
    """
    try:
        # Use the analyze_message method from LLM client
        analysis = await llm_client.analyze_message(
            request.message,
            request.context
        )
        
        return {"analysis": analysis, "timestamp": time.time()}
        
    except Exception as e:
        logger.error(f"Message analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@llm_router.post("/analyze/service")
async def analyze_service(request: AnalyzeServiceRequest) -> Dict[str, Any]:
    """
    Analyze service data using the LLM.
    
    Args:
        request: Service data for analysis
        
    Returns:
        Service analysis results
    """
    try:
        # Use the analyze_service method from LLM client
        analysis = await llm_client.analyze_service(request.service_data)
        
        return {"analysis": analysis, "timestamp": time.time()}
        
    except Exception as e:
        logger.error(f"Service analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@llm_router.get("/providers", response_model=ProviderInfo)
async def get_providers() -> ProviderInfo:
    """
    Get available LLM providers and current selection.
    
    Returns:
        Provider information including available providers and current selection
    """
    try:
        # Get available providers from tekton-llm-client
        providers = await llm_client.get_available_providers()
        settings = llm_client.client.get_settings()
        
        return ProviderInfo(
            providers=providers,
            current_provider=settings.get('provider', 'unknown'),
            current_model=settings.get('model', 'unknown')
        )
        
    except Exception as e:
        logger.error(f"Provider info error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get providers: {str(e)}")

@integration_point(
    title="LLM WebSocket interface",
    target_component="Rhetor",
    protocol="WebSocket",
    data_flow="Client <-> Hermes <-> Rhetor (bidirectional streaming)"
)
@performance_boundary(
    title="Real-time LLM streaming",
    sla="<100ms first token latency",
    optimization_notes="Direct WebSocket pass-through to Rhetor"
)
@api_contract(
    title="WebSocket LLM chat",
    endpoint="/llm/ws",
    method="WebSocket",
    request_schema={"type": "chat|analyze", "message": "string", "stream": "bool"},
    response_schema={"type": "response|error", "content": "string"}
)
@llm_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time LLM interactions.
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get("type", "chat")
            
            if message_type == "chat":
                # Handle chat messages
                message = data.get("message", "")
                history = data.get("history", [])
                stream = data.get("stream", True)
                
                if stream:
                    # Stream response
                    async for chunk in llm_client.streaming_chat(message, history):
                        await websocket.send_json({
                            "type": "chunk",
                            "content": chunk
                        })
                    
                    # Send completion
                    await websocket.send_json({
                        "type": "complete"
                    })
                else:
                    # Single response
                    response = await llm_client.chat(message, history)
                    await websocket.send_json({
                        "type": "response",
                        "content": response
                    })
                    
            elif message_type == "analyze":
                # Handle analysis requests
                target = data.get("target", "message")
                payload = data.get("payload", {})
                
                if target == "message":
                    analysis = await llm_client.analyze_message(
                        payload.get("message", {}),
                        payload.get("context", {})
                    )
                else:
                    analysis = await llm_client.analyze_service(payload)
                
                await websocket.send_json({
                    "type": "analysis",
                    "result": analysis
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        await websocket.close()