"""
Main service class for the Hermes Memory Adapter.

This module provides the HermesMemoryService class,
which integrates Engram memory with Hermes database services.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from .imports import logger, HAS_HERMES, DatabaseClient
from ..utils.fallback import FallbackStorage
from ..compartments.manager import CompartmentManager
from ..operations.memory import (
    add_memory, 
    clear_namespace, 
    write_session_memory,
    keep_memory
)
from ..operations.search import (
    search_memories,
    get_relevant_context,
    get_namespaces
)


class HermesMemoryService:
    """
    Memory service implementation using Hermes database services.
    
    This class provides the same interface as Engram's MemoryService, but
    uses Hermes's centralized database services for storage and retrieval.
    """
    
    def __init__(self, client_id: str = "default", data_dir: Optional[str] = None):
        """
        Initialize the Hermes memory service.
        
        Args:
            client_id: Unique identifier for the client (default: "default")
            data_dir: Directory to store memory data (default: ~/.engram)
        """
        self.client_id = client_id
        
        # Set up data directory - maintained for compatibility with original
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path(os.path.expanduser("~/.engram"))
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize compartment manager
        self.compartment_manager = CompartmentManager(client_id, self.data_dir)
        
        # Available namespaces
        self.namespaces = ["conversations", "thinking", "longterm", "projects", "compartments", "session"]
        
        # Initialize Hermes client if available
        self.hermes_available = HAS_HERMES
        self.hermes_client = None
        
        if self.hermes_available:
            try:
                # Initialize the DatabaseClient
                self.hermes_client = DatabaseClient(
                    component_id=f"engram.{client_id}",
                    data_path=str(self.data_dir),
                    config={"vector_dim": 1536}  # Default dimension for most embedding models
                )
                logger.info(f"Initialized Hermes database client for Engram ({client_id})")
            except Exception as e:
                logger.error(f"Error initializing Hermes client: {e}")
                self.hermes_available = False
        
        # Initialize fallback storage if needed
        self.fallback_storage = FallbackStorage(client_id, self.data_dir)
        
        # Initialize namespaces in fallback storage
        for namespace in self.namespaces:
            self.fallback_storage.initialize_namespace(namespace)
        
        # Initialize compartment storage in fallback storage
        for compartment_id in self.compartment_manager.compartments:
            self.fallback_storage.initialize_compartment(compartment_id)
    
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
        return await add_memory(
            self.hermes_client if self.hermes_available else None,
            self.fallback_storage,
            self.compartment_manager,
            content=content,
            namespace=namespace,
            metadata=metadata,
            client_id=self.client_id
        )
    
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
        return await search_memories(
            self.hermes_client if self.hermes_available else None,
            self.fallback_storage,
            self.compartment_manager,
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
            self.hermes_client if self.hermes_available else None,
            self.fallback_storage,
            self.compartment_manager,
            query=query,
            namespaces=namespaces,
            limit=limit
        )
    
    async def get_namespaces(self) -> List[str]:
        """
        Get available namespaces.
        
        Returns:
            List of namespace names
        """
        return await get_namespaces(self.compartment_manager)
    
    async def clear_namespace(self, namespace: str) -> bool:
        """
        Clear all memories in a namespace.
        
        Args:
            namespace: The namespace to clear
            
        Returns:
            Boolean indicating success
        """
        return await clear_namespace(
            self.hermes_client if self.hermes_available else None,
            self.fallback_storage,
            self.compartment_manager,
            namespace=namespace
        )
    
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
        compartment_id = await self.compartment_manager.create_compartment(
            name=name, description=description, parent=parent
        )
        
        if compartment_id:
            # Store the compartment info in the compartments namespace
            await self.add(
                content=f"Compartment: {name} (ID: {compartment_id})\nDescription: {description or 'N/A'}\nParent: {parent or 'None'}",
                namespace="compartments",
                metadata={"compartment_id": compartment_id}
            )
            
            # Initialize in fallback storage
            self.fallback_storage.initialize_compartment(compartment_id)
        
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
        return await self.compartment_manager.set_compartment_expiration(
            compartment_id=compartment_id, days=days
        )
    
    async def list_compartments(self, include_expired: bool = False) -> List[Dict[str, Any]]:
        """
        List all compartments.
        
        Args:
            include_expired: Whether to include expired compartments
            
        Returns:
            List of compartment information dictionaries
        """
        return await self.compartment_manager.list_compartments(include_expired=include_expired)
    
    async def write_session_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Write a memory to the session namespace for persistence across sessions.
        
        Args:
            content: The content to store
            metadata: Optional metadata
            
        Returns:
            Boolean indicating success
        """
        return await write_session_memory(
            self.hermes_client if self.hermes_available else None,
            self.fallback_storage,
            self.compartment_manager,
            content=content,
            metadata=metadata,
            client_id=self.client_id
        )
    
    async def keep_memory(self, memory_id: str, days: int = 30) -> bool:
        """
        Keep a memory for a specified number of days by setting expiration.
        
        Args:
            memory_id: The ID of the memory to keep
            days: Number of days to keep the memory
            
        Returns:
            Boolean indicating success
        """
        return await keep_memory(
            self.hermes_client if self.hermes_available else None,
            self.fallback_storage,
            memory_id=memory_id,
            days=days
        )
    
    async def close(self) -> None:
        """Close connections and clean up resources."""
        if self.hermes_available and self.hermes_client:
            try:
                await self.hermes_client.close_connections()
                logger.debug("Closed Hermes database connections")
            except Exception as e:
                logger.error(f"Error closing Hermes connections: {e}")