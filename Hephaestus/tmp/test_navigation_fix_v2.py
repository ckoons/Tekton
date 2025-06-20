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

async def test_navigation_issue():
    print("=== Examining Rhetor Navigation Issue ===\n")
    
    # Step 1: Check initial state
    print("1. Checking initial state...")
    initial = await mcp_request("ui_capture", {})
    print(f"   Currently loaded: {initial['result'].get('loaded_component', 'Unknown')}")
    
    # Step 2: Navigate to Rhetor
    print("\n2. Navigating to Rhetor...")
    nav_result = await mcp_request("ui_navigate", {"component": "rhetor"})
    print(f"   Navigation completed: {nav_result['result'].get('navigation_completed')}")
    
    await asyncio.sleep(1)
    
    # Step 3: Check what's loaded now
    print("\n3. Checking loaded component after navigation...")
    after_nav = await mcp_request("ui_capture", {})
    loaded = after_nav['result'].get('loaded_component', 'Unknown')
    print(f"   Loaded component: {loaded}")
    
    if loaded != 'rhetor':
        print(f"\n❌ ISSUE CONFIRMED: Navigation succeeded but {loaded} is still displayed")
        print("   This confirms the panel switching issue from the handoff document")
        
        # Step 4: Look for the navigation implementation
        print("\n4. Analyzing navigation mechanism...")
        
        # Check if minimalLoader exists
        check_loader = await mcp_request("ui_sandbox", {
            "changes": [{
                "type": "script", 
                "content": "return typeof window.minimalLoader !== 'undefined' ? 'minimalLoader exists' : 'minimalLoader NOT found';"
            }],
            "preview": False
        })
        
        if check_loader['status'] == 'success':
            print(f"   Loader check: {check_loader['result'].get('changes_applied', ['Unknown'])[0]}")
        
        # Check panel states
        check_panels = await mcp_request("ui_sandbox", {
            "changes": [{
                "type": "script",
                "content": """
                const htmlPanel = document.getElementById('html-panel');
                const terminalPanel = document.getElementById('terminal-panel');
                return {
                    htmlPanelExists: !!htmlPanel,
                    htmlPanelDisplay: htmlPanel ? htmlPanel.style.display : 'not found',
                    terminalPanelExists: !!terminalPanel,
                    terminalPanelDisplay: terminalPanel ? terminalPanel.style.display : 'not found'
                };
                """
            }],
            "preview": False
        })
        
        if check_panels['status'] == 'success':
            print(f"   Panel states: {check_panels['result'].get('changes_applied', ['Unknown'])[0]}")
            
        print("\n5. Proposed fix for rhetor-component.html:")
        print("   Add this to the component initialization script:")
        print("""
   // Force HTML panel visible when Rhetor loads
   window.addEventListener('DOMContentLoaded', function() {
       const htmlPanel = document.getElementById('html-panel');
       const terminalPanel = document.getElementById('terminal-panel');
       
       if (htmlPanel && terminalPanel) {
           htmlPanel.style.display = 'block';
           terminalPanel.style.display = 'none';
           console.log('[RHETOR] Forced HTML panel visible on load');
       }
   });
        """)
        
    else:
        print("\n✓ Rhetor loaded successfully!")
        
        # Analyze semantic coverage
        print("\n4. Checking Rhetor semantic tag coverage...")
        capture = await mcp_request("ui_capture", {"area": "rhetor"})
        
        if capture['status'] == 'success':
            selectors = capture['result'].get('selectors_available', {})
            
            # Count semantic tags
            semantic_tags = {k: v for k, v in selectors.items() if 'data-tekton' in k and v > 0}
            
            print(f"\n   Found {len(semantic_tags)} types of semantic tags:")
            for tag, count in semantic_tags.items():
                print(f"     {tag}: {count}")
                
            # Check for missing important tags
            expected_tags = [
                '[data-tekton-area]',
                '[data-tekton-zone]', 
                '[data-tekton-action]',
                '[data-tekton-state]',
                '[data-tekton-element]'
            ]
            
            missing = [tag for tag in expected_tags if tag not in semantic_tags]
            if missing:
                print(f"\n   ⚠️  Missing expected tags: {', '.join(missing)}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_navigation_issue())