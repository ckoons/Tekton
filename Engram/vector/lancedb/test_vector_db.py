#!/usr/bin/env python
"""
Comprehensive test script for vector database implementation.
Tests both LanceDB and FAISS to verify functionality and integration.
"""

import os
import sys
import time
import random
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add Engram root to path
ENGRAM_DIR = str(Path(__file__).parent.parent.parent)
if ENGRAM_DIR not in sys.path:
    sys.path.insert(0, ENGRAM_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vector_db_test")

# Import detection script to determine available DBs
try:
    sys.path.append(os.path.join(ENGRAM_DIR, "utils"))
    from detect_best_vector_db import get_vector_db_info
    available_dbs = []
    best_db, reason, deps, hw = get_vector_db_info()
    if deps.get("faiss", False):
        available_dbs.append("faiss")
    if deps.get("lancedb", False):
        available_dbs.append("lancedb")
except ImportError:
    logger.warning("Could not import detect_best_vector_db.py")
    # Assume both are available, will check imports later
    available_dbs = ["faiss", "lancedb"]

class VectorDBTest:
    """Base class for testing vector database implementations"""
    
    def __init__(self, 
                 db_name: str, 
                 test_dir: str,
                 vector_dimension: int = 64):
        """Initialize the test harness."""
        self.db_name = db_name
        self.test_dir = test_dir
        self.vector_dimension = vector_dimension
        self.adapter = None
        self.vector_store = None
        os.makedirs(test_dir, exist_ok=True)
        
    def setup(self) -> bool:
        """Setup the vector database implementation."""
        raise NotImplementedError("Subclasses must implement setup()")
        
    def run_tests(self) -> Dict[str, bool]:
        """Run the test suite."""
        results = {}
        
        # Basic storage test
        results["store_memory"] = self.test_store_memory()
        
        # Search tests
        if results["store_memory"]:
            results["text_search"] = self.test_text_search()
            results["semantic_search"] = self.test_semantic_search()
            results["get_by_id"] = self.test_get_by_id()
        else:
            logger.warning("Skipping search tests because storage test failed")
            results["text_search"] = False
            results["semantic_search"] = False
            results["get_by_id"] = False
            
        # Compartment operations
        results["compartment_operations"] = self.test_compartment_operations()
        
        return results
        
    def test_store_memory(self) -> bool:
        """Test storing memories in the vector store."""
        try:
            # Store test memories
            self.text_samples = [
                "The quick brown fox jumps over the lazy dog.",
                "Machine learning is revolutionizing many industries.",
                "Vector databases enable efficient similarity search.",
                "Python is a popular programming language for data science.",
                f"{self.db_name} can be used for memory operations in AI systems."
            ]
            
            self.memory_ids = []
            
            # Store with metadata
            for i, text in enumerate(self.text_samples):
                metadata = {
                    "test_id": i,
                    "category": f"test_category_{i % 3}",
                    "priority": random.randint(1, 5),
                    "timestamp": time.time()
                }
                
                memory_id = self.adapter.store(text, "test_compartment", metadata)
                self.memory_ids.append(memory_id)
                logger.info(f"Stored memory with ID {memory_id}: {text[:30]}...")
                
            return len(self.memory_ids) == len(self.text_samples)
        except Exception as e:
            logger.error(f"Error in store_memory test: {e}")
            return False
            
    def test_text_search(self) -> bool:
        """Test text-based search."""
        try:
            # Simple text match
            results = self.adapter.search("vector database", "test_compartment", limit=2)
            
            if not results:
                logger.error("Text search returned no results")
                return False
                
            logger.info(f"Text search results: {len(results)} found")
            for result in results:
                logger.info(f"  [{result['score']:.2f}] {result['text'][:50]}...")
                
            return len(results) > 0
        except Exception as e:
            logger.error(f"Error in text_search test: {e}")
            return False
            
    def test_semantic_search(self) -> bool:
        """Test semantic search."""
        try:
            # Semantic search
            query = "How do computers find similar information?"
            results = self.adapter.semantic_search(query, "test_compartment", limit=3)
            
            if not results:
                logger.error("Semantic search returned no results")
                return False
                
            logger.info(f"Semantic search results for '{query}':")
            for result in results:
                logger.info(f"  [{result['score']:.2f}] {result['text'][:50]}...")
                
            return len(results) > 0
        except Exception as e:
            logger.error(f"Error in semantic_search test: {e}")
            return False
            
    def test_get_by_id(self) -> bool:
        """Test retrieving memories by ID."""
        try:
            if not self.memory_ids:
                logger.error("No memory IDs available for testing")
                return False
                
            # Get a memory by ID
            memory_id = self.memory_ids[0]
            memory = self.adapter.get_memory_by_id(memory_id, "test_compartment")
            
            if not memory:
                logger.error(f"Failed to retrieve memory with ID {memory_id}")
                return False
                
            logger.info(f"Retrieved memory with ID {memory_id}: {memory['text'][:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error in get_by_id test: {e}")
            return False
            
    def test_compartment_operations(self) -> bool:
        """Test compartment operations."""
        try:
            # Create a new compartment
            new_compartment = "test_compartment_new"
            
            # Store a test memory in the new compartment
            memory_text = f"This is a test memory for {self.db_name} in a new compartment"
            metadata = {"test": True, "db": self.db_name}
            self.adapter.store(memory_text, new_compartment, metadata)
            
            # List compartments
            compartments = self.adapter.get_compartments()
            logger.info(f"Available compartments: {compartments}")
            
            # Should contain both test compartments
            has_original = "test_compartment" in compartments
            has_new = new_compartment in compartments
            
            if not (has_original and has_new):
                logger.error(f"Missing compartments: orig={has_original}, new={has_new}")
                return False
                
            # Delete the new compartment
            success = self.adapter.delete_compartment(new_compartment)
            if not success:
                logger.error(f"Failed to delete compartment {new_compartment}")
                return False
                
            # Verify deletion
            compartments = self.adapter.get_compartments()
            deleted = new_compartment not in compartments
            
            logger.info(f"Compartment deletion success: {deleted}")
            return deleted
        except Exception as e:
            logger.error(f"Error in compartment_operations test: {e}")
            return False
            
    def cleanup(self) -> None:
        """Clean up test resources."""
        try:
            # Delete test compartment
            if self.adapter:
                self.adapter.delete_compartment("test_compartment")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


class LanceDBTest(VectorDBTest):
    """Test implementation for LanceDB"""
    
    def setup(self) -> bool:
        """Setup LanceDB test environment."""
        try:
            # Import necessary modules
            try:
                import lancedb
                import pyarrow
            except ImportError as e:
                logger.error(f"LanceDB dependencies not installed: {e}")
                return False
            
            # Import vector store and adapter
            try:
                from vector.lancedb.adapter import LanceDBAdapter
                from vector.lancedb.vector_store import VectorStore
            except ImportError as e:
                logger.error(f"LanceDB implementation not found: {e}")
                return False
                
            # Create adapter instance
            self.vector_store = VectorStore(
                data_path=self.test_dir,
                dimension=self.vector_dimension
            )
            
            self.adapter = LanceDBAdapter(
                client_id="test_client",
                memory_dir=self.test_dir,
                vector_dimension=self.vector_dimension
            )
            
            if not self.adapter.vector_store:
                logger.error("LanceDB adapter's vector store not initialized")
                return False
                
            logger.info("LanceDB test setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up LanceDB test: {e}")
            return False


class FAISSTest(VectorDBTest):
    """Test implementation for FAISS"""
    
    def setup(self) -> bool:
        """Setup FAISS test environment."""
        try:
            # Import necessary modules
            try:
                import faiss
                import numpy
            except ImportError as e:
                logger.error(f"FAISS dependencies not installed: {e}")
                return False
            
            # Import adapter from vector test directory
            try:
                sys.path.append(os.path.join(ENGRAM_DIR, "vector", "test"))
                from engram_memory_adapter import MemoryService
                from vector_store import VectorStore
            except ImportError as e:
                logger.error(f"FAISS implementation not found: {e}")
                return False
                
            # Create adapter instance
            self.vector_store = VectorStore(
                data_path=self.test_dir,
                dimension=self.vector_dimension
            )
            
            self.adapter = MemoryService(
                client_id="test_client",
                memory_dir=self.test_dir,
                vector_dimension=self.vector_dimension
            )
            
            logger.info("FAISS test setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up FAISS test: {e}")
            return False


def run_vector_db_tests() -> Dict[str, Dict[str, bool]]:
    """Run tests for all available vector database implementations."""
    results = {}
    
    for db_name in available_dbs:
        logger.info(f"\n=== Testing {db_name.upper()} Vector Database ===\n")
        
        test_dir = os.path.join(ENGRAM_DIR, "test_memories", f"{db_name}_test")
        
        if db_name == "lancedb":
            tester = LanceDBTest(db_name, test_dir)
        elif db_name == "faiss":
            tester = FAISSTest(db_name, test_dir)
        else:
            logger.error(f"Unknown database: {db_name}")
            continue
            
        # Setup test environment
        setup_success = tester.setup()
        
        if setup_success:
            # Run the tests
            test_results = tester.run_tests()
            results[db_name] = test_results
            
            # Cleanup
            tester.cleanup()
        else:
            logger.error(f"Failed to set up {db_name} test environment")
            results[db_name] = {"setup": False}
    
    return results


def print_results(results: Dict[str, Dict[str, bool]]) -> None:
    """Print test results in a formatted table."""
    if not results:
        print("\nNo vector database tests were run!")
        return
        
    print("\n=== Vector Database Test Results ===\n")
    
    # Find all test cases across all databases
    all_tests = set()
    for db_results in results.values():
        all_tests.update(db_results.keys())
    
    # Header
    header = "Test".ljust(25)
    for db_name in results:
        header += f" | {db_name.upper().ljust(10)}"
    print(header)
    print("-" * len(header))
    
    # Test results
    for test in sorted(all_tests):
        row = test.replace("_", " ").title().ljust(25)
        for db_name in results:
            db_results = results[db_name]
            if test in db_results:
                status = "✅ PASS" if db_results[test] else "❌ FAIL"
            else:
                status = "➖ N/A"
            row += f" | {status.ljust(10)}"
        print(row)
    
    # Summary
    print("\n=== Summary ===\n")
    for db_name, db_results in results.items():
        passed = sum(1 for r in db_results.values() if r)
        total = len(db_results)
        print(f"{db_name.upper()}: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    

if __name__ == "__main__":
    print("\nComprehensive Vector Database Test")
    print("=================================\n")
    
    if not available_dbs:
        print("No vector database implementations available!")
        print("Please install at least one of: FAISS, LanceDB")
        sys.exit(1)
    
    print(f"Testing these implementations: {', '.join(db.upper() for db in available_dbs)}")
    
    # Run all tests
    results = run_vector_db_tests()
    
    # Print results
    print_results(results)