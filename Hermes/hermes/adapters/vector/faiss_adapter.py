"""
FAISS Vector Adapter - High-performance vector database using Facebook CI Similarity Search.

This module provides a VectorDatabaseAdapter implementation that uses FAISS
for fast and efficient similarity search with hardware acceleration.

This module has been refactored into a modular structure. This file is kept for
backward compatibility.
"""

# Re-export the adapter from the modular structure
from hermes.adapters.vector.faiss import FAISSVectorAdapter

# For backward compatibility
from hermes.core.database.database_types import DatabaseBackend