#!/usr/bin/env python3
"""
MCP Compatibility layer for the new simple Memory API.

This ensures existing MCP tools continue to work while using the new simplified interface.
"""

from typing import Dict, List, Any, Optional
from engram.simple import Memory


# Global memory instance for MCP tools
_mcp_memory = None


def get_mcp_memory() -> Memory:
    """Get or create the MCP memory instance"""
    global _mcp_memory
    if _mcp_memory is None:
        _mcp_memory = Memory(namespace="mcp")
    return _mcp_memory


async def memory_store(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP-compatible memory store function.
    
    Args:
        params: Dictionary with 'text' and optional metadata
        
    Returns:
        Success response with memory ID
    """
    mem = get_mcp_memory()
    
    text = params.get("text", "")
    metadata = params.get("metadata", {})
    
    # Extract known metadata fields
    if "namespace" in params:
        metadata["namespace"] = params["namespace"]
    if "tags" in params:
        metadata["tags"] = params["tags"]
    if "importance" in params:
        metadata["importance"] = params["importance"]
    
    memory_id = await mem.store(text, **metadata)
    
    return {
        "success": True,
        "memory_id": memory_id,
        "message": "Memory stored successfully"
    }


async def memory_query(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP-compatible memory query function.
    
    Args:
        params: Dictionary with 'query' and optional 'limit'
        
    Returns:
        Success response with memories
    """
    mem = get_mcp_memory()
    
    query = params.get("query", "")
    limit = params.get("limit", 5)
    
    memories = await mem.recall(query, limit=limit)
    
    # Convert to MCP format
    results = []
    for m in memories:
        results.append({
            "id": m.id,
            "text": m.content,
            "timestamp": m.timestamp.isoformat() if m.timestamp else None,
            "metadata": m.metadata,
            "score": m.relevance
        })
    
    return {
        "success": True,
        "memories": results,
        "count": len(results)
    }


async def get_context(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP-compatible context retrieval function.
    
    Args:
        params: Dictionary with 'query' and optional 'limit'
        
    Returns:
        Success response with context
    """
    mem = get_mcp_memory()
    
    query = params.get("query", "")
    limit = params.get("limit", 10)
    
    context = await mem.context(query, limit=limit)
    
    return {
        "success": True,
        "context": context
    }


# MCP tool definitions that can be registered
MCP_TOOLS = {
    "memory_store": {
        "function": memory_store,
        "description": "Store a memory",
        "parameters": {
            "text": {"type": "string", "required": True},
            "namespace": {"type": "string", "required": False},
            "metadata": {"type": "object", "required": False}
        }
    },
    "memory_query": {
        "function": memory_query,
        "description": "Query memories",
        "parameters": {
            "query": {"type": "string", "required": True},
            "limit": {"type": "integer", "required": False, "default": 5}
        }
    },
    "get_context": {
        "function": get_context,
        "description": "Get relevant context",
        "parameters": {
            "query": {"type": "string", "required": True},
            "limit": {"type": "integer", "required": False, "default": 10}
        }
    }
}