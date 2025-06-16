"""
FAISS Index Management

This module provides functions for creating and managing FAISS indexes.
"""

import numpy as np
import faiss
import logging
from typing import Dict, Any, Optional, List

# Logger for this module
logger = logging.getLogger("hermes.adapters.vector.faiss.index")


async def create_index(
    vectors: Dict[str, Dict[str, Any]],
    vector_dim: int,
    use_gpu: bool = False,
    id_to_index: Optional[Dict[str, int]] = None,
    index_to_id: Optional[Dict[int, str]] = None
) -> tuple[faiss.Index, Dict[str, int], Dict[int, str]]:
    """
    Create a FAISS search index.
    
    Args:
        vectors: Dictionary of vector data
        vector_dim: Vector dimension
        use_gpu: Whether to use GPU acceleration
        id_to_index: Optional existing ID to index mapping
        index_to_id: Optional existing index to ID mapping
        
    Returns:
        Tuple of (index, id_to_index, index_to_id)
    """
    try:
        # Initialize mappings if not provided
        if id_to_index is None:
            id_to_index = {}
        if index_to_id is None:
            index_to_id = {}
        
        # Create index
        if use_gpu:
            # Use IVF index for large datasets on GPU
            if len(vectors) > 1000:
                # Number of centroids - rule of thumb: sqrt(n) * 4
                n_centroids = max(4, min(1024, int(np.sqrt(len(vectors)) * 4)))
                
                # Create CPU index first
                quantizer = faiss.IndexFlatIP(vector_dim)
                index = faiss.IndexIVFFlat(quantizer, vector_dim, n_centroids, faiss.METRIC_INNER_PRODUCT)
                
                # Only train if we have vectors
                if vectors:
                    # Extract vectors for training
                    train_vectors = np.array([v["vector"] for v in vectors.values()], dtype=np.float32)
                    faiss.normalize_L2(train_vectors)
                    
                    # Train index
                    index.train(train_vectors)
                
                # Convert to GPU
                res = faiss.StandardGpuResources()
                index = faiss.index_cpu_to_gpu(res, 0, index)
            else:
                # Use flat index for small datasets
                res = faiss.StandardGpuResources()
                index = faiss.index_cpu_to_gpu(res, 0, faiss.IndexFlatIP(vector_dim))
        else:
            # Use IVF index for large datasets on CPU
            if len(vectors) > 10000:
                # Number of centroids - rule of thumb: sqrt(n) * 4
                n_centroids = max(4, min(1024, int(np.sqrt(len(vectors)) * 4)))
                
                quantizer = faiss.IndexFlatIP(vector_dim)
                index = faiss.IndexIVFFlat(quantizer, vector_dim, n_centroids, faiss.METRIC_INNER_PRODUCT)
                
                # Only train if we have vectors
                if vectors:
                    # Extract vectors for training
                    train_vectors = np.array([v["vector"] for v in vectors.values()], dtype=np.float32)
                    faiss.normalize_L2(train_vectors)
                    
                    # Train index
                    index.train(train_vectors)
            else:
                # Use flat index for small/medium datasets
                index = faiss.IndexFlatIP(vector_dim)
        
        # Add vectors to index
        if vectors:
            # Extract vectors and IDs
            all_vectors = []
            all_ids = []
            
            for i, (vector_id, vector_data) in enumerate(vectors.items()):
                all_vectors.append(vector_data["vector"])
                all_ids.append(vector_id)
                
                # Update mappings
                id_to_index[vector_id] = i
                index_to_id[i] = vector_id
            
            # Convert to numpy and normalize
            vectors_np = np.array(all_vectors, dtype=np.float32)
            faiss.normalize_L2(vectors_np)
            
            # Add to index
            index.add(vectors_np)
        
        logger.debug(f"Built FAISS search index with {len(vectors)} vectors")
        return index, id_to_index, index_to_id
        
    except Exception as e:
        logger.error(f"Error building FAISS index: {e}")
        # Create empty index
        index = faiss.IndexFlatIP(vector_dim)
        return index, {}, {}


async def add_to_index(
    index: faiss.Index,
    vector: List[float],
    id_to_index: Dict[str, int],
    index_to_id: Dict[int, str],
    vector_id: str
) -> tuple[Dict[str, int], Dict[int, str]]:
    """
    Add a vector to the index.
    
    Args:
        index: FAISS index
        vector: Vector to add
        id_to_index: ID to index mapping
        index_to_id: Index to ID mapping
        vector_id: ID of the vector
        
    Returns:
        Updated (id_to_index, index_to_id) mappings
    """
    try:
        # Convert vector to numpy array
        vector_np = np.array([vector], dtype=np.float32)
        
        # Normalize vector
        faiss.normalize_L2(vector_np)
        
        # If vector already in index, remove it first
        if vector_id in id_to_index:
            idx = id_to_index[vector_id]
            index.remove_ids(np.array([idx], dtype=np.int64))
        
        # Add vector to index
        idx = len(id_to_index) if vector_id not in id_to_index else id_to_index[vector_id]
        index.add(vector_np)
        
        # Update mappings
        id_to_index[vector_id] = idx
        index_to_id[idx] = vector_id
        
        return id_to_index, index_to_id
        
    except Exception as e:
        logger.error(f"Error adding vector to index: {e}")
        return id_to_index, index_to_id


async def remove_from_index(
    index: faiss.Index,
    id_to_index: Dict[str, int],
    index_to_id: Dict[int, str],
    vector_id: str
) -> tuple[Dict[str, int], Dict[int, str]]:
    """
    Remove a vector from the index.
    
    Args:
        index: FAISS index
        id_to_index: ID to index mapping
        index_to_id: Index to ID mapping
        vector_id: ID of the vector to remove
        
    Returns:
        Updated (id_to_index, index_to_id) mappings
    """
    try:
        if vector_id in id_to_index:
            idx = id_to_index[vector_id]
            index.remove_ids(np.array([idx], dtype=np.int64))
            
            # Remove from mappings
            del index_to_id[idx]
            del id_to_index[vector_id]
        
        return id_to_index, index_to_id
        
    except Exception as e:
        logger.error(f"Error removing vector from index: {e}")
        return id_to_index, index_to_id