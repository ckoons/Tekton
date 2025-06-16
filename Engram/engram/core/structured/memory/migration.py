#!/usr/bin/env python3
"""
Memory Service Migration

Provides functionality to migrate from the legacy MemoryService to StructuredMemory.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

from engram.core.structured.constants import (
    NAMESPACE_TO_CATEGORY_MAP,
    NAMESPACE_IMPORTANCE_MAP
)

logger = logging.getLogger("engram.structured.memory.migration")

async def migrate_from_memory_service(self, memory_service, limit: int = 1000) -> int:
    """
    Migrate memories from the old MemoryService to StructuredMemory.
    
    Args:
        self: StructuredMemory instance
        memory_service: Instance of the old MemoryService
        limit: Maximum number of memories to migrate
        
    Returns:
        Number of memories migrated
    """
    migrated_count = 0
    
    try:
        # Get available namespaces
        namespaces = await memory_service.get_namespaces()
        
        for namespace in namespaces:
            # Map to new category
            if namespace.startswith("compartment-"):
                category = "projects"
            else:
                category = NAMESPACE_TO_CATEGORY_MAP.get(namespace, "session")
            
            # Set default importance based on namespace
            default_importance = NAMESPACE_IMPORTANCE_MAP.get(namespace, 3)
            
            # Search all memories in this namespace
            results = await memory_service.search(
                query="",
                namespace=namespace,
                limit=limit
            )
            
            # Migrate each memory
            for memory in results.get("results", []):
                content = memory.get("content", "")
                metadata = memory.get("metadata", {})
                
                # Generate tags based on namespace
                tags = [namespace]
                
                # Add compartment name as a tag if available
                if namespace.startswith("compartment-"):
                    compartment_id = namespace[len("compartment-"):]
                    tags.append(f"compartment:{compartment_id}")
                
                # Add the memory to structured storage
                memory_id = await self.add_memory(
                    content=content,
                    category=category,
                    importance=default_importance,
                    metadata={
                        "migrated_from": namespace,
                        "original_timestamp": metadata.get("timestamp"),
                        **metadata
                    },
                    tags=tags
                )
                
                if memory_id:
                    migrated_count += 1
                
                # Break if we've reached the limit
                if migrated_count >= limit:
                    break
            
            # Break if we've reached the limit
            if migrated_count >= limit:
                break
        
        logger.info(f"Migrated {migrated_count} memories from MemoryService to StructuredMemory")
        return migrated_count
    except Exception as e:
        logger.error(f"Error migrating memories: {e}")
        return migrated_count