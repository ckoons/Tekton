#!/usr/bin/env python3
"""
Memory Service Base

Provides the main MemoryService class that manages memory operations.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from engram.core.memory.config import initialize_vector_db, USE_FALLBACK
from engram.core.memory.storage import FileStorage
from engram.core.memory.compartments import CompartmentManager
from engram.core.memory.search import search_memory, get_relevant_context
from engram.core.memory.utils import load_json_file, save_json_file

logger = logging.getLogger("engram.memory")

class MemoryService:
    """
    Memory service providing storage and retrieval across different namespaces.
    
    Supports the following namespaces:
    - conversations: Dialog history between user and AI
    - thinking: AI's internal thought processes
    - longterm: High-priority persistent memories
    - projects: Project-specific context
    - compartments: Metadata about compartments
    - session: Session-specific memory
    """
    
    def __init__(self, client_id: str = "default", data_dir: Optional[str] = None):
        """
        Initialize the memory service.
        
        Args:
            client_id: Unique identifier for the client (default: "default")
            data_dir: Directory to store memory data (default: ~/.engram)
        """
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
        
        # Initialize compartment manager
        self.compartment_manager = CompartmentManager(client_id, self.data_dir)
        self.active_compartments = []
        
        # Initialize storage backend
        self.vector_available = False
        self.storage = None
        self._initialize_storage()
        
    def _initialize_storage(self) -> None:
        """Initialize the appropriate storage backend."""
        # Check if vector DB is available
        has_vector_db, vector_db_info, vector_model = initialize_vector_db()
        
        if has_vector_db and not USE_FALLBACK:
            # Initialize vector storage
            try:
                from engram.core.memory.storage import HAS_VECTOR_STORAGE, VectorStorage
                
                if HAS_VECTOR_STORAGE:
                    self.storage = VectorStorage(
                        client_id=self.client_id,
                        data_dir=self.data_dir,
                        vector_model=vector_model,
                        vector_db_name=vector_db_info.get("name")
                    )
                    self.vector_available = True
                    logger.info("Initialized vector-based memory storage")
                else:
                    # Fall back to file storage
                    logger.warning("Vector storage module not available, using file storage")
                    self.storage = FileStorage(self.client_id, self.data_dir)
            except Exception as e:
                logger.error(f"Error initializing vector storage: {e}")
                # Fall back to file storage
                self.storage = FileStorage(self.client_id, self.data_dir)
        else:
            # Use file storage
            logger.info("Using file-based memory storage")
            self.storage = FileStorage(self.client_id, self.data_dir)
            
        # Initialize namespaces in storage
        for namespace in self.namespaces:
            if hasattr(self.storage, "initialize_namespace"):
                self.storage.initialize_namespace(namespace)
                
        # Initialize compartment namespaces
        for compartment_id in self.compartment_manager.compartments:
            namespace = f"compartment-{compartment_id}"
            if hasattr(self.storage, "initialize_namespace"):
                self.storage.initialize_namespace(namespace)
            
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
        # Validate namespace
        valid_namespaces = self.namespaces + self.compartment_manager.get_compartment_namespaces()
        
        if namespace not in valid_namespaces:
            # Invalid namespace, fall back to default
            logger.warning(f"Invalid namespace: {namespace}, using 'conversations'")
            namespace = "conversations"
            
        # Add memory using storage backend
        return self.storage.add(content, namespace, metadata)
    
    async def search(self, 
                    query: str, 
                    namespace: str = "conversations", 
                    limit: int = 5,
                    check_forget: bool = True) -> Dict[str, Any]:
        """
        Search for memories based on a query.
        
        Args:
            query: The search query
            namespace: The namespace to search in (default: "conversations")
            limit: Maximum number of results to return
            check_forget: Whether to check for and filter out forgotten information
            
        Returns:
            Dictionary with search results
        """
        return await search_memory(
            storage=self.storage,
            query=query,
            namespace=namespace,
            limit=limit,
            check_forget=check_forget
        )
    
    async def get_relevant_context(self, 
                                  query: str, 
                                  namespaces: List[str] = None,
                                  limit: int = 3) -> str:
        """
        Get formatted context from multiple namespaces for a given query.
        
        Args:
            query: The query to search for
            namespaces: List of namespaces to search (default: all)
            limit: Maximum memories per namespace
            
        Returns:
            Formatted context string
        """
        return await get_relevant_context(
            storage=self.storage,
            query=query,
            namespaces=namespaces,
            limit=limit
        )
    
    async def get_namespaces(self) -> List[str]:
        """Get available namespaces."""
        # Start with standard namespaces
        all_namespaces = self.namespaces.copy()
        
        # Add compartment namespaces
        all_namespaces.extend(self.compartment_manager.get_compartment_namespaces())
        
        return all_namespaces
    
    async def clear_namespace(self, namespace: str) -> bool:
        """
        Clear all memories in a namespace.
        
        Args:
            namespace: The namespace to clear
            
        Returns:
            Boolean indicating success
        """
        # Validate namespace
        valid_namespaces = self.namespaces + self.compartment_manager.get_compartment_namespaces()
        
        if namespace not in valid_namespaces:
            logger.warning(f"Invalid namespace: {namespace}")
            return False
            
        # Clear namespace using storage backend
        return self.storage.clear_namespace(namespace)
    
    async def create_compartment(self, name: str, description: str = None, parent: str = None) -> Optional[str]:
        """
        Create a new memory compartment.
        
        Args:
            name: Name of the compartment
            description: Optional description
            parent: Optional parent compartment ID for hierarchical organization
            
        Returns:
            Compartment ID if successful, None otherwise
        """
        # Create compartment
        compartment_id = await self.compartment_manager.create_compartment(
            name, description, parent
        )
        
        if compartment_id:
            # Initialize storage for this compartment
            namespace = f"compartment-{compartment_id}"
            if hasattr(self.storage, "initialize_namespace"):
                self.storage.initialize_namespace(namespace)
                
            # Store the compartment info in the compartments namespace
            await self.add(
                content=f"Compartment: {name} (ID: {compartment_id})\nDescription: {description or 'N/A'}\nParent: {parent or 'None'}",
                namespace="compartments",
                metadata={"compartment_id": compartment_id}
            )
            
        return compartment_id
    
    async def activate_compartment(self, compartment_id_or_name: str) -> bool:
        """
        Activate a compartment to include in automatic context retrieval.
        
        Args:
            compartment_id_or_name: ID or name of compartment to activate
            
        Returns:
            Boolean indicating success
        """
        return await self.compartment_manager.activate_compartment(compartment_id_or_name)
    
    async def deactivate_compartment(self, compartment_id_or_name: str) -> bool:
        """
        Deactivate a compartment to exclude from automatic context retrieval.
        
        Args:
            compartment_id_or_name: ID or name of compartment to deactivate
            
        Returns:
            Boolean indicating success
        """
        return await self.compartment_manager.deactivate_compartment(compartment_id_or_name)
    
    async def set_compartment_expiration(self, compartment_id: str, days: int = None) -> bool:
        """
        Set expiration for a compartment in days.
        
        Args:
            compartment_id: ID of the compartment
            days: Number of days until expiration, or None to remove expiration
            
        Returns:
            Boolean indicating success
        """
        return await self.compartment_manager.set_compartment_expiration(compartment_id, days)
    
    async def list_compartments(self, include_expired: bool = False) -> List[Dict[str, Any]]:
        """
        List all compartments.
        
        Args:
            include_expired: Whether to include expired compartments
            
        Returns:
            List of compartment information dictionaries
        """
        return await self.compartment_manager.list_compartments(include_expired)
    
    async def write_session_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Write a memory to the session namespace for persistence across sessions.
        
        Args:
            content: The content to store
            metadata: Optional metadata
            
        Returns:
            Boolean indicating success
        """
        return await self.add(content=content, namespace="session", metadata=metadata)
            
    async def keep_memory(self, memory_id: str, days: int = 30) -> bool:
        """
        Keep a memory for a specified number of days by setting expiration.
        
        Args:
            memory_id: The ID of the memory to keep
            days: Number of days to keep the memory
            
        Returns:
            Boolean indicating success
        """
        # Update memory metadata with expiration
        try:
            from datetime import timedelta
            expiration_date = datetime.now() + timedelta(days=days)
            expiration_str = expiration_date.isoformat()
            
            if hasattr(self.storage, "update_memory"):
                # Use storage-specific update method
                return self.storage.update_memory(
                    memory_id=memory_id,
                    metadata={"expiration": expiration_str}
                )
            
            # Default implementation for storages without update_memory
            logger.warning(f"Storage does not support updating memory metadata")
            return False
        except Exception as e:
            logger.error(f"Error keeping memory: {e}")
            return False
            
    async def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about the storage backend.
        
        Returns:
            Dictionary containing storage information
        """
        try:
            storage_info = {
                "storage_type": self.storage.__class__.__name__,
                "vector_available": self.vector_available,
                "client_id": self.client_id,
                "data_dir": str(self.data_dir),
                "namespaces": await self.get_namespaces()
            }
            
            # Get additional storage-specific info if available
            if hasattr(self.storage, "get_storage_info"):
                storage_specific_info = self.storage.get_storage_info()
                storage_info.update(storage_specific_info)
                
            return storage_info
        except Exception as e:
            logger.error(f"Error getting storage info: {e}")
            return {
                "storage_type": "unknown",
                "error": str(e)
            }