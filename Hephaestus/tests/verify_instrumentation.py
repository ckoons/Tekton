#!/usr/bin/env python3
"""
Verify UI instrumentation is working with DevTools
"""
import httpx
import json
import time

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

def test_devtools():
    """Test if DevTools can see semantic tags"""
    print("🔍 Testing UI Instrumentation with DevTools\n")
    
    # Test components
    components = ['rhetor', 'profile', 'settings', 'athena']
    
    for comp in components:
        print(f"Testing {comp}...")
        
        # Navigate to component
        nav_response = httpx.post(MCP_URL, json={
            "tool_name": "ui_navigate",
            "arguments": {"component": comp}
        })
        
        if nav_response.status_code != 200:
            print(f"  ❌ Failed to navigate: {nav_response.text}")
            continue
            
        # Wait for component to load
        time.sleep(2)
        
        # Try to evaluate semantic tags
        eval_response = httpx.post(MCP_URL, json={
            "tool_name": "ui_interact",
            "arguments": {
                "area": comp,
                "action": "evaluate", 
                "value": """
                    const container = document.querySelector('#html-panel');
                    const semanticTags = container ? container.querySelectorAll('[data-tekton-area], [data-tekton-component], [data-tekton-zone]') : [];
                    {
                        found: semanticTags.length,
                        tags: Array.from(semanticTags).slice(0, 5).map(el => ({
                            tag: el.tagName,
                            area: el.getAttribute('data-tekton-area'),
                            component: el.getAttribute('data-tekton-component'),
                            zone: el.getAttribute('data-tekton-zone')
                        }))
                    }
                """
            }
        })
        
        if eval_response.status_code == 200:
            result = eval_response.json()
            if result['status'] == 'success' and result['result']:
                data = result['result']
                print(f"  ✅ Found {data.get('found', 0)} semantic tags")
                if 'tags' in data:
                    for tag in data['tags']:
                        print(f"     - {tag['tag']}: area={tag['area']}, zone={tag['zone']}")
            else:
                print(f"  ⚠️  No semantic tags found or error: {result.get('error', 'Unknown')}")
        else:
            print(f"  ❌ Failed to evaluate: {eval_response.text}")
        
        print()

if __name__ == "__main__":
    test_devtools()