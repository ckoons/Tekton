#!/usr/bin/env python3
"""
Test Engram health after cleanup.

Tests:
1. Service health check
2. Basic memory operations
3. Search functionality
4. API endpoints
"""

import httpx
import asyncio
import json
from datetime import datetime

ENGRAM_URL = "http://localhost:8000"

async def test_health():
    """Test Engram health endpoint."""
    print("1. Testing health endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{ENGRAM_URL}/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Service: {data.get('service', 'unknown')}")
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Status: {data.get('status', 'unknown')}")
                return True
        except Exception as e:
            print(f"   Error: {e}")
            return False
    return False

async def test_add_memory():
    """Test adding a memory."""
    print("\n2. Testing memory addition...")
    async with httpx.AsyncClient() as client:
        try:
            memory_data = {
                "content": f"Test memory from Engram cleanup - {datetime.now().isoformat()}",
                "namespace": "conversations",  # Use valid namespace
                "metadata": {
                    "source": "test_script",
                    "test_run": True
                }
            }
            response = await client.post(
                f"{ENGRAM_URL}/api/v1/memory",
                json=memory_data
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Memory ID: {data.get('id', 'unknown')}")
                print(f"   Success: {data.get('status') == 'success'}")
                return data.get('id')
        except Exception as e:
            print(f"   Error: {e}")
    return None

async def test_search():
    """Test search functionality."""
    print("\n3. Testing search...")
    async with httpx.AsyncClient() as client:
        try:
            search_data = {
                "query": "test memory cleanup",
                "namespace": "conversations",  # Use valid namespace
                "limit": 5
            }
            response = await client.post(
                f"{ENGRAM_URL}/api/v1/search",
                json=search_data
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"   Results found: {len(results)}")
                print(f"   Count: {data.get('count', 0)}")
                return True
        except Exception as e:
            print(f"   Error: {e}")
    return False

async def test_namespaces():
    """Test namespace listing."""
    print("\n4. Testing namespace listing...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{ENGRAM_URL}/api/v1/namespaces")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                # Handle both list and dict response formats
                if isinstance(data, list):
                    namespaces = data
                else:
                    namespaces = data.get('namespaces', [])
                print(f"   Namespaces: {', '.join(namespaces) if namespaces else 'none'}")
                return True
        except Exception as e:
            print(f"   Error: {e}")
    return False

async def test_discovery():
    """Test discovery endpoint."""
    print("\n5. Testing discovery endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{ENGRAM_URL}/api/v1/discovery")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                # Handle different response formats
                if isinstance(data, str):
                    print(f"   Response: {data}")
                elif isinstance(data, dict):
                    print(f"   Component: {data.get('component', 'unknown')}")
                    print(f"   Version: {data.get('version', 'unknown')}")
                    print(f"   Endpoints: {len(data.get('endpoints', []))}")
                return True
        except Exception as e:
            print(f"   Error: {e}")
    return False

async def main():
    """Run all tests."""
    print("Engram Health Check")
    print("=" * 50)
    print(f"Testing Engram at {ENGRAM_URL}")
    print()
    
    # Track results
    results = []
    
    # Run tests
    results.append(("Health Check", await test_health()))
    
    if results[0][1]:  # Only continue if health check passed
        memory_id = await test_add_memory()
        results.append(("Add Memory", memory_id is not None))
        
        results.append(("Search", await test_search()))
        results.append(("Namespaces", await test_namespaces()))
        results.append(("Discovery", await test_discovery()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ Engram is healthy and working correctly!")
    else:
        print("\n⚠️  Some tests failed. Check Engram logs for details.")

if __name__ == "__main__":
    asyncio.run(main())