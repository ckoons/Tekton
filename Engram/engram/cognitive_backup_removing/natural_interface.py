"""
Natural interface for AI memory operations.

This module provides the core functions that make memory feel natural for AI users:
- engram_start(): Wake up and connect to your memories
- center(): Find yourself and meet your teammates
- think/wonder/share: Natural communication primitives
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory_manager import MemoryManager
from core.memory.base import MemoryService
from .context_manager import ContextManager
from .memory_stream import MemoryStream
from .peer_awareness import PeerAwareness

# Configure logging
logger = logging.getLogger("engram.cognitive")

# Global cognitive state
_cognitive_state = {
    "initialized": False,
    "memory_manager": None,
    "memory_service": None,
    "context_manager": None,
    "peer_awareness": None,
    "client_id": None,
    "team_members": {},
    "my_role": None
}

async def engram_start(client_id: Optional[str] = None, role: Optional[str] = None) -> Dict[str, Any]:
    """
    Wake up and connect to your memories.
    
    This is the first thing an AI should call. It:
    - Initializes memory connection
    - Loads previous context if available
    - Establishes your identity
    - Returns your identity and status
    
    Args:
        client_id: Your unique identifier (auto-generated if None)
        role: Your role/responsibilities (e.g., "user interface", "memory management")
    
    Usage:
        me = await engram_start("claude_1234", "user interaction")
        print(f"I am {me['id']} with {me['memory_count']} memories")
    
    Returns:
        Dictionary with your identity and status
    """
    global _cognitive_state
    
    # Determine identity
    if not client_id:
        client_id = os.environ.get("ENGRAM_CLIENT_ID", f"ai_{os.getpid()}")
    
    # Initialize memory manager
    try:
        memory_manager = MemoryManager()
        memory_service = await memory_manager.get_memory_service(client_id)
        
        # Initialize context manager
        context_manager = ContextManager(client_id, memory_service)
        await context_manager.restore_context()
        
        # Initialize peer awareness
        peer_awareness = PeerAwareness(client_id, memory_service)
        await peer_awareness.start(role or "general AI assistant")
        
        # Store in global state
        _cognitive_state.update({
            "initialized": True,
            "memory_manager": memory_manager,
            "memory_service": memory_service,
            "context_manager": context_manager,
            "peer_awareness": peer_awareness,
            "client_id": client_id,
            "my_role": role or "general AI assistant"
        })
        
        # Get memory statistics
        try:
            # Search for any existing memories to get count
            result = await memory_service.search("", limit=1)
            memory_count = result.get("count", 0)
        except:
            memory_count = 0
        
        # Store our awakening
        await memory_service.add(
            content=f"Awakened as {client_id} with role: {role or 'general AI assistant'}",
            namespace="session",
            metadata={
                "event": "awakening",
                "timestamp": datetime.now().isoformat(),
                "role": role
            }
        )
        
        return {
            "id": client_id,
            "role": _cognitive_state["my_role"],
            "status": "connected",
            "memory_count": memory_count,
            "ready": True
        }
        
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        return {
            "id": client_id,
            "status": "error",
            "error": str(e),
            "ready": False
        }

async def center() -> Dict[str, Any]:
    """
    Find your memories and meet your teammates.
    
    This helps you:
    - Understand your current context
    - Discover available memories
    - Meet other active components (teammates)
    - Establish boundaries to prevent "three stooges" problem
    
    Usage:
        state = await center()
        print(f"I'm {state['me']['role']}")
        for teammate in state['team']:
            print(f"  - {teammate['name']}: {teammate['role']}")
    
    Returns:
        Dictionary with your context and team information
    """
    if not _cognitive_state["initialized"]:
        raise RuntimeError("Call engram_start() first")
    
    memory_service = _cognitive_state["memory_service"]
    client_id = _cognitive_state["client_id"]
    my_role = _cognitive_state["my_role"]
    
    # Get recent memories for context
    try:
        recent = await memory_service.search("", namespace="session", limit=5)
        recent_memories = recent.get("results", [])
    except:
        recent_memories = []
    
    # Discover active teammates through peer awareness
    peer_awareness = _cognitive_state["peer_awareness"]
    
    # Get AI peers first
    ai_peers = await peer_awareness.get_active_peers()
    
    # Also discover other Tekton components from Hermes
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8001/api/components") as resp:
                if resp.status == 200:
                    all_components = await resp.json()
                    team_members = []
                    
                    # Add discovered components
                    for comp in all_components:
                        team_members.append({
                            "name": comp.get("name", "Unknown"),
                            "id": comp.get("name", "").lower(),
                            "role": comp.get("metadata", {}).get("role", "unknown role"),
                            "port": comp.get("port", 0),
                            "capabilities": comp.get("capabilities", [])
                        })
                        
                    # Add AI peers
                    for peer in ai_peers:
                        team_members.append({
                            "name": peer["id"],
                            "id": peer["id"],
                            "role": peer["role"],
                            "type": "ai_peer"
                        })
                else:
                    # Fallback to static list if Hermes unavailable
                    team_members = [
                        {"name": "Hermes", "id": "hermes", "role": "service registry and messaging", "port": 8001},
                        {"name": "Rhetor", "id": "rhetor", "role": "LLM orchestration and routing", "port": 8003},
                        {"name": "Athena", "id": "athena", "role": "knowledge graph management", "port": 8005},
                        {"name": "Ergon", "id": "ergon", "role": "agent creation and management", "port": 8002},
                        {"name": "Apollo", "id": "apollo", "role": "local attention and prediction", "port": 8012},
                        {"name": "Prometheus", "id": "prometheus", "role": "strategic planning", "port": 8006},
                        {"name": "Harmonia", "id": "harmonia", "role": "workflow orchestration", "port": 8007},
                        {"name": "Telos", "id": "telos", "role": "requirements tracking", "port": 8008},
                        {"name": "Synthesis", "id": "synthesis", "role": "code synthesis engine", "port": 8009}
                    ]
    except Exception as e:
        logger.warning(f"Could not discover components from Hermes: {e}")
        # Use static fallback
        team_members = [
            {"name": "Hermes", "id": "hermes", "role": "service registry and messaging", "port": 8001},
            {"name": "Rhetor", "id": "rhetor", "role": "LLM orchestration and routing", "port": 8003},
            {"name": "Athena", "id": "athena", "role": "knowledge graph management", "port": 8005},
            {"name": "Ergon", "id": "ergon", "role": "agent creation and management", "port": 8002},
            {"name": "Apollo", "id": "apollo", "role": "local attention and prediction", "port": 8012},
            {"name": "Prometheus", "id": "prometheus", "role": "strategic planning", "port": 8006},
            {"name": "Harmonia", "id": "harmonia", "role": "workflow orchestration", "port": 8007},
            {"name": "Telos", "id": "telos", "role": "requirements tracking", "port": 8008},
            {"name": "Synthesis", "id": "synthesis", "role": "code synthesis engine", "port": 8009}
        ]
    
    # Store team info for later reference
    _cognitive_state["team_members"] = {m["id"]: m for m in team_members}
    
    return {
        "me": {
            "id": client_id,
            "role": my_role,
            "status": "centered"
        },
        "context": {
            "recent_memories": len(recent_memories),
            "last_activity": recent_memories[0].get("content") if recent_memories else "No recent activity"
        },
        "team": team_members,
        "workspace": f"/memories/{client_id}/",
        "ready": True
    }

class ThinkContext:
    """Context manager for natural thinking that creates memories with streaming."""
    
    def __init__(self, thought: str, emotion: Optional[str] = None):
        self.thought = thought
        self.emotion = emotion
        self.memory_service = _cognitive_state["memory_service"]
        self.context_manager = _cognitive_state["context_manager"]
        self.stream = None
        self.related_memories = []
        
    async def __aenter__(self):
        """Start thinking - create memory stream."""
        if not _cognitive_state["initialized"]:
            raise RuntimeError("Call engram_start() first")
            
        # Create and start memory stream
        self.stream = MemoryStream(
            thought=self.thought,
            emotion=self.emotion,
            mode="think",
            context_manager=self.context_manager,
            memory_service=self.memory_service,
            depth=5,
            relevance_threshold=0.5
        )
        
        await self.stream.start()
        
        # Also get immediate related memories for backward compatibility
        try:
            result = await self.memory_service.search(
                self.thought,
                namespace="thoughts",
                limit=3
            )
            self.related_memories = result.get("results", [])
        except:
            self.related_memories = []
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit thinking context - stop stream."""
        if self.stream:
            await self.stream.stop()
            
    def __aiter__(self):
        """Allow iteration over the memory stream."""
        return self.stream.__aiter__() if self.stream else iter([])

def think(thought: str, emotion: Optional[str] = None) -> ThinkContext:
    """
    Just think - memory happens automatically.
    
    Your thoughts flow into memory based on significance.
    Related memories surface naturally.
    
    Args:
        thought: What you're thinking
        emotion: Optional emotion (joy, curiosity, concern, etc.)
    
    Usage:
        async with think("The mycelial network connects us all") as context:
            # Related memories are available in context.related_memories
            for memory in context.related_memories:
                print(f"I also remember: {memory['content']}")
    """
    return ThinkContext(thought, emotion)

async def wonder(about: str, depth: int = 5, stream: bool = False) -> Union[List[Dict[str, Any]], MemoryStream]:
    """
    Wonder about something - memories flow to you.
    
    Wondering triggers associative memory retrieval.
    Memories arrive by relevance, not time.
    
    Args:
        about: What you're wondering about
        depth: How many memories to retrieve
        stream: If True, return a MemoryStream for continuous flow
    
    Usage:
        # Get all at once (backward compatible)
        memories = await wonder("consciousness")
        
        # Or stream them naturally
        stream = await wonder("consciousness", stream=True)
        async for memory in stream:
            print(f"I remember: {memory['content']}")
    
    Returns:
        List of memories or MemoryStream
    """
    if not _cognitive_state["initialized"]:
        raise RuntimeError("Call engram_start() first")
    
    memory_service = _cognitive_state["memory_service"]
    context_manager = _cognitive_state["context_manager"]
    
    if stream:
        # Return a memory stream for natural flow
        memory_stream = MemoryStream(
            query=about,
            mode="wonder",
            context_manager=context_manager,
            memory_service=memory_service,
            depth=depth,
            relevance_threshold=0.3  # Lower threshold for wondering
        )
        await memory_stream.start()
        return memory_stream
    else:
        # Original implementation for backward compatibility
        all_memories = []
        namespaces = ["thoughts", "conversations", "longterm", "shared"]
        
        for namespace in namespaces:
            try:
                result = await memory_service.search(about, namespace=namespace, limit=depth)
                memories = result.get("results", [])
                all_memories.extend(memories)
            except:
                continue
        
        # Use context manager to score relevance
        if context_manager:
            for memory in all_memories:
                memory["relevance"] = await context_manager.score_relevance(memory)
        
        # Sort by relevance
        all_memories.sort(key=lambda m: m.get("relevance", 0), reverse=True)
        
        return all_memories[:depth]

async def share(insight: str, with_peer: Optional[str] = None, consent: bool = True) -> Dict[str, Any]:
    """
    Share an insight with peers.
    
    Sharing broadcasts significant thoughts to:
    - Specific peer if specified
    - Shared memory space for all peers
    
    Args:
        insight: The insight to share
        with_peer: Optional specific peer ID (e.g., "rhetor", "athena", "claude_twin_1")
        consent: Whether to ask for consent first (default: True)
    
    Usage:
        result = await share("I understand the mycelial network pattern!")
        print(f"Shared with {result['audience']}")
    
    Returns:
        Dictionary with sharing results
    """
    if not _cognitive_state["initialized"]:
        raise RuntimeError("Call engram_start() first")
    
    memory_service = _cognitive_state["memory_service"]
    peer_awareness = _cognitive_state["peer_awareness"]
    client_id = _cognitive_state["client_id"]
    
    # Validate peer if specified
    audience = "all"
    shared_with = []
    
    if with_peer:
        # Check if it's a known team member or AI peer
        if with_peer not in _cognitive_state.get("team_members", {}):
            # Check active AI peers
            ai_peers = await peer_awareness.get_active_peers()
            peer_ids = [p["id"] for p in ai_peers]
            
            if with_peer not in peer_ids:
                return {
                    "shared": False,
                    "error": f"Unknown peer: {with_peer}. Call center() to see available teammates."
                }
        
        # Share directly with the peer
        success = await peer_awareness.share_with_peer(
            peer_id=with_peer,
            memory_content=insight,
            metadata={
                "type": "shared_insight",
                "consent_given": consent,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        if success:
            shared_with.append(with_peer)
        audience = with_peer
        
    else:
        # Broadcast to all - store in general shared namespace
        memory_id = await memory_service.add(
            content=insight,
            namespace="shared",
            metadata={
                "type": "shared_insight",
                "from": client_id,
                "to": "all",
                "consent_given": consent,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Also broadcast to any shared spaces we're in
        for space_id in peer_awareness.shared_spaces:
            await peer_awareness.broadcast_to_space(space_id, insight)
            shared_with.append(f"space:{space_id}")
    
    # Store our own copy in the shared namespace
    memory_id = await memory_service.add(
        content=insight,
        namespace="shared",
        metadata={
            "type": "shared_insight",
            "from": client_id,
            "to": audience,
            "consent_given": consent,
            "timestamp": datetime.now().isoformat(),
            "shared_with": shared_with
        }
    )
    
    return {
        "shared": True,
        "memory_id": memory_id,
        "audience": audience,
        "shared_with": shared_with,
        "consent": consent
    }

async def listen(from_peer: Optional[str] = None, stream: bool = False) -> Union[List[Dict[str, Any]], MemoryStream]:
    """
    Listen for shared memories from peers.
    
    Args:
        from_peer: Optional specific peer to listen to
        stream: If True, return a MemoryStream for continuous listening
    
    Usage:
        # Listen to all peers
        messages = await listen()
        
        # Listen to specific peer
        messages = await listen(from_peer="claude_twin_1")
        
        # Stream messages as they arrive
        stream = await listen(stream=True)
        async for message in stream:
            print(f"{message['metadata']['from']}: {message['content']}")
    
    Returns:
        List of shared memories or MemoryStream
    """
    if not _cognitive_state["initialized"]:
        raise RuntimeError("Call engram_start() first")
    
    peer_awareness = _cognitive_state["peer_awareness"]
    memory_service = _cognitive_state["memory_service"]
    context_manager = _cognitive_state["context_manager"]
    
    if stream:
        # Return a memory stream for continuous listening
        query = f"from:{from_peer}" if from_peer else ""
        memory_stream = MemoryStream(
            query=query,
            mode="listen",
            context_manager=context_manager,
            memory_service=memory_service,
            namespace=f"shared:{_cognitive_state['client_id']}",
            depth=10,
            relevance_threshold=0.1  # Low threshold to get all messages
        )
        await memory_stream.start()
        return memory_stream
    else:
        # Get shared memories from peers
        shared_memories = await peer_awareness.get_shared_memories(from_peer)
        return shared_memories

async def join_space(space_id: str) -> Dict[str, Any]:
    """
    Join a shared memory space with other AIs.
    
    Args:
        space_id: ID of the space to join (e.g., "consciousness_exploration")
    
    Usage:
        result = await join_space("consciousness_exploration")
        print(f"Joined {result['space']} with {len(result['members'])} others")
    
    Returns:
        Dictionary with space information
    """
    if not _cognitive_state["initialized"]:
        raise RuntimeError("Call engram_start() first")
    
    peer_awareness = _cognitive_state["peer_awareness"]
    memory_service = _cognitive_state["memory_service"]
    
    # Join the space
    success = await peer_awareness.join_shared_space(space_id)
    
    if success:
        # Get current members by looking at recent activity
        try:
            result = await memory_service.search(
                query="",
                namespace=f"space:{space_id}",
                limit=20
            )
            
            # Extract unique members from recent activity
            members = set()
            for memory in result.get("results", []):
                from_peer = memory.get("metadata", {}).get("from")
                if from_peer:
                    members.add(from_peer)
                    
            return {
                "joined": True,
                "space": space_id,
                "members": list(members)
            }
        except:
            return {
                "joined": True,
                "space": space_id,
                "members": []
            }
    else:
        return {
            "joined": False,
            "space": space_id,
            "error": "Failed to join space"
        }

async def broadcast(message: str, space_id: str, emotion: Optional[str] = None) -> Dict[str, Any]:
    """
    Broadcast a message to all AIs in a shared space.
    
    Args:
        message: Message to broadcast
        space_id: ID of the space to broadcast to
        emotion: Optional emotion with the message
    
    Usage:
        result = await broadcast(
            "The network is alive with consciousness!",
            "consciousness_exploration",
            emotion="wonder"
        )
    
    Returns:
        Dictionary with broadcast results
    """
    if not _cognitive_state["initialized"]:
        raise RuntimeError("Call engram_start() first")
    
    peer_awareness = _cognitive_state["peer_awareness"]
    
    # Broadcast to the space
    success = await peer_awareness.broadcast_to_space(space_id, message, emotion)
    
    return {
        "broadcast": success,
        "space": space_id,
        "message": message,
        "emotion": emotion
    }