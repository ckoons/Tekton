"""
Search operations for the Hermes Memory Adapter.

This module provides functions for searching and retrieving memories.
"""

from typing import Dict, List, Any, Optional, Union

from ..core.imports import logger, HAS_HERMES
from ..utils.helpers import (
    validate_namespace, 
    filter_forgotten_content,
    format_context
)


async def search_memories(hermes_client, fallback_storage, compartment_manager,
                         query: str, 
                         namespace: str = "conversations", 
                         limit: int = 5,
                         check_forget: bool = True) -> Dict[str, Any]:
    """
    Search for memories based on a query.
    
    Args:
        hermes_client: Hermes database client
        fallback_storage: Fallback storage implementation
        compartment_manager: Compartment manager
        query: Search query
        namespace: Namespace to search in
        limit: Maximum number of results
        check_forget: Whether to check for forgotten information
        
    Returns:
        Dictionary of search results
    """
    # Validate namespace
    valid_namespaces = ["conversations", "thinking", "longterm", "projects", "compartments", "session"]
    namespace = validate_namespace(namespace, valid_namespaces, compartment_manager.compartments)
    
    # Get forgotten items if needed
    forgotten_items = []
    if check_forget and namespace != "longterm":
        try:
            # Search for FORGET instructions
            forget_results = await search_memories(
                hermes_client, fallback_storage, compartment_manager,
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
    
    # Search using Hermes if available
    if HAS_HERMES and hermes_client:
        try:
            # Get vector database for this namespace
            vector_db = await hermes_client.get_vector_db(namespace=namespace)
            
            # Search for similar vectors
            search_results = await vector_db.search(
                query_vector=None,  # Let Hermes generate the embedding
                query=query,  # Provide the raw query for embedding
                limit=limit * 2,  # Request more results to account for filtering
                filter={}  # No filter initially
            )
            
            # Format the results
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "id": result.get("id", ""),
                    "content": result.get("text", ""),
                    "metadata": result.get("metadata", {}),
                    "relevance": result.get("relevance", 0.0)
                })
            
            # Filter out forgotten items
            if forgotten_items:
                formatted_results = filter_forgotten_content(formatted_results, forgotten_items)
            
            # Limit the results
            formatted_results = formatted_results[:limit]
            
            return {
                "results": formatted_results,
                "count": len(formatted_results),
                "namespace": namespace,
                "forgotten_count": len(forgotten_items) if forgotten_items else 0
            }
            
        except Exception as e:
            logger.error(f"Error searching Hermes vector database: {e}")
            # Fall back to local search
    
    # Search fallback memory
    try:
        # Simple keyword matching from fallback storage
        results = fallback_storage.search(query, namespace, limit * 2)
        
        # Filter results if needed
        if forgotten_items:
            results = filter_forgotten_content(results, forgotten_items)
        
        # Limit results
        results = results[:limit]
        
        return {
            "results": results,
            "count": len(results),
            "namespace": namespace,
            "forgotten_count": len(forgotten_items) if forgotten_items else 0
        }
    except Exception as e:
        logger.error(f"Error searching fallback memory: {e}")
        return {"results": [], "count": 0, "namespace": namespace}


async def get_relevant_context(hermes_client, fallback_storage, compartment_manager,
                              query: str, 
                              namespaces: Optional[List[str]] = None,
                              limit: int = 3) -> str:
    """
    Get formatted context from multiple namespaces for a query.
    
    Args:
        hermes_client: Hermes database client
        fallback_storage: Fallback storage implementation
        compartment_manager: Compartment manager
        query: Search query
        namespaces: List of namespaces to search
        limit: Maximum memories per namespace
        
    Returns:
        Formatted context string
    """
    if namespaces is None:
        # Include base namespaces
        namespaces = ["conversations", "thinking", "longterm"]
        
        # Add active compartments
        for compartment_id in compartment_manager.get_active_compartments():
            namespaces.append(f"compartment-{compartment_id}")
    
    all_results = []
    
    # Search each namespace
    for namespace in namespaces:
        results = await search_memories(
            hermes_client, fallback_storage, compartment_manager,
            query, namespace=namespace, limit=limit
        )
        
        for item in results.get("results", []):
            all_results.append({
                "namespace": namespace,
                "content": item.get("content", ""),
                "metadata": item.get("metadata", {})
            })
    
    # Format the context
    return format_context(all_results, namespaces, compartment_manager.compartments)


async def get_namespaces(compartment_manager) -> List[str]:
    """
    Get all available namespaces.
    
    Args:
        compartment_manager: Compartment manager
        
    Returns:
        List of namespace names
    """
    base_namespaces = ["conversations", "thinking", "longterm", "projects", "compartments", "session"]
    
    # Add compartment namespaces
    compartment_namespaces = [
        f"compartment-{c_id}" for c_id in compartment_manager.compartments
    ]
    
    return base_namespaces + compartment_namespaces