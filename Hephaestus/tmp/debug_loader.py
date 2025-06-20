#!/usr/bin/env python3
"""
Debug why Rhetor isn't loading
"""
import httpx
import asyncio

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def mcp_request(tool_name, arguments, timeout=10.0):
    """Make MCP request with specified timeout"""
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(MCP_URL, json={
            "tool_name": tool_name,
            "arguments": arguments
        })
        return response.json()

async def debug_loader():
    print("=== Debugging Rhetor Loading Issue ===\n")
    
    # Check if minimalLoader exists and what components it knows about
    print("1. Checking minimalLoader...")
    loader_check = await mcp_request("ui_sandbox", {
        "changes": [{
            "type": "script",
            "content": """
            if (window.minimalLoader) {
                return {
                    exists: true,
                    componentPaths: window.minimalLoader.componentPaths,
                    currentComponent: window.minimalLoader.currentComponent
                };
            } else {
                return { exists: false, error: 'minimalLoader not found' };
            }
            """
        }],
        "preview": False
    })
    
    if loader_check['status'] == 'success':
        result = loader_check['result'].get('changes_applied', [{}])[0]
        print(f"   MinimalLoader: {result}")
        
    # Try to manually trigger Rhetor loading
    print("\n2. Attempting manual Rhetor load...")
    manual_load = await mcp_request("ui_sandbox", {
        "changes": [{
            "type": "script", 
            "content": """
            try {
                if (window.minimalLoader && window.minimalLoader.loadComponent) {
                    console.log('[DEBUG] Manually calling minimalLoader.loadComponent("rhetor")');
                    window.minimalLoader.loadComponent('rhetor');
                    return 'Called loadComponent for rhetor';
                } else if (window.uiManager && window.uiManager.loadComponentUI) {
                    console.log('[DEBUG] Manually calling uiManager.loadComponentUI("rhetor")');
                    window.uiManager.loadComponentUI('rhetor');
                    return 'Called loadComponentUI for rhetor';
                } else {
                    return 'No suitable loader method found';
                }
            } catch (error) {
                return 'Error: ' + error.message;
            }
            """
        }],
        "preview": False
    })
    
    if manual_load['status'] == 'success':
        print(f"   Manual load result: {manual_load['result'].get('changes_applied', ['Unknown'])[0]}")
        
    # Wait for load
    await asyncio.sleep(3)
    
    # Check if Rhetor loaded
    print("\n3. Checking if Rhetor loaded...")
    capture = await mcp_request("ui_capture", {})
    loaded = capture['result'].get('loaded_component', 'Unknown')
    print(f"   Loaded component: {loaded}")
    
    if loaded == 'rhetor':
        print("   ✅ Manual load succeeded!")
    else:
        # Check HTML panel content
        print("\n4. Checking HTML panel content...")
        panel_check = await mcp_request("ui_sandbox", {
            "changes": [{
                "type": "script",
                "content": """
                const htmlPanel = document.getElementById('html-panel');
                if (htmlPanel) {
                    const content = htmlPanel.innerHTML.substring(0, 200);
                    const hasRhetor = content.includes('rhetor');
                    return {
                        exists: true,
                        display: htmlPanel.style.display,
                        hasRhetorContent: hasRhetor,
                        preview: content + '...'
                    };
                } else {
                    return { exists: false };
                }
                """
            }],
            "preview": False
        })
        
        if panel_check['status'] == 'success':
            print(f"   HTML panel: {panel_check['result'].get('changes_applied', ['Unknown'])[0]}")

# Run debug
asyncio.run(debug_loader())