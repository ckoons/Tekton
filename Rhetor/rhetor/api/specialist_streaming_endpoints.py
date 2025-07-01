"""
Specialist Streaming API endpoints for Rhetor.

Provides SSE (Server-Sent Events) streaming for individual AI specialist interactions,
enabling real-time progressive responses with enhanced metadata.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Optional, Any, AsyncIterator
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field

from landmarks import (
    architecture_decision,
    performance_boundary,
    integration_point,
    api_contract
)

# Add parent directory to path for imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from shared.ai.socket_client import AISocketClient, StreamChunk
from shared.ai.ai_discovery_service import AIDiscoveryService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/chat", tags=["specialist-streaming"])

# Initialize shared components
socket_client = AISocketClient(default_timeout=30.0, debug=True)
discovery_service = AIDiscoveryService()


class StreamingRequest(BaseModel):
    """Request model for streaming chat."""
    message: str = Field(..., description="The message to send to the specialist")
    context_id: Optional[str] = Field(None, description="Context ID for conversation continuity")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Response creativity")
    max_tokens: Optional[int] = Field(4000, gt=0, description="Maximum response tokens")
    include_metadata: bool = Field(True, description="Include enhanced metadata in stream")
    reasoning_depth: Optional[int] = Field(None, description="Track reasoning depth for complex thoughts")


@performance_boundary(
    title="Team Chat Streaming",
    sla="<100ms first token from each AI",
    optimization_notes="Parallel streaming from multiple AIs",
    metrics={"max_concurrent_streams": 18}
)
@router.post("/team/stream")
async def stream_team_chat(request: StreamingRequest):
    """
    Stream responses from all available AI specialists simultaneously.
    
    This creates a real-time "Greek Chorus" effect with multiple AIs
    responding to the same prompt in parallel.
    """
    start_time = time.time()
    
    logger.info(f"Starting team streaming chat: {request.message[:100]}...")
    
    async def generate_team_stream():
        try:
            # Discover all available specialists
            all_ais = await discovery_service.list_ais()
            greek_chorus = [
                ai for ai in all_ais.get('ais', [])
                if ai.get('connection', {}).get('port') 
                and 45000 <= ai['connection']['port'] <= 50000
                and ai.get('status') == 'healthy'
            ]
            
            if not greek_chorus:
                yield {
                    "data": json.dumps({
                        "type": "error",
                        "error": "No healthy Greek Chorus AIs available"
                    })
                }
                return
            
            logger.info(f"Streaming from {len(greek_chorus)} AIs in parallel")
            
            # Create streaming tasks for each AI
            streaming_tasks = []
            for ai in greek_chorus:
                # Create a task to collect all chunks from this AI
                async def collect_chunks(ai_info):
                    chunks = []
                    async for chunk in stream_from_specialist(
                        ai_info['id'],
                        ai_info['connection']['host'],
                        ai_info['connection']['port'],
                        request,
                        ai_info
                    ):
                        chunks.append(chunk)
                    return chunks
                
                task = asyncio.create_task(collect_chunks(ai))
                streaming_tasks.append((ai['id'], task))
            
            # Stream responses as they arrive
            pending_tasks = {ai_id: task for ai_id, task in streaming_tasks}
            
            while pending_tasks:
                # Wait for any task to complete
                done, pending = await asyncio.wait(
                    pending_tasks.values(),
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Process completed tasks
                for task in done:
                    # Find which AI this task belongs to
                    ai_id = None
                    for aid, t in pending_tasks.items():
                        if t == task:
                            ai_id = aid
                            break
                    
                    if ai_id:
                        # Remove from pending
                        del pending_tasks[ai_id]
                        
                        try:
                            chunks = await task
                            # Stream all chunks from this AI
                            for chunk_data in chunks:
                                yield {"data": json.dumps(chunk_data)}
                        except Exception as e:
                            logger.error(f"Error streaming from {ai_id}: {e}")
                            yield {
                                "data": json.dumps({
                                    "type": "error",
                                    "specialist_id": ai_id,
                                    "error": str(e)
                                })
                            }
            
            # Final summary
            completed_count = len(streaming_tasks) - len(pending_tasks)
            yield {
                "data": json.dumps({
                    "type": "team_complete",
                    "summary": {
                        "total_ais": len(greek_chorus),
                        "completed_streams": completed_count,
                        "total_time": time.time() - start_time
                    }
                })
            }
            
        except Exception as e:
            logger.error(f"Team streaming error: {e}", exc_info=True)
            yield {
                "data": json.dumps({
                    "type": "error",
                    "error": str(e)
                })
            }
    
    return EventSourceResponse(generate_team_stream())


# IMPORTANT: Define individual specialist routes AFTER team routes to avoid conflicts
@architecture_decision(
    title="SSE Streaming for Individual Specialists",
    rationale="Enable real-time progressive responses with enhanced metadata for better UX and observability",
    alternatives_considered=["WebSockets", "Long polling", "Batch responses"],
    impacts=["user_experience", "latency", "observability"],
    decided_by="Casey"
)
@integration_point(
    title="Greek Chorus AI Streaming Integration",
    target_component="AI Specialists (ports 45000-50000)",
    protocol="SSE over HTTP",
    data_flow="Request → AISocketClient → AI Specialist → Stream chunks → SSE Response"
)
@api_contract(
    title="Specialist Streaming Endpoint",
    endpoint="/api/chat/{specialist_id}/stream",
    method="POST",
    request_schema=StreamingRequest.schema(),
    response_schema={"type": "event-stream", "data": "StreamChunk"}
)
@router.post("/{specialist_id}/stream")
async def stream_specialist_chat(
    specialist_id: str = Path(..., description="AI specialist ID (e.g., 'apollo-ai', 'athena-ai')"),
    request: StreamingRequest = ...
):
    """
    Stream a chat response from a specific AI specialist.
    
    This endpoint provides real-time streaming responses with enhanced metadata including:
    - Token usage tracking
    - Confidence scores
    - Reasoning depth for chain-of-thought
    - Chunk sequencing
    
    Returns Server-Sent Events (SSE) stream.
    """
    start_time = time.time()
    total_tokens = 0
    chunk_count = 0
    
    logger.info(f"Starting streaming chat with {specialist_id}: {request.message[:100]}...")
    
    async def generate_stream():
        nonlocal total_tokens, chunk_count
        
        try:
            # Discover AI specialist details
            ai_info = await discovery_service.get_ai_info(specialist_id)
            if not ai_info:
                yield {
                    "data": json.dumps({
                        "type": "error",
                        "error": f"Specialist {specialist_id} not found",
                        "specialist_id": specialist_id
                    })
                }
                return
            
            # Check if AI is healthy
            if ai_info.get('status') != 'healthy':
                yield {
                    "data": json.dumps({
                        "type": "error", 
                        "error": f"Specialist {specialist_id} is not healthy: {ai_info.get('status')}",
                        "specialist_id": specialist_id
                    })
                }
                return
            
            # Get connection details
            connection = ai_info.get('connection', {})
            host = connection.get('host', 'localhost')
            port = connection.get('port')
            
            if not port:
                yield {
                    "data": json.dumps({
                        "type": "error",
                        "error": f"No port configured for {specialist_id}",
                        "specialist_id": specialist_id
                    })
                }
                return
            
            logger.info(f"Connecting to {specialist_id} at {host}:{port}")
            
            # Build context for the request
            context = {
                "context_id": request.context_id,
                "specialist_id": specialist_id,
                "timestamp": datetime.utcnow().isoformat(),
                "reasoning_depth": request.reasoning_depth
            }
            
            # Stream the response
            async for chunk in socket_client.send_message_stream(
                host=host,
                port=port,
                message=request.message,
                context=context,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                chunk_count += 1
                
                # Estimate tokens (rough approximation)
                if chunk.content:
                    # Approximate 4 chars per token
                    chunk_tokens = len(chunk.content) // 4
                    total_tokens += chunk_tokens
                
                # Build enhanced metadata
                enhanced_metadata = {
                    "chunk_index": chunk_count,
                    "elapsed_time": time.time() - start_time,
                    "total_tokens_so_far": total_tokens,
                    "specialist_id": specialist_id,
                    "ai_name": ai_info.get('name', specialist_id),
                    "model": ai_info.get('model', 'unknown'),
                }
                
                # Add chunk metadata if available
                if chunk.metadata:
                    enhanced_metadata.update(chunk.metadata)
                
                # Add reasoning depth tracking
                if request.reasoning_depth and "reasoning_level" in enhanced_metadata:
                    enhanced_metadata["reasoning_depth"] = enhanced_metadata["reasoning_level"]
                
                # Yield the chunk
                if chunk.is_final:
                    # Final chunk with complete metadata
                    yield {
                        "data": json.dumps({
                            "type": "complete",
                            "content": chunk.content,
                            "metadata": enhanced_metadata if request.include_metadata else None,
                            "summary": {
                                "total_chunks": chunk_count,
                                "total_tokens": total_tokens,
                                "total_time": time.time() - start_time,
                                "specialist_id": specialist_id,
                                "model": ai_info.get('model', 'unknown')
                            }
                        })
                    }
                else:
                    # Regular content chunk
                    yield {
                        "data": json.dumps({
                            "type": "chunk",
                            "content": chunk.content,
                            "metadata": enhanced_metadata if request.include_metadata else None
                        })
                    }
            
            logger.info(f"Completed streaming from {specialist_id}: {chunk_count} chunks, ~{total_tokens} tokens")
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout streaming from {specialist_id}")
            yield {
                "data": json.dumps({
                    "type": "error",
                    "error": f"Timeout after {socket_client.default_timeout}s",
                    "specialist_id": specialist_id,
                    "partial_response": {
                        "chunks_received": chunk_count,
                        "tokens_received": total_tokens
                    }
                })
            }
        except Exception as e:
            logger.error(f"Error streaming from {specialist_id}: {e}", exc_info=True)
            yield {
                "data": json.dumps({
                    "type": "error",
                    "error": str(e),
                    "specialist_id": specialist_id
                })
            }
    
    # Return SSE response
    return EventSourceResponse(generate_stream())


@router.get("/{specialist_id}/stream")
async def stream_specialist_chat_get(
    specialist_id: str = Path(..., description="AI specialist ID"),
    message: str = Query(..., description="The message to send"),
    context_id: Optional[str] = Query(None, description="Context ID"),
    temperature: float = Query(0.7, ge=0.0, le=2.0),
    max_tokens: int = Query(4000, gt=0),
    include_metadata: bool = Query(True)
):
    """
    GET version of streaming endpoint for easier testing with curl.
    
    Example:
        curl -N "http://localhost:8003/api/chat/apollo-ai/stream?message=Hello"
    """
    request = StreamingRequest(
        message=message,
        context_id=context_id,
        temperature=temperature,
        max_tokens=max_tokens,
        include_metadata=include_metadata
    )
    
    return await stream_specialist_chat(specialist_id, request)




async def stream_from_specialist(
    ai_id: str,
    host: str,
    port: int,
    request: StreamingRequest,
    ai_info: Dict[str, Any]
) -> AsyncIterator[Dict[str, Any]]:
    """Helper function to stream from a single specialist."""
    try:
        async for chunk in socket_client.send_message_stream(
            host=host,
            port=port,
            message=request.message,
            context={"specialist_id": ai_id, "team_chat": True},
            temperature=request.temperature,
            max_tokens=request.max_tokens
        ):
            chunk_data = {
                "type": "team_chunk",
                "specialist_id": ai_id,
                "specialist_name": ai_info.get('name', ai_id),
                "content": chunk.content,
                "is_final": chunk.is_final
            }
            
            if request.include_metadata and chunk.metadata:
                chunk_data["metadata"] = chunk.metadata
            
            yield chunk_data
    
    except Exception as e:
        yield {
            "type": "specialist_error",
            "specialist_id": ai_id,
            "error": str(e)
        }