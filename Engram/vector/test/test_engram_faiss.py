#!/usr/bin/env python
"""
Test script for Engram with FAISS integration
This verifies that the FAISS adapter works with Engram's memory functions
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_engram_faiss")

# Add Engram to the Python path if not already there
ENGRAM_DIR = str(Path(__file__).parent.parent.parent)
if ENGRAM_DIR not in sys.path:
    sys.path.insert(0, ENGRAM_DIR)
    logger.info(f"Added {ENGRAM_DIR} to Python path")

# Import FAISS first to verify it works
try:
    import faiss
    import numpy as np
    logger.info(f"FAISS version: {faiss.__version__}")
    logger.info(f"NumPy version: {np.__version__}")
except ImportError as e:
    logger.error(f"Failed to import FAISS or NumPy: {e}")
    sys.exit(1)

# Import vector store and adapter
try:
    from vector_store import VectorStore
    from engram_memory_adapter import MemoryService
    logger.info("Successfully imported vector storage components")
except ImportError as e:
    logger.error(f"Failed to import vector storage components: {e}")
    sys.exit(1)

def test_with_engram_memory():
    """Test that Engram's memory functions work with FAISS adapter"""
    try:
        # Now test with Engram's memory module
        logger.info("Testing with Engram's memory module...")
        
        # First, let's monkey-patch the memory module
        from engram.core import memory
        
        # Backup original functions
        original_has_vector_db = memory.HAS_VECTOR_DB
        original_vector_db_name = memory.VECTOR_DB_NAME
        
        # Apply patches
        memory.HAS_VECTOR_DB = True
        memory.VECTOR_DB_NAME = "FAISS"
        
        # Replace the MemoryService class with our FAISS-compatible version
        memory_service_class = memory.MemoryService
        memory.MemoryService = MemoryService
        
        # Create a memory instance
        ms = memory.MemoryService(client_id="test_faiss", memory_dir="./test_memories")
        
        # Test memory operations
        logger.info("Testing memory operations...")
        
        # Store some test memories
        memory_id = ms.store("This is a test memory for FAISS integration", "faiss_test",
                          {"source": "test_script", "tag": "test"})
        logger.info(f"Stored memory with ID: {memory_id}")
        
        # Search for the memory
        results = ms.search("test memory", "faiss_test", 5)
        logger.info(f"Search found {len(results)} results")
        for i, result in enumerate(results):
            logger.info(f"  {i+1}. {result['text'][:50]}...")
        
        # Test semantic search
        results = ms.semantic_search("How does FAISS work?", "faiss_test", 5)
        logger.info(f"Semantic search found {len(results)} results")
        for i, result in enumerate(results):
            logger.info(f"  {i+1}. [{result['score']:.2f}] {result['text'][:50]}...")
        
        # Check getting memory by ID
        memory_result = ms.get_memory_by_id(memory_id, "faiss_test")
        if memory_result:
            logger.info(f"Retrieved memory: {memory_result['text'][:50]}...")
        else:
            logger.error(f"Failed to retrieve memory with ID {memory_id}")
        
        # Restore original functions
        memory.HAS_VECTOR_DB = original_has_vector_db
        memory.VECTOR_DB_NAME = original_vector_db_name
        memory.MemoryService = memory_service_class
        
        logger.info("Successfully tested Engram memory functions with FAISS adapter")
        return True
    except Exception as e:
        logger.error(f"Error testing Engram memory functions: {e}")
        return False

if __name__ == "__main__":
    try:
        # Test the vector store
        store = VectorStore(dimension=64)
        
        # Add a test vector
        store.add("test", ["This is a test vector for FAISS"])
        
        # Search for it
        results = store.search("test", "test", 1)
        
        logger.info(f"Vector store test successful, found {len(results)} results")
        
        # Test with Engram memory
        success = test_with_engram_memory()
        
        if success:
            logger.info("✅ All tests passed!")
            print("\n✅ FAISS integration with Engram is working correctly!\n")
        else:
            logger.error("❌ Some tests failed")
            print("\n❌ FAISS integration with Engram has issues.\n")
    except Exception as e:
        logger.error(f"Error during testing: {e}")
        print("\n❌ FAISS integration with Engram has issues.\n")