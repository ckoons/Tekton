"""
Search functionality for FAISS vector store.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple

from tekton.core.storage.vector.faiss.utils import convert_distance_to_similarity

# Configure logger
logger = logging.getLogger(__name__)

class SearchOperations:
    """
    Handles search operations for FAISS vector store.
    """
    
    def __init__(self, index_manager, metadata_manager, normalize, distance_metric):
        """
        Initialize search operations.
        
        Args:
            index_manager: FAISS index manager
            metadata_manager: Metadata manager
            normalize: Whether to normalize vectors
            distance_metric: Distance metric (cosine, l2, ip)
        """
        self.index_manager = index_manager
        self.metadata_manager = metadata_manager
        self.normalize = normalize
        self.distance_metric = distance_metric
    
    async def query(
        self, 
        query_vector: np.ndarray, 
        top_k: int = 10,
        filter_ids: Optional[List[str]] = None,
        similarity_threshold: float = 0.2,
        index_to_id: Dict[int, str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the vector store for similar vectors.
        
        Args:
            query_vector: Query vector
            top_k: Maximum number of results to return
            filter_ids: Optional list of IDs to filter results
            similarity_threshold: Minimum similarity score threshold
            index_to_id: Mapping from index to ID
            
        Returns:
            List of result dictionaries
        """
        if not self.index_manager or not self.index_manager.index:
            logger.error("FAISS index not initialized")
            return []
            
        if self.index_manager.index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return []
            
        # Clone query vector to avoid modifying the original
        vector = query_vector.copy()
        
        # Ensure vector is in the correct format
        if len(vector.shape) == 1:
            vector = vector.reshape(1, -1)
            
        # Ensure vector has the correct dimension
        if vector.shape[1] != self.index_manager.embedding_dim:
            logger.error(f"Query vector dimension mismatch: {vector.shape[1]} != {self.index_manager.embedding_dim}")
            return []
            
        # Normalize if using cosine similarity
        if self.normalize:
            from tekton.core.storage.vector.faiss.utils import normalize_vectors
            vector = normalize_vectors(vector)
            
        try:
            # Perform search
            distances, indices = self.index_manager.search(
                vector, 
                min(top_k * 2, self.index_manager.index.ntotal)
            )
            
            # Convert distances to similarity scores
            distances = convert_distance_to_similarity(distances[0], self.distance_metric)
                
            # Apply similarity threshold and prepare results
            results = []
            for idx, (distance, index) in enumerate(zip(distances, indices[0])):
                # Check if we've collected enough results
                if len(results) >= top_k:
                    break
                    
                # Skip if below threshold
                if distance < similarity_threshold:
                    continue
                    
                # Skip if index is invalid
                if index < 0 or index >= self.index_manager.index.ntotal or index not in index_to_id:
                    continue
                    
                # Get vector ID
                vector_id = index_to_id[index]
                
                # Skip if filtered
                if filter_ids and vector_id not in filter_ids:
                    continue
                    
                # Create result
                result = {
                    "id": vector_id,
                    "score": float(distance),
                    "vector_index": int(index)
                }
                
                # Add metadata if available
                metadata = self.metadata_manager.load_vector_metadata(vector_id)
                if metadata:
                    result.update(metadata)
                        
                results.append(result)
                
            return results
            
        except Exception as e:
            logger.error(f"Error querying FAISS index: {e}")
            return []