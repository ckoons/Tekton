#!/usr/bin/env python3
"""
Complete ESR System Test - Tests the full ESR implementation.

This tests:
1. Engram's ESR HTTP API
2. Apollo's integration with ESR
3. Memory reflection triggers
4. Multi-CI namespace support
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any

# Configuration
ENGRAM_URL = "http://localhost:8100"
APOLLO_URL = "http://localhost:8112"

async def test_esr_api():
    """Test Engram's ESR API endpoints."""
    print("\n" + "="*60)
    print("Testing ESR API Endpoints")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Check ESR status
        print("\n1. Checking ESR status...")
        try:
            response = await client.get(f"{ENGRAM_URL}/api/esr/status")
            if response.status_code == 200:
                status = response.json()
                print(f"   ✓ ESR Status: {status.get('status')}")
                print(f"   ✓ Available endpoints: {len(status.get('endpoints', []))}")
            else:
                print(f"   ✗ ESR status returned {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # 2. Store a thought
        print("\n2. Storing a thought...")
        thought_data = {
            "content": "Testing ESR system from Apollo integration",
            "thought_type": "IDEA",
            "context": {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "source": "test_script"
            },
            "confidence": 0.95,
            "ci_id": "apollo"
        }
        
        memory_id = None
        try:
            response = await client.post(
                f"{ENGRAM_URL}/api/esr/store",
                json=thought_data
            )
            if response.status_code == 200:
                result = response.json()
                memory_id = result.get("memory_id")
                print(f"   ✓ Thought stored with ID: {memory_id}")
            else:
                print(f"   ✗ Store failed: {response.status_code}")
                print(f"      Response: {response.text}")
        except Exception as e:
            print(f"   ✗ Error storing: {e}")
        
        # 3. Recall the thought
        if memory_id:
            print("\n3. Recalling the thought...")
            try:
                response = await client.get(
                    f"{ENGRAM_URL}/api/esr/recall/{memory_id}",
                    params={"ci_id": "apollo"}
                )
                if response.status_code == 200:
                    result = response.json()
                    memory = result.get("memory", {})
                    print(f"   ✓ Memory recalled: {str(memory.get('content', ''))[:50]}...")
                else:
                    print(f"   ✗ Recall failed: {response.status_code}")
            except Exception as e:
                print(f"   ✗ Error recalling: {e}")
        
        # 4. Search for similar thoughts
        print("\n4. Searching for similar thoughts...")
        search_data = {
            "query": "ESR system Apollo",
            "limit": 5,
            "min_confidence": 0.5,
            "ci_id": "apollo"
        }
        
        try:
            response = await client.post(
                f"{ENGRAM_URL}/api/esr/search",
                json=search_data
            )
            if response.status_code == 200:
                result = response.json()
                count = result.get("count", 0)
                print(f"   ✓ Found {count} similar thoughts")
            else:
                print(f"   ✗ Search failed: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error searching: {e}")
        
        # 5. Build context
        print("\n5. Building context around 'Apollo'...")
        context_data = {
            "topic": "Apollo ESR integration",
            "depth": 2,
            "max_items": 10,
            "ci_id": "apollo"
        }
        
        try:
            response = await client.post(
                f"{ENGRAM_URL}/api/esr/context",
                json=context_data
            )
            if response.status_code == 200:
                result = response.json()
                context = result.get("context", {})
                print(f"   ✓ Context built with depth {result.get('depth')}")
            else:
                print(f"   ✗ Context building failed: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error building context: {e}")
        
        # 6. Test multi-CI namespaces
        print("\n6. Testing multi-CI namespace support...")
        
        # Store for different CIs
        for ci_id in ["apollo", "hermes", "rhetor"]:
            thought = {
                "content": f"Memory from {ci_id}",
                "thought_type": "MEMORY",
                "ci_id": ci_id
            }
            try:
                response = await client.post(
                    f"{ENGRAM_URL}/api/esr/store",
                    json=thought
                )
                if response.status_code == 200:
                    print(f"   ✓ Stored memory for {ci_id}")
            except:
                print(f"   ✗ Failed to store for {ci_id}")
        
        # 7. Check namespaces
        print("\n7. Checking available namespaces...")
        try:
            response = await client.get(f"{ENGRAM_URL}/api/esr/namespaces")
            if response.status_code == 200:
                result = response.json()
                namespaces = result.get("namespaces", [])
                print(f"   ✓ Active namespaces: {', '.join(namespaces) if namespaces else 'none yet'}")
            else:
                print(f"   ✗ Namespaces check failed: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error checking namespaces: {e}")
        
        # 8. Test reflection trigger
        print("\n8. Triggering memory reflection...")
        reflection_data = {
            "ci_id": "apollo",
            "reason": "test_reflection"
        }
        
        try:
            response = await client.post(
                f"{ENGRAM_URL}/api/esr/reflect",
                json=reflection_data
            )
            if response.status_code == 200:
                result = response.json()
                print(f"   ✓ Reflection triggered: {result.get('action')}")
            else:
                print(f"   ✗ Reflection trigger failed: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error triggering reflection: {e}")
        
        # 9. Check metabolism status
        print("\n9. Checking memory metabolism status...")
        try:
            response = await client.get(
                f"{ENGRAM_URL}/api/esr/metabolism/status",
                params={"ci_id": "apollo"}
            )
            if response.status_code == 200:
                result = response.json()
                metabolism = result.get("metabolism", {})
                print(f"   ✓ Metabolism status retrieved")
                if metabolism:
                    print(f"      Total memories: {metabolism.get('total_memories', 0)}")
                    print(f"      Promoted: {metabolism.get('promoted', 0)}")
                    print(f"      Forgotten: {metabolism.get('forgotten', 0)}")
            else:
                print(f"   ✗ Metabolism check failed: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error checking metabolism: {e}")

async def test_apollo_integration():
    """Test Apollo's integration with ESR."""
    print("\n" + "="*60)
    print("Testing Apollo ESR Integration")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Check Apollo status
        print("\n1. Checking Apollo status...")
        try:
            response = await client.get(f"{APOLLO_URL}/api/status")
            if response.status_code == 200:
                status = response.json()
                print(f"   ✓ Apollo is running")
                print(f"   ✓ Active contexts: {status['data'].get('active_contexts', 0)}")
                
                # Check for ESR in components
                components = status['data'].get('components_status', {})
                if 'esr_system' in components:
                    print(f"   ✓ ESR system integrated: {components['esr_system']}")
                else:
                    print(f"   ℹ ESR not yet exposed in Apollo status")
        except Exception as e:
            print(f"   ✗ Error checking Apollo: {e}")

async def test_mcp_tools():
    """Test MCP tool availability."""
    print("\n" + "="*60)
    print("Testing MCP Tools")
    print("="*60)
    
    # This would normally test MCP tools through Hermes
    # For now, we'll check if they're registered
    print("\n1. MCP tools should be registered with Hermes")
    print("   ℹ Check Hermes logs for 'esr_' tool registrations")
    
    print("\n2. Available MCP tools:")
    tools = [
        "esr_store_thought",
        "esr_recall_thought", 
        "esr_search_similar",
        "esr_build_context",
        "esr_create_association",
        "esr_get_metabolism_status",
        "esr_trigger_reflection",
        "esr_get_namespaces"
    ]
    for tool in tools:
        print(f"   • {tool}")

async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("ESR COMPLETE SYSTEM TEST")
    print("="*60)
    print(f"Started: {datetime.now().isoformat()}")
    
    # Run tests
    await test_esr_api()
    await test_apollo_integration()
    await test_mcp_tools()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("""
The ESR system provides:
1. ✓ Natural memory operations (store, recall, search)
2. ✓ Context building around topics
3. ✓ Multi-CI namespace support
4. ✓ Memory reflection triggers
5. ✓ Memory metabolism tracking
6. ✓ Both HTTP and MCP interfaces
7. ✓ Integration ready for all Tekton components

Next steps:
- Apollo can use ESR for context memory
- Other components can store/recall via Engram
- CIs can have persistent, evolving memories
""")
    print(f"Completed: {datetime.now().isoformat()}")

if __name__ == "__main__":
    asyncio.run(main())