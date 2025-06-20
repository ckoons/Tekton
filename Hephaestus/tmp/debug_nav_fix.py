#!/usr/bin/env python3
"""
Debug the navigation fix in more detail
"""
import httpx
import asyncio

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def debug_nav():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=== Debugging Navigation Fix ===\n")
        
        # Navigate to Rhetor
        print("1. Navigating to Rhetor...")
        nav_resp = await client.post(MCP_URL, json={
            "tool_name": "ui_navigate",
            "arguments": {"component": "rhetor", "wait_for_load": True}
        })
        
        nav_result = nav_resp.json()['result']
        print(f"   Navigation completed: {nav_result.get('navigation_completed')}")
        
        # Give it more time
        await asyncio.sleep(3)
        
        # Try different capture approaches
        print("\n2. Testing different capture methods...")
        
        # Method 1: Capture with area
        print("\n   a) Capture with area='rhetor':")
        resp1 = await client.post(MCP_URL, json={
            "tool_name": "ui_capture",
            "arguments": {"area": "rhetor"}
        })
        result1 = resp1.json()['result']
        print(f"      HTML length: {result1.get('html_length', 0)}")
        print(f"      Found with: {result1.get('found_with_selector', 'Not specified')}")
        
        # Method 2: Capture whole UI
        print("\n   b) Capture whole UI:")
        resp2 = await client.post(MCP_URL, json={
            "tool_name": "ui_capture",
            "arguments": {}
        })
        result2 = resp2.json()['result']
        print(f"      Loaded component: {result2.get('loaded_component')}")
        html = result2.get('html', '')
        
        # Check if rhetor content exists
        rhetor_indicators = [
            'rhetor__panel',
            'rhetor__content',
            'rhetor__header',
            'data-tekton-area="rhetor"',
            'Rhetor - LLM'
        ]
        
        print("\n   c) Checking for Rhetor indicators in HTML:")
        for indicator in rhetor_indicators:
            if indicator in html:
                print(f"      ✓ Found: {indicator}")
            else:
                print(f"      ✗ Missing: {indicator}")
                
        # Method 3: Check specific selector
        print("\n   d) Checking specific Rhetor selectors:")
        selectors_to_check = [
            '.rhetor',
            '[data-tekton-area="rhetor"]',
            '[data-tekton-component="rhetor"]',
            '#rhetor-component',
            '.rhetor__panel'
        ]
        
        selectors = result2.get('selectors_available', {})
        for sel in selectors_to_check:
            count = selectors.get(sel, 0)
            if count > 0:
                print(f"      ✓ {sel}: {count}")
            else:
                print(f"      ✗ {sel}: 0")

asyncio.run(debug_nav())