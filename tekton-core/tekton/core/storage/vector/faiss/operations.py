"""
Vector operations for FAISS vector store.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set

from tekton.core.storage.vector.faiss.utils import normalize_vectors

# Configure logger
logger = logging.getLogger(__name__)

class VectorOperations:
    """
    Handles vector operations for FAISS vector store.
    """
    
    def __init__(self, index_manager, metadata_manager, normalize):
        """
        Initialize vector operations.
        
        Args:
            index_manager: FAISS index manager
            metadata_manager: Metadata manager
            normalize: Whether to normalize vectors
        """
        self.index_manager = index_manager
        self.metadata_manager = metadata_manager
        self.normalize = normalize
    
    async def upsert(
        self, 
        data: Dict[str, Dict[str, Any]], 
        id_to_index: Dict[str, int], 
        index_to_id: Dict[int, str]
    ) -> Tuple[List[str], List[str]]:
        """
        Insert or update vectors.
        
        Args:
            data: Dictionary mapping IDs to vector data and metadata
            id_to_index: Mapping from ID to index
            index_to_id: Mapping from index to ID
            
        Returns:
            Tuple of (updated IDs, added IDs)
        """
        if not self.index_manager or not self.index_manager.index:
            logger.error("FAISS index not initialized")
            raise RuntimeError("FAISS index not initialized")
            
        # Collect vectors and IDs
        updated_ids = []
        added_ids = []
        updates = []
        new_vectors = []
        vectors = []
        
        for vector_id, item in data.items():
            if "vector" not in item:
                logger.error(f"Vector missing for ID {vector_id}")
                continue
                
            vector = item["vector"]
            
            # Ensure vector is a numpy array
            if not isinstance(vector, np.ndarray):
                try:
                    vector = np.array(vector, dtype=np.float32)
                except:
                    logger.error(f"Invalid vector format for ID {vector_id}")
                    continue
                    
            # Ensure vector has the correct dimension
            if len(vector.shape) == 1:
                if vector.shape[0] != self.index_manager.embedding_dim:
                    logger.error(
                        f"Vector dimension mismatch: {vector.shape[0]} != {self.index_manager.embedding_dim}"
                    )
                    continue
            else:
                logger.error(f"Invalid vector shape: {vector.shape}")
                continue
                
            # Check if this is an update or new vector
            if vector_id in id_to_index:
                # Update existing vector
                updates.append((vector_id, vector, item.get("metadata", {})))
                updated_ids.append(vector_id)
            else:
                # New vector
                vectors.append(vector)
                new_vectors.append((vector_id, vector, item.get("metadata", {})))
                added_ids.append(vector_id)
        
        # Process updates
        await self._process_updates(updates, id_to_index)
            
        # Process new vectors
        if vectors:
            start_idx = await self._add_new_vectors(vectors, new_vectors, id_to_index, index_to_id)
            
        return updated_ids, added_ids
        
    async def _process_updates(self, updates: List[Tuple[str, np.ndarray, Dict[str, Any]]], id_to_index: Dict[str, int]) -> None:
        """Process vector updates."""
        for vector_id, vector, metadata in updates:
            index = id_to_index[vector_id]
            
            # Normalize if using cosine similarity
            if self.normalize:
                vector = normalize_vectors(vector)
            
            # Replace vector
            if self.index_manager.replace_vector(vector, index):
                # Save metadata
                if metadata:
                    self.metadata_manager.save_vector_metadata(vector_id, metadata)
            else:
                # Cannot replace directly
                logger.warning(f"Could not replace vector for {vector_id}")
                
    async def _add_new_vectors(
        self, 
        vectors: List[np.ndarray], 
        new_vectors: List[Tuple[str, np.ndarray, Dict[str, Any]]],
        id_to_index: Dict[str, int],
        index_to_id: Dict[int, str]
    ) -> int:
        """Add new vectors to the index."""
        vectors_array = np.vstack(vectors)
        
        # Normalize if using cosine similarity
        if self.normalize:
            vectors_array = normalize_vectors(vectors_array)
        
        # Get starting index
        start_idx = self.index_manager.index.ntotal
        
        # Add vectors to index
        self.index_manager.add_vectors(vectors_array)
        
        # Update mappings
        for i, (vector_id, _, metadata) in enumerate(new_vectors):
            index = start_idx + i
            id_to_index[vector_id] = index
            index_to_id[index] = vector_id
            
            # Save metadata
            if metadata:
                self.metadata_manager.save_vector_metadata(vector_id, metadata)
                
        return start_idx
    
    async def delete(
        self, 
        ids: List[str], 
        id_to_index: Dict[str, int], 
        index_to_id: Dict[int, str]
    ) -> None:
        """
        Delete vectors by IDs.
        
        Args:
            ids: Vector IDs to delete
            id_to_index: Mapping from ID to index
            index_to_id: Mapping from index to ID
        """
        if not self.index_manager or not self.index_manager.index:
            logger.error("FAISS index not initialized")
            raise RuntimeError("FAISS index not initialized")
            
        if not ids:
            return
            
        # Get indices to remove
        indices_to_remove = set()
        for vector_id in ids:
            if vector_id in id_to_index:
                indices_to_remove.add(id_to_index[vector_id])
                
        if not indices_to_remove:
            return  # Nothing to remove
        
        # Get all vectors except the ones to remove
        if self.index_manager.index.ntotal <= len(indices_to_remove):
            # All vectors are being deleted, just create a new index
            self.index_manager.create_index()
            id_to_index.clear()
            index_to_id.clear()
        else:
            # Need to rebuild the index with remaining vectors
            await self._rebuild_index_without_indices(indices_to_remove, id_to_index, index_to_id)
        
        # Delete metadata files
        for vector_id in ids:
            self.metadata_manager.delete_vector_metadata(vector_id)
    
    async def _rebuild_index_without_indices(
        self, 
        indices_to_remove: Set[int],
        id_to_index: Dict[str, int],
        index_to_id: Dict[int, str]
    ) -> None:
        """
        Rebuild the index without the specified indices.
        
        Args:
            indices_to_remove: Set of indices to remove
            id_to_index: Mapping from ID to index
            index_to_id: Mapping from index to ID
        """
        try:
            import faiss
            
            # Extract vectors to keep
            all_indices = set(range(self.index_manager.index.ntotal))
            indices_to_keep = sorted(list(all_indices - indices_to_remove))
            
            # Create a selector to keep specific indices
            selector = faiss.IDSelectorBatch(len(indices_to_keep), np.array(indices_to_keep, dtype=np.int64))
            
            # Create new index with same parameters
            new_index_manager = type(self.index_manager)(
                embedding_dim=self.index_manager.embedding_dim,
                index_type=self.index_manager.index_type,
                faiss_metric=self.index_manager.faiss_metric,
                use_gpu=self.index_manager.use_gpu,
                index_config=self.index_manager.index_config
            )
            new_index_manager.create_index()
            
            # Copy subset of vectors
            faiss.copy_index_subset(self.index_manager.index, new_index_manager.index, selector)
            
            # Update mappings
            new_id_to_index = {}
            new_index_to_id = {}
            
            for new_idx, old_idx in enumerate(indices_to_keep):
                if old_idx in index_to_id:
                    vector_id = index_to_id[old_idx]
                    new_id_to_index[vector_id] = new_idx
                    new_index_to_id[new_idx] = vector_id
            
            # Replace old index and mappings
            self.index_manager.index = new_index_manager.index
            id_to_index.clear()
            id_to_index.update(new_id_to_index)
            index_to_id.clear()
            index_to_id.update(new_index_to_id)
            
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            raise