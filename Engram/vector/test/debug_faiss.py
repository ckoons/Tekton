#!/usr/bin/env python
"""
Debug script to diagnose FAISS and NumPy compatibility issues
"""

import sys
import os
import logging

# Configure verbose logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("debug_faiss")

def check_imports():
    """Check all required imports one by one with detailed error reporting"""
    # Check Python version
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python executable: {sys.executable}")
    
    # Check NumPy
    try:
        import numpy as np
        logger.info(f"NumPy version: {np.__version__}")
        logger.info(f"NumPy path: {np.__file__}")
    except ImportError as e:
        logger.error(f"Failed to import NumPy: {e}")
    except Exception as e:
        logger.error(f"Error with NumPy: {e}")
    
    # Check FAISS
    try:
        import faiss
        logger.info(f"FAISS version: {faiss.__version__}")
        logger.info(f"FAISS path: {faiss.__file__}")
        
        # Check if FAISS CPU works
        try:
            index = faiss.IndexFlatL2(10)
            logger.info(f"Successfully created FAISS index with dimension 10")
            
            # Create a simple vector
            try:
                vector = np.random.random((1, 10)).astype(np.float32)
                logger.info(f"Created random vector with shape {vector.shape}")
                
                # Try to add to index
                try:
                    index.add(vector)
                    logger.info(f"Successfully added vector to index")
                    
                    # Try to search
                    try:
                        distances, indices = index.search(vector, 1)
                        logger.info(f"Successfully searched index: {distances}, {indices}")
                        logger.info("FAISS is WORKING CORRECTLY")
                    except Exception as e:
                        logger.error(f"Error searching index: {e}")
                except Exception as e:
                    logger.error(f"Error adding vector to index: {e}")
            except Exception as e:
                logger.error(f"Error creating vector: {e}")
        except Exception as e:
            logger.error(f"Error creating FAISS index: {e}")
    except ImportError as e:
        logger.error(f"Failed to import FAISS: {e}")
    except Exception as e:
        logger.error(f"Error with FAISS: {e}")
    
    # Check environment
    logger.info("\nEnvironment Information:")
    logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    logger.info(f"LD_LIBRARY_PATH: {os.environ.get('LD_LIBRARY_PATH', 'Not set')}")
    logger.info(f"DYLD_LIBRARY_PATH: {os.environ.get('DYLD_LIBRARY_PATH', 'Not set')}")
    
    # Check all sys.path directories
    logger.info("\nPython Path Directories:")
    for i, path in enumerate(sys.path):
        logger.info(f"  {i}: {path}")

if __name__ == "__main__":
    logger.info("Starting FAISS debug script...")
    check_imports()