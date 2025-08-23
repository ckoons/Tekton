#!/usr/bin/env python3
"""
Test vector database configuration and automatic selection.

Tests:
1. Configuration loading
2. Auto-detection on M4 Max
3. Manual selection via environment
4. FAISS implementation completeness
"""

import os
from shared.env import TektonEnviron
import sys
import asyncio

# Add Tekton to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils.global_config import GlobalConfig
from Engram.utils.detect_best_vector_db import get_vector_db_info, print_vector_db_status


def test_configuration():
    """Test vector DB configuration from environment."""
    print("=== Testing Vector DB Configuration ===\n")
    
    # Get global config
    config = GlobalConfig.get_instance()
    
    # Check vector config
    vector_config = config.config.vector
    print("Vector DB Configuration:")
    print(f"  Preferred DB: {vector_config.vector_db}")
    print(f"  CPU Only: {vector_config.cpu_only}")
    print(f"  GPU Enabled: {vector_config.gpu_enabled}")
    
    # Check environment variables
    print("\nEnvironment Variables:")
    print(f"  TEKTON_VECTOR_DB: {TektonEnviron.get('TEKTON_VECTOR_DB', 'not set')}")
    print(f"  TEKTON_VECTOR_CPU_ONLY: {TektonEnviron.get('TEKTON_VECTOR_CPU_ONLY', 'not set')}")
    print(f"  TEKTON_VECTOR_GPU_ENABLED: {TektonEnviron.get('TEKTON_VECTOR_GPU_ENABLED', 'not set')}")


def test_auto_detection():
    """Test auto-detection of best vector DB."""
    print("\n=== Testing Auto-Detection ===")
    
    best_db, reason, dependencies, hardware = get_vector_db_info()
    print_vector_db_status(dependencies, hardware, best_db, reason)


async def test_engram_init():
    """Test Engram initialization with vector DB."""
    print("\n=== Testing Engram Initialization ===")
    
    # Temporarily set to auto mode
    original_db = TektonEnviron.get('TEKTON_VECTOR_DB')
    TektonEnviron.set('TEKTON_VECTOR_DB', 'auto')
    
    try:
        # Import and check what Engram detects
        from Engram.engram.core.memory.config import initialize_vector_db
        
        has_vector, db_info, vector_model = initialize_vector_db()
        
        print(f"\nEngram Vector DB Status:")
        print(f"  Has Vector DB: {has_vector}")
        print(f"  Database: {db_info.get('name', 'none')}")
        print(f"  Version: {db_info.get('version', 'unknown')}")
        print(f"  Model: {db_info.get('model', 'none')}")
        print(f"  Model Dimension: {db_info.get('model_dim', 'N/A')}")
        
    finally:
        # Restore original setting
        if original_db:
            TektonEnviron.set('TEKTON_VECTOR_DB', original_db)
        else:
            os.environ.pop('TEKTON_VECTOR_DB', None)


async def test_faiss_operations():
    """Test FAISS operations are complete."""
    print("\n=== Testing FAISS Implementation ===")
    
    # Set to use FAISS specifically
    TektonEnviron.set('TEKTON_VECTOR_DB', 'faiss')
    
    try:
        from Engram.engram.core.memory.storage.vector_storage import VectorStorage
        
        # Create a test instance
        from pathlib import Path
        test_path = Path("/tmp/test_vectors")
        test_path.mkdir(parents=True, exist_ok=True)
        
        storage = VectorStorage(
            client_id="test",
            data_dir=test_path
        )
        
        print("FAISS Storage Operations:")
        
        # Test add
        try:
            success = await storage.add(
                content="Test memory for FAISS",
                namespace="test",
                metadata={"test": True}
            )
            print(f"  ✓ Add operation: {'Success' if success else 'Failed'}")
        except Exception as e:
            print(f"  ✗ Add operation failed: {e}")
        
        # Test search
        try:
            results = storage.search(
                query="test memory",
                namespace="test",
                limit=5
            )
            print(f"  ✓ Search operation: Found {len(results)} results")
        except Exception as e:
            print(f"  ✗ Search operation failed: {e}")
        
        # Test clear
        try:
            success = await storage.clear_namespace("test")
            print(f"  ✓ Clear operation: {'Success' if success else 'Failed'}")
        except Exception as e:
            print(f"  ✗ Clear operation failed: {e}")
            
    except Exception as e:
        print(f"Failed to test FAISS: {e}")


async def main():
    """Run all tests."""
    print("Vector Database Configuration Test Suite")
    print("=" * 50)
    
    # Test configuration loading
    test_configuration()
    
    # Test auto-detection
    test_auto_detection()
    
    # Test Engram initialization
    await test_engram_init()
    
    # Test FAISS operations
    await test_faiss_operations()
    
    print("\n" + "=" * 50)
    print("All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())