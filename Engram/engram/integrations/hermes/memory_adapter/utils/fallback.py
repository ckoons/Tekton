"""
Fallback implementation for when Hermes is not available.

This module provides a simple file-based fallback implementation
for memory storage and retrieval when Hermes services are unavailable.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from ..core.imports import logger


class FallbackStorage:
    """
    File-based fallback storage for memories when Hermes is not available.
    """
    
    def __init__(self, client_id: str, data_dir: Path):
        """
        Initialize fallback storage.
        
        Args:
            client_id: Client identifier
            data_dir: Data directory for storage
        """
        self.client_id = client_id
        self.data_dir = data_dir
        self.fallback_file = data_dir / f"{client_id}-memories.json"
        self.memories = {}
        
        self._load_memories()
    
    def _load_memories(self) -> None:
        """Load memories from file."""
        # Load existing memories if available
        if self.fallback_file.exists():
            try:
                with open(self.fallback_file, "r") as f:
                    self.memories = json.load(f)
                    logger.debug(f"Loaded {len(self.memories)} namespaces from fallback storage")
            except Exception as e:
                logger.error(f"Error loading fallback memories: {e}")
                self.memories = {}
    
    def _save_memories(self) -> bool:
        """Save memories to file."""
        try:
            with open(self.fallback_file, "w") as f:
                json.dump(self.memories, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving fallback memories: {e}")
            return False
    
    def initialize_namespace(self, namespace: str) -> None:
        """
        Initialize a namespace if it doesn't exist.
        
        Args:
            namespace: Namespace to initialize
        """
        if namespace not in self.memories:
            self.memories[namespace] = []
    
    def initialize_compartment(self, compartment_id: str) -> None:
        """
        Initialize a compartment namespace if it doesn't exist.
        
        Args:
            compartment_id: Compartment ID
        """
        namespace = f"compartment-{compartment_id}"
        self.initialize_namespace(namespace)
    
    def add_memory(self, memory_id: str, content: str, namespace: str, 
                  metadata: Dict[str, Any]) -> bool:
        """
        Add a memory to fallback storage.
        
        Args:
            memory_id: Unique memory ID
            content: Memory content
            namespace: Namespace to store in
            metadata: Memory metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure namespace exists
            self.initialize_namespace(namespace)
            
            # Create memory object
            memory_obj = {
                "id": memory_id,
                "content": content,
                "metadata": metadata
            }
            
            # Add to memory list
            self.memories[namespace].append(memory_obj)
            
            # Save to file
            return self._save_memories()
        except Exception as e:
            logger.error(f"Error adding memory to fallback storage: {e}")
            return False
    
    def search(self, query: str, namespace: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search for memories in fallback storage.
        
        Args:
            query: Search query
            namespace: Namespace to search in
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        try:
            # Simple keyword matching for fallback
            results = []
            
            for memory in self.memories.get(namespace, []):
                content = memory.get("content", "")
                if query.lower() in content.lower():
                    results.append({
                        "id": memory.get("id", ""),
                        "content": content,
                        "metadata": memory.get("metadata", {}),
                        "relevance": 1.0  # No real relevance score in fallback
                    })
            
            # Sort by timestamp (newest first) and limit results
            results.sort(
                key=lambda x: x.get("metadata", {}).get("timestamp", ""), 
                reverse=True
            )
            results = results[:limit]
            
            return results
        except Exception as e:
            logger.error(f"Error searching fallback memory: {e}")
            return []
    
    def clear_namespace(self, namespace: str) -> bool:
        """
        Clear all memories in a namespace.
        
        Args:
            namespace: Namespace to clear
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.memories[namespace] = []
            return self._save_memories()
        except Exception as e:
            logger.error(f"Error clearing namespace in fallback storage: {e}")
            return False
    
    def keep_memory(self, memory_id: str, days: int) -> bool:
        """
        Mark a memory to be kept for a specified number of days.
        
        Args:
            memory_id: ID of the memory to keep
            days: Number of days to keep
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the memory in fallback storage
            for namespace, memories in self.memories.items():
                for memory in memories:
                    if memory.get("id") == memory_id:
                        # Set expiration date in metadata
                        if "metadata" not in memory:
                            memory["metadata"] = {}
                        
                        expiration_date = datetime.now() + timedelta(days=days)
                        memory["metadata"]["expiration"] = expiration_date.isoformat()
                        
                        # Save to file
                        return self._save_memories()
            
            logger.warning(f"Memory {memory_id} not found in fallback storage")
            return False
        except Exception as e:
            logger.error(f"Error keeping memory: {e}")
            return False