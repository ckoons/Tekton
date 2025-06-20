#!/usr/bin/env python3
"""
Force Rhetor to load by directly calling the loader
"""
import httpx
import asyncio

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def force_rhetor_load():
    async with httpx.AsyncClient(timeout=20.0) as client:
        print("=== Forcing Rhetor Load ===\n")
        
        # First, navigate away to reset
        print("1. Resetting to profile...")
        await client.post(MCP_URL, json={
            "tool_name": "ui_navigate",
            "arguments": {"component": "profile"}
        })
        await asyncio.sleep(1)
        
        # Now use sandbox to directly call the loader
        print("\n2. Directly calling minimalLoader for Rhetor...")
        load_response = await client.post(MCP_URL, json={
            "tool_name": "ui_sandbox",
            "arguments": {
                "changes": [{
                    "type": "script",
                    "content": """
                    // Direct load approach
                    if (window.minimalLoader) {
                        console.log('[FORCE] Calling minimalLoader.loadComponent("rhetor")');
                        window.minimalLoader.loadComponent('rhetor');
                        
                        // Also ensure panel visibility
                        const htmlPanel = document.getElementById('html-panel');
                        const terminalPanel = document.getElementById('terminal-panel');
                        if (htmlPanel) {
                            htmlPanel.style.display = 'block';
                            htmlPanel.classList.add('active');
                        }
                        if (terminalPanel) {
                            terminalPanel.style.display = 'none';
                            terminalPanel.classList.remove('active');
                        }
                        
                        // Update nav state
                        document.querySelectorAll('.nav-item').forEach(item => {
                            if (item.getAttribute('data-component') === 'rhetor') {
                                item.classList.add('active');
                            } else {
                                item.classList.remove('active');
                            }
                        });
                        
                        return 'Forced Rhetor load and panel switch';
                    } else if (window.uiManager) {
                        console.log('[FORCE] Calling uiManager.activateComponent("rhetor")');
                        window.uiManager.activateComponent('rhetor');
                        return 'Called uiManager.activateComponent';
                    } else {
                        return 'No loader available';
                    }
                    """
                }],
                "preview": False
            }
        })
        
        load_data = load_response.json()
        if load_data.get('status') == 'success':
            print(f"   Result: {load_data['result'].get('changes_applied', ['Unknown'])[0]}")
        else:
            print(f"   Failed: {load_data.get('error', 'Unknown error')}")
        
        # Wait for load
        await asyncio.sleep(3)
        
        # Check if it worked
        print("\n3. Checking if Rhetor loaded...")
        capture_response = await client.post(MCP_URL, json={
            "tool_name": "ui_capture",
            "arguments": {"area": "rhetor"}
        })
        
        if capture_response['status'] == 'success':
            result = capture_response['result']
            html_length = result.get('html_length', 0)
            
            if html_length > 1000:  # Rhetor is a large component
                print(f"   ✅ SUCCESS! Rhetor loaded (HTML: {html_length} chars)")
                
                # Check semantic tags
                selectors = result.get('selectors_available', {})
                semantic_count = sum(1 for k, v in selectors.items() if 'data-tekton' in k and v > 0)
                print(f"   ✅ Found {semantic_count} types of semantic tags")
                
                # Show the tags
                print("\n   Semantic tags present:")
                for sel, count in selectors.items():
                    if 'data-tekton' in sel and count > 0:
                        print(f"     {sel}: {count}")
            else:
                print(f"   ❌ Rhetor not loaded (HTML too short: {html_length} chars)")
                print(f"   Preview: {result.get('html', '')[:200]}...")
        else:
            print(f"   ❌ Capture failed: {capture_response.get('error', 'Unknown')}")

asyncio.run(force_rhetor_load())