"""FAISS Index Component for Vector Store.

This module provides the core FAISS index functionality for the Vector Store.
"""

import os
import logging
import numpy as np
import faiss
from typing import Dict, Any, Optional, Tuple, List

# Configure logger
logger = logging.getLogger(__name__)


class FAISSIndex:
    """
    Core FAISS index implementation with support for different index types,
    memory mapping and GPU acceleration.
    """

    def __init__(
        self,
        dimension: int,
        index_type: str = "Flat",
        distance_metric: str = "cosine",
        use_mmap: bool = True,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the FAISS index.
        
        Args:
            dimension: Embedding dimension
            index_type: FAISS index type (Flat, IVF, HNSW)
            distance_metric: Distance metric for comparison
            use_mmap: Whether to use memory-mapped indices
            config: Optional configuration parameters
        """
        self.dimension = dimension
        self.index_type = index_type
        self.distance_metric = distance_metric
        self.use_mmap = use_mmap
        
        # Default index configuration
        self.index_config = {
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
        
        # Update with provided config if available
        if config:
            for key, value in config.items():
                if key in self.index_config:
                    self.index_config[key].update(value)
                    
        # Check if CUDA is available for GPU acceleration
        self.gpu_available = False
        try:
            import torch
            self.gpu_available = torch.cuda.is_available()
            if self.gpu_available:
                self.res = faiss.StandardGpuResources()
                logger.info("GPU acceleration available for FAISS")
        except ImportError:
            logger.info("Torch not available, running in CPU-only mode")
            
        # Initialize index
        self.index = None
        
    def create(self, train_data: Optional[np.ndarray] = None) -> bool:
        """Create a new FAISS index based on index type and distance metric.
        
        Args:
            train_data: Optional training data for IVF indices
            
        Returns:
            True if successful
        """
        try:
            # Create base index based on distance metric
            if self.distance_metric == "cosine":
                if self.index_type == "Flat":
                    self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
                elif self.index_type == "IVF":
                    # Create quantizer
                    quantizer = faiss.IndexFlatIP(self.dimension)
                    # Create IVF index
                    nlist = self.index_config["IVF"]["nlist"]
                    self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
                    # Set search parameters
                    self.index.nprobe = self.index_config["IVF"]["nprobe"]
                    # Train if data provided
                    if train_data is not None and len(train_data) > 0:
                        self.index.train(train_data)
                elif self.index_type == "HNSW":
                    self.index = faiss.IndexHNSWFlat(
                        self.dimension, 
                        self.index_config["HNSW"]["M"]
                    )
                    self.index.hnsw.efConstruction = self.index_config["HNSW"]["efConstruction"]
                    self.index.hnsw.efSearch = self.index_config["HNSW"]["efSearch"]
                else:
                    logger.warning(f"Unknown index type {self.index_type}, falling back to Flat")
                    self.index = faiss.IndexFlatIP(self.dimension)
            else:  # L2 distance
                if self.index_type == "Flat":
                    self.index = faiss.IndexFlatL2(self.dimension)
                elif self.index_type == "IVF":
                    quantizer = faiss.IndexFlatL2(self.dimension)
                    nlist = self.index_config["IVF"]["nlist"]
                    self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
                    self.index.nprobe = self.index_config["IVF"]["nprobe"]
                    # Train if data provided
                    if train_data is not None and len(train_data) > 0:
                        self.index.train(train_data)
                elif self.index_type == "HNSW":
                    self.index = faiss.IndexHNSWFlat(
                        self.dimension, 
                        self.index_config["HNSW"]["M"]
                    )
                    self.index.hnsw.efConstruction = self.index_config["HNSW"]["efConstruction"]
                    self.index.hnsw.efSearch = self.index_config["HNSW"]["efSearch"]
                else:
                    logger.warning(f"Unknown index type {self.index_type}, falling back to Flat")
                    self.index = faiss.IndexFlatL2(self.dimension)
            
            # Move to GPU if available
            if self.gpu_available:
                try:
                    self.index = faiss.index_cpu_to_gpu(self.res, 0, self.index)
                    logger.info("Using GPU FAISS index")
                except Exception as e:
                    logger.warning(f"Failed to create GPU index: {e}")
            
            logger.info(f"Created new {self.index_type} FAISS index")
            return True
            
        except Exception as e:
            logger.error(f"Error creating FAISS index: {e}")
            return False
            
    def load(self, path: str) -> bool:
        """Load FAISS index from file with memory mapping.
        
        Args:
            path: Path to the index file
            
        Returns:
            True if successful
        """
        try:
            # Load index with memory mapping if enabled
            if self.use_mmap:
                try:
                    self.index = faiss.read_index(path, faiss.IO_FLAG_MMAP)
                    logger.info(f"Loaded memory-mapped FAISS index from {path}")
                except Exception as e:
                    logger.warning(f"Failed to load memory-mapped index ({str(e)}), falling back to standard loading")
                    self.index = faiss.read_index(path)
            else:
                self.index = faiss.read_index(path)
            
            # Move to GPU if available
            if self.gpu_available:
                try:
                    self.index = faiss.index_cpu_to_gpu(self.res, 0, self.index)
                    logger.info("Moved index to GPU")
                except Exception as e:
                    logger.warning(f"Failed to move index to GPU: {e}")
                    
            return True
            
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            return False
            
    def save(self, path: str) -> bool:
        """Save FAISS index to file.
        
        Args:
            path: Path to save the index
            
        Returns:
            True if successful
        """
        try:
            # If index is on GPU, convert back to CPU for saving
            index_to_save = self.index
            try:
                if self.gpu_available:
                    index_to_save = faiss.index_gpu_to_cpu(self.index)
            except Exception as e:
                logger.warning(f"Failed to convert GPU index to CPU for saving: {e}")
            
            # Save FAISS index
            faiss.write_index(index_to_save, path)
            return True
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
            return False
            
    def add_vectors(self, vectors: np.ndarray) -> bool:
        """Add vectors to the index.
        
        Args:
            vectors: Vectors to add
            
        Returns:
            True if successful
        """
        try:
            if self.index is None:
                raise ValueError("Index not initialized")
                
            self.index.add(vectors)
            return True
            
        except Exception as e:
            logger.error(f"Error adding vectors to index: {e}")
            return False
            
    def search(self, query_vector: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray]:
        """Search for similar vectors.
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            
        Returns:
            Tuple of (distances, indices)
        """
        try:
            if self.index is None:
                raise ValueError("Index not initialized")
                
            # Ensure query_vector is 2D
            if len(query_vector.shape) == 1:
                query_vector = np.expand_dims(query_vector, axis=0)
                
            # Search the index
            distances, indices = self.index.search(query_vector, top_k)
            return distances, indices
            
        except Exception as e:
            logger.error(f"Error searching index: {e}")
            raise
            
    def get_vector(self, idx: int) -> np.ndarray:
        """Get vector by index.
        
        Args:
            idx: Vector index
            
        Returns:
            Vector at the specified index
        """
        try:
            if self.index is None:
                raise ValueError("Index not initialized")
                
            # Get CPU index if needed
            cpu_index = self.index
            if self.gpu_available:
                cpu_index = faiss.index_gpu_to_cpu(self.index)
                
            # Reconstruct vector
            return cpu_index.reconstruct(idx)
            
        except Exception as e:
            logger.error(f"Error getting vector at index {idx}: {e}")
            raise
            
    def get_all_vectors(self) -> np.ndarray:
        """Get all vectors in the index.
        
        Returns:
            All vectors
        """
        try:
            if self.index is None:
                raise ValueError("Index not initialized")
                
            # Get CPU index for operations
            cpu_index = self.index
            if self.gpu_available:
                cpu_index = faiss.index_gpu_to_cpu(self.index)
                
            # Reconstruct all vectors
            return cpu_index.reconstruct_n(0, cpu_index.ntotal)
            
        except Exception as e:
            logger.error(f"Error getting all vectors: {e}")
            raise
            
    def replace_vector(self, vector: np.ndarray, idx: int) -> bool:
        """Replace vector at specific index (only works for Flat indices).
        
        Args:
            vector: New vector
            idx: Index to replace
            
        Returns:
            True if successful
        """
        try:
            if self.index is None:
                raise ValueError("Index not initialized")
                
            # Get CPU index for operations
            cpu_index = self.index
            if self.gpu_available:
                cpu_index = faiss.index_gpu_to_cpu(self.index)
                
            # Update vector at specific index (only works for Flat indices)
            if hasattr(cpu_index, 'replace_vector'):
                cpu_index.replace_vector(vector, idx)
                
                # Move back to GPU if needed
                if self.gpu_available:
                    self.index = faiss.index_cpu_to_gpu(self.res, 0, cpu_index)
                    
                return True
            else:
                # Fallback for indices that don't support direct replacement
                return False
                
        except Exception as e:
            logger.error(f"Error replacing vector at index {idx}: {e}")
            return False
            
    def count_vectors(self) -> int:
        """Get number of vectors in the index.
        
        Returns:
            Number of vectors
        """
        if self.index is None:
            return 0
            
        return self.index.ntotal
        
    def get_config(self) -> Dict[str, Any]:
        """Get index configuration.
        
        Returns:
            Dictionary with index configuration
        """
        return {
            "index_type": self.index_type,
            "dimension": self.dimension,
            "distance_metric": self.distance_metric,
            "use_mmap": self.use_mmap,
            "gpu_available": self.gpu_available,
            "vector_count": self.count_vectors(),
            "config": self.index_config
        }