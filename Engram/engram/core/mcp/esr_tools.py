"""
MCP Tools for ESR (Encoding Storage Retrieval) System.

This module provides MCP-compatible tools for memory operations
using the Cognitive Workflows system.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

# Import cognitive workflows
try:
    from engram.core.storage.cognitive_workflows import CognitiveWorkflows, ThoughtType
    from engram.core.storage.unified_interface import ESRMemorySystem
    ESR_AVAILABLE = True
except ImportError as e:
    ESR_AVAILABLE = False
    logger = logging.getLogger("engram.mcp.esr_tools")
    logger.warning(f"ESR system not available: {e}")

logger = logging.getLogger("engram.mcp.esr_tools")


# Global ESR instance (initialized on first use)
_esr_system = None
_cognitive_workflows = None


async def get_esr_system():
    """Get or create the global ESR system."""
    global _esr_system, _cognitive_workflows
    
    if not ESR_AVAILABLE:
        raise RuntimeError("ESR system not available")
    
    if _esr_system is None:
        # Initialize ESR system
        _esr_system = ESRMemorySystem(
            cache_size=100000,
            enable_backends={'vector', 'document', 'kv', 'sql'},
            config={
                'namespace': 'engram',
                'data_dir': '/tmp/tekton/engram/esr_data'
            }
        )
        await _esr_system.start()
        
        # Initialize cognitive workflows
        if hasattr(_esr_system, 'encoder') and hasattr(_esr_system, 'cache'):
            _cognitive_workflows = CognitiveWorkflows(
                cache=_esr_system.cache,
                encoder=_esr_system.encoder
            )
            logger.info("ESR system and Cognitive Workflows initialized")
        else:
            raise RuntimeError("ESR system initialized but cache/encoder not available")
    
    return _esr_system, _cognitive_workflows


# MCP Tool Definitions

async def esr_store_thought(
    content: str,
    thought_type: str = "IDEA",
    context: Optional[Dict[str, Any]] = None,
    associations: Optional[List[str]] = None,
    confidence: float = 1.0,
    ci_id: str = "system"
) -> Dict[str, Any]:
    """
    Store a thought in the ESR system.
    
    Args:
        content: The thought content to store
        thought_type: Type of thought (IDEA, MEMORY, FACT, etc.)
        context: Optional context metadata
        associations: Optional list of associated memory IDs
        confidence: Confidence level (0-1)
        ci_id: CI identifier
        
    Returns:
        Dictionary with memory_id and status
    """
    try:
        _, workflows = await get_esr_system()
        
        # Convert string thought_type to enum
        try:
            thought_enum = ThoughtType[thought_type.upper()]
        except KeyError:
            thought_enum = ThoughtType.IDEA
        
        # Store the thought
        memory_id = await workflows.store_thought(
            content=content,
            thought_type=thought_enum,
            context=context or {},
            associations=associations or [],
            confidence=confidence,
            ci_id=ci_id
        )
        
        return {
            "status": "success",
            "memory_id": memory_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error storing thought: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


async def esr_recall_thought(
    memory_id: str,
    ci_id: str = "system"
) -> Dict[str, Any]:
    """
    Recall a specific thought from memory.
    
    Args:
        memory_id: The memory ID to recall
        ci_id: CI identifier
        
    Returns:
        Dictionary with memory content or error
    """
    try:
        _, workflows = await get_esr_system()
        
        # Recall the thought
        memory = await workflows.recall_thought(memory_id, ci_id=ci_id)
        
        if memory:
            return {
                "status": "success",
                "memory": memory,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "not_found",
                "memory_id": memory_id
            }
            
    except Exception as e:
        logger.error(f"Error recalling thought: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


async def esr_search_similar(
    query: str,
    limit: int = 10,
    thought_type: Optional[str] = None,
    min_confidence: float = 0.5,
    ci_id: str = "system"
) -> Dict[str, Any]:
    """
    Search for similar thoughts in memory.
    
    Args:
        query: Search query
        limit: Maximum number of results
        thought_type: Optional filter by thought type
        min_confidence: Minimum confidence threshold
        ci_id: CI identifier
        
    Returns:
        Dictionary with search results
    """
    try:
        _, workflows = await get_esr_system()
        
        # Convert thought_type if provided
        thought_enum = None
        if thought_type:
            try:
                thought_enum = ThoughtType[thought_type.upper()]
            except KeyError:
                pass
        
        # Search for similar thoughts
        # Note: recall_similar takes 'reference' not 'query', and doesn't support thought_type/min_confidence
        results = await workflows.recall_similar(
            reference=query,
            limit=limit,
            ci_id=ci_id
        )
        
        # Filter by thought_type and min_confidence if provided
        if thought_type or min_confidence > 0:
            filtered_results = []
            for thought in results:
                if thought_type and thought.thought_type.value != thought_type.upper():
                    continue
                if thought.confidence < min_confidence:
                    continue
                filtered_results.append(thought)
            results = filtered_results
        
        # Convert Thought objects to dictionaries for JSON serialization
        results_dict = [
            thought.to_dict() if hasattr(thought, 'to_dict') else thought
            for thought in results
        ]
        
        return {
            "status": "success",
            "results": results_dict,
            "count": len(results_dict),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error searching thoughts: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


async def esr_build_context(
    topic: str,
    depth: int = 3,
    max_items: int = 20,
    ci_id: str = "system"
) -> Dict[str, Any]:
    """
    Build context around a topic.
    
    Args:
        topic: Topic to build context for
        depth: Depth of context building
        max_items: Maximum items in context
        ci_id: CI identifier
        
    Returns:
        Dictionary with context information
    """
    try:
        _, workflows = await get_esr_system()
        
        # Build context
        # Note: build_context doesn't have max_items parameter
        context = await workflows.build_context(
            topic=topic,
            depth=depth,
            ci_id=ci_id
        )
        
        # If max_items is specified, limit the results
        if max_items and isinstance(context, dict):
            for key in context:
                if isinstance(context[key], list) and len(context[key]) > max_items:
                    context[key] = context[key][:max_items]
        
        return {
            "status": "success",
            "context": context,
            "topic": topic,
            "depth": depth,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error building context: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


async def esr_create_association(
    from_memory: str,
    to_memory: str,
    association_type: str = "related",
    strength: float = 1.0,
    ci_id: str = "system"
) -> Dict[str, Any]:
    """
    Create an association between memories.
    
    Args:
        from_memory: Source memory ID
        to_memory: Target memory ID
        association_type: Type of association
        strength: Association strength (0-1)
        ci_id: CI identifier
        
    Returns:
        Dictionary with association status
    """
    try:
        _, workflows = await get_esr_system()
        
        # Create the association (using store_thought with association metadata)
        association_id = await workflows.store_thought(
            content={
                "type": "association",
                "from": from_memory,
                "to": to_memory,
                "association_type": association_type,
                "strength": strength
            },
            thought_type=ThoughtType.MEMORY,
            associations=[from_memory, to_memory],
            confidence=strength,
            ci_id=ci_id
        )
        
        return {
            "status": "success",
            "association_id": association_id,
            "from": from_memory,
            "to": to_memory,
            "type": association_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating association: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


async def esr_get_metabolism_status(
    ci_id: str = "system"
) -> Dict[str, Any]:
    """
    Get the status of memory metabolism.
    
    Args:
        ci_id: CI identifier
        
    Returns:
        Dictionary with metabolism status
    """
    try:
        _, workflows = await get_esr_system()
        
        # Get metabolism statistics
        if hasattr(workflows, 'metabolism_stats'):
            stats = workflows.metabolism_stats
        else:
            stats = {
                "total_memories": 0,
                "promoted": 0,
                "forgotten": 0,
                "last_metabolism": None
            }
        
        return {
            "status": "success",
            "metabolism": stats,
            "ci_id": ci_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting metabolism status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


async def esr_trigger_reflection(
    ci_id: str = "system",
    reason: str = "explicit_request"
) -> Dict[str, Any]:
    """
    Trigger memory reflection for a CI.
    
    Args:
        ci_id: CI identifier
        reason: Reason for triggering reflection
        
    Returns:
        Dictionary with reflection status
    """
    try:
        _, workflows = await get_esr_system()
        
        # Trigger metabolism/reflection
        if hasattr(workflows, 'trigger_metabolism'):
            await workflows.trigger_metabolism()
            
        return {
            "status": "success",
            "action": "reflection_triggered",
            "ci_id": ci_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering reflection: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


async def esr_get_namespaces() -> Dict[str, Any]:
    """
    Get list of available namespaces.
    
    Returns:
        Dictionary with namespace information
    """
    try:
        esr_system, _ = await get_esr_system()
        
        # Get namespaces from backends
        namespaces = set()
        
        if hasattr(esr_system, 'backends'):
            for backend in esr_system.backends.values():
                if hasattr(backend, 'namespace'):
                    namespaces.add(backend.namespace)
        
        return {
            "status": "success",
            "namespaces": list(namespaces),
            "count": len(namespaces),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting namespaces: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# Register tools for MCP if available
MCP_TOOLS = {
    "esr_store_thought": {
        "function": esr_store_thought,
        "description": "Store a thought in the ESR memory system",
        "parameters": {
            "content": "The thought content to store",
            "thought_type": "Type of thought (IDEA, MEMORY, FACT, OPINION, QUESTION, ANSWER, PLAN, REFLECTION, FEELING, OBSERVATION)",
            "context": "Optional context metadata",
            "associations": "Optional list of associated memory IDs",
            "confidence": "Confidence level (0-1)",
            "ci_id": "CI identifier"
        }
    },
    "esr_recall_thought": {
        "function": esr_recall_thought,
        "description": "Recall a specific thought from memory",
        "parameters": {
            "memory_id": "The memory ID to recall",
            "ci_id": "CI identifier"
        }
    },
    "esr_search_similar": {
        "function": esr_search_similar,
        "description": "Search for similar thoughts in memory",
        "parameters": {
            "query": "Search query",
            "limit": "Maximum number of results",
            "thought_type": "Optional filter by thought type",
            "min_confidence": "Minimum confidence threshold",
            "ci_id": "CI identifier"
        }
    },
    "esr_build_context": {
        "function": esr_build_context,
        "description": "Build context around a topic",
        "parameters": {
            "topic": "Topic to build context for",
            "depth": "Depth of context building",
            "max_items": "Maximum items in context",
            "ci_id": "CI identifier"
        }
    },
    "esr_create_association": {
        "function": esr_create_association,
        "description": "Create an association between memories",
        "parameters": {
            "from_memory": "Source memory ID",
            "to_memory": "Target memory ID",
            "association_type": "Type of association",
            "strength": "Association strength (0-1)",
            "ci_id": "CI identifier"
        }
    },
    "esr_get_metabolism_status": {
        "function": esr_get_metabolism_status,
        "description": "Get the status of memory metabolism",
        "parameters": {
            "ci_id": "CI identifier"
        }
    },
    "esr_trigger_reflection": {
        "function": esr_trigger_reflection,
        "description": "Trigger memory reflection for a CI",
        "parameters": {
            "ci_id": "CI identifier",
            "reason": "Reason for triggering reflection"
        }
    },
    "esr_get_namespaces": {
        "function": esr_get_namespaces,
        "description": "Get list of available namespaces",
        "parameters": {}
    }
}