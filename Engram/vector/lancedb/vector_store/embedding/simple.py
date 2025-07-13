"""
Simple embedding generator for vector store.

This module provides a simple embedding generator using a TF-IDF like approach,
intended for use when more advanced embedding models are not available.
"""

import logging
import numpy as np
import re
from typing import List, Dict, Union

# Configure logging
logger = logging.getLogger("lancedb_vector_store.embedding")


class SimpleEmbedding:
    """
    A simple embedding generator using TF-IDF like approach.
    This is NOT meant to be a production-grade embedding system,
    but rather a demonstration of embedding generation without
    dependencies on libraries that may have NumPy version conflicts.
    """
    
    def __init__(self, vector_size: int = 128, seed: int = 42):
        """
        Initialize the simple embedding generator
        
        Args:
            vector_size: Dimension of the generated embeddings
            seed: Random seed for reproducibility
        """
        self.vector_size = vector_size
        self.seed = seed
        self.vocab: Dict[str, np.ndarray] = {}
        self.rng = np.random.RandomState(seed)
        
    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization by splitting on non-alphanumeric characters
        and converting to lowercase
        """
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def _get_or_create_token_vector(self, token: str) -> np.ndarray:
        """Generate a stable vector for a token"""
        if token not in self.vocab:
            # Generate a stable random vector for this token
            # We use the hash of the token to seed the random generator
            # This ensures the same token always gets the same vector
            token_hash = hash(token) % 2**32
            token_rng = np.random.RandomState(token_hash)
            self.vocab[token] = token_rng.randn(self.vector_size).astype(np.float32)
        return self.vocab[token]
    
    def encode(self, texts: Union[str, List[str]], 
            normalize: bool = True) -> np.ndarray:
        """
        Encode text(s) into fixed-size vectors using a simple TF-IDF
        like approach with random vectors for words.
        
        Args:
            texts: Text or list of texts to encode
            normalize: Whether to normalize the vectors to unit length
            
        Returns:
            Numpy array of embeddings with shape (n_texts, vector_size)
        """
        if isinstance(texts, str):
            texts = [texts]
            
        result = np.zeros((len(texts), self.vector_size), dtype=np.float32)
        
        for i, text in enumerate(texts):
            tokens = self._tokenize(text)
            if not tokens:
                continue
                
            # Create the embedding by averaging token vectors
            token_vectors = np.stack([self._get_or_create_token_vector(t) for t in tokens])
            
            # Apply TF component (token frequency)
            token_counts = {}
            for token in tokens:
                token_counts[token] = token_counts.get(token, 0) + 1
            
            # Calculate embedding as weighted average of token vectors
            embedding = np.zeros(self.vector_size, dtype=np.float32)
            for token, count in token_counts.items():
                # Higher weight for tokens that appear less frequently in this document
                # (similar to TF-IDF concept, but very simplified)
                weight = 1.0 / (1.0 + np.log(count))
                embedding += weight * self._get_or_create_token_vector(token)
            
            # Store the result
            result[i] = embedding
        
        # Normalize if requested
        if normalize:
            norms = np.linalg.norm(result, axis=1, keepdims=True)
            # Avoid division by zero
            norms = np.maximum(norms, 1e-10)
            result = result / norms
            
        return result
    
    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))