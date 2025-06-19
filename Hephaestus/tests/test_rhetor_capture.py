#!/usr/bin/env python3
"""
Simple test of UI DevTools capture for Rhetor
"""

import httpx
import asyncio
import json

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def test_rhetor_capture():
    """Test capturing Rhetor's UI structure"""
    async with httpx.AsyncClient() as client:
        # Check health first
        health = await client.get("http://localhost:8088/health")
        if health.status_code != 200:
            print("❌ MCP server not running. Start with: cd Hephaestus && ./run_mcp.sh")
            return
        
        print("✅ MCP server is running")
        
        # Capture Rhetor UI
        request = {
            "tool_name": "ui_capture",
            "arguments": {
                "area": "rhetor"
            }
        }
        
        print("\n📸 Capturing Rhetor UI structure...")
        response = await client.post(MCP_URL, json=request, timeout=30.0)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                result = data['result']
                print(f"✅ Successfully captured {result['area']} UI")
                print(f"   - UI URL: {result['ui_url']}")
                print(f"   - Current URL: {result['current_url']}")
                print(f"   - Loaded Component: {result['loaded_component']}")
                print(f"   - Working With: {result['working_with']}")
                
                # Show structure info
                if 'structure' in result:
                    structure = result['structure']
                    print(f"\n📊 Structure:")
                    print(f"   - Elements: {structure.get('element_count', 'N/A')}")
                    
                    # Show HTML content if present
                    if 'html_content' in structure:
                        html_content = structure['html_content']
                        print(f"   - HTML Length: {len(html_content)} characters")
                        
                        # Save HTML for inspection
                        with open('rhetor_capture.html', 'w') as f:
                            f.write(html_content)
                        print("\n💾 Saved HTML to rhetor_capture.html")
                        
                        # Check for semantic tags
                        import re
                        semantic_tags = re.findall(r'data-tekton-\w+', html_content)
                        if semantic_tags:
                            print(f"\n🏷️  Found {len(set(semantic_tags))} unique semantic tag types")
                        else:
                            print("\n⚠️  No semantic tags (data-tekton-*) found")
                
            else:
                print(f"❌ Capture failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    asyncio.run(test_rhetor_capture())