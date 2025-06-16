#!/usr/bin/env python3
"""
Metadata Index Management

Provides functions for managing the memory metadata index.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("engram.structured.memory.index")

def load_metadata_index(metadata_index_file: Path, client_id: str) -> Dict[str, Any]:
    """
    Load the metadata index from file or initialize if it doesn't exist.
    
    Args:
        metadata_index_file: Path to the metadata index file
        client_id: Client identifier for the index
        
    Returns:
        Metadata index dictionary
    """
    if metadata_index_file.exists():
        try:
            with open(metadata_index_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata index: {e}")
            return initialize_metadata_index(metadata_index_file, client_id)
    else:
        return initialize_metadata_index(metadata_index_file, client_id)
        
def initialize_metadata_index(metadata_index_file: Path, client_id: str) -> Dict[str, Any]:
    """
    Initialize a new metadata index.
    
    Args:
        metadata_index_file: Path to the metadata index file
        client_id: Client identifier for the index
        
    Returns:
        New metadata index dictionary
    """
    from engram.core.structured.constants import DEFAULT_MEMORY_CATEGORIES
    
    index = {
        "client_id": client_id,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "categories": {},
        "memory_count": 0,
        "importance_counters": {str(i): 0 for i in range(1, 6)},
        "tags": {},
    }
    
    # Initialize category sub-indices
    for category in DEFAULT_MEMORY_CATEGORIES:
        index["categories"][category] = {
            "memory_count": 0,
            "last_updated": datetime.now().isoformat(),
            "memories": {}  # Will contain memory_id -> metadata mappings
        }
        
    # Save the initial index
    save_metadata_index(metadata_index_file, index)
    return index
    
def save_metadata_index(metadata_index_file: Path, index: Dict[str, Any]) -> bool:
    """
    Save the metadata index to file.
    
    Args:
        metadata_index_file: Path to the metadata index file
        index: Metadata index dictionary to save
        
    Returns:
        Boolean indicating success
    """
    try:
        # Update the last_updated timestamp
        index["last_updated"] = datetime.now().isoformat()
        
        with open(metadata_index_file, "w") as f:
            json.dump(index, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving metadata index: {e}")
        return False
        
def update_memory_in_index(index: Dict[str, Any], memory_id: str, 
                             category: str, importance: int, 
                             tags: list, timestamp: str) -> None:
    """
    Update or add a memory in the metadata index.
    
    Args:
        index: Metadata index dictionary
        memory_id: ID of the memory to update/add
        category: Category of the memory
        importance: Importance level of the memory
        tags: Tags associated with the memory
        timestamp: ISO format timestamp
    """
    # Update global counters
    index["memory_count"] += 1
    index["importance_counters"][str(importance)] += 1
    
    # Update category metrics
    index["categories"][category]["memory_count"] += 1
    index["categories"][category]["last_updated"] = datetime.now().isoformat()
    
    # Add/update memory in category index
    index["categories"][category]["memories"][memory_id] = {
        "importance": importance,
        "timestamp": timestamp,
        "tags": tags
    }
    
    # Update tag index
    for tag in tags:
        if tag not in index["tags"]:
            index["tags"][tag] = []
        if memory_id not in index["tags"][tag]:
            index["tags"][tag].append(memory_id)
            
def update_memory_importance(index: Dict[str, Any], memory_id: str,
                                category: str, original_importance: int,
                                new_importance: int) -> None:
    """
    Update the importance level of a memory in the index.
    
    Args:
        index: Metadata index dictionary
        memory_id: ID of the memory to update
        category: Category of the memory
        original_importance: Original importance level
        new_importance: New importance level
    """
    # Update importance counters
    index["importance_counters"][str(original_importance)] -= 1
    index["importance_counters"][str(new_importance)] += 1
    
    # Update memory metadata
    index["categories"][category]["memories"][memory_id]["importance"] = new_importance
    index["categories"][category]["last_updated"] = datetime.now().isoformat()
    
def remove_memory_from_index(index: Dict[str, Any], memory_id: str,
                               category: str, importance: int,
                               tags: list) -> None:
    """
    Remove a memory from the metadata index.
    
    Args:
        index: Metadata index dictionary
        memory_id: ID of the memory to remove
        category: Category of the memory
        importance: Importance level of the memory
        tags: Tags associated with the memory
    """
    # Update global counters
    index["memory_count"] -= 1
    index["importance_counters"][str(importance)] -= 1
    
    # Update category metrics
    if memory_id in index["categories"][category]["memories"]:
        index["categories"][category]["memory_count"] -= 1
        del index["categories"][category]["memories"][memory_id]
    
    # Remove from tag indices
    for tag in tags:
        if tag in index["tags"] and memory_id in index["tags"][tag]:
            index["tags"][tag].remove(memory_id)
            
            # Clean up empty tag entries
            if not index["tags"][tag]:
                del index["tags"][tag]