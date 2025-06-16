#!/usr/bin/env python3
"""Quick script to check available MCP endpoints in Rhetor."""

import asyncio
import aiohttp

async def check_endpoints():
    """Check which MCP endpoints are available."""
    base_url = "http://localhost:8003"
    
    endpoints_to_test = [
        # MCP v2 endpoints
        ("GET", "/api/mcp/v2/health"),
        ("GET", "/api/mcp/v2/capabilities"),
        ("GET", "/api/mcp/v2/tools"),
        ("GET", "/api/mcp/v2/llm-status"),
        
        # Standard API endpoints
        ("GET", "/health"),
        ("GET", "/ready"),
        ("GET", "/discovery"),
        
        # Check OpenAPI docs
        ("GET", "/docs"),
        ("GET", "/redoc"),
    ]
    
    async with aiohttp.ClientSession() as session:
        print("Checking Rhetor endpoints...\n")
        
        for method, endpoint in endpoints_to_test:
            try:
                url = f"{base_url}{endpoint}"
                if method == "GET":
                    async with session.get(url) as resp:
                        status = resp.status
                        if status == 200:
                            print(f"✓ {method} {endpoint} - OK")
                        else:
                            print(f"✗ {method} {endpoint} - Status {status}")
                elif method == "POST":
                    async with session.post(url, json={}) as resp:
                        status = resp.status
                        if status in [200, 422]:  # 422 is OK for POST without proper data
                            print(f"✓ {method} {endpoint} - Available")
                        else:
                            print(f"✗ {method} {endpoint} - Status {status}")
            except Exception as e:
                print(f"✗ {method} {endpoint} - Error: {e}")
        
        # Check if MCP tools are registered
        print("\nChecking MCP tools...")
        try:
            async with session.get(f"{base_url}/api/mcp/v2/tools") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "tools" in data:
                        print(f"\nFound {len(data['tools'])} MCP tools:")
                        for tool in data['tools'][:5]:  # Show first 5
                            print(f"  - {tool.get('name', 'Unknown')}")
                        if len(data['tools']) > 5:
                            print(f"  ... and {len(data['tools']) - 5} more")
                    else:
                        print("Response doesn't contain tools list")
        except Exception as e:
            print(f"Error getting tools: {e}")

if __name__ == "__main__":
    print("Checking Rhetor MCP endpoints...")
    print("Make sure Rhetor is running on port 8003\n")
    asyncio.run(check_endpoints())