#!/usr/bin/env python3
"""
Test script to verify and fix the Rhetor navigation issue.
Uses simpler operations to avoid timeouts.
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

async def test_and_fix_navigation():
    print("=== Testing Rhetor Navigation Fix ===\n")
    
    # Step 1: Navigate to Rhetor
    print("1. Navigating to Rhetor component...")
    nav_result = await mcp_request("ui_navigate", {"component": "rhetor"})
    print(f"   Navigation reported: {nav_result['result'].get('navigation_completed')}")
    
    # Small wait for any async operations
    await asyncio.sleep(1)
    
    # Step 2: Check what's actually loaded
    print("\n2. Checking what component is loaded...")
    capture = await mcp_request("ui_capture", {})
    loaded = capture['result'].get('loaded_component', 'Unknown')
    print(f"   Loaded component: {loaded}")
    
    if loaded != 'rhetor':
        print(f"\n❌ Navigation issue confirmed: {loaded} is still loaded instead of rhetor")
        
        # Step 3: Try to force panel switch using sandbox
        print("\n3. Attempting to force HTML panel visible...")
        
        # First, let's check if we can find the panel switching code
        sandbox_result = await mcp_request("ui_sandbox", {
            "changes": [{
                "type": "script",
                "content": """
                // Force HTML panel visible
                const htmlPanel = document.getElementById('html-panel');
                const terminalPanel = document.getElementById('terminal-panel');
                
                if (htmlPanel && terminalPanel) {
                    htmlPanel.style.display = 'block';
                    terminalPanel.style.display = 'none';
                    console.log('Forced HTML panel visible');
                    
                    // Now try to load Rhetor
                    if (window.minimalLoader) {
                        window.minimalLoader.loadComponent('rhetor');
                        return 'Attempted to load Rhetor with minimalLoader';
                    } else if (window.uiManager) {
                        window.uiManager.loadComponentUI('rhetor');
                        return 'Attempted to load Rhetor with uiManager';
                    } else {
                        return 'No loader found';
                    }
                } else {
                    return 'Panels not found';
                }
                """
            }],
            "preview": False  # Actually execute it
        }, timeout=30.0)
        
        print(f"   Sandbox result: {sandbox_result['result'].get('description', 'No description')}")
        
        # Wait for component to load
        await asyncio.sleep(2)
        
        # Step 4: Check again
        print("\n4. Checking if Rhetor loaded after fix...")
        capture2 = await mcp_request("ui_capture", {"area": "rhetor"})
        
        if capture2['status'] == 'success':
            html_length = capture2['result'].get('html_length', 0)
            if html_length > 1000:  # Rhetor component is quite large
                print(f"   ✓ Rhetor appears to be loaded! (HTML length: {html_length})")
                
                # Check for semantic tags
                selectors = capture2['result'].get('selectors_available', {})
                semantic_count = sum(1 for k, v in selectors.items() if 'data-tekton' in k and v > 0)
                print(f"   ✓ Found {semantic_count} types of semantic tags")
                
                # Show some of the semantic tags
                print("\n   Semantic tags found:")
                for selector, count in selectors.items():
                    if 'data-tekton' in selector and count > 0:
                        print(f"     {selector}: {count}")
            else:
                print(f"   ✗ Rhetor not fully loaded (HTML length: {html_length})")
        else:
            print(f"   ✗ Failed to capture Rhetor: {capture2.get('error', 'Unknown error')}")
    else:
        print("\n✓ Rhetor loaded successfully on first try!")
        
        # Analyze semantic tags
        print("\n5. Analyzing Rhetor semantic tags...")
        analysis = await mcp_request("ui_semantic_analysis", {"component": "rhetor"}, timeout=20.0)
        
        if analysis['status'] == 'success':
            result = analysis['result']
            print(f"   Semantic score: {result.get('score', 0)}/100")
            print(f"   Total tags: {result.get('total_tags', 0)}")
            
            coverage = result.get('coverage', {})
            if coverage:
                print("\n   Coverage by category:")
                for category, info in coverage.items():
                    print(f"     {category}: {info.get('found', 0)}/{info.get('expected', 0)}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_and_fix_navigation())