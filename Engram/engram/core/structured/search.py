#!/usr/bin/env python3
"""
Structured Memory Search

Provides search functionality for structured memories.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

from engram.core.structured.utils import extract_keywords

logger = logging.getLogger("engram.structured.search")

async def search_by_content(
    storage, 
    metadata_index: Dict[str, Any],
    query: str,
    categories: List[str] = None,
    min_importance: int = 1,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search memories by content.
    
    Args:
        storage: Memory storage instance
        metadata_index: Memory metadata index
        query: Search query string
        categories: List of categories to search in
        min_importance: Minimum importance level (1-5)
        limit: Maximum number of results
        
    Returns:
        List of matching memory dictionaries
    """
    try:
        results = []
        
        # Default to all categories if not specified
        if categories is None:
            categories = list(metadata_index["categories"].keys())
        
        # Get candidate memories matching importance criteria
        candidates = []
        for category in categories:
            if category not in metadata_index["categories"]:
                continue
                
            # Get memories in this category meeting importance threshold
            for memory_id, memory_meta in metadata_index["categories"][category]["memories"].items():
                if memory_meta["importance"] >= min_importance:
                    candidates.append((memory_id, category))
        
        # Check content of each candidate
        for memory_id, category in candidates:
            memory = await storage.load_memory(memory_id, category)
            
            if memory and query.lower() in memory["content"].lower():
                # Add a relevance score based on query occurrence count
                count = memory["content"].lower().count(query.lower())
                memory["relevance"] = count * memory["importance"]
                results.append(memory)
                
        # Sort by relevance score
        results.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        
        # Limit results
        return results[:limit]
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        return []

async def search_by_tags(
    storage,
    metadata_index: Dict[str, Any],
    tags: List[str],
    min_importance: int = 1,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search memories by tags.
    
    Args:
        storage: Memory storage instance
        metadata_index: Memory metadata index
        tags: List of tags to search for
        min_importance: Minimum importance level (1-5)
        limit: Maximum number of results
        
    Returns:
        List of matching memory dictionaries
    """
    try:
        results = []
        
        # Get memory IDs for each tag
        tag_matches = {}
        for tag in tags:
            if tag in metadata_index["tags"]:
                for memory_id in metadata_index["tags"][tag]:
                    tag_matches[memory_id] = tag_matches.get(memory_id, 0) + 1
        
        # Load memories and check importance
        for memory_id, tag_count in tag_matches.items():
            # Extract category from memory ID
            if "-" not in memory_id:
                continue
                
            category = memory_id.split("-")[0]
            
            # Check if memory exists in the index
            if (category in metadata_index["categories"] and 
                memory_id in metadata_index["categories"][category]["memories"]):
                
                # Check importance threshold
                memory_meta = metadata_index["categories"][category]["memories"][memory_id]
                if memory_meta["importance"] >= min_importance:
                    # Load full memory
                    memory = await storage.load_memory(memory_id, category)
                    
                    if memory:
                        # Add tag match count as a relevance factor
                        memory["tag_matches"] = tag_count
                        results.append(memory)
        
        # Sort by tag matches (more matches first) then by importance
        results.sort(key=lambda x: (x.get("tag_matches", 0), x["importance"]), reverse=True)
        
        # Limit results
        return results[:limit]
    except Exception as e:
        logger.error(f"Error searching by tags: {e}")
        return []

async def search_context_memories(
    storage,
    metadata_index: Dict[str, Any],
    text: str,
    min_importance: int = 3,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Find memories relevant to the given context text.
    
    Args:
        storage: Memory storage instance
        metadata_index: Memory metadata index
        text: Context text to find relevant memories for
        min_importance: Minimum importance level (1-5)
        limit: Maximum number of results
        
    Returns:
        List of relevant memory dictionaries
    """
    try:
        # Extract keywords from text
        keywords = extract_keywords(text)
        
        if not keywords:
            return []
            
        # Search for each keyword
        all_results = []
        
        for keyword in keywords:
            # Search by content
            content_results = await search_by_content(
                storage=storage,
                metadata_index=metadata_index,
                query=keyword,
                min_importance=min_importance,
                limit=limit
            )
            all_results.extend(content_results)
            
        # Deduplicate by memory ID
        unique_results = {}
        for memory in all_results:
            memory_id = memory["id"]
            if memory_id not in unique_results:
                unique_results[memory_id] = memory
                
        # Sort by importance (highest first)
        sorted_results = sorted(
            unique_results.values(),
            key=lambda x: x["importance"],
            reverse=True
        )
        
        return sorted_results[:limit]
    except Exception as e:
        logger.error(f"Error finding context memories: {e}")
        return []

async def search_semantic_memories(
    storage,
    metadata_index: Dict[str, Any],
    query: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for semantically relevant memories.
    
    Args:
        storage: Memory storage instance
        metadata_index: Memory metadata index
        query: Semantic query
        limit: Maximum number of results
        
    Returns:
        List of semantically relevant memories
    """
    try:
        # Try to access vector-based memory service for semantic search
        try:
            from engram.core.memory import MemoryService, HAS_VECTOR_DB
            
            # Check if vector search is available
            if HAS_VECTOR_DB:
                # Initialize memory service
                memory_service = MemoryService(client_id=storage.client_id)
                
                # Use vector search across namespaces
                results = []
                namespaces = ["conversations", "thinking", "longterm", "projects", "session"]
                
                for namespace in namespaces:
                    # Use vector search
                    search_results = await memory_service.search(
                        query=query,
                        namespace=namespace,
                        limit=limit // len(namespaces) + 1
                    )
                    
                    # Format results to match structured memory format
                    for result in search_results.get("results", []):
                        memory_obj = {
                            "id": result.get("id", ""),
                            "content": result.get("content", ""),
                            "category": namespace,  # Map namespace to category
                            "importance": 4,  # Default importance
                            "metadata": result.get("metadata", {}),
                            "tags": ["semantic_search"],
                            "relevance": result.get("relevance", 0.0)
                        }
                        results.append(memory_obj)
                
                # Sort by relevance
                results.sort(key=lambda x: x.get("relevance", 0.0), reverse=True)
                
                # Return results if found
                if results:
                    return results[:limit]
        except Exception as vector_err:
            logger.debug(f"Vector search unavailable: {vector_err}")
        
        # Fallback to keyword search
        logger.info("Using keyword search fallback for semantic query")
        
        # Extract keywords from query
        keywords = extract_keywords(query)
        
        # Combine results from all keywords
        all_results = []
        for keyword in keywords:
            results = await search_by_content(
                storage=storage,
                metadata_index=metadata_index,
                query=keyword,
                limit=limit // len(keywords) if keywords else limit
            )
            all_results.extend(results)
            
        # Deduplicate and sort
        unique_results = {}
        for memory in all_results:
            if memory["id"] not in unique_results:
                unique_results[memory["id"]] = memory
                
        sorted_results = sorted(
            unique_results.values(),
            key=lambda x: x.get("relevance", 0),
            reverse=True
        )
        
        return sorted_results[:limit]
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return []