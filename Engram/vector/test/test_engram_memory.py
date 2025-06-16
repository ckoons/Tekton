#!/usr/bin/env python
"""
Comprehensive test for Engram memory with FAISS integration
This script tests both with and without FAISS to diagnose any issues
"""

import os
import sys
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_engram_memory")

# Add Engram to the Python path if not already there
ENGRAM_DIR = str(Path(__file__).parent.parent.parent)
if ENGRAM_DIR not in sys.path:
    sys.path.insert(0, ENGRAM_DIR)
    logger.info(f"Added {ENGRAM_DIR} to Python path")

async def test_standard_memory():
    """Test Engram's standard memory functionality (non-FAISS)"""
    try:
        import asyncio
        from engram.core import memory
        
        # Create a memory instance with a unique client ID to avoid conflicts
        client_id = f"memory_test_{int(time.time())}"
        logger.info(f"Testing standard memory with client_id: {client_id}")
        ms = memory.MemoryService(client_id=client_id)
        
        # Test basic operations
        logger.info("Testing basic memory operations...")
        
        # Store a memory
        logger.info("Storing a test memory...")
        memory_id = await ms.add("This is a test memory", "test_compartment")
        logger.info(f"Stored memory with ID: {memory_id['id']}")
        
        # Retrieve memory
        logger.info("Retrieving the test memory...")
        retrieved = await ms.get(memory_id['id'], "test_compartment")
        if retrieved:
            logger.info(f"Successfully retrieved memory: {retrieved['content'][:30]}...")
        else:
            logger.error("Failed to retrieve memory")
            return False
        
        # Search for memory
        logger.info("Searching for the test memory...")
        search_results = await ms.search("test memory", "test_compartment")
        logger.info(f"Search found {len(search_results['results'])} results")
        
        # Delete the test compartment to clean up
        logger.info("Cleaning up test compartment...")
        await ms.delete_compartment("test_compartment")
        
        logger.info("Standard memory test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error in standard memory test: {e}")
        return False

def test_faiss_memory():
    """Test Engram memory with FAISS integration"""
    try:
        # First, check if FAISS is available
        try:
            import faiss
            import numpy as np
            logger.info(f"FAISS version: {faiss.__version__}")
            logger.info(f"NumPy version: {np.__version__}")
        except ImportError as e:
            logger.error(f"FAISS or NumPy not available: {e}")
            return False
            
        # Import our custom FAISS adapter components
        try:
            from vector_store import VectorStore
            from engram_memory_adapter import MemoryService as FAISSMemoryService
            logger.info("Successfully imported FAISS adapter components")
        except ImportError as e:
            logger.error(f"Failed to import FAISS adapter: {e}")
            return False
            
        # Replace the MemoryService in Engram with our FAISS-enabled version
        from engram.core import memory as engram_memory
        
        # Backup original settings
        original_has_vector_db = engram_memory.HAS_VECTOR_DB
        original_vector_db_name = engram_memory.VECTOR_DB_NAME
        original_memory_service = engram_memory.MemoryService
        
        try:
            # Enable vector database and set to FAISS
            engram_memory.HAS_VECTOR_DB = True
            engram_memory.VECTOR_DB_NAME = "FAISS"
            # Replace the memory service class
            engram_memory.MemoryService = FAISSMemoryService
            
            # Create a memory instance with our FAISS adapter
            client_id = f"faiss_test_{int(time.time())}"
            logger.info(f"Testing FAISS memory with client_id: {client_id}")
            test_dir = "./test_memories"
            os.makedirs(test_dir, exist_ok=True)
            
            ms = FAISSMemoryService(client_id=client_id, memory_dir=test_dir, vector_dimension=128)
            
            # Test storing a memory
            logger.info("Storing a test memory...")
            memory_id = ms.store(
                "This is a test memory for FAISS integration", 
                "faiss_test_compartment",
                {"source": "test_script"}
            )
            logger.info(f"Stored memory with ID: {memory_id}")
            
            # Test exact search
            logger.info("Testing exact search...")
            search_results = ms.search("test memory", "faiss_test_compartment", 5)
            logger.info(f"Exact search found {len(search_results)} results")
            for i, result in enumerate(search_results):
                logger.info(f"  {i+1}. {result['text'][:30]}...")
            
            # Test semantic search
            logger.info("Testing semantic search...")
            search_results = ms.semantic_search("How does FAISS work?", "faiss_test_compartment", 5)
            logger.info(f"Semantic search found {len(search_results)} results")
            for i, result in enumerate(search_results):
                logger.info(f"  {i+1}. [{result['score']:.2f}] {result['text'][:30]}...")
                
            logger.info("FAISS memory test completed successfully")
            return True
            
        finally:
            # Restore original Engram memory components
            engram_memory.HAS_VECTOR_DB = original_has_vector_db
            engram_memory.VECTOR_DB_NAME = original_vector_db_name
            engram_memory.MemoryService = original_memory_service
            
    except Exception as e:
        logger.error(f"Error in FAISS memory test: {e}")
        return False

def setup_environment():
    """Check and set up FAISS environment if needed"""
    try:
        # First, make sure faiss-cpu is installed
        try:
            import faiss
            logger.info(f"FAISS version {faiss.__version__} is already installed")
        except ImportError:
            logger.info("FAISS not found, attempting to install...")
            import subprocess
            result = subprocess.run([sys.executable, "-m", "pip", "install", "faiss-cpu>=1.7.0"])
            if result.returncode != 0:
                logger.error("Failed to install FAISS")
                return False
                
            # Try importing again
            try:
                import faiss
                logger.info(f"Successfully installed FAISS version {faiss.__version__}")
            except ImportError as e:
                logger.error(f"Failed to import FAISS after installation: {e}")
                return False
                
        return True
    except Exception as e:
        logger.error(f"Error setting up environment: {e}")
        return False

async def run_tests():
    # Test standard memory
    print("\nTesting standard memory system...")
    if await test_standard_memory():
        print("✅ Standard memory test passed")
    else:
        print("❌ Standard memory test failed")
    
    # Test FAISS memory
    print("\nTesting FAISS-enabled memory system...")
    if test_faiss_memory():
        print("✅ FAISS memory test passed")
    else:
        print("❌ FAISS memory test failed")
    
    print("\nMemory system tests completed.\n")

if __name__ == "__main__":
    import asyncio
    
    print("\n--- Engram Memory System Test ---\n")
    
    # Set up environment if needed
    if not setup_environment():
        print("\n❌ Failed to set up test environment\n")
        sys.exit(1)
    
    # Run tests with async support
    asyncio.run(run_tests())