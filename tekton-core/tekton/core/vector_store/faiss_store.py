"""FAISS-based vector store for Tekton.

This module provides a FAISS-based vector store implementation,
optimized for NVIDIA GPUs but also works on other platforms.
"""

import os
import json
import pickle
import logging
import numpy as np
import threading
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime

from tekton.core.vector_store import VectorStore
from .components.faiss_index import FAISSIndex
from .components.document_store import DocumentStore
from .components.embedding import EmbeddingEngine
from .components.search import SearchEngine
from .components.keyword_index import KeywordIndex

# Configure logger
logger = logging.getLogger(__name__)


class EnhancedFAISSStore(VectorStore):
    """
    Enhanced FAISS-based vector store with improved performance and features.
    
    This class provides semantic search capabilities for Tekton
    using FAISS for vector indexing and retrieval, with advanced features like:
    - Memory-mapped indices for improved performance
    - Hybrid search combining vector similarity and keyword matching
    - Incremental updates to avoid full index rebuilds
    - Configurable indexing and search parameters
    """
    
    def __init__(
        self,
        path: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        index_type: str = "Flat",
        distance_metric: str = "cosine",
        use_mmap: bool = True,
        enable_hybrid_search: bool = True
    ):
        """Initialize the enhanced FAISS document store.
        
        Args:
            path: Path to store the index
            embedding_model: Model to use for embeddings
            dimension: Embedding dimension
            index_type: FAISS index type (Flat, IVF, HNSW)
            distance_metric: Distance metric for comparison
            use_mmap: Whether to use memory-mapped indices
            enable_hybrid_search: Whether to enable hybrid search
        """
        self.path = path or TektonEnviron.get("TEKTON_VECTOR_DB_PATH", os.path.expanduser("~/.tekton/vector_store"))
        self.embedding_model_name = embedding_model
        self.dimension = dimension
        self.index_type = index_type
        self.distance_metric = distance_metric
        self.use_mmap = use_mmap
        self.enable_hybrid_search = enable_hybrid_search
        
        # Index configuration
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
        
        # Create directories if they don't exist
        os.makedirs(self.path, exist_ok=True)
        
        # Initialize paths
        self.index_path = os.path.join(self.path, "faiss.index")
        
        # Lock for thread safety
        self.write_lock = threading.RLock()
        
        # Initialize components
        self._initialize_components()
        
        # Load or create index
        self._initialize_or_load_index()
        
    def _initialize_components(self):
        """Initialize the vector store components."""
        # Initialize document store
        self.document_store = DocumentStore(self.path)
        
        # Initialize embedding engine
        self.embedding_engine = EmbeddingEngine(
            model_name=self.embedding_model_name,
            dimension=self.dimension,
            normalize=(self.distance_metric == "cosine"),
            use_gpu=True
        )
        
        # Initialize FAISS index
        self.faiss_index = FAISSIndex(
            dimension=self.dimension,
            index_type=self.index_type,
            distance_metric=self.distance_metric,
            use_mmap=self.use_mmap,
            config=self.index_config
        )
        
        # Initialize keyword index if hybrid search is enabled
        if self.enable_hybrid_search:
            self.keyword_index = KeywordIndex(self.path, use_nltk=True)
        else:
            self.keyword_index = None
        
        # Initialize search engine
        self.search_engine = SearchEngine(
            document_store=self.document_store,
            faiss_index=self.faiss_index,
            keyword_index=self.keyword_index,
            embedding_engine=self.embedding_engine
        )
        
    def _initialize_or_load_index(self):
        """Initialize or load FAISS index and documents."""
        with self.write_lock:
            # Check if index exists
            if os.path.exists(self.index_path):
                try:
                    # Load existing index
                    self.faiss_index.load(self.index_path)
                    logger.info(f"Loaded existing index with {self.document_store.count()} documents")
                except Exception as e:
                    logger.error(f"Error loading existing index: {e}")
                    self.faiss_index.create()
            else:
                # Create new index
                self.faiss_index.create()
                logger.info(f"Created new {self.index_type} FAISS index")
        
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
                for doc in documents:
                    if "id" not in doc:
                        # Generate ID from content hash
                        import hashlib
                        doc_id = hashlib.md5(doc["content"].encode()).hexdigest()
                        doc["id"] = doc_id
                    doc_ids.append(doc["id"])
                
                # Get or compute embeddings
                embeddings = self.embedding_engine.encode([doc["content"] for doc in documents])
                
                # Add to FAISS index
                self.faiss_index.add_vectors(embeddings)
                
                # Get embedding IDs
                start_idx = self.faiss_index.count_vectors() - len(documents)
                embedding_ids = list(range(start_idx, start_idx + len(documents)))
                
                # Add to document store
                self.document_store.add(documents, embedding_ids)
                
                # Index for keyword search if enabled
                if self.enable_hybrid_search:
                    for i, doc in enumerate(documents):
                        embedding_idx = embedding_ids[i]
                        self.keyword_index.index_document(doc["id"], doc["content"], embedding_idx)
                    
                    # Save keyword index
                    self.keyword_index.save()
                
                return doc_ids
                
            except Exception as e:
                logger.error(f"Error adding documents: {e}")
                return []
    
    def update_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        """Update a document in the vector store with optimized updating.
        
        Args:
            doc_id: Document ID to update
            document: New document content
            
        Returns:
            True if successful
        """
        with self.write_lock:
            try:
                # Get the embedding ID
                embedding_id = self.document_store.get_embedding_id(doc_id)
                if embedding_id is None:
                    logger.error(f"Document not found: {doc_id}")
                    return False
                
                # Compute new embedding
                new_embedding = self.embedding_engine.encode(document["content"])
                
                # Update the index
                if self.index_type == "Flat":
                    # For Flat indices, we can potentially update in place
                    if self.faiss_index.replace_vector(new_embedding[0], embedding_id):
                        # Update document in document store
                        self.document_store.update(doc_id, document, embedding_id)
                        
                        # Update keyword index if hybrid search is enabled
                        if self.enable_hybrid_search:
                            # Remove old keywords
                            self.keyword_index.remove_document(embedding_id)
                            
                            # Add new keywords
                            self.keyword_index.index_document(doc_id, document["content"], embedding_id)
                            self.keyword_index.save()
                            
                        return True
                    else:
                        # Fallback: Delete and re-add
                        logger.debug(f"Falling back to delete-and-add for updating document {doc_id}")
                
                # For other index types or if direct replacement failed
                # Delete and re-add is the safest approach
                if self.delete_document(doc_id):
                    return self.add_documents([document])[0] == doc_id
                else:
                    return False
                    
            except Exception as e:
                logger.error(f"Error updating document: {e}")
                return False
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the vector store with optimized deletion.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful
        """
        with self.write_lock:
            try:
                # Get embedding ID
                embedding_id = self.document_store.get_embedding_id(doc_id)
                if embedding_id is None:
                    logger.error(f"Document not found: {doc_id}")
                    return False
                
                # With FAISS, we need to rebuild the index when deleting
                # Get current vector count
                vector_count = self.faiss_index.count_vectors()
                
                if vector_count <= 1:
                    # If this is the last document, just clear everything
                    self.document_store.clear()
                    self.faiss_index.create()
                    if self.enable_hybrid_search:
                        self.keyword_index.clear()
                        self.keyword_index.save()
                else:
                    # Otherwise we need to rebuild the index
                    # First remove from keyword index if enabled
                    if self.enable_hybrid_search:
                        self.keyword_index.remove_document(embedding_id)
                    
                    # Delete from document store
                    self.document_store.delete(doc_id)
                    
                    # Rebuild FAISS index
                    self.rebuild_index()
                
                return True
                
            except Exception as e:
                logger.error(f"Error deleting document: {e}")
                return False
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        hybrid_alpha: float = 0.5,  # Weight for vector search (1-hybrid_alpha for keyword)
        use_hybrid: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Search for documents by semantic similarity with hybrid search support.
        
        Args:
            query: Query string
            top_k: Number of results to return
            filters: Optional metadata filters
            hybrid_alpha: Weight for vector similarity (0.0-1.0)
            use_hybrid: Whether to use hybrid search (defaults to self.enable_hybrid_search)
            
        Returns:
            List of matching documents
        """
        # Determine whether to use hybrid search
        if use_hybrid is None:
            use_hybrid = self.enable_hybrid_search
            
        return self.search_engine.search(
            query=query,
            top_k=top_k,
            filters=filters,
            hybrid_alpha=hybrid_alpha,
            use_hybrid=use_hybrid
        )
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document or None if not found
        """
        return self.document_store.get(doc_id)
    
    def get_documents_by_metadata(self, metadata_key: str, metadata_value: Any) -> List[Dict[str, Any]]:
        """Get documents by metadata with support for nested fields.
        
        Args:
            metadata_key: Metadata key (can use dot notation for nested fields)
            metadata_value: Metadata value
            
        Returns:
            List of matching documents
        """
        return self.document_store.get_by_metadata(metadata_key, metadata_value)
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents.
        
        Returns:
            List of all documents
        """
        return self.document_store.get_all()
    
    def count_documents(self) -> int:
        """Get document count.
        
        Returns:
            Number of documents in the store
        """
        return self.document_store.count()
    
    def rebuild_index(self) -> bool:
        """Rebuild the FAISS index from scratch.
        
        Returns:
            True if successful
        """
        with self.write_lock:
            try:
                # Get all documents
                all_docs = self.document_store.get_all()
                
                if not all_docs:
                    logger.info("No documents to rebuild index")
                    return True
                
                # Extract content
                contents = [doc["content"] for doc in all_docs]
                
                # Compute embeddings
                embeddings = self.embedding_engine.encode(contents)
                
                # Create new index
                self.faiss_index.create(embeddings)  # Pass embeddings as training data for IVF
                
                # Add vectors
                self.faiss_index.add_vectors(embeddings)
                
                # Update document store with new embedding IDs
                for i, doc in enumerate(all_docs):
                    self.document_store.update(doc["id"], doc, i)
                
                # Rebuild keyword index if hybrid search is enabled
                if self.enable_hybrid_search:
                    self.keyword_index.clear()
                    for i, doc in enumerate(all_docs):
                        self.keyword_index.index_document(doc["id"], doc["content"], i)
                    self.keyword_index.save()
                
                # Save index
                self.faiss_index.save(self.index_path)
                
                logger.info(f"Successfully rebuilt index with {len(all_docs)} documents")
                return True
                
            except Exception as e:
                logger.error(f"Error rebuilding index: {e}")
                return False
    
    def get_index_info(self) -> Dict[str, Any]:
        """Get information about the index.
        
        Returns:
            Dictionary with index information
        """
        metadata = self.document_store.get_metadata()
        faiss_config = self.faiss_index.get_config()
        
        return {
            "index_type": self.index_type,
            "dimension": self.dimension,
            "distance_metric": self.distance_metric,
            "document_count": self.document_store.count(),
            "embedding_model": self.embedding_model_name,
            "hybrid_search_enabled": self.enable_hybrid_search,
            "memory_mapped": self.use_mmap,
            "gpu_acceleration": faiss_config.get("gpu_available", False),
            "created_at": metadata.get("created_at"),
            "updated_at": metadata.get("updated_at"),
            "version": metadata.get("version", "2.0.0")
        }


# For backward compatibility
class FAISSStore(EnhancedFAISSStore):
    """Backward compatibility wrapper around EnhancedFAISSStore."""
    
    def __init__(
        self,
        path: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        index_type: str = "Flat",
        distance_metric: str = "cosine"
    ):
        """Initialize the FAISS document store.
        
        Args:
            path: Path to store the index
            embedding_model: Model to use for embeddings
            dimension: Embedding dimension
            index_type: FAISS index type
            distance_metric: Distance metric for comparison
        """
        super().__init__(
            path=path,
            embedding_model=embedding_model,
            dimension=dimension,
            index_type=index_type,
            distance_metric=distance_metric,
            use_mmap=False,  # Disable memory mapping for compatibility
            enable_hybrid_search=False  # Disable hybrid search for compatibility
        )