#!/usr/bin/env python3
"""
Memory Search Module

Provides search functionality across memory namespaces with relevance ranking.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from engram.core.memory.utils import truncate_content

logger = logging.getLogger("engram.memory.search")

async def search_memory(
    storage, 
    query: str, 
    namespace: str = "conversations", 
    limit: int = 5,
    check_forget: bool = True
) -> Dict[str, Any]:
    """
    Search for memories based on a query.
    
    Args:
        storage: Storage backend to use (file or vector)
        query: The search query
        namespace: The namespace to search in
        limit: Maximum number of results to return
        check_forget: Whether to check for and filter out forgotten information
        
    Returns:
        Dictionary with search results
    """
    # Get forgotten items if needed
    forgotten_items = []
    if check_forget and namespace != "longterm":
        try:
            # Search for FORGET instructions
            forget_results = await search_memory(
                storage=storage,
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
    
    # Perform the search
    results = storage.search(query, namespace, limit * 2)  # Get extra for filtering
    
    # Ensure results is a list
    if results is None:
        results = []
    
    # Filter out forgotten items
    if forgotten_items:
        filtered_results = []
        for result in results:
            if result is None:
                continue
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
        
        results = filtered_results
    
    # Ensure results is still a list after filtering
    if results is None:
        results = []
    
    # Limit the results
    results = results[:limit]
    
    # Filter out any None values that might have slipped through
    results = [r for r in results if r is not None]
    
    return {
        "results": results,
        "count": len(results),
        "namespace": namespace,
        "forgotten_count": len(forgotten_items) if forgotten_items else 0
    }

async def get_relevant_context(
    storage,
    query: str, 
    namespaces: List[str] = None,
    limit: int = 3
) -> str:
    """
    Get formatted context from multiple namespaces for a given query.
    
    Args:
        storage: Storage backend to use (file or vector)
        query: The query to search for
        namespaces: List of namespaces to search (default: standard namespaces)
        limit: Maximum memories per namespace
        
    Returns:
        Formatted context string
    """
    # Use standard namespaces if none provided
    if namespaces is None:
        # Include base namespaces
        from engram.core.memory import STANDARD_NAMESPACES
        namespaces = ["conversations", "thinking", "longterm"]
        
        # Add active compartments if available
        if hasattr(storage, "get_active_compartments"):
            active_compartments = storage.get_active_compartments()
            for compartment_id in active_compartments:
                namespaces.append(f"compartment-{compartment_id}")
    
    all_results = []
    
    # Search each namespace
    for namespace in namespaces:
        results = await search_memory(
            storage=storage,
            query=query, 
            namespace=namespace, 
            limit=limit
        )
        
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
            # Format header based on namespace
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
                compartment_name = "Unknown"
                
                # Try to get compartment name if available
                if hasattr(storage, "compartments"):
                    compartment_name = storage.compartments.get(
                        compartment_id, {}
                    ).get("name", compartment_id)
                    
                context_parts.append(f"\n#### Compartment: {compartment_name}\n")
            
            # Add each result with formatting
            for i, result in enumerate(namespace_results):
                content = result.get("content", "")
                
                # Truncate long content
                content = truncate_content(content)
                
                context_parts.append(f"{i+1}. {content}\n")
    
    return "\n".join(context_parts)