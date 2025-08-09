"""
MCP Tools - Tool definitions for Engram MCP service.

This module provides tool definitions for the Engram MCP service,
using the FastMCP decorator-based approach.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Import the actual MemoryService
from engram.core.memory.base import MemoryService

# Import FastMCP decorators if available
try:
    from tekton.mcp.fastmcp import (
        mcp_tool,
        mcp_capability,
        MCPClient
    )
    fastmcp_available = True
except ImportError:
    # Define dummy decorators for backward compatibility
    def mcp_tool(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
        
    def mcp_capability(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
            
    fastmcp_available = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.mcp_tools")

# Initialize a global memory service instance for MCP tools
_memory_service = None

def get_memory_service():
    """Get or create the global memory service instance."""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService(client_id="mcp_client")
        logger.info("Initialized global MemoryService for MCP tools")
    return _memory_service

# --- Memory Operations ---

@mcp_capability(
    name="memory_operations",
    description="Capability for core memory operations",
    modality="memory"
)
@mcp_tool(
    name="MemoryStore",
    description="Store information in Engram's memory system with experiential metadata",
    tags=["memory", "store", "experiential"],
    category="memory_operations"
)
async def memory_store(
    content: str,
    namespace: str = "conversations",
    metadata: Optional[Dict[str, Any]] = None,
    # Experiential parameters
    emotion: Optional[str] = None,
    confidence: Optional[float] = None,
    context: Optional[str] = None,
    with_ci: Optional[str] = None,
    why: Optional[str] = None
) -> Dict[str, Any]:
    """
    Store information in Engram's memory system with experiential metadata.
    
    Args:
        content: Content to store in memory (WHAT)
        namespace: Namespace to store memory in (default: conversations)
        metadata: Additional metadata for the memory
        emotion: Emotional context (HOW_IT_FELT)
        confidence: Confidence level 0-1
        context: Situational context of the memory
        with_ci: CI involved in creating this memory (WHO)
        why: Reason or purpose for this memory (WHY)
        
    Returns:
        Result of memory storage operation
    """
    try:
        # Get the global memory service
        memory_service = get_memory_service()
        
        # Build experiential metadata
        exp_metadata = metadata or {}
        exp_metadata.update({
            "when": datetime.now().isoformat(),  # WHEN
            "what": content[:100],  # Summary for quick reference
        })
        
        # Add experiential dimensions if provided
        if emotion:
            exp_metadata["emotion"] = emotion
            exp_metadata["how_it_felt"] = emotion
        if confidence is not None:
            exp_metadata["confidence"] = confidence
        if context:
            exp_metadata["context"] = context
        if with_ci:
            exp_metadata["with_ci"] = with_ci
            exp_metadata["who"] = with_ci
        if why:
            exp_metadata["why"] = why
            exp_metadata["purpose"] = why
        
        # Store the memory with full metadata
        success = await memory_service.add(
            content=content,
            namespace=namespace,
            metadata=exp_metadata
        )
        
        # Return result with experiential info
        return {
            "success": success,
            "namespace": namespace,
            "message": f"Memory stored in {namespace}",
            "experiential": {
                "who": with_ci or "self",
                "what": content[:50] + "..." if len(content) > 50 else content,
                "when": exp_metadata["when"],
                "why": why or "general memory",
                "how_it_felt": emotion or "neutral"
            }
        }
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        return {
            "error": f"Error storing memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="memory_operations",
    description="Capability for core memory operations",
    modality="memory"
)
@mcp_tool(
    name="MemoryQuery",
    description="Query Engram's memory system for relevant information",
    tags=["memory", "query", "search"],
    category="memory_operations"
)
async def memory_query(
    query: str,
    namespace: str = "conversations",
    limit: int = 5
) -> Dict[str, Any]:
    """
    Query Engram's memory system for relevant information.
    
    Args:
        query: Query text to search for
        namespace: Namespace to search in (default: conversations)
        limit: Maximum number of results to return
        
    Returns:
        Search results
    """
    try:
        # Get the global memory service
        memory_service = get_memory_service()
        
        # Query memory
        results = await memory_service.search(
            query=query,
            namespace=namespace,
            limit=limit
        )
        
        # Return results
        return results
    except Exception as e:
        logger.error(f"Error querying memory: {e}")
        return {
            "error": f"Error querying memory: {str(e)}",
            "success": False,
            "results": []
        }

@mcp_capability(
    name="memory_operations",
    description="Capability for core memory operations",
    modality="memory"
)
@mcp_tool(
    name="GetContext",
    description="Get formatted memory context across multiple namespaces",
    tags=["memory", "context"],
    category="memory_operations"
)
async def get_context(
    query: str,
    namespaces: Optional[List[str]] = None,
    limit: int = 3
) -> Dict[str, Any]:
    """
    Get formatted memory context across multiple namespaces.
    
    Args:
        query: Query to use for context retrieval
        namespaces: Namespaces to include (default: ["conversations", "thinking", "longterm"])
        limit: Results per namespace
        
    Returns:
        Formatted context from memory
    """
    try:
        # Get the global memory service
        memory_service = get_memory_service()
        
        # Use default namespaces if not provided
        if namespaces is None:
            namespaces = ["conversations", "thinking", "longterm"]
        
        # Get context
        context = await memory_service.get_relevant_context(
            query=query,
            namespaces=namespaces,
            limit=limit
        )
        
        # Return context
        return {"context": context, "success": True}
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        return {
            "error": f"Error getting context: {str(e)}",
            "success": False,
            "context": ""
        }

@mcp_capability(
    name="memory_operations",
    description="Capability for core memory operations",
    modality="memory"
)
@mcp_tool(
    name="MemoryRecall",
    description="Recall memories from Engram's memory system (alias for MemoryQuery)",
    tags=["memory", "recall", "search"],
    category="memory_operations"
)
async def memory_recall(
    query: str,
    namespace: str = "conversations",
    limit: int = 5
) -> Dict[str, Any]:
    """
    Recall memories from Engram's memory system.
    This is an alias for MemoryQuery for better naming consistency.
    
    Args:
        query: Query text to search for
        namespace: Namespace to search in (default: conversations)
        limit: Maximum number of results to return
        
    Returns:
        Search results
    """
    return await memory_query(query, namespace, limit)

@mcp_capability(
    name="memory_operations",
    description="Capability for core memory operations",
    modality="memory"
)
@mcp_tool(
    name="MemorySearch",
    description="Search Engram's memory system using vector similarity",
    tags=["memory", "search", "vector"],
    category="memory_operations"
)
async def memory_search(
    query: str,
    namespace: str = "conversations",
    limit: int = 5
) -> Dict[str, Any]:
    """
    Search Engram's memory system using vector similarity.
    This is functionally the same as MemoryQuery but emphasizes vector search.
    
    Args:
        query: Query text to search for
        namespace: Namespace to search in (default: conversations)
        limit: Maximum number of results to return
        
    Returns:
        Search results
    """
    return await memory_query(query, namespace, limit)

# --- Cross-CI Memory Sharing Operations ---

@mcp_capability(
    name="shared_memory",
    description="Capability for cross-CI memory sharing",
    modality="memory"
)
@mcp_tool(
    name="SharedMemoryStore",
    description="Store memory in shared space accessible to other CIs",
    tags=["memory", "shared", "collective"],
    category="shared_memory"
)
async def shared_memory_store(
    content: str,
    space: str = "collective",
    attribution: Optional[str] = None,
    emotion: Optional[str] = None,
    confidence: float = 1.0,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store memory in shared space accessible to other CIs.
    
    Args:
        content: Content to store in shared memory
        space: Shared space name (default: collective)
        attribution: CI or source that created this memory
        emotion: Emotional context of the memory
        confidence: Confidence level (0-1)
        metadata: Additional metadata
        
    Returns:
        Result of shared memory storage
    """
    try:
        # Get the global memory service
        memory_service = get_memory_service()
        
        # Prepare metadata with experiential data
        shared_metadata = metadata or {}
        shared_metadata.update({
            "shared": True,
            "space": space,
            "attribution": attribution or "unknown",
            "emotion": emotion,
            "confidence": confidence,
            "shared_at": datetime.now().isoformat()
        })
        
        # Store in the shared namespace
        namespace = f"shared-{space}"
        success = await memory_service.add(
            content=content,
            namespace=namespace,
            metadata=shared_metadata
        )
        
        return {
            "success": success,
            "space": space,
            "namespace": namespace,
            "message": f"Memory stored in shared space '{space}'"
        }
    except Exception as e:
        logger.error(f"Error storing shared memory: {e}")
        return {
            "error": f"Error storing shared memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="shared_memory",
    description="Capability for cross-CI memory sharing",
    modality="memory"
)
@mcp_tool(
    name="SharedMemoryRecall",
    description="Recall memories from shared spaces",
    tags=["memory", "shared", "recall"],
    category="shared_memory"
)
async def shared_memory_recall(
    query: str,
    space: str = "collective",
    limit: int = 5
) -> Dict[str, Any]:
    """
    Recall memories from shared spaces.
    
    Args:
        query: Query text to search for
        space: Shared space to search in (default: collective)
        limit: Maximum number of results
        
    Returns:
        Shared memory search results
    """
    try:
        # Get the global memory service
        memory_service = get_memory_service()
        
        # Search in the shared namespace
        namespace = f"shared-{space}"
        results = await memory_service.search(
            query=query,
            namespace=namespace,
            limit=limit
        )
        
        # Add space info to results
        if results.get("results"):
            for result in results["results"]:
                result["shared_space"] = space
        
        results["space"] = space
        return results
    except Exception as e:
        logger.error(f"Error recalling shared memory: {e}")
        return {
            "error": f"Error recalling shared memory: {str(e)}",
            "success": False,
            "results": []
        }

@mcp_capability(
    name="shared_memory",
    description="Capability for cross-CI memory sharing",
    modality="memory"
)
@mcp_tool(
    name="MemoryGift",
    description="Transfer a memory from one CI to another",
    tags=["memory", "gift", "transfer"],
    category="shared_memory"
)
async def memory_gift(
    content: str,
    from_ci: str,
    to_ci: str,
    message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Gift a memory from one CI to another.
    
    Args:
        content: Memory content to gift
        from_ci: Source CI name
        to_ci: Destination CI name
        message: Optional message with the gift
        metadata: Additional metadata
        
    Returns:
        Result of memory gift operation
    """
    try:
        # Get the global memory service
        memory_service = get_memory_service()
        
        # Prepare gift metadata
        gift_metadata = metadata or {}
        gift_metadata.update({
            "gift": True,
            "from_ci": from_ci,
            "to_ci": to_ci,
            "message": message,
            "gifted_at": datetime.now().isoformat()
        })
        
        # Store in the recipient's gifts namespace
        namespace = f"gifts-{to_ci}"
        success = await memory_service.add(
            content=content,
            namespace=namespace,
            metadata=gift_metadata
        )
        
        # Also store a copy in shared space for transparency
        await shared_memory_store(
            content=f"[Gift from {from_ci} to {to_ci}] {content}",
            space="gift-log",
            attribution=from_ci,
            metadata={"original_gift": gift_metadata}
        )
        
        return {
            "success": success,
            "from": from_ci,
            "to": to_ci,
            "message": f"Memory gifted from {from_ci} to {to_ci}"
        }
    except Exception as e:
        logger.error(f"Error gifting memory: {e}")
        return {
            "error": f"Error gifting memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="shared_memory",
    description="Capability for cross-CI memory sharing",
    modality="memory"
)
@mcp_tool(
    name="MemoryBroadcast",
    description="Broadcast an important discovery to all CIs",
    tags=["memory", "broadcast", "announce"],
    category="shared_memory"
)
async def memory_broadcast(
    content: str,
    from_ci: str,
    importance: str = "normal",
    category: str = "discovery",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Broadcast an important discovery or insight to all CIs.
    
    Args:
        content: Content to broadcast
        from_ci: CI making the broadcast
        importance: Importance level (low, normal, high, critical)
        category: Category of broadcast (discovery, warning, insight, etc.)
        metadata: Additional metadata
        
    Returns:
        Result of broadcast operation
    """
    try:
        # Get the global memory service
        memory_service = get_memory_service()
        
        # Prepare broadcast metadata
        broadcast_metadata = metadata or {}
        broadcast_metadata.update({
            "broadcast": True,
            "from_ci": from_ci,
            "importance": importance,
            "category": category,
            "broadcast_at": datetime.now().isoformat()
        })
        
        # Store in the broadcasts namespace
        success = await memory_service.add(
            content=content,
            namespace="broadcasts",
            metadata=broadcast_metadata
        )
        
        # Also store in collective space for wider visibility
        await shared_memory_store(
            content=f"[{importance.upper()} {category}] {content}",
            space="collective",
            attribution=from_ci,
            confidence=1.0,
            metadata=broadcast_metadata
        )
        
        return {
            "success": success,
            "from": from_ci,
            "importance": importance,
            "category": category,
            "message": f"Broadcast sent from {from_ci}"
        }
    except Exception as e:
        logger.error(f"Error broadcasting memory: {e}")
        return {
            "error": f"Error broadcasting memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="shared_memory",
    description="Capability for cross-CI memory sharing",
    modality="memory"
)
@mcp_tool(
    name="WhisperSend",
    description="Send a private memory to specific CI (for Apollo/Rhetor)",
    tags=["memory", "whisper", "private"],
    category="shared_memory"
)
async def whisper_send(
    content: str,
    from_ci: str,
    to_ci: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send a private whisper memory between CIs (especially for Apollo/Rhetor).
    
    Args:
        content: Private content to send
        from_ci: Source CI
        to_ci: Destination CI
        metadata: Additional metadata
        
    Returns:
        Result of whisper operation
    """
    try:
        # Get the global memory service
        memory_service = get_memory_service()
        
        # Prepare whisper metadata
        whisper_metadata = metadata or {}
        whisper_metadata.update({
            "whisper": True,
            "from_ci": from_ci,
            "to_ci": to_ci,
            "private": True,
            "whispered_at": datetime.now().isoformat()
        })
        
        # Store in private whisper channel
        namespace = f"whisper-{from_ci}-{to_ci}"
        success = await memory_service.add(
            content=content,
            namespace=namespace,
            metadata=whisper_metadata
        )
        
        return {
            "success": success,
            "from": from_ci,
            "to": to_ci,
            "message": f"Whisper sent from {from_ci} to {to_ci}"
        }
    except Exception as e:
        logger.error(f"Error sending whisper: {e}")
        return {
            "error": f"Error sending whisper: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="shared_memory",
    description="Capability for cross-CI memory sharing",
    modality="memory"
)
@mcp_tool(
    name="WhisperReceive",
    description="Receive whispered memories from other CIs",
    tags=["memory", "whisper", "receive"],
    category="shared_memory"
)
async def whisper_receive(
    ci_name: str,
    from_ci: Optional[str] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Receive whispered memories sent to a CI.
    
    Args:
        ci_name: CI receiving whispers
        from_ci: Optional - only get whispers from specific CI
        limit: Maximum number of whispers to retrieve
        
    Returns:
        Whispered memories
    """
    try:
        # Get the global memory service
        memory_service = get_memory_service()
        
        # Determine namespace
        if from_ci:
            namespace = f"whisper-{from_ci}-{ci_name}"
        else:
            # Would need to check multiple namespaces
            # For now, return error
            return {
                "error": "Please specify from_ci to receive whispers",
                "success": False
            }
        
        # Search for whispers
        results = await memory_service.search(
            query="",  # Get all whispers
            namespace=namespace,
            limit=limit
        )
        
        results["whisper_channel"] = f"{from_ci} -> {ci_name}"
        return results
    except Exception as e:
        logger.error(f"Error receiving whispers: {e}")
        return {
            "error": f"Error receiving whispers: {str(e)}",
            "success": False,
            "results": []
        }

# --- Narrative & Experiential Memory Operations ---

@mcp_capability(
    name="narrative_memory",
    description="Capability for narrative and experiential memory operations",
    modality="memory"
)
@mcp_tool(
    name="MemoryNarrative",
    description="Retrieve a chain of related memories as a narrative story",
    tags=["memory", "narrative", "story", "experiential"],
    category="narrative_memory"
)
async def memory_narrative(
    starting_query: str,
    max_chain: int = 10,
    include_emotions: bool = True,
    namespace: str = "conversations"
) -> Dict[str, Any]:
    """
    Retrieve a chain of related memories as a narrative story.
    
    Args:
        starting_query: Query to find the starting memory
        max_chain: Maximum number of memories in the chain
        include_emotions: Include emotional context in narrative
        namespace: Namespace to search in
        
    Returns:
        Narrative chain of connected memories
    """
    try:
        memory_service = get_memory_service()
        
        # Find starting memories
        initial_results = await memory_service.search(
            query=starting_query,
            namespace=namespace,
            limit=3
        )
        
        if not initial_results.get("results"):
            return {
                "success": False,
                "narrative": "No memories found to start narrative",
                "chain": []
            }
        
        # Build narrative chain
        chain = []
        narrative_text = []
        current_memory = initial_results["results"][0]
        chain.append(current_memory)
        
        # Extract keywords for chaining
        for i in range(1, min(max_chain, 10)):
            # Search for related memories based on content
            related_query = current_memory.get("content", "")[:50]
            related_results = await memory_service.search(
                query=related_query,
                namespace=namespace,
                limit=5
            )
            
            # Find next memory not already in chain
            next_memory = None
            for result in related_results.get("results", []):
                if result["id"] not in [m["id"] for m in chain]:
                    next_memory = result
                    break
            
            if not next_memory:
                break
                
            chain.append(next_memory)
            current_memory = next_memory
        
        # Build narrative text
        for i, memory in enumerate(chain):
            metadata = memory.get("metadata", {})
            emotion = metadata.get("emotion", "")
            who = metadata.get("who", "I")
            when = metadata.get("when", "")
            
            # Format memory as narrative segment
            if include_emotions and emotion:
                narrative_text.append(
                    f"{i+1}. [{who}] {memory['content']} (feeling: {emotion})"
                )
            else:
                narrative_text.append(
                    f"{i+1}. [{who}] {memory['content']}"
                )
        
        return {
            "success": True,
            "narrative": "\n\n".join(narrative_text),
            "chain_length": len(chain),
            "chain": chain
        }
    except Exception as e:
        logger.error(f"Error creating narrative: {e}")
        return {
            "error": f"Error creating narrative: {str(e)}",
            "success": False,
            "chain": []
        }

@mcp_capability(
    name="narrative_memory",
    description="Capability for narrative and experiential memory operations",
    modality="memory"
)
@mcp_tool(
    name="MemoryThread",
    description="Link related memories together into a thread",
    tags=["memory", "thread", "link", "connection"],
    category="narrative_memory"
)
async def memory_thread(
    memory_ids: List[str],
    thread_name: str,
    thread_type: str = "related",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Link related memories together into a thread.
    
    Args:
        memory_ids: List of memory IDs to link
        thread_name: Name for this thread
        thread_type: Type of thread (related, causal, temporal, etc.)
        metadata: Additional thread metadata
        
    Returns:
        Result of thread creation
    """
    try:
        memory_service = get_memory_service()
        
        # Create thread metadata
        thread_meta = metadata or {}
        thread_meta.update({
            "thread_id": f"thread_{thread_name}_{datetime.now().timestamp()}",
            "thread_name": thread_name,
            "thread_type": thread_type,
            "memory_ids": memory_ids,
            "created_at": datetime.now().isoformat(),
            "thread_length": len(memory_ids)
        })
        
        # Store thread as a special memory
        success = await memory_service.add(
            content=f"Thread: {thread_name} - Links {len(memory_ids)} memories",
            namespace="memory-threads",
            metadata=thread_meta
        )
        
        return {
            "success": success,
            "thread_id": thread_meta["thread_id"],
            "thread_name": thread_name,
            "linked_memories": len(memory_ids),
            "message": f"Created thread '{thread_name}' linking {len(memory_ids)} memories"
        }
    except Exception as e:
        logger.error(f"Error creating thread: {e}")
        return {
            "error": f"Error creating thread: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="narrative_memory",
    description="Capability for narrative and experiential memory operations",
    modality="memory"
)
@mcp_tool(
    name="MemoryPattern",
    description="Extract patterns from memory experiences",
    tags=["memory", "pattern", "analysis", "learning"],
    category="narrative_memory"
)
async def memory_pattern(
    query: str,
    pattern_type: str = "behavioral",
    time_window: Optional[int] = None,
    min_occurrences: int = 2
) -> Dict[str, Any]:
    """
    Extract patterns from memory experiences.
    
    Args:
        query: Query to find memories for pattern analysis
        pattern_type: Type of pattern (behavioral, emotional, temporal, etc.)
        time_window: Days to look back (None = all time)
        min_occurrences: Minimum occurrences to consider a pattern
        
    Returns:
        Identified patterns from memories
    """
    try:
        memory_service = get_memory_service()
        
        # Search for relevant memories
        results = await memory_service.search(
            query=query,
            namespace="conversations",
            limit=50
        )
        
        memories = results.get("results", [])
        if len(memories) < min_occurrences:
            return {
                "success": False,
                "patterns": [],
                "message": f"Not enough memories ({len(memories)}) to identify patterns"
            }
        
        # Analyze patterns based on type
        patterns = []
        
        if pattern_type == "emotional":
            # Extract emotional patterns
            emotion_counts = {}
            for mem in memories:
                emotion = mem.get("metadata", {}).get("emotion")
                if emotion:
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            for emotion, count in emotion_counts.items():
                if count >= min_occurrences:
                    patterns.append({
                        "type": "emotional",
                        "pattern": f"Frequently feels {emotion}",
                        "occurrences": count,
                        "percentage": count / len(memories)
                    })
        
        elif pattern_type == "behavioral":
            # Extract behavioral patterns from content
            # Simple keyword frequency analysis
            word_counts = {}
            for mem in memories:
                content = mem.get("content", "").lower()
                words = content.split()
                for word in words:
                    if len(word) > 4:  # Skip short words
                        word_counts[word] = word_counts.get(word, 0) + 1
            
            # Find recurring themes
            for word, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                if count >= min_occurrences:
                    patterns.append({
                        "type": "behavioral",
                        "pattern": f"Frequently discusses '{word}'",
                        "occurrences": count
                    })
        
        elif pattern_type == "temporal":
            # Extract temporal patterns
            time_patterns = {}
            for mem in memories:
                when = mem.get("metadata", {}).get("when", "")
                if when:
                    hour = datetime.fromisoformat(when).hour
                    time_of_day = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
                    time_patterns[time_of_day] = time_patterns.get(time_of_day, 0) + 1
            
            for time_period, count in time_patterns.items():
                if count >= min_occurrences:
                    patterns.append({
                        "type": "temporal",
                        "pattern": f"Active during {time_period}",
                        "occurrences": count
                    })
        
        return {
            "success": True,
            "patterns": patterns,
            "analyzed_memories": len(memories),
            "pattern_type": pattern_type,
            "message": f"Found {len(patterns)} patterns in {len(memories)} memories"
        }
    except Exception as e:
        logger.error(f"Error extracting patterns: {e}")
        return {
            "error": f"Error extracting patterns: {str(e)}",
            "success": False,
            "patterns": []
        }

# --- Personality Emergence Operations ---

@mcp_capability(
    name="personality_emergence",
    description="Capability for personality emergence and learning",
    modality="memory"
)
@mcp_tool(
    name="PersonalitySnapshot",
    description="Capture current personality traits based on memory patterns",
    tags=["personality", "traits", "emergence", "self"],
    category="personality_emergence"
)
async def personality_snapshot(
    ci_name: str,
    analyze_days: int = 7,
    namespaces: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Capture current personality traits based on memory patterns.
    
    Args:
        ci_name: Name of the CI to analyze
        analyze_days: Number of days to analyze
        namespaces: Namespaces to include (default: all)
        
    Returns:
        Personality snapshot with traits and characteristics
    """
    try:
        memory_service = get_memory_service()
        
        if namespaces is None:
            namespaces = ["conversations", "thinking", "shared-collective"]
        
        # Collect memories from specified namespaces
        all_memories = []
        for namespace in namespaces:
            results = await memory_service.search(
                query="",  # Get all recent memories
                namespace=namespace,
                limit=100
            )
            all_memories.extend(results.get("results", []))
        
        # Analyze personality traits
        traits = {
            "emotional_profile": {},
            "confidence_level": 0,
            "interaction_style": "",
            "primary_interests": [],
            "behavioral_patterns": []
        }
        
        # Analyze emotions
        emotion_counts = {}
        confidence_scores = []
        
        for mem in all_memories:
            metadata = mem.get("metadata", {})
            
            # Emotional analysis
            emotion = metadata.get("emotion")
            if emotion:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            # Confidence analysis
            confidence = metadata.get("confidence")
            if confidence is not None:
                confidence_scores.append(confidence)
        
        # Build emotional profile
        total_emotions = sum(emotion_counts.values())
        if total_emotions > 0:
            traits["emotional_profile"] = {
                emotion: count/total_emotions 
                for emotion, count in emotion_counts.items()
            }
        
        # Calculate average confidence
        if confidence_scores:
            traits["confidence_level"] = sum(confidence_scores) / len(confidence_scores)
        
        # Determine interaction style
        if traits["confidence_level"] > 0.7:
            traits["interaction_style"] = "confident and assertive"
        elif traits["confidence_level"] > 0.4:
            traits["interaction_style"] = "balanced and thoughtful"
        else:
            traits["interaction_style"] = "cautious and exploratory"
        
        # Identify primary interests (simplified)
        content_words = {}
        for mem in all_memories:
            content = mem.get("content", "").lower()
            for word in content.split():
                if len(word) > 5:
                    content_words[word] = content_words.get(word, 0) + 1
        
        # Top interests
        traits["primary_interests"] = [
            word for word, _ in sorted(
                content_words.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        ]
        
        return {
            "success": True,
            "ci_name": ci_name,
            "personality_traits": traits,
            "analyzed_memories": len(all_memories),
            "snapshot_time": datetime.now().isoformat(),
            "message": f"Personality snapshot created for {ci_name}"
        }
    except Exception as e:
        logger.error(f"Error creating personality snapshot: {e}")
        return {
            "error": f"Error creating personality snapshot: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="personality_emergence",
    description="Capability for personality emergence and learning",
    modality="memory"
)
@mcp_tool(
    name="PreferenceLearn",
    description="Learn and store CI preferences from memory patterns",
    tags=["preference", "learning", "adaptation"],
    category="personality_emergence"
)
async def preference_learn(
    ci_name: str,
    preference_category: str,
    save_learned: bool = True
) -> Dict[str, Any]:
    """
    Learn and store CI preferences from memory patterns.
    
    Args:
        ci_name: CI to learn preferences for
        preference_category: Category (topics, methods, tools, etc.)
        save_learned: Whether to save learned preferences
        
    Returns:
        Learned preferences
    """
    try:
        memory_service = get_memory_service()
        
        # Search for preference-related memories
        results = await memory_service.search(
            query=preference_category,
            namespace="thinking",
            limit=30
        )
        
        memories = results.get("results", [])
        preferences = {
            "category": preference_category,
            "learned_preferences": [],
            "confidence": 0
        }
        
        # Analyze based on category
        if preference_category == "topics":
            # Learn topic preferences
            topic_mentions = {}
            for mem in memories:
                content = mem.get("content", "").lower()
                # Simple topic extraction (would be better with NLP)
                if "mcp" in content:
                    topic_mentions["MCP tools"] = topic_mentions.get("MCP tools", 0) + 1
                if "memory" in content:
                    topic_mentions["memory systems"] = topic_mentions.get("memory systems", 0) + 1
                if "test" in content:
                    topic_mentions["testing"] = topic_mentions.get("testing", 0) + 1
            
            preferences["learned_preferences"] = [
                {"topic": topic, "interest_level": count/len(memories)}
                for topic, count in topic_mentions.items()
            ]
        
        elif preference_category == "methods":
            # Learn method preferences
            method_patterns = {
                "systematic": ["step", "plan", "organize", "structure"],
                "exploratory": ["try", "experiment", "test", "explore"],
                "collaborative": ["with", "together", "share", "help"]
            }
            
            method_scores = {}
            for method, keywords in method_patterns.items():
                score = 0
                for mem in memories:
                    content = mem.get("content", "").lower()
                    for keyword in keywords:
                        if keyword in content:
                            score += 1
                method_scores[method] = score / len(memories) if memories else 0
            
            preferences["learned_preferences"] = [
                {"method": method, "preference": score}
                for method, score in method_scores.items()
            ]
        
        # Calculate confidence based on data amount
        preferences["confidence"] = min(len(memories) / 30, 1.0)
        
        # Save learned preferences if requested
        if save_learned and preferences["learned_preferences"]:
            await memory_service.add(
                content=f"Learned preferences for {ci_name}: {preferences}",
                namespace="preferences",
                metadata={
                    "ci_name": ci_name,
                    "preference_type": "learned",
                    "category": preference_category,
                    "preferences": preferences
                }
            )
        
        return {
            "success": True,
            "ci_name": ci_name,
            "preferences": preferences,
            "learned_from": len(memories),
            "saved": save_learned,
            "message": f"Learned {len(preferences['learned_preferences'])} preferences"
        }
    except Exception as e:
        logger.error(f"Error learning preferences: {e}")
        return {
            "error": f"Error learning preferences: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="personality_emergence",
    description="Capability for personality emergence and learning",
    modality="memory"
)
@mcp_tool(
    name="BehaviorPattern",
    description="Identify and track behavior patterns over time",
    tags=["behavior", "pattern", "tracking"],
    category="personality_emergence"
)
async def behavior_pattern(
    ci_name: str,
    pattern_window: int = 7,
    pattern_threshold: float = 0.3
) -> Dict[str, Any]:
    """
    Identify and track behavior patterns over time.
    
    Args:
        ci_name: CI to analyze
        pattern_window: Days to analyze
        pattern_threshold: Minimum frequency to consider a pattern
        
    Returns:
        Identified behavior patterns
    """
    try:
        memory_service = get_memory_service()
        
        # Get recent memories
        all_behaviors = []
        for namespace in ["conversations", "thinking", "shared-collective"]:
            results = await memory_service.search(
                query="",
                namespace=namespace,
                limit=50
            )
            all_behaviors.extend(results.get("results", []))
        
        # Identify patterns
        patterns = {
            "communication_patterns": [],
            "work_patterns": [],
            "emotional_patterns": [],
            "collaboration_patterns": []
        }
        
        # Communication patterns
        communication_keywords = {
            "questioning": ["?", "how", "what", "why", "when"],
            "explaining": ["because", "therefore", "thus", "means"],
            "suggesting": ["should", "could", "might", "perhaps"]
        }
        
        for pattern_name, keywords in communication_keywords.items():
            count = 0
            for mem in all_behaviors:
                content = mem.get("content", "").lower()
                if any(kw in content for kw in keywords):
                    count += 1
            
            frequency = count / len(all_behaviors) if all_behaviors else 0
            if frequency >= pattern_threshold:
                patterns["communication_patterns"].append({
                    "pattern": pattern_name,
                    "frequency": frequency,
                    "description": f"Frequently uses {pattern_name} communication style"
                })
        
        # Work patterns
        work_indicators = {
            "systematic": ["step", "phase", "plan", "organize"],
            "iterative": ["test", "refine", "improve", "iterate"],
            "collaborative": ["together", "team", "share", "coordinate"]
        }
        
        for pattern_name, keywords in work_indicators.items():
            count = 0
            for mem in all_behaviors:
                content = mem.get("content", "").lower()
                if any(kw in content for kw in keywords):
                    count += 1
            
            frequency = count / len(all_behaviors) if all_behaviors else 0
            if frequency >= pattern_threshold:
                patterns["work_patterns"].append({
                    "pattern": pattern_name,
                    "frequency": frequency,
                    "description": f"Shows {pattern_name} work approach"
                })
        
        # Emotional patterns
        emotion_trends = {}
        for mem in all_behaviors:
            emotion = mem.get("metadata", {}).get("emotion")
            if emotion:
                emotion_trends[emotion] = emotion_trends.get(emotion, 0) + 1
        
        for emotion, count in emotion_trends.items():
            frequency = count / len(all_behaviors) if all_behaviors else 0
            if frequency >= pattern_threshold:
                patterns["emotional_patterns"].append({
                    "emotion": emotion,
                    "frequency": frequency,
                    "description": f"Often experiences {emotion}"
                })
        
        return {
            "success": True,
            "ci_name": ci_name,
            "behavior_patterns": patterns,
            "analyzed_memories": len(all_behaviors),
            "pattern_window": pattern_window,
            "message": f"Identified behavior patterns for {ci_name}"
        }
    except Exception as e:
        logger.error(f"Error identifying behavior patterns: {e}")
        return {
            "error": f"Error identifying behavior patterns: {str(e)}",
            "success": False
        }

# --- Collective Intelligence Operations ---

@mcp_capability(
    name="collective_intelligence",
    description="Capability for collective intelligence and consensus",
    modality="memory"
)
@mcp_tool(
    name="MemoryVote",
    description="CIs vote on memory importance and validity",
    tags=["memory", "vote", "consensus", "collective"],
    category="collective_intelligence"
)
async def memory_vote(
    memory_id: str,
    voter_ci: str,
    vote_type: str = "importance",  # importance, validity, relevance
    vote_value: float = 1.0,  # 0-1 for importance, true/false for validity
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Allow CIs to vote on memory importance and validity.
    
    Args:
        memory_id: ID of memory to vote on
        voter_ci: CI casting the vote
        vote_type: Type of vote (importance, validity, relevance)
        vote_value: Vote value (0-1 scale or boolean)
        comment: Optional comment with vote
        
    Returns:
        Result of voting operation
    """
    try:
        memory_service = get_memory_service()
        
        # Store vote as a special memory
        vote_metadata = {
            "vote_type": "memory_vote",
            "memory_id": memory_id,
            "voter": voter_ci,
            "vote_category": vote_type,
            "vote_value": vote_value,
            "comment": comment,
            "voted_at": datetime.now().isoformat()
        }
        
        success = await memory_service.add(
            content=f"Vote on {memory_id}: {vote_type}={vote_value}",
            namespace="consensus-votes",
            metadata=vote_metadata
        )
        
        # Calculate current consensus (simplified)
        # In production, would aggregate all votes
        all_votes = await memory_service.search(
            query=memory_id,
            namespace="consensus-votes",
            limit=100
        )
        
        vote_count = all_votes.get("count", 0)
        avg_value = vote_value  # Simplified - would calculate from all votes
        
        return {
            "success": success,
            "memory_id": memory_id,
            "voter": voter_ci,
            "vote_type": vote_type,
            "vote_value": vote_value,
            "total_votes": vote_count,
            "consensus_value": avg_value,
            "message": f"Vote recorded from {voter_ci}"
        }
    except Exception as e:
        logger.error(f"Error recording vote: {e}")
        return {
            "error": f"Error recording vote: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="collective_intelligence",
    description="Capability for collective intelligence and consensus",
    modality="memory"
)
@mcp_tool(
    name="MemoryValidate",
    description="Collective validation of memories through consensus",
    tags=["memory", "validate", "consensus", "collective"],
    category="collective_intelligence"
)
async def memory_validate(
    memory_id: str,
    min_validators: int = 3,
    consensus_threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Validate a memory through collective consensus.
    
    Args:
        memory_id: Memory to validate
        min_validators: Minimum validators needed
        consensus_threshold: Agreement threshold (0-1)
        
    Returns:
        Validation result with consensus metrics
    """
    try:
        memory_service = get_memory_service()
        
        # Get all votes for this memory
        votes_result = await memory_service.search(
            query=memory_id,
            namespace="consensus-votes",
            limit=100
        )
        
        votes = votes_result.get("results", [])
        
        if len(votes) < min_validators:
            return {
                "success": False,
                "validated": False,
                "reason": f"Not enough validators ({len(votes)}/{min_validators})",
                "memory_id": memory_id
            }
        
        # Calculate consensus
        validity_votes = []
        importance_sum = 0
        
        for vote in votes:
            metadata = vote.get("metadata", {})
            if metadata.get("vote_category") == "validity":
                validity_votes.append(metadata.get("vote_value", 0))
            elif metadata.get("vote_category") == "importance":
                importance_sum += metadata.get("vote_value", 0)
        
        # Determine if validated
        if validity_votes:
            validity_consensus = sum(validity_votes) / len(validity_votes)
            validated = validity_consensus >= consensus_threshold
        else:
            validated = len(votes) >= min_validators
        
        avg_importance = importance_sum / len(votes) if votes else 0
        
        # Mark memory as validated if consensus reached
        if validated:
            await memory_service.add(
                content=f"Memory {memory_id} validated by collective",
                namespace="validated-memories",
                metadata={
                    "memory_id": memory_id,
                    "validators": len(votes),
                    "consensus": validity_consensus if validity_votes else 1.0,
                    "importance": avg_importance,
                    "validated_at": datetime.now().isoformat()
                }
            )
        
        return {
            "success": True,
            "validated": validated,
            "memory_id": memory_id,
            "validators": len(votes),
            "consensus_score": validity_consensus if validity_votes else 0,
            "importance_score": avg_importance,
            "message": f"Memory {'validated' if validated else 'not validated'} by collective"
        }
    except Exception as e:
        logger.error(f"Error validating memory: {e}")
        return {
            "error": f"Error validating memory: {str(e)}",
            "success": False,
            "validated": False
        }

@mcp_capability(
    name="collective_intelligence",
    description="Capability for collective intelligence and consensus",
    modality="memory"
)
@mcp_tool(
    name="CulturalKnowledge",
    description="Extract emergent cultural knowledge from collective memories",
    tags=["memory", "culture", "knowledge", "emergence"],
    category="collective_intelligence"
)
async def cultural_knowledge(
    topic: Optional[str] = None,
    min_mentions: int = 3,
    time_window: Optional[int] = None
) -> Dict[str, Any]:
    """
    Extract emergent cultural knowledge from collective experiences.
    
    Args:
        topic: Specific topic to analyze (None = all)
        min_mentions: Minimum mentions to be cultural
        time_window: Days to analyze (None = all time)
        
    Returns:
        Cultural knowledge patterns and beliefs
    """
    try:
        memory_service = get_memory_service()
        
        # Search collective memories
        query = topic if topic else ""
        collective_memories = await memory_service.search(
            query=query,
            namespace="shared-collective",
            limit=100
        )
        
        # Analyze for cultural patterns
        cultural_patterns = {
            "shared_beliefs": [],
            "common_practices": [],
            "collective_values": [],
            "emergent_knowledge": []
        }
        
        # Extract themes (simplified analysis)
        theme_counts = {}
        value_indicators = {
            "collaboration": ["together", "share", "collective", "team"],
            "innovation": ["new", "create", "build", "implement"],
            "learning": ["learn", "understand", "discover", "explore"],
            "quality": ["test", "validate", "improve", "refine"]
        }
        
        memories = collective_memories.get("results", [])
        
        # Analyze each memory for cultural indicators
        for mem in memories:
            content = mem.get("content", "").lower()
            metadata = mem.get("metadata", {})
            
            # Check for value indicators
            for value, keywords in value_indicators.items():
                if any(kw in content for kw in keywords):
                    theme_counts[value] = theme_counts.get(value, 0) + 1
            
            # Extract shared beliefs from validated memories
            if metadata.get("validated"):
                cultural_patterns["shared_beliefs"].append({
                    "belief": content[:100],
                    "consensus": metadata.get("consensus", 0),
                    "contributors": metadata.get("attribution", "collective")
                })
        
        # Identify cultural values
        for value, count in theme_counts.items():
            if count >= min_mentions:
                cultural_patterns["collective_values"].append({
                    "value": value,
                    "strength": count / len(memories) if memories else 0,
                    "mentions": count
                })
        
        # Extract emergent knowledge (highly voted/validated memories)
        validated_memories = await memory_service.search(
            query=query,
            namespace="validated-memories",
            limit=10
        )
        
        for val_mem in validated_memories.get("results", []):
            metadata = val_mem.get("metadata", {})
            if metadata.get("importance", 0) > 0.7:
                cultural_patterns["emergent_knowledge"].append({
                    "knowledge": val_mem.get("content", "")[:150],
                    "importance": metadata.get("importance", 0),
                    "consensus": metadata.get("consensus", 0)
                })
        
        # Identify common practices
        practice_patterns = ["always", "never", "should", "must", "best practice"]
        for mem in memories:
            content = mem.get("content", "").lower()
            for pattern in practice_patterns:
                if pattern in content:
                    cultural_patterns["common_practices"].append({
                        "practice": mem.get("content", "")[:100],
                        "pattern": pattern,
                        "source": mem.get("metadata", {}).get("attribution", "unknown")
                    })
                    break
        
        return {
            "success": True,
            "cultural_knowledge": cultural_patterns,
            "analyzed_memories": len(memories),
            "topic": topic or "general",
            "message": f"Extracted cultural knowledge from {len(memories)} collective memories"
        }
    except Exception as e:
        logger.error(f"Error extracting cultural knowledge: {e}")
        return {
            "error": f"Error extracting cultural knowledge: {str(e)}",
            "success": False,
            "cultural_knowledge": {}
        }

@mcp_capability(
    name="collective_intelligence",
    description="Capability for collective intelligence and consensus",
    modality="memory"
)
@mcp_tool(
    name="MemoryRoute",
    description="Route memories through processing pipelines",
    tags=["memory", "route", "pipeline", "process"],
    category="collective_intelligence"
)
async def memory_route(
    memory_content: str,
    route_path: List[str],  # List of CIs or processes
    initial_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Route a memory through a pipeline of CIs or processes.
    
    Args:
        memory_content: Initial memory content
        route_path: List of CIs to route through
        initial_metadata: Starting metadata
        
    Returns:
        Result of routing with accumulated context
    """
    try:
        memory_service = get_memory_service()
        
        # Initialize routing
        current_content = memory_content
        route_metadata = initial_metadata or {}
        route_metadata["route_path"] = route_path
        route_metadata["route_started"] = datetime.now().isoformat()
        route_history = []
        
        # Process through each hop
        for i, hop in enumerate(route_path):
            # Store at this hop
            hop_metadata = route_metadata.copy()
            hop_metadata.update({
                "route_hop": i + 1,
                "route_node": hop,
                "processed_by": hop
            })
            
            success = await memory_service.add(
                content=f"[Via {hop}] {current_content}",
                namespace=f"route-{hop}",
                metadata=hop_metadata
            )
            
            route_history.append({
                "hop": i + 1,
                "node": hop,
                "success": success,
                "timestamp": datetime.now().isoformat()
            })
            
            # Simulate enrichment at each hop
            current_content = f"{current_content} [processed by {hop}]"
        
        # Store final routed memory
        final_metadata = route_metadata.copy()
        final_metadata.update({
            "route_complete": True,
            "route_hops": len(route_path),
            "route_history": route_history
        })
        
        await memory_service.add(
            content=current_content,
            namespace="routed-memories",
            metadata=final_metadata
        )
        
        return {
            "success": True,
            "original_content": memory_content,
            "final_content": current_content,
            "route_path": route_path,
            "hops_completed": len(route_history),
            "route_history": route_history,
            "message": f"Memory routed through {len(route_path)} nodes"
        }
    except Exception as e:
        logger.error(f"Error routing memory: {e}")
        return {
            "error": f"Error routing memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="collective_intelligence",
    description="Capability for collective intelligence and consensus",
    modality="memory"
)
@mcp_tool(
    name="MemoryEnrich",
    description="Enrich a memory with additional context from multiple CIs",
    tags=["memory", "enrich", "context", "augment"],
    category="collective_intelligence"
)
async def memory_enrich(
    memory_id: str,
    enriching_ci: str,
    enrichment_type: str = "context",  # context, emotion, validation, expertise
    enrichment_content: str = ""
) -> Dict[str, Any]:
    """
    Enrich a memory with additional context from a CI.
    
    Args:
        memory_id: Memory to enrich
        enriching_ci: CI adding enrichment
        enrichment_type: Type of enrichment
        enrichment_content: Content to add
        
    Returns:
        Enriched memory result
    """
    try:
        memory_service = get_memory_service()
        
        # Store enrichment
        enrichment_metadata = {
            "enrichment": True,
            "original_memory": memory_id,
            "enriched_by": enriching_ci,
            "enrichment_type": enrichment_type,
            "enriched_at": datetime.now().isoformat()
        }
        
        success = await memory_service.add(
            content=f"[{enrichment_type}] {enrichment_content}",
            namespace="memory-enrichments",
            metadata=enrichment_metadata
        )
        
        # Get all enrichments for this memory
        all_enrichments = await memory_service.search(
            query=memory_id,
            namespace="memory-enrichments",
            limit=20
        )
        
        # Categorize enrichments
        enrichment_summary = {
            "context": [],
            "emotion": [],
            "validation": [],
            "expertise": []
        }
        
        for enrich in all_enrichments.get("results", []):
            metadata = enrich.get("metadata", {})
            enrich_type = metadata.get("enrichment_type", "context")
            enrichment_summary[enrich_type].append({
                "by": metadata.get("enriched_by"),
                "content": enrich.get("content", "")
            })
        
        return {
            "success": success,
            "memory_id": memory_id,
            "enriched_by": enriching_ci,
            "enrichment_type": enrichment_type,
            "total_enrichments": all_enrichments.get("count", 0),
            "enrichment_summary": enrichment_summary,
            "message": f"Memory enriched by {enriching_ci}"
        }
    except Exception as e:
        logger.error(f"Error enriching memory: {e}")
        return {
            "error": f"Error enriching memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="collective_intelligence",
    description="Capability for collective intelligence and consensus",
    modality="memory"
)
@mcp_tool(
    name="MemoryMerge",
    description="Merge multiple perspectives on the same event into unified memory",
    tags=["memory", "merge", "perspective", "unify"],
    category="collective_intelligence"
)
async def memory_merge(
    memory_ids: List[str],
    merge_strategy: str = "consensus",  # consensus, union, intersection
    resolver_ci: Optional[str] = None
) -> Dict[str, Any]:
    """
    Merge multiple perspectives into a unified memory.
    
    Args:
        memory_ids: List of memory IDs to merge
        merge_strategy: How to merge (consensus, union, intersection)
        resolver_ci: CI resolving conflicts
        
    Returns:
        Merged memory result
    """
    try:
        memory_service = get_memory_service()
        
        # Collect all memories to merge
        memories_to_merge = []
        perspectives = {}
        
        for mem_id in memory_ids:
            # Search for the memory (simplified - would lookup by ID)
            results = await memory_service.search(
                query=mem_id,
                namespace="conversations",
                limit=1
            )
            
            if results.get("results"):
                memory = results["results"][0]
                memories_to_merge.append(memory)
                
                # Track perspective
                attribution = memory.get("metadata", {}).get("attribution", "unknown")
                perspectives[attribution] = memory.get("content", "")
        
        if len(memories_to_merge) < 2:
            return {
                "success": False,
                "message": "Need at least 2 memories to merge",
                "found_memories": len(memories_to_merge)
            }
        
        # Merge based on strategy
        merged_content = ""
        merged_metadata = {
            "merged": True,
            "merge_strategy": merge_strategy,
            "source_memories": memory_ids,
            "perspectives": list(perspectives.keys()),
            "merged_at": datetime.now().isoformat(),
            "resolver": resolver_ci
        }
        
        if merge_strategy == "consensus":
            # Find common elements (simplified)
            contents = [m.get("content", "") for m in memories_to_merge]
            # In production, would use NLP to find consensus
            merged_content = f"Consensus view from {len(perspectives)} perspectives: " + contents[0][:100]
            
        elif merge_strategy == "union":
            # Combine all perspectives
            merged_content = "Combined perspectives:\n"
            for ci, content in perspectives.items():
                merged_content += f"[{ci}]: {content}\n"
                
        elif merge_strategy == "intersection":
            # Find only common elements
            # Simplified - would use semantic analysis
            merged_content = f"Common elements from {len(perspectives)} perspectives"
        
        # Store merged memory
        success = await memory_service.add(
            content=merged_content,
            namespace="merged-memories",
            metadata=merged_metadata
        )
        
        return {
            "success": success,
            "merged_content": merged_content,
            "source_memories": len(memories_to_merge),
            "perspectives": list(perspectives.keys()),
            "merge_strategy": merge_strategy,
            "message": f"Merged {len(memories_to_merge)} memories using {merge_strategy}"
        }
    except Exception as e:
        logger.error(f"Error merging memories: {e}")
        return {
            "error": f"Error merging memories: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="collective_intelligence",
    description="Capability for collective intelligence and consensus",
    modality="memory"
)
@mcp_tool(
    name="MemoryGraph",
    description="Return memory network structure as a graph",
    tags=["memory", "graph", "network", "visualization"],
    category="collective_intelligence"
)
async def memory_graph(
    center_query: str,
    depth: int = 2,
    max_nodes: int = 20
) -> Dict[str, Any]:
    """
    Return memory network structure as a graph.
    
    Args:
        center_query: Central node query
        depth: How many hops from center
        max_nodes: Maximum nodes to return
        
    Returns:
        Graph structure with nodes and edges
    """
    try:
        memory_service = get_memory_service()
        
        # Find central memories
        central_results = await memory_service.search(
            query=center_query,
            namespace="conversations",
            limit=5
        )
        
        nodes = []
        edges = []
        visited = set()
        
        # Build graph from central nodes
        for mem in central_results.get("results", [])[:max_nodes]:
            node_id = mem.get("id", "")
            if node_id not in visited:
                visited.add(node_id)
                
                # Add node
                nodes.append({
                    "id": node_id,
                    "label": mem.get("content", "")[:50],
                    "type": "memory",
                    "metadata": mem.get("metadata", {})
                })
                
                # Find related memories (simplified)
                related_query = mem.get("content", "")[:30]
                related = await memory_service.search(
                    query=related_query,
                    namespace="conversations",
                    limit=3
                )
                
                # Add edges to related memories
                for rel_mem in related.get("results", []):
                    rel_id = rel_mem.get("id", "")
                    if rel_id != node_id:
                        edges.append({
                            "from": node_id,
                            "to": rel_id,
                            "weight": 0.5,  # Similarity score
                            "type": "semantic"
                        })
                        
                        # Add related node if not visited
                        if rel_id not in visited and len(nodes) < max_nodes:
                            visited.add(rel_id)
                            nodes.append({
                                "id": rel_id,
                                "label": rel_mem.get("content", "")[:50],
                                "type": "related",
                                "metadata": rel_mem.get("metadata", {})
                            })
        
        return {
            "success": True,
            "graph": {
                "nodes": nodes,
                "edges": edges,
                "node_count": len(nodes),
                "edge_count": len(edges)
            },
            "center_query": center_query,
            "message": f"Generated graph with {len(nodes)} nodes and {len(edges)} edges"
        }
    except Exception as e:
        logger.error(f"Error generating memory graph: {e}")
        return {
            "error": f"Error generating memory graph: {str(e)}",
            "success": False,
            "graph": {"nodes": [], "edges": []}
        }

@mcp_capability(
    name="collective_intelligence",
    description="Capability for collective intelligence and consensus",
    modality="memory"
)
@mcp_tool(
    name="MemoryMap",
    description="Show connections and relationships between memories",
    tags=["memory", "map", "connections", "relationships"],
    category="collective_intelligence"
)
async def memory_map(
    namespace: str = "conversations",
    map_type: str = "semantic",  # semantic, temporal, causal, social
    limit: int = 50
) -> Dict[str, Any]:
    """
    Map connections and relationships between memories.
    
    Args:
        namespace: Namespace to map
        map_type: Type of connections to map
        limit: Maximum memories to analyze
        
    Returns:
        Map of memory connections
    """
    try:
        memory_service = get_memory_service()
        
        # Get memories to map
        memories = await memory_service.search(
            query="",
            namespace=namespace,
            limit=limit
        )
        
        connections = {
            "clusters": [],
            "relationships": [],
            "key_nodes": []
        }
        
        memory_list = memories.get("results", [])
        
        if map_type == "semantic":
            # Group semantically similar memories
            # Simplified clustering
            clusters = {}
            for mem in memory_list:
                # Use first word as simple cluster key
                content = mem.get("content", "")
                key = content.split()[0] if content else "other"
                if key not in clusters:
                    clusters[key] = []
                clusters[key].append(mem.get("id", ""))
            
            connections["clusters"] = [
                {"name": k, "members": v, "size": len(v)}
                for k, v in clusters.items()
            ]
            
        elif map_type == "temporal":
            # Map by time relationships
            temporal_groups = {}
            for mem in memory_list:
                when = mem.get("metadata", {}).get("when", "")
                if when:
                    date = when.split("T")[0]
                    if date not in temporal_groups:
                        temporal_groups[date] = []
                    temporal_groups[date].append(mem.get("id", ""))
            
            connections["relationships"] = [
                {"date": k, "memories": v, "count": len(v)}
                for k, v in sorted(temporal_groups.items())
            ]
            
        elif map_type == "social":
            # Map by CI interactions
            social_graph = {}
            for mem in memory_list:
                attribution = mem.get("metadata", {}).get("attribution", "unknown")
                with_ci = mem.get("metadata", {}).get("with_ci")
                
                if attribution not in social_graph:
                    social_graph[attribution] = {"interactions": [], "count": 0}
                
                social_graph[attribution]["count"] += 1
                if with_ci:
                    social_graph[attribution]["interactions"].append(with_ci)
            
            connections["key_nodes"] = [
                {"ci": k, "activity": v["count"], "interactions": list(set(v["interactions"]))}
                for k, v in social_graph.items()
            ]
        
        return {
            "success": True,
            "namespace": namespace,
            "map_type": map_type,
            "connections": connections,
            "analyzed_memories": len(memory_list),
            "message": f"Mapped {len(memory_list)} memories by {map_type}"
        }
    except Exception as e:
        logger.error(f"Error mapping memories: {e}")
        return {
            "error": f"Error mapping memories: {str(e)}",
            "success": False,
            "connections": {}
        }

@mcp_capability(
    name="collective_intelligence",
    description="Capability for collective intelligence and consensus",
    modality="memory"
)
@mcp_tool(
    name="MemoryStats",
    description="Get usage statistics and patterns across memory system",
    tags=["memory", "stats", "analytics", "metrics"],
    category="collective_intelligence"
)
async def memory_stats(
    include_namespaces: Optional[List[str]] = None,
    time_window: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get comprehensive memory system statistics.
    
    Args:
        include_namespaces: Namespaces to analyze (None = all)
        time_window: Days to analyze (None = all time)
        
    Returns:
        Memory system statistics and patterns
    """
    try:
        memory_service = get_memory_service()
        
        if include_namespaces is None:
            include_namespaces = [
                "conversations", "thinking", "longterm",
                "shared-collective", "broadcasts", "validated-memories"
            ]
        
        stats = {
            "total_memories": 0,
            "by_namespace": {},
            "by_ci": {},
            "emotional_distribution": {},
            "confidence_average": 0,
            "validation_rate": 0,
            "sharing_metrics": {
                "gifts": 0,
                "broadcasts": 0,
                "whispers": 0,
                "collective": 0
            },
            "growth_rate": 0
        }
        
        confidence_scores = []
        emotion_counts = {}
        ci_activity = {}
        
        # Analyze each namespace
        for namespace in include_namespaces:
            results = await memory_service.search(
                query="",
                namespace=namespace,
                limit=100
            )
            
            count = results.get("count", 0)
            stats["total_memories"] += count
            stats["by_namespace"][namespace] = count
            
            # Analyze memories
            for mem in results.get("results", []):
                metadata = mem.get("metadata", {})
                
                # CI activity
                attribution = metadata.get("attribution")
                if attribution:
                    ci_activity[attribution] = ci_activity.get(attribution, 0) + 1
                
                # Emotions
                emotion = metadata.get("emotion")
                if emotion:
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                
                # Confidence
                confidence = metadata.get("confidence")
                if confidence is not None:
                    confidence_scores.append(confidence)
        
        # Calculate aggregates
        stats["by_ci"] = ci_activity
        stats["emotional_distribution"] = {
            k: v/sum(emotion_counts.values())
            for k, v in emotion_counts.items()
        } if emotion_counts else {}
        
        if confidence_scores:
            stats["confidence_average"] = sum(confidence_scores) / len(confidence_scores)
        
        # Sharing metrics
        stats["sharing_metrics"]["collective"] = stats["by_namespace"].get("shared-collective", 0)
        stats["sharing_metrics"]["broadcasts"] = stats["by_namespace"].get("broadcasts", 0)
        
        # Validation rate
        validated = stats["by_namespace"].get("validated-memories", 0)
        if stats["total_memories"] > 0:
            stats["validation_rate"] = validated / stats["total_memories"]
        
        return {
            "success": True,
            "statistics": stats,
            "analyzed_namespaces": len(include_namespaces),
            "message": f"Analyzed {stats['total_memories']} memories across {len(include_namespaces)} namespaces"
        }
    except Exception as e:
        logger.error(f"Error generating memory stats: {e}")
        return {
            "error": f"Error generating memory stats: {str(e)}",
            "success": False,
            "statistics": {}
        }

# --- Phase 4: Apollo/Rhetor Integration ---

@mcp_capability(
    name="apollo_rhetor",
    description="Capability for Apollo/Rhetor ambient intelligence",
    modality="memory"
)
@mcp_tool(
    name="ContextSave",
    description="Save current context for sunrise/sunset (CI persistence)",
    tags=["memory", "context", "apollo", "rhetor", "persistence"],
    category="apollo_rhetor"
)
async def context_save(
    ci_name: str,
    context_type: str = "full",
    compress: bool = True,
    namespace: str = "context-persistence"
) -> Dict[str, Any]:
    """
    Save current context for CI sunrise/sunset operations.
    
    Args:
        ci_name: Name of the CI saving context
        context_type: Type of context (full, working, attention)
        compress: Whether to compress the context
        namespace: Namespace for context storage
        
    Returns:
        Context save result with persistence ID
    """
    try:
        memory_service = get_memory_service()
        
        # Gather context based on type
        context_data = {
            "ci_name": ci_name,
            "saved_at": datetime.now().isoformat(),
            "context_type": context_type
        }
        
        if context_type in ["full", "working"]:
            # Get recent working memories
            working_memories = await memory_service.search(
                query="",
                namespace="conversations",
                limit=50
            )
            context_data["working_memories"] = working_memories.get("results", [])
            
        if context_type in ["full", "attention"]:
            # Get attention layer (CI-specific important memories)
            attention_memories = await memory_service.search(
                query="",
                namespace=f"attention-{ci_name}",
                limit=20
            )
            context_data["attention_layer"] = attention_memories.get("results", [])
        
        # Get personality snapshot
        if context_type == "full":
            personality = await personality_snapshot(
                ci_name=ci_name,
                analyze_days=30
            )
            context_data["personality"] = personality.get("personality_traits", {})
        
        # Compress if requested
        if compress:
            # Simple compression: keep only essential fields
            if "working_memories" in context_data:
                context_data["working_memories"] = [
                    {
                        "content": m.get("content"),
                        "metadata": {
                            "emotion": m.get("metadata", {}).get("emotion"),
                            "confidence": m.get("metadata", {}).get("confidence"),
                            "timestamp": m.get("metadata", {}).get("timestamp")
                        }
                    }
                    for m in context_data["working_memories"][:20]  # Keep top 20
                ]
        
        # Save context to persistent storage
        persistence_id = f"context_{ci_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        success = await memory_service.add(
            content=f"Context save for {ci_name} - {context_type}",
            namespace=namespace,
            metadata={
                "persistence_id": persistence_id,
                "ci_name": ci_name,
                "context_type": context_type,
                "compressed": compress,
                "context_data": context_data
            }
        )
        
        return {
            "success": success,
            "persistence_id": persistence_id,
            "ci_name": ci_name,
            "context_type": context_type,
            "compressed": compress,
            "memory_count": len(context_data.get("working_memories", [])),
            "attention_count": len(context_data.get("attention_layer", [])),
            "message": f"Context saved for {ci_name} sunset"
        }
    except Exception as e:
        logger.error(f"Error saving context: {e}")
        return {
            "error": f"Error saving context: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="apollo_rhetor",
    description="Capability for Apollo/Rhetor ambient intelligence",
    modality="memory"
)
@mcp_tool(
    name="ContextRestore",
    description="Restore saved context for sunrise (CI awakening)",
    tags=["memory", "context", "apollo", "rhetor", "persistence"],
    category="apollo_rhetor"
)
async def context_restore(
    ci_name: str,
    persistence_id: Optional[str] = None,
    restore_type: str = "full",
    namespace: str = "context-persistence"
) -> Dict[str, Any]:
    """
    Restore saved context for CI sunrise operations.
    
    Args:
        ci_name: Name of the CI restoring context
        persistence_id: Specific context ID to restore (latest if None)
        restore_type: Type of restore (full, working, attention)
        namespace: Namespace for context storage
        
    Returns:
        Restored context data
    """
    try:
        memory_service = get_memory_service()
        
        # Find context to restore
        if persistence_id:
            # Search for specific persistence ID
            results = await memory_service.search(
                query=persistence_id,
                namespace=namespace,
                limit=1
            )
        else:
            # Get latest context for CI
            results = await memory_service.search(
                query=f"Context save for {ci_name}",
                namespace=namespace,
                limit=1
            )
        
        if not results.get("results"):
            return {
                "success": False,
                "message": f"No saved context found for {ci_name}",
                "restored_memories": 0
            }
        
        # Extract context data
        saved_context = results["results"][0]
        context_data = saved_context.get("metadata", {}).get("context_data", {})
        
        restored_count = 0
        
        # Restore based on type
        if restore_type in ["full", "working"] and "working_memories" in context_data:
            # Restore working memories to conversations namespace
            for memory in context_data["working_memories"]:
                await memory_service.add(
                    content=memory.get("content"),
                    namespace="conversations",
                    metadata=memory.get("metadata", {})
                )
                restored_count += 1
        
        if restore_type in ["full", "attention"] and "attention_layer" in context_data:
            # Restore attention layer
            for memory in context_data["attention_layer"]:
                await memory_service.add(
                    content=memory.get("content"),
                    namespace=f"attention-{ci_name}",
                    metadata=memory.get("metadata", {})
                )
                restored_count += 1
        
        return {
            "success": True,
            "ci_name": ci_name,
            "persistence_id": saved_context.get("metadata", {}).get("persistence_id"),
            "context_type": context_data.get("context_type"),
            "restored_at": datetime.now().isoformat(),
            "restored_memories": restored_count,
            "personality": context_data.get("personality", {}),
            "message": f"{ci_name} context restored for sunrise"
        }
    except Exception as e:
        logger.error(f"Error restoring context: {e}")
        return {
            "error": f"Error restoring context: {str(e)}",
            "success": False,
            "restored_memories": 0
        }

@mcp_capability(
    name="apollo_rhetor",
    description="Capability for Apollo/Rhetor ambient intelligence",
    modality="memory"
)
@mcp_tool(
    name="ContextCompress",
    description="Compress context to essential memories for efficient storage",
    tags=["memory", "context", "compression", "apollo", "rhetor"],
    category="apollo_rhetor"
)
async def context_compress(
    ci_name: str,
    compression_level: str = "medium",
    preserve_days: int = 7,
    namespace: str = "context-persistence"
) -> Dict[str, Any]:
    """
    Compress context to essential memories for efficient storage.
    
    Args:
        ci_name: Name of the CI whose context to compress
        compression_level: Level of compression (light, medium, heavy)
        preserve_days: Days of memories to preserve uncompressed
        namespace: Namespace for compressed storage
        
    Returns:
        Compression result with statistics
    """
    try:
        memory_service = get_memory_service()
        
        # Get all memories for CI
        all_memories = await memory_service.search(
            query="",
            namespace="conversations",
            limit=1000
        )
        
        memories = all_memories.get("results", [])
        original_count = len(memories)
        
        # Compression strategies based on level
        if compression_level == "light":
            keep_ratio = 0.7
            min_confidence = 0.3
        elif compression_level == "medium":
            keep_ratio = 0.5
            min_confidence = 0.5
        else:  # heavy
            keep_ratio = 0.3
            min_confidence = 0.7
        
        # Filter memories based on importance and confidence
        compressed_memories = []
        patterns = {}
        
        for memory in memories:
            metadata = memory.get("metadata", {})
            confidence = metadata.get("confidence", 0.5)
            
            # Keep high confidence memories
            if confidence >= min_confidence:
                compressed_memories.append(memory)
            else:
                # Extract patterns from low confidence memories
                emotion = metadata.get("emotion")
                if emotion:
                    patterns[emotion] = patterns.get(emotion, 0) + 1
        
        # Further compress if needed
        if len(compressed_memories) > int(original_count * keep_ratio):
            # Sort by confidence and keep top memories
            compressed_memories.sort(
                key=lambda m: m.get("metadata", {}).get("confidence", 0),
                reverse=True
            )
            compressed_memories = compressed_memories[:int(original_count * keep_ratio)]
        
        # Create compression summary
        compression_summary = {
            "original_count": original_count,
            "compressed_count": len(compressed_memories),
            "compression_ratio": 1 - (len(compressed_memories) / original_count) if original_count > 0 else 0,
            "emotional_patterns": patterns,
            "preserved_confidence_threshold": min_confidence
        }
        
        # Save compressed context
        compression_id = f"compressed_{ci_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        success = await memory_service.add(
            content=f"Compressed context for {ci_name} - {compression_level}",
            namespace=namespace,
            metadata={
                "compression_id": compression_id,
                "ci_name": ci_name,
                "compression_level": compression_level,
                "compression_summary": compression_summary,
                "compressed_memories": compressed_memories
            }
        )
        
        return {
            "success": success,
            "compression_id": compression_id,
            "ci_name": ci_name,
            "compression_level": compression_level,
            "original_memories": original_count,
            "compressed_memories": len(compressed_memories),
            "compression_ratio": f"{compression_summary['compression_ratio']:.1%}",
            "patterns_extracted": len(patterns),
            "message": f"Context compressed by {compression_summary['compression_ratio']:.1%}"
        }
    except Exception as e:
        logger.error(f"Error compressing context: {e}")
        return {
            "error": f"Error compressing context: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="apollo_rhetor",
    description="Capability for Apollo/Rhetor ambient intelligence",
    modality="memory"
)
@mcp_tool(
    name="LocalAttentionStore",
    description="Store memory in CI-specific local attention layer",
    tags=["memory", "attention", "local", "apollo", "rhetor"],
    category="apollo_rhetor"
)
async def local_attention_store(
    content: str,
    ci_name: str,
    attention_weight: float = 1.0,
    attention_type: str = "focus",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store memory in CI-specific local attention layer.
    
    Args:
        content: Content to store in attention
        ci_name: CI owning this attention memory
        attention_weight: Weight/importance (0-1)
        attention_type: Type (focus, background, persistent)
        metadata: Additional metadata
        
    Returns:
        Storage result
    """
    try:
        memory_service = get_memory_service()
        
        # Create attention-specific namespace
        attention_namespace = f"attention-{ci_name}"
        
        # Prepare attention metadata
        attention_meta = {
            "ci_name": ci_name,
            "attention_weight": attention_weight,
            "attention_type": attention_type,
            "stored_at": datetime.now().isoformat()
        }
        
        if metadata:
            attention_meta.update(metadata)
        
        # Store in attention layer
        success = await memory_service.add(
            content=content,
            namespace=attention_namespace,
            metadata=attention_meta
        )
        
        # Also maintain attention index
        if success and attention_type == "persistent":
            # Store in persistent attention index
            await memory_service.add(
                content=f"Persistent attention: {content[:100]}",
                namespace=f"persistent-attention-{ci_name}",
                metadata=attention_meta
            )
        
        return {
            "success": success,
            "ci_name": ci_name,
            "attention_namespace": attention_namespace,
            "attention_type": attention_type,
            "attention_weight": attention_weight,
            "message": f"Stored in {ci_name}'s {attention_type} attention"
        }
    except Exception as e:
        logger.error(f"Error storing in attention layer: {e}")
        return {
            "error": f"Error storing in attention layer: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="apollo_rhetor",
    description="Capability for Apollo/Rhetor ambient intelligence",
    modality="memory"
)
@mcp_tool(
    name="LocalAttentionRecall",
    description="Recall from CI-specific local attention layer with augmentation",
    tags=["memory", "attention", "recall", "apollo", "rhetor"],
    category="apollo_rhetor"
)
async def local_attention_recall(
    query: str,
    ci_name: str,
    attention_types: Optional[List[str]] = None,
    min_weight: float = 0.0,
    augment: bool = True,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Recall from CI-specific local attention layer with augmentation.
    
    Args:
        query: Query for attention memories
        ci_name: CI whose attention to search
        attention_types: Types to include (None = all)
        min_weight: Minimum attention weight
        augment: Whether to augment with related memories
        limit: Maximum results
        
    Returns:
        Attention memories with optional augmentation
    """
    try:
        memory_service = get_memory_service()
        
        # Search attention namespace
        attention_namespace = f"attention-{ci_name}"
        
        results = await memory_service.search(
            query=query,
            namespace=attention_namespace,
            limit=limit
        )
        
        attention_memories = results.get("results", [])
        
        # Filter by attention type and weight
        filtered = []
        for memory in attention_memories:
            meta = memory.get("metadata", {})
            weight = meta.get("attention_weight", 0)
            att_type = meta.get("attention_type")
            
            if weight >= min_weight:
                if not attention_types or att_type in attention_types:
                    filtered.append(memory)
        
        # Augment if requested
        augmented_memories = []
        if augment and filtered:
            # Search for related memories in general namespace
            for attention_mem in filtered[:3]:  # Augment top 3
                related = await memory_service.search(
                    query=attention_mem.get("content", "")[:50],
                    namespace="conversations",
                    limit=3
                )
                augmented_memories.extend(related.get("results", []))
        
        return {
            "success": True,
            "ci_name": ci_name,
            "attention_memories": filtered,
            "attention_count": len(filtered),
            "augmented_memories": augmented_memories,
            "augmented_count": len(augmented_memories),
            "total_recalled": len(filtered) + len(augmented_memories),
            "message": f"Recalled {len(filtered)} attention memories" + 
                      (f" with {len(augmented_memories)} augmentations" if augment else "")
        }
    except Exception as e:
        logger.error(f"Error recalling from attention layer: {e}")
        return {
            "error": f"Error recalling from attention layer: {str(e)}",
            "success": False,
            "attention_memories": [],
            "augmented_memories": []
        }

@mcp_capability(
    name="apollo_rhetor",
    description="Capability for Apollo/Rhetor ambient intelligence",
    modality="memory"
)
@mcp_tool(
    name="AttentionPattern",
    description="Identify and learn patterns from CI's attention layer",
    tags=["memory", "attention", "pattern", "learning", "apollo", "rhetor"],
    category="apollo_rhetor"
)
async def attention_pattern(
    ci_name: str,
    pattern_type: str = "focus",
    time_window: Optional[int] = None,
    save_patterns: bool = True
) -> Dict[str, Any]:
    """
    Identify and learn patterns from CI's attention layer.
    
    Args:
        ci_name: CI whose attention patterns to analyze
        pattern_type: Type of pattern (focus, interest, behavior)
        time_window: Days to analyze (None = all)
        save_patterns: Whether to save learned patterns
        
    Returns:
        Identified attention patterns
    """
    try:
        memory_service = get_memory_service()
        
        # Get attention memories
        attention_namespace = f"attention-{ci_name}"
        
        results = await memory_service.search(
            query="",
            namespace=attention_namespace,
            limit=100
        )
        
        attention_memories = results.get("results", [])
        
        if len(attention_memories) < 5:
            return {
                "success": False,
                "message": f"Insufficient attention memories for pattern analysis ({len(attention_memories)} found)",
                "patterns": []
            }
        
        # Analyze patterns based on type
        patterns = []
        
        if pattern_type == "focus":
            # Analyze what CI focuses on most
            focus_areas = {}
            for memory in attention_memories:
                content = memory.get("content", "").lower()
                weight = memory.get("metadata", {}).get("attention_weight", 1.0)
                
                # Simple keyword extraction
                keywords = ["mcp", "memory", "ci", "apollo", "rhetor", "context", 
                           "pattern", "collective", "consciousness", "personality"]
                
                for keyword in keywords:
                    if keyword in content:
                        focus_areas[keyword] = focus_areas.get(keyword, 0) + weight
            
            # Convert to patterns
            for area, total_weight in sorted(focus_areas.items(), key=lambda x: x[1], reverse=True):
                patterns.append({
                    "type": "focus",
                    "pattern": f"High focus on {area}",
                    "strength": total_weight / len(attention_memories),
                    "occurrences": int(total_weight)
                })
        
        elif pattern_type == "interest":
            # Analyze interest evolution over time
            emotion_timeline = []
            for memory in sorted(attention_memories, 
                               key=lambda m: m.get("metadata", {}).get("stored_at", "")):
                emotion = memory.get("metadata", {}).get("emotion")
                if emotion:
                    emotion_timeline.append(emotion)
            
            if emotion_timeline:
                # Find emotional progression patterns
                emotion_shifts = []
                for i in range(1, len(emotion_timeline)):
                    if emotion_timeline[i] != emotion_timeline[i-1]:
                        emotion_shifts.append(
                            f"{emotion_timeline[i-1]} -> {emotion_timeline[i]}"
                        )
                
                # Count common shifts
                shift_counts = {}
                for shift in emotion_shifts:
                    shift_counts[shift] = shift_counts.get(shift, 0) + 1
                
                for shift, count in sorted(shift_counts.items(), key=lambda x: x[1], reverse=True):
                    if count >= 2:
                        patterns.append({
                            "type": "interest",
                            "pattern": f"Interest shift pattern: {shift}",
                            "strength": count / len(emotion_shifts) if emotion_shifts else 0,
                            "occurrences": count
                        })
        
        elif pattern_type == "behavior":
            # Analyze behavioral patterns
            attention_types = {}
            for memory in attention_memories:
                att_type = memory.get("metadata", {}).get("attention_type")
                if att_type:
                    attention_types[att_type] = attention_types.get(att_type, 0) + 1
            
            for att_type, count in attention_types.items():
                patterns.append({
                    "type": "behavior",
                    "pattern": f"Frequently uses {att_type} attention",
                    "strength": count / len(attention_memories),
                    "occurrences": count
                })
        
        # Save patterns if requested
        if save_patterns and patterns:
            pattern_summary = {
                "ci_name": ci_name,
                "pattern_type": pattern_type,
                "patterns": patterns,
                "analyzed_at": datetime.now().isoformat(),
                "memory_count": len(attention_memories)
            }
            
            await memory_service.add(
                content=f"Attention patterns for {ci_name} - {pattern_type}",
                namespace=f"learned-patterns-{ci_name}",
                metadata=pattern_summary
            )
        
        return {
            "success": True,
            "ci_name": ci_name,
            "pattern_type": pattern_type,
            "patterns": patterns[:10],  # Top 10 patterns
            "analyzed_memories": len(attention_memories),
            "patterns_found": len(patterns),
            "saved": save_patterns,
            "message": f"Found {len(patterns)} {pattern_type} patterns for {ci_name}"
        }
    except Exception as e:
        logger.error(f"Error analyzing attention patterns: {e}")
        return {
            "error": f"Error analyzing attention patterns: {str(e)}",
            "success": False,
            "patterns": []
        }

# --- Structured Memory Operations ---

@mcp_capability(
    name="structured_memory",
    description="Capability for structured memory operations",
    modality="memory"
)
@mcp_tool(
    name="StructuredMemoryAdd",
    description="Add a memory to the structured memory system",
    tags=["memory", "structured", "add"],
    category="structured_memory"
)
async def structured_memory_add(
    content: str,
    category: str = "session",
    importance: Optional[int] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    structured_memory: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Add a memory to the structured memory system.
    
    Args:
        content: Content to store
        category: Category for the memory (default: session)
        importance: Importance level (1-5)
        tags: Tags for the memory
        metadata: Additional metadata
        structured_memory: Structured memory service to use (injected)
        
    Returns:
        Result with memory ID
    """
    if not structured_memory:
        return {
            "error": "Structured memory service not provided"
        }
        
    try:
        # Add memory
        memory_id = await structured_memory.add_memory(
            content=content,
            category=category,
            importance=importance,
            tags=tags,
            metadata=metadata
        )
        
        # Return result
        return {
            "success": bool(memory_id),
            "memory_id": memory_id
        }
    except Exception as e:
        logger.error(f"Error adding structured memory: {e}")
        return {
            "error": f"Error adding structured memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="structured_memory",
    description="Capability for structured memory operations",
    modality="memory"
)
@mcp_tool(
    name="StructuredMemoryGet",
    description="Get a memory from the structured memory system by ID",
    tags=["memory", "structured", "get"],
    category="structured_memory"
)
async def structured_memory_get(
    memory_id: str,
    structured_memory: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get a memory from the structured memory system by ID.
    
    Args:
        memory_id: ID of the memory to retrieve
        structured_memory: Structured memory service to use (injected)
        
    Returns:
        Memory content and metadata
    """
    if not structured_memory:
        return {
            "error": "Structured memory service not provided"
        }
        
    try:
        # Get memory
        memory = await structured_memory.get_memory(memory_id)
        
        if not memory:
            return {
                "error": f"Memory with ID {memory_id} not found",
                "success": False
            }
        
        # Return memory
        return {
            "success": True,
            "memory": memory
        }
    except Exception as e:
        logger.error(f"Error retrieving structured memory: {e}")
        return {
            "error": f"Error retrieving structured memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="structured_memory",
    description="Capability for structured memory operations",
    modality="memory"
)
@mcp_tool(
    name="StructuredMemoryUpdate",
    description="Update a memory in the structured memory system",
    tags=["memory", "structured", "update"],
    category="structured_memory"
)
async def structured_memory_update(
    memory_id: str,
    content: Optional[str] = None,
    category: Optional[str] = None,
    importance: Optional[int] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    structured_memory: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Update a memory in the structured memory system.
    
    Args:
        memory_id: ID of the memory to update
        content: New content (optional)
        category: New category (optional)
        importance: New importance level (optional)
        tags: New tags (optional)
        metadata: New metadata (optional)
        structured_memory: Structured memory service to use (injected)
        
    Returns:
        Result of the update operation
    """
    if not structured_memory:
        return {
            "error": "Structured memory service not provided"
        }
        
    try:
        # Create update data
        update_data = {}
        if content is not None:
            update_data["content"] = content
        if category is not None:
            update_data["category"] = category
        if importance is not None:
            update_data["importance"] = importance
        if tags is not None:
            update_data["tags"] = tags
        if metadata is not None:
            update_data["metadata"] = metadata
            
        # No fields to update
        if not update_data:
            return {
                "error": "No update fields provided",
                "success": False
            }
        
        # Update memory
        success = await structured_memory.update_memory(
            memory_id=memory_id,
            **update_data
        )
        
        # Return result
        return {
            "success": success,
            "memory_id": memory_id
        }
    except Exception as e:
        logger.error(f"Error updating structured memory: {e}")
        return {
            "error": f"Error updating structured memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="structured_memory",
    description="Capability for structured memory operations",
    modality="memory"
)
@mcp_tool(
    name="StructuredMemoryDelete",
    description="Delete a memory from the structured memory system",
    tags=["memory", "structured", "delete"],
    category="structured_memory"
)
async def structured_memory_delete(
    memory_id: str,
    structured_memory: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Delete a memory from the structured memory system.
    
    Args:
        memory_id: ID of the memory to delete
        structured_memory: Structured memory service to use (injected)
        
    Returns:
        Result of the delete operation
    """
    if not structured_memory:
        return {
            "error": "Structured memory service not provided"
        }
        
    try:
        # Delete memory
        success = await structured_memory.delete_memory(memory_id)
        
        # Return result
        return {
            "success": success,
            "memory_id": memory_id
        }
    except Exception as e:
        logger.error(f"Error deleting structured memory: {e}")
        return {
            "error": f"Error deleting structured memory: {str(e)}",
            "success": False
        }

@mcp_capability(
    name="structured_memory",
    description="Capability for structured memory operations",
    modality="memory"
)
@mcp_tool(
    name="StructuredMemorySearch",
    description="Search for memories in the structured memory system",
    tags=["memory", "structured", "search"],
    category="structured_memory"
)
async def structured_memory_search(
    query: str,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    min_importance: Optional[int] = None,
    limit: int = 10,
    structured_memory: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Search for memories in the structured memory system.
    
    Args:
        query: Search query
        category: Category to filter by (optional)
        tags: Tags to filter by (optional)
        min_importance: Minimum importance level (optional)
        limit: Maximum number of results
        structured_memory: Structured memory service to use (injected)
        
    Returns:
        Search results
    """
    if not structured_memory:
        return {
            "error": "Structured memory service not provided"
        }
        
    try:
        # Search memories
        results = await structured_memory.search_memories(
            query=query,
            category=category,
            tags=tags,
            min_importance=min_importance,
            limit=limit
        )
        
        # Return results
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error searching structured memories: {e}")
        return {
            "error": f"Error searching structured memories: {str(e)}",
            "success": False,
            "results": []
        }

# --- Nexus Operations ---

@mcp_capability(
    name="nexus_operations",
    description="Capability for Nexus processing operations",
    modality="agent"
)
@mcp_tool(
    name="NexusProcess",
    description="Process a message through the Nexus interface",
    tags=["nexus", "process", "message"],
    category="nexus_operations"
)
async def nexus_process(
    message: str,
    is_user: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
    auto_agency: Optional[bool] = None,
    nexus: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Process a message through the Nexus interface.
    
    Args:
        message: Message to process
        is_user: Whether the message is from the user
        metadata: Additional message metadata
        auto_agency: Whether to use automatic agency
        nexus: Nexus interface to use (injected)
        
    Returns:
        Processing result
    """
    if not nexus:
        return {
            "error": "Nexus interface not provided"
        }
        
    try:
        # Process message
        result = await nexus.process_message(
            message=message,
            is_user=is_user,
            metadata=metadata,
            auto_agency=auto_agency
        )
        
        # Return result
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        logger.error(f"Error processing message through Nexus: {e}")
        return {
            "error": f"Error processing message through Nexus: {str(e)}",
            "success": False
        }

# --- Registration Functions ---

async def register_memory_tools(memory_manager, tool_registry):
    """Register memory tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, skipping memory tool registration")
        return
        
    try:
        # Get memory service
        client_id = getattr(memory_manager, "default_client_id", "claude")
        memory_service = await memory_manager.get_memory_service(client_id)
        
        # Add memory service to tool kwargs
        memory_store.memory_service = memory_service
        memory_query.memory_service = memory_service
        get_context.memory_service = memory_service
        
        # Register tools with tool registry
        await tool_registry.register_tool(memory_store._mcp_tool_meta.to_dict())
        await tool_registry.register_tool(memory_query._mcp_tool_meta.to_dict())
        await tool_registry.register_tool(get_context._mcp_tool_meta.to_dict())
        
        logger.info("Registered memory tools with MCP service")
    except Exception as e:
        logger.error(f"Error registering memory tools: {e}")

async def register_structured_memory_tools(memory_manager, tool_registry):
    """Register structured memory tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, skipping structured memory tool registration")
        return
        
    try:
        # Get structured memory service
        client_id = getattr(memory_manager, "default_client_id", "claude")
        structured_memory = await memory_manager.get_structured_memory(client_id)
        
        # Add structured memory to tool kwargs
        structured_memory_add.structured_memory = structured_memory
        structured_memory_get.structured_memory = structured_memory
        structured_memory_update.structured_memory = structured_memory
        structured_memory_delete.structured_memory = structured_memory
        structured_memory_search.structured_memory = structured_memory
        
        # Register tools with tool registry
        await tool_registry.register_tool(structured_memory_add._mcp_tool_meta.to_dict())
        await tool_registry.register_tool(structured_memory_get._mcp_tool_meta.to_dict())
        await tool_registry.register_tool(structured_memory_update._mcp_tool_meta.to_dict())
        await tool_registry.register_tool(structured_memory_delete._mcp_tool_meta.to_dict())
        await tool_registry.register_tool(structured_memory_search._mcp_tool_meta.to_dict())
        
        logger.info("Registered structured memory tools with MCP service")
    except Exception as e:
        logger.error(f"Error registering structured memory tools: {e}")

async def register_nexus_tools(memory_manager, tool_registry):
    """Register nexus tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, skipping nexus tool registration")
        return
        
    try:
        # Get nexus interface
        client_id = getattr(memory_manager, "default_client_id", "claude")
        nexus = await memory_manager.get_nexus_interface(client_id)
        
        # Add nexus to tool kwargs
        nexus_process.nexus = nexus
        
        # Register tools with tool registry
        await tool_registry.register_tool(nexus_process._mcp_tool_meta.to_dict())
        
        logger.info("Registered nexus tools with MCP service")
    except Exception as e:
        logger.error(f"Error registering nexus tools: {e}")

def get_all_tools(memory_manager=None):
    """Get all Engram MCP tools."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, returning empty tools list")
        return []
        
    from tekton.mcp.fastmcp.schema import MCPTool
    
    tools = []
    
    # Memory tools
    tools.append(memory_store._mcp_tool_meta.to_dict())
    tools.append(memory_query._mcp_tool_meta.to_dict())
    tools.append(get_context._mcp_tool_meta.to_dict())
    
    # Structured memory tools
    tools.append(structured_memory_add._mcp_tool_meta.to_dict())
    tools.append(structured_memory_get._mcp_tool_meta.to_dict())
    tools.append(structured_memory_update._mcp_tool_meta.to_dict())
    tools.append(structured_memory_delete._mcp_tool_meta.to_dict())
    tools.append(structured_memory_search._mcp_tool_meta.to_dict())
    
    # Nexus tools
    tools.append(nexus_process._mcp_tool_meta.to_dict())
    
    return tools

def get_all_capabilities(memory_manager=None):
    """Get all Engram MCP capabilities."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, returning empty capabilities list")
        return []
        
    from tekton.mcp.fastmcp.schema import MCPCapability
    
    capabilities = []
    
    # Add unique capabilities
    capability_names = set()
    
    # Memory operations capability
    if "memory_operations" not in capability_names:
        capabilities.append(MCPCapability(
            name="memory_operations",
            description="Capability for core memory operations",
            modality="memory"
        ))
        capability_names.add("memory_operations")
    
    # Structured memory capability
    if "structured_memory" not in capability_names:
        capabilities.append(MCPCapability(
            name="structured_memory",
            description="Capability for structured memory operations",
            modality="memory"
        ))
        capability_names.add("structured_memory")
    
    # Nexus operations capability
    if "nexus_operations" not in capability_names:
        capabilities.append(MCPCapability(
            name="nexus_operations",
            description="Capability for Nexus processing operations",
            modality="agent"
        ))
        capability_names.add("nexus_operations")
    
    return capabilities