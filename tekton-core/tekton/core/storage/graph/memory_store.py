"""
In-memory graph storage adapter for Tekton.

This module provides an in-memory implementation of the BaseGraphStorage
interface, suitable for testing or small datasets.
"""

from tekton.core.storage.graph.memory import MemoryGraphStore

# Re-export for backward compatibility
__all__ = ["MemoryGraphStore"]