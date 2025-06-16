"""
FAISS index management functionality.
"""

import os
import logging
import numpy as np
from typing import Dict, Any, Optional, List

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from tekton.core.storage.vector.faiss.utils import gpu_available, safe_write_index

# Configure logger
logger = logging.getLogger(__name__)

class FAISSIndexManager:
    """
    Manages FAISS index operations including creation, loading, and search.
    """
    
    def __init__(
        self,
        embedding_dim: int,
        index_type: str,
        faiss_metric: int,
        use_gpu: bool = True,
        index_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the FAISS index manager.
        
        Args:
            embedding_dim: Dimension of vector embeddings
            index_type: FAISS index type (Flat, IVF, HNSW)
            faiss_metric: FAISS metric type
            use_gpu: Whether to use GPU acceleration if available
            index_config: Configuration parameters for the index
        """
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.faiss_metric = faiss_metric
        self.use_gpu = use_gpu
        self.index_config = index_config or {
            "Flat": {},  # No special parameters for flat index
            "IVF": {
                "nlist": 100,  # Number of clusters
                "nprobe": 10   # Number of clusters to search
            },
            "HNSW": {
                "M": 32,       # Number of neighbors
                "efConstruction": 200,  # Size of dynamic list during construction
                "efSearch": 64 # Size of dynamic list during search
            }
        }
        
        self.index = None
        
    def create_index(self, train_data: Optional[np.ndarray] = None) -> faiss.Index:
        """
        Create a new FAISS index.
        
        Args:
            train_data: Optional training data for IVF indices
            
        Returns:
            FAISS index
        """
        # Create a new index based on the specified type
        if self.index_type == "Flat":
            index = faiss.IndexFlat(self.embedding_dim, self.faiss_metric)
        elif self.index_type == "IVF":
            quantizer = faiss.IndexFlat(self.embedding_dim, self.faiss_metric)
            index = faiss.IndexIVFFlat(
                quantizer, 
                self.embedding_dim, 
                self.index_config["IVF"]["nlist"],
                self.faiss_metric
            )
            
            # Train IVF index if data is provided
            if train_data is not None and train_data.shape[0] > 0:
                index.train(train_data)
                
            # Set search parameters
            index.nprobe = self.index_config["IVF"]["nprobe"]
            
        elif self.index_type == "HNSW":
            index = faiss.IndexHNSWFlat(
                self.embedding_dim, 
                self.index_config["HNSW"]["M"],
                self.faiss_metric
            )
            index.hnsw.efConstruction = self.index_config["HNSW"]["efConstruction"]
            index.hnsw.efSearch = self.index_config["HNSW"]["efSearch"]
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")
        
        # Move to GPU if requested and available
        if self.use_gpu and gpu_available():
            try:
                res = faiss.StandardGpuResources()
                index = faiss.index_cpu_to_gpu(res, 0, index)
                logger.info("Using GPU for FAISS index")
            except Exception as e:
                logger.warning(f"Failed to use GPU for FAISS: {e}")
        
        self.index = index
        return index
    
    def load_index(self, filepath: str) -> faiss.Index:
        """
        Load a FAISS index from disk.
        
        Args:
            filepath: Path to the index file
            
        Returns:
            FAISS index
        """
        try:
            # Load the index
            index = faiss.read_index(filepath)
            
            # Move to GPU if requested and available
            if self.use_gpu and gpu_available():
                try:
                    res = faiss.StandardGpuResources()
                    index = faiss.index_cpu_to_gpu(res, 0, index)
                    logger.info("Using GPU for FAISS index")
                except Exception as e:
                    logger.warning(f"Failed to use GPU for FAISS: {e}")
            
            # Set search parameters
            if self.index_type == "IVF" and hasattr(index, 'nprobe'):
                index.nprobe = self.index_config["IVF"]["nprobe"]
            elif self.index_type == "HNSW" and hasattr(index, 'hnsw'):
                index.hnsw.efSearch = self.index_config["HNSW"]["efSearch"]
            
            self.index = index
            return index
            
        except Exception as e:
            logger.error(f"Error loading index from {filepath}: {e}")
            # Create a new index if loading fails
            return self.create_index()
    
    def save_index(self, filepath: str) -> bool:
        """
        Save the index to disk.
        
        Args:
            filepath: Path to save the index
            
        Returns:
            True if successful
        """
        if self.index is None:
            logger.warning("No index to save")
            return False
        
        # Prepare index for saving (convert to CPU if needed)
        index_to_save = self.index
        if self.use_gpu and hasattr(self.index, "device_id"):
            index_to_save = faiss.index_gpu_to_cpu(self.index)
        
        return safe_write_index(index_to_save, filepath)
    
    def search(
        self, 
        query_vector: np.ndarray, 
        k: int
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Search the index for similar vectors.
        
        Args:
            query_vector: Query vector(s)
            k: Number of results to return
            
        Returns:
            Tuple of (distances, indices)
        """
        if self.index is None:
            raise ValueError("Index not initialized")
        
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)
        
        return self.index.search(query_vector, k)
    
    def add_vectors(self, vectors: np.ndarray) -> bool:
        """
        Add vectors to the index.
        
        Args:
            vectors: Vectors to add
            
        Returns:
            True if successful
        """
        if self.index is None:
            raise ValueError("Index not initialized")
        
        try:
            self.index.add(vectors)
            return True
        except Exception as e:
            logger.error(f"Error adding vectors to index: {e}")
            return False
    
    def replace_vector(self, vector: np.ndarray, idx: int) -> bool:
        """
        Replace a vector in the index.
        Only supported for Flat indices.
        
        Args:
            vector: New vector
            idx: Index of vector to replace
            
        Returns:
            True if successful
        """
        if self.index is None:
            raise ValueError("Index not initialized")
        
        # Only flat indices support direct replacement
        if not isinstance(self.index, faiss.IndexFlat) and not hasattr(self.index, "replace_vector"):
            return False
        
        try:
            if len(vector.shape) == 1:
                vector = vector.reshape(1, -1)
            
            if hasattr(self.index, "replace_vector"):
                self.index.replace_vector(vector[0], idx)
            else:
                # Manual replacement for flat index
                storage = self.index.get_xb()
                storage[idx] = vector[0]
            
            return True
        except Exception as e:
            logger.error(f"Error replacing vector at index {idx}: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the configuration of the index.
        
        Returns:
            Dictionary with index configuration
        """
        config = {
            "index_type": self.index_type,
            "embedding_dim": self.embedding_dim,
            "faiss_metric": self.faiss_metric,
            "use_gpu": self.use_gpu,
            "gpu_available": gpu_available(),
            "parameters": self.index_config.get(self.index_type, {})
        }
        
        # Add additional info
        if self.index is not None:
            config["ntotal"] = self.index.ntotal
            
            # Add index-specific info
            if self.index_type == "IVF" and hasattr(self.index, "nprobe"):
                config["nprobe"] = self.index.nprobe
            elif self.index_type == "HNSW" and hasattr(self.index, "hnsw"):
                config["efSearch"] = self.index.hnsw.efSearch
        
        return config