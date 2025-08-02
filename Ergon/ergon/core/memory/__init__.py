"""
Memory management system for Ergon.

This package provides persistent memory capabilities for agents using
Tekton's shared vector database approach with hardware optimization.

Key components:
- MemoryService: Core service for storing and retrieving memories
- RAGService: Retrieval Augmented Generation for enhancing prompts
- MemoryCategory: Categories for organizing memories
- RAGToolFunctions: Tool functions for agent use
- ClientManager: Client registration and lifecycle management
"""

from .service import MemoryService
from .rag import RAGService, RAGToolFunctions
from .utils.categories import MemoryCategory
from .models.schema import Memory, MemoryCollection
from .services.client import ClientManager, client_manager

__all__ = [
    'MemoryService',
    'RAGService',
    'RAGToolFunctions',
    'MemoryCategory',
    'Memory',
    'MemoryCollection',
    'ClientManager',
    'client_manager'
]