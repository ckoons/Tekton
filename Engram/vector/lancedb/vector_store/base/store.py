"""
Base VectorStore implementation using LanceDB.

This module provides the core VectorStore class that integrates with LanceDB
for high-performance vector storage and similarity search.
"""

import os
import lancedb
from typing import Dict, List, Any, Optional, Union

from ..utils.logging import get_logger, log_versions, configure_path
from ..utils.metadata import MetadataCache
from ..embedding.simple import SimpleEmbedding
from ..operations.crud import (
    create_compartment, add_to_compartment, 
    save_compartment, delete_compartment
)
from ..search.text import text_search
from ..search.vector import vector_search, get_by_id

# Configure path to ensure imports work
configure_path()

# Get logger
logger = get_logger()


class VectorStore:
    """
    A vector store implementation using LanceDB for high-performance similarity search.
    Works well on Apple Silicon and CUDA-enabled hardware.
    """
    
    def __init__(self, 
                data_path: str = "vector_data", 
                dimension: int = 128,
                use_gpu: bool = False) -> None:
        """
        Initialize the vector store
        
        Args:
            data_path: Directory to store vector database
            dimension: Dimension of the vectors to store
            use_gpu: Whether to use GPU acceleration if available
        """
        self.data_path = data_path
        self.dimension = dimension
        self.use_gpu = use_gpu
        self.embedding = SimpleEmbedding(vector_size=dimension)
        self.db = None
        
        # Create data directory if it doesn't exist
        os.makedirs(data_path, exist_ok=True)
        
        # Initialize metadata cache manager
        self.metadata_cache = MetadataCache(data_path)
        
        # Initialize LanceDB
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize the LanceDB connection and check GPU availability."""
        try:
            # Connect to LanceDB
            # Use URI format for consistency and better path handling
            db_uri = f"file://{os.path.abspath(self.data_path)}"
            self.db = lancedb.connect(db_uri)
            logger.info(f"LanceDB initialized at {self.data_path}")
            
            # Log versions
            log_versions(logger)
            
            # Verify connection by listing tables
            _ = self.db.table_names()
            
            # Check for GPU acceleration
            if self.use_gpu:
                self._check_gpu_availability()
                
        except Exception as e:
            logger.error(f"Failed to initialize LanceDB: {e}")
            logger.error(f"Attempted to connect to: {self.data_path}")
            # Retry with a simpler approach as fallback
            try:
                self.db = lancedb.connect(self.data_path)
                logger.info(f"LanceDB initialized with fallback approach")
                _ = self.db.table_names()  # Verify connection
            except Exception as retry_error:
                logger.error(f"Fallback initialization also failed: {retry_error}")
                self.db = None
    
    def _check_gpu_availability(self) -> None:
        """Check if GPU acceleration is available."""
        try:
            import torch
            if torch.cuda.is_available():
                logger.info(f"GPU support available: {torch.cuda.get_device_name(0)}")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                logger.info(f"Apple Metal support available")
            else:
                logger.warning("No GPU support available for torch, using CPU")
                self.use_gpu = False
        except ImportError:
            logger.warning("PyTorch not available, using CPU mode")
            self.use_gpu = False
    
    def create_compartment(self, compartment: str) -> bool:
        """
        Create a new compartment (table in LanceDB)
        
        Args:
            compartment: Name of the compartment to create
            
        Returns:
            True if successful, False otherwise
        """
        if not self.db:
            logger.error("Database not initialized")
            return False
            
        return create_compartment(self.db, self.metadata_cache, compartment, self.dimension)
    
    def get_compartments(self) -> List[str]:
        """
        Get all compartment names
        
        Returns:
            List of compartment names
        """
        if not self.db:
            logger.error("Database not initialized")
            return []
            
        try:
            return self.db.table_names()
        except Exception as e:
            logger.error(f"Failed to get compartments: {e}")
            return []
    
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
        if not self.db:
            logger.error("Database not initialized")
            # Try to reinitialize the database
            try:
                self._initialize_db()
                if not self.db:
                    return []
            except Exception:
                return []
                
        if not texts:
            return []
            
        # Convert texts to embeddings
        embeddings = self.embedding.encode(texts).tolist()
        
        # Add to compartment
        return add_to_compartment(
            self.db, self.metadata_cache, compartment, texts, embeddings, metadatas
        )
    
    def save(self, compartment: str) -> bool:
        """
        Save the compartment explicitly (forces an immediate flush)
        
        Args:
            compartment: The compartment to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.db:
            logger.error("Database not initialized")
            return False
            
        try:
            if compartment not in self.get_compartments():
                logger.warning(f"Compartment '{compartment}' doesn't exist, nothing to save")
                return False
                
            return save_compartment(self.db, self.metadata_cache, compartment)
                
        except Exception as e:
            logger.error(f"Failed to save compartment '{compartment}': {e}")
            return False
    
    def text_search(self, query: str, compartment: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for text matches in the vector store
        
        Args:
            query: The search query
            compartment: The compartment to search in
            top_k: Number of results to return
            
        Returns:
            List of matching documents with metadata and scores
        """
        if not self.db:
            logger.error("Database not initialized")
            return []
            
        try:
            if compartment not in self.get_compartments():
                logger.warning(f"Compartment '{compartment}' doesn't exist")
                return []
                
            # Load metadata cache
            cache = self.metadata_cache.load(compartment)
            
            # Perform text search
            return text_search(cache, query, top_k)
                
        except Exception as e:
            logger.error(f"Failed to search in compartment '{compartment}': {e}")
            return []
    
    def vector_search(self, query: str, compartment: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar texts using vector similarity
        
        Args:
            query: The search query
            compartment: The compartment to search in
            top_k: Number of results to return
            
        Returns:
            List of matching documents with metadata and scores
        """
        if not self.db:
            logger.error("Database not initialized")
            return []
            
        try:
            if compartment not in self.get_compartments():
                logger.warning(f"Compartment '{compartment}' doesn't exist")
                return []
                
            # Create query embedding
            query_embedding = self.embedding.encode(query)[0].tolist()
            
            # Load metadata cache
            cache = self.metadata_cache.load(compartment)
            
            # Open LanceDB table
            db_table = self.db.open_table(compartment)
            
            # Perform vector search
            return vector_search(db_table, query_embedding, cache, top_k)
                
        except Exception as e:
            logger.error(f"Failed to perform vector search in compartment '{compartment}': {e}")
            return []
    
    def get_by_id(self, memory_id: int, compartment: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory by its ID
        
        Args:
            memory_id: The ID of the memory
            compartment: The compartment to look in
            
        Returns:
            The memory if found, None otherwise
        """
        if not self.db:
            logger.error("Database not initialized")
            return None
            
        try:
            if compartment not in self.get_compartments():
                logger.warning(f"Compartment '{compartment}' doesn't exist")
                return None
                
            # Load metadata cache
            cache = self.metadata_cache.load(compartment)
            
            # Open LanceDB table
            db_table = self.db.open_table(compartment)
            
            # Get memory by ID
            return get_by_id(db_table, memory_id, cache)
                
        except Exception as e:
            logger.error(f"Failed to get memory by ID in compartment '{compartment}': {e}")
            return None
    
    def delete(self, compartment: str) -> bool:
        """
        Delete a compartment and its files
        
        Args:
            compartment: The compartment to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.db:
            logger.error("Database not initialized")
            return False
            
        try:
            if compartment not in self.get_compartments():
                logger.warning(f"Compartment '{compartment}' doesn't exist")
                return False
                
            return delete_compartment(self.db, self.metadata_cache, compartment)
                
        except Exception as e:
            logger.error(f"Failed to delete compartment '{compartment}': {e}")
            return False