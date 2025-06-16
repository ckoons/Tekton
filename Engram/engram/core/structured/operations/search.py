#!/usr/bin/env python3
"""
Memory Search Operations

Provides functions for searching memories in the structured memory system.
"""

import logging
from typing import Dict, List, Any, Optional

from engram.core.structured.search.content import search_by_content
from engram.core.structured.search.tags import search_by_tags

logger = logging.getLogger("engram.structured.operations.search")

async def search_memories(self, storage, metadata_index, category_importance,
                        query=None, categories=None, tags=None,
                        min_importance=1, limit=10, sort_by="importance") -> List[Dict[str, Any]]:
    """
    Search for memories based on multiple criteria.
    
    Args:
        self: StructuredMemory instance
        storage: MemoryStorage instance
        metadata_index: Current metadata index dictionary
        category_importance: Dictionary mapping categories to importance settings
        query: Text to search for in memory content (optional)
        categories: List of categories to search in (defaults to all)
        tags: List of tags to filter by (optional)
        min_importance: Minimum importance level (1-5)
        limit: Maximum number of results to return
        sort_by: How to sort results ("importance", "recency", or "relevance")
        
    Returns:
        List of matching memory data dictionaries
    """
    try:
        # Default to all categories if not specified
        if categories is None:
            categories = list(category_importance.keys())
            
        # Validate categories
        valid_categories = [c for c in categories if c in category_importance]
        if not valid_categories:
            logger.warning(f"No valid categories specified")
            return []
            
        # If tags are specified, search by tags first
        if tags:
            memories = await search_by_tags(
                storage=storage,
                metadata_index=metadata_index,
                tags=tags,
                min_importance=min_importance,
                limit=limit
            )
        # If query is specified, search by content
        elif query:
            memories = await search_by_content(
                storage=storage,
                metadata_index=metadata_index,
                query=query,
                categories=valid_categories,
                min_importance=min_importance,
                limit=limit
            )
        # Otherwise, get all memories in the categories
        else:
            memories = []
            for category in valid_categories:
                category_memories = metadata_index["categories"][category]["memories"]
                
                # Filter by minimum importance
                for memory_id, metadata in category_memories.items():
                    if metadata["importance"] >= min_importance:
                        memory = await self.get_memory(memory_id)
                        if memory:
                            memories.append(memory)
            
        # Sort memories
        if sort_by == "importance":
            # Sort by importance (higher first), then by timestamp (newest first)
            memories.sort(key=lambda x: (-(x.get("importance", 0)), 
                                       x.get("metadata", {}).get("timestamp", "")))
        elif sort_by == "recency":
            # Sort by timestamp (newest first)
            memories.sort(key=lambda x: x.get("metadata", {}).get("timestamp", ""), 
                        reverse=True)
        elif sort_by == "relevance" and query:
            # Simple relevance scoring
            for memory in memories:
                if "relevance" not in memory:
                    query_count = memory["content"].lower().count(query.lower())
                    memory["relevance"] = query_count * memory.get("importance", 3)
            memories.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        
        # Limit results
        return memories[:limit]
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        return []