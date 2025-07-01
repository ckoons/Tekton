#!/usr/bin/env python3
"""
Comprehensive Vector Database Test Suite for Engram

Tests all three vector database implementations:
- FAISS (High-performance with GPU acceleration)
- ChromaDB (Feature-rich with built-in embedding functions)  
- LanceDB (Optimized for Apple Silicon with Metal support)

This script temporarily overrides the vector DB configuration to test each implementation.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add Tekton paths to Python path
sys.path.insert(0, '/Users/cskoons/projects/github/Tekton')
sys.path.insert(0, '/Users/cskoons/projects/github/Tekton/Engram')

from engram.core.memory import MemoryService

class VectorDBTester:
    """Test suite for all vector database implementations."""
    
    def __init__(self):
        self.test_data = [
            {
                "content": "FAISS is a high-performance vector database optimized for GPU acceleration and large-scale similarity search operations.",
                "namespace": "tech_info",
                "metadata": {"db": "faiss", "test": "performance", "gpu": True}
            },
            {
                "content": "ChromaDB provides feature-rich vector storage with built-in embedding functions and advanced filtering capabilities.",
                "namespace": "tech_info", 
                "metadata": {"db": "chromadb", "test": "features", "embeddings": "built-in"}
            },
            {
                "content": "LanceDB is optimized for Apple Silicon with Metal support, providing excellent performance on M-series chips.",
                "namespace": "tech_info",
                "metadata": {"db": "lancedb", "test": "apple_silicon", "metal": True}
            },
            {
                "content": "Vector databases enable semantic search by storing high-dimensional embeddings that capture meaning and context.",
                "namespace": "concepts",
                "metadata": {"category": "ai", "topic": "embeddings", "complexity": "medium"}
            },
            {
                "content": "Memory systems in AI can leverage vector similarity to retrieve contextually relevant information efficiently.",
                "namespace": "concepts", 
                "metadata": {"category": "ai", "topic": "memory", "complexity": "advanced"}
            }
        ]
        
        self.test_queries = [
            ("GPU acceleration performance", "tech_info"),
            ("Apple Silicon Metal optimization", "tech_info"), 
            ("semantic search embeddings", "concepts"),
            ("vector similarity retrieval", "concepts"),
            ("ChromaDB features", "tech_info")
        ]
        
        self.results = {}
        
    def override_vector_db_config(self, db_name: str) -> None:
        """Temporarily override vector DB configuration for testing."""
        # Set environment variable to force specific DB choice
        os.environ['TEKTON_VECTOR_DB'] = db_name
        os.environ['ENGRAM_FORCE_VECTOR_DB'] = db_name
        print(f"🔧 Overriding vector DB configuration to: {db_name.upper()}")
        
    def restore_vector_db_config(self) -> None:
        """Restore original vector DB configuration."""
        # Restore to auto-detection
        os.environ['TEKTON_VECTOR_DB'] = 'auto'
        if 'ENGRAM_FORCE_VECTOR_DB' in os.environ:
            del os.environ['ENGRAM_FORCE_VECTOR_DB']
        print("🔄 Restored vector DB configuration to auto-detection")
        
    async def test_vector_db(self, db_name: str) -> Dict[str, Any]:
        """Test a specific vector database implementation."""
        print(f"\n{'='*60}")
        print(f"🧪 TESTING {db_name.upper()} IMPLEMENTATION")
        print(f"{'='*60}")
        
        # Override configuration
        self.override_vector_db_config(db_name)
        
        # Create unique client ID for this test
        client_id = f"test_{db_name}_{int(time.time())}"
        
        test_results = {
            "db_name": db_name,
            "client_id": client_id,
            "initialization": False,
            "storage_operations": [],
            "search_operations": [],
            "errors": [],
            "performance": {},
            "total_memories_stored": 0,
            "total_searches_performed": 0
        }
        
        try:
            # Initialize memory service
            print(f"🚀 Initializing {db_name.upper()} memory service...")
            start_time = time.time()
            
            memory = MemoryService(client_id)
            init_time = time.time() - start_time
            
            test_results["initialization"] = True
            test_results["performance"]["initialization_time"] = init_time
            print(f"✅ {db_name.upper()} initialized in {init_time:.3f}s")
            
            # Test storage operations
            print(f"\n📝 Testing memory storage operations...")
            for i, test_item in enumerate(self.test_data):
                try:
                    start_time = time.time()
                    success = await memory.add(
                        test_item["content"], 
                        test_item["namespace"], 
                        test_item["metadata"]
                    )
                    storage_time = time.time() - start_time
                    
                    result = {
                        "index": i,
                        "success": success,
                        "time": storage_time,
                        "content_preview": test_item["content"][:50] + "...",
                        "namespace": test_item["namespace"]
                    }
                    test_results["storage_operations"].append(result)
                    
                    if success:
                        test_results["total_memories_stored"] += 1
                        print(f"  ✅ Stored memory {i+1}: {test_item['content'][:30]}... ({storage_time:.3f}s)")
                    else:
                        print(f"  ❌ Failed to store memory {i+1}")
                        
                except Exception as e:
                    error_msg = f"Storage error for item {i}: {str(e)}"
                    test_results["errors"].append(error_msg)
                    print(f"  ❌ Error storing memory {i+1}: {e}")
            
            # Test search operations
            print(f"\n🔍 Testing search operations...")
            total_search_time = 0
            
            for i, (query, namespace) in enumerate(self.test_queries):
                try:
                    start_time = time.time()
                    results = await memory.search(query, namespace, limit=3)
                    search_time = time.time() - start_time
                    total_search_time += search_time
                    
                    # Handle the search results format (dict with 'results' key)
                    actual_results = []
                    if isinstance(results, dict) and 'results' in results:
                        actual_results = results['results']
                    elif isinstance(results, list):
                        actual_results = results
                    else:
                        actual_results = []
                    
                    search_result = {
                        "index": i,
                        "query": query,
                        "namespace": namespace,
                        "results_count": len(actual_results),
                        "time": search_time,
                        "results": []
                    }
                    
                    if actual_results and len(actual_results) > 0:
                        for j, result in enumerate(actual_results[:2]):  # Show top 2 results
                            if isinstance(result, dict):
                                search_result["results"].append({
                                    "content_preview": result.get("content", "No content")[:40] + "...",
                                    "relevance": result.get("relevance", 0)
                                })
                            else:
                                search_result["results"].append({
                                    "content_preview": str(result)[:40] + "...",
                                    "relevance": "unknown"
                                })
                        
                        test_results["total_searches_performed"] += 1
                        print(f"  ✅ Query '{query}': {len(actual_results)} results ({search_time:.3f}s)")
                        for j, res in enumerate(search_result["results"]):
                            print(f"     {j+1}. {res['content_preview']} (rel: {res['relevance']})")
                    else:
                        print(f"  ⚠️  Query '{query}': No results ({search_time:.3f}s)")
                    
                    test_results["search_operations"].append(search_result)
                    
                except Exception as e:
                    error_msg = f"Search error for query '{query}': {str(e)}"
                    test_results["errors"].append(error_msg)
                    print(f"  ❌ Error searching '{query}': {e}")
            
            # Calculate performance metrics
            test_results["performance"]["total_search_time"] = total_search_time
            test_results["performance"]["avg_search_time"] = total_search_time / len(self.test_queries) if self.test_queries else 0
            test_results["performance"]["avg_storage_time"] = sum(op["time"] for op in test_results["storage_operations"]) / len(test_results["storage_operations"]) if test_results["storage_operations"] else 0
            
            # Test namespace operations
            print(f"\n🗂️  Testing namespace operations...")
            try:
                namespaces = await memory.get_namespaces()
                print(f"  ✅ Found namespaces: {namespaces}")
                test_results["namespaces"] = namespaces
            except Exception as e:
                error_msg = f"Namespace error: {str(e)}"
                test_results["errors"].append(error_msg)
                print(f"  ❌ Error getting namespaces: {e}")
            
            # Get storage info
            try:
                storage_info = await memory.get_storage_info()
                test_results["storage_info"] = storage_info
                print(f"  ✅ Storage type: {storage_info.get('storage_type', 'unknown')}")
                print(f"  ✅ Vector support: {storage_info.get('vector_support', False)}")
            except Exception as e:
                error_msg = f"Storage info error: {str(e)}"
                test_results["errors"].append(error_msg)
                print(f"  ❌ Error getting storage info: {e}")
            
        except Exception as e:
            error_msg = f"Critical error during {db_name} testing: {str(e)}"
            test_results["errors"].append(error_msg)
            print(f"❌ Critical error: {e}")
        
        # Summary
        print(f"\n📊 {db_name.upper()} TEST SUMMARY:")
        print(f"  • Initialization: {'✅ Success' if test_results['initialization'] else '❌ Failed'}")
        print(f"  • Memories stored: {test_results['total_memories_stored']}/{len(self.test_data)}")
        print(f"  • Searches performed: {test_results['total_searches_performed']}/{len(self.test_queries)}")
        print(f"  • Errors: {len(test_results['errors'])}")
        print(f"  • Avg storage time: {test_results['performance'].get('avg_storage_time', 0):.3f}s")
        print(f"  • Avg search time: {test_results['performance'].get('avg_search_time', 0):.3f}s")
        
        return test_results
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test suite for all vector databases."""
        print("🎯 ENGRAM VECTOR DATABASE COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print("Testing: FAISS, ChromaDB, and LanceDB implementations")
        print("Platform: M4 Max with Metal support")
        print("=" * 80)
        
        # Test each vector database
        databases = ["faiss", "chromadb", "lancedb"]
        
        for db_name in databases:
            try:
                self.results[db_name] = await self.test_vector_db(db_name)
                
                # Small delay between tests
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ Failed to test {db_name}: {e}")
                self.results[db_name] = {
                    "db_name": db_name,
                    "initialization": False,
                    "errors": [f"Test setup failed: {str(e)}"],
                    "total_memories_stored": 0,
                    "total_searches_performed": 0
                }
        
        # Restore configuration
        self.restore_vector_db_config()
        
        # Generate comprehensive report
        await self.generate_test_report()
        
        return self.results
    
    async def generate_test_report(self) -> None:
        """Generate comprehensive test report."""
        print(f"\n{'='*80}")
        print("📈 COMPREHENSIVE TEST REPORT")
        print(f"{'='*80}")
        
        # Summary table
        print(f"\n{'Database':<12} {'Init':<6} {'Stored':<8} {'Searched':<10} {'Errors':<8} {'Avg Store':<12} {'Avg Search':<12}")
        print("-" * 80)
        
        for db_name, results in self.results.items():
            init_status = "✅" if results.get("initialization", False) else "❌"
            stored = f"{results.get('total_memories_stored', 0)}/{len(self.test_data)}"
            searched = f"{results.get('total_searches_performed', 0)}/{len(self.test_queries)}"
            errors = len(results.get("errors", []))
            avg_store = f"{results.get('performance', {}).get('avg_storage_time', 0):.3f}s"
            avg_search = f"{results.get('performance', {}).get('avg_search_time', 0):.3f}s"
            
            print(f"{db_name.upper():<12} {init_status:<6} {stored:<8} {searched:<10} {errors:<8} {avg_store:<12} {avg_search:<12}")
        
        # Detailed analysis
        print(f"\n🏆 PERFORMANCE ANALYSIS:")
        
        # Find fastest for each operation
        fastest_init = min(self.results.items(), key=lambda x: x[1].get('performance', {}).get('initialization_time', float('inf')))
        fastest_store = min(self.results.items(), key=lambda x: x[1].get('performance', {}).get('avg_storage_time', float('inf')))
        fastest_search = min(self.results.items(), key=lambda x: x[1].get('performance', {}).get('avg_search_time', float('inf')))
        
        print(f"  • Fastest initialization: {fastest_init[0].upper()} ({fastest_init[1].get('performance', {}).get('initialization_time', 0):.3f}s)")
        print(f"  • Fastest storage: {fastest_store[0].upper()} ({fastest_store[1].get('performance', {}).get('avg_storage_time', 0):.3f}s avg)")
        print(f"  • Fastest search: {fastest_search[0].upper()} ({fastest_search[1].get('performance', {}).get('avg_search_time', 0):.3f}s avg)")
        
        # Success rates
        print(f"\n✅ SUCCESS RATES:")
        for db_name, results in self.results.items():
            storage_rate = (results.get('total_memories_stored', 0) / len(self.test_data)) * 100
            search_rate = (results.get('total_searches_performed', 0) / len(self.test_queries)) * 100
            print(f"  • {db_name.upper()}: Storage {storage_rate:.1f}%, Search {search_rate:.1f}%")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        working_dbs = [db for db, results in self.results.items() if results.get('initialization', False) and results.get('total_memories_stored', 0) > 0]
        
        if 'lancedb' in working_dbs:
            print("  🎯 LanceDB: Best choice for M4 Max - optimized for Apple Silicon with Metal support")
        if 'faiss' in working_dbs:
            print("  ⚡ FAISS: Excellent for high-performance applications requiring GPU acceleration")
        if 'chromadb' in working_dbs:
            print("  🔧 ChromaDB: Great for feature-rich applications needing built-in embedding functions")
        
        if len(working_dbs) == 3:
            print("  🎉 All three vector databases are working correctly!")
            print("  🔄 Auto-detection system can safely choose optimal DB for each platform")
        elif len(working_dbs) > 0:
            print(f"  ⚠️  {len(working_dbs)}/3 databases working - consider fixing failed implementations")
        else:
            print("  ❌ No vector databases working - check dependencies and configuration")
        
        # Save detailed results to file
        report_file = Path("/Users/cskoons/projects/github/Tekton/Engram/vector_db_test_report.json")
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {report_file}")

async def main():
    """Main test runner."""
    tester = VectorDBTester()
    
    try:
        results = await tester.run_comprehensive_test()
        print(f"\n🎯 Test suite completed successfully!")
        return results
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return None

if __name__ == "__main__":
    # Run the test suite
    results = asyncio.run(main())
    
    if results:
        print(f"\n✅ All tests completed. Check the report above for detailed analysis.")
    else:
        print(f"\n❌ Test suite encountered errors.")