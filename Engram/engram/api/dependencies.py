"""
API Dependencies - Dependency injection for FastAPI routes

This module provides functions for dependency injection in FastAPI routes.
"""

from typing import Optional
from fastapi import Header, HTTPException, Depends

# Use the new turn-based storage service
from engram.services.storage_service import StorageService

# Keep these for compatibility, though they may not be used
try:
    from engram.core.structured_memory import StructuredMemory
    from engram.core.nexus import NexusInterface
except ImportError:
    # These modules may not exist in the simplified architecture
    StructuredMemory = None
    NexusInterface = None

# Global memory manager instance
memory_manager = None
default_client_id = "claude"


# Helper to get client ID from request
async def get_client_id(x_client_id: Optional[str] = Header(None)) -> str:
    """Get client ID from header or use default."""
    return x_client_id or default_client_id


# Helper to get memory manager
async def get_memory_manager():
    """Get memory manager instance."""
    if memory_manager is None:
        raise HTTPException(status_code=500, detail="Memory manager not initialized")
    return memory_manager


# Helper to get storage service for client
async def get_memory_service(client_id: str = Depends(get_client_id)) -> StorageService:
    """Get storage service for the specified client."""
    # For now, return a simple storage service instance
    # In the turn-based architecture, we don't need complex memory management
    return StorageService()


# Helper to get structured memory for client
async def get_structured_memory(client_id: str = Depends(get_client_id)) -> StructuredMemory:
    """Get structured memory for the specified client."""
    if memory_manager is None:
        raise HTTPException(status_code=500, detail="Memory manager not initialized")
    return await memory_manager.get_structured_memory(client_id)


# Helper to get nexus interface for client
async def get_nexus_interface(client_id: str = Depends(get_client_id)) -> NexusInterface:
    """Get nexus interface for the specified client."""
    if memory_manager is None:
        raise HTTPException(status_code=500, detail="Memory manager not initialized")
    return await memory_manager.get_nexus_interface(client_id)