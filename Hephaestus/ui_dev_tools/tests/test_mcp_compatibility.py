#!/usr/bin/env python3
"""
Test the new MCP server to ensure it maintains compatibility
"""
import asyncio
import httpx
import json
import sys

MCP_URL = "http://localhost:8088"


async def test_health_endpoint():
    """Test that health endpoint still works"""
    print("Testing /health endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{MCP_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Health check passed: {data}")
                return True
            else:
                print(f"✗ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Cannot connect to MCP server: {e}")
            print("  Make sure to run: ./run_mcp.sh")
            return False


async def test_tool_list():
    """Test listing available tools"""
    print("\nTesting /api/mcp/v2/tools endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MCP_URL}/api/mcp/v2/tools")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {data['count']} tools")
            # Show categories
            categories = set(tool['category'] for tool in data['tools'])
            print(f"  Categories: {', '.join(sorted(categories))}")
            return True
        else:
            print(f"✗ Failed to list tools: {response.status_code}")
            return False


async def test_code_reader():
    """Test CodeReader via MCP"""
    print("\nTesting CodeReader via MCP...")
    async with httpx.AsyncClient() as client:
        # List components
        response = await client.post(
            f"{MCP_URL}/api/mcp/v2/execute",
            json={
                "tool_name": "code_list_components",
                "arguments": {}
            }
        )
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                components = data['data']['components']
                print(f"✓ CodeReader working: Found {len(components)} components")
                print(f"  Components: {', '.join(components[:5])}...")
                return True
        
        print(f"✗ CodeReader failed")
        return False


async def test_navigator():
    """Test Navigator via MCP"""
    print("\nTesting Navigator via MCP...")
    async with httpx.AsyncClient() as client:
        # Get current component
        response = await client.post(
            f"{MCP_URL}/api/mcp/v2/execute",
            json={
                "tool_name": "navigate_get_current",
                "arguments": {}
            }
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Navigator working: {data}")
            return True
        
        print(f"✗ Navigator failed")
        return False


async def test_comparator():
    """Test Comparator via MCP"""
    print("\nTesting Comparator via MCP...")
    async with httpx.AsyncClient() as client:
        # Compare rhetor component
        response = await client.post(
            f"{MCP_URL}/api/mcp/v2/execute",
            json={
                "tool_name": "compare_component",
                "arguments": {"component_name": "rhetor"}
            }
        )
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                summary = data['data']['summary']
                print(f"✓ Comparator working:")
                print(f"  Source tags: {summary['code_tags']}")
                print(f"  Browser tags: {summary['browser_tags']}")
                print(f"  Dynamic tags added: {summary['dynamic_tags_added']}")
                return True
        
        print(f"✗ Comparator failed")
        return False


async def main():
    """Run all tests"""
    print("Testing new MCP server compatibility...\n")
    
    tests = [
        test_health_endpoint,
        test_tool_list,
        test_code_reader,
        test_navigator,
        test_comparator
    ]
    
    passed = 0
    for test in tests:
        if await test():
            passed += 1
        print()
    
    print(f"\nTest Summary: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✓ New MCP server is fully compatible!")
        print("\nTo replace the old server:")
        print("  1. Stop the current server (tekton-kill ui_devtools)")
        print("  2. mv mcp_server.py mcp_server_old.py")
        print("  3. mv mcp_server_new.py mcp_server.py")
        print("  4. Restart with ./run_mcp.sh")
    else:
        print("✗ Some compatibility issues found")


if __name__ == "__main__":
    asyncio.run(main())