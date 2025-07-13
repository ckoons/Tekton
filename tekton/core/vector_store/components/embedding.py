"""Embedding Engine Component for Vector Store.

This module provides text embedding functionality for the Vector Store.
"""

import logging
import numpy as np
import faiss
from typing import List, Dict, Any, Optional, Union

# Configure logger
logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """
    Embedding engine for generating text embeddings with support for
    batch processing and GPU acceleration.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        normalize: bool = True,
        use_gpu: bool = True
    ):
        """Initialize the embedding engine.
        
        Args:
            model_name: Name of the embedding model
            dimension: Embedding dimension
            normalize: Whether to normalize embeddings
            use_gpu: Whether to use GPU acceleration
        """
        self.model_name = model_name
        self.dimension = dimension
        self.normalize = normalize
        self.use_gpu = use_gpu
        self.model = None
        self.gpu_available = False
        
        # Load model
        self._load_model()
        
    def _load_model(self):
        """Load the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Load embedding model
            self.model = SentenceTransformer(self.model_name)
            
            # Check if CUDA is available for GPU acceleration
            if self.use_gpu:
                try:
                    import torch
                    self.gpu_available = torch.cuda.is_available()
                    if self.gpu_available and hasattr(self.model, "cuda"):
                        self.model = self.model.cuda()
                        logger.info("Using GPU acceleration for embeddings")
                except Exception as e:
                    logger.warning(f"Failed to use GPU for embeddings: {e}")
                    
            logger.info(f"Loaded embedding model {self.model_name} with dimension {self.dimension}")
            
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
            
    def encode(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """Encode texts to embeddings.
        
        Args:
            texts: Text or list of texts to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings
        """
        if self.model is None:
            raise ValueError("Embedding model not loaded")
            
        # Handle single text
        if isinstance(texts, str):
            texts = [texts]
            
        # Process in batches if there are many texts
        if len(texts) > batch_size:
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                batch_embeddings = self.model.encode(batch)
                all_embeddings.append(batch_embeddings)
            embeddings = np.vstack(all_embeddings)
        else:
            embeddings = self.model.encode(texts)
        
        # Normalize embeddings if requested
        if self.normalize:
            faiss.normalize_L2(embeddings)
        
        return embeddings
        
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score (0-1 range)
        """
        # Ensure embeddings are normalized
        if self.normalize:
            norm1 = np.linalg.norm(embedding1)
            if norm1 > 0:
                embedding1 = embedding1 / norm1
                
            norm2 = np.linalg.norm(embedding2)
            if norm2 > 0:
                embedding2 = embedding2 / norm2
        
        # Calculate cosine similarity
        return float(np.dot(embedding1, embedding2))
        
    def batch_similarity(self, query_embedding: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
        """Calculate similarities between query and multiple embeddings.
        
        Args:
            query_embedding: Query embedding
            embeddings: Matrix of embeddings to compare against
            
        Returns:
            Array of similarity scores
        """
        # Ensure query embedding is normalized
        if self.normalize:
            norm = np.linalg.norm(query_embedding)
            if norm > 0:
                query_embedding = query_embedding / norm
        
        # Calculate similarities (dot product for normalized vectors = cosine similarity)
        return np.dot(embeddings, query_embedding)
        
    def get_info(self) -> Dict[str, Any]:
        """Get information about the embedding engine.
        
        Returns:
            Dictionary with embedding engine information
        """
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "normalize": self.normalize,
            "gpu_available": self.gpu_available
        }