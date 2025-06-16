#!/usr/bin/env python3
"""
Context-based Memory Search

Provides functions for finding memories relevant to a given context.
"""

import logging
from typing import Dict, List, Any, Optional

from engram.core.structured.utils import extract_keywords
from engram.core.structured.search.content import search_by_content

logger = logging.getLogger("engram.structured.search.context")

async def search_context_memories(storage, metadata_index, text, limit=5) -> List[Dict[str, Any]]:
    """
    Find memories relevant to the provided context text.
    
    Args:
        storage: MemoryStorage instance
        metadata_index: Current metadata index dictionary
        text: Context text to find relevant memories for
        limit: Maximum number of memories to return
        
    Returns:
        List of context-relevant memory dictionaries
    """
    try:
        # Extract keywords for context matching
        keywords = extract_keywords(text, min_length=4, max_keywords=10)
        
        if not keywords:
            logger.info(f"No significant keywords found in context text")
            return []
            
        # Create a search query from the top keywords
        context_query = " ".join(keywords)
        
        # Use content search with the context keywords
        # Focus on more important memories for context
        return await search_by_content(
            storage=storage,
            metadata_index=metadata_index,
            query=context_query,
            min_importance=2,  # Only moderately+ important memories for context
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error in context memory search: {e}")
        return []