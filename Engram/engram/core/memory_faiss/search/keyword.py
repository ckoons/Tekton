#!/usr/bin/env python3
"""
Keyword-based memory search functionality
"""

from typing import Dict, List, Any, Optional

# Import from the utilities
from ..utils.logging import setup_logger

# Initialize logger
logger = setup_logger("engram.memory.search")

async def keyword_search(
    memory_service,
    query: str, 
    namespace: str = "conversations", 
    limit: int = 5,
    check_forget: bool = True
) -> Dict[str, Any]:
    """
    Search for memories using keyword matching.
    
    Args:
        memory_service: The memory service instance
        query: The search query
        namespace: The namespace to search in
        limit: Maximum number of results to return
        check_forget: Whether to check for and filter out forgotten information
        
    Returns:
        Dictionary with search results
    """
    try:
        # Get forgotten items if needed
        forgotten_items = []
        if check_forget and namespace != "longterm":
            try:
                # Search for FORGET instructions
                forget_results = await memory_service.search(
                    query="FORGET/IGNORE",
                    namespace="longterm",
                    limit=100,
                    check_forget=False  # Prevent recursion
                )
                
                # Extract the forgotten items
                for item in forget_results.get("results", []):
                    content = item.get("content", "")
                    if content.startswith("FORGET/IGNORE: "):
                        forgotten_text = content[len("FORGET/IGNORE: "):]
                        forgotten_items.append(forgotten_text)
            except Exception as e:
                logger.error(f"Error checking for forgotten items: {e}")
        
        # Simple keyword matching for fallback
        results = []
        
        for memory in memory_service.fallback_memories.get(namespace, []):
            content = memory.get("content", "")
            if query.lower() in content.lower():
                results.append({
                    "id": memory.get("id", ""),
                    "content": content,
                    "metadata": memory.get("metadata", {}),
                    "relevance": 1.0  # No real relevance score in fallback
                })
        
        # Sort by timestamp (newest first) and limit results
        results.sort(
            key=lambda x: x.get("metadata", {}).get("timestamp", ""), 
            reverse=True
        )
        results = results[:limit]
        
        # Filter results if needed
        if forgotten_items:
            filtered_results = []
            for result in results:
                should_include = True
                content = result.get("content", "")
                
                # Check if any forgotten item appears in this content
                for forgotten in forgotten_items:
                    if forgotten.lower() in content.lower():
                        # This memory contains forgotten information
                        should_include = False
                        logger.debug(f"Filtered out fallback memory containing: {forgotten}")
                        break
                
                if should_include:
                    filtered_results.append(result)
            
            results = filtered_results
        
        return {
            "results": results,
            "count": len(results),
            "namespace": namespace,
            "forgotten_count": len(forgotten_items) if forgotten_items else 0
        }
    except Exception as e:
        logger.error(f"Error performing keyword search: {e}")
        return {"results": [], "count": 0, "namespace": namespace}