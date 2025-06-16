"""
In-memory graph storage implementation for Tekton.

This package provides an in-memory implementation of the BaseGraphStorage
interface, suitable for testing or small datasets.
"""

from tekton.core.storage.graph.memory.store import MemoryGraphStore

__all__ = ["MemoryGraphStore"]