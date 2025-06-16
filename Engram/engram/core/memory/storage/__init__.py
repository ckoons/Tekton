#!/usr/bin/env python3
"""
Memory Storage Module

Provides storage implementations for the memory service.
"""

# Export storage implementations
from engram.core.memory.storage.file_storage import FileStorage

try:
    from engram.core.memory.storage.vector_storage import VectorStorage
    HAS_VECTOR_STORAGE = True
except ImportError:
    HAS_VECTOR_STORAGE = False

__all__ = ["FileStorage", "HAS_VECTOR_STORAGE"]

if HAS_VECTOR_STORAGE:
    __all__.append("VectorStorage")