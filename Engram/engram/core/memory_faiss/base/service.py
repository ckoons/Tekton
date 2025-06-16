#!/usr/bin/env python3
"""
Base Memory Service implementation using FAISS for vector storage

This module provides the core MemoryService class with initialization
and common memory operations across different namespaces.
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Import from refactored structure
from ..utils.logging import setup_logger
from ..utils.helpers import is_valid_namespace

# Initialize logger
logger = setup_logger("engram.memory")

class MemoryService:
    """
    Memory service providing storage and retrieval across different namespaces.
    
    Supports the following namespaces:
    - conversations: Dialog history between user and AI
    - thinking: AI's internal thought processes
    - longterm: High-priority persistent memories
    - projects: Project-specific context
    """
    
    def __init__(self, client_id: str = "default", data_dir: Optional[str] = None):
        """
        Initialize the memory service.
        
        Args:
            client_id: Unique identifier for the client (default: "default")
            data_dir: Directory to store memory data (default: ~/.engram)
        """
        from ..storage.vector import setup_vector_storage
        from ..storage.file import setup_file_storage
        
        self.client_id = client_id
        
        # Set up data directory
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path(os.path.expanduser("~/.engram"))
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Standard namespaces
        self.namespaces = ["conversations", "thinking", "longterm", "projects", "compartments", "session"]
        
        # Store active compartments
        self.active_compartments = []
        self.compartment_file = self.data_dir / f"{client_id}-compartments.json"
        self.compartments = self._load_compartments()
        
        # Set up storage (either vector or fallback file-based)
        vector_info = setup_vector_storage(self.data_dir, self.client_id, self.namespaces, self.compartments)
        self.vector_available = vector_info["available"]
        self.vector_store = vector_info["store"]
        self.vector_model = vector_info["model"]
        self.namespace_collections = vector_info["collections"]
        self.vector_dim = vector_info["dimension"]
        
        # Set up fallback file storage if vector storage is not available
        if not self.vector_available:
            fallback_info = setup_file_storage(self.data_dir, self.client_id, self.namespaces, self.compartments)
            self.fallback_file = fallback_info["file"]
            self.fallback_memories = fallback_info["memories"]
    
    def _load_compartments(self) -> Dict[str, Dict[str, Any]]:
        """Load compartment definitions from file."""
        if self.compartment_file.exists():
            try:
                with open(self.compartment_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading compartments: {e}")
        
        # Initialize with empty compartments dict if none exists
        return {}
        
    def _save_compartments(self) -> bool:
        """Save compartment definitions to file."""
        try:
            with open(self.compartment_file, "w") as f:
                json.dump(self.compartments, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving compartments: {e}")
            return False
    
    def _ensure_compartment_collection(self, compartment_id: str) -> bool:
        """Ensure vector collection or fallback storage exists for the given compartment."""
        from ..storage.vector import ensure_vector_compartment
        from ..storage.file import ensure_file_compartment
        
        if self.vector_available:
            return ensure_vector_compartment(
                compartment_id=compartment_id, 
                client_id=self.client_id,
                vector_store=self.vector_store,
                namespace_collections=self.namespace_collections
            )
        else:
            return ensure_file_compartment(
                compartment_id=compartment_id,
                fallback_memories=self.fallback_memories
            )
    
    async def add(self, 
                  content: Union[str, List[Dict[str, str]]], 
                  namespace: str = "conversations", 
                  metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a memory to storage.
        
        Args:
            content: The memory content (string or list of message objects)
            namespace: The namespace to store in (default: "conversations")
            metadata: Optional metadata for the memory
            
        Returns:
            Boolean indicating success
        """
        from ..storage.vector import add_to_vector_store
        from ..storage.file import add_to_file_store
        
        # Check if namespace is a valid base namespace or a compartment
        if not is_valid_namespace(namespace, self.namespaces, self.compartments):
            logger.warning(f"Invalid namespace: {namespace}, using 'conversations'")
            namespace = "conversations"
        
        timestamp = datetime.now().isoformat()
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata["timestamp"] = timestamp
        metadata["client_id"] = self.client_id
        
        # Convert content to string if it's a list of messages
        if isinstance(content, list):
            try:
                # Format as conversation
                content_str = "\n".join([
                    f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" 
                    for msg in content
                ])
            except Exception as e:
                logger.error(f"Error formatting conversation: {e}")
                content_str = str(content)
        else:
            content_str = content
        
        # Generate a unique memory ID
        memory_id = f"{namespace}-{int(time.time())}-{hash(content_str) % 10000}"
        
        # Store in vector database if available
        if self.vector_available:
            try:
                success = add_to_vector_store(
                    vector_store=self.vector_store,
                    namespace=namespace,
                    namespace_collections=self.namespace_collections,
                    client_id=self.client_id,
                    memory_id=memory_id,
                    content=content_str,
                    metadata=metadata
                )
                
                if success:
                    return True
                # Fall back to local storage if vector storage fails
            except Exception as e:
                logger.error(f"Error adding memory to vector store: {e}")
                # Fall back to local storage
        
        # Store in fallback memory
        try:
            return add_to_file_store(
                fallback_memories=self.fallback_memories,
                fallback_file=self.fallback_file,
                namespace=namespace,
                memory_id=memory_id,
                content=content_str,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Error adding memory to fallback storage: {e}")
            return False
    
    async def get_namespaces(self) -> List[str]:
        """Get available namespaces."""
        base_namespaces = ["conversations", "thinking", "longterm", "projects", "compartments", "session"]
        
        # Add compartment namespaces
        compartment_namespaces = [f"compartment-{c_id}" for c_id in self.compartments]
        
        return base_namespaces + compartment_namespaces
    
    async def clear_namespace(self, namespace: str) -> bool:
        """
        Clear all memories in a namespace.
        
        Args:
            namespace: The namespace to clear
            
        Returns:
            Boolean indicating success
        """
        from ..storage.vector import clear_vector_namespace
        from ..storage.file import clear_file_namespace
        
        valid_namespaces = ["conversations", "thinking", "longterm", "projects", "compartments", "session"]
        
        # Support compartment namespaces
        if namespace.startswith("compartment-"):
            compartment_id = namespace[len("compartment-"):]
            if compartment_id not in self.compartments:
                logger.warning(f"Invalid compartment: {compartment_id}")
                return False
        elif namespace not in valid_namespaces:
            logger.warning(f"Invalid namespace: {namespace}")
            return False
        
        # Clear vector database if available
        if self.vector_available:
            try:
                return clear_vector_namespace(
                    vector_store=self.vector_store,
                    namespace=namespace,
                    namespace_collections=self.namespace_collections,
                    client_id=self.client_id
                )
            except Exception as e:
                logger.error(f"Error clearing namespace in vector storage: {e}")
                # Fall back to file storage
        
        # Clear fallback memory
        try:
            return clear_file_namespace(
                fallback_memories=self.fallback_memories,
                fallback_file=self.fallback_file,
                namespace=namespace
            )
        except Exception as e:
            logger.error(f"Error clearing namespace in fallback storage: {e}")
            return False
    
    async def write_session_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Write a memory to the session namespace for persistence across sessions.
        
        Args:
            content: The content to store
            metadata: Optional metadata
            
        Returns:
            Boolean indicating success
        """
        try:
            # Add to session namespace
            return await self.add(content=content, namespace="session", metadata=metadata)
        except Exception as e:
            logger.error(f"Error writing session memory: {e}")
            return False