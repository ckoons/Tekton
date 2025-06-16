"""
Utility functions for Qdrant vector store.
"""

import os
import logging
import numpy as np
from typing import Dict, Any, Optional, Tuple, Union

# Configure logger
logger = logging.getLogger(__name__)

def check_qdrant_available():
    """Check if Qdrant client is available."""
    try:
        from qdrant_client import QdrantClient
        return True
    except ImportError:
        return False

def get_qdrant_distance(distance_metric: str) -> Tuple[str, bool]:
    """
    Convert distance metric string to Qdrant distance type.
    
    Args:
        distance_metric: Distance metric (cosine, l2, dot)
        
    Returns:
        Tuple of (qdrant_distance, normalize)
    """
    try:
        from qdrant_client.http.models import Distance
        
        if distance_metric == "cosine":
            return Distance.COSINE, True
        elif distance_metric == "l2":
            return Distance.EUCLID, False
        elif distance_metric == "dot":
            return Distance.DOT, False
        else:
            raise ValueError(f"Unsupported distance metric: {distance_metric}")
    except ImportError:
        logger.warning("Qdrant client not available")
        return "cosine", True

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

def convert_to_score_threshold(distance_metric: str, similarity_threshold: float) -> Optional[Dict[str, float]]:
    """
    Convert similarity threshold to Qdrant score threshold.
    
    Args:
        distance_metric: Distance metric (cosine, l2, dot)
        similarity_threshold: Minimum similarity score threshold
        
    Returns:
        Dictionary with min/max parameters
    """
    try:
        from qdrant_client.http.models import ScoreThreshold
        
        if distance_metric == "cosine":
            return {"min": similarity_threshold}
        elif distance_metric == "l2":
            # L2 distance: smaller is better, convert to maximum threshold
            max_distance = (1.0 / similarity_threshold) - 1.0
            return {"max": max_distance}
        elif distance_metric == "dot":
            return {"min": similarity_threshold}
        else:
            return None
    except ImportError:
        logger.warning("Qdrant client not available")
        return None

def convert_distance_to_similarity(score: float, distance_metric: str) -> float:
    """
    Convert Qdrant score to normalized similarity score.
    
    Args:
        score: Qdrant score
        distance_metric: Distance metric (cosine, l2, dot)
        
    Returns:
        Normalized similarity score
    """
    if distance_metric == "l2":
        # Convert L2 distance to similarity score
        return 1.0 / (1.0 + score)
    else:
        # Cosine and dot scores are already similarity scores
        return score