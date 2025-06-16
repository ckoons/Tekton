#!/usr/bin/env python3
"""
Memory Deletion Operations

Provides functions for deleting memories from the structured memory system.
"""

import logging
from typing import Dict, Any, Optional, List

from engram.core.structured.memory.index import save_metadata_index, remove_memory_from_index

logger = logging.getLogger("engram.structured.operations.delete")

async def delete_memory(self, storage, metadata_index, metadata_index_file, memory_id) -> bool:
    """
    Delete a memory from storage.
    
    Args:
        self: StructuredMemory instance
        storage: MemoryStorage instance
        metadata_index: Current metadata index dictionary
        metadata_index_file: Path to metadata index file
        memory_id: The ID of the memory to delete
        
    Returns:
        Boolean indicating success
    """
    try:
        # Get the memory to find its category
        memory = await self.get_memory(memory_id)
        if not memory:
            logger.warning(f"Memory not found: {memory_id}")
            return False
            
        category = memory["category"]
        importance = memory["importance"]
        tags = memory.get("tags", [])
        
        # Delete the memory file
        if not await storage.delete_memory(memory_id, category):
            logger.error(f"Failed to delete memory file for {memory_id}")
            return False
            
        # Update the metadata index
        if memory_id in metadata_index["categories"][category]["memories"]:
            remove_memory_from_index(
                index=metadata_index,
                memory_id=memory_id,
                category=category,
                importance=importance,
                tags=tags
            )
            save_metadata_index(metadata_index_file, metadata_index)
            
        return True
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        return False