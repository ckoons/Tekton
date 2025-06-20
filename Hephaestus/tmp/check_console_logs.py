#!/usr/bin/env python3
"""
Check browser console for errors
"""
import httpx
import asyncio

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def check_console():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=== Checking Browser Console ===\n")
        
        # Navigate to Rhetor
        print("1. Navigating to Rhetor...")
        await client.post(MCP_URL, json={
            "tool_name": "ui_navigate",
            "arguments": {"component": "rhetor"}
        })
        
        await asyncio.sleep(2)
        
        # Get console logs
        print("\n2. Retrieving console logs...")
        console_resp = await client.post(MCP_URL, json={
            "tool_name": "ui_sandbox",
            "arguments": {
                "area": "hephaestus",  # Add area parameter
                "changes": [{
                    "type": "script",
                    "content": """
                    // Get console logs from the page
                    const logs = [];
                    
                    // Check for DevTools logs
                    const allLogs = window.performance.getEntriesByType('measure')
                        .map(m => m.name)
                        .filter(name => name.includes('DevTools') || name.includes('rhetor'));
                    
                    // Check console directly
                    if (window.console && window.console._log) {
                        logs.push('Console has been intercepted');
                    }
                    
                    // Check for loader
                    if (window.minimalLoader) {
                        logs.push(`minimalLoader exists, current: ${window.minimalLoader.currentComponent}`);
                        logs.push(`rhetor path: ${window.minimalLoader.componentPaths.rhetor || 'not defined'}`);
                    } else {
                        logs.push('minimalLoader NOT found');
                    }
                    
                    // Check for uiManager
                    if (window.uiManager) {
                        logs.push(`uiManager exists, active: ${window.uiManager.activeComponent}`);
                    } else {
                        logs.push('uiManager NOT found');
                    }
                    
                    // Check panels
                    const htmlPanel = document.getElementById('html-panel');
                    const terminalPanel = document.getElementById('terminal-panel');
                    
                    logs.push(`HTML panel: ${htmlPanel ? htmlPanel.style.display : 'not found'}`);
                    logs.push(`Terminal panel: ${terminalPanel ? terminalPanel.style.display : 'not found'}`);
                    
                    return logs;
                    """
                }],
                "preview": False
            }
        })
        
        if console_resp.status_code == 200:
            result = console_resp.json()
            if result['status'] == 'success':
                logs = result['result'].get('changes_applied', [['No logs']])[0]
                print("\n   Console state:")
                if isinstance(logs, list):
                    for log in logs:
                        print(f"     - {log}")
                else:
                    print(f"     {logs}")
            else:
                print(f"   Error: {result.get('error', 'Unknown')}")
        else:
            print(f"   Request failed: {console_resp.status_code}")

asyncio.run(check_console())