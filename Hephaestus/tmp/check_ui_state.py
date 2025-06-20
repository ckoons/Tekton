#!/usr/bin/env python3
"""
Check what's actually in the UI
"""
import httpx
import asyncio

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def check_ui():
    async with httpx.AsyncClient(timeout=20.0) as client:
        print("=== Checking UI State ===\n")
        
        # Capture the whole UI without area
        print("1. Capturing full UI...")
        capture_resp = await client.post(MCP_URL, json={
            "tool_name": "ui_capture",
            "arguments": {}
        })
        
        result = capture_resp.json()
        if result['status'] == 'success':
            data = result['result']
            print(f"   Loaded component: {data.get('loaded_component', 'Unknown')}")
            print(f"   Working with: {data.get('working_with', 'Unknown')}")
            print(f"   HTML length: {data.get('html_length', 0)}")
            
            # Check what selectors are available
            selectors = data.get('selectors_available', {})
            print("\n   Available selectors with content:")
            for sel, count in selectors.items():
                if count > 0:
                    print(f"     {sel}: {count}")
                    
            # Look for component content
            html = data.get('html', '')
            print(f"\n   HTML preview (first 500 chars):")
            print(f"   {html[:500]}...")
            
            # Check if profile content is in the terminal
            if 'profile' in html.lower() and 'terminal' in html.lower():
                print("\n   ⚠️  Profile might be rendering in terminal panel instead of HTML panel")
                
        # Try to see what's in the panels
        print("\n2. Checking panel contents...")
        panel_resp = await client.post(MCP_URL, json={
            "tool_name": "ui_sandbox",
            "arguments": {
                "area": "hephaestus",
                "changes": [{
                    "type": "script",
                    "content": """
                    const result = {};
                    
                    // Check terminal panel
                    const terminalPanel = document.getElementById('terminal-panel');
                    if (terminalPanel) {
                        result.terminalVisible = terminalPanel.style.display !== 'none';
                        result.terminalContent = terminalPanel.textContent.substring(0, 200);
                    }
                    
                    // Check HTML panel
                    const htmlPanel = document.getElementById('html-panel');
                    if (htmlPanel) {
                        result.htmlVisible = htmlPanel.style.display !== 'none';
                        result.htmlContent = htmlPanel.innerHTML.substring(0, 200);
                        result.htmlEmpty = htmlPanel.innerHTML.trim().length === 0;
                    }
                    
                    return result;
                    """
                }],
                "preview": False
            }
        })
        
        if panel_resp.status_code == 200:
            panel_result = panel_resp.json()
            if panel_result['status'] == 'success':
                panels = panel_result['result'].get('changes_applied', [{}])[0]
                print(f"\n   Panel states:")
                print(f"     Terminal visible: {panels.get('terminalVisible', 'Unknown')}")
                print(f"     HTML visible: {panels.get('htmlVisible', 'Unknown')}")
                print(f"     HTML empty: {panels.get('htmlEmpty', 'Unknown')}")
                
                if panels.get('htmlEmpty'):
                    print("\n   ⚠️  HTML panel is empty - components not loading properly")

asyncio.run(check_ui())