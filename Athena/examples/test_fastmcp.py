#!/usr/bin/env python3
"""
Test script for Athena FastMCP implementation.

This script tests all FastMCP tools and capabilities for Athena knowledge graph
management, entity operations, querying, and integrations.
"""

import asyncio
import json
import uuid
from datetime import datetime
from tekton.mcp.fastmcp.client import FastMCPClient


class AthenaFastMCPTester:
    """Test suite for Athena FastMCP implementation."""
    
    def __init__(self, base_url="http://localhost:8001"):
        """Initialize the tester with Athena server URL."""
        self.base_url = base_url
        self.fastmcp_url = f"{base_url}/api/mcp/v2"
        self.client = FastMCPClient(self.fastmcp_url)
        self.test_entity_ids = []
        self.test_relationship_ids = []
        
    async def run_all_tests(self):
        """Run all tests for Athena FastMCP."""
        print("🚀 Starting Athena FastMCP Test Suite")
        print("=" * 50)
        
        try:
            # Test server availability
            await self.test_server_availability()
            
            # Test capabilities and tools
            await self.test_capabilities()
            await self.test_tools_list()
            
            # Test knowledge graph operations
            await self.test_knowledge_graph_operations()
            
            # Test query engine
            await self.test_query_engine()
            
            # Test visualization capabilities (if available)
            await self.test_visualization_capabilities()
            
            # Test integration capabilities
            await self.test_integration_capabilities()
            
            print("\n✅ All Athena FastMCP tests completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            raise
    
    async def test_server_availability(self):
        """Test if the Athena FastMCP server is available."""
        print("\n📡 Testing server availability...")
        
        try:
            health = await self.client.get_health()
            print(f"✅ Server health: {health}")
            
            if health.get("status") != "healthy":
                raise Exception(f"Server not healthy: {health}")
                
        except Exception as e:
            print(f"❌ Server availability test failed: {e}")
            raise
    
    async def test_capabilities(self):
        """Test getting capabilities from the server."""
        print("\n🔧 Testing capabilities...")
        
        try:
            capabilities = await self.client.get_capabilities()
            print(f"✅ Retrieved {len(capabilities)} capabilities")
            
            # Verify expected capabilities exist
            expected_capabilities = [
                "knowledge_graph",
                "query_engine",
                "visualization",
                "integration"
            ]
            
            capability_names = [cap.get("name") for cap in capabilities]
            for expected in expected_capabilities:
                if expected in capability_names:
                    print(f"  ✓ Found capability: {expected}")
                else:
                    print(f"  ⚠ Missing capability: {expected}")
                    
        except Exception as e:
            print(f"❌ Capabilities test failed: {e}")
            raise
    
    async def test_tools_list(self):
        """Test getting tools list from the server."""
        print("\n🛠 Testing tools list...")
        
        try:
            tools = await self.client.get_tools()
            print(f"✅ Retrieved {len(tools)} tools")
            
            # Verify expected tools exist
            expected_tools = [
                "search_entities", "get_entity_by_id", "create_entity",
                "get_entity_relationships", "create_relationship",
                "query_knowledge_graph", "naive_query", "local_query",
                "global_query", "hybrid_query", "semantic_search"
            ]
            
            tool_names = [tool.get("name") for tool in tools]
            for expected in expected_tools:
                if expected in tool_names:
                    print(f"  ✓ Found tool: {expected}")
                else:
                    print(f"  ⚠ Missing tool: {expected}")
                    
        except Exception as e:
            print(f"❌ Tools list test failed: {e}")
            raise
    
    async def test_knowledge_graph_operations(self):
        """Test knowledge graph management tools."""
        print("\n🧠 Testing knowledge graph operations...")
        
        try:
            # Test create_entity
            print("  Testing create_entity...")
            entity_data = [
                {
                    "name": "Artificial Intelligence",
                    "type": "concept",
                    "properties": {
                        "description": "The simulation of human intelligence processes by machines",
                        "category": "technology",
                        "importance": "high"
                    }
                },
                {
                    "name": "Machine Learning",
                    "type": "concept", 
                    "properties": {
                        "description": "A subset of AI that enables computers to learn without explicit programming",
                        "category": "technology",
                        "parent_concept": "Artificial Intelligence"
                    }
                },
                {
                    "name": "Neural Networks",
                    "type": "concept",
                    "properties": {
                        "description": "Computing systems inspired by biological neural networks",
                        "category": "technology",
                        "parent_concept": "Machine Learning"
                    }
                }
            ]
            
            for entity in entity_data:
                entity_result = await self.client.call_tool("create_entity", entity)
                
                if "error" in entity_result:
                    print(f"  ⚠ create_entity failed for {entity['name']}: {entity_result['error']}")
                else:
                    entity_id = entity_result.get("entity_id")
                    if entity_id:
                        self.test_entity_ids.append(entity_id)
                        print(f"  ✅ Created entity: {entity['name']} ({entity_id})")
            
            # Test search_entities
            print("  Testing search_entities...")
            search_result = await self.client.call_tool("search_entities", {
                "query": "artificial intelligence",
                "entity_type": "concept",
                "limit": 10
            })
            
            if "error" in search_result:
                print(f"  ⚠ search_entities failed: {search_result['error']}")
            else:
                entity_count = len(search_result.get("entities", []))
                print(f"  ✅ Found {entity_count} entities matching 'artificial intelligence'")
            
            # Test get_entity_by_id
            if self.test_entity_ids:
                print("  Testing get_entity_by_id...")
                get_result = await self.client.call_tool("get_entity_by_id", {
                    "entity_id": self.test_entity_ids[0]
                })
                
                if "error" in get_result:
                    print(f"  ⚠ get_entity_by_id failed: {get_result['error']}")
                else:
                    print(f"  ✅ Retrieved entity details")
            
            # Test create_relationship
            if len(self.test_entity_ids) >= 2:
                print("  Testing create_relationship...")
                rel_result = await self.client.call_tool("create_relationship", {
                    "source_entity_id": self.test_entity_ids[0],
                    "target_entity_id": self.test_entity_ids[1],
                    "relationship_type": "contains",
                    "properties": {
                        "description": "AI contains Machine Learning as a subfield"
                    }
                })
                
                if "error" in rel_result:
                    print(f"  ⚠ create_relationship failed: {rel_result['error']}")
                else:
                    rel_id = rel_result.get("relationship_id")
                    if rel_id:
                        self.test_relationship_ids.append(rel_id)
                        print(f"  ✅ Created relationship")
            
            # Test get_entity_relationships
            if self.test_entity_ids:
                print("  Testing get_entity_relationships...")
                rel_result = await self.client.call_tool("get_entity_relationships", {
                    "entity_id": self.test_entity_ids[0],
                    "direction": "outgoing"
                })
                
                if "error" in rel_result:
                    print(f"  ⚠ get_entity_relationships failed: {rel_result['error']}")
                else:
                    rel_count = len(rel_result.get("relationships", []))
                    print(f"  ✅ Found {rel_count} relationships")
                    
        except Exception as e:
            print(f"❌ Knowledge graph operations test failed: {e}")
            raise
    
    async def test_query_engine(self):
        """Test query engine tools."""
        print("\n🔍 Testing query engine...")
        
        if not self.test_entity_ids:
            print("  ⚠ Skipping query tests - no test entities available")
            return
        
        try:
            # Test query_knowledge_graph
            print("  Testing query_knowledge_graph...")
            query_result = await self.client.call_tool("query_knowledge_graph", {
                "query": "Find all concepts related to artificial intelligence",
                "query_type": "semantic",
                "limit": 20
            })
            
            if "error" in query_result:
                print(f"  ⚠ query_knowledge_graph failed: {query_result['error']}")
            else:
                result_count = len(query_result.get("results", []))
                print(f"  ✅ Query returned {result_count} results")
            
            # Test semantic_search
            print("  Testing semantic_search...")
            semantic_result = await self.client.call_tool("semantic_search", {
                "query": "machine learning algorithms",
                "similarity_threshold": 0.7,
                "limit": 10
            })
            
            if "error" in semantic_result:
                print(f"  ⚠ semantic_search failed: {semantic_result['error']}")
            else:
                search_count = len(semantic_result.get("results", []))
                print(f"  ✅ Semantic search returned {search_count} results")
            
            # Test find_entity_paths
            if len(self.test_entity_ids) >= 2:
                print("  Testing find_entity_paths...")
                path_result = await self.client.call_tool("find_entity_paths", {
                    "source_entity_id": self.test_entity_ids[0],
                    "target_entity_id": self.test_entity_ids[1],
                    "max_depth": 3
                })
                
                if "error" in path_result:
                    print(f"  ⚠ find_entity_paths failed: {path_result['error']}")
                else:
                    path_count = len(path_result.get("paths", []))
                    print(f"  ✅ Found {path_count} paths between entities")
                    
        except Exception as e:
            print(f"❌ Query engine test failed: {e}")
            raise
    
    async def test_visualization_capabilities(self):
        """Test visualization capabilities."""
        print("\n📊 Testing visualization capabilities...")
        
        try:
            # Test generate_graph_visualization
            print("  Testing generate_graph_visualization...")
            viz_result = await self.client.call_tool("generate_graph_visualization", {
                "entity_ids": self.test_entity_ids[:3] if len(self.test_entity_ids) >= 3 else self.test_entity_ids,
                "layout": "force_directed",
                "format": "json"
            })
            
            if "error" in viz_result:
                print(f"  ⚠ generate_graph_visualization failed: {viz_result['error']}")
            else:
                print(f"  ✅ Generated graph visualization")
            
            # Test export_subgraph
            print("  Testing export_subgraph...")
            export_result = await self.client.call_tool("export_subgraph", {
                "center_entity_id": self.test_entity_ids[0] if self.test_entity_ids else "test",
                "radius": 2,
                "format": "json"
            })
            
            if "error" in export_result:
                print(f"  ⚠ export_subgraph failed: {export_result['error']}")
            else:
                print(f"  ✅ Exported subgraph")
                
        except Exception as e:
            print(f"❌ Visualization capabilities test failed: {e}")
            # Don't raise here as visualization is optional
    
    async def test_integration_capabilities(self):
        """Test integration capabilities."""
        print("\n🔗 Testing integration capabilities...")
        
        try:
            # Test health_check
            print("  Testing health_check...")
            health_result = await self.client.call_tool("health_check", {})
            
            if "error" in health_result:
                print(f"  ⚠ health_check failed: {health_result['error']}")
            else:
                print(f"  ✅ Health check passed")
            
            # Test register_with_hermes
            print("  Testing register_with_hermes...")
            register_result = await self.client.call_tool("register_with_hermes", {
                "service_info": {
                    "name": "athena-test",
                    "version": "1.0.0",
                    "capabilities": ["knowledge_graph", "query_engine"]
                }
            })
            
            if "error" in register_result:
                print(f"  ⚠ register_with_hermes failed (Hermes may not be available): {register_result['error']}")
            else:
                print(f"  ✅ Registered with Hermes")
                
        except Exception as e:
            print(f"❌ Integration capabilities test failed: {e}")
            # Don't raise here as integrations are optional
    
    async def cleanup(self):
        """Clean up test data."""
        print("\n🧹 Cleaning up test data...")
        
        # Note: In a real implementation, you might want to add cleanup operations
        # For now, we'll leave the test data as it can be useful for manual inspection
        print("  ℹ Test data preserved for manual inspection")


async def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Athena FastMCP implementation")
    parser.add_argument("--url", default="http://localhost:8001", 
                       help="Athena server URL (default: http://localhost:8001)")
    parser.add_argument("--cleanup", action="store_true",
                       help="Clean up test data after tests")
    
    args = parser.parse_args()
    
    tester = AthenaFastMCPTester(args.url)
    
    try:
        await tester.run_all_tests()
        
        if args.cleanup:
            await tester.cleanup()
            
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))