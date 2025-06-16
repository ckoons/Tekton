"""
Qdrant vector storage adapter for Tekton.

This module provides a Qdrant implementation of the BaseVectorStorage
interface, allowing Tekton components to store and query vectors with
optimized performance on Apple Silicon.
"""

from tekton.core.storage.vector.qdrant import QdrantVectorStore

# Re-export for backward compatibility
__all__ = ["QdrantVectorStore"]