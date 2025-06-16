#!/usr/bin/env python3
"""
Test script to verify adapter imports are working correctly
"""

############################################################################
# INTEGRATION TEST NOTE:
#
# This script verifies that the basic class imports are working correctly.
# Before running full Tekton integration tests, you should:
#
# 1. Ensure all external dependencies are installed:
#    - FAISS: pip install faiss-cpu or faiss-gpu
#    - Redis: pip install redis
#    - Neo4j: pip install neo4j
#    - Other database backends as needed
#
# 2. Create or expand this test script to verify:
#    - Actual database connections to all required backends
#    - Proper handling of connection failures and fallbacks
#    - Integration with other Tekton components (Engram, etc.)
# 
# 3. Test performance and scalability:
#    - Vector operations with large embedding collections
#    - Graph operations with complex relationship queries
#    - Key-value and cache operations under high load
#
# 4. After passing integration tests, the launch scripts should be
#    updated to perform proper connection validation during startup.
############################################################################

import sys
import os

# Add Hermes to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Attempting to import DatabaseAdapter...")
    from hermes.core.database.adapters import DatabaseAdapter
    print("✅ Success! DatabaseAdapter imported correctly")
except ImportError as e:
    print(f"❌ Error: {e}")
    print("Traceback:")
    import traceback
    traceback.print_exc()

try:
    print("\nAttempting to import VectorDatabaseAdapter...")
    from hermes.core.database.adapters import VectorDatabaseAdapter
    print("✅ Success! VectorDatabaseAdapter imported correctly")
except ImportError as e:
    print(f"❌ Error: {e}")

try:
    print("\nAttempting to import FAISSVectorAdapter...")
    from hermes.adapters.vector import FAISSVectorAdapter
    print("✅ Success! FAISSVectorAdapter imported correctly")
except ImportError as e:
    print(f"❌ Error: {e}")
    print("Traceback:")
    import traceback
    traceback.print_exc()

# INTEGRATION TEST SUGGESTION:
# Uncomment these tests when implementing integration testing with actual database connections

# try:
#     print("\nTesting actual FAISS vector database connection...")
#     from hermes.core.database.manager import DatabaseManager
#     
#     # Initialize the manager
#     manager = DatabaseManager(base_path="/tmp/hermes_test")
#     
#     # Try to get a vector database connection
#     vector_db = await manager.get_vector_db(namespace="test")
#     
#     # Test basic operations
#     test_id = "test_vector"
#     test_vector = [0.1, 0.2, 0.3, 0.4]
#     await vector_db.store(id=test_id, vector=test_vector, metadata={"test": True})
#     
#     # Search and verify
#     results = await vector_db.search(query_vector=test_vector, limit=1)
#     if results and len(results) > 0 and results[0]["id"] == test_id:
#         print("✅ FAISS vector storage and search working correctly")
#     else:
#         print("❌ FAISS vector operations failed or returned unexpected results")
# except Exception as e:
#     print(f"❌ Error testing FAISS connection: {e}")

print("\nBasic import test complete! For full integration testing, expand this script.")
print("See INTEGRATION TEST NOTE at the top of this file for guidance.")