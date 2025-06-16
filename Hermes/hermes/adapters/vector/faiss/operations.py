"""
FAISS Vector Operations

This module provides vector operations for the FAISS vector adapter.
"""

import time
import numpy as np
import faiss
import logging
from typing import Dict, List, Any, Optional, Union, Tuple

from hermes.adapters.vector.faiss.utils import matches_filter, rebuild_id_mappings
from hermes.adapters.vector.faiss.index import add_to_index, remove_from_index, create_index

# Logger for this module
logger = logging.getLogger("hermes.adapters.vector.faiss.operations")


async def store_vector(
    vectors: Dict[str, Dict[str, Any]],
    index,
    id_to_index: Dict[str, int],
    index_to_id: Dict[int, str],
    id: str,
    vector: List[float],
    metadata: Optional[Dict[str, Any]] = None,
    text: Optional[str] = None,
    vector_dim: int = 1536
) -> tuple[Dict[str, Dict[str, Any]], Dict[str, int], Dict[int, str], bool]:
    """
    Store a vector in the database.
    
    Args:
        vectors: Dictionary of vector data
        index: FAISS index
        id_to_index: ID to index mapping
        index_to_id: Index to ID mapping
        id: Unique identifier for the vector
        vector: The vector embedding
        metadata: Optional metadata to store with the vector
        text: Optional text content associated with the vector
        vector_dim: Vector dimension
        
    Returns:
        Tuple of (vectors, id_to_index, index_to_id, success)
    """
    try:
        # Check vector dimensions
        if len(vector) != vector_dim and vectors:
            logger.error(f"Vector dimension mismatch: expected {vector_dim}, got {len(vector)}")
            return vectors, id_to_index, index_to_id, False
        
        # Store vector data
        vectors[id] = {
            "id": id,
            "vector": vector,
            "metadata": metadata or {},
            "text": text,
            "created_at": time.time()
        }
        
        # Add to index
        id_to_index, index_to_id = await add_to_index(
            index=index,
            vector=vector,
            id_to_index=id_to_index,
            index_to_id=index_to_id,
            vector_id=id
        )
        
        logger.debug(f"Stored vector with ID {id}")
        return vectors, id_to_index, index_to_id, True
        
    except Exception as e:
        logger.error(f"Error storing vector: {e}")
        return vectors, id_to_index, index_to_id, False


async def search_vectors(
    vectors: Dict[str, Dict[str, Any]],
    index,
    id_to_index: Dict[str, int],
    index_to_id: Dict[int, str],
    query_vector: List[float],
    limit: int = 10,
    filter: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search for similar vectors.
    
    Args:
        vectors: Dictionary of vector data
        index: FAISS index
        id_to_index: ID to index mapping
        index_to_id: Index to ID mapping
        query_vector: The query vector
        limit: Maximum number of results
        filter: Optional metadata filter
        
    Returns:
        List of matching vectors with metadata and similarity scores
    """
    try:
        # If no vectors, return empty list
        if not vectors or index.ntotal == 0:
            return []
        
        # Convert query vector to numpy array
        query_np = np.array([query_vector], dtype=np.float32)
        
        # Normalize query vector
        faiss.normalize_L2(query_np)
        
        # Get more results for filtering
        search_limit = limit * 10 if filter else limit
        
        # Search index
        distances, indices = index.search(query_np, min(search_limit, index.ntotal))
        
        # Process results
        results = []
        
        for i, idx in enumerate(indices[0]):
            if idx == -1:  # FAISS sentinel value for no more results
                break
            
            # Get vector ID
            vector_id = index_to_id.get(int(idx))
            if not vector_id or vector_id not in vectors:
                continue
            
            vector = vectors[vector_id]
            
            # Apply filter if provided
            if filter and not matches_filter(vector, filter):
                continue
            
            # Calculate similarity score (convert distance to similarity)
            similarity = 1.0 - float(distances[0][i] / 2.0)
            
            results.append({
                "id": vector_id,
                "metadata": vector.get("metadata", {}),
                "text": vector.get("text"),
                "relevance": similarity,
                "vector": vector.get("vector")
            })
            
            if len(results) >= limit:
                break
        
        logger.debug(f"Found {len(results)} similar vectors")
        return results
        
    except Exception as e:
        logger.error(f"Error searching vectors: {e}")
        return []


async def delete_vectors(
    vectors: Dict[str, Dict[str, Any]],
    index,
    id_to_index: Dict[str, int],
    index_to_id: Dict[int, str],
    id: Optional[str] = None,
    filter: Optional[Dict[str, Any]] = None,
    vector_dim: int = 1536,
    use_gpu: bool = False
) -> tuple[Dict[str, Dict[str, Any]], Dict[str, int], Dict[int, str], bool]:
    """
    Delete vectors from the database.
    
    Args:
        vectors: Dictionary of vector data
        index: FAISS index
        id_to_index: ID to index mapping
        index_to_id: Index to ID mapping
        id: Optional specific vector ID to delete
        filter: Optional metadata filter for bulk deletion
        vector_dim: Vector dimension
        use_gpu: Whether to use GPU acceleration
        
    Returns:
        Tuple of (vectors, id_to_index, index_to_id, success)
    """
    try:
        if id:
            # Delete specific vector
            if id in vectors:
                # Remove from vectors dict
                del vectors[id]
                
                # Remove from index
                id_to_index, index_to_id = await remove_from_index(
                    index=index,
                    id_to_index=id_to_index,
                    index_to_id=index_to_id,
                    vector_id=id
                )
                
                logger.debug(f"Deleted vector with ID {id}")
                return vectors, id_to_index, index_to_id, True
            else:
                logger.warning(f"Vector with ID {id} not found")
                return vectors, id_to_index, index_to_id, False
        
        elif filter:
            # Delete vectors matching filter
            deleted = False
            ids_to_delete = []
            
            for vector_id, vector in vectors.items():
                if matches_filter(vector, filter):
                    ids_to_delete.append(vector_id)
            
            if ids_to_delete:
                # Delete from vectors dict
                for vector_id in ids_to_delete:
                    del vectors[vector_id]
                
                # Rebuild index (more efficient than removing individual IDs)
                index, id_to_index, index_to_id = await create_index(
                    vectors=vectors,
                    vector_dim=vector_dim,
                    use_gpu=use_gpu
                )
                
                deleted = True
            
            if deleted:
                logger.debug(f"Deleted {len(ids_to_delete)} vectors matching filter")
                return vectors, id_to_index, index_to_id, True
            else:
                logger.warning("No vectors matched filter")
                return vectors, id_to_index, index_to_id, False
        
        else:
            # Delete all vectors
            vectors = {}
            index, id_to_index, index_to_id = await create_index(
                vectors={},
                vector_dim=vector_dim,
                use_gpu=use_gpu
            )
            
            logger.debug("Deleted all vectors")
            return vectors, id_to_index, index_to_id, True
        
    except Exception as e:
        logger.error(f"Error deleting vectors: {e}")
        return vectors, id_to_index, index_to_id, False


async def get_vector(
    vectors: Dict[str, Dict[str, Any]],
    id: str
) -> Optional[Dict[str, Any]]:
    """
    Get a specific vector by ID.
    
    Args:
        vectors: Dictionary of vector data
        id: Vector ID to retrieve
        
    Returns:
        Vector with metadata if found, None otherwise
    """
    try:
        if id in vectors:
            vector = vectors[id]
            
            return {
                "id": id,
                "metadata": vector.get("metadata", {}),
                "text": vector.get("text"),
                "vector": vector.get("vector"),
                "created_at": vector.get("created_at")
            }
        else:
            logger.debug(f"Vector with ID {id} not found")
            return None
        
    except Exception as e:
        logger.error(f"Error getting vector: {e}")
        return None


async def list_vectors(
    vectors: Dict[str, Dict[str, Any]],
    limit: int = 100,
    offset: int = 0,
    filter: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    List vectors in the database.
    
    Args:
        vectors: Dictionary of vector data
        limit: Maximum number of results
        offset: Starting offset for pagination
        filter: Optional metadata filter
        
    Returns:
        List of vectors with metadata
    """
    try:
        # Get matching vectors
        matching_vectors = []
        
        for vector_id, vector in vectors.items():
            if filter and not matches_filter(vector, filter):
                continue
            
            matching_vectors.append({
                "id": vector_id,
                "metadata": vector.get("metadata", {}),
                "text": vector.get("text"),
                "created_at": vector.get("created_at")
            })
        
        # Sort by creation time (newest first)
        matching_vectors.sort(key=lambda v: v.get("created_at", 0), reverse=True)
        
        # Apply pagination
        paginated = matching_vectors[offset:offset + limit]
        
        logger.debug(f"Listed {len(paginated)} vectors")
        return paginated
        
    except Exception as e:
        logger.error(f"Error listing vectors: {e}")
        return []