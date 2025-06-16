"""
Fallback Vector Adapter - Simple file-based vector database.

This module provides a fallback implementation of the VectorDatabaseAdapter
that uses simple JSON files to store vector data when specialized
vector databases are not available.
"""

import os
import json
import time
import uuid
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from hermes.core.logging import get_logger
from hermes.core.database.adapters import VectorDatabaseAdapter
from hermes.core.database.database_types import DatabaseBackend

# Logger for this module
logger = get_logger("hermes.adapters.vector.fallback")


class FallbackVectorAdapter(VectorDatabaseAdapter):
    """
    Fallback vector database adapter using simple JSON files.
    
    This adapter provides basic vector operations using numpy for
    vector similarity and JSON files for persistence.
    """
    
    def __init__(self, 
                namespace: str,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the fallback vector adapter.
        
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
        self.index_file = self.namespace_path / "index.npy"
        
        # In-memory storage
        self.vectors: Dict[str, Dict[str, Any]] = {}
        self.index: Optional[np.ndarray] = None
        self.id_to_index: Dict[str, int] = {}
        
        # Internal state
        self._connected = False
        self._modified = False
    
    @property
    def backend(self) -> DatabaseBackend:
        """Get the database backend."""
        return DatabaseBackend.JSONDB
    
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
            else:
                self.vectors = {}
            
            # Load index from file if it exists
            if self.index_file.exists():
                self.index = np.load(self.index_file, allow_pickle=True)
                
                # Rebuild id_to_index mapping
                self.id_to_index = {
                    id: i for i, id in enumerate(self.vectors.keys())
                }
            else:
                self.index = None
                self.id_to_index = {}
            
            self._connected = True
            self._modified = False
            
            logger.info(f"Connected to fallback vector database for namespace {self.namespace}")
            logger.debug(f"Loaded {len(self.vectors)} vectors")
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to fallback vector database: {e}")
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
            
            self._connected = False
            self._modified = False
            
            logger.info(f"Disconnected from fallback vector database for namespace {self.namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from fallback vector database: {e}")
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
        
        try:
            # Convert vector to numpy array
            vector_np = np.array(vector, dtype=np.float32)
            
            # Store vector
            self.vectors[id] = {
                "id": id,
                "vector": vector,
                "metadata": metadata or {},
                "text": text,
                "created_at": time.time()
            }
            
            # Mark as modified
            self._modified = True
            
            # Invalidate index (will be rebuilt on next search)
            self.index = None
            self.id_to_index = {}
            
            logger.debug(f"Stored vector with ID {id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing vector: {e}")
            return False
    
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
        
        try:
            # Convert query vector to numpy array
            query_np = np.array(query_vector, dtype=np.float32)
            
            # Normalize query vector
            query_norm = np.linalg.norm(query_np)
            if query_norm > 0:
                query_np = query_np / query_norm
            
            # Rebuild index if needed
            if self.index is None:
                await self._build_index()
            
            if len(self.vectors) == 0:
                return []
            
            # Compute similarities
            similarities = np.dot(self.index, query_np)
            
            # Get top results
            top_indices = np.argsort(similarities)[::-1][:limit * 2]  # Get more results for filtering
            
            # Prepare results
            results = []
            
            for idx in top_indices:
                vector_id = list(self.vectors.keys())[idx]
                vector = self.vectors[vector_id]
                
                # Apply filter if provided
                if filter and not self._matches_filter(vector, filter):
                    continue
                
                results.append({
                    "id": vector_id,
                    "metadata": vector.get("metadata", {}),
                    "text": vector.get("text"),
                    "relevance": float(similarities[idx]),
                    "vector": vector.get("vector")
                })
                
                if len(results) >= limit:
                    break
            
            logger.debug(f"Found {len(results)} similar vectors")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
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
        
        try:
            if id:
                # Delete specific vector
                if id in self.vectors:
                    del self.vectors[id]
                    self._modified = True
                    
                    # Invalidate index
                    self.index = None
                    self.id_to_index = {}
                    
                    logger.debug(f"Deleted vector with ID {id}")
                    return True
                else:
                    logger.warning(f"Vector with ID {id} not found")
                    return False
            
            elif filter:
                # Delete vectors matching filter
                deleted = False
                
                for vector_id in list(self.vectors.keys()):
                    vector = self.vectors[vector_id]
                    
                    if self._matches_filter(vector, filter):
                        del self.vectors[vector_id]
                        deleted = True
                
                if deleted:
                    self._modified = True
                    
                    # Invalidate index
                    self.index = None
                    self.id_to_index = {}
                    
                    logger.debug("Deleted vectors matching filter")
                    return True
                else:
                    logger.warning("No vectors matched filter")
                    return False
            
            else:
                # Delete all vectors
                self.vectors = {}
                self._modified = True
                
                # Invalidate index
                self.index = None
                self.id_to_index = {}
                
                logger.debug("Deleted all vectors")
                return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False
    
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
        
        try:
            if id in self.vectors:
                vector = self.vectors[id]
                
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
        
        try:
            # Get matching vectors
            matching_vectors = []
            
            for vector_id, vector in self.vectors.items():
                if filter and not self._matches_filter(vector, filter):
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
    
    async def _save(self) -> bool:
        """Save vectors to disk."""
        try:
            # Save vectors
            with open(self.data_file, "w") as f:
                json.dump(self.vectors, f)
            
            # Save index if it exists
            if self.index is not None:
                np.save(self.index_file, self.index)
            
            self._modified = False
            
            logger.debug(f"Saved {len(self.vectors)} vectors to disk")
            return True
            
        except Exception as e:
            logger.error(f"Error saving vectors to disk: {e}")
            return False
    
    async def _build_index(self) -> None:
        """Build search index."""
        try:
            if not self.vectors:
                self.index = np.zeros((0, 0), dtype=np.float32)
                self.id_to_index = {}
                return
            
            # Extract vector dimensions from the first vector
            first_vector = next(iter(self.vectors.values()))
            vector_dim = len(first_vector["vector"])
            
            # Create index
            self.index = np.zeros((len(self.vectors), vector_dim), dtype=np.float32)
            
            # Add vectors to index
            for i, (vector_id, vector) in enumerate(self.vectors.items()):
                vector_np = np.array(vector["vector"], dtype=np.float32)
                
                # Normalize
                vector_norm = np.linalg.norm(vector_np)
                if vector_norm > 0:
                    vector_np = vector_np / vector_norm
                
                self.index[i] = vector_np
                self.id_to_index[vector_id] = i
            
            logger.debug(f"Built search index with {len(self.vectors)} vectors")
            
        except Exception as e:
            logger.error(f"Error building search index: {e}")
            self.index = None
            self.id_to_index = {}
    
    def _matches_filter(self, vector: Dict[str, Any], filter: Dict[str, Any]) -> bool:
        """Check if a vector matches a metadata filter."""
        metadata = vector.get("metadata", {})
        
        for key, value in filter.items():
            # Handle nested keys
            if "." in key:
                parts = key.split(".")
                current = metadata
                
                for part in parts[:-1]:
                    if not isinstance(current, dict) or part not in current:
                        return False
                    current = current[part]
                
                last_part = parts[-1]
                
                if not isinstance(current, dict) or last_part not in current:
                    return False
                
                if current[last_part] != value:
                    return False
            
            # Simple key
            elif key not in metadata or metadata[key] != value:
                return False
        
        return True