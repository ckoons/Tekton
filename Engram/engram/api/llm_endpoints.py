#!/usr/bin/env python3
"""
LLM API Endpoints for Engram

This module implements FastAPI endpoints for interacting with LLMs
through the Engram system, leveraging the LLM adapter with enhanced
tekton-llm-client features.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Any, Optional, AsyncGenerator, Callable, Awaitable
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import StreamingResponse
from tekton.models import TektonBaseModel

# Import enhanced tekton-llm-client features
from tekton_llm_client import (
    StreamHandler, LLMSettings,
    collect_stream, stream_to_string
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.api.llm_endpoints")

# Import Engram modules
from engram.core.llm_adapter import LLMAdapter
from engram.core.memory_manager import MemoryManager
from engram.api.dependencies import get_memory_manager

# Models for request/response
class ChatMessage(TektonBaseModel):
    role: str
    content: str

class ChatRequest(TektonBaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    system: Optional[str] = None
    persist_memory: Optional[bool] = True
    memory_namespace: Optional[str] = "conversations"

class ChatResponse(TektonBaseModel):
    content: str
    model: str
    provider: Optional[str] = None

class LLMAnalysisRequest(TektonBaseModel):
    content: str
    context: Optional[str] = None
    model: Optional[str] = None

class LLMAnalysisResponse(TektonBaseModel):
    analysis: str
    success: bool
    error: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None

# Create router
router = APIRouter(
    prefix="/v1/llm",
    tags=["LLM"],
)

# Dependency to get LLM adapter
async def get_llm_adapter():
    return LLMAdapter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    llm_adapter: LLMAdapter = Depends(get_llm_adapter),
    memory_manager: MemoryManager = Depends(get_memory_manager)
):
    """
    Send a chat request to the LLM and get a response.
    """
    # Format messages for the LLM adapter
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    # Extract user message and system prompt
    user_message = None
    system_prompt = request.system
    
    for msg in reversed(messages):
        if msg["role"] == "user" and not user_message:
            user_message = msg["content"]
        if msg["role"] == "system" and not system_prompt:
            system_prompt = msg["content"]
    
    # If no user message found, use the last message
    if not user_message and messages:
        user_message = messages[-1]["content"]
    
    # Get chat response
    try:
        # Create custom settings
        custom_settings = LLMSettings(
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            model=request.model
        )
        
        # Get LLM client
        client = await llm_adapter._get_client()
        
        # Generate text
        response = await client.generate_text(
            prompt=user_message,
            system_prompt=system_prompt,
            settings=custom_settings
        )
        
        # Store in memory if requested
        if request.persist_memory:
            # Create formatted conversation for memory
            conversation = "\n\n".join([
                f"{'User' if msg.role == 'user' else 'Assistant'}: {msg.content}"
                for msg in request.messages
            ])
            conversation += f"\n\nAssistant: {response.content}"
            
            # Get memory service
            memory_service = await memory_manager.get_memory_service(None)
            
            # Store in memory
            await memory_service.add(
                content=conversation,
                namespace=request.memory_namespace,
                metadata={
                    "type": "conversation",
                    "model": response.model,
                    "provider": response.provider
                }
            )
        
        return {
            "content": response.content,
            "model": response.model,
            "provider": response.provider
        }
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def stream_chat(
    request: ChatRequest,
    llm_adapter: LLMAdapter = Depends(get_llm_adapter),
    memory_manager: MemoryManager = Depends(get_memory_manager)
):
    """
    Stream a chat response from the LLM.
    """
    if not request.stream:
        # If stream is False, redirect to regular chat endpoint
        return await chat(request, llm_adapter, memory_manager)
    
    # Format messages for the LLM adapter
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    # Extract user message and system prompt
    user_message = None
    system_prompt = request.system
    
    for msg in reversed(messages):
        if msg["role"] == "user" and not user_message:
            user_message = msg["content"]
        if msg["role"] == "system" and not system_prompt:
            system_prompt = msg["content"]
    
    # If no user message found, use the last message
    if not user_message and messages:
        user_message = messages[-1]["content"]
    
    # Create custom settings
    custom_settings = LLMSettings(
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        model=request.model
    )
    
    # Create streaming response
    async def generate():
        full_response = ""
        
        # Get LLM client
        client = await llm_adapter._get_client()
        
        try:
            # Start streaming
            response_stream = await client.generate_text(
                prompt=user_message,
                system_prompt=system_prompt,
                settings=custom_settings,
                streaming=True
            )
            
            # Create a callback for collecting the full response
            async def collect_callback(chunk: str) -> None:
                nonlocal full_response
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            # Process the stream using StreamHandler
            stream_handler = StreamHandler(
                process_fn=lambda chunk: json.dumps({'content': chunk.chunk if hasattr(chunk, 'chunk') else chunk})
            )
            
            # Process each chunk in the stream
            async for chunk in response_stream:
                chunk_text = chunk.chunk if hasattr(chunk, 'chunk') else chunk
                full_response += chunk_text
                yield f"data: {json.dumps({'content': chunk_text})}\n\n"
                
            # Get final model info
            model_info = getattr(response_stream, '_model_info', {})
            model = model_info.get('model', request.model or llm_adapter.default_model)
            provider = model_info.get('provider', llm_adapter.default_provider)
            
            # Store in memory if requested
            if request.persist_memory:
                # Create formatted conversation for memory
                conversation = "\n\n".join([
                    f"{'User' if msg.role == 'user' else 'Assistant'}: {msg.content}"
                    for msg in request.messages
                ])
                conversation += f"\n\nAssistant: {full_response}"
                
                # Get memory service
                memory_service = await memory_manager.get_memory_service(None)
                
                # Store in memory asynchronously (don't wait for completion)
                asyncio.create_task(memory_service.add(
                    content=conversation,
                    namespace=request.memory_namespace,
                    metadata={
                        "type": "conversation",
                        "model": model,
                        "provider": provider
                    }
                ))
            
            yield f"data: {json.dumps({'type': 'done', 'model': model, 'provider': provider})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@router.websocket("/chat/ws")
async def websocket_chat(
    websocket: WebSocket,
    llm_adapter: LLMAdapter = Depends(get_llm_adapter),
    memory_manager: MemoryManager = Depends(get_memory_manager)
):
    """
    WebSocket endpoint for interactive chat sessions.
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Extract request parameters
            messages = data.get("messages", [])
            model = data.get("model")
            temperature = data.get("temperature", 0.7)
            max_tokens = data.get("max_tokens")
            stream = data.get("stream", False)
            system = data.get("system")
            persist_memory = data.get("persist_memory", True)
            memory_namespace = data.get("memory_namespace", "conversations")
            
            # Extract user message and system prompt
            user_message = None
            system_prompt = system
            
            for msg in reversed(messages):
                if msg["role"] == "user" and not user_message:
                    user_message = msg["content"]
                if msg["role"] == "system" and not system_prompt:
                    system_prompt = msg["content"]
            
            # If no user message found, use the last message
            if not user_message and messages:
                user_message = messages[-1]["content"]
            
            # Create custom settings
            custom_settings = LLMSettings(
                temperature=temperature,
                max_tokens=max_tokens,
                model=model
            )
            
            # Get LLM client
            client = await llm_adapter._get_client()
            
            if stream:
                # Create a websocket callback
                async def ws_callback(chunk: str) -> None:
                    await websocket.send_json({
                        "type": "chunk",
                        "content": chunk
                    })
                
                # Create a stream handler
                stream_handler = StreamHandler(callback_fn=ws_callback)
                
                # Streaming response
                full_response = ""
                
                try:
                    # Start streaming
                    response_stream = await client.generate_text(
                        prompt=user_message,
                        system_prompt=system_prompt,
                        settings=custom_settings,
                        streaming=True
                    )
                    
                    # Process the stream manually
                    async for chunk in response_stream:
                        chunk_text = chunk.chunk if hasattr(chunk, 'chunk') else chunk
                        full_response += chunk_text
                        await websocket.send_json({
                            "type": "chunk",
                            "content": chunk_text
                        })
                    
                    # Get final model info
                    model_info = getattr(response_stream, '_model_info', {})
                    model_used = model_info.get('model', model or llm_adapter.default_model)
                    provider_used = model_info.get('provider', llm_adapter.default_provider)
                    
                    # Send completion message
                    await websocket.send_json({
                        "type": "done",
                        "model": model_used,
                        "provider": provider_used
                    })
                    
                    # Store in memory if requested
                    if persist_memory:
                        # Create formatted conversation for memory
                        conversation = "\n\n".join([
                            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                            for msg in messages
                        ])
                        conversation += f"\n\nAssistant: {full_response}"
                        
                        # Get memory service
                        memory_service = await memory_manager.get_memory_service(None)
                        
                        # Store in memory asynchronously
                        asyncio.create_task(memory_service.add(
                            content=conversation,
                            namespace=memory_namespace,
                            metadata={
                                "type": "conversation",
                                "model": model_used,
                                "provider": provider_used
                            }
                        ))
                except Exception as e:
                    logger.error(f"WebSocket streaming error: {str(e)}")
                    await websocket.send_json({
                        "type": "error",
                        "error": str(e)
                    })
            else:
                # Non-streaming response
                try:
                    # Generate text
                    response = await client.generate_text(
                        prompt=user_message,
                        system_prompt=system_prompt,
                        settings=custom_settings
                    )
                    
                    # Send complete response
                    await websocket.send_json({
                        "type": "message",
                        "content": response.content,
                        "model": response.model,
                        "provider": response.provider
                    })
                    
                    # Store in memory if requested
                    if persist_memory:
                        # Create formatted conversation for memory
                        conversation = "\n\n".join([
                            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                            for msg in messages
                        ])
                        conversation += f"\n\nAssistant: {response.content}"
                        
                        # Get memory service
                        memory_service = await memory_manager.get_memory_service(None)
                        
                        # Store in memory asynchronously
                        asyncio.create_task(memory_service.add(
                            content=conversation,
                            namespace=memory_namespace,
                            metadata={
                                "type": "conversation",
                                "model": response.model,
                                "provider": response.provider
                            }
                        ))
                except Exception as e:
                    logger.error(f"WebSocket error: {str(e)}")
                    await websocket.send_json({
                        "type": "error",
                        "error": str(e)
                    })
    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except:
            # Connection may already be closed
            pass

@router.post("/analyze", response_model=LLMAnalysisResponse)
async def analyze_content(
    request: LLMAnalysisRequest,
    llm_adapter: LLMAdapter = Depends(get_llm_adapter)
):
    """
    Analyze content using the LLM with enhanced features.
    """
    try:
        result = await llm_adapter.analyze_memory(
            content=request.content,
            context=request.context,
            model=request.model
        )
        return result
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return {
            "analysis": "",
            "success": False,
            "error": str(e)
        }

@router.get("/models")
async def get_models(
    llm_adapter: LLMAdapter = Depends(get_llm_adapter)
):
    """
    Get available LLM models using the enhanced client features.
    """
    try:
        models = await llm_adapter.get_available_models()
        return models
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))