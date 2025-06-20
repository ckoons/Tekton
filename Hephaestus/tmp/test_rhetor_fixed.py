#!/usr/bin/env python3
"""
Test if the Rhetor navigation fix works
"""
import httpx
import asyncio
import json

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def mcp_request(tool_name, arguments, timeout=10.0):
    """Make MCP request with specified timeout"""
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(MCP_URL, json={
            "tool_name": tool_name,
            "arguments": arguments
        })
        return response.json()

async def test_rhetor_navigation():
    print("=== Testing Rhetor Navigation After Fix ===\n")
    
    # Step 1: Navigate away from Rhetor first (to reset state)
    print("1. Navigating to profile to reset state...")
    await mcp_request("ui_navigate", {"component": "profile"})
    await asyncio.sleep(1)
    
    # Step 2: Navigate to Rhetor
    print("\n2. Navigating to Rhetor...")
    nav_result = await mcp_request("ui_navigate", {"component": "rhetor"})
    print(f"   Navigation completed: {nav_result['result'].get('navigation_completed')}")
    
    # Wait for component to load and panel switch to happen
    await asyncio.sleep(2)
    
    # Step 3: Check what's loaded
    print("\n3. Checking loaded component...")
    capture = await mcp_request("ui_capture", {})
    loaded = capture['result'].get('loaded_component', 'Unknown')
    print(f"   Loaded component: {loaded}")
    
    if loaded == 'rhetor':
        print("\n✅ SUCCESS! Rhetor loaded correctly!")
        
        # Step 4: Capture Rhetor content
        print("\n4. Capturing Rhetor content...")
        rhetor_capture = await mcp_request("ui_capture", {"area": "rhetor"})
        
        if rhetor_capture['status'] == 'success':
            result = rhetor_capture['result']
            print(f"   HTML length: {result.get('html_length', 0)} characters")
            
            # Check semantic tags
            selectors = result.get('selectors_available', {})
            semantic_tags = {k: v for k, v in selectors.items() if 'data-tekton' in k and v > 0}
            
            print(f"\n   Found {len(semantic_tags)} types of semantic tags:")
            for tag, count in semantic_tags.items():
                print(f"     {tag}: {count}")
                
            # Check for expected zones
            if '[data-tekton-zone]' in selectors:
                print(f"\n   ✓ Zone tags found: {selectors['[data-tekton-zone]']}")
            if '[data-tekton-area]' in selectors:
                print(f"   ✓ Area tags found: {selectors['[data-tekton-area]']}")
            if '[data-tekton-action]' in selectors:
                print(f"   ✓ Action tags found: {selectors['[data-tekton-action]']}")
                
    else:
        print(f"\n❌ ISSUE PERSISTS: {loaded} is still loaded instead of rhetor")
        print("   The navigation fix may need additional adjustments")
        
        # Try to debug what happened
        print("\n5. Checking console logs...")
        logs_result = await mcp_request("ui_sandbox", {
            "changes": [{
                "type": "script",
                "content": """
                // Get recent console logs
                const logs = window._devToolsConsoleLogs || [];
                const rhetorLogs = logs.filter(log => log.includes('[RHETOR]')).slice(-5);
                return rhetorLogs.length > 0 ? rhetorLogs : 'No Rhetor logs found';
                """
            }],
            "preview": False
        })
        
        if logs_result['status'] == 'success':
            print(f"   Recent Rhetor logs: {logs_result['result'].get('changes_applied', ['None'])[0]}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_rhetor_navigation())