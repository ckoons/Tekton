#!/usr/bin/env python3
"""Test Apollo ESR integration is working."""

import asyncio
import httpx
import json

async def test_apollo_esr():
    """Test Apollo's ESR integration."""
    base_url = "http://localhost:8112"
    
    print("Testing Apollo ESR Integration...")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Check Apollo is running
        try:
            response = await client.get(f"{base_url}/health")
            print(f"1. Apollo health check: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ Apollo is running")
        except Exception as e:
            print(f"   ✗ Apollo not responding: {e}")
            return
        
        # 2. Test memory storage through ESR
        try:
            test_memory = {
                "content": "Testing ESR integration from Coder-A",
                "memory_type": "test",
                "metadata": {
                    "test": True,
                    "source": "test_script"
                }
            }
            
            response = await client.post(
                f"{base_url}/api/memory/store",
                json=test_memory
            )
            
            if response.status_code == 200:
                result = response.json()
                memory_id = result.get("memory_id")
                print(f"2. Stored memory via ESR: {memory_id}")
                print("   ✓ ESR storage working")
                
                # 3. Try to recall the memory
                response = await client.get(f"{base_url}/api/memory/{memory_id}")
                if response.status_code == 200:
                    recalled = response.json()
                    print(f"3. Recalled memory: {recalled.get('content', 'No content')[:50]}...")
                    print("   ✓ ESR recall working")
            else:
                print(f"   ✗ Storage failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ ESR test failed: {e}")
        
        # 4. Check if Cognitive Workflows are available
        try:
            response = await client.get(f"{base_url}/api/status")
            if response.status_code == 200:
                status = response.json()
                if "esr_enabled" in status:
                    print(f"4. ESR enabled: {status['esr_enabled']}")
                    if status.get('esr_enabled'):
                        print("   ✓ Cognitive Workflows available")
                    else:
                        print("   ✗ Cognitive Workflows not available")
                        
                if "storage_mode" in status:
                    print(f"   Storage mode: {status['storage_mode']}")
        except Exception as e:
            print(f"   Status check failed: {e}")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_apollo_esr())