"""
FAISS Vector Adapter - High-performance vector database using Facebook CI Similarity Search.

This module provides a VectorDatabaseAdapter implementation that uses FAISS
for fast and efficient similarity search with hardware acceleration.
"""

from hermes.adapters.vector.faiss.adapter import FAISSVectorAdapter

# Re-export the adapter class for backward compatibility
__all__ = ["FAISSVectorAdapter"]