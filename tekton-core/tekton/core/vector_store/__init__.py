"""Vector store module for Tekton with hardware-specific optimizations.

This module provides a unified interface for vector stores with implementations
optimized for different hardware platforms.
"""

from enum import Enum
import platform
import subprocess
import logging
import os
from typing import Optional, Dict, Any, List

# Configure logger
logger = logging.getLogger(__name__)


class HardwareType(Enum):
    """Enumeration of hardware platforms."""
    APPLE_SILICON = "apple_silicon"
    NVIDIA = "nvidia"
    OTHER = "other"


def detect_hardware() -> HardwareType:
    """Detect hardware platform type."""
    # Check for Apple Silicon
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        logger.info("Detected Apple Silicon hardware")
        return HardwareType.APPLE_SILICON
    
    # Check for NVIDIA GPUs
    try:
        gpu_info = subprocess.check_output("nvidia-smi", shell=True)
        if gpu_info:
            logger.info("Detected NVIDIA GPU hardware")
            return HardwareType.NVIDIA
    except:
        pass
    
    logger.info("Could not detect specialized hardware, using default configuration")
    return HardwareType.OTHER


class VectorStore:
    """Abstract base class for vector stores."""
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add documents to the vector store."""
        raise NotImplementedError()
    
    def update_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        """Update a document in the vector store."""
        raise NotImplementedError()
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the vector store."""
        raise NotImplementedError()
    
    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for documents by semantic similarity."""
        raise NotImplementedError()
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        raise NotImplementedError()
    
    def get_documents_by_metadata(self, metadata_key: str, metadata_value: Any) -> List[Dict[str, Any]]:
        """Get documents by metadata."""
        raise NotImplementedError()
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents."""
        raise NotImplementedError()
    
    def count_documents(self) -> int:
        """Get document count."""
        raise NotImplementedError()
    
    def rebuild_index(self) -> bool:
        """Rebuild the vector store index from scratch."""
        raise NotImplementedError()


# Vector store factory
def get_vector_store(path: Optional[str] = None, dimension: int = 384, distance_metric: str = "cosine", embedding_model: str = "all-MiniLM-L6-v2") -> VectorStore:
    """Get appropriate vector store based on hardware.
    
    Args:
        path: Path to store vector database files
        dimension: Embedding dimension
        distance_metric: Distance metric for comparison (cosine or l2)
        embedding_model: Model to use for embeddings
        
    Returns:
        Vector store instance optimized for the current hardware
    """
    hardware = detect_hardware()
    
    if hardware == HardwareType.APPLE_SILICON:
        try:
            from tekton.core.vector_store.qdrant_store import QdrantStore
            logger.info("Using Qdrant vector store optimized for Apple Silicon")
            return QdrantStore(path=path, dimension=dimension, distance_metric=distance_metric, embedding_model=embedding_model)
        except ImportError:
            logger.warning("Qdrant not available, falling back to FAISS")
            from tekton.core.vector_store.faiss_store import FAISSStore
            return FAISSStore(path=path, dimension=dimension, distance_metric=distance_metric, embedding_model=embedding_model)
    else:
        # Default to FAISS for NVIDIA and other platforms
        from tekton.core.vector_store.faiss_store import FAISSStore
        logger.info("Using FAISS vector store optimized for NVIDIA/CPU")
        return FAISSStore(path=path, dimension=dimension, distance_metric=distance_metric, embedding_model=embedding_model)
