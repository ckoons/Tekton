"""Team Chat API endpoints for Rhetor.

Implements the team chat functionality using the MCP Tools Integration.
Connects to real Greek Chorus AIs for multi-AI collaboration.
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

from ..core.mcp.tools_integration_unified import MCPToolsIntegrationUnified, get_mcp_tools_integration

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
        2.0,
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
    
    This endpoint connects to real Greek Chorus AIs via the MCP tools integration
    for multi-AI collaboration on answering questions or solving problems.
    """
    start_time = datetime.utcnow()
    request_id = f"team-chat-{start_time.timestamp()}"
    
    logger.info(f"Team chat request {request_id}: {request.message[:100]}...")
    logger.info(f"Moderation mode: {request.moderation_mode}, Target AIs: {request.target_sockets}")
    
    try:
        # Get MCP tools integration
        integration = get_mcp_tools_integration()
        if not integration:
            # Initialize if needed
            integration = MCPToolsIntegrationUnified()
            from ..core.mcp.tools_integration_unified import set_mcp_tools_integration
            set_mcp_tools_integration(integration)
            logger.info("Initialized MCP tools integration for team chat")
        
        # Use orchestrate_team_chat to connect to real Greek Chorus AIs
        topic = request.metadata.get("topic", "General Discussion") if request.metadata else "General Discussion"
        
        logger.info("Calling orchestrate_team_chat with real Greek Chorus AIs")
        result = await integration.orchestrate_team_chat(
            topic=topic,
            specialists=request.target_sockets or [],  # Empty list means all available
            initial_prompt=request.message,
            max_rounds=1,  # Single round for now
            orchestration_style=request.moderation_mode,
            timeout=request.timeout
        )
        
        # Convert responses to expected format
        responses = []
        if result["success"] and result["responses"]:
            for ai_id, response_data in result["responses"].items():
                if not response_data.get("error", False):
                    responses.append({
                        "socket_id": ai_id,
                        "content": response_data["response"],
                        "timestamp": datetime.utcnow().isoformat(),
                        "metadata": {
                            "role": response_data.get("role", "unknown"),
                            "type": response_data.get("type", "socket")
                        }
                    })
            logger.info(f"Collected {len(responses)} successful responses")
        else:
            logger.warning(f"Team chat failed or no responses: {result.get('error', 'Unknown error')}")
        
        # Process based on moderation mode
        synthesis = None
        consensus = None
        
        if request.moderation_mode == "synthesis" and responses:
            synthesis = await _synthesize_responses(responses)
        elif request.moderation_mode == "consensus" and responses:
            consensus = await _analyze_consensus(responses)
        
        # Calculate elapsed time
        elapsed_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Log summary
        logger.info(f"Team chat complete: {result.get('summary', 'No summary')}")
        logger.info(f"Response count: {len(responses)}, Elapsed time: {elapsed_time:.2f}s")
        
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
        logger.error(f"Team chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team-chat/stream")
async def team_chat_stream(
    message: str = Query(..., description="Message to broadcast"),
    moderation_mode: str = Query("pass_through", description="Moderation mode"),
    timeout: float = Query(2.0, description="Timeout in seconds")
):
    """
    Stream team chat responses using Server-Sent Events.
    
    This endpoint allows real-time streaming of AI responses as they arrive
    from the Greek Chorus AIs.
    """
    async def event_generator():
        try:
            logger.info(f"Starting team chat stream: {message[:100]}...")
            
            # Get MCP tools integration
            integration = get_mcp_tools_integration()
            if not integration:
                integration = MCPToolsIntegrationUnified()
                from ..core.mcp.tools_integration_unified import set_mcp_tools_integration
                set_mcp_tools_integration(integration)
            
            # Send initial connected event
            yield {
                "event": "connected",
                "data": json.dumps({
                    "type": "connected",
                    "message": "Connected to team chat stream"
                })
            }
            
            # Start orchestration in background
            topic = "Stream Discussion"
            task = asyncio.create_task(
                integration.orchestrate_team_chat(
                    topic=topic,
                    specialists=[],  # All available
                    initial_prompt=message,
                    max_rounds=1,
                    orchestration_style=moderation_mode,
                    timeout=timeout
                )
            )
            
            # Stream responses as they arrive
            start_time = datetime.utcnow()
            response_count = 0
            last_check = 0
            
            while not task.done() and (datetime.utcnow() - start_time).total_seconds() < timeout:
                # Check if we have partial results (this is a simplified approach)
                # In a real implementation, we'd modify orchestrate_team_chat to yield results
                await asyncio.sleep(0.5)
                
                # For now, we'll wait for completion and send all at once
                if task.done():
                    result = await task
                    if result["success"] and result["responses"]:
                        for ai_id, response_data in result["responses"].items():
                            if not response_data.get("error", False):
                                response_count += 1
                                event_data = {
                                    "type": "response",
                                    "socket_id": ai_id,
                                    "content": response_data["response"],
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "metadata": {
                                        "role": response_data.get("role", "unknown"),
                                        "type": response_data.get("type", "socket")
                                    },
                                    "index": response_count
                                }
                                
                                yield {
                                    "event": "message",
                                    "data": json.dumps(event_data)
                                }
            
            # Ensure task is complete
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
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
            logger.error(f"Stream error: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(event_generator())


@router.get("/team-chat/sockets")
async def list_team_sockets():
    """List all Greek Chorus AIs available for team chat."""
    try:
        # Get MCP tools integration
        integration = get_mcp_tools_integration()
        if not integration:
            integration = MCPToolsIntegrationUnified()
            from ..core.mcp.tools_integration_unified import set_mcp_tools_integration
            set_mcp_tools_integration(integration)
        
        # List all specialists
        all_specialists = await integration.list_specialists()
        
        # Filter for Greek Chorus AIs (those with socket connections)
        team_sockets = []
        for spec in all_specialists:
            if 'connection' in spec and spec['connection'].get('port'):
                port = spec['connection']['port']
                if 45000 <= port <= 50000:  # Greek Chorus port range
                    team_sockets.append({
                        "socket_id": spec['id'],
                        "model": spec.get('model', 'unknown'),
                        "state": "active" if spec.get('status') == 'healthy' else "inactive",
                        "role": spec.get('role', 'specialist'),
                        "port": port,
                        "capabilities": spec.get('capabilities', [])
                    })
        
        logger.info(f"Found {len(team_sockets)} Greek Chorus AIs for team chat")
        
        return {
            "sockets": team_sockets,
            "count": len(team_sockets),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error listing team sockets: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/team-chat/sockets/{socket_id}/reset")
async def reset_team_socket(socket_id: str):
    """Reset a specific AI specialist (clear context)."""
    try:
        # Get MCP tools integration
        integration = get_mcp_tools_integration()
        if not integration:
            integration = MCPToolsIntegrationUnified()
            from ..core.mcp.tools_integration_unified import set_mcp_tools_integration
            set_mcp_tools_integration(integration)
        
        # Send reset message to the AI
        reset_message = "Please reset your context and start fresh. Forget all previous conversations."
        result = await integration.send_message_to_specialist(
            socket_id,
            reset_message,
            context={"command": "reset"}
        )
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=f"Failed to reset AI: {result.get('error', 'Unknown error')}")
        
        logger.info(f"Reset AI specialist: {socket_id}")
        
        return {
            "socket_id": socket_id,
            "status": "reset",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting AI specialist: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions


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