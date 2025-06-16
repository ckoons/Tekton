"""
FAISS vector storage adapter for Tekton.

This module provides a FAISS implementation of the BaseVectorStorage
interface, allowing Tekton components to store and query vectors with
support for GPU acceleration.
"""

from tekton.core.storage.vector.faiss import FAISSVectorStore

# Re-export for backward compatibility
__all__ = ["FAISSVectorStore"]