"""
FAISS vector store for Ergon.

This module provides a FAISS-based vector store for semantic search
of components and documentation.
"""

import os
import json
import pickle
import logging
from typing import List, Dict, Any, Optional, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer
else:
    # Create placeholder types for runtime when imports might fail
    np = None
    faiss = None
    SentenceTransformer = None
from pathlib import Path
from datetime import datetime
import threading
import hashlib

from ergon.utils.config.settings import settings

# Configure logger first
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))

# Check if dependencies might be available without importing them
FULL_FUNCTIONALITY_AVAILABLE = False

try:
    import importlib
    # Check all required packages are available
    faiss_spec = importlib.find_spec("faiss")
    numpy_spec = importlib.find_spec("numpy") 
    st_spec = importlib.find_spec("sentence_transformers")
    
    if faiss_spec and numpy_spec and st_spec:
        FULL_FUNCTIONALITY_AVAILABLE = True
        logger.info("FAISS vector store - dependencies available, will attempt full functionality")
    else:
        logger.info("FAISS vector store - missing dependencies, using lightweight fallback mode")
        FULL_FUNCTIONALITY_AVAILABLE = False
except Exception as e:
    logger.info(f"FAISS vector store - dependency check failed ({e}), using fallback mode")
    FULL_FUNCTIONALITY_AVAILABLE = False


class FAISSDocumentStore:
    """
    FAISS-based vector store for document and component storage.
    
    This class provides semantic search capabilities for Ergon
    components and documentation.
    """
    
    def __init__(
        self,
        path: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        index_type: str = "Flat",
        distance_metric: str = "cosine"
    ):
        """
        Initialize the FAISS document store.
        
        Args:
            path: Path to store the index
            embedding_model: Model to use for embeddings
            dimension: Embedding dimension
            index_type: FAISS index type
            distance_metric: Distance metric for comparison
        """
        self.path = path or settings.vector_db_path
        self.embedding_model_name = embedding_model
        self.dimension = dimension
        self.index_type = index_type
        self.distance_metric = distance_metric
        
        # Create directories if they don't exist
        os.makedirs(self.path, exist_ok=True)
        
        # Initialize index path
        self.index_path = os.path.join(self.path, "faiss.index")
        self.documents_path = os.path.join(self.path, "documents.pkl")
        
        # Initialize based on available functionality
        self.fallback_mode = not FULL_FUNCTIONALITY_AVAILABLE
        self.documents = {}  # In-memory document storage for fallback
        
        if FULL_FUNCTIONALITY_AVAILABLE:
            # Try to import and initialize dependencies at runtime
            try:
                # Import at runtime to avoid module-level NumPy errors
                import faiss
                import numpy as np
                from sentence_transformers import SentenceTransformer
                
                # Store for use in methods
                self.faiss = faiss
                self.np = np
                
                # Load embeddings model
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
                logger.info(f"FAISS store initialized with embedding model: {self.embedding_model_name}")
                
            except Exception as e:
                logger.warning(f"Error importing dependencies or loading model: {e}, switching to fallback mode")
                self.fallback_mode = True
                self.embedding_model = None
                self.faiss = None
                self.np = None
        else:
            logger.info("FAISS store running in lightweight fallback mode")
            self.embedding_model = None
            self.faiss = None
            self.np = None
        
        # Lock for thread safety
        self.write_lock = threading.RLock()
        
        # Initialize or load index
        if not self.fallback_mode:
            self._initialize_or_load_index()
        else:
            self._initialize_fallback_storage()
    
    def _initialize_fallback_storage(self):
        """Initialize lightweight fallback storage."""
        self.documents = {}
        self.document_embeddings = {}
        self.next_id = 0
        
        # Try to load existing fallback data
        fallback_path = os.path.join(self.path, "fallback_documents.json")
        if os.path.exists(fallback_path):
            try:
                with open(fallback_path, 'r') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', {})
                    self.document_embeddings = data.get('embeddings', {})
                    self.next_id = data.get('next_id', 0)
                logger.info(f"Loaded {len(self.documents)} documents from fallback storage")
            except Exception as e:
                logger.warning(f"Error loading fallback storage: {e}")
                self.documents = {}
                self.document_embeddings = {}
                self.next_id = 0
    
    def _simple_embedding(self, text: str) -> List[float]:
        """Simple fallback embedding using text hashing and features."""
        if not text:
            return [0.0] * self.dimension
        
        text = str(text).lower().strip()
        embedding = [0.0] * self.dimension
        
        # Hash-based features
        char_hash = hash(text) % (2**32)
        for i in range(min(self.dimension // 2, 32)):
            embedding[i] = ((char_hash >> i) & 1) * 2.0 - 1.0
        
        # Word-based features
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        
        if self.dimension > 32:
            embedding[32] = min(1.0, word_count / 50.0)
            embedding[33] = min(1.0, char_count / 500.0)
        
        # Simple word hashing
        for i, word in enumerate(words[:min(len(words), self.dimension - 50)]):
            idx = 50 + i
            if idx < self.dimension:
                word_hash = hash(word) % (2**16)
                embedding[idx] = (word_hash / (2**15)) - 1.0
        
        # Normalize
        magnitude = sum(x*x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def _save_fallback_data(self):
        """Save fallback data to JSON file."""
        try:
            fallback_path = os.path.join(self.path, "fallback_documents.json")
            data = {
                'documents': self.documents,
                'embeddings': self.document_embeddings,
                'next_id': self.next_id
            }
            with open(fallback_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Error saving fallback data: {e}")
    
    def _initialize_or_load_index(self):
        """Initialize or load FAISS index and documents."""
        # Load existing index and documents if available
        if os.path.exists(self.index_path) and os.path.exists(self.documents_path):
            try:
                self.index = self.faiss.read_index(self.index_path)
                with open(self.documents_path, "rb") as f:
                    self.documents = pickle.load(f)
                logger.info(f"Loaded existing index with {len(self.documents)} documents")
            except Exception as e:
                logger.error(f"Error loading existing index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index."""
        # Initialize empty documents list
        self.documents = []
        
        # Create a new index based on distance metric
        if self.distance_metric == "cosine":
            self.index = self.faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity with normalized vectors
        elif self.distance_metric == "l2":
            self.index = self.faiss.IndexFlatL2(self.dimension)  # L2 distance
        else:
            raise ValueError(f"Unsupported distance metric: {self.distance_metric}")
        
        logger.info("Created new FAISS index")
        
        # Save empty index
        self._save_index()
    
    def _save_index(self):
        """Save index and documents to disk."""
        with self.write_lock:
            try:
                # Save FAISS index
                self.faiss.write_index(self.index, self.index_path)
                
                # Save documents
                with open(self.documents_path, "wb") as f:
                    pickle.dump(self.documents, f)
                
                logger.info(f"Saved index with {len(self.documents)} documents")
            except Exception as e:
                logger.error(f"Error saving index: {e}")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add documents to the vector store.
        
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
                        doc_id = hashlib.md5(doc["content"].encode()).hexdigest()
                        doc["id"] = doc_id
                    doc_ids.append(doc["id"])
                
                if self.fallback_mode:
                    # Fallback mode: simple storage with basic embeddings
                    for doc in documents:
                        doc_id = doc["id"]
                        embedding = self._simple_embedding(doc["content"])
                        
                        self.documents[doc_id] = {
                            "id": doc_id,
                            "content": doc["content"],
                            "metadata": doc.get("metadata", {}),
                            "added_at": datetime.now().isoformat()
                        }
                        self.document_embeddings[doc_id] = embedding
                    
                    # Save fallback data
                    self._save_fallback_data()
                    
                else:
                    # Full FAISS mode
                    # Get or compute embeddings
                    embeddings = self._get_embeddings([doc["content"] for doc in documents])
                    
                    # Add to index
                    self.index.add(embeddings)
                    
                    # Add to documents list
                    for i, doc in enumerate(documents):
                        self.documents.append({
                            "id": doc["id"],
                            "content": doc["content"],
                            "metadata": doc.get("metadata", {}),
                            "embedding_id": len(self.documents) + i,
                            "added_at": datetime.now().isoformat()
                        })
                    
                    # Save updated index
                    self._save_index()
                
                return doc_ids
            except Exception as e:
                logger.error(f"Error adding documents: {e}")
                return []
    
    def update_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        """
        Update a document in the vector store.
        
        Args:
            doc_id: Document ID to update
            document: New document content
            
        Returns:
            True if successful
        """
        with self.write_lock:
            try:
                # Find document by ID
                doc_index = None
                for i, doc in enumerate(self.documents):
                    if doc["id"] == doc_id:
                        doc_index = i
                        break
                
                if doc_index is None:
                    logger.error(f"Document not found: {doc_id}")
                    return False
                
                # Get embedding ID
                embedding_id = self.documents[doc_index]["embedding_id"]
                
                # Compute new embedding
                new_embedding = self._get_embeddings([document["content"]])[0]
                
                # Update the index (requires rebuilding for FAISS)
                # This is inefficient for many updates, but works for occasional updates
                all_vectors = self.index.reconstruct_n(0, self.index.ntotal)
                all_vectors[embedding_id] = new_embedding
                
                # Create new index
                if self.distance_metric == "cosine":
                    new_index = self.faiss.IndexFlatIP(self.dimension)
                else:
                    new_index = self.faiss.IndexFlatL2(self.dimension)
                
                # Add vectors to new index
                new_index.add(all_vectors)
                
                # Replace old index
                self.index = new_index
                
                # Update document
                self.documents[doc_index] = {
                    "id": doc_id,
                    "content": document["content"],
                    "metadata": document.get("metadata", {}),
                    "embedding_id": embedding_id,
                    "updated_at": datetime.now().isoformat(),
                    "added_at": self.documents[doc_index].get("added_at")
                }
                
                # Save updated index
                self._save_index()
                
                return True
            except Exception as e:
                logger.error(f"Error updating document: {e}")
                return False
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the vector store.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful
        """
        with self.write_lock:
            try:
                # Find document by ID
                doc_index = None
                for i, doc in enumerate(self.documents):
                    if doc["id"] == doc_id:
                        doc_index = i
                        break
                
                if doc_index is None:
                    logger.error(f"Document not found: {doc_id}")
                    return False
                
                # For FAISS, deletion requires rebuilding the index
                # This is inefficient for many deletions, but works for occasional deletions
                
                # Get all vectors except the one to delete
                all_vectors = []
                new_documents = []
                
                for i, doc in enumerate(self.documents):
                    if doc["id"] != doc_id:
                        # Keep this document
                        vector = self.index.reconstruct(doc["embedding_id"])
                        all_vectors.append(vector)
                        
                        # Update embedding ID in the document
                        doc_copy = doc.copy()
                        doc_copy["embedding_id"] = len(all_vectors) - 1
                        new_documents.append(doc_copy)
                
                # Convert vectors to numpy array
                all_vectors = self.np.array(all_vectors)
                
                # Create new index
                if self.distance_metric == "cosine":
                    new_index = self.faiss.IndexFlatIP(self.dimension)
                else:
                    new_index = self.faiss.IndexFlatL2(self.dimension)
                
                # Add vectors to new index
                if len(all_vectors) > 0:
                    new_index.add(all_vectors)
                
                # Replace old index and documents
                self.index = new_index
                self.documents = new_documents
                
                # Save updated index
                self._save_index()
                
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
        """
        Search for documents by semantic similarity.
        
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
            
            # If no documents, return empty list
            if len(self.documents) == 0:
                return []
            
            # Search the index
            distances, indices = self.index.search(self.np.array([query_embedding]), top_k * 4)  # Get 4x results for filtering
            
            # Process results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < 0 or idx >= len(self.documents):
                    continue
                
                doc = self.documents[idx]
                
                # Apply filters if provided
                if filters and not self._matches_filters(doc, filters):
                    continue
                
                # Calculate score (convert distance to similarity score)
                if self.distance_metric == "cosine":
                    score = float(distances[0][i])  # Already a similarity score
                else:
                    # Convert L2 distance to similarity score (0-1 range)
                    distance = float(distances[0][i])
                    max_distance = 2.0  # Maximum L2 distance for normalized vectors
                    score = 1.0 - (distance / max_distance)
                
                results.append({
                    "id": doc["id"],
                    "content": doc["content"],
                    "metadata": doc.get("metadata", {}),
                    "score": score
                })
                
                # Stop after top_k actual results
                if len(results) >= top_k:
                    break
            
            return results
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def _matches_filters(self, doc: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if document matches filters."""
        metadata = doc.get("metadata", {})
        
        for key, value in filters.items():
            if key not in metadata:
                return False
            
            if isinstance(value, list):
                # List filter (any match)
                if metadata[key] not in value:
                    return False
            elif isinstance(value, dict):
                # Range filter
                for op, op_value in value.items():
                    if op == "gt" and not metadata[key] > op_value:
                        return False
                    elif op == "gte" and not metadata[key] >= op_value:
                        return False
                    elif op == "lt" and not metadata[key] < op_value:
                        return False
                    elif op == "lte" and not metadata[key] <= op_value:
                        return False
            else:
                # Exact match
                if metadata[key] != value:
                    return False
        
        return True
    
    def _get_embeddings(self, texts: List[str]) -> "np.ndarray":
        """Get embeddings for texts."""
        embeddings = self.embedding_model.encode(texts)
        
        # Normalize embeddings if using cosine similarity
        if self.distance_metric == "cosine":
            self.faiss.normalize_L2(embeddings)
        
        return embeddings
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document or None if not found
        """
        for doc in self.documents:
            if doc["id"] == doc_id:
                return {
                    "id": doc["id"],
                    "content": doc["content"],
                    "metadata": doc.get("metadata", {})
                }
        
        return None
    
    def get_documents_by_metadata(self, metadata_key: str, metadata_value: Any) -> List[Dict[str, Any]]:
        """
        Get documents by metadata.
        
        Args:
            metadata_key: Metadata key
            metadata_value: Metadata value
            
        Returns:
            List of matching documents
        """
        results = []
        for doc in self.documents:
            metadata = doc.get("metadata", {})
            if metadata_key in metadata and metadata[metadata_key] == metadata_value:
                results.append({
                    "id": doc["id"],
                    "content": doc["content"],
                    "metadata": metadata
                })
        
        return results
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get all documents.
        
        Returns:
            List of all documents
        """
        return [
            {
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc.get("metadata", {})
            }
            for doc in self.documents
        ]
    
    def count_documents(self) -> int:
        """
        Get document count.
        
        Returns:
            Number of documents in the store
        """
        return len(self.documents)
    
    def rebuild_index(self) -> bool:
        """
        Rebuild the FAISS index from scratch.
        
        Returns:
            True if successful
        """
        with self.write_lock:
            try:
                if not self.documents:
                    logger.info("No documents to rebuild index")
                    return True
                
                # Extract content for all documents
                contents = [doc["content"] for doc in self.documents]
                
                # Compute embeddings
                embeddings = self._get_embeddings(contents)
                
                # Create new index
                if self.distance_metric == "cosine":
                    new_index = self.faiss.IndexFlatIP(self.dimension)
                else:
                    new_index = self.faiss.IndexFlatL2(self.dimension)
                
                # Add vectors to new index
                new_index.add(embeddings)
                
                # Replace old index
                self.index = new_index
                
                # Update embedding IDs
                for i, doc in enumerate(self.documents):
                    doc["embedding_id"] = i
                
                # Save updated index
                self._save_index()
                
                logger.info(f"Successfully rebuilt index with {len(self.documents)} documents")
                return True
            except Exception as e:
                logger.error(f"Error rebuilding index: {e}")
                return False


# Create singleton instance with error handling
faiss_store = None
try:
    faiss_store = FAISSDocumentStore()
    logger.info("FAISS store singleton created successfully")
except Exception as e:
    logger.warning(f"Error creating FAISS store singleton: {e}")
    # Create a minimal fallback 
    faiss_store = None