#!/usr/bin/env python3
"""
Test script to verify Rhetor API endpoints are properly configured.

This tests:
1. /api/v1/generate endpoint
2. /api/v1/chat endpoint  
3. /api/models/assignments endpoint
"""

import asyncio
import aiohttp
import json
import sys

RHETOR_URL = "http://localhost:8103"


async def test_generate_endpoint():
    """Test the /api/v1/generate endpoint."""
    print("\n=== Testing /api/v1/generate ===")
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "prompt": "Say hello",
            "temperature": 0.5,
            "max_tokens": 10,
            "component": "test",
            "capability": "reasoning"
        }
        
        try:
            async with session.post(f"{RHETOR_URL}/api/v1/generate", json=payload) as resp:
                print(f"Status: {resp.status}")
                
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✓ Success: Got response")
                    print(f"  Response: {data.get('response', 'N/A')[:100]}...")
                    print(f"  Model: {data.get('model', 'N/A')}")
                    return True
                else:
                    text = await resp.text()
                    print(f"✗ Failed: {resp.status} - {text}")
                    return False
                    
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


async def test_chat_endpoint():
    """Test the /api/v1/chat endpoint."""
    print("\n=== Testing /api/v1/chat ===")
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "temperature": 0.5,
            "max_tokens": 10,
            "component": "test",
            "capability": "chat"
        }
        
        try:
            async with session.post(f"{RHETOR_URL}/api/v1/chat", json=payload) as resp:
                print(f"Status: {resp.status}")
                
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✓ Success: Got response")
                    
                    # Check both response formats
                    if 'response' in data:
                        print(f"  Response field: {data.get('response', 'N/A')[:100]}...")
                    if 'content' in data:
                        print(f"  Content field: {data.get('content', 'N/A')[:100]}...")
                    
                    print(f"  Model: {data.get('model', 'N/A')}")
                    
                    # Check that we have at least one response field
                    if 'response' in data or 'content' in data:
                        return True
                    else:
                        print("✗ Warning: No response or content field found")
                        return False
                else:
                    text = await resp.text()
                    print(f"✗ Failed: {resp.status} - {text}")
                    return False
                    
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


async def test_model_assignments_endpoint():
    """Test the /api/models/assignments endpoint."""
    print("\n=== Testing /api/models/assignments ===")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{RHETOR_URL}/api/models/assignments") as resp:
                print(f"Status: {resp.status}")
                
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✓ Success: Got assignments")
                    
                    # Check structure
                    if 'defaults' in data:
                        print(f"  Defaults found: {list(data['defaults'].keys())}")
                    if 'components' in data:
                        print(f"  Components found: {list(data['components'].keys())[:5]}...")
                    
                    return True
                else:
                    text = await resp.text()
                    print(f"✗ Failed: {resp.status} - {text}")
                    return False
                    
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


async def test_rhetor_client():
    """Test using the RhetorClient."""
    print("\n=== Testing RhetorClient ===")
    
    # Import our client
    sys.path.insert(0, '/Users/cskoons/projects/github/Coder-A')
    from shared.rhetor_client import RhetorClient
    
    client = RhetorClient(component="test")
    
    try:
        # Test generate
        response = await client.generate(
            prompt="Say hello",
            capability="reasoning",
            max_tokens=10
        )
        
        if response and not response.startswith("Error:"):
            print(f"✓ Generate works: {response[:50]}...")
        else:
            print(f"✗ Generate failed: {response}")
            return False
        
        # Test chat
        response = await client.chat(
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )
        
        if response and not response.startswith("Error:"):
            print(f"✓ Chat works: {response[:50]}...")
        else:
            print(f"✗ Chat failed: {response}")
            return False
            
        await client.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        await client.close()
        return False


async def main():
    """Run all tests."""
    print("=" * 50)
    print("RHETOR ENDPOINT TESTS")
    print("=" * 50)
    
    # Check if Rhetor is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{RHETOR_URL}/health") as resp:
                if resp.status == 200:
                    print(f"✓ Rhetor is running on {RHETOR_URL}")
                else:
                    print(f"⚠ Rhetor returned status {resp.status}")
    except Exception as e:
        print(f"✗ Rhetor is not accessible: {e}")
        print("Please ensure Rhetor is running on port 8103")
        return
    
    # Run tests
    results = []
    
    results.append(await test_generate_endpoint())
    results.append(await test_chat_endpoint())
    results.append(await test_model_assignments_endpoint())
    results.append(await test_rhetor_client())
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ ALL TESTS PASSED ({passed}/{total})")
    else:
        print(f"⚠ {passed}/{total} tests passed")
        
    print("\nRhetor API endpoints are", "properly configured!" if passed == total else "partially configured.")


if __name__ == "__main__":
    asyncio.run(main())