#!/usr/bin/env python
"""
An adapter for Engram that provides memory operations using FAISS vector search.
This implementation doesn't require SentenceTransformers or other libraries 
that have NumPy version conflicts.

This can be used as a drop-in replacement for Engram's memory module.
"""

import os
import re
import json
import logging
import time
from typing import List, Dict, Any, Optional, Union, Tuple

# Import our vector store implementation
from vector_store import VectorStore

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("engram_memory_adapter")

class MemoryService:
    """
    A memory service for Engram that uses FAISS vector store for 
    semantic search with NumPy 2.x compatibility.
    
    This mimics the API of Engram's original MemoryService but
    uses a different implementation that's compatible with NumPy 2.x.
    """
    
    def __init__(self, 
                 client_id: str = "default",
                 memory_dir: str = "memories",
                 vector_dimension: int = 128,
                 use_gpu: bool = False,
                 data_dir: Optional[str] = None) -> None:
        """
        Initialize the memory service
        
        Args:
            client_id: Unique identifier for the client
            memory_dir: Directory to store memory data
            vector_dimension: Dimension of the embeddings
            use_gpu: Whether to use GPU for FAISS if available
            data_dir: Optional data directory
        """
        self.client_id = client_id
        self.memory_dir = memory_dir
        self.vector_dimension = vector_dimension
        
        # Create the vector store
        self.vector_store = VectorStore(
            data_path=memory_dir,
            dimension=vector_dimension,
            use_gpu=use_gpu
        )
        
        logger.info(f"MemoryService initialized with client_id={client_id}, vector_dimension={vector_dimension}")
    
    def _ensure_compartment(self, compartment_id: str) -> None:
        """Ensure the compartment exists"""
        if compartment_id not in self.vector_store.get_compartments():
            # Try to load the compartment from disk
            loaded = self.vector_store.load(compartment_id)
            if not loaded:
                # Create an empty compartment
                self.vector_store.add(compartment_id, [""], [{"placeholder": True}])
                # Save it so it exists on disk
                self.vector_store.save(compartment_id)
                # Delete the placeholder
                self.vector_store.delete(compartment_id)
    
    def store(self, 
              memory_text: str, 
              compartment_id: str, 
              metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Store a memory with optional metadata
        
        Args:
            memory_text: The text to remember
            compartment_id: The compartment to store in
            metadata: Optional metadata to associate with the memory
            
        Returns:
            ID of the stored memory
        """
        if not metadata:
            metadata = {}
        
        # Store the memory
        ids = self.vector_store.add(
            compartment=compartment_id,
            texts=[memory_text],
            metadatas=[metadata]
        )
        
        # Save the compartment
        self.vector_store.save(compartment_id)
        
        logger.info(f"Stored memory in compartment '{compartment_id}' with ID {ids[0]}")
        return ids[0]
    
    def search(self, 
               query: str, 
               compartment_id: str, 
               limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memories by exact text match
        
        Args:
            query: The text to search for
            compartment_id: The compartment to search in
            limit: Maximum number of results to return
            
        Returns:
            List of matching memories
        """
        # Ensure compartment exists
        self._ensure_compartment(compartment_id)
        
        # Convert to lowercase for case-insensitive matching
        query_lower = query.lower()
        
        results = []
        for entry in self.vector_store.metadata.get(compartment_id, []):
            if query_lower in entry["text"].lower():
                # Format the result
                results.append({
                    "id": entry["id"],
                    "text": entry["text"],
                    "score": 1.0,  # Exact match gets perfect score
                    "metadata": {k: v for k, v in entry.items() 
                                if k not in ["id", "text", "timestamp"]}
                })
            
            if len(results) >= limit:
                break
        
        return results
    
    def semantic_search(self, 
                        query: str, 
                        compartment_id: str, 
                        limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memories by semantic similarity
        
        Args:
            query: The text to search for
            compartment_id: The compartment to search in
            limit: Maximum number of results to return
            
        Returns:
            List of matching memories with similarity scores
        """
        # Ensure compartment exists
        self._ensure_compartment(compartment_id)
        
        # Use vector search
        results = self.vector_store.search(
            compartment=compartment_id,
            query=query,
            top_k=limit
        )
        
        return results
    
    def search_by_metadata(self, 
                           metadata_key: str,
                           metadata_value: Any,
                           compartment_id: str,
                           limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memories by metadata
        
        Args:
            metadata_key: The metadata key to match
            metadata_value: The metadata value to match
            compartment_id: The compartment to search in
            limit: Maximum number of results to return
            
        Returns:
            List of matching memories
        """
        # Ensure compartment exists
        self._ensure_compartment(compartment_id)
        
        results = []
        for entry in self.vector_store.metadata.get(compartment_id, []):
            # Check if the metadata matches
            entry_metadata = {k: v for k, v in entry.items() 
                             if k not in ["id", "text", "timestamp"]}
            
            if metadata_key in entry_metadata and entry_metadata[metadata_key] == metadata_value:
                # Format the result
                results.append({
                    "id": entry["id"],
                    "text": entry["text"],
                    "score": 1.0,  # Exact match gets perfect score
                    "metadata": entry_metadata
                })
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_compartments(self) -> List[str]:
        """Get all compartment IDs"""
        return self.vector_store.get_compartments()
    
    def delete_compartment(self, compartment_id: str) -> bool:
        """Delete a compartment"""
        return self.vector_store.delete(compartment_id)
    
    def get_memory_by_id(self, 
                         memory_id: int, 
                         compartment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory by its ID
        
        Args:
            memory_id: The ID of the memory
            compartment_id: The compartment to look in
            
        Returns:
            The memory if found, None otherwise
        """
        # Ensure compartment exists
        self._ensure_compartment(compartment_id)
        
        for entry in self.vector_store.metadata.get(compartment_id, []):
            if entry["id"] == memory_id:
                return {
                    "id": entry["id"],
                    "text": entry["text"],
                    "metadata": {k: v for k, v in entry.items() 
                                if k not in ["id", "text", "timestamp"]}
                }
        
        return None


# Example usage
if __name__ == "__main__":
    # Create memory service
    memory = MemoryService(memory_dir="./test_memories", vector_dimension=64)
    
    # Store some memories
    memory.store("Python is a popular programming language", "general", 
                {"category": "technology", "topic": "programming"})
    
    memory.store("Artificial intelligence is revolutionizing many industries", "general", 
                {"category": "technology", "topic": "ai"})
    
    memory.store("Vector search allows for semantic matching", "general", 
                {"category": "technology", "topic": "search"})
    
    memory.store("FAISS is a library for efficient similarity search", "general", 
                {"category": "technology", "topic": "search"})
    
    memory.store("The weather in San Francisco is often foggy", "general", 
                {"category": "weather", "location": "San Francisco"})
    
    # Test semantic search
    print("Semantic search results for 'How do vector databases work?':")
    results = memory.semantic_search("How do vector databases work?", "general", 3)
    for i, result in enumerate(results):
        print(f"  {i+1}. [{result['score']:.2f}] {result['text']}")
        print(f"     Metadata: {result['metadata']}")
    
    # Test exact search
    print("\nExact search results for 'FAISS':")
    results = memory.search("FAISS", "general", 3)
    for i, result in enumerate(results):
        print(f"  {i+1}. [{result['score']:.2f}] {result['text']}")
        print(f"     Metadata: {result['metadata']}")
    
    # Test metadata search
    print("\nMetadata search results for topic=search:")
    results = memory.search_by_metadata("topic", "search", "general", 3)
    for i, result in enumerate(results):
        print(f"  {i+1}. [{result['score']:.2f}] {result['text']}")
        print(f"     Metadata: {result['metadata']}")
    
    # Test get by ID
    memory_id = results[0]["id"]
    print(f"\nGet memory by ID {memory_id}:")
    memory_result = memory.get_memory_by_id(memory_id, "general")
    print(f"  Text: {memory_result['text']}")
    print(f"  Metadata: {memory_result['metadata']}")