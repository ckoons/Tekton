"""
Text-based search functionality for the LanceDB vector store.

This module provides text-based search functionality for the vector store.
"""

import logging
from typing import Dict, List, Any, Optional, Union

# Get logger
logger = logging.getLogger("lancedb_vector_store.search.text")


def text_search(metadata_cache: List[Dict[str, Any]], query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search for text matches in the metadata cache.
    
    Args:
        metadata_cache: List of metadata entries to search
        query: The search query
        top_k: Number of results to return
        
    Returns:
        List of matching documents with metadata and scores
    """
    # Convert to lowercase for case-insensitive matching
    query_lower = query.lower()
    
    results = []
    for entry in metadata_cache:
        # Skip placeholder entries
        if entry.get("placeholder", False):
            continue
            
        if query_lower in entry["text"].lower():
            # Format the result
            results.append({
                "id": entry["id"],
                "text": entry["text"],
                "score": 1.0,  # Exact match gets perfect score
                "metadata": {k: v for k, v in entry.items() 
                           if k not in ["id", "text", "timestamp", "placeholder"]}
            })
        
        if len(results) >= top_k:
            break
    
    return results