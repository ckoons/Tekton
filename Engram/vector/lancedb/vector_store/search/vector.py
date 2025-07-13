"""
Vector-based search functionality for the LanceDB vector store.

This module provides vector-based search functionality for the vector store.
"""

import logging
import lancedb
import pandas as pd
from typing import Dict, List, Any, Optional, Union

# Get logger
logger = logging.getLogger("lancedb_vector_store.search.vector")


def vector_search(db_table, query_embedding: List[float], metadata_cache: List[Dict[str, Any]], 
                 top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search for similar texts using vector similarity.
    
    Args:
        db_table: LanceDB table to search in
        query_embedding: The query embedding vector
        metadata_cache: Fallback metadata cache to use if DB search fails
        top_k: Number of results to return
        
    Returns:
        List of matching documents with metadata and scores
    """
    try:
        # Skip the placeholder record (id=0) in search
        search_query = db_table.search(query_embedding)
        
        # Check if the table is empty (except for placeholder)
        table_empty = len(db_table.to_pandas()) <= 1
        if table_empty:
            logger.warning(f"Table is empty (has only placeholder)")
            return []
            
        # Get search results and then filter out placeholder with pandas
        search_results = search_query.limit(top_k + 1).to_pandas()
        search_results = search_results[search_results["id"] != 0].head(top_k)
        
        # If no results (could happen if only placeholder exists)
        if search_results.empty:
            return []
        
        # Format results
        results = []
        for _, row in search_results.iterrows():
            # Get metadata
            metadata = {k: v for k, v in row.items() 
                       if k not in ["id", "text", "vector", "timestamp", "_distance"]}
            
            # Calculate score (convert distance to similarity score)
            # LanceDB returns L2 distance, so we convert to a similarity score
            # where 1.0 is most similar and 0.0 is least similar
            max_distance = 10.0  # Arbitrary max distance to normalize
            score = max(0.0, 1.0 - (row["_distance"] / max_distance))
            
            # Add to results
            results.append({
                "id": int(row["id"]),
                "text": row["text"],
                "score": score,
                "metadata": metadata
            })
            
        return results
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        # Use metadata cache as fallback
        if metadata_cache:
            logger.warning(f"Using metadata cache as fallback")
            non_placeholder = [item for item in metadata_cache if item.get("id", 0) != 0 
                              and not item.get("placeholder", False)]
            return [{
                "id": item["id"],
                "text": item["text"],
                "score": 0.5,  # Arbitrary score for fallback results
                "metadata": {k: v for k, v in item.items() 
                           if k not in ["id", "text", "timestamp", "placeholder"]}
            } for item in non_placeholder[:top_k]]
        return []


def get_by_id(db_table, memory_id: int, metadata_cache: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Get a memory by its ID.
    
    Args:
        db_table: LanceDB table to search in
        memory_id: The ID of the memory to retrieve
        metadata_cache: Metadata cache for fallback retrieval
        
    Returns:
        The memory if found, None otherwise
    """
    # Look in metadata cache first for faster retrieval
    for entry in metadata_cache:
        if entry.get("id") == memory_id and not entry.get("placeholder", False):
            return {
                "id": entry["id"],
                "text": entry["text"],
                "metadata": {k: v for k, v in entry.items() 
                           if k not in ["id", "text", "timestamp", "placeholder"]}
            }
    
    # Not found in cache, query the database
    try:
        result = db_table.to_pandas(filter=f"id = {memory_id}")
        
        if len(result) > 0:
            row = result.iloc[0]
            return {
                "id": int(row["id"]),
                "text": row["text"],
                "metadata": {k: v for k, v in row.items() 
                           if k not in ["id", "text", "vector", "timestamp"]}
            }
        else:
            return None
    except Exception as e:
        logger.error(f"Failed to get memory by ID: {e}")
        return None