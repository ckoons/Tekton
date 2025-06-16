#!/usr/bin/env python3
"""
Vector Database Setup for Engram

This script installs and configures the necessary dependencies for the Engram
vector database integration. It verifies the installation, creates necessary
directories, and tests the vector database functionality.

Usage:
    python vector_db_setup.py [--install] [--test]

Options:
    --install    Install required vector database dependencies
    --test       Run vector database test after setup
"""

import os
import sys
import subprocess
import argparse
import logging
import json
from pathlib import Path
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.vector_setup")

# Required packages
REQUIRED_PACKAGES = [
    "faiss-cpu",  # Vector database (use faiss-gpu for CUDA support)
    "numpy",      # No version restriction, works with any NumPy version
]

def check_packages():
    """Check if required packages are installed and importable."""
    missing_packages = []
    
    # Check NumPy version
    try:
        import numpy
        numpy_version = numpy.__version__
        logger.info(f"✅ NumPy version {numpy_version} is compatible")
    except ImportError:
        logger.warning("❌ NumPy is not installed")
        missing_packages.append("numpy")
    
    # Check FAISS
    try:
        import faiss
        try:
            version = faiss.__version__
        except AttributeError:
            version = "unknown"
        logger.info(f"✅ Package faiss-cpu is installed (version: {version})")
    except ImportError:
        logger.warning("❌ Package faiss-cpu is not installed or not importable")
        missing_packages.append("faiss-cpu")
    
    return missing_packages

def install_packages(packages):
    """Install the specified packages using pip."""
    if not packages:
        logger.info("No packages to install")
        return True
    
    logger.info(f"Installing packages: {', '.join(packages)}")
    
    # For venv aware installation
    pip_cmd = [sys.executable, "-m", "pip", "install"] + packages
    
    try:
        result = subprocess.run(pip_cmd, check=True, capture_output=True, text=True)
        logger.info(f"Installation output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install packages: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def verify_vector_db():
    """Verify that the vector database components are working properly."""
    try:
        import faiss
        import numpy as np
        
        # Check version if available
        try:
            version = faiss.__version__
        except AttributeError:
            version = "unknown"
            
        logger.info(f"FAISS installed (version: {version})")
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test index
            dimension = 128
            index = faiss.IndexFlatL2(dimension)
            
            logger.info("✅ Successfully created FAISS test index")
            
            # Create a test embedding
            embedding = np.random.random(dimension).astype(np.float32)
            embedding_size = len(embedding)
            
            if embedding_size > 0:
                logger.info(f"✅ Successfully created embedding of size {embedding_size}")
                
                # Add to index
                index.add(np.array([embedding]))
                logger.info("✅ Successfully added document to FAISS")
                
                # Test searching
                distances, indices = index.search(np.array([embedding]), 1)
                
                if len(indices) > 0 and indices[0][0] == 0:
                    logger.info("✅ Successfully queried FAISS")
                    
                    # Save the index to file
                    index_path = os.path.join(temp_dir, "test.index")
                    faiss.write_index(index, index_path)
                    
                    # Load the index from file
                    loaded_index = faiss.read_index(index_path)
                    if loaded_index.ntotal == 1:
                        logger.info("✅ Successfully saved and loaded FAISS index")
                        return True
                    else:
                        logger.error("❌ Failed to load FAISS index from file")
                        return False
                else:
                    logger.error("❌ Failed to query FAISS")
                    return False
            else:
                logger.error("❌ Failed to create embedding")
                return False
    
    except Exception as e:
        logger.error(f"Error verifying FAISS vector database: {e}")
        logger.error("FAISS is required for vector search capabilities.")
        return False

def test_engram_with_vector():
    """Test Engram with vector database integration."""
    try:
        # Import Engram modules
        from engram.core.memory import MemoryService, HAS_VECTOR_DB, VECTOR_DB_NAME
        
        if not HAS_VECTOR_DB:
            logger.error("❌ Vector database not recognized by Engram")
            return False
        
        logger.info(f"✅ Vector database recognized by Engram: {VECTOR_DB_NAME}")
        
        # Initialize memory service with test client ID
        client_id = f"vector_test_{os.getpid()}"
        memory = MemoryService(client_id=client_id)
        
        if not memory.vector_available:
            logger.error("❌ Vector database not available in memory service")
            return False
        
        logger.info(f"✅ Vector database ({VECTOR_DB_NAME}) available in memory service")
        
        # Test adding and searching memories
        import asyncio
        
        async def test_memory():
            # Add a few test memories
            memories = [
                "Artificial intelligence is revolutionizing the world",
                "Machine learning models can identify patterns in data",
                "Neural networks are inspired by the human brain",
                "Deep learning uses multiple layers of neural networks"
            ]
            
            for i, content in enumerate(memories):
                await memory.add(content, namespace="test_vector")
                logger.info(f"Added memory {i+1}")
            
            # Search using semantic query
            search_query = "computational intelligence and algorithms"
            results = await memory.search(search_query, namespace="test_vector", limit=5)
            
            if results["count"] > 0:
                logger.info(f"✅ Successfully retrieved {results['count']} memories with semantic search")
                for i, result in enumerate(results["results"]):
                    relevance = result.get("relevance", 0)
                    content = result.get("content", "")
                    logger.info(f"  {i+1}. [Score: {relevance:.4f}] {content[:50]}...")
                return True
            else:
                logger.error("❌ No results found with semantic search")
                return False
        
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_memory())
        
    except Exception as e:
        logger.error(f"Error testing Engram with vector database: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description="Vector Database Setup for Engram")
    parser.add_argument("--install", action="store_true", help="Install required vector database dependencies")
    parser.add_argument("--test", action="store_true", help="Run vector database test after setup")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("ENGRAM VECTOR DATABASE SETUP (FAISS)")
    print("="*60 + "\n")
    
    # Check for required packages
    missing_packages = check_packages()
    
    # Install packages if requested
    if args.install and missing_packages:
        if not install_packages(missing_packages):
            logger.error("Failed to install required packages")
            sys.exit(1)
        
        # Re-check after installation
        missing_packages = check_packages()
        if missing_packages:
            logger.error(f"Still missing packages after installation: {missing_packages}")
            sys.exit(1)
    elif missing_packages:
        logger.warning("Some required packages are missing. Run with --install to install them.")
    
    # Verify vector database functionality
    if not missing_packages:
        logger.info("\nVerifying vector database functionality...")
        if verify_vector_db():
            logger.info("✅ Vector database verification successful")
        else:
            logger.error("❌ Vector database verification failed")
            sys.exit(1)
    
    # Test Engram with vector database
    if args.test and not missing_packages:
        logger.info("\nTesting Engram with vector database...")
        try:
            if test_engram_with_vector():
                logger.info("✅ Engram vector database test successful")
            else:
                logger.error("❌ Engram vector database test failed")
                
                # Add guidance for users on how to work around the issue
                logger.info("\n" + "="*60)
                logger.info("WORKAROUND GUIDANCE")
                logger.info("="*60)
                logger.info("The vector database test failed. To work around this issue:")
                logger.info("")
                logger.info("1. Use the fallback mode in Engram by setting this environment variable:")
                logger.info("   export ENGRAM_USE_FALLBACK=1")
                logger.info("")
                logger.info("2. This will make Engram use the file-based memory implementation")
                logger.info("   which will work correctly without the vector database.")
                logger.info("")
                logger.info("3. When running Python scripts or commands, you can also set it inline:")
                logger.info("   ENGRAM_USE_FALLBACK=1 python your_script.py")
                logger.info("")
                logger.info("4. To enable vector database in the future, either:")
                logger.info("   - Unset the environment variable: unset ENGRAM_USE_FALLBACK")
                logger.info("   - Or set it to false: export ENGRAM_USE_FALLBACK=0")
                logger.info("="*60)
        except Exception as e:
            logger.error(f"❌ Engram vector database test failed with error: {e}")
            logger.error("Consider using fallback mode with ENGRAM_USE_FALLBACK=1")
    
    print("\n" + "="*60)
    print("SETUP COMPLETE")
    print("="*60)
    
    if not args.install and not args.test:
        print("\nUsage:")
        print("  - Run with --install to install required packages")
        print("  - Run with --test to test vector database functionality")
        print("  - Run with both --install --test to install and test")

if __name__ == "__main__":
    main()