"""Team Chat API endpoints for Rhetor.

Implements the team chat functionality using the AI Socket Registry.
Supports real-time multi-AI collaboration with various moderation modes.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field

from ..core.ai_socket_registry import get_socket_registry
# AI specialist management now handled by AI Registry

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["team-chat"])


class TeamChatRequest(BaseModel):
    """Team chat request model."""
    message: str = Field(..., description="The message to broadcast to all AIs")
    moderation_mode: Optional[str] = Field(
        "pass_through", 
        description="Moderation mode: pass_through, synthesis, consensus, directed"
    )
    target_sockets: Optional[List[str]] = Field(
        None,
        description="Specific socket IDs to target (None for all)"
    )
    timeout: Optional[float] = Field(
        30.0,
        description="Timeout in seconds for collecting responses"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata for the message"
    )


class TeamChatResponse(BaseModel):
    """Team chat response model."""
    request_id: str = Field(..., description="Unique request identifier")
    responses: List[Dict[str, Any]] = Field(..., description="AI responses")
    moderation_mode: str = Field(..., description="Moderation mode used")
    synthesis: Optional[str] = Field(None, description="Synthesized response (if applicable)")
    consensus: Optional[Dict[str, Any]] = Field(None, description="Consensus analysis (if applicable)")
    timestamp: str = Field(..., description="Response timestamp")
    elapsed_time: float = Field(..., description="Time taken to collect responses")


@router.post("/team-chat", response_model=TeamChatResponse)
async def team_chat(request: TeamChatRequest):
    """
    Broadcast a message to all AI specialists and collect responses.
    
    This endpoint implements the team chat functionality where multiple AIs
    can collaborate on answering questions or solving problems.
    """
    start_time = datetime.utcnow()
    request_id = f"team-chat-{start_time.timestamp()}"
    
    try:
        # Get socket registry
        registry = await get_socket_registry()
        
        # Broadcast message
        metadata = request.metadata or {}
        metadata["request_id"] = request_id
        metadata["moderation_mode"] = request.moderation_mode
        
        # Write to team-chat-all or specific sockets
        if request.target_sockets:
            # Write to specific sockets
            for socket_id in request.target_sockets:
                await registry.write(socket_id, request.message, metadata)
        else:
            # Broadcast to all
            await registry.write("team-chat-all", request.message, metadata)
        
        # Collect responses based on moderation mode
        responses = []
        
        if request.moderation_mode == "pass_through":
            # Stream responses as they arrive
            responses = await _collect_responses_streaming(
                registry, request.timeout, request.target_sockets
            )
        else:
            # Collect all responses first
            responses = await _collect_responses_batch(
                registry, request.timeout, request.target_sockets
            )
        
        # Process based on moderation mode
        synthesis = None
        consensus = None
        
        if request.moderation_mode == "synthesis" and responses:
            synthesis = await _synthesize_responses(responses)
        elif request.moderation_mode == "consensus" and responses:
            consensus = await _analyze_consensus(responses)
        
        # Calculate elapsed time
        elapsed_time = (datetime.utcnow() - start_time).total_seconds()
        
        return TeamChatResponse(
            request_id=request_id,
            responses=responses,
            moderation_mode=request.moderation_mode,
            synthesis=synthesis,
            consensus=consensus,
            timestamp=datetime.utcnow().isoformat(),
            elapsed_time=elapsed_time
        )
        
    except Exception as e:
        logger.error(f"Team chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team-chat/stream")
async def team_chat_stream(
    message: str = Query(..., description="Message to broadcast"),
    moderation_mode: str = Query("pass_through", description="Moderation mode"),
    timeout: float = Query(30.0, description="Timeout in seconds")
):
    """
    Stream team chat responses using Server-Sent Events.
    
    This endpoint allows real-time streaming of AI responses as they arrive.
    """
    async def event_generator():
        try:
            # Get socket registry
            registry = await get_socket_registry()
            
            # Broadcast message
            metadata = {
                "request_id": f"stream-{datetime.utcnow().timestamp()}",
                "moderation_mode": moderation_mode,
                "stream": True
            }
            
            await registry.write("team-chat-all", message, metadata)
            
            # Stream responses
            start_time = datetime.utcnow()
            response_count = 0
            
            while (datetime.utcnow() - start_time).total_seconds() < timeout:
                # Read responses
                messages = await registry.read("team-chat-all")
                
                for msg in messages:
                    response_count += 1
                    event_data = {
                        "type": "response",
                        "socket_id": msg["header"].replace("[team-chat-from-", "").replace("]", ""),
                        "content": msg["content"],
                        "timestamp": msg["timestamp"],
                        "metadata": msg.get("metadata", {}),
                        "index": response_count
                    }
                    
                    yield {
                        "event": "message",
                        "data": json.dumps(event_data)
                    }
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
            
            # Send completion event
            yield {
                "event": "complete",
                "data": json.dumps({
                    "type": "complete",
                    "response_count": response_count,
                    "elapsed_time": (datetime.utcnow() - start_time).total_seconds()
                })
            }
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(event_generator())


@router.get("/team-chat/sockets")
async def list_team_sockets():
    """List all registered AI sockets available for team chat."""
    try:
        registry = await get_socket_registry()
        sockets = await registry.list_sockets()
        
        # Filter out the broadcast socket
        team_sockets = [s for s in sockets if s["socket_id"] != "team-chat-all"]
        
        return {
            "sockets": team_sockets,
            "count": len(team_sockets),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error listing sockets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/team-chat/sockets/{socket_id}/reset")
async def reset_team_socket(socket_id: str):
    """Reset a specific AI socket (clear context)."""
    try:
        registry = await get_socket_registry()
        success = await registry.reset(socket_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Socket not found: {socket_id}")
        
        return {
            "socket_id": socket_id,
            "status": "reset",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error resetting socket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions

async def _collect_responses_streaming(
    registry,
    timeout: float,
    target_sockets: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Collect responses in streaming mode."""
    responses = []
    start_time = datetime.utcnow()
    
    while (datetime.utcnow() - start_time).total_seconds() < timeout:
        # Read available responses
        if target_sockets:
            # Read from specific sockets
            for socket_id in target_sockets:
                messages = await registry.read(socket_id)
                for msg in messages:
                    responses.append({
                        "socket_id": socket_id,
                        "content": msg["content"],
                        "timestamp": msg["timestamp"],
                        "metadata": msg.get("metadata", {})
                    })
        else:
            # Read from all
            messages = await registry.read("team-chat-all")
            for msg in messages:
                socket_id = msg["header"].replace("[team-chat-from-", "").replace("]", "")
                responses.append({
                    "socket_id": socket_id,
                    "content": msg["content"],
                    "timestamp": msg["timestamp"],
                    "metadata": msg.get("metadata", {})
                })
        
        # Small delay to prevent busy waiting
        await asyncio.sleep(0.1)
    
    return responses


async def _collect_responses_batch(
    registry,
    timeout: float,
    target_sockets: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Collect all responses in batch mode."""
    # Wait for responses to arrive
    await asyncio.sleep(min(timeout, 5.0))  # Wait up to 5 seconds
    
    # Collect all available responses
    responses = []
    
    if target_sockets:
        for socket_id in target_sockets:
            messages = await registry.read(socket_id)
            for msg in messages:
                responses.append({
                    "socket_id": socket_id,
                    "content": msg["content"],
                    "timestamp": msg["timestamp"],
                    "metadata": msg.get("metadata", {})
                })
    else:
        messages = await registry.read("team-chat-all")
        for msg in messages:
            socket_id = msg["header"].replace("[team-chat-from-", "").replace("]", "")
            responses.append({
                "socket_id": socket_id,
                "content": msg["content"],
                "timestamp": msg["timestamp"],
                "metadata": msg.get("metadata", {})
            })
    
    return responses


async def _synthesize_responses(responses: List[Dict[str, Any]]) -> str:
    """Synthesize multiple AI responses into a coherent summary."""
    if not responses:
        return "No responses to synthesize."
    
    # Group responses for better readability
    synthesis_parts = ["Based on the team's input:\n"]
    
    # Extract key points from each response
    for resp in responses:
        socket_name = resp['socket_id'].split('-')[0].capitalize()
        content = resp['content']
        
        # Truncate very long responses
        if len(content) > 200:
            content = content[:197] + "..."
        
        synthesis_parts.append(f"\n**{socket_name}** suggests: {content}")
    
    # Add summary
    synthesis_parts.append(f"\n\n*Total perspectives: {len(responses)}*")
    
    return "".join(synthesis_parts)


async def _analyze_consensus(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze consensus patterns in AI responses."""
    if not responses:
        return {
            "total_responses": 0,
            "consensus_found": False,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Extract themes (simple keyword analysis for now)
    all_words = []
    for resp in responses:
        # Simple word extraction (lowercase, split)
        words = resp['content'].lower().split()
        all_words.extend([w.strip('.,!?;:') for w in words if len(w) > 4])
    
    # Find common words (appearing in multiple responses)
    word_counts = {}
    for word in all_words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Get top common themes
    common_themes = sorted(
        [(word, count) for word, count in word_counts.items() if count > 1],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    consensus = {
        "total_responses": len(responses),
        "sockets": list(set(r["socket_id"] for r in responses)),
        "common_themes": [{"theme": word, "mentions": count} for word, count in common_themes],
        "consensus_found": len(common_themes) > 0,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return consensus