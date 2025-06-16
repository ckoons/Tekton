#!/usr/bin/env python3
"""
Memory Update Operations

Provides functions for updating existing memories in the structured memory system.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union

from engram.core.structured.memory.index import save_metadata_index, update_memory_importance

logger = logging.getLogger("engram.structured.operations.update")

async def set_memory_importance(self, storage, metadata_index, metadata_index_file, 
                             memory_id, importance) -> bool:
    """
    Update the importance of an existing memory.
    
    Args:
        self: StructuredMemory instance
        storage: MemoryStorage instance
        metadata_index: Current metadata index dictionary
        metadata_index_file: Path to metadata index file
        memory_id: The ID of the memory to update
        importance: New importance level (1-5)
        
    Returns:
        Boolean indicating success
    """
    try:
        # Ensure importance is in valid range
        importance = max(1, min(5, importance))
        
        # Get the memory
        memory = await self.get_memory(memory_id)
        if not memory:
            logger.warning(f"Memory not found: {memory_id}")
            return False
            
        # Get original importance for index updating
        original_importance = memory["importance"]
        
        # Update the memory
        memory["importance"] = importance
        memory["metadata"]["importance_updated"] = datetime.now().isoformat()
        memory["metadata"]["importance_reason"] = "Manually updated importance"
        
        # Save updated memory
        category = memory["category"]
        if not await storage.store_memory(memory):
            logger.error(f"Failed to update memory {memory_id}")
            return False
            
        # Update metadata index
        update_memory_importance(
            index=metadata_index,
            memory_id=memory_id,
            category=category,
            original_importance=original_importance,
            new_importance=importance
        )
        save_metadata_index(metadata_index_file, metadata_index)
        
        return True
    except Exception as e:
        logger.error(f"Error updating memory importance: {e}")
        return False