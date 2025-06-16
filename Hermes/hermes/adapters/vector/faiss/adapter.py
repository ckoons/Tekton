"""
FAISS Vector Adapter - High-performance vector database using Facebook AI Similarity Search.

This module provides a VectorDatabaseAdapter implementation that uses FAISS
for fast and efficient similarity search with hardware acceleration.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from hermes.core.logging import get_logger
from hermes.core.database.adapters import VectorDatabaseAdapter
from hermes.core.database.database_types import DatabaseBackend

from hermes.adapters.vector.faiss.operations import (
    store_vector,
    search_vectors,
    delete_vectors,
    get_vector,
    list_vectors
)
from hermes.adapters.vector.faiss.index import create_index
from hermes.adapters.vector.faiss.utils import rebuild_id_mappings

# Logger for this module
logger = get_logger("hermes.adapters.vector.faiss.adapter")


class FAISSVectorAdapter(VectorDatabaseAdapter):
    """
    FAISS vector database adapter for high-performance similarity search.
    
    This adapter provides fast vector operations using FAISS for
    hardware-accelerated vector similarity search (CPU or GPU).
    """
    
    def __init__(self, 
                namespace: str,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the FAISS vector adapter.
        
        Args:
            namespace: Namespace for data isolation
            config: Optional configuration parameters
        """
        super().__init__(namespace, config)
        
        # Get base path from config
        self.base_path = Path(self.config.get("base_path", os.path.expanduser("~/.tekton/data/vector")))
        
        # Create directory for this namespace
        self.namespace_path = self.base_path / namespace
        self.namespace_path.mkdir(parents=True, exist_ok=True)
        
        # Paths for data and index files
        self.data_file = self.namespace_path / "vectors.json"
        self.index_file = self.namespace_path / "index.faiss"
        
        # Vector dimensions
        self.vector_dim = self.config.get("vector_dim", 1536)  # Default for OpenAI embeddings
        
        # In-memory storage
        self.vectors: Dict[str, Dict[str, Any]] = {}
        self.index = None
        self.id_to_index: Dict[str, int] = {}
        self.index_to_id: Dict[int, str] = {}
        
        # Internal state
        self._connected = False
        self._modified = False
        
        # GPU usage
        self.use_gpu = self.config.get("use_gpu", False)
        if self.use_gpu:
            try:
                # Check CUDA availability
                import torch
                self.use_gpu = torch.cuda.is_available()
                if not self.use_gpu:
                    logger.warning("GPU requested but CUDA not available, falling back to CPU")
            except ImportError:
                logger.warning("GPU requested but PyTorch not installed, falling back to CPU")
                self.use_gpu = False
    
    @property
    def backend(self) -> DatabaseBackend:
        """Get the database backend."""
        return DatabaseBackend.FAISS
    
    async def connect(self) -> bool:
        """
        Connect to the database.
        
        Returns:
            True if connection successful
        """
        try:
            # Load vectors from file if it exists
            if self.data_file.exists():
                with open(self.data_file, "r") as f:
                    self.vectors = json.load(f)
                
                # If vectors exist, get vector dimension from first vector
                if self.vectors:
                    first_id = next(iter(self.vectors))
                    self.vector_dim = len(self.vectors[first_id]["vector"])
            else:
                self.vectors = {}
            
            # Load index from file if it exists
            if self.index_file.exists() and self.vectors:
                try:
                    import faiss
                    self.index = faiss.read_index(str(self.index_file))
                    
                    # Rebuild id mappings
                    self.id_to_index, self.index_to_id = rebuild_id_mappings(self.vectors)
                except Exception as e:
                    logger.error(f"Error loading FAISS index, rebuilding: {e}")
                    self.index, self.id_to_index, self.index_to_id = await create_index(
                        vectors=self.vectors,
                        vector_dim=self.vector_dim,
                        use_gpu=self.use_gpu
                    )
            else:
                # Create new index
                self.index, self.id_to_index, self.index_to_id = await create_index(
                    vectors=self.vectors,
                    vector_dim=self.vector_dim,
                    use_gpu=self.use_gpu
                )
            
            self._connected = True
            self._modified = False
            
            logger.info(f"Connected to FAISS vector database for namespace {self.namespace}")
            logger.debug(f"Loaded {len(self.vectors)} vectors")
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to FAISS vector database: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from the database.
        
        Returns:
            True if disconnection successful
        """
        try:
            # Save vectors if modified
            if self._modified:
                await self._save()
            
            self.vectors = {}
            self.index = None
            self.id_to_index = {}
            self.index_to_id = {}
            
            self._connected = False
            self._modified = False
            
            logger.info(f"Disconnected from FAISS vector database for namespace {self.namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from FAISS vector database: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """
        Check if connected to the database.
        
        Returns:
            True if connected
        """
        return self._connected
    
    async def store(self,
                  id: str,
                  vector: List[float],
                  metadata: Optional[Dict[str, Any]] = None,
                  text: Optional[str] = None) -> bool:
        """
        Store a vector in the database.
        
        Args:
            id: Unique identifier for the vector
            vector: The vector embedding
            metadata: Optional metadata to store with the vector
            text: Optional text content associated with the vector
            
        Returns:
            True if storage successful
        """
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        vectors, id_to_index, index_to_id, success = await store_vector(
            vectors=self.vectors,
            index=self.index,
            id_to_index=self.id_to_index,
            index_to_id=self.index_to_id,
            id=id,
            vector=vector,
            metadata=metadata,
            text=text,
            vector_dim=self.vector_dim
        )
        
        if success:
            self.vectors = vectors
            self.id_to_index = id_to_index
            self.index_to_id = index_to_id
            self._modified = True
            
        return success
    
    async def search(self,
                   query_vector: List[float],
                   limit: int = 10,
                   filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: The query vector
            limit: Maximum number of results
            filter: Optional metadata filter
            
        Returns:
            List of matching vectors with metadata and similarity scores
        """
        if not self._connected:
            logger.error("Not connected to database")
            return []
        
        return await search_vectors(
            vectors=self.vectors,
            index=self.index,
            id_to_index=self.id_to_index,
            index_to_id=self.index_to_id,
            query_vector=query_vector,
            limit=limit,
            filter=filter
        )
    
    async def delete(self,
                   id: Optional[str] = None,
                   filter: Optional[Dict[str, Any]] = None) -> bool:
        """
        Delete vectors from the database.
        
        Args:
            id: Optional specific vector ID to delete
            filter: Optional metadata filter for bulk deletion
            
        Returns:
            True if deletion successful
        """
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        vectors, id_to_index, index_to_id, success = await delete_vectors(
            vectors=self.vectors,
            index=self.index,
            id_to_index=self.id_to_index,
            index_to_id=self.index_to_id,
            id=id,
            filter=filter,
            vector_dim=self.vector_dim,
            use_gpu=self.use_gpu
        )
        
        if success:
            self.vectors = vectors
            self.id_to_index = id_to_index
            self.index_to_id = index_to_id
            self._modified = True
            
        return success
    
    async def get(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific vector by ID.
        
        Args:
            id: Vector ID to retrieve
            
        Returns:
            Vector with metadata if found, None otherwise
        """
        if not self._connected:
            logger.error("Not connected to database")
            return None
        
        return await get_vector(
            vectors=self.vectors,
            id=id
        )
    
    async def list(self,
                 limit: int = 100,
                 offset: int = 0,
                 filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List vectors in the database.
        
        Args:
            limit: Maximum number of results
            offset: Starting offset for pagination
            filter: Optional metadata filter
            
        Returns:
            List of vectors with metadata
        """
        if not self._connected:
            logger.error("Not connected to database")
            return []
        
        return await list_vectors(
            vectors=self.vectors,
            limit=limit,
            offset=offset,
            filter=filter
        )
    
    async def _save(self) -> bool:
        """Save vectors and index to disk."""
        try:
            # Save vectors
            with open(self.data_file, "w") as f:
                json.dump(self.vectors, f)
            
            # Save index if it exists
            if self.index is not None:
                import faiss
                faiss.write_index(self.index, str(self.index_file))
            
            self._modified = False
            
            logger.debug(f"Saved {len(self.vectors)} vectors to disk")
            return True
            
        except Exception as e:
            logger.error(f"Error saving vectors to disk: {e}")
            return False