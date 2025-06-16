#!/usr/bin/env python3
"""
Content-based Memory Search

Provides functions for searching memories by their content.
"""

import logging
from typing import Dict, List, Any, Optional

from engram.core.structured.utils import extract_keywords

logger = logging.getLogger("engram.structured.search.content")

async def search_by_content(storage, metadata_index, query, categories=None,
                         min_importance=1, limit=10) -> List[Dict[str, Any]]:
    """
    Search memories by their content, supporting simple keyword matching.
    
    Args:
        storage: MemoryStorage instance
        metadata_index: Current metadata index dictionary
        query: The search query text
        categories: List of categories to search (defaults to all)
        min_importance: Minimum importance level (1-5)
        limit: Maximum number of results to return
        
    Returns:
        List of matching memory dictionaries
    """
    try:
        if not query or not query.strip():
            logger.warning("Empty query provided for content search")
            return []
            
        # Default to all categories if not specified
        if categories is None:
            categories = metadata_index["categories"].keys()
            
        # Extract keywords for search
        keywords = extract_keywords(query)
        
        if not keywords:
            logger.warning(f"No keywords extracted from query: {query}")
            return []
            
        # Set up results
        matched_memories = []
        query_lower = query.lower()
        
        # Search through categories
        for category in categories:
            # Get memory IDs for this category
            if category not in metadata_index["categories"]:
                continue
                
            memory_metadata = metadata_index["categories"][category]["memories"]
            
            # Check each memory in the category
            for memory_id, meta in memory_metadata.items():
                # Filter by importance
                if meta["importance"] < min_importance:
                    continue
                    
                # Load the full memory
                memory = await storage.load_memory(memory_id, category)
                if not memory:
                    continue
                    
                # Check for keyword matches
                memory_content = memory["content"].lower()
                
                # Count matches for scoring
                exact_match_score = 10 if query_lower in memory_content else 0
                keyword_match_count = sum(1 for kw in keywords if kw in memory_content)
                
                if exact_match_score > 0 or keyword_match_count > 0:
                    # Calculate relevance score
                    score = (
                        exact_match_score +
                        keyword_match_count +
                        memory["importance"]
                    )
                    
                    # Add relevance score to memory
                    memory["relevance"] = score
                    matched_memories.append(memory)
                    
                    # Break early if we've found enough results
                    if len(matched_memories) >= limit * 2:  # Get extra for sorting
                        break
                        
        # Sort by relevance and limit results
        matched_memories.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        return matched_memories[:limit]
    except Exception as e:
        logger.error(f"Error in content search: {e}")
        return []