#!/usr/bin/env python3
"""
Memory Retrieval Operations

Provides functions for retrieving memories from the structured memory system.
"""

import logging
from typing import Dict, List, Any, Optional

from engram.core.structured.utils import format_memory_digest
from engram.core.structured.search.content import search_by_content
from engram.core.structured.search.tags import search_by_tags
from engram.core.structured.search.context import search_context_memories
from engram.core.structured.search.semantic import search_semantic_memories

logger = logging.getLogger("engram.structured.operations.retrieve")

async def get_memory(storage, category_importance, memory_id) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific memory by ID.
    
    Args:
        storage: MemoryStorage instance
        category_importance: Dictionary mapping categories to importance settings
        memory_id: The ID of the memory to retrieve
        
    Returns:
        Memory data dictionary if found, None otherwise
    """
    try:
        # Parse category from memory ID
        if "-" not in memory_id:
            logger.warning(f"Invalid memory ID format: {memory_id}")
            return None
            
        category = memory_id.split("-")[0]
        
        if category not in category_importance:
            logger.warning(f"Invalid category in memory ID: {memory_id}")
            return None
            
        # Load memory
        return await storage.load_memory(memory_id, category)
    except Exception as e:
        logger.error(f"Error retrieving memory {memory_id}: {e}")
        return None

async def get_memories_by_category(self, category, limit=10) -> List[Dict[str, Any]]:
    """
    Get memories by category (compatibility method for Agenteer).
    
    Args:
        self: StructuredMemory instance
        category: The category to retrieve memories from
        limit: Maximum number of memories to retrieve
        
    Returns:
        List of memory objects
    """
    try:
        # Delegate to search_memories with the category filter
        return await self.search_memories(categories=[category], limit=limit)
    except Exception as e:
        logger.error(f"Error retrieving memories by category: {e}")
        return []

async def get_memory_digest(self, category_importance, categories=None,
                          max_memories=10, include_private=False) -> str:
    """
    Generate a formatted digest of important memories for session start.
    
    Args:
        self: StructuredMemory instance
        category_importance: Dictionary mapping categories to importance settings
        categories: List of categories to include (defaults to all except private)
        max_memories: Maximum memories to include in digest
        include_private: Whether to include private memories
        
    Returns:
        Formatted text digest of important memories
    """
    try:
        # Default to all categories except private
        if categories is None:
            categories = [c for c in category_importance.keys() 
                        if c != "private" or include_private]
            
        digest_parts = ["# Memory Digest\n\n"]
        
        # Get most important memories from each category
        for category in categories:
            category_memories = await self.search_memories(
                categories=[category],
                min_importance=3,  # Only include moderately+ important memories
                limit=max_memories // len(categories) + 1,  # Distribute limit across categories
                sort_by="importance"
            )
            
            if category_memories:
                digest_parts.append(f"## {category.capitalize()}\n")
                
                # Format memories for this category
                formatted_memories = format_memory_digest(category_memories)
                digest_parts.extend(formatted_memories)
                digest_parts.append("\n")
                
        return "".join(digest_parts)
    except Exception as e:
        logger.error(f"Error generating memory digest: {e}")
        return "# Memory Digest\n\nUnable to generate memory digest due to an error."

async def get_memory_by_content(self, category_importance, content, category=None) -> Optional[Dict[str, Any]]:
    """
    Find a memory by its content.
    
    Args:
        self: StructuredMemory instance
        category_importance: Dictionary mapping categories to importance settings
        content: The exact content to search for
        category: Optional category to limit the search
        
    Returns:
        Memory data if found, None otherwise
    """
    try:
        categories_to_search = [category] if category else category_importance.keys()
        
        for cat in categories_to_search:
            if cat not in category_importance:
                continue
                
            # Search through the metadata index for this category
            for memory_id in self.metadata_index["categories"][cat]["memories"]:
                memory = await self.get_memory(memory_id)
                
                if memory and memory["content"] == content:
                    return memory
                    
        return None
    except Exception as e:
        logger.error(f"Error finding memory by content: {e}")
        return None

async def get_memories_by_tag(storage, metadata_index, tag, max_memories=10) -> List[Dict[str, Any]]:
    """
    Get memories with a specific tag.
    
    Args:
        storage: MemoryStorage instance
        metadata_index: Current metadata index dictionary
        tag: The tag to search for
        max_memories: Maximum number of memories to return
        
    Returns:
        List of memory dictionaries with the specified tag
    """
    return await search_by_tags(
        storage=storage,
        metadata_index=metadata_index,
        tags=[tag],
        limit=max_memories
    )

async def get_context_memories(storage, metadata_index, text, max_memories=5) -> List[Dict[str, Any]]:
    """
    Get memories relevant to the given context text.
    
    Args:
        storage: MemoryStorage instance
        metadata_index: Current metadata index dictionary
        text: The context text to find relevant memories for
        max_memories: Maximum number of memories to return
        
    Returns:
        List of relevant memory dictionaries
    """
    return await search_context_memories(
        storage=storage,
        metadata_index=metadata_index,
        text=text,
        limit=max_memories
    )

async def get_semantic_memories(storage, metadata_index, query, max_memories=10) -> List[Dict[str, Any]]:
    """
    Get semantically similar memories using vector search if available,
    falling back to keyword search if vector search is not available.
    
    Args:
        storage: MemoryStorage instance
        metadata_index: Current metadata index dictionary
        query: The semantic query to search for
        max_memories: Maximum number of memories to return
        
    Returns:
        List of semantically relevant memory dictionaries
    """
    return await search_semantic_memories(
        storage=storage,
        metadata_index=metadata_index,
        query=query,
        limit=max_memories
    )