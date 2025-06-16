"""
Qdrant client management for vector store.
"""

import os
import logging
import hashlib
import numpy as np
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as rest
    from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

from tekton.core.storage.vector.qdrant.utils import (
    check_qdrant_available,
    get_qdrant_distance,
    normalize_vectors,
    convert_to_score_threshold,
    convert_distance_to_similarity
)

# Configure logger
logger = logging.getLogger(__name__)

class QdrantClient:
    """
    Manages Qdrant connections and operations.
    """
    
    def __init__(
        self,
        collection_name: str,
        distance_metric: str,
        embedding_dim: int,
        url: Optional[str] = None,
        port: int = 6333,
        grpc_port: Optional[int] = None,
        api_key: Optional[str] = None,
        path: Optional[str] = None,
        use_disk: bool = True,
        prefer_grpc: bool = True
    ):
        """
        Initialize Qdrant client.
        
        Args:
            collection_name: Name of the Qdrant collection
            distance_metric: Distance metric (cosine, l2, dot)
            embedding_dim: Vector dimension
            url: Qdrant server URL for remote connection
            port: Qdrant server port for remote connection
            grpc_port: gRPC port for Qdrant connection
            api_key: API key for remote Qdrant server
            path: Directory for local Qdrant storage
            use_disk: Whether to use disk storage (True) or in-memory (False)
            prefer_grpc: Whether to prefer gRPC over HTTP
        """
        # Check if Qdrant is available
        if not check_qdrant_available():
            raise ImportError(
                "Qdrant client is required. "
                "Install with: pip install qdrant-client"
            )
            
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        
        # Convert distance metric
        self.qdrant_distance, self.normalize = get_qdrant_distance(distance_metric)
        self.distance_metric = distance_metric
        
        # Connection parameters
        self.url = url
        self.port = port
        self.path = path
        self.api_key = api_key
        self.grpc_port = grpc_port
        self.prefer_grpc = prefer_grpc
        self.use_disk = use_disk
        
        # State
        self.client = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize the Qdrant client.
        
        Returns:
            True if successful
        """
        if self._initialized:
            return True
            
        try:
            # Create client connection
            if self.url:
                # Remote connection
                self.client = QdrantClient(
                    url=self.url,
                    port=self.port,
                    api_key=self.api_key,
                    grpc_port=self.grpc_port,
                    prefer_grpc=self.prefer_grpc
                )
                logger.info(f"Connected to remote Qdrant server at {self.url}")
            else:
                # Local connection
                if self.use_disk:
                    # Ensure directory exists
                    os.makedirs(self.path, exist_ok=True)
                    self.client = QdrantClient(path=self.path)
                    logger.info(f"Connected to local Qdrant at {self.path}")
                else:
                    # In-memory
                    self.client = QdrantClient(":memory:")
                    logger.info("Connected to in-memory Qdrant")
            
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                # Create new collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=self.qdrant_distance
                    )
                )
                logger.info(f"Created new Qdrant collection: {self.collection_name}")
            else:
                # Verify collection configuration
                collection_info = self.client.get_collection(self.collection_name)
                if collection_info.config.params.vectors.distance != self.qdrant_distance:
                    logger.warning(
                        f"Collection distance metric mismatch: "
                        f"{collection_info.config.params.vectors.distance} != {self.qdrant_distance}"
                    )
                if collection_info.config.params.vectors.size != self.embedding_dim:
                    logger.warning(
                        f"Collection vector dimension mismatch: "
                        f"{collection_info.config.params.vectors.size} != {self.embedding_dim}"
                    )
                    
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Qdrant client: {e}")
            return False
    
    def close(self) -> None:
        """Close Qdrant connection."""
        if self.client:
            self.client.close()
            self.client = None
            
        self._initialized = False
        logger.info("Qdrant client closed")
    
    def search(
        self, 
        query_vector: np.ndarray,
        top_k: int = 10,
        filter_ids: Optional[List[str]] = None,
        similarity_threshold: float = 0.2
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query vector
            top_k: Maximum number of results
            filter_ids: Optional list of IDs to filter results
            similarity_threshold: Minimum similarity score threshold
            
        Returns:
            List of search results
        """
        if not self._initialized:
            raise RuntimeError("Qdrant client not initialized")
            
        # Ensure vector is in the correct format
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1).astype(np.float32)
        else:
            query_vector = query_vector.astype(np.float32)
            
        # Normalize if using cosine similarity
        if self.normalize and self.distance_metric == "cosine":
            query_vector = normalize_vectors(query_vector)
            
        try:
            # Prepare filter if needed
            qdrant_filter = None
            if filter_ids:
                qdrant_filter = rest.Filter(
                    must=[rest.HasIdCondition(has_id=filter_ids)]
                )
                
            # Adjust score threshold
            score_threshold = None
            threshold_params = convert_to_score_threshold(self.distance_metric, similarity_threshold)
            if threshold_params:
                score_threshold = rest.ScoreThreshold(**threshold_params)
                
            # Perform search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector[0].tolist(),
                limit=top_k,
                query_filter=qdrant_filter,
                score_threshold=score_threshold
            )
            
            # Process results
            results = []
            for hit in search_result:
                # Convert score for consistent format across adapters
                score = convert_distance_to_similarity(hit.score, self.distance_metric)
                
                payload = hit.payload or {}
                results.append({
                    "id": hit.id,
                    "score": score,
                    "metadata": payload.get("metadata", {}),
                    "content": payload.get("content", ""),
                    "vector_id": hit.id
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Error searching Qdrant: {e}")
            return []
    
    def upsert(self, points: List[Dict[str, Any]]) -> bool:
        """
        Insert or update vectors.
        
        Args:
            points: List of point dictionaries with id, vector, and payload
            
        Returns:
            True if successful
        """
        if not self._initialized:
            raise RuntimeError("Qdrant client not initialized")
            
        if not points:
            return True
            
        try:
            # Prepare points for upsert
            qdrant_points = []
            
            for point in points:
                if "vector" not in point:
                    logger.error(f"Vector missing for point {point.get('id')}")
                    continue
                    
                vector_id = point.get("id")
                vector = point["vector"]
                
                # Ensure vector is a numpy array
                if not isinstance(vector, np.ndarray):
                    try:
                        vector = np.array(vector, dtype=np.float32)
                    except:
                        logger.error(f"Invalid vector format for ID {vector_id}")
                        continue
                        
                # Ensure vector has the correct dimension
                if len(vector.shape) == 1:
                    if vector.shape[0] != self.embedding_dim:
                        logger.error(
                            f"Vector dimension mismatch: {vector.shape[0]} != {self.embedding_dim}"
                        )
                        continue
                else:
                    logger.error(f"Invalid vector shape: {vector.shape}")
                    continue
                    
                # Normalize if using cosine similarity
                if self.normalize and self.distance_metric == "cosine":
                    vector_norm = vector.copy()
                    norm = np.linalg.norm(vector_norm)
                    if norm > 0:
                        vector_norm = vector_norm / norm
                    vector = vector_norm
                    
                # Prepare payload
                payload = {
                    "metadata": point.get("metadata", {}),
                    "content": point.get("content", ""),
                    "updated_at": datetime.now().isoformat()
                }
                
                # Add point
                qdrant_points.append(PointStruct(
                    id=vector_id,
                    vector=vector.tolist(),
                    payload=payload
                ))
                
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(qdrant_points), batch_size):
                batch = qdrant_points[i:i+batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                
            logger.info(f"Upserted {len(qdrant_points)} vectors to Qdrant")
            return True
                
        except Exception as e:
            logger.error(f"Error upserting vectors to Qdrant: {e}")
            return False
    
    def delete(self, ids: List[str]) -> bool:
        """
        Delete vectors by IDs.
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            True if successful
        """
        if not self._initialized:
            raise RuntimeError("Qdrant client not initialized")
            
        if not ids:
            return True
            
        try:
            # Delete points
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=rest.Filter(
                    must=[rest.HasIdCondition(has_id=ids)]
                )
            )
            
            logger.info(f"Deleted {len(ids)} vectors from Qdrant")
            return True
                
        except Exception as e:
            logger.error(f"Error deleting vectors from Qdrant: {e}")
            return False
    
    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get vector by ID.
        
        Args:
            id: Vector ID
            
        Returns:
            Dictionary with vector data and metadata
        """
        if not self._initialized:
            raise RuntimeError("Qdrant client not initialized")
            
        try:
            # Get points from Qdrant
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[id],
                with_vectors=True
            )
            
            if not points:
                return None
                
            # Convert point to dictionary
            point = points[0]
            payload = point.payload or {}
            
            return {
                "id": id,
                "vector": np.array(point.vector),
                "metadata": payload.get("metadata", {}),
                "content": payload.get("content", "")
            }
                
        except Exception as e:
            logger.error(f"Error getting vector by ID: {e}")
            return None
    
    def get_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple vectors by IDs.
        
        Args:
            ids: List of vector IDs
            
        Returns:
            List of dictionaries with vector data and metadata
        """
        if not self._initialized:
            raise RuntimeError("Qdrant client not initialized")
            
        if not ids:
            return []
            
        try:
            # Get points from Qdrant
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=ids,
                with_vectors=True
            )
            
            # Convert points to dictionaries
            results = []
            for point in points:
                payload = point.payload or {}
                results.append({
                    "id": point.id,
                    "vector": np.array(point.vector),
                    "metadata": payload.get("metadata", {}),
                    "content": payload.get("content", "")
                })
                
            return results
                
        except Exception as e:
            logger.error(f"Error getting vectors by IDs: {e}")
            return []
    
    def count(self) -> int:
        """
        Get count of vectors in collection.
        
        Returns:
            Number of vectors
        """
        if not self._initialized:
            raise RuntimeError("Qdrant client not initialized")
            
        try:
            collection_info = self.client.get_collection(
                collection_name=self.collection_name
            )
            return collection_info.vectors_count
        except Exception as e:
            logger.error(f"Error counting vectors: {e}")
            return 0
    
    def optimize(self) -> bool:
        """
        Optimize the collection.
        
        Returns:
            True if successful
        """
        if not self._initialized:
            raise RuntimeError("Qdrant client not initialized")
            
        try:
            # Trigger index optimization
            self.client.update_collection(
                collection_name=self.collection_name,
                optimizer_config=rest.OptimizersConfigDiff(
                    indexing_threshold=0  # Force reindexing
                )
            )
            logger.info("Successfully triggered Qdrant index optimization")
            return True
        except Exception as e:
            logger.error(f"Error optimizing Qdrant collection: {e}")
            return False