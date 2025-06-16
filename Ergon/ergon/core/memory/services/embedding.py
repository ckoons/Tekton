"""
Embedding service for Ergon memory system.

This module provides functions to generate embeddings for text using
the configured embedding model.
"""

import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Union
import threading

from ergon.utils.config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)

# Check if sentence transformers might be available 
# We'll do the actual import test at runtime to handle NumPy compatibility issues
SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import importlib
    spec = importlib.find_spec("sentence_transformers")
    if spec is not None:
        SENTENCE_TRANSFORMERS_AVAILABLE = True
        logger.info("sentence-transformers package found - will test import at runtime")
except Exception:
    logger.info("sentence-transformers package not found, will use OpenAI or fallback embedding")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Try to import OpenAI
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def simple_text_embedding(text: str, dimension: int = 384) -> List[float]:
    """
    Simple fallback embedding using text hashing and basic features.
    
    This provides a lightweight embedding when sentence-transformers 
    and OpenAI are not available. Not as semantically rich, but allows
    the system to function.
    
    Args:
        text: Input text to embed
        dimension: Embedding dimension (default 384 to match all-MiniLM-L6-v2)
        
    Returns:
        List of floats representing the embedding
    """
    if not text:
        return [0.0] * dimension
    
    # Normalize text
    text = text.lower().strip()
    
    # Create embedding based on multiple text features
    embedding = [0.0] * dimension
    
    # Feature 1: Character-based hash (first quarter of embedding)
    char_hash = hash(text) % (2**32)
    for i in range(dimension // 4):
        embedding[i] = ((char_hash >> (i % 32)) & 1) * 2.0 - 1.0
    
    # Feature 2: Word count and length features (second quarter)
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    
    for i in range(dimension // 4, dimension // 2):
        idx = i - (dimension // 4)
        if idx == 0:
            embedding[i] = min(1.0, word_count / 100.0)  # Normalized word count
        elif idx == 1:
            embedding[i] = min(1.0, char_count / 1000.0)  # Normalized char count
        else:
            # Additional length-based features
            embedding[i] = ((word_count * char_count + idx) % 1000) / 500.0 - 1.0
    
    # Feature 3: Simple word hashing (third quarter)
    for i, word in enumerate(words[:dimension//4]):
        idx = dimension // 2 + i
        if idx < 3 * dimension // 4:
            word_hash = hash(word) % (2**16)
            embedding[idx] = (word_hash / (2**15)) - 1.0
    
    # Feature 4: Bigram features (last quarter)
    bigrams = [text[i:i+2] for i in range(len(text)-1)]
    for i, bigram in enumerate(bigrams[:dimension//4]):
        idx = 3 * dimension // 4 + i
        if idx < dimension:
            bigram_hash = hash(bigram) % (2**16)
            embedding[idx] = (bigram_hash / (2**15)) - 1.0
    
    # Normalize to unit vector
    magnitude = sum(x*x for x in embedding) ** 0.5
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]
    
    return embedding

class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Optional model name to override settings
        """
        self.model_name = model_name or settings.embedding_model
        self.model = None
        self.openai_client = None
        self._lock = threading.RLock()
        
        # Determine embedding approach with graceful degradation
        self.embedding_type = "fallback"  # Default to fallback
        
        if self.model_name.startswith("openai/"):
            if HAS_OPENAI and settings.openai_api_key:
                self.embedding_type = "openai"
                self.openai_model = self.model_name.split("/")[1]
                self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
                self.embedding_dimension = 1536  # Default for OpenAI embeddings
                logger.info(f"Using OpenAI embeddings with model: {self.openai_model}")
            elif not HAS_OPENAI:
                logger.warning("OpenAI package not available, falling back to simple embedding")
                self.embedding_dimension = 384
            elif not settings.openai_api_key:
                logger.warning("OpenAI API key not configured, falling back to simple embedding")
                self.embedding_dimension = 384
        else:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                try:
                    # Import at runtime instead of module level to avoid NumPy conflicts
                    from sentence_transformers import SentenceTransformer
                    self.embedding_type = "sentence_transformers"
                    self.model = SentenceTransformer(self.model_name)
                    self.embedding_dimension = self.model.get_sentence_embedding_dimension()
                    logger.info(f"Using sentence-transformers with model: {self.model_name} (dim={self.embedding_dimension})")
                except Exception as e:
                    logger.warning(f"Error initializing sentence-transformers model: {e}, falling back to simple embedding")
                    self.embedding_type = "fallback"
                    self.embedding_dimension = 384
            else:
                logger.info("sentence-transformers not available, using simple embedding fallback")
                self.embedding_dimension = 384
        
        if self.embedding_type == "fallback":
            logger.info(f"Using simple text embedding fallback (dim={self.embedding_dimension})")
    
    async def embed_text(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text.
        
        Args:
            text: Single text string or list of texts
            
        Returns:
            Embedding vector(s)
        """
        with self._lock:
            try:
                if isinstance(text, str):
                    texts = [text]
                    single_input = True
                else:
                    texts = text
                    single_input = False
                
                # Use the appropriate embedding method
                if self.embedding_type == "openai":
                    response = self.openai_client.embeddings.create(
                        model=self.openai_model,
                        input=texts
                    )
                    embeddings = [item.embedding for item in response.data]
                elif self.embedding_type == "sentence_transformers":
                    embeddings = self.model.encode(texts).tolist()
                else:  # fallback
                    embeddings = [simple_text_embedding(text, self.embedding_dimension) for text in texts]
                
                # Return single embedding or list based on input
                if single_input:
                    return embeddings[0]
                return embeddings
            except Exception as e:
                logger.error(f"Error generating embeddings: {e}")
                # Try fallback embedding if primary method failed
                try:
                    if self.embedding_type != "fallback":
                        logger.info("Attempting fallback embedding after primary method failed")
                        embeddings = [simple_text_embedding(text, self.embedding_dimension) for text in texts]
                        if single_input:
                            return embeddings[0]
                        return embeddings
                except Exception as fallback_error:
                    logger.error(f"Fallback embedding also failed: {fallback_error}")
                
                # Final fallback: return zeros
                if single_input:
                    return [0.0] * self.embedding_dimension
                return [[0.0] * self.embedding_dimension for _ in range(len(texts))]

# Create singleton instance
embedding_service = EmbeddingService()