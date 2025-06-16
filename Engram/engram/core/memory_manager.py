#!/usr/bin/env python3
"""
Memory Manager - Multi-client memory service for Engram

This module provides a manager that handles multiple client connections to the
memory service, allowing a single server to serve multiple Claude instances.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.memory_manager")

# Import MemoryService
from engram.core.memory import MemoryService
from engram.core.structured_memory import StructuredMemory
from engram.core.nexus import NexusInterface

class MemoryManager:
    """
    Memory manager for handling multiple client connections.
    
    This class maintains a pool of MemoryService instances for different clients,
    allowing a single server to handle requests from multiple Claude instances.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the memory manager.
        
        Args:
            data_dir: Root directory to store memory data (default: ~/.engram)
        """
        # Set up data directory
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path(os.path.expanduser("~/.engram"))
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache of memory service instances by client_id
        self.memory_services: Dict[str, MemoryService] = {}
        self.structured_memories: Dict[str, StructuredMemory] = {}
        self.nexus_interfaces: Dict[str, NexusInterface] = {}
        
        # Default client ID
        self.default_client_id = "claude"
        
        # Last access time for each client
        self.last_access: Dict[str, float] = {}
        
        # Lock for thread safety
        self.lock = asyncio.Lock()
        
        logger.info(f"Memory manager initialized with data directory: {self.data_dir}")
    
    async def get_memory_service(self, client_id: Optional[str] = None) -> MemoryService:
        """
        Get a memory service instance for the specified client.
        
        If no instance exists for the client, one will be created.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            A MemoryService instance for the client
        """
        # Use default client ID if none provided
        client_id = client_id or self.default_client_id
        
        async with self.lock:
            # Check if we already have a service for this client
            if client_id not in self.memory_services:
                logger.info(f"Creating new memory service for client: {client_id}")
                self.memory_services[client_id] = MemoryService(
                    client_id=client_id,
                    data_dir=str(self.data_dir)
                )
            
            # Update last access time
            import time
            self.last_access[client_id] = time.time()
            
            return self.memory_services[client_id]
    
    async def get_structured_memory(self, client_id: Optional[str] = None) -> StructuredMemory:
        """
        Get a structured memory instance for the specified client.
        
        If no instance exists for the client, one will be created.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            A StructuredMemory instance for the client
        """
        # Use default client ID if none provided
        client_id = client_id or self.default_client_id
        
        async with self.lock:
            # Check if we already have a service for this client
            if client_id not in self.structured_memories:
                logger.info(f"Creating new structured memory for client: {client_id}")
                self.structured_memories[client_id] = StructuredMemory(
                    client_id=client_id,
                    data_dir=str(self.data_dir)
                )
            
            # Update last access time
            import time
            self.last_access[client_id] = time.time()
            
            return self.structured_memories[client_id]
    
    async def get_nexus_interface(self, client_id: Optional[str] = None) -> NexusInterface:
        """
        Get a nexus interface for the specified client.
        
        If no instance exists for the client, one will be created.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            A NexusInterface instance for the client
        """
        # Use default client ID if none provided
        client_id = client_id or self.default_client_id
        
        async with self.lock:
            # Check if we already have an interface for this client
            if client_id not in self.nexus_interfaces:
                logger.info(f"Creating new nexus interface for client: {client_id}")
                
                # Create memory service and structured memory if needed
                memory_service = await self.get_memory_service(client_id)
                structured_memory = await self.get_structured_memory(client_id)
                
                # Create nexus interface
                self.nexus_interfaces[client_id] = NexusInterface(
                    memory_service=memory_service,
                    structured_memory=structured_memory
                )
            
            # Update last access time
            import time
            self.last_access[client_id] = time.time()
            
            return self.nexus_interfaces[client_id]
    
    async def list_clients(self) -> List[Dict[str, Any]]:
        """
        Get a list of active clients.
        
        Returns:
            A list of client information dictionaries
        """
        async with self.lock:
            clients = []
            
            import time
            current_time = time.time()
            
            # Create a list of clients with their last access time
            for client_id, last_time in self.last_access.items():
                clients.append({
                    "client_id": client_id,
                    "last_access": last_time,
                    "last_access_time": datetime_from_timestamp(last_time),
                    "idle_seconds": int(current_time - last_time),
                    "active": client_id in self.memory_services,
                    "structured_memory": client_id in self.structured_memories,
                    "nexus": client_id in self.nexus_interfaces
                })
            
            # Sort by most recently accessed
            clients.sort(key=lambda c: c["last_access"], reverse=True)
            
            return clients
    
    async def cleanup_idle_clients(self, idle_threshold: int = 3600) -> int:
        """
        Clean up clients that have been idle for a specified time.
        
        Args:
            idle_threshold: Time in seconds after which a client is considered idle
            
        Returns:
            Number of clients cleaned up
        """
        async with self.lock:
            import time
            current_time = time.time()
            cleanup_count = 0
            
            # Identify idle clients
            idle_clients = [
                client_id
                for client_id, last_time in self.last_access.items()
                if (current_time - last_time) > idle_threshold
            ]
            
            # Clean up idle clients
            for client_id in idle_clients:
                logger.info(f"Cleaning up idle client: {client_id}")
                self.memory_services.pop(client_id, None)
                self.structured_memories.pop(client_id, None)
                self.nexus_interfaces.pop(client_id, None)
                cleanup_count += 1
            
            return cleanup_count
    
    async def shutdown(self):
        """
        Shutdown the memory manager and release resources.
        """
        async with self.lock:
            # Clear all service instances
            self.memory_services.clear()
            self.structured_memories.clear()
            self.nexus_interfaces.clear()
            self.last_access.clear()
            
            logger.info("Memory manager shut down")


def datetime_from_timestamp(timestamp: float) -> str:
    """
    Convert a timestamp to a formatted datetime string.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Formatted datetime string
    """
    import datetime
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")