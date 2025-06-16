"""
API Models for Engram Consolidated Server

This module defines Pydantic models for API requests and responses.
"""

from typing import Dict, List, Any, Optional
from tekton.models import TektonBaseModel


class MemoryQuery(TektonBaseModel):
    """Request model for memory query endpoint."""
    query: str
    namespace: str = "conversations"
    limit: int = 5


class MemoryStore(TektonBaseModel):
    """Request model for memory store endpoint."""
    key: str
    value: str
    namespace: str = "conversations"
    metadata: Optional[Dict[str, Any]] = None


class MemoryMultiQuery(TektonBaseModel):
    """Request model for multi-namespace memory query endpoint."""
    query: str
    namespaces: List[str] = ["conversations", "thinking", "longterm"]
    limit: int = 3


class HealthResponse(TektonBaseModel):
    """Response model for health check endpoint."""
    status: str
    client_id: str
    mem0_available: bool  # For backward compatibility
    vector_available: bool = False
    namespaces: List[str]
    structured_memory_available: bool
    nexus_available: bool
    implementation_type: str = "unknown"
    vector_search: bool = False
    vector_db_version: Optional[str] = None
    vector_db_name: Optional[str] = None
    multi_client: bool = True


class ClientModel(TektonBaseModel):
    """Model for client information."""
    client_id: str
    last_access_time: str
    idle_seconds: int
    active: bool
    structured_memory: bool
    nexus: bool