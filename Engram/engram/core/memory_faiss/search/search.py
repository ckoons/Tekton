#!/usr/bin/env python3
"""
Unified memory search functionality
"""

from typing import Dict, List, Any, Optional

# Import from the utilities
from ..utils.logging import setup_logger
from .vector import vector_search
from .keyword import keyword_search
from .context import get_relevant_context

# Initialize logger
logger = setup_logger("engram.memory.search")

async def search(
    memory_service,
    query: str, 
    namespace: str = "conversations", 
    limit: int = 5,
    check_forget: bool = True
) -> Dict[str, Any]:
    """
    Search for memories based on a query.
    
    Args:
        memory_service: The memory service instance
        query: The search query
        namespace: The namespace to search in
        limit: Maximum number of results to return
        check_forget: Whether to check for and filter out forgotten information
        
    Returns:
        Dictionary with search results
    """
    # Check if namespace is a valid base namespace or a compartment
    from ..utils.helpers import is_valid_namespace
    
    if not is_valid_namespace(namespace, memory_service.namespaces, memory_service.compartments):
        logger.warning(f"Invalid namespace: {namespace}, using 'conversations'")
        namespace = "conversations"
    
    # Use vector search if available, otherwise fall back to keyword search
    if memory_service.vector_available:
        return await vector_search(
            memory_service=memory_service,
            query=query, 
            namespace=namespace, 
            limit=limit,
            check_forget=check_forget
        )
    else:
        return await keyword_search(
            memory_service=memory_service,
            query=query, 
            namespace=namespace, 
            limit=limit,
            check_forget=check_forget
        )