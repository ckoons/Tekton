"""
Memory-focused vector database operations.

This module provides a vector store service specifically optimized
for memory storage and retrieval, leveraging Tekton's shared 
hardware-optimized vector store implementation.
"""

import os
import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path

from ergon.utils.config.settings import settings
from ergon.core.vector_store.faiss_store import FAISSDocumentStore

# Configure logger
logger = logging.getLogger(__name__)

class MemoryVectorService:
    """Memory-focused vector database operations."""
    
    def __init__(self, namespace: str):
        """
        Initialize the memory vector service.
        
        Args:
            namespace: Namespace for memory isolation (typically agent_id)
        """
        self.namespace = namespace
        self.collection_name = f"memory_{namespace}"
        
        # Initialize vector store and embedding service
        self.vector_store = FAISSDocumentStore(
            path=os.path.join(settings.tekton_home, "memory_vectors"),
            embedding_model=settings.embedding_model
        )
        
        logger.info(f"Initialized memory vector service with namespace: {namespace}")
    
    async def add_memory(self, 
                       content: str, 
                       embedding: List[float], 
                       metadata: Dict[str, Any]) -> str:
        """
        Add a memory with embedding to the vector store.
        
        Args:
            content: Memory content text
            embedding: Pre-computed embedding vector
            metadata: Metadata for the memory
            
        Returns:
            Memory ID
        """
        # Generate a unique ID for the memory
        memory_id = f"mem_{metadata.get('timestamp', int(time.time()))}_{uuid.uuid4().hex[:8]}"
        
        # Add namespace to metadata
        full_metadata = {**metadata, "namespace": self.namespace}
        
        # Add to vector store
        self.vector_store.add_documents([{
            "id": memory_id,
            "content": content,
            "metadata": full_metadata
        }])
        
        return memory_id
    
    async def search(self, 
                   query_embedding: List[float], 
                   filter_dict: Dict[str, Any] = None,
                   limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar memories.
        
        Args:
            query_embedding: Query embedding vector
            filter_dict: Optional metadata filters
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        # Ensure namespace filter is applied
        filter_dict = filter_dict or {}
        filter_dict["namespace"] = self.namespace
        
        # Search vector store
        results = self.vector_store.search(
            query="",  # Not used when using custom embedding
            top_k=limit,
            filters=filter_dict,
            custom_embedding=query_embedding
        )
        
        return results
    
    async def delete(self, memory_ids: List[str]) -> bool:
        """
        Delete memories by IDs.
        
        Args:
            memory_ids: List of memory IDs to delete
            
        Returns:
            True if successful
        """
        if not memory_ids:
            return True
            
        success = True
        for memory_id in memory_ids:
            if not self.vector_store.delete_document(memory_id):
                success = False
        
        return success
    
    async def get_by_category(self, 
                           category: str, 
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get memories by category.
        
        Args:
            category: Memory category
            limit: Maximum number of results
            
        Returns:
            List of memories
        """
        filters = {
            "namespace": self.namespace,
            "category": category
        }
        
        # This is inefficient but FAISS doesn't support retrieving by metadata only
        # For a production implementation, consider a hybrid approach with a metadata index
        docs = self.vector_store.get_documents_by_metadata("category", category)
        
        # Filter by namespace
        docs = [doc for doc in docs if doc.get("metadata", {}).get("namespace") == self.namespace]
        
        # Sort by timestamp (most recent first)
        docs = sorted(
            docs, 
            key=lambda x: x.get("metadata", {}).get("timestamp", 0), 
            reverse=True
        )[:limit]
        
        return docs
    
    async def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most recent memories.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of memories
        """
        # Get all documents for this namespace
        all_docs = self.vector_store.get_all_documents()
        
        # Filter by namespace
        namespace_docs = [
            doc for doc in all_docs 
            if doc.get("metadata", {}).get("namespace") == self.namespace
        ]
        
        # Sort by timestamp (most recent first)
        recent_docs = sorted(
            namespace_docs, 
            key=lambda x: x.get("metadata", {}).get("timestamp", 0), 
            reverse=True
        )[:limit]
        
        return recent_docs