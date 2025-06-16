#!/usr/bin/env python
"""
Simple test script to verify FAISS works with NumPy 2.x
"""

import os
import numpy as np
import faiss
import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("faiss_test")

def setup_test_index():
    """Create a simple FAISS index with test data"""
    # Print versions
    logger.info(f"NumPy version: {np.__version__}")
    logger.info(f"FAISS version: {faiss.__version__}")
    
    # Create a simple vector database with FAISS
    dimension = 128  # Vector dimension
    
    # Create a flat index - the simplest index type that stores vectors as is
    index = faiss.IndexFlatL2(dimension)
    logger.info(f"Index created with dimension {dimension}")
    
    # Generate 1000 random vectors for testing
    vectors = np.random.random((1000, dimension)).astype(np.float32)
    logger.info(f"Generated {len(vectors)} random vectors")
    
    # Add vectors to the index
    index.add(vectors)
    logger.info(f"Added vectors to index. Total vectors: {index.ntotal}")
    
    # Generate a query vector
    query = np.random.random((1, dimension)).astype(np.float32)
    
    # Search for similar vectors
    k = 5  # Number of nearest neighbors to return
    distances, indices = index.search(query, k)
    
    logger.info(f"Search results for query vector:")
    for i, (idx, dist) in enumerate(zip(indices[0], distances[0])):
        logger.info(f"  {i+1}. Vector #{idx}, Distance: {dist:.4f}")
        
    # Test writing and reading the index
    index_path = "test_index.faiss"
    faiss.write_index(index, index_path)
    logger.info(f"Index written to {index_path}")
    
    loaded_index = faiss.read_index(index_path)
    logger.info(f"Index loaded from {index_path}. Total vectors: {loaded_index.ntotal}")
    
    # Clean up
    if os.path.exists(index_path):
        os.remove(index_path)
        logger.info(f"Removed test file {index_path}")
    
    return True

if __name__ == "__main__":
    try:
        success = setup_test_index()
        logger.info(f"Test {'PASSED' if success else 'FAILED'}")
    except Exception as e:
        logger.error(f"Test FAILED with error: {str(e)}")
        raise