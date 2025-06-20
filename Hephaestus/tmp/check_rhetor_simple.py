#!/usr/bin/env python3
import httpx
import asyncio
import json

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def devtools_request(tool_name, arguments):
    async with httpx.AsyncClient(timeout=10.0) as client:  # 10 second timeout
        response = await client.post(MCP_URL, json={
            "tool_name": tool_name,
            "arguments": arguments
        })
        return response.json()

async def check_rhetor():
    print("=== Checking Rhetor Navigation Issue ===\n")
    
    # Navigate to Rhetor
    print("1. Navigating to Rhetor...")
    nav_result = await devtools_request("ui_navigate", {"component": "rhetor"})
    print(f"   Navigation completed: {nav_result['result'].get('navigation_completed')}")
    
    # Check what's loaded
    print("\n2. Checking loaded component...")
    capture_result = await devtools_request("ui_capture", {})
    loaded = capture_result['result'].get('loaded_component', 'Unknown')
    print(f"   Currently loaded: {loaded}")
    
    if loaded != 'rhetor':
        print(f"\n❌ Issue confirmed: Rhetor navigation succeeded but {loaded} is still loaded")
        print("   This is the panel switching issue mentioned in the handoff")
        
        # Let's check if rhetor content exists in the DOM
        html = capture_result['result'].get('html', '')
        if 'rhetor__panel' in html:
            print("   ✓ Rhetor content IS in the DOM")
        else:
            print("   ✗ Rhetor content NOT in the DOM")
            
        # Check panel visibility
        print("\n3. Checking panel states...")
        selectors = capture_result['result'].get('selectors_available', {})
        print(f"   HTML panel elements: {selectors.get('#html-panel', 0)}")
        print(f"   Terminal panel elements: {selectors.get('#terminal-panel', 0)}")
    else:
        print("\n✓ Rhetor loaded successfully!")
        
        # Check semantic tags
        print("\n3. Checking semantic tags...")
        rhetor_capture = await devtools_request("ui_capture", {"area": "rhetor"})
        selectors = rhetor_capture['result'].get('selectors_available', {})
        
        semantic_count = 0
        for selector, count in selectors.items():
            if 'data-tekton' in selector and count > 0:
                semantic_count += count
                print(f"   {selector}: {count}")
        
        print(f"\n   Total semantic tags: {semantic_count}")

# Run the check
asyncio.run(check_rhetor())