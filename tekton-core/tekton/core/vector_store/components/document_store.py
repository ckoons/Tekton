"""Document Store Component for Vector Store.

This module provides document storage and management for the Vector Store.
"""

import os
import json
import pickle
import logging
import hashlib
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)


class DocumentStore:
    """
    Document storage and management with metadata handling and persistence.
    """

    def __init__(self, path: str):
        """Initialize the document store.
        
        Args:
            path: Path to store the documents
        """
        self.path = path
        
        # Initialize paths
        self.documents_path = os.path.join(self.path, "documents.pkl")
        self.metadata_path = os.path.join(self.path, "metadata.json")
        self.id_map_path = os.path.join(self.path, "id_map.json")
        
        # Initialize internal state
        self.documents = []
        self.id_map = {}  # Maps document IDs to embedding IDs
        self.metadata = {
            "version": "2.0.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "document_count": 0
        }
        
        # Create directories if they don't exist
        os.makedirs(self.path, exist_ok=True)
        
        # Load existing data if available
        self._load()
        
    def _load(self):
        """Load documents and metadata from disk."""
        try:
            # Load documents if available
            if os.path.exists(self.documents_path):
                with open(self.documents_path, "rb") as f:
                    self.documents = pickle.load(f)
                    
            # Load ID map if available
            if os.path.exists(self.id_map_path):
                with open(self.id_map_path, "r") as f:
                    self.id_map = json.load(f)
            else:
                # Generate ID map from documents (backward compatibility)
                self.id_map = {doc["id"]: idx for idx, doc in enumerate(self.documents)}
                    
            # Load metadata if available
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, "r") as f:
                    self.metadata = json.load(f)
                    
            # Update document count in case it's out of sync
            self.metadata["document_count"] = len(self.documents)
                
            logger.info(f"Loaded {len(self.documents)} documents from {self.path}")
                
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            
    def save(self):
        """Save documents and metadata to disk."""
        try:
            # Save documents
            with open(self.documents_path, "wb") as f:
                pickle.dump(self.documents, f)
                
            # Save ID map
            with open(self.id_map_path, "w") as f:
                json.dump(self.id_map, f)
                
            # Update metadata
            self.metadata["document_count"] = len(self.documents)
            self.metadata["updated_at"] = datetime.now().isoformat()
                
            # Save metadata
            with open(self.metadata_path, "w") as f:
                json.dump(self.metadata, f)
                
            logger.info(f"Saved {len(self.documents)} documents to {self.path}")
                
        except Exception as e:
            logger.error(f"Error saving documents: {e}")
            
    def add(self, documents: List[Dict[str, Any]], embedding_ids: Optional[List[int]] = None) -> List[str]:
        """Add documents to the store.
        
        Args:
            documents: List of document dictionaries
            embedding_ids: Optional list of embedding IDs to associate with documents
            
        Returns:
            List of document IDs
        """
        if not documents:
            return []
            
        try:
            doc_ids = []
            
            # Generate document IDs if not provided
            for i, doc in enumerate(documents):
                if "id" not in doc:
                    # Generate ID from content hash
                    doc_id = hashlib.md5(doc["content"].encode()).hexdigest()
                    doc["id"] = doc_id
                doc_ids.append(doc["id"])
                
                # Add to documents with embedding ID if provided
                doc_copy = doc.copy()
                if embedding_ids and i < len(embedding_ids):
                    embedding_id = embedding_ids[i]
                    doc_copy["embedding_id"] = embedding_id
                    self.id_map[doc["id"]] = embedding_id
                else:
                    # Use fallback embedding ID (document index)
                    embedding_id = len(self.documents) + i
                    doc_copy["embedding_id"] = embedding_id
                    self.id_map[doc["id"]] = embedding_id
                    
                # Add timestamp if not present
                if "added_at" not in doc_copy:
                    doc_copy["added_at"] = datetime.now().isoformat()
                    
                # Ensure metadata exists
                if "metadata" not in doc_copy:
                    doc_copy["metadata"] = {}
                    
                self.documents.append(doc_copy)
                
            # Save to disk
            self.save()
            
            return doc_ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return []
            
    def update(self, doc_id: str, document: Dict[str, Any], embedding_id: Optional[int] = None) -> bool:
        """Update a document in the store.
        
        Args:
            doc_id: Document ID to update
            document: New document content
            embedding_id: Optional new embedding ID
            
        Returns:
            True if successful
        """
        try:
            # Find document in ID map
            if doc_id not in self.id_map:
                logger.error(f"Document not found: {doc_id}")
                return False
                
            # Get current embedding ID
            current_embedding_id = self.id_map[doc_id]
                
            # Find document in documents list
            doc_index = None
            for i, doc in enumerate(self.documents):
                if doc["id"] == doc_id:
                    doc_index = i
                    break
                    
            if doc_index is None:
                logger.error(f"Document not found in documents list: {doc_id}")
                return False
                
            # Create updated document
            updated_doc = {
                "id": doc_id,
                "content": document["content"],
                "metadata": document.get("metadata", {}),
                "embedding_id": embedding_id if embedding_id is not None else current_embedding_id,
                "updated_at": datetime.now().isoformat(),
                "added_at": self.documents[doc_index].get("added_at")
            }
                
            # Update document
            self.documents[doc_index] = updated_doc
                
            # Update ID map if embedding ID changed
            if embedding_id is not None and embedding_id != current_embedding_id:
                self.id_map[doc_id] = embedding_id
                
            # Save to disk
            self.save()
                
            return True
                
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
            
    def delete(self, doc_id: str) -> bool:
        """Delete a document from the store.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            # Find document in ID map
            if doc_id not in self.id_map:
                logger.error(f"Document not found: {doc_id}")
                return False
                
            # Find document in documents list
            doc_index = None
            for i, doc in enumerate(self.documents):
                if doc["id"] == doc_id:
                    doc_index = i
                    break
                    
            if doc_index is None:
                logger.error(f"Document not found in documents list: {doc_id}")
                return False
                
            # Remove document
            del self.documents[doc_index]
                
            # Remove from ID map
            del self.id_map[doc_id]
                
            # Save to disk
            self.save()
                
            return True
                
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
            
    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document or None if not found
        """
        # Check if document exists in ID map
        if doc_id not in self.id_map:
            return None
            
        # Find document in documents list
        for doc in self.documents:
            if doc["id"] == doc_id:
                return doc.copy()
                
        return None
        
    def get_embedding_id(self, doc_id: str) -> Optional[int]:
        """Get embedding ID for document.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Embedding ID or None if not found
        """
        return self.id_map.get(doc_id)
        
    def get_doc_id_by_embedding_id(self, embedding_id: int) -> Optional[str]:
        """Get document ID for embedding ID.
        
        Args:
            embedding_id: Embedding ID
            
        Returns:
            Document ID or None if not found
        """
        for doc_id, emb_id in self.id_map.items():
            if emb_id == embedding_id:
                return doc_id
                
        return None
        
    def get_by_metadata(self, key: str, value: Any) -> List[Dict[str, Any]]:
        """Get documents by metadata field.
        
        Args:
            key: Metadata key (can use dot notation for nested fields)
            value: Metadata value
            
        Returns:
            List of matching documents
        """
        results = []
        
        for doc in self.documents:
            metadata = doc.get("metadata", {})
            
            # Handle nested paths with dot notation
            if "." in key:
                parts = key.split(".")
                current = metadata
                found = True
                
                for part in parts[:-1]:
                    if part not in current or not isinstance(current[part], dict):
                        found = False
                        break
                    current = current[part]
                
                if found:
                    final_key = parts[-1]
                    if final_key in current and current[final_key] == value:
                        results.append(doc.copy())
            else:
                # Regular non-nested field
                if key in metadata and metadata[key] == value:
                    results.append(doc.copy())
        
        return results
        
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all documents.
        
        Returns:
            List of all documents
        """
        return [doc.copy() for doc in self.documents]
        
    def count(self) -> int:
        """Get document count.
        
        Returns:
            Number of documents in the store
        """
        return len(self.documents)
        
    def get_metadata(self) -> Dict[str, Any]:
        """Get store metadata.
        
        Returns:
            Dictionary with store metadata
        """
        return self.metadata.copy()
        
    def clear(self) -> bool:
        """Clear all documents.
        
        Returns:
            True if successful
        """
        try:
            self.documents = []
            self.id_map = {}
            self.save()
            return True
        except Exception as e:
            logger.error(f"Error clearing documents: {e}")
            return False