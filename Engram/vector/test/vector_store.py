#!/usr/bin/env python
"""
Simple vector database using FAISS for semantic search with NumPy 2.x compatibility.
"""

import os
import json
import time
import logging
import faiss
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from simple_embedding import SimpleEmbedding

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vector_store")

class VectorStore:
    """
    A simple vector store using FAISS for high-performance similarity search.
    Works with NumPy 2.x and doesn't require SentenceTransformers or other
    libraries with potential NumPy version conflicts.
    """
    
    def __init__(self, 
                 data_path: str = "vector_data",
                 dimension: int = 128,
                 use_gpu: bool = False) -> None:
        """
        Initialize the vector store
        
        Args:
            data_path: Directory to store vector indices and metadata
            dimension: Dimension of the vectors to store
            use_gpu: Whether to use GPU for FAISS if available
        """
        self.data_path = data_path
        self.dimension = dimension
        self.use_gpu = use_gpu
        self.indices: Dict[str, Any] = {}
        self.metadata: Dict[str, List[Dict[str, Any]]] = {}
        self.embedding = SimpleEmbedding(vector_size=dimension)
        
        # Create data directory if it doesn't exist
        os.makedirs(data_path, exist_ok=True)
        
        logger.info(f"VectorStore initialized with dimension {dimension}")
        logger.info(f"NumPy version: {np.__version__}")
        logger.info(f"FAISS version: {faiss.__version__}")
        
        # Check if GPU is available when requested
        if use_gpu:
            try:
                if faiss.get_num_gpus() > 0:
                    logger.info(f"FAISS GPU support enabled: {faiss.get_num_gpus()} GPUs")
                else:
                    logger.warning("No GPUs available for FAISS, falling back to CPU")
                    self.use_gpu = False
            except:
                logger.warning("FAISS GPU support not available, falling back to CPU")
                self.use_gpu = False
        
    def _create_index(self, compartment: str) -> faiss.Index:
        """Create a new FAISS index for the given compartment"""
        # Create a flat index (exact search)
        index = faiss.IndexFlatL2(self.dimension)
        
        # Optionally move to GPU
        if self.use_gpu:
            try:
                res = faiss.StandardGpuResources()
                index = faiss.index_cpu_to_gpu(res, 0, index)
                logger.info(f"Created GPU FAISS index for '{compartment}'")
            except Exception as e:
                logger.warning(f"Failed to move index to GPU: {str(e)}")
        else:
            logger.info(f"Created CPU FAISS index for '{compartment}'")
            
        return index
    
    def _ensure_compartment(self, compartment: str) -> None:
        """Ensure the compartment exists, creating it if necessary"""
        if compartment not in self.indices:
            self.indices[compartment] = self._create_index(compartment)
            self.metadata[compartment] = []
            logger.info(f"Created new compartment '{compartment}'")
    
    def _get_index_path(self, compartment: str) -> str:
        """Get the path for storing a compartment's index"""
        return os.path.join(self.data_path, f"{compartment}.index")
    
    def _get_metadata_path(self, compartment: str) -> str:
        """Get the path for storing a compartment's metadata"""
        return os.path.join(self.data_path, f"{compartment}.json")
    
    def save(self, compartment: str) -> None:
        """Save the compartment to disk"""
        if compartment not in self.indices:
            logger.warning(f"Compartment '{compartment}' doesn't exist, nothing to save")
            return
        
        index_path = self._get_index_path(compartment)
        metadata_path = self._get_metadata_path(compartment)
        
        # FAISS CPU index for saving
        index = self.indices[compartment]
        if self.use_gpu:
            index = faiss.index_gpu_to_cpu(index)
        
        # Save index
        faiss.write_index(index, index_path)
        
        # Save metadata
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata[compartment], f)
        
        logger.info(f"Saved compartment '{compartment}' to {index_path} and {metadata_path}")
    
    def load(self, compartment: str) -> bool:
        """Load a compartment from disk"""
        index_path = self._get_index_path(compartment)
        metadata_path = self._get_metadata_path(compartment)
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            logger.warning(f"Compartment '{compartment}' files not found")
            return False
        
        try:
            # Load index
            index = faiss.read_index(index_path)
            
            # Optionally move to GPU
            if self.use_gpu:
                try:
                    res = faiss.StandardGpuResources()
                    index = faiss.index_cpu_to_gpu(res, 0, index)
                except Exception as e:
                    logger.warning(f"Failed to move index to GPU: {str(e)}")
            
            # Load metadata
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Store in memory
            self.indices[compartment] = index
            self.metadata[compartment] = metadata
            
            logger.info(f"Loaded compartment '{compartment}' with {len(metadata)} items")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load compartment '{compartment}': {str(e)}")
            return False
    
    def get_compartments(self) -> List[str]:
        """Get all compartment names"""
        return list(self.indices.keys())
    
    def add(self, compartment: str, texts: List[str], 
            metadatas: Optional[List[Dict[str, Any]]] = None) -> List[int]:
        """
        Add texts and their metadata to the vector store
        
        Args:
            compartment: The compartment to add to
            texts: The texts to add
            metadatas: Optional metadata associated with each text
            
        Returns:
            List of IDs assigned to the added texts
        """
        if not texts:
            return []
        
        # Ensure metadata is provided for each text
        if metadatas is None:
            metadatas = [{} for _ in texts]
        elif len(metadatas) != len(texts):
            raise ValueError(f"Number of texts ({len(texts)}) and metadata ({len(metadatas)}) must match")
        
        # Ensure compartment exists
        self._ensure_compartment(compartment)
        
        # Convert texts to embeddings
        embeddings = self.embedding.encode(texts)
        
        # Current count in the index
        start_id = len(self.metadata[compartment])
        
        # Add embeddings to the index
        self.indices[compartment].add(embeddings)
        
        # Store metadata with generated IDs
        ids = list(range(start_id, start_id + len(texts)))
        
        # Add timestamp to metadata
        timestamp = time.time()
        for i, (text, meta) in enumerate(zip(texts, metadatas)):
            # Store the original text, metadata, and timestamp
            entry = {
                "id": ids[i],
                "text": text,
                "timestamp": timestamp,
                **meta
            }
            self.metadata[compartment].append(entry)
        
        logger.info(f"Added {len(texts)} texts to compartment '{compartment}'")
        return ids
    
    def search(self, compartment: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar texts in the vector store
        
        Args:
            compartment: The compartment to search in
            query: The search query
            top_k: Number of results to return
            
        Returns:
            List of matching documents with metadata and scores
        """
        if compartment not in self.indices:
            logger.warning(f"Compartment '{compartment}' doesn't exist")
            return []
        
        # Create query embedding
        query_embedding = self.embedding.encode(query)
        
        # Search the index
        distances, indices = self.indices[compartment].search(query_embedding, top_k)
        
        # Format results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            # Skip invalid indices
            if idx < 0 or idx >= len(self.metadata[compartment]):
                continue
                
            # Get metadata
            metadata = self.metadata[compartment][idx]
            
            # Calculate score (convert distance to similarity score)
            # FAISS returns L2 distance, so we convert to a similarity score
            # where 1.0 is most similar and 0.0 is least similar
            max_distance = 100.0  # Arbitrary max distance to normalize
            score = max(0.0, 1.0 - (distance / max_distance))
            
            # Add to results
            results.append({
                "id": metadata["id"],
                "text": metadata["text"],
                "score": score,
                "metadata": {k: v for k, v in metadata.items() 
                             if k not in ["id", "text"]}
            })
        
        return results
    
    def delete(self, compartment: str) -> bool:
        """Delete a compartment and its files"""
        if compartment not in self.indices:
            logger.warning(f"Compartment '{compartment}' doesn't exist")
            return False
        
        # Delete files
        index_path = self._get_index_path(compartment)
        metadata_path = self._get_metadata_path(compartment)
        
        if os.path.exists(index_path):
            os.remove(index_path)
        
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        
        # Remove from memory
        del self.indices[compartment]
        del self.metadata[compartment]
        
        logger.info(f"Deleted compartment '{compartment}'")
        return True


# Example usage
if __name__ == "__main__":
    # Create a vector store
    store = VectorStore(dimension=64)
    
    # Add some texts to the "test" compartment
    texts = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is a subset of artificial intelligence",
        "Vector search allows semantic matching of text",
        "Python is a popular programming language for data science",
        "FAISS is a library for efficient similarity search"
    ]
    metadatas = [
        {"category": "phrase", "source": "common"},
        {"category": "definition", "source": "ml"},
        {"category": "technology", "source": "search"},
        {"category": "technology", "source": "programming"},
        {"category": "technology", "source": "search"}
    ]
    
    store.add("test", texts, metadatas)
    
    # Search for similar texts
    query = "How do I find similar text documents?"
    results = store.search("test", query, top_k=3)
    
    print(f"Search results for: '{query}'")
    for i, result in enumerate(results):
        print(f"  {i+1}. [{result['score']:.2f}] {result['text']}")
        print(f"     Metadata: {result['metadata']}")
    
    # Save the compartment
    store.save("test")
    
    # Create a new store and load the saved compartment
    new_store = VectorStore(dimension=64)
    new_store.load("test")
    
    # Verify the data was loaded correctly
    print("\nVerifying loaded data:")
    print(f"Compartments: {new_store.get_compartments()}")
    print(f"Items in 'test': {len(new_store.metadata['test'])}")