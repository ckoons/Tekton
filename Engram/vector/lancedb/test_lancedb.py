#!/usr/bin/env python
"""
Test script for the LanceDB vector store implementation.
Demonstrates basic functionality and compatibility with Engram.
"""

import os
import sys
import logging
from pathlib import Path

# Add Engram to path
ENGRAM_DIR = str(Path(__file__).parent.parent.parent)
if ENGRAM_DIR not in sys.path:
    sys.path.insert(0, ENGRAM_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("lancedb_test")

# Import adapter
try:
    from vector.lancedb.adapter import LanceDBAdapter
    logger.info("Successfully imported LanceDB adapter")
except ImportError as e:
    logger.error(f"Failed to import LanceDB adapter: {e}")
    sys.exit(1)

def test_memory_operations():
    """Test memory operations using the LanceDB adapter"""
    print("\n=== Testing Memory Operations ===\n")
    
    # Create memory directory
    test_dir = os.path.join(ENGRAM_DIR, "test_memories", "lancedb")
    os.makedirs(test_dir, exist_ok=True)
    
    # Initialize adapter
    adapter = LanceDBAdapter(
        client_id="test_client",
        memory_dir=test_dir,
        vector_dimension=64
    )
    
    # Store some memories
    memories = [
        "The quick brown fox jumps over the lazy dog.",
        "Artificial intelligence is transforming many industries.",
        "Vector databases enable efficient similarity search.",
        "Python is a popular programming language for data science.",
        "LanceDB is a vector database built on Apache Arrow."
    ]
    
    compartment = "test_compartment"
    memory_ids = []
    
    print("Storing memories...")
    for i, memory_text in enumerate(memories):
        metadata = {
            "source": "test",
            "category": f"category_{i % 3}",
            "importance": i + 1
        }
        memory_id = adapter.store(memory_text, compartment, metadata)
        memory_ids.append(memory_id)
        print(f"  {i+1}. ID {memory_id}: {memory_text[:40]}...")
    
    # List compartments
    print("\nCompartments:")
    compartments = adapter.get_compartments()
    for i, comp in enumerate(compartments):
        print(f"  {i+1}. {comp}")
    
    # Text search
    search_query = "vector"
    print(f"\nText search for '{search_query}':")
    results = adapter.search(search_query, compartment, limit=3)
    for i, result in enumerate(results):
        print(f"  {i+1}. [{result['score']:.2f}] {result['text']}")
        print(f"     Metadata: {result['metadata']}")
    
    # Semantic search
    semantic_query = "How to find similar information?"
    print(f"\nSemantic search for '{semantic_query}':")
    results = adapter.semantic_search(semantic_query, compartment, limit=3)
    for i, result in enumerate(results):
        print(f"  {i+1}. [{result['score']:.2f}] {result['text']}")
        print(f"     Metadata: {result['metadata']}")
    
    # Get memory by ID
    if memory_ids:
        test_id = memory_ids[0]
        print(f"\nGetting memory by ID {test_id}:")
        memory = adapter.get_memory_by_id(test_id, compartment)
        if memory:
            print(f"  Text: {memory['text']}")
            print(f"  Metadata: {memory['metadata']}")
        else:
            print(f"  Memory not found")
    
    print("\nTest completed successfully!")
    return True

def test_engram_integration():
    """Test integration with Engram memory system"""
    print("\n=== Testing Engram Integration ===\n")
    
    try:
        # Try to import memory modules
        from engram.core import memory
        
        # Install the adapter
        from vector.lancedb.adapter import install_lancedb_adapter
        success = install_lancedb_adapter()
        
        if success:
            print("Successfully installed LanceDB adapter to Engram memory system")
            
            # Get memory service (should be our adapter)
            mem_service = memory.get_memory_service()
            print(f"Memory service type: {type(mem_service).__name__}")
            
            # Store a test memory
            memory_id = mem_service.store(
                "This is a test memory using LanceDB with Engram",
                "engram_test",
                {"source": "test_integration"}
            )
            print(f"Stored test memory with ID {memory_id}")
            
            # Search for it
            results = mem_service.semantic_search("test memory", "engram_test")
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results):
                print(f"  {i+1}. [{result['score']:.2f}] {result['text']}")
            
            print("\nEngram integration test completed successfully!")
            return True
        else:
            print("Failed to install LanceDB adapter to Engram memory system")
            return False
            
    except ImportError as e:
        print(f"Engram integration test skipped: {e}")
        return False
        
    except Exception as e:
        print(f"Engram integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("\nLanceDB Vector Store Test")
    print("========================\n")
    
    # Check if LanceDB is available
    try:
        import lancedb
        import pyarrow
        print(f"LanceDB version: {lancedb.__version__}")
        print(f"PyArrow version: {pyarrow.__version__}")
    except ImportError as e:
        print(f"LanceDB not available: {e}")
        print("Please run vector/lancedb/install.py first")
        sys.exit(1)
    
    # Run memory operations test
    success = test_memory_operations()
    
    # Run Engram integration test if memory operations succeeded
    if success:
        test_engram_integration()
    
    print("\nAll tests completed.")