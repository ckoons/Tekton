"""
Utility functions for FAISS vector store.
"""

import os
import logging
import tempfile
import numpy as np
from typing import Dict, Any, Optional, Tuple, Union

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False

# Configure logger
logger = logging.getLogger(__name__)

def check_faiss_available():
    """Check if FAISS is available."""
    if not FAISS_AVAILABLE:
        raise ImportError(
            "FAISS is required for FAISSVectorStore. "
            "Install with: pip install faiss-gpu or faiss-cpu"
        )

def get_faiss_metric(distance_metric: str) -> Tuple[int, bool]:
    """
    Convert distance metric string to FAISS metric type.
    
    Args:
        distance_metric: Distance metric (cosine, l2, ip)
        
    Returns:
        Tuple of (faiss_metric, normalize)
    """
    if distance_metric == "cosine":
        return faiss.METRIC_INNER_PRODUCT, True
    elif distance_metric == "l2":
        return faiss.METRIC_L2, False
    elif distance_metric == "ip":
        return faiss.METRIC_INNER_PRODUCT, False
    else:
        raise ValueError(f"Unsupported distance metric: {distance_metric}")

def normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    """
    Normalize vectors to unit length.
    
    Args:
        vectors: Vectors to normalize
        
    Returns:
        Normalized vectors
    """
    if len(vectors.shape) == 1:
        vectors = vectors.reshape(1, -1)
    
    norm = np.linalg.norm(vectors, axis=1, keepdims=True)
    mask = norm > 0
    result = np.zeros_like(vectors)
    result[mask.reshape(-1)] = vectors[mask.reshape(-1)] / norm[mask]
    return result

def gpu_available() -> bool:
    """Check if GPU is available for FAISS."""
    try:
        return faiss.get_num_gpus() > 0
    except:
        return False

def convert_distance_to_similarity(
    distances: np.ndarray, 
    distance_metric: str
) -> np.ndarray:
    """
    Convert distances to similarity scores.
    
    Args:
        distances: Distance values
        distance_metric: Distance metric (cosine, l2, ip)
        
    Returns:
        Similarity scores
    """
    if distance_metric == "cosine":
        # Convert inner product [-1, 1] to similarity [0, 1]
        return (distances + 1) / 2
    elif distance_metric == "l2":
        # Convert L2 distance to similarity score
        return 1 / (1 + distances)
    else:  # Inner product
        return distances

def safe_write_index(index: faiss.Index, filepath: str) -> bool:
    """
    Safely write a FAISS index to disk using a temporary file.
    
    Args:
        index: FAISS index to save
        filepath: Path to save the index
        
    Returns:
        True if successful
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            faiss.write_index(index, tmp.name)
            os.replace(tmp.name, filepath)
        return True
    except Exception as e:
        logger.error(f"Error writing index to {filepath}: {e}")
        return False