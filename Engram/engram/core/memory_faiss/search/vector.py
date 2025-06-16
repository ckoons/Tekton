#!/usr/bin/env python3
"""
Vector-based memory search functionality
"""

from typing import Dict, List, Any, Optional

# Import from the utilities
from ..utils.logging import setup_logger

# Initialize logger
logger = setup_logger("engram.memory.search")

async def vector_search(
    memory_service,
    query: str, 
    namespace: str = "conversations", 
    limit: int = 5,
    check_forget: bool = True
) -> Dict[str, Any]:
    """
    Search for memories using vector similarity.
    
    Args:
        memory_service: The memory service instance
        query: The search query
        namespace: The namespace to search in
        limit: Maximum number of results to return
        check_forget: Whether to check for and filter out forgotten information
        
    Returns:
        Dictionary with search results
    """
    if not memory_service.vector_available:
        logger.warning("Vector search not available. Using fallback search.")
        return {"results": [], "count": 0, "namespace": namespace}
    
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
        
        # Get the appropriate collection
        collection_name = memory_service.namespace_collections.get(namespace)
        if not collection_name and namespace.startswith("compartment-"):
            compartment_id = namespace[len("compartment-"):]
            collection_name = f"engram-{memory_service.client_id}-compartment-{compartment_id}"
        
        if not collection_name:
            raise ValueError(f"No collection found for namespace: {namespace}")
        
        # Search using vector store
        search_results = memory_service.vector_store.search(
            compartment=collection_name,
            query=query,
            top_k=limit * 2  # Request more to account for filtering
        )
        
        # Format the results
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                "id": result.get("id", ""),
                "content": result.get("text", ""),
                "metadata": result.get("metadata", {}),
                "relevance": result.get("score", 0.0)
            })
        
        # Filter out forgotten items
        if forgotten_items:
            filtered_results = []
            for result in formatted_results:
                should_include = True
                content = result.get("content", "")
                
                # Check if any forgotten item appears in this content
                for forgotten in forgotten_items:
                    if forgotten.lower() in content.lower():
                        # This memory contains forgotten information
                        should_include = False
                        logger.debug(f"Filtered out memory containing: {forgotten}")
                        break
                
                if should_include:
                    filtered_results.append(result)
            
            formatted_results = filtered_results
        
        # Limit the results
        formatted_results = formatted_results[:limit]
        
        return {
            "results": formatted_results,
            "count": len(formatted_results),
            "namespace": namespace,
            "forgotten_count": len(forgotten_items) if forgotten_items else 0
        }
    except Exception as e:
        logger.error(f"Error performing vector search: {e}")
        return {"results": [], "count": 0, "namespace": namespace}