"""Qdrant-based vector store for Tekton.

This module provides a Qdrant-based vector store implementation,
optimized for Apple Silicon but also works on other platforms.
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import threading
import hashlib

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from tekton.core.vector_store import VectorStore

# Configure logger
logger = logging.getLogger(__name__)


class QdrantStore(VectorStore):
    """Qdrant-based vector store implementation.
    
    This class provides semantic search capabilities for Tekton
    using Qdrant for vector indexing and retrieval, optimized
    for Apple Silicon.
    """
    
    def __init__(
        self,
        path: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        collection_name: str = "tekton_documents",
        distance_metric: str = "cosine"
    ):
        """Initialize the Qdrant document store.
        
        Args:
            path: Path to store the Qdrant database
            embedding_model: Model to use for embeddings
            dimension: Embedding dimension
            collection_name: Name of the Qdrant collection
            distance_metric: Distance metric for comparison
        """
        self.path = path or TektonEnviron.get("TEKTON_VECTOR_DB_PATH", os.path.expanduser("~/.tekton/vector_store"))
        self.embedding_model_name = embedding_model
        self.dimension = dimension
        self.collection_name = collection_name
        self.distance_metric = distance_metric
        
        # Create directories if they don't exist
        os.makedirs(self.path, exist_ok=True)
        
        # Lock for thread safety
        self.write_lock = threading.RLock()
        
        # Load embeddings model
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
        
        # Initialize Qdrant client
        try:
            self.client = QdrantClient(path=self.path)
            self._initialize_collection()
            logger.info(f"Initialized Qdrant vector store at {self.path}")
        except Exception as e:
            logger.error(f"Error initializing Qdrant client: {e}")
            raise
    
    def _initialize_collection(self):
        """Initialize or get the Qdrant collection."""
        # Convert distance metric to Qdrant format
        if self.distance_metric == "cosine":
            qdrant_distance = Distance.COSINE
        elif self.distance_metric == "l2":
            qdrant_distance = Distance.EUCLID
        else:
            raise ValueError(f"Unsupported distance metric: {self.distance_metric}")
        
        # Check if collection exists
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.dimension,
                    distance=qdrant_distance
                )
            )
            logger.info(f"Created new Qdrant collection: {self.collection_name}")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add documents to the vector store.
        
        Args:
            documents: List of document dictionaries with 'content' and 'metadata'
            
        Returns:
            List of document IDs
        """
        if not documents:
            return []
        
        with self.write_lock:
            try:
                # Generate document IDs if not provided
                doc_ids = []
                points = []
                
                for doc in documents:
                    # Generate ID from content hash if not provided
                    if "id" not in doc:
                        doc_id = hashlib.md5(doc["content"].encode()).hexdigest()
                        doc["id"] = doc_id
                    
                    doc_ids.append(doc["id"])
                    
                    # Get or compute embeddings
                    embedding = self._get_embeddings([doc["content"]])[0]
                    
                    # Add to points
                    points.append(PointStruct(
                        id=doc["id"],
                        vector=embedding.tolist(),
                        payload={
                            "content": doc["content"],
                            "metadata": doc.get("metadata", {}),
                            "added_at": datetime.now().isoformat()
                        }
                    ))
                
                # Add to Qdrant
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                
                logger.info(f"Added {len(documents)} documents to Qdrant")
                return doc_ids
                
            except Exception as e:
                logger.error(f"Error adding documents: {e}")
                return []
    
    def update_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        """Update a document in the vector store.
        
        Args:
            doc_id: Document ID to update
            document: New document content
            
        Returns:
            True if successful
        """
        with self.write_lock:
            try:
                # Get old document to preserve added_at
                old_doc = self.get_document(doc_id)
                if not old_doc:
                    logger.error(f"Document not found: {doc_id}")
                    return False
                
                # Compute new embedding
                embedding = self._get_embeddings([document["content"]])[0]
                
                # Update the document
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        PointStruct(
                            id=doc_id,
                            vector=embedding.tolist(),
                            payload={
                                "content": document["content"],
                                "metadata": document.get("metadata", {}),
                                "added_at": old_doc.get("metadata", {}).get("added_at", datetime.now().isoformat()),
                                "updated_at": datetime.now().isoformat()
                            }
                        )
                    ]
                )
                
                logger.info(f"Updated document: {doc_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error updating document: {e}")
                return False
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the vector store.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful
        """
        with self.write_lock:
            try:
                # Check if document exists
                if not self.get_document(doc_id):
                    logger.error(f"Document not found: {doc_id}")
                    return False
                
                # Delete the document
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=[doc_id]
                )
                
                logger.info(f"Deleted document: {doc_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error deleting document: {e}")
                return False
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for documents by semantic similarity.
        
        Args:
            query: Query string
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of matching documents
        """
        try:
            # Get query embedding
            query_embedding = self._get_embeddings([query])[0]
            
            # Prepare filter
            qdrant_filter = None
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    filter_key = f"metadata.{key}"
                    
                    if isinstance(value, list):
                        # List filter (any match)
                        filter_conditions.append(
                            rest.HasIdCondition(has_id=value)
                        )
                    elif isinstance(value, dict):
                        # Range filter
                        range_conditions = []
                        for op, op_value in value.items():
                            if op == "gt":
                                range_conditions.append(rest.Range(gt=op_value))
                            elif op == "gte":
                                range_conditions.append(rest.Range(gte=op_value))
                            elif op == "lt":
                                range_conditions.append(rest.Range(lt=op_value))
                            elif op == "lte":
                                range_conditions.append(rest.Range(lte=op_value))
                        
                        filter_conditions.append(
                            rest.FieldCondition(key=filter_key, range=range_conditions)
                        )
                    else:
                        # Exact match
                        filter_conditions.append(
                            rest.FieldCondition(key=filter_key, match=rest.MatchValue(value=value))
                        )
                
                if filter_conditions:
                    qdrant_filter = rest.Filter(must=filter_conditions)
            
            # Search Qdrant
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=top_k,
                query_filter=qdrant_filter
            )
            
            # Process results
            results = []
            for hit in search_result:
                payload = hit.payload
                results.append({
                    "id": hit.id,
                    "content": payload["content"],
                    "metadata": payload.get("metadata", {}),
                    "score": hit.score
                })
            
            return results
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for texts."""
        embeddings = self.embedding_model.encode(texts)
        
        # Normalize embeddings if using cosine similarity
        if self.distance_metric == "cosine":
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        return embeddings
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document or None if not found
        """
        try:
            # Get document from Qdrant
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[doc_id]
            )
            
            if not points:
                return None
            
            payload = points[0].payload
            return {
                "id": doc_id,
                "content": payload["content"],
                "metadata": payload.get("metadata", {})
            }
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
    
    def get_documents_by_metadata(self, metadata_key: str, metadata_value: Any) -> List[Dict[str, Any]]:
        """Get documents by metadata.
        
        Args:
            metadata_key: Metadata key
            metadata_value: Metadata value
            
        Returns:
            List of matching documents
        """
        try:
            # Search by metadata
            filter_condition = rest.FieldCondition(
                key=f"metadata.{metadata_key}",
                match=rest.MatchValue(value=metadata_value)
            )
            
            # Get points from Qdrant
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=rest.Filter(must=[filter_condition]),
                limit=100  # Adjust as needed
            )
            
            # Process results
            results = []
            for point in scroll_result[0]:
                payload = point.payload
                results.append({
                    "id": point.id,
                    "content": payload["content"],
                    "metadata": payload.get("metadata", {})
                })
            
            return results
        except Exception as e:
            logger.error(f"Error getting documents by metadata: {e}")
            return []
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents.
        
        Returns:
            List of all documents
        """
        try:
            # Scroll through all documents
            all_points = []
            offset = None
            
            while True:
                scroll_result = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=100,  # Batch size
                    offset=offset
                )
                
                points, offset = scroll_result
                all_points.extend(points)
                
                if offset is None:
                    break
            
            # Process results
            results = []
            for point in all_points:
                payload = point.payload
                results.append({
                    "id": point.id,
                    "content": payload["content"],
                    "metadata": payload.get("metadata", {})
                })
            
            return results
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            return []
    
    def count_documents(self) -> int:
        """Get document count.
        
        Returns:
            Number of documents in the store
        """
        try:
            collection_info = self.client.get_collection(
                collection_name=self.collection_name
            )
            return collection_info.vectors_count
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0
    
    def rebuild_index(self) -> bool:
        """Rebuild the Qdrant index from scratch.
        
        Returns:
            True if successful
        """
        # Qdrant doesn't require explicit rebuilding, but we can optimize
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
            logger.error(f"Error rebuilding index: {e}")
            return False
