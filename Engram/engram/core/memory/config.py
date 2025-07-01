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

# Get vector DB preference from Tekton configuration system
try:
    from shared.utils.global_config import GlobalConfig
    config = GlobalConfig.get_instance()
    vector_config = config.config.vector
    PREFERRED_VECTOR_DB = vector_config.vector_db.lower()
    VECTOR_CPU_ONLY = vector_config.cpu_only
    VECTOR_GPU_ENABLED = vector_config.gpu_enabled
except Exception as e:
    logger.warning(f"Failed to load vector config from GlobalConfig: {e}, using defaults")
    PREFERRED_VECTOR_DB = 'auto'
    VECTOR_CPU_ONLY = False
    VECTOR_GPU_ENABLED = True

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
    
    # Determine which vector DB to use
    selected_db = PREFERRED_VECTOR_DB
    
    # If auto mode, detect best vector DB
    if selected_db == "auto":
        try:
            from utils.detect_best_vector_db import get_vector_db_info
            best_db, reason, deps, hw = get_vector_db_info()
            selected_db = best_db if best_db != "none" else "faiss"
            logger.info(f"Auto-detected vector DB: {selected_db} ({reason})")
        except Exception as e:
            logger.warning(f"Auto-detection failed: {e}, defaulting to FAISS")
            selected_db = "faiss"
    
    # Try to import the selected vector DB
    vector_model = None
    
    # First, try to initialize the embedding model (shared across all vector DBs)
    try:
        from sentence_transformers import SentenceTransformer
        model_name = "all-MiniLM-L6-v2"  # Small, fast model with good performance
        vector_model = SentenceTransformer(model_name)
        vector_db_info["model"] = model_name
        vector_db_info["model_dim"] = vector_model.get_sentence_embedding_dimension()
    except ImportError:
        logger.warning("SentenceTransformer not found. Vector embedding will not be available")
    
    # Initialize the selected vector DB
    if selected_db == "chromadb":
        try:
            import chromadb
            HAS_VECTOR_DB = True
            VECTOR_DB_NAME = "chromadb"
            VECTOR_DB_VERSION = getattr(chromadb, "__version__", "unknown")
            
            logger.info(f"Vector storage library found: {VECTOR_DB_NAME} {VECTOR_DB_VERSION}")
            logger.info("Using ChromaDB for vector-based memory implementation")
            
            vector_db_info["available"] = True
            vector_db_info["name"] = VECTOR_DB_NAME
            vector_db_info["version"] = VECTOR_DB_VERSION
            
            return True, vector_db_info, vector_model
        except ImportError:
            logger.warning("ChromaDB not found, falling back to FAISS")
            selected_db = "faiss"
    
    elif selected_db == "qdrant":
        try:
            import qdrant_client
            HAS_VECTOR_DB = True
            VECTOR_DB_NAME = "qdrant"
            VECTOR_DB_VERSION = getattr(qdrant_client, "__version__", "unknown")
            
            logger.info(f"Vector storage library found: {VECTOR_DB_NAME} {VECTOR_DB_VERSION}")
            logger.info("Using Qdrant for vector-based memory implementation")
            
            vector_db_info["available"] = True
            vector_db_info["name"] = VECTOR_DB_NAME
            vector_db_info["version"] = VECTOR_DB_VERSION
            
            return True, vector_db_info, vector_model
        except ImportError:
            logger.warning("Qdrant not found, falling back to FAISS")
            selected_db = "faiss"
    
    elif selected_db == "lancedb":
        try:
            import lancedb
            HAS_VECTOR_DB = True
            VECTOR_DB_NAME = "lancedb"
            VECTOR_DB_VERSION = getattr(lancedb, "__version__", "unknown")
            
            logger.info(f"Vector storage library found: {VECTOR_DB_NAME} {VECTOR_DB_VERSION}")
            logger.info("Using LanceDB for vector-based memory implementation")
            
            vector_db_info["available"] = True
            vector_db_info["name"] = VECTOR_DB_NAME
            vector_db_info["version"] = VECTOR_DB_VERSION
            
            return True, vector_db_info, vector_model
        except ImportError:
            logger.warning("LanceDB not found, falling back to FAISS")
            selected_db = "faiss"
    
    # Default to FAISS or use it as fallback
    if selected_db == "faiss" or not HAS_VECTOR_DB:
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
            logger.info("Using FAISS for vector-based memory implementation")
            
            # Update info dictionary
            vector_db_info["available"] = True
            vector_db_info["name"] = VECTOR_DB_NAME
            vector_db_info["version"] = VECTOR_DB_VERSION
            
            return True, vector_db_info, vector_model
        except ImportError:
            HAS_VECTOR_DB = False
            logger.warning("No vector database found, using fallback file-based implementation")
            logger.info("Memory will still work but without vector search capabilities")
            return False, vector_db_info, None