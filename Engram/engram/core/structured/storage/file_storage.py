#!/usr/bin/env python3
"""
Structured Memory Storage

Provides the MemoryStorage class for file-based memory operations.
"""

import logging
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from engram.core.structured.utils import load_json_file, save_json_file

logger = logging.getLogger("engram.structured.storage")

class MemoryStorage:
    """
    File-based storage for structured memories with caching.
    """
    
    def __init__(self, client_id: str, base_dir: Path):
        """
        Initialize memory storage.
        
        Args:
            client_id: Unique identifier for the client
            base_dir: Base directory for memory storage
        """
        self.client_id = client_id
        self.base_dir = base_dir
        self.memory_dirs = {}
        
        # Set up category directories
        for category_dir in base_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                self.memory_dirs[category_dir.name] = category_dir
                
                # Ensure client dir exists
                client_dir = category_dir / client_id
                client_dir.mkdir(exist_ok=True)
        
        # Memory cache to avoid repeated disk reads
        self.memory_cache = {}
        self.cache_size_limit = 1000  # Maximum number of memories to cache
        
    async def store_memory(self, memory_data: Dict[str, Any]) -> bool:
        """
        Store a memory to the filesystem.
        
        Args:
            memory_data: Memory data to store
            
        Returns:
            Boolean indicating success
        """
        try:
            memory_id = memory_data["id"]
            category = memory_data["category"]
            
            if category not in self.memory_dirs:
                logger.warning(f"Invalid category '{category}' for memory {memory_id}")
                return False
                
            # Construct file path
            memory_file = self.memory_dirs[category] / self.client_id / f"{memory_id}.json"
            
            # Save to filesystem
            if save_json_file(memory_file, memory_data):
                # Update cache
                self.memory_cache[memory_id] = memory_data
                
                # Trim cache if needed
                self._trim_cache()
                
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return False
            
    async def load_memory(self, memory_id: str, category: str) -> Optional[Dict[str, Any]]:
        """
        Load a memory from cache or filesystem.
        
        Args:
            memory_id: ID of the memory to load
            category: Category of the memory
            
        Returns:
            Memory data if found, None otherwise
        """
        try:
            # Check cache first
            if memory_id in self.memory_cache:
                return self.memory_cache[memory_id]
                
            # Construct file path
            if category not in self.memory_dirs:
                logger.warning(f"Invalid category '{category}' for memory {memory_id}")
                return None
                
            memory_file = self.memory_dirs[category] / self.client_id / f"{memory_id}.json"
            
            # Load from filesystem
            memory_data = load_json_file(memory_file)
            
            if memory_data:
                # Update cache
                self.memory_cache[memory_id] = memory_data
                
                # Trim cache if needed
                self._trim_cache()
                
            return memory_data
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
            return None
            
    async def delete_memory(self, memory_id: str, category: str) -> bool:
        """
        Delete a memory from filesystem and cache.
        
        Args:
            memory_id: ID of the memory to delete
            category: Category of the memory
            
        Returns:
            Boolean indicating success
        """
        try:
            # Construct file path
            if category not in self.memory_dirs:
                logger.warning(f"Invalid category '{category}' for memory {memory_id}")
                return False
                
            memory_file = self.memory_dirs[category] / self.client_id / f"{memory_id}.json"
            
            # Remove from cache
            if memory_id in self.memory_cache:
                del self.memory_cache[memory_id]
                
            # Delete file if it exists
            if memory_file.exists():
                memory_file.unlink()
                return True
            else:
                logger.warning(f"Memory file not found: {memory_file}")
                return False
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return False
            
    def _trim_cache(self) -> None:
        """
        Trim the memory cache if it exceeds the size limit.
        """
        if len(self.memory_cache) > self.cache_size_limit:
            # Simple strategy: remove oldest cached entries
            excess = len(self.memory_cache) - self.cache_size_limit
            
            # Sort by timestamp (oldest first)
            sorted_ids = sorted(
                self.memory_cache.keys(),
                key=lambda x: self.memory_cache[x].get("metadata", {}).get("timestamp", "")
            )
            
            # Remove oldest entries
            for memory_id in sorted_ids[:excess]:
                del self.memory_cache[memory_id]