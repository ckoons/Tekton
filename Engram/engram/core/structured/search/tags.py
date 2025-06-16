#!/usr/bin/env python3
"""
Tag-based Memory Search

Provides functions for searching memories by their tags.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("engram.structured.search.tags")

async def search_by_tags(storage, metadata_index, tags, min_importance=1, limit=10) -> List[Dict[str, Any]]:
    """
    Search memories by their tags, returning those that match any of the specified tags.
    
    Args:
        storage: MemoryStorage instance
        metadata_index: Current metadata index dictionary
        tags: List of tags to search for
        min_importance: Minimum importance level (1-5)
        limit: Maximum number of results to return
        
    Returns:
        List of matching memory dictionaries
    """
    try:
        if not tags:
            logger.warning("No tags provided for tag search")
            return []
            
        # Get all memory IDs that match any of the tags
        matching_memory_ids = set()
        
        for tag in tags:
            if tag in metadata_index["tags"]:
                matching_memory_ids.update(metadata_index["tags"][tag])
                
        if not matching_memory_ids:
            logger.info(f"No memories found with tags: {tags}")
            return []
            
        # Load and filter memories
        memories = []
        for memory_id in matching_memory_ids:
            # Determine category from ID
            if "-" not in memory_id:
                continue
                
            category = memory_id.split("-")[0]
            
            # Check if memory exists in the index
            if category not in metadata_index["categories"] or \
               memory_id not in metadata_index["categories"][category]["memories"]:
                continue
                
            # Check importance
            memory_meta = metadata_index["categories"][category]["memories"][memory_id]
            if memory_meta["importance"] < min_importance:
                continue
                
            # Load the memory
            memory = await storage.load_memory(memory_id, category)
            if memory:
                # Calculate tag match score for relevance
                memory_tags = set(memory.get("tags", []))
                tag_match_count = len(memory_tags.intersection(set(tags)))
                
                # Add relevance score combining tag matches and importance
                memory["relevance"] = tag_match_count * 2 + memory["importance"]
                memories.append(memory)
                
        # Sort by relevance and limit results
        memories.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        return memories[:limit]
    except Exception as e:
        logger.error(f"Error in tag search: {e}")
        return []