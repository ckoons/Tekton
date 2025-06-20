#!/usr/bin/env python3
"""
Check what's happening with panels
"""
import httpx
import asyncio

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def check_panels():
    async with httpx.AsyncClient(timeout=10.0) as client:
        print("=== Checking Panel States ===\n")
        
        # Navigate to Rhetor
        print("1. Navigating to Rhetor...")
        nav_resp = await client.post(MCP_URL, json={
            "tool_name": "ui_navigate",
            "arguments": {"component": "rhetor"}
        })
        print(f"   Status: {nav_resp.json()['status']}")
        
        await asyncio.sleep(2)
        
        # Capture the whole UI
        print("\n2. Capturing full UI...")
        capture_resp = await client.post(MCP_URL, json={
            "tool_name": "ui_capture",
            "arguments": {}
        })
        
        result = capture_resp.json()['result']
        loaded = result.get('loaded_component', 'Unknown')
        print(f"   Loaded component: {loaded}")
        
        # Check for rhetor in the HTML
        html = result.get('html', '')
        if 'rhetor' in html.lower():
            print("   ✓ Found 'rhetor' in HTML")
            # Count how many times
            count = html.lower().count('rhetor')
            print(f"   Found {count} occurrences of 'rhetor'")
        else:
            print("   ✗ No 'rhetor' found in HTML")
            
        # Check selectors
        selectors = result.get('selectors_available', {})
        print("\n3. Checking available selectors:")
        for sel, count in selectors.items():
            if count > 0 and any(x in sel for x in ['panel', 'rhetor', 'component']):
                print(f"   {sel}: {count}")

asyncio.run(check_panels())