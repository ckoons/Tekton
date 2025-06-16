"""
Qdrant vector storage implementation for Tekton.

This package provides a Qdrant implementation of the BaseVectorStorage
interface, allowing Tekton components to store and query vectors with
optimization for Apple Silicon.
"""

from tekton.core.storage.vector.qdrant.store import QdrantVectorStore

__all__ = ["QdrantVectorStore"]