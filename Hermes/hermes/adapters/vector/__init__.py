"""
Vector Database Adapters - Implementations for vector databases.

This package contains concrete implementations of the VectorDatabaseAdapter interface
for various vector database backends.
"""

# INTEGRATION TEST NOTE:
# During full Tekton stack integration testing, verify the following vector database
# implementations and their dependencies:
#
# 1. FAISS (Facebook AI Similarity Search)
#    - Requires: pip install faiss-cpu or faiss-gpu
#    - Hardware acceleration with CUDA is recommended for production
#    - Configuration in Tekton should specify dimensionality and index type
#
# 2. Potential Additions for Production:
#    - Qdrant (qdrant_adapter.py) - Fast vector DB with filtering
#    - ChromaDB (chromadb_adapter.py) - Good for document collections
#    - Milvus/Zilliz - For scaled deployments
#
# The fallback adapter should only be used for development/testing, not production.

# Re-export adapters for simplified imports
from .faiss_adapter import FAISSVectorAdapter
from .fallback_adapter import FallbackVectorAdapter

__all__ = [
    "FAISSVectorAdapter",
    "FallbackVectorAdapter"
]