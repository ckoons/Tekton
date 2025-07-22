"""
Qdrant vector store implementation.
"""

import os
import logging
import hashlib
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime

from tekton.core.storage.base import BaseVectorStorage, StorageNamespace
from tekton.core.storage.vector.qdrant.client import QdrantClient
from tekton.core.storage.vector.qdrant.utils import check_qdrant_available

# Configure logger
logger = logging.getLogger(__name__)

class QdrantVectorStore(BaseVectorStorage):
    """
    Qdrant implementation of BaseVectorStorage.
    
    Provides vector storage and similarity search with optimization
    for Apple Silicon processors but works on all platforms.
    """
    
    def __init__(
        self,
        namespace: str = "default",
        embedding_dim: int = 1536,
        distance_metric: str = "cosine",
        use_disk: bool = True,
        collection_name: Optional[str] = None,
        url: Optional[str] = None,
        port: int = 6333,
        path: Optional[str] = None,
        api_key: Optional[str] = None,
        grpc_port: Optional[int] = None,
        prefer_grpc: bool = True,
        embedding_model: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Qdrant vector store.
        
        Args:
            namespace: Namespace for the vector store
            embedding_dim: Dimension of vector embeddings
            distance_metric: Distance metric for comparison (cosine, l2, dot)
            use_disk: Whether to use disk storage (True) or in-memory (False)
            collection_name: Name of the Qdrant collection (defaults to namespace)
            url: Qdrant server URL for remote connection
            port: Qdrant server port for remote connection
            path: Directory for local Qdrant storage
            api_key: API key for remote Qdrant server
            grpc_port: gRPC port for Qdrant connection
            prefer_grpc: Whether to prefer gRPC over HTTP
            embedding_model: Model name for text embedding (optional)
            **kwargs: Additional configuration parameters
        """
        # Check if Qdrant is available
        check_qdrant_available()
            
        self.namespace = StorageNamespace(namespace)
        self.embedding_dim = embedding_dim
        self.distance_metric = distance_metric
        self.collection_name = collection_name or f"tekton_{namespace}"
        self.use_disk = use_disk
        
        # Define data path
        from shared.env import TektonEnviron
        self.data_path = path or TektonEnviron.get(
            "TEKTON_VECTOR_DB_PATH", 
            os.path.expanduser(f"~/.tekton/qdrant/{namespace}")
        )
        
        # Set up embedding model if provided
        self.embedding_model = None
        self.embedding_model_name = embedding_model
        
        if embedding_model:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(embedding_model)
                logger.info(f"Loaded embedding model: {embedding_model}")
            except ImportError:
                logger.warning("SentenceTransformer not available, embeddings will not be generated")
            except Exception as e:
                logger.error(f"Error loading embedding model: {e}")
                
        # Create client
        self.client = QdrantClient(
            collection_name=self.collection_name,
            distance_metric=distance_metric,
            embedding_dim=embedding_dim,
            url=url,
            port=port,
            grpc_port=grpc_port,
            api_key=api_key,
            path=self.data_path,
            use_disk=use_disk,
            prefer_grpc=prefer_grpc
        )
        
        # State
        self._initialized = False
        
    async def initialize(self) -> None:
        """
        Initialize the Qdrant vector storage backend.
        
        This method handles connection establishment and collection creation.
        """
        if self._initialized:
            return
            
        logger.info(f"Initializing Qdrant vector store with namespace: {self.namespace.namespace}")
        
        # Initialize client
        if not self.client.initialize():
            raise RuntimeError("Failed to initialize Qdrant client")
            
        self._initialized = True
        logger.info(f"Qdrant vector store initialized with collection: {self.collection_name}")
            
    async def finalize(self) -> None:
        """
        Finalize and clean up the Qdrant storage backend.
        
        This method handles connection closure and resource cleanup.
        """
        logger.info("Finalizing Qdrant vector store")
        
        if self.client:
            self.client.close()
            
        self._initialized = False
        logger.info("Qdrant vector store finalized")
    
    async def drop(self) -> Dict[str, str]:
        """
        Drop all data from storage.
        
        Returns:
            Dictionary with status and message
        """
        logger.warning(f"Dropping all vectors for namespace: {self.namespace.namespace}")
        
        if not self.client or not self._initialized:
            return {
                "status": "error",
                "message": "Qdrant vector store not initialized"
            }
            
        try:
            from qdrant_client.http import models as rest
            
            # First try to delete all points
            self.client.client.delete(
                collection_name=self.collection_name,
                points_selector=rest.Filter()
            )
            
            # Recreate collection to ensure clean state
            self.client.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=rest.VectorParams(
                    size=self.embedding_dim,
                    distance=self.client.qdrant_distance
                )
            )
            
            return {
                "status": "success",
                "message": f"All vectors for namespace {self.namespace.namespace} have been dropped"
            }
        except Exception as e:
            logger.error(f"Error dropping Qdrant collection: {e}")
            return {
                "status": "error",
                "message": f"Failed to drop vectors: {str(e)}"
            }
    
    async def index_done_callback(self) -> None:
        """
        Callback invoked when indexing operations are complete.
        
        For Qdrant, trigger optimization of the collection.
        """
        if not self.client or not self._initialized:
            return
            
        self.client.optimize()
    
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
        if not self.client or not self._initialized:
            logger.error("Qdrant vector store not initialized")
            return []
            
        return self.client.search(
            query_vector=query_vector,
            top_k=top_k,
            filter_ids=filter_ids,
            similarity_threshold=similarity_threshold
        )
    
    async def upsert(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Insert or update vectors in storage.
        
        Args:
            data: Dictionary mapping IDs to vector data and metadata
        """
        if not self.client or not self._initialized:
            logger.error("Qdrant vector store not initialized")
            raise RuntimeError("Qdrant vector store not initialized")
            
        if not data:
            return
            
        # Convert data format
        points = []
        for vector_id, item in data.items():
            points.append({
                "id": vector_id,
                "vector": item["vector"],
                "metadata": item.get("metadata", {}),
                "content": item.get("content", "")
            })
            
        # Upsert points
        self.client.upsert(points)
    
    async def delete(self, ids: List[str]) -> None:
        """
        Delete vectors with specified IDs.
        
        Args:
            ids: List of vector IDs to delete
        """
        if not self.client or not self._initialized:
            logger.error("Qdrant vector store not initialized")
            raise RuntimeError("Qdrant vector store not initialized")
            
        if not ids:
            return
            
        self.client.delete(ids)
    
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get vector data by ID.
        
        Args:
            id: The vector ID to retrieve
            
        Returns:
            Dictionary with vector data and metadata, or None if not found
        """
        if not self.client or not self._initialized:
            logger.error("Qdrant vector store not initialized")
            return None
            
        return self.client.get_by_id(id)
    
    async def get_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple vector data by their IDs.
        
        Args:
            ids: List of vector IDs to retrieve
            
        Returns:
            List of dictionaries with vector data and metadata
        """
        if not self.client or not self._initialized:
            logger.error("Qdrant vector store not initialized")
            return []
            
        return self.client.get_by_ids(ids)
    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for texts using the embedding model.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of embeddings
        """
        if not self.embedding_model:
            raise RuntimeError("Embedding model not available")
            
        embeddings = self.embedding_model.encode(texts)
        
        # Normalize embeddings if using cosine similarity
        if self.distance_metric == "cosine":
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        return embeddings