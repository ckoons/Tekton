#!/usr/bin/env python3
"""
Memory Addition Operations

Provides functions for adding new memories to the structured memory system.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from engram.core.structured.utils import generate_memory_id
from engram.core.structured.memory.index import update_memory_in_index, save_metadata_index
from engram.core.structured.categorization.auto import auto_categorize_memory

logger = logging.getLogger("engram.structured.operations.add")

async def add_memory(storage, metadata_index, metadata_index_file, client_id, 
                  category_importance, content, category="session",
                  importance=None, metadata=None, tags=None) -> Optional[str]:
    """
    Add a new memory with structured metadata and importance ranking.
    
    Args:
        storage: MemoryStorage instance
        metadata_index: Current metadata index dictionary
        metadata_index_file: Path to metadata index file
        client_id: Client identifier
        category_importance: Dictionary mapping categories to importance settings
        content: The memory content to store
        category: The category to store in (personal, projects, facts, etc.)
        importance: Importance ranking 1-5 (5 being most important)
        metadata: Additional metadata for the memory
        tags: Tags for easier searching and categorization
        
    Returns:
        Memory ID if successful, None otherwise
    """
    # Validate category
    if category not in category_importance:
        logger.warning(f"Invalid category: {category}, using 'session'")
        category = "session"
        
    # Set default importance from category if not provided
    if importance is None:
        importance = category_importance[category]["default_importance"]
    else:
        # Ensure importance is in valid range
        importance = max(1, min(5, importance))
        
    # Initialize metadata if not provided
    if metadata is None:
        metadata = {}
        
    # Initialize tags if not provided
    if tags is None:
        tags = []
        
    try:
        # Generate memory ID
        memory_id = generate_memory_id(category, content)
        
        # Prepare memory data
        memory_data = {
            "id": memory_id,
            "content": content,
            "category": category,
            "importance": importance,
            "metadata": {
                **metadata,
                "timestamp": datetime.now().isoformat(),
                "client_id": client_id,
                "importance_reason": metadata.get("importance_reason", "Default category importance")
            },
            "tags": tags
        }
        
        # Store memory
        if not await storage.store_memory(memory_data):
            logger.error(f"Failed to store memory {memory_id}")
            return None
            
        # Update metadata index
        update_memory_in_index(
            index=metadata_index,
            memory_id=memory_id,
            category=category,
            importance=importance,
            tags=tags,
            timestamp=memory_data["metadata"]["timestamp"]
        )
        
        # Save updated index
        save_metadata_index(metadata_index_file, metadata_index)
        
        logger.info(f"Added memory {memory_id} to {category} with importance {importance}")
        return memory_id
    except Exception as e:
        logger.error(f"Error adding memory: {e}")
        return None
        
async def add_auto_categorized_memory(self, content, manual_category=None,
                                     manual_importance=None, manual_tags=None,
                                     metadata=None) -> Optional[str]:
    """
    Add a memory with automatic categorization, allowing manual overrides.
    
    Args:
        self: StructuredMemory instance
        content: The memory content to store
        manual_category: Override the automatic category (optional)
        manual_importance: Override the automatic importance (optional)
        manual_tags: Additional tags to add (optional)
        metadata: Additional metadata for the memory
        
    Returns:
        Memory ID if successful, None otherwise
    """
    try:
        # Auto-categorize unless overridden
        if manual_category is None or manual_importance is None:
            auto_category, auto_importance, auto_tags = await auto_categorize_memory(content)
            
            # Use auto values as defaults
            category = manual_category or auto_category
            importance = manual_importance or auto_importance
            
            # Combine auto and manual tags without duplicates
            tags = list(set(auto_tags + (manual_tags or [])))
            
            # Add categorization info to metadata
            if metadata is None:
                metadata = {}
            
            metadata["auto_categorized"] = (manual_category is None)
            metadata["auto_importance"] = auto_importance
            metadata["importance_reason"] = "Auto-categorized based on content analysis"
            
            if manual_importance is not None:
                metadata["importance_reason"] = "Manually set importance level"
        else:
            # Use manual values
            category = manual_category
            importance = manual_importance
            tags = manual_tags or []
            
            if metadata is None:
                metadata = {}
            
            metadata["auto_categorized"] = False
            metadata["importance_reason"] = "Manually categorized"
            
        # Add the memory with the determined category and importance
        return await self.add_memory(
            content=content,
            category=category,
            importance=importance,
            metadata=metadata,
            tags=tags
        )
    except Exception as e:
        logger.error(f"Error adding auto-categorized memory: {e}")
        return None