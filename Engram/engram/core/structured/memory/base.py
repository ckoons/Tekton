#!/usr/bin/env python3
"""
Structured Memory Base

Provides the main StructuredMemory class for file-based memory management
with organization and importance ranking.
"""

import logging
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from engram.core.structured.constants import (
    DEFAULT_MEMORY_CATEGORIES,
    DEFAULT_CATEGORY_IMPORTANCE,
    IMPORTANCE_LEVELS
)
from engram.core.structured.memory.index import (
    load_metadata_index,
    initialize_metadata_index,
    save_metadata_index
)
from engram.core.structured.storage.file_storage import MemoryStorage
from engram.core.structured.operations.add import add_memory, add_auto_categorized_memory
from engram.core.structured.operations.retrieve import (
    get_memory,
    get_memories_by_category,
    get_memory_digest,
    get_memory_by_content,
    get_memories_by_tag,
    get_context_memories,
    get_semantic_memories
)
from engram.core.structured.operations.update import set_memory_importance
from engram.core.structured.operations.delete import delete_memory
from engram.core.structured.operations.search import search_memories
from engram.core.structured.memory.migration import migrate_from_memory_service

logger = logging.getLogger("engram.structured.base")

class StructuredMemory:
    """
    Structured memory service with file-based organization and importance ranking.
    
    Key features:
    - Organized, searchable memory files by category/project
    - Standardized formats (JSON) for easier parsing
    - Metadata with timestamps, context, and importance
    - Memory importance ranking (1-5 scale)
    - Context-aware memory loading
    """
    
    def __init__(self, client_id: str = "default", data_dir: Optional[str] = None):
        """
        Initialize the structured memory service.
        
        Args:
            client_id: Unique identifier for the client (default: "default")
            data_dir: Directory to store memory data (default: ~/.engram/structured)
        """
        self.client_id = client_id
        
        # Set up base data directory
        if data_dir:
            self.base_dir = Path(data_dir) / "structured"
        else:
            self.base_dir = Path(os.path.expanduser("~/.engram/structured"))
        
        # Create structured directory layout
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Key directories for different memory categories
        self.memory_dirs = {}
        for category in DEFAULT_MEMORY_CATEGORIES:
            self.memory_dirs[category] = self.base_dir / category
            
        # Create all memory category directories
        for dir_path in self.memory_dirs.values():
            dir_path.mkdir(exist_ok=True)
            
        # Create clients directory within each category
        for dir_path in self.memory_dirs.values():
            client_dir = dir_path / client_id
            client_dir.mkdir(exist_ok=True)
            
        # Import category importance and descriptions
        self.category_importance = DEFAULT_CATEGORY_IMPORTANCE
        
        # Import importance level descriptions
        self.importance_levels = IMPORTANCE_LEVELS
        
        # Initialize storage
        self.storage = MemoryStorage(client_id, self.base_dir)
        
        # Initialize metadata index
        self.metadata_index_file = self.base_dir / f"{client_id}_metadata_index.json"
        self.metadata_index = load_metadata_index(self.metadata_index_file, client_id)
    
    # Delegate methods to the appropriate modules
    async def add_memory(self, content: str, category: str = "session",
                      importance: int = None, metadata: Optional[Dict[str, Any]] = None,
                      tags: Optional[List[str]] = None) -> Optional[str]:
        """
        Add a new memory with structured metadata and importance ranking.
        
        Args:
            content: The memory content to store
            category: The category to store in (personal, projects, facts, etc.)
            importance: Importance ranking 1-5 (5 being most important)
            metadata: Additional metadata for the memory
            tags: Tags for easier searching and categorization
            
        Returns:
            Memory ID if successful, None otherwise
        """
        return await add_memory(
            storage=self.storage,
            metadata_index=self.metadata_index,
            metadata_index_file=self.metadata_index_file,
            client_id=self.client_id,
            category_importance=self.category_importance,
            content=content,
            category=category,
            importance=importance,
            metadata=metadata,
            tags=tags
        )
    
    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: The ID of the memory to retrieve
            
        Returns:
            Memory data dictionary if found, None otherwise
        """
        return await get_memory(
            storage=self.storage,
            category_importance=self.category_importance,
            memory_id=memory_id
        )
    
    async def get_memories_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get memories by category (compatibility method for Agenteer).
        
        Args:
            category: The category to retrieve memories from
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of memory objects
        """
        return await get_memories_by_category(
            self=self,
            category=category,
            limit=limit
        )
    
    async def search_memories(self, query: str = None, categories: List[str] = None,
                          tags: List[str] = None, min_importance: int = 1,
                          limit: int = 10, sort_by: str = "importance") -> List[Dict[str, Any]]:
        """
        Search for memories based on multiple criteria.
        
        Args:
            query: Text to search for in memory content (optional)
            categories: List of categories to search in (defaults to all)
            tags: List of tags to filter by (optional)
            min_importance: Minimum importance level (1-5)
            limit: Maximum number of results to return
            sort_by: How to sort results ("importance", "recency", or "relevance")
            
        Returns:
            List of matching memory data dictionaries
        """
        return await search_memories(
            self=self,
            storage=self.storage,
            metadata_index=self.metadata_index,
            category_importance=self.category_importance,
            query=query,
            categories=categories,
            tags=tags,
            min_importance=min_importance,
            limit=limit,
            sort_by=sort_by
        )
    
    async def get_memory_digest(self, categories: List[str] = None,
                            max_memories: int = 10,
                            include_private: bool = False) -> str:
        """
        Generate a formatted digest of important memories for session start.
        
        Args:
            categories: List of categories to include (defaults to all except private)
            max_memories: Maximum memories to include in digest
            include_private: Whether to include private memories
            
        Returns:
            Formatted text digest of important memories
        """
        return await get_memory_digest(
            self=self,
            category_importance=self.category_importance,
            categories=categories,
            max_memories=max_memories,
            include_private=include_private
        )
    
    async def add_auto_categorized_memory(self, content: str, 
                                       manual_category: str = None,
                                       manual_importance: int = None,
                                       manual_tags: List[str] = None,
                                       metadata: Dict[str, Any] = None) -> Optional[str]:
        """
        Add a memory with automatic categorization, allowing manual overrides.
        
        Args:
            content: The memory content to store
            manual_category: Override the automatic category (optional)
            manual_importance: Override the automatic importance (optional)
            manual_tags: Additional tags to add (optional)
            metadata: Additional metadata for the memory
            
        Returns:
            Memory ID if successful, None otherwise
        """
        return await add_auto_categorized_memory(
            self=self,
            content=content,
            manual_category=manual_category,
            manual_importance=manual_importance,
            manual_tags=manual_tags,
            metadata=metadata
        )
    
    async def set_memory_importance(self, memory_id: str, importance: int) -> bool:
        """
        Update the importance of an existing memory.
        
        Args:
            memory_id: The ID of the memory to update
            importance: New importance level (1-5)
            
        Returns:
            Boolean indicating success
        """
        return await set_memory_importance(
            self=self,
            storage=self.storage,
            metadata_index=self.metadata_index,
            metadata_index_file=self.metadata_index_file,
            memory_id=memory_id,
            importance=importance
        )
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory from storage.
        
        Args:
            memory_id: The ID of the memory to delete
            
        Returns:
            Boolean indicating success
        """
        return await delete_memory(
            self=self,
            storage=self.storage,
            metadata_index=self.metadata_index,
            metadata_index_file=self.metadata_index_file,
            memory_id=memory_id
        )
    
    async def get_memory_by_content(self, content: str, category: str = None) -> Optional[Dict[str, Any]]:
        """
        Find a memory by its content.
        
        Args:
            content: The exact content to search for
            category: Optional category to limit the search
            
        Returns:
            Memory data if found, None otherwise
        """
        return await get_memory_by_content(
            self=self,
            category_importance=self.category_importance,
            content=content,
            category=category
        )
    
    async def get_memories_by_tag(self, tag: str, max_memories: int = 10) -> List[Dict[str, Any]]:
        """
        Get memories with a specific tag.
        
        Args:
            tag: The tag to search for
            max_memories: Maximum number of memories to return
            
        Returns:
            List of memory dictionaries with the specified tag
        """
        return await get_memories_by_tag(
            storage=self.storage,
            metadata_index=self.metadata_index,
            tag=tag,
            max_memories=max_memories
        )
    
    async def get_context_memories(self, text: str, max_memories: int = 5) -> List[Dict[str, Any]]:
        """
        Get memories relevant to the given context text.
        
        Args:
            text: The context text to find relevant memories for
            max_memories: Maximum number of memories to return
            
        Returns:
            List of relevant memory dictionaries
        """
        return await get_context_memories(
            storage=self.storage,
            metadata_index=self.metadata_index,
            text=text,
            max_memories=max_memories
        )
    
    async def get_semantic_memories(self, query: str, max_memories: int = 10) -> List[Dict[str, Any]]:
        """
        Get semantically similar memories using vector search if available,
        falling back to keyword search if vector search is not available.
        
        Args:
            query: The semantic query to search for
            max_memories: Maximum number of memories to return
            
        Returns:
            List of semantically relevant memory dictionaries
        """
        return await get_semantic_memories(
            storage=self.storage,
            metadata_index=self.metadata_index,
            query=query,
            max_memories=max_memories
        )
    
    async def migrate_from_memory_service(self, memory_service, limit: int = 1000) -> int:
        """
        Migrate memories from the old MemoryService to StructuredMemory.
        
        Args:
            memory_service: Instance of the old MemoryService
            limit: Maximum number of memories to migrate
            
        Returns:
            Number of memories migrated
        """
        return await migrate_from_memory_service(
            self=self,
            memory_service=memory_service,
            limit=limit
        )