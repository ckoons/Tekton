#!/usr/bin/env python3
"""
Semantic Memory Search

Provides functions for semantic search of memories using vector embeddings if available.
"""

import logging
from typing import Dict, List, Any, Optional

from engram.core.structured.search.content import search_by_content

logger = logging.getLogger("engram.structured.search.semantic")

async def search_semantic_memories(storage, metadata_index, query, limit=10) -> List[Dict[str, Any]]:
    """
    Search memories using semantic similarity if available, falling back to keyword search.
    
    This function attempts to use vector embeddings for semantic search, but falls back
    to keyword-based search if vector search is not available.
    
    Args:
        storage: MemoryStorage instance
        metadata_index: Current metadata index dictionary
        query: Semantic query text
        limit: Maximum number of results to return
        
    Returns:
        List of semantically relevant memory dictionaries
    """
    try:
        # Try to import MemoryService for vector search
        try:
            from engram.core.memory import MemoryService
            has_vector_search = True
        except ImportError:
            has_vector_search = False
            logger.info("Vector search not available, falling back to keyword search")
            
        # If vector search is available, use it
        if has_vector_search:
            try:
                # Instantiate MemoryService
                memory_service = MemoryService()
                
                # Create an empty list for results
                vector_results = []
                
                # Get categories from metadata
                categories = list(metadata_index["categories"].keys())
                
                # Search each category
                for category in categories:
                    # Create a namespace for the category
                    namespace = f"structured_{category}"
                    
                    # Perform semantic search
                    search_results = await memory_service.search(
                        query=query,
                        namespace=namespace,
                        limit=limit // len(categories) + 1  # Distribute limit
                    )
                    
                    # Process results
                    for result in search_results.get("results", []):
                        content = result.get("content")
                        score = result.get("score", 0)
                        
                        # Find matching memory by content
                        memory = None
                        for memory_id, meta in metadata_index["categories"][category]["memories"].items():
                            memory_data = await storage.load_memory(memory_id, category)
                            if memory_data and memory_data["content"] == content:
                                memory = memory_data
                                break
                                
                        if memory:
                            # Add semantic score
                            memory["relevance"] = score * 10  # Scale up vector scores
                            vector_results.append(memory)
                            
                # If we got vector results, return them
                if vector_results:
                    # Sort by relevance
                    vector_results.sort(key=lambda x: x.get("relevance", 0), reverse=True)
                    return vector_results[:limit]
            except Exception as e:
                logger.warning(f"Error in vector search, falling back to keyword search: {e}")
                
        # Fall back to keyword-based search
        return await search_by_content(
            storage=storage,
            metadata_index=metadata_index,
            query=query,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error in semantic memory search: {e}")
        return []