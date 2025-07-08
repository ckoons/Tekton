"""
FAISS vector store implementation.
"""

import os
import pickle
import logging
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime

import numpy as np

from tekton.core.storage.base import BaseVectorStorage, StorageNamespace
from tekton.core.storage.vector.faiss.utils import check_faiss_available, get_faiss_metric
from tekton.core.storage.vector.faiss.index import FAISSIndexManager
from tekton.core.storage.vector.faiss.metadata import MetadataManager
from tekton.core.storage.vector.faiss.search import SearchOperations
from tekton.core.storage.vector.faiss.operations import VectorOperations

# Configure logger
logger = logging.getLogger(__name__)

class FAISSVectorStore(BaseVectorStorage):
    """
    FAISS implementation of BaseVectorStorage.
    
    Provides vector storage and similarity search with support for GPU
    acceleration and multiple index types.
    """
    
    def __init__(
        self,
        namespace: str = "default",
        embedding_dim: int = 1536,
        index_type: str = "Flat",
        distance_metric: str = "cosine",
        use_gpu: bool = True,
        data_path: Optional[str] = None,
        embedding_model: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the FAISS vector store.
        
        Args:
            namespace: Namespace for the vector store
            embedding_dim: Dimension of vector embeddings
            index_type: FAISS index type (Flat, IVF, HNSW)
            distance_metric: Distance metric for comparison (cosine, l2, ip)
            use_gpu: Whether to use GPU acceleration if available
            data_path: Directory to store persistent data
            embedding_model: Model name for text embedding (optional)
            **kwargs: Additional configuration parameters
        """
        # Check FAISS availability
        check_faiss_available()
            
        self.namespace = StorageNamespace(namespace)
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.distance_metric = distance_metric
        self.use_gpu = use_gpu
        
        # Define data path
        tekton_root = os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
        self.data_path = data_path or os.environ.get(
            "TEKTON_VECTOR_DB_PATH", 
            os.path.join(tekton_root, ".tekton", "vector_stores", namespace)
        )
        
        # Convert distance metric
        self.faiss_metric, self.normalize = get_faiss_metric(distance_metric)
            
        # Index configuration
        self.index_config = {
            "Flat": {},  # No special parameters for flat index
            "IVF": {
                "nlist": kwargs.get("nlist", 100),  # Number of clusters
                "nprobe": kwargs.get("nprobe", 10)  # Number of clusters to search
            },
            "HNSW": {
                "M": kwargs.get("M", 32),          # Number of neighbors
                "efConstruction": kwargs.get("efConstruction", 200),  # Size of dynamic list during construction
                "efSearch": kwargs.get("efSearch", 64)  # Size of dynamic list during search
            }
        }
        
        # Set up embedding model if provided
        self.embedding_model = None
        self.embedding_model_name = embedding_model
        
        # State
        self.index_manager = None
        self.metadata_manager = None
        self.search_ops = None
        self.vector_ops = None
        self.id_to_index = {}
        self.index_to_id = {}
        self.write_lock = threading.RLock()
        self._initialized = False
        
    async def initialize(self) -> None:
        """
        Initialize the FAISS vector storage backend.
        
        This method handles index creation/loading and resource allocation.
        """
        if self._initialized:
            return
            
        logger.info(f"Initializing FAISS vector store with namespace: {self.namespace.namespace}")
        
        try:
            # Create directories if they don't exist
            os.makedirs(self.data_path, exist_ok=True)
            
            # Initialize managers
            self.index_manager = FAISSIndexManager(
                embedding_dim=self.embedding_dim,
                index_type=self.index_type,
                faiss_metric=self.faiss_metric,
                use_gpu=self.use_gpu,
                index_config=self.index_config
            )
            
            self.metadata_manager = MetadataManager(self.data_path)
            
            # Initialize operation modules
            self.search_ops = SearchOperations(
                self.index_manager,
                self.metadata_manager,
                self.normalize,
                self.distance_metric
            )
            
            self.vector_ops = VectorOperations(
                self.index_manager,
                self.metadata_manager,
                self.normalize
            )
            
            # Define file paths
            self.index_path = os.path.join(self.data_path, "index.faiss")
            self.id_to_index_path = os.path.join(self.data_path, "id_to_index.pkl")
            self.index_to_id_path = os.path.join(self.data_path, "index_to_id.pkl")
            
            # Load existing index and metadata if available
            if os.path.exists(self.index_path):
                await self._load_index_and_mappings()
            else:
                await self._create_new_index()
                
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing FAISS vector store: {e}")
            raise
            
    async def _load_index_and_mappings(self) -> None:
        """Load existing index and ID mappings."""
        with self.write_lock:
            try:
                # Load index
                self.index_manager.load_index(self.index_path)
                
                # Load mappings
                if os.path.exists(self.id_to_index_path) and os.path.exists(self.index_to_id_path):
                    with open(self.id_to_index_path, 'rb') as f:
                        self.id_to_index = pickle.load(f)
                    with open(self.index_to_id_path, 'rb') as f:
                        self.index_to_id = pickle.load(f)
                        
                # Load metadata
                self.metadata = self.metadata_manager.load_index_metadata()
                
                logger.info(f"Loaded existing FAISS index with {len(self.id_to_index)} vectors")
            except Exception as e:
                logger.error(f"Error loading index, creating new: {e}")
                await self._create_new_index()
    
    async def _create_new_index(self) -> None:
        """Create a new index and initialize metadata."""
        with self.write_lock:
            # Create new index
            self.index_manager.create_index()
            
            # Initialize mappings
            self.id_to_index = {}
            self.index_to_id = {}
            
            # Initialize metadata
            self.metadata = {
                "namespace": self.namespace.namespace,
                "embedding_dim": self.embedding_dim,
                "index_type": self.index_type,
                "distance_metric": self.distance_metric,
                "vector_count": 0,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Save metadata
            self.metadata_manager.save_index_metadata(self.metadata)
            
            logger.info(f"Created new FAISS {self.index_type} index")
            
    async def finalize(self) -> None:
        """
        Finalize and clean up the FAISS storage backend.
        
        This method handles resource cleanup and saving of any unsaved changes.
        """
        logger.info("Finalizing FAISS vector store")
        
        with self.write_lock:
            await self._save_state()
            
        self._initialized = False
        logger.info("FAISS vector store finalized")
        
    async def _save_state(self) -> None:
        """Save index, mappings, and metadata to disk."""
        with self.write_lock:
            try:
                # Save index
                if self.index_manager and self.index_manager.index is not None:
                    self.index_manager.save_index(self.index_path)
                
                # Save mappings
                with open(self.id_to_index_path, 'wb') as f:
                    pickle.dump(self.id_to_index, f)
                with open(self.index_to_id_path, 'wb') as f:
                    pickle.dump(self.index_to_id, f)
                
                # Update and save metadata
                if self.index_manager and self.index_manager.index is not None:
                    self.metadata["vector_count"] = self.index_manager.index.ntotal
                    self.metadata["updated_at"] = datetime.now().isoformat()
                    self.metadata_manager.save_index_metadata(self.metadata)
                
                logger.info(f"Saved FAISS state to {self.data_path}")
            except Exception as e:
                logger.error(f"Error saving FAISS state: {e}")
    
    async def drop(self) -> Dict[str, str]:
        """
        Drop all data from storage.
        
        Returns:
            Dictionary with status and message
        """
        logger.warning(f"Dropping all vectors for namespace: {self.namespace.namespace}")
        
        with self.write_lock:
            try:
                # Create a fresh index
                await self._create_new_index()
                await self._save_state()
                
                return {
                    "status": "success",
                    "message": f"All vectors for namespace {self.namespace.namespace} have been dropped"
                }
            except Exception as e:
                logger.error(f"Error dropping FAISS index: {e}")
                return {
                    "status": "error",
                    "message": f"Failed to drop vectors: {str(e)}"
                }
    
    async def index_done_callback(self) -> None:
        """
        Callback invoked when indexing operations are complete.
        
        This method handles persistence of changes and index optimization.
        """
        with self.write_lock:
            await self._save_state()
    
    async def query(self, 
                  query_vector: np.ndarray, 
                  top_k: int = 10,
                  filter_ids: Optional[List[str]] = None,
                  similarity_threshold: float = 0.2) -> List[Dict[str, Any]]:
        """
        Query vector database for similar vectors.
        
        Args:
            query_vector: The query vector to search for
            top_k: Maximum number of results to return
            filter_ids: Optional list of IDs to filter results
            similarity_threshold: Minimum similarity score threshold
            
        Returns:
            List of dictionaries with vector data and metadata
        """
        if not self._initialized:
            logger.error("FAISS vector store not initialized")
            return []
            
        return await self.search_ops.query(
            query_vector=query_vector,
            top_k=top_k,
            filter_ids=filter_ids,
            similarity_threshold=similarity_threshold,
            index_to_id=self.index_to_id
        )
    
    async def upsert(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Insert or update vectors in storage.
        
        Args:
            data: Dictionary mapping IDs to vector data and metadata
        """
        if not self._initialized:
            logger.error("FAISS vector store not initialized")
            raise RuntimeError("FAISS vector store not initialized")
            
        if not data:
            return
            
        with self.write_lock:
            # Handle vector operations
            updated_ids, added_ids = await self.vector_ops.upsert(
                data=data,
                id_to_index=self.id_to_index,
                index_to_id=self.index_to_id
            )
                
            # Update metadata
            self.metadata["vector_count"] = self.index_manager.index.ntotal
            self.metadata["updated_at"] = datetime.now().isoformat()
            
            # Save state periodically
            if len(data) > 10:
                await self._save_state()
    
    async def delete(self, ids: List[str]) -> None:
        """
        Delete vectors with specified IDs.
        
        Args:
            ids: List of vector IDs to delete
        """
        if not self._initialized:
            logger.error("FAISS vector store not initialized")
            raise RuntimeError("FAISS vector store not initialized")
            
        if not ids:
            return
            
        with self.write_lock:
            # Handle vector operations
            await self.vector_ops.delete(
                ids=ids,
                id_to_index=self.id_to_index,
                index_to_id=self.index_to_id
            )
                
            # Update metadata
            self.metadata["vector_count"] = self.index_manager.index.ntotal
            self.metadata["updated_at"] = datetime.now().isoformat()
            
            # Save index
            await self._save_state()
    
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get vector data by ID.
        
        Args:
            id: The vector ID to retrieve
            
        Returns:
            Dictionary with vector data and metadata, or None if not found
        """
        if not self._initialized:
            logger.error("FAISS vector store not initialized")
            return None
            
        if id not in self.id_to_index:
            return None
            
        try:
            index = self.id_to_index[id]
            
            # Get metadata
            metadata = self.metadata_manager.load_vector_metadata(id) or {}
                    
            # We can't efficiently retrieve a single vector from FAISS
            # Return metadata with index information
            return {
                "id": id,
                "vector_index": index,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error getting vector by ID: {e}")
            return None
    
    async def get_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple vector data by their IDs.
        
        Args:
            ids: List of vector IDs to retrieve
            
        Returns:
            List of dictionaries with vector data and metadata
        """
        if not self._initialized:
            logger.error("FAISS vector store not initialized")
            return []
            
        results = []
        for vector_id in ids:
            result = await self.get_by_id(vector_id)
            if result:
                results.append(result)
                
        return results