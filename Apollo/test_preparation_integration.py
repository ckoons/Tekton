#!/usr/bin/env python3
"""
Integration test for Apollo Preparation System

Tests the complete flow:
1. Store memories in Apollo
2. Retrieve Context Brief via MCP
3. Test UI endpoints
4. Verify Rhetor integration
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from pathlib import Path

# Add paths for imports
apollo_root = Path(__file__).parent
sys.path.insert(0, str(apollo_root))
tekton_root = apollo_root.parent
sys.path.insert(0, str(tekton_root))

# Use shared URLs - no hardcoded ports!
from shared.urls import apollo_url, rhetor_url

# Get URLs from shared configuration
APOLLO_URL = apollo_url()
RHETOR_URL = rhetor_url()

async def test_apollo_preparation():
    """Test Apollo's preparation system"""
    print("🧪 Testing Apollo Preparation System")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Store a memory via API
        print("\n1️⃣ Testing memory storage...")
        memory_data = {
            "ci_source": "test-ci",
            "type": "decision",
            "summary": "Test decision memory",
            "content": "Decided to use Apollo for memory management",
            "tags": ["test", "apollo", "memory"],
            "priority": 8
        }
        
        try:
            async with session.post(
                f"{APOLLO_URL}/api/preparation/memory",
                json=memory_data
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✅ Memory stored: {result}")
                else:
                    print(f"❌ Failed to store memory: {resp.status}")
        except Exception as e:
            print(f"❌ Error storing memory: {e}")
        
        # Test 2: Search memories
        print("\n2️⃣ Testing memory search...")
        search_data = {
            "query": "apollo",
            "max_results": 10
        }
        
        try:
            async with session.post(
                f"{APOLLO_URL}/api/preparation/search",
                json=search_data
            ) as resp:
                if resp.status == 200:
                    memories = await resp.json()
                    print(f"✅ Found {len(memories)} memories")
                else:
                    print(f"❌ Search failed: {resp.status}")
        except Exception as e:
            print(f"❌ Error searching: {e}")
        
        # Test 3: Generate Context Brief
        print("\n3️⃣ Testing Context Brief generation...")
        brief_data = {
            "ci_name": "test-ci",
            "message": "Working on memory system",
            "max_tokens": 500
        }
        
        try:
            async with session.post(
                f"{APOLLO_URL}/api/preparation/brief",
                json=brief_data
            ) as resp:
                if resp.status == 200:
                    brief = await resp.json()
                    print(f"✅ Brief generated: {brief.get('tokens_used', 0)} tokens")
                    print(f"   Content preview: {brief.get('content', '')[:100]}...")
                else:
                    print(f"❌ Brief generation failed: {resp.status}")
        except Exception as e:
            print(f"❌ Error generating brief: {e}")
        
        # Test 4: Analyze relationships
        print("\n4️⃣ Testing relationship analysis...")
        try:
            async with session.post(
                f"{APOLLO_URL}/api/preparation/analyze"
            ) as resp:
                if resp.status == 200:
                    analysis = await resp.json()
                    print(f"✅ Analysis complete:")
                    print(f"   Landmarks: {analysis.get('landmarks', {})}")
                    print(f"   Relationships created: {analysis.get('relationships_created', 0)}")
                else:
                    print(f"❌ Analysis failed: {resp.status}")
        except Exception as e:
            print(f"❌ Error analyzing: {e}")
        
        # Test 5: Get statistics
        print("\n5️⃣ Testing statistics endpoint...")
        try:
            async with session.get(
                f"{APOLLO_URL}/api/preparation/statistics"
            ) as resp:
                if resp.status == 200:
                    stats = await resp.json()
                    print(f"✅ Statistics retrieved:")
                    print(f"   Total memories: {stats.get('total_memories', 0)}")
                    print(f"   Total tokens: {stats.get('total_tokens', 0)}")
                    print(f"   By type: {stats.get('by_type', {})}")
                else:
                    print(f"❌ Statistics failed: {resp.status}")
        except Exception as e:
            print(f"❌ Error getting stats: {e}")

async def test_mcp_tools():
    """Test Apollo's MCP tools"""
    print("\n\n🔧 Testing Apollo MCP Tools")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test MCP tool invocation
        print("\n1️⃣ Testing MCP get_context_brief...")
        mcp_request = {
            "tool_name": "get_context_brief",
            "arguments": {
                "ci_name": "test-ci",
                "message": "Testing MCP integration",
                "max_tokens": 500
            }
        }
        
        try:
            async with session.post(
                f"{APOLLO_URL}/mcp/tools/invoke",
                json=mcp_request
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✅ MCP tool worked: {result.get('status')}")
                else:
                    print(f"❌ MCP tool failed: {resp.status}")
        except Exception as e:
            print(f"❌ Error with MCP: {e}")

async def test_rhetor_integration():
    """Test Rhetor's integration with Apollo"""
    print("\n\n🎭 Testing Rhetor Integration")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test Rhetor completion with component context
        print("\n1️⃣ Testing Rhetor completion with Apollo context...")
        completion_request = {
            "message": "What memories do you have about Apollo?",
            "component_name": "test-ci",
            "task_type": "general",
            "provider_id": "ollama",
            "model_id": "llama3.3"
        }
        
        try:
            async with session.post(
                f"{RHETOR_URL}/complete",
                json=completion_request,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✅ Rhetor completion successful")
                    print(f"   Model: {result.get('model')}")
                    print(f"   Provider: {result.get('provider')}")
                    # Check if context was injected
                    if "Apollo" in result.get("content", ""):
                        print(f"   ✅ Context Brief was likely included")
                else:
                    print(f"❌ Rhetor completion failed: {resp.status}")
                    error = await resp.text()
                    print(f"   Error: {error}")
        except asyncio.TimeoutError:
            print(f"⚠️ Rhetor request timed out (might not have Ollama running)")
        except Exception as e:
            print(f"❌ Error with Rhetor: {e}")

async def main():
    """Run all tests"""
    print("🚀 Apollo Preparation System Integration Test")
    print("=" * 50)
    print(f"Apollo URL: {APOLLO_URL}")
    print(f"Rhetor URL: {RHETOR_URL}")
    print()
    
    # Check if services are running
    print("Checking services...")
    async with aiohttp.ClientSession() as session:
        # Check Apollo
        try:
            async with session.get(f"{APOLLO_URL}/health") as resp:
                if resp.status == 200:
                    print("✅ Apollo is running")
                else:
                    print("❌ Apollo is not healthy")
                    return
        except:
            print("❌ Apollo is not running - start it with: cd Apollo && python -m apollo.api.app")
            return
        
        # Check Rhetor
        try:
            async with session.get(f"{RHETOR_URL}/health") as resp:
                if resp.status == 200:
                    print("✅ Rhetor is running")
                else:
                    print("⚠️ Rhetor is not healthy")
        except:
            print("⚠️ Rhetor is not running - start it with: cd Rhetor && python -m rhetor.api.app_enhanced")
    
    # Run tests
    await test_apollo_preparation()
    await test_mcp_tools()
    await test_rhetor_integration()
    
    print("\n\n✨ Integration test complete!")
    print("\nNext steps:")
    print(f"1. Open Apollo UI at {APOLLO_URL}")
    print("2. Click on the 'Preparation' tab")
    print("3. You should see the test memories in the catalog")
    print("4. Try generating a Context Brief")
    print("5. Check the landmark visualization")

if __name__ == "__main__":
    asyncio.run(main())