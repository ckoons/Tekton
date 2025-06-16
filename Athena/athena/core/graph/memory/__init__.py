"""
Memory-based Graph Module for Athena

Provides a simple in-memory implementation of the graph database interface
with file-based persistence. Uses NetworkX as the underlying graph storage.
"""

from .adapter import MemoryAdapter

__all__ = ['MemoryAdapter']