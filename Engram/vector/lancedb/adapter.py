#!/usr/bin/env python
"""
LanceDB Adapter for Engram Memory System

This module provides the adapter layer between Engram's memory system and LanceDB.
It implements the same interface as the FAISS adapter for easy swapping.
"""

import os
import sys
import logging
import time
import json
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("lancedb_adapter")

# Path handling for imports
ENGRAM_DIR = str(Path(__file__).parent.parent.parent)
if ENGRAM_DIR not in sys.path:
    sys.path.insert(0, ENGRAM_DIR)
    logger.debug(f"Added {ENGRAM_DIR} to Python path")

# Import vector_store module once it's created
try:
    from vector.lancedb.vector_store import VectorStore
    logger.info("Imported LanceDB vector store")
except ImportError:
    logger.warning("LanceDB vector store module not found")
    VectorStore = None

class LanceDBAdapter:
    """
    LanceDB Adapter for Engram Memory System.
    
    This adapter provides vector database operations using LanceDB,
    which offers excellent performance on both Apple Silicon and CUDA-enabled hardware.
    """
    
    def __init__(self, 
                 client_id: str = "default",
                 memory_dir: str = "memories",
                 vector_dimension: int = 128,
                 use_gpu: bool = False) -> None:
        """
        Initialize the LanceDB adapter.
        
        Args:
            client_id: Unique identifier for the client
            memory_dir: Directory to store memory data
            vector_dimension: Dimension of the embeddings
            use_gpu: Whether to use GPU acceleration when available
        """
        self.client_id = client_id
        self.memory_dir = memory_dir
        self.vector_dimension = vector_dimension
        self.use_gpu = use_gpu
        
        # Initialize LanceDB vector store
        if VectorStore:
            try:
                # Ensure directory exists
                vector_path = os.path.join(memory_dir, "lancedb")
                os.makedirs(vector_path, exist_ok=True)
                
                # Create vector store with absolute path
                self.vector_store = VectorStore(
                    data_path=os.path.abspath(vector_path),
                    dimension=vector_dimension,
                    use_gpu=use_gpu
                )
                
                # Verify connection by calling a method
                _ = self.vector_store.get_compartments()
                
                logger.info(f"LanceDB adapter initialized with vector_dimension={vector_dimension}")
            except Exception as e:
                logger.error(f"Error initializing LanceDB vector store: {e}")
                # Try alternative initialization as fallback
                try:
                    self.vector_store = VectorStore(
                        data_path=memory_dir,
                        dimension=vector_dimension,
                        use_gpu=use_gpu
                    )
                    logger.info("LanceDB adapter initialized with fallback approach")
                except Exception as fallback_error:
                    logger.error(f"Fallback initialization failed: {fallback_error}")
                    self.vector_store = None
        else:
            logger.error("Failed to initialize LanceDB adapter: missing VectorStore class")
            self.vector_store = None
    
    def _ensure_compartment(self, compartment_id: str) -> None:
        """Ensure the compartment exists"""
        if not self.vector_store:
            return
            
        if compartment_id not in self.vector_store.get_compartments():
            # Create compartment if it doesn't exist
            self.vector_store.create_compartment(compartment_id)
            logger.info(f"Created new compartment: {compartment_id}")
    
    def store(self, 
              memory_text: str, 
              compartment_id: str, 
              metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Store a memory with optional metadata.
        
        Args:
            memory_text: The text to remember
            compartment_id: The compartment to store in
            metadata: Optional metadata to associate with the memory
            
        Returns:
            ID of the stored memory
        """
        if not self.vector_store:
            logger.error("Cannot store memory: Vector store not initialized")
            return -1
            
        if not metadata:
            metadata = {}
            
        # Ensure compartment exists
        self._ensure_compartment(compartment_id)
        
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
        Search for memories by text match.
        
        Args:
            query: The text to search for
            compartment_id: The compartment to search in
            limit: Maximum number of results to return
            
        Returns:
            List of matching memories
        """
        if not self.vector_store:
            logger.error("Cannot search: Vector store not initialized")
            return []
            
        # Ensure compartment exists
        self._ensure_compartment(compartment_id)
        
        # Perform text search (exact match)
        results = self.vector_store.text_search(
            query=query,
            compartment=compartment_id,
            top_k=limit
        )
        
        logger.info(f"Searched for '{query}' in compartment '{compartment_id}', found {len(results)} results")
        return results
    
    def semantic_search(self, 
                        query: str, 
                        compartment_id: str, 
                        limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memories by semantic similarity.
        
        Args:
            query: The text to search for
            compartment_id: The compartment to search in
            limit: Maximum number of results to return
            
        Returns:
            List of matching memories with similarity scores
        """
        if not self.vector_store:
            logger.error("Cannot perform semantic search: Vector store not initialized")
            return []
            
        # Ensure compartment exists
        self._ensure_compartment(compartment_id)
        
        # Perform semantic search
        results = self.vector_store.vector_search(
            query=query,
            compartment=compartment_id,
            top_k=limit
        )
        
        logger.info(f"Semantic search for '{query}' in compartment '{compartment_id}', found {len(results)} results")
        return results
    
    def get_compartments(self) -> List[str]:
        """Get all compartment IDs."""
        if not self.vector_store:
            logger.error("Cannot get compartments: Vector store not initialized")
            return []
            
        return self.vector_store.get_compartments()
    
    def delete_compartment(self, compartment_id: str) -> bool:
        """Delete a compartment."""
        if not self.vector_store:
            logger.error("Cannot delete compartment: Vector store not initialized")
            return False
            
        return self.vector_store.delete(compartment_id)
    
    def get_memory_by_id(self, 
                         memory_id: int, 
                         compartment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory by its ID.
        
        Args:
            memory_id: The ID of the memory
            compartment_id: The compartment to look in
            
        Returns:
            The memory if found, None otherwise
        """
        if not self.vector_store:
            logger.error("Cannot get memory by ID: Vector store not initialized")
            return None
            
        # Ensure compartment exists
        self._ensure_compartment(compartment_id)
        
        # Get memory by ID
        memory = self.vector_store.get_by_id(
            memory_id=memory_id,
            compartment=compartment_id
        )
        
        if memory:
            logger.info(f"Retrieved memory with ID {memory_id} from compartment '{compartment_id}'")
        else:
            logger.warning(f"Memory with ID {memory_id} not found in compartment '{compartment_id}'")
            
        return memory

# Integration with Engram memory system
def install_lancedb_adapter():
    """
    Install the LanceDB adapter into Engram's memory system.
    
    This function monkey patches the Engram memory module to use LanceDB
    for vector operations.
    
    Returns:
        True if installation was successful, False otherwise
    """
    try:
        # Import Engram memory module
        from engram.core import memory
        
        # Check if LanceDB is available
        try:
            import lancedb
            import pyarrow
            logger.info(f"Using LanceDB version {lancedb.__version__} with PyArrow {pyarrow.__version__}")
        except ImportError as e:
            logger.error(f"LanceDB installation not found: {e}")
            logger.error("Please run vector/lancedb/install.py to install LanceDB")
            return False
        
        # Create the adapter
        adapter = LanceDBAdapter()
        
        # Override the MemoryService class instead of looking for get_memory_service function
        # Store the original class for later reference
        original_memory_service = memory.MemoryService
        
        # Replace the memory service class with our LanceDB adapter
        memory.MemoryService = LanceDBAdapter
        
        # Update the module's variables to indicate vector database availability
        memory.HAS_VECTOR_DB = True
        memory.VECTOR_DB_NAME = "lancedb"
        memory.VECTOR_DB_VERSION = lancedb.__version__
        
        # Set environment variable to ensure we're not in fallback mode
        import os
        os.environ['ENGRAM_USE_FALLBACK'] = "0"
        
        logger.info("Successfully installed LanceDB adapter")
        return True
        
    except Exception as e:
        logger.error(f"Failed to install LanceDB adapter: {e}")
        return False

if __name__ == "__main__":
    # When run directly, display implementation status
    print("\nLanceDB Adapter for Engram Memory System")
    
    # Check for LanceDB
    try:
        import lancedb
        import pyarrow
        print(f"Status: AVAILABLE - Using LanceDB {lancedb.__version__} with PyArrow {pyarrow.__version__}")
    except ImportError:
        print("Status: PLANNED - LanceDB not installed")
        print("\nTo install LanceDB, run:")
        print("  python vector/lancedb/install.py")
    
    # Display implementation info
    print("\nImplementation Status:")
    if VectorStore:
        print("✅ Vector Store: Implemented")
    else:
        print("❌ Vector Store: Not implemented")
    
    print("\nFor more information, see vector/lancedb/README.md")