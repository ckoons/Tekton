#!/usr/bin/env python3
"""
Memory Service Configuration

This module manages configuration for the memory service,
including vector database dependencies and fallback mode.
"""

import logging
import os
from typing import Optional, Tuple, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.memory")

# Vector database configuration
HAS_VECTOR_DB = False
VECTOR_DB_NAME = None
VECTOR_DB_VERSION = None

# Check if fallback mode is forced (set by environment variable)
USE_FALLBACK = os.environ.get('ENGRAM_USE_FALLBACK', '').lower() in ('1', 'true', 'yes')

def initialize_vector_db() -> Tuple[bool, Optional[Dict[str, Any]], Optional[Any]]:
    """
    Initialize vector database components if available.
    
    Returns:
        Tuple containing:
        - Boolean indicating if vector DB is available
        - Dictionary with vector DB information
        - Vector model for embeddings (or None if unavailable)
    """
    global HAS_VECTOR_DB, VECTOR_DB_NAME, VECTOR_DB_VERSION
    
    vector_db_info = {
        "available": False,
        "name": None,
        "version": None
    }
    vector_model = None
    
    if USE_FALLBACK:
        # Skip vector DB imports entirely
        logger.info("Fallback mode requested by environment variable")
        logger.info("Using file-based memory implementation (no vector search)")
        return False, vector_db_info, None
    
    # Import FAISS for vector-based memory
    try:
        import faiss
        from engram.core.vector_store import VectorStore, SimpleEmbedding
        
        HAS_VECTOR_DB = True
        VECTOR_DB_NAME = "faiss"
        
        # Get version if available
        try:
            VECTOR_DB_VERSION = faiss.__version__
        except AttributeError:
            VECTOR_DB_VERSION = "unknown"
        
        logger.info(f"Vector storage library found: {VECTOR_DB_NAME} {VECTOR_DB_VERSION}")
        logger.info("Using vector-based memory implementation with FAISS")
        
        # Update info dictionary
        vector_db_info["available"] = True
        vector_db_info["name"] = VECTOR_DB_NAME
        vector_db_info["version"] = VECTOR_DB_VERSION
        
        # Try to initialize the vector model
        try:
            from sentence_transformers import SentenceTransformer
            model_name = "all-MiniLM-L6-v2"  # Small, fast model with good performance
            vector_model = SentenceTransformer(model_name)
            vector_db_info["model"] = model_name
            vector_db_info["model_dim"] = vector_model.get_sentence_embedding_dimension()
        except ImportError:
            logger.warning("SentenceTransformer not found. Vector embedding will not be available")
        
        return True, vector_db_info, vector_model
    except ImportError:
        HAS_VECTOR_DB = False
        logger.warning("FAISS not found, using fallback file-based implementation")
        logger.info("Memory will still work but without vector search capabilities")
        return False, vector_db_info, None