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

from ergon.core.memory.service import MemoryService
from ergon.core.memory.rag import RAGService, RAGToolFunctions
from ergon.core.memory.utils.categories import MemoryCategory
from ergon.core.memory.models.schema import Memory, MemoryCollection
from ergon.core.memory.services.client import ClientManager, client_manager

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