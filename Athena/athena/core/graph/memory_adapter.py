"""
In-Memory Graph Adapter for Athena

Provides a simple in-memory implementation of the graph database interface
with file-based persistence.

This file has been refactored into the memory/ directory.
This module remains as a compatibility layer for backward compatibility.
"""

from .memory import MemoryAdapter

# Re-export the MemoryAdapter class for backward compatibility
__all__ = ['MemoryAdapter']