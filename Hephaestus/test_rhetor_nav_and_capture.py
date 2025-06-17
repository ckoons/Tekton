#!/usr/bin/env python3
"""
Test navigating to Rhetor and then capturing
"""

import httpx
import asyncio
import json

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def test_rhetor_navigation():
    """Test navigating to Rhetor then capturing"""
    async with httpx.AsyncClient() as client:
        # 1. First navigate to Rhetor
        print("🧭 Navigating to Rhetor...")
        nav_request = {
            "tool_name": "ui_navigate",
            "arguments": {
                "component": "rhetor"
            }
        }
        
        nav_response = await client.post(MCP_URL, json=nav_request, timeout=30.0)
        if nav_response.status_code == 200:
            nav_data = nav_response.json()
            if nav_data['status'] == 'success':
                print("✅ Successfully navigated to Rhetor")
                print(f"   - Navigation method: {nav_data['result'].get('navigation_method', 'N/A')}")
            else:
                print(f"❌ Navigation failed: {nav_data.get('error', 'Unknown error')}")
                return
        
        # 2. Wait a moment for content to load
        print("\n⏳ Waiting for content to load...")
        await asyncio.sleep(2)
        
        # 3. Now capture Rhetor
        print("\n📸 Capturing Rhetor UI structure...")
        capture_request = {
            "tool_name": "ui_capture",
            "arguments": {
                "area": "rhetor"
            }
        }
        
        capture_response = await client.post(MCP_URL, json=capture_request, timeout=30.0)
        if capture_response.status_code == 200:
            data = capture_response.json()
            if data['status'] == 'success':
                result = data['result']
                print(f"✅ Successfully captured {result['area']} UI")
                print(f"   - Loaded Component: {result['loaded_component']}")
                print(f"   - Working With: {result['working_with']}")
                
                # Check structure
                if 'structure' in result:
                    structure = result['structure']
                    print(f"\n📊 Structure:")
                    print(f"   - Structure keys: {list(structure.keys())}")
                    print(f"   - Elements: {structure.get('element_count', 'N/A')}")
                    
                    # Show what was found
                    if 'html_content' in structure:
                        html = structure['html_content']
                        
                        # Look for Rhetor-specific elements
                        rhetor_found = 'rhetor' in html.lower()
                        has_rhetor_class = 'class="rhetor"' in html or "class='rhetor'" in html
                        
                        print(f"\n🔍 Content Analysis:")
                        print(f"   - Contains 'rhetor' text: {rhetor_found}")
                        print(f"   - Has rhetor class: {has_rhetor_class}")
                        print(f"   - HTML length: {len(html)} characters")
                        
                        # Save full HTML for inspection
                        with open('rhetor_nav_capture.html', 'w') as f:
                            f.write(html)
                        print(f"   - Saved full HTML to rhetor_nav_capture.html")
                        
                        # Look for the actual loaded content
                        if '<div id="html-panel"' in html:
                            print(f"   - Found html-panel div")
                            # Extract just the html-panel content
                            import re
                            panel_match = re.search(r'<div[^>]*id="html-panel"[^>]*>(.*?)</div>', html, re.DOTALL)
                            if panel_match:
                                panel_content = panel_match.group(1).strip()
                                if panel_content:
                                    print(f"   - HTML panel content: {panel_content[:100]}...")
                                else:
                                    print(f"   - HTML panel is empty!")

if __name__ == "__main__":
    asyncio.run(test_rhetor_navigation())