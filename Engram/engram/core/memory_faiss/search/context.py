#!/usr/bin/env python3
"""
Context retrieval functionality
"""

from typing import Dict, List, Any, Optional

# Import from the utilities
from ..utils.logging import setup_logger

# Initialize logger
logger = setup_logger("engram.memory.search")

async def get_relevant_context(
    memory_service,
    query: str, 
    namespaces: List[str] = None,
    limit: int = 3
) -> str:
    """
    Get formatted context from multiple namespaces for a given query.
    
    Args:
        memory_service: The memory service instance
        query: The query to search for
        namespaces: List of namespaces to search (default: all)
        limit: Maximum memories per namespace
        
    Returns:
        Formatted context string
    """
    if namespaces is None:
        # Include base namespaces
        namespaces = ["conversations", "thinking", "longterm"]
        
        # Add active compartments
        for compartment_id in memory_service.active_compartments:
            namespaces.append(f"compartment-{compartment_id}")
    
    all_results = []
    
    # Search each namespace
    for namespace in namespaces:
        results = await memory_service.search(query, namespace=namespace, limit=limit)
        
        for item in results.get("results", []):
            all_results.append({
                "namespace": namespace,
                "content": item.get("content", ""),
                "metadata": item.get("metadata", {})
            })
    
    # Format the context
    if not all_results:
        return ""
    
    context_parts = ["### Memory Context\n"]
    
    for namespace in namespaces:
        namespace_results = [r for r in all_results if r["namespace"] == namespace]
        
        if namespace_results:
            if namespace == "conversations":
                context_parts.append(f"\n#### Previous Conversations\n")
            elif namespace == "thinking":
                context_parts.append(f"\n#### Thoughts\n")
            elif namespace == "longterm":
                context_parts.append(f"\n#### Important Information\n")
            elif namespace == "projects":
                context_parts.append(f"\n#### Project Context\n")
            elif namespace == "session":
                context_parts.append(f"\n#### Session Memory\n")
            elif namespace == "compartments":
                context_parts.append(f"\n#### Compartment Information\n")
            elif namespace.startswith("compartment-"):
                compartment_id = namespace[len("compartment-"):]
                compartment_name = memory_service.compartments.get(compartment_id, {}).get("name", compartment_id)
                context_parts.append(f"\n#### Compartment: {compartment_name}\n")
            
            for i, result in enumerate(namespace_results):
                timestamp = result.get("metadata", {}).get("timestamp", "Unknown time")
                content = result.get("content", "")
                
                # Truncate long content
                if len(content) > 500:
                    content = content[:497] + "..."
                
                context_parts.append(f"{i+1}. {content}\n")
    
    return "\n".join(context_parts)