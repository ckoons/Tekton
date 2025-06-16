#!/usr/bin/env python3
"""
File-based Memory Storage

Provides fallback file-based storage for when vector DB is not available.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from engram.core.memory.utils import (
    generate_memory_id, 
    format_content,
    load_json_file,
    save_json_file
)

logger = logging.getLogger("engram.memory.file_storage")

class FileStorage:
    """
    File-based memory storage implementation.
    
    Provides a fallback storage mechanism when vector database
    is not available or when in fallback mode.
    """
    
    def __init__(self, client_id: str, data_dir: Path):
        """
        Initialize file-based memory storage.
        
        Args:
            client_id: Unique identifier for the client
            data_dir: Directory to store memory data
        """
        self.client_id = client_id
        self.data_dir = data_dir
        self.fallback_file = data_dir / f"{client_id}-memories.json"
        self.memories = self._load_memories()
        
    def _load_memories(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load memories from file.
        
        Returns:
            Dictionary of memories by namespace
        """
        if self.fallback_file.exists():
            try:
                with open(self.fallback_file, "r") as f:
                    data = json.load(f)
                    # Ensure all namespaces have list values
                    if isinstance(data, dict):
                        for namespace, memories in data.items():
                            if memories is None:
                                data[namespace] = []
                            elif not isinstance(memories, list):
                                data[namespace] = []
                    return data
            except Exception as e:
                logger.error(f"Error loading fallback memories: {e}")
        
        return {}
        
    def _save_memories(self) -> bool:
        """
        Save memories to file.
        
        Returns:
            Boolean indicating success
        """
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
            namespace: The namespace to initialize
        """
        if namespace not in self.memories:
            self.memories[namespace] = []
            
    def add(self, 
           content: Union[str, List[Dict[str, str]]],
           namespace: str,
           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a memory to storage.
        
        Args:
            content: The memory content (string or message objects)
            namespace: The namespace to store in
            metadata: Optional metadata for the memory
            
        Returns:
            Boolean indicating success
        """
        # Initialize namespace if needed
        self.initialize_namespace(namespace)
        
        # Format content to string if needed
        content_str = format_content(content)
        
        # Generate a unique memory ID
        memory_id = generate_memory_id(namespace, content_str)
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
            
        metadata["timestamp"] = datetime.now().isoformat()
        metadata["client_id"] = self.client_id
        
        # Create memory object
        memory_obj = {
            "id": memory_id,
            "content": content_str,
            "metadata": metadata
        }
        
        # Add to memory storage
        self.memories[namespace].append(memory_obj)
        
        # Save to file
        return self._save_memories()
        
    def search(self,
              query: str,
              namespace: str,
              limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memories based on a query.
        
        Args:
            query: The search query
            namespace: The namespace to search in
            limit: Maximum number of results to return
            
        Returns:
            List of matching memory objects
        """
        # Initialize results list
        results = []
        
        # Check if namespace exists
        if namespace not in self.memories:
            return results
            
        # Get memories for namespace, ensure it's a list
        namespace_memories = self.memories.get(namespace, [])
        if namespace_memories is None:
            namespace_memories = []
            
        # Simple keyword matching for fallback
        for memory in namespace_memories:
            # Skip None or invalid memory entries
            if memory is None or not isinstance(memory, dict):
                continue
                
            content = memory.get("content", "")
            if content and query.lower() in content.lower():
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
        
    def clear_namespace(self, namespace: str) -> bool:
        """
        Clear all memories in a namespace.
        
        Args:
            namespace: The namespace to clear
            
        Returns:
            Boolean indicating success
        """
        # Check if namespace exists
        if namespace not in self.memories:
            return True  # Nothing to clear
            
        # Clear the namespace
        self.memories[namespace] = []
        
        # Save changes
        return self._save_memories()
        
    def update_memory(self,
                     memory_id: str,
                     metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a specific memory.
        
        Args:
            memory_id: ID of the memory to update
            metadata: New or updated metadata values
            
        Returns:
            Boolean indicating success
        """
        # Find the memory
        for namespace, memories in self.memories.items():
            for i, memory in enumerate(memories):
                if memory.get("id") == memory_id:
                    # Update metadata
                    memory["metadata"].update(metadata)
                    
                    # Save changes
                    return self._save_memories()
        
        # Memory not found
        logger.warning(f"Memory {memory_id} not found in fallback storage")
        return False