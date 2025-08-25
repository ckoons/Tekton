#!/usr/bin/env python3
"""
Integration test for Rhetor MCP tools with live components.
"""

import asyncio
import httpx
import json
import sys


async def test_mcp_integration():
    """Test MCP integration with live components."""
    base_url = "http://localhost:8003"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n" + "="*60)
        print("Rhetor MCP Integration Test")
        print("="*60)
        
        # 1. Test MCP health
        print("\n1. Testing MCP Health")
        try:
            response = await client.get(f"{base_url}/api/mcp/v2/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✓ MCP service is healthy")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # 2. Test capabilities
        print("\n2. Testing Capabilities Endpoint")
        try:
            response = await client.get(f"{base_url}/api/mcp/v2/capabilities")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Found {data['count']} capabilities")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # 3. Test tools listing
        print("\n3. Testing Tools Endpoint")
        try:
            response = await client.get(f"{base_url}/api/mcp/v2/tools")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Found {data['count']} tools")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # 4. Test CI Specialists listing
        print("\n4. Testing CI Specialists Tool")
        try:
            response = await client.post(
                f"{base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "ListAISpecialists",
                    "arguments": {}
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success' and data.get('result'):
                    specialists = data['result'].get('specialists', [])
                    print(f"   ✓ Found {len(specialists)} specialists")
                    for spec in specialists[:3]:  # Show first 3
                        print(f"     - {spec.get('name', 'Unknown')}")
                else:
                    print(f"   ✗ Tool returned error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ✗ HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # 5. Test LLM model listing
        print("\n5. Testing LLM Models Tool")
        try:
            response = await client.post(
                f"{base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "GetAvailableModels",
                    "arguments": {}
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success' and data.get('result'):
                    providers = data['result'].get('providers', {})
                    print(f"   ✓ Found {len(providers)} providers")
                    for provider, info in list(providers.items())[:3]:
                        models_count = len(info.get('models', []))
                        print(f"     - {provider}: {models_count} models")
                else:
                    print(f"   ✗ Tool returned error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ✗ HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # 6. Test context analysis tool
        print("\n6. Testing Context Analysis Tool")
        try:
            response = await client.post(
                f"{base_url}/api/mcp/v2/process",
                json={
                    "tool_name": "AnalyzeContextUsage",
                    "arguments": {
                        "context_id": "test",
                        "time_period": "last_hour"
                    }
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    print(f"   ✓ Context analysis completed")
                else:
                    print(f"   ✗ Tool returned error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ✗ HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print("\n" + "="*60)
        print("Integration Test Complete")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(test_mcp_integration())