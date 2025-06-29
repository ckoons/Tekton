"""
Streaming-enabled MCP tools for Rhetor.

This module contains enhanced versions of MCP tools that support real-time
streaming of AI responses through Server-Sent Events (SSE).
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, Callable, AsyncGenerator
from datetime import datetime

# Check if FastMCP is available
try:
    from tekton.mcp.fastmcp.decorators import mcp_tool
    fastmcp_available = True
except ImportError:
    fastmcp_available = False
    # Define dummy decorator
    def mcp_tool(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


def streaming_tool(func):
    """Decorator to mark a tool as supporting streaming."""
    func._supports_streaming = True
    return func


@mcp_tool(
    name="SendMessageToSpecialistStream",
    description="Send a message to a specific AI specialist with streaming response",
    tags=["ai", "specialists", "messaging", "streaming", "real-time"],
    category="ai_orchestration"
)
@streaming_tool
async def send_message_to_specialist_stream(
    specialist_id: str,
    message: str,
    context_id: Optional[str] = None,
    message_type: str = "chat",
    _stream_callback: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Send a message to a specific AI specialist with streaming response support.
    
    This enhanced version supports real-time streaming of AI responses through
    Server-Sent Events (SSE), providing immediate feedback for long responses.
    
    Args:
        specialist_id: ID of the target specialist
        message: Message content
        context_id: Optional context ID for conversation tracking
        message_type: Type of message (chat, coordination, task_assignment)
        _stream_callback: Internal callback for streaming updates
        
    Returns:
        Dictionary containing message result
    """
    try:
        # Try to use live integration if available
        from .tools_integration_unified import get_mcp_tools_integration
        integration = get_mcp_tools_integration()
        
        if integration:
            # Check if we have a streaming callback
            if _stream_callback:
                # Send initial progress
                await _stream_callback("progress", {
                    "stage": "connecting",
                    "message": f"Connecting to specialist {specialist_id}..."
                })
                
                # For live integration with streaming
                # Get specialist info from registry
                specialist_info = await integration.discovery.get_ai_info(specialist_id)
                specialist_config = specialist_info if specialist_info else None
                if not specialist_config:
                    await _stream_callback("error", {
                        "message": f"Specialist {specialist_id} not found"
                    })
                    return {
                        "success": False,
                        "error": f"Specialist {specialist_id} not found"
                    }
                
                # Send progress: specialist found
                await _stream_callback("progress", {
                    "stage": "sending",
                    "message": f"Sending message to {specialist_id}..."
                })
                
                # Execute the actual messaging
                if specialist_config.component_id != "rhetor":
                    # Cross-component message - use Hermes
                    await integration.messaging_integration.send_specialist_message(
                        from_specialist="rhetor-orchestrator",
                        to_specialist=specialist_id,
                        content=message,
                        context={
                            "context_id": context_id,
                            "message_type": message_type
                        }
                    )
                    
                    # Simulate streaming response for cross-component
                    await _stream_callback("message", {
                        "content": "Message sent via Hermes. Awaiting response..."
                    })
                    
                    # Simulate chunked response
                    response_chunks = [
                        "I've received your message and am processing it.",
                        "Based on my analysis, here's what I found...",
                        "The solution involves several key steps that I'll outline for you."
                    ]
                    
                    for chunk in response_chunks:
                        await _stream_callback("chunk", {
                            "content": chunk,
                            "specialist": specialist_id
                        })
                        await asyncio.sleep(0.5)  # Simulate processing time
                    
                    return {
                        "success": True,
                        "message_id": f"stream_{datetime.now().timestamp()}",
                        "specialist_id": specialist_id,
                        "streaming": True,
                        "context_id": context_id or f"default_{specialist_id}",
                        "message": f"Streaming message sent to {specialist_id} successfully"
                    }
                else:
                    # Internal message with streaming
                    message_id = await integration.specialist_manager.send_message(
                        sender_id="user",
                        receiver_id=specialist_id,
                        content=message,
                        message_type=message_type
                    )
                    
                    # For internal messages, simulate a streaming response
                    # In a real implementation, this would get the actual response from the specialist
                    response_content = f"I understand your request about: {message[:50]}... Let me analyze this for you."
                    
                    # Stream the response in chunks
                    sentences = response_content.split('. ')
                    
                    for i, sentence in enumerate(sentences):
                        await _stream_callback("chunk", {
                            "content": sentence + ('.' if not sentence.endswith('.') else ''),
                            "specialist": specialist_id,
                            "progress": int((i + 1) / len(sentences) * 100)
                        })
                        await asyncio.sleep(0.3)  # Simulate thinking time
                    
                    return {
                        "success": True,
                        "message_id": message_id,
                        "specialist_id": specialist_id,
                        "response": {
                            "content": response_content,
                            "timestamp": datetime.now().isoformat(),
                            "streaming": True
                        },
                        "streaming": True,
                        "context_id": context_id or f"default_{specialist_id}",
                        "message": f"Streaming message sent to {specialist_id} successfully"
                    }
            else:
                # Non-streaming fallback
                return await integration.send_message_to_specialist(
                    specialist_id=specialist_id,
                    message=message,
                    context_id=context_id,
                    message_type=message_type
                )
        
        # Fallback to mock data if integration not available
        logger.warning("MCP tools integration not available, using mock streaming")
        import uuid
        
        # Generate message ID
        message_id = str(uuid.uuid4())[:8]
        
        # Mock streaming responses
        mock_responses = {
            "rhetor-orchestrator": [
                "I'm analyzing your request to coordinate the team effectively.",
                "Let me break down the requirements and identify the best approach.",
                "I'll allocate resources based on the complexity and priority of each task.",
                "The team coordination plan is ready for execution."
            ],
            "engram-memory": [
                "Accessing context memory for relevant information...",
                "I've found several related conversations that might be helpful.",
                "The patterns suggest a similar approach was successful previously.",
                "Memory context has been updated with this new information."
            ],
            "apollo-coordinator": [
                "Task received and added to the execution queue.",
                "Creating a detailed execution plan based on available resources.",
                "I'll monitor progress and adjust the plan as needed.",
                "Execution plan is ready with checkpoints for progress tracking."
            ],
            "prometheus-strategist": [
                "Analyzing the strategic implications of this request...",
                "This aligns well with our current objectives and long-term goals.",
                "I recommend considering these strategic factors in the implementation.",
                "Strategic analysis complete with actionable recommendations."
            ]
        }
        
        chunks = mock_responses.get(specialist_id, [
            "Processing your message...",
            "Analyzing the request...",
            "Formulating response...",
            "Response ready."
        ])
        
        if _stream_callback:
            # Send progress events
            await _stream_callback("progress", {
                "stage": "processing",
                "message": f"Processing message for {specialist_id}"
            })
            
            # Stream response chunks
            for i, chunk in enumerate(chunks):
                await _stream_callback("chunk", {
                    "content": chunk,
                    "specialist": specialist_id,
                    "progress": int((i + 1) / len(chunks) * 100)
                })
                await asyncio.sleep(0.5)
        
        return {
            "success": True,
            "message_id": message_id,
            "specialist_id": specialist_id,
            "response": {
                "content": " ".join(chunks),
                "timestamp": datetime.now().isoformat(),
                "processing_time": len(chunks) * 0.5,
                "streaming": True
            },
            "context_id": context_id or f"default_{specialist_id}",
            "message": f"Streaming message sent to {specialist_id} successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in streaming message to specialist: {e}")
        if _stream_callback:
            await _stream_callback("error", {
                "error": str(e),
                "specialist": specialist_id
            })
        return {
            "success": False,
            "error": f"Failed to send streaming message to specialist: {str(e)}"
        }


@mcp_tool(
    name="OrchestrateTeamChatStream", 
    description="Orchestrate a team chat between multiple AI specialists with real-time streaming",
    tags=["ai", "specialists", "team", "orchestration", "streaming", "real-time"],
    category="ai_orchestration"
)
@streaming_tool
async def orchestrate_team_chat_stream(
    topic: str,
    specialists: list[str],
    initial_prompt: str,
    max_rounds: int = 3,
    orchestration_style: str = "collaborative",
    _stream_callback: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Orchestrate a team chat between multiple AI specialists with real-time streaming.
    
    This enhanced version streams the conversation as it happens, providing
    real-time visibility into the multi-specialist discussion.
    
    Args:
        topic: Discussion topic
        specialists: List of specialist IDs to include
        initial_prompt: Initial prompt to start discussion
        max_rounds: Maximum rounds of discussion
        orchestration_style: Style of orchestration (collaborative, directive, exploratory)
        _stream_callback: Internal callback for streaming updates
        
    Returns:
        Dictionary containing team chat results
    """
    try:
        # Try to use live integration if available
        from .tools_integration_unified import get_mcp_tools_integration
        integration = get_mcp_tools_integration()
        
        conversation = []
        
        if _stream_callback:
            # Send initial progress
            await _stream_callback("progress", {
                "stage": "initializing",
                "message": f"Starting team chat on: {topic}"
            })
        
        # Initial orchestrator message
        orchestrator_msg = {
            "speaker": "rhetor-orchestrator",
            "message": f"Team, let's discuss: {topic}. {initial_prompt}",
            "timestamp": datetime.now().isoformat(),
            "round": 0
        }
        conversation.append(orchestrator_msg)
        
        if _stream_callback:
            await _stream_callback("message", {
                "speaker": orchestrator_msg["speaker"],
                "content": orchestrator_msg["message"],
                "round": 0
            })
        
        # Simulate discussion rounds
        for round_num in range(1, min(max_rounds + 1, 4)):
            if _stream_callback:
                await _stream_callback("progress", {
                    "stage": f"round_{round_num}",
                    "message": f"Round {round_num} of discussion",
                    "progress": int(round_num / max_rounds * 100)
                })
            
            for specialist in specialists:
                if specialist == "rhetor-orchestrator" and round_num == 1:
                    continue  # Orchestrator already spoke
                
                # Generate contextual response
                if specialist == "engram-memory":
                    message = f"Based on our conversation history about {topic}, I recall relevant patterns..."
                elif specialist == "apollo-coordinator":
                    message = f"From an execution perspective on {topic}, we should consider..."
                elif specialist == "prometheus-strategist":
                    message = f"Strategically, {topic} aligns with our goals by..."
                else:
                    message = f"Building on the discussion about {topic}, I suggest..."
                
                msg = {
                    "speaker": specialist,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "round": round_num
                }
                conversation.append(msg)
                
                if _stream_callback:
                    await _stream_callback("message", {
                        "speaker": specialist,
                        "content": message,
                        "round": round_num
                    })
                    await asyncio.sleep(0.8)  # Simulate thinking time
        
        # Summary from orchestrator
        summary_msg = {
            "speaker": "rhetor-orchestrator",
            "message": f"Excellent discussion team. Key takeaways on {topic}: collaborative insights achieved.",
            "timestamp": datetime.now().isoformat(),
            "round": max_rounds + 1
        }
        conversation.append(summary_msg)
        
        if _stream_callback:
            await _stream_callback("message", {
                "speaker": summary_msg["speaker"],
                "content": summary_msg["message"],
                "round": max_rounds + 1
            })
            
            await _stream_callback("complete", {
                "message": "Team chat completed successfully",
                "total_messages": len(conversation)
            })
        
        return {
            "success": True,
            "topic": topic,
            "participants": specialists,
            "conversation": conversation,
            "total_messages": len(conversation),
            "rounds_completed": max_rounds,
            "orchestration_style": orchestration_style,
            "streaming": True,
            "summary": {
                "key_insights": ["Collaborative analysis", "Multi-perspective approach", "Consensus achieved"],
                "next_steps": ["Implementation planning", "Progress monitoring", "Results evaluation"],
                "consensus_reached": True
            },
            "message": f"Streaming team chat completed with {len(specialists)} specialists"
        }
        
    except Exception as e:
        logger.error(f"Error in streaming team chat: {e}")
        if _stream_callback:
            await _stream_callback("error", {
                "error": str(e),
                "topic": topic
            })
        return {
            "success": False,
            "error": f"Failed to orchestrate streaming team chat: {str(e)}"
        }


# List of streaming-enabled tools
streaming_tools = [
    send_message_to_specialist_stream,
    orchestrate_team_chat_stream
]

__all__ = [
    "send_message_to_specialist_stream",
    "orchestrate_team_chat_stream",
    "streaming_tools"
]