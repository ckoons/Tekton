#!/usr/bin/env python3
"""
Structured Memory Storage

Handles file-based storage operations for structured memory.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from engram.core.structured.utils import (
    generate_memory_id,
    load_json_file,
    save_json_file
)

logger = logging.getLogger("engram.structured.storage")

class MemoryStorage:
    """Handles storage operations for structured memory."""
    
    def __init__(self, client_id: str, base_dir: Path):
        """
        Initialize memory storage.
        
        Args:
            client_id: Unique identifier for the client
            base_dir: Base directory for memory storage
        """
        self.client_id = client_id
        self.base_dir = base_dir
        
        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory cache for quick access
        self.memory_cache = {}
        
    def get_memory_path(self, memory_id: str, category: str) -> Path:
        """
        Get the file path for a specific memory.
        
        Args:
            memory_id: Memory ID
            category: Memory category
            
        Returns:
            Path to the memory file
        """
        return self.base_dir / category / self.client_id / f"{memory_id}.json"
        
    async def store_memory(self, memory_data: Dict[str, Any]) -> bool:
        """
        Store a memory to file.
        
        Args:
            memory_data: Memory data dictionary
            
        Returns:
            Boolean indicating success
        """
        try:
            memory_id = memory_data["id"]
            category = memory_data["category"]
            
            # Get memory file path
            memory_path = self.get_memory_path(memory_id, category)
            
            # Save memory to file
            with open(memory_path, "w") as f:
                json.dump(memory_data, f, indent=2)
                
            # Update cache
            self.memory_cache[memory_id] = memory_data
            
            return True
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return False
            
    async def load_memory(self, memory_id: str, category: str) -> Optional[Dict[str, Any]]:
        """
        Load a memory from file.
        
        Args:
            memory_id: Memory ID
            category: Memory category
            
        Returns:
            Memory data dictionary or None if not found
        """
        try:
            # Check cache first
            if memory_id in self.memory_cache:
                return self.memory_cache[memory_id]
                
            # Get memory file path
            memory_path = self.get_memory_path(memory_id, category)
            
            if not memory_path.exists():
                logger.debug(f"Memory file not found: {memory_path}")
                return None
                
            # Load memory from file
            with open(memory_path, "r") as f:
                memory_data = json.load(f)
                
            # Cache for future retrievals
            self.memory_cache[memory_id] = memory_data
            
            return memory_data
        except Exception as e:
            logger.error(f"Error loading memory {memory_id}: {e}")
            return None
            
    async def delete_memory(self, memory_id: str, category: str) -> bool:
        """
        Delete a memory file.
        
        Args:
            memory_id: Memory ID
            category: Memory category
            
        Returns:
            Boolean indicating success
        """
        try:
            # Get memory file path
            memory_path = self.get_memory_path(memory_id, category)
            
            if not memory_path.exists():
                logger.warning(f"Memory file not found: {memory_path}")
                return False
                
            # Remove the file
            os.remove(memory_path)
            
            # Remove from cache
            if memory_id in self.memory_cache:
                del self.memory_cache[memory_id]
                
            return True
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return False