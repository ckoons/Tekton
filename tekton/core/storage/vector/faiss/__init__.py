"""
FAISS vector storage implementation for Tekton.

This package provides a FAISS implementation of the BaseVectorStorage
interface, allowing Tekton components to store and query vectors with
support for GPU acceleration.
"""

from tekton.core.storage.vector.faiss.store import FAISSVectorStore

__all__ = ["FAISSVectorStore"]