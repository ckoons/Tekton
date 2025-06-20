#!/usr/bin/env python3
"""
Test if the navigation fix works for Rhetor
"""
import httpx
import asyncio

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def test_nav_fix():
    async with httpx.AsyncClient(timeout=20.0) as client:
        print("=== Testing Navigation Fix for Rhetor ===\n")
        
        # Reset to profile first
        print("1. Resetting to profile...")
        await client.post(MCP_URL, json={
            "tool_name": "ui_navigate",
            "arguments": {"component": "profile"}
        })
        await asyncio.sleep(2)
        
        # Navigate to Rhetor with the fixed navigation
        print("\n2. Navigating to Rhetor with fixed navigation tools...")
        nav_resp = await client.post(MCP_URL, json={
            "tool_name": "ui_navigate",
            "arguments": {"component": "rhetor", "wait_for_load": True}
        })
        
        nav_result = nav_resp.json()
        print(f"   Status: {nav_result['status']}")
        if nav_result['status'] == 'success':
            result = nav_result['result']
            print(f"   Navigation completed: {result.get('navigation_completed')}")
            if 'component_info' in result:
                info = result['component_info']
                print(f"   Component verified: {info.get('verified')}")
                print(f"   Component visible: {info.get('isVisible')}")
        
        # Wait a bit more for component to fully load
        await asyncio.sleep(2)
        
        # Capture Rhetor content
        print("\n3. Capturing Rhetor component...")
        capture_resp = await client.post(MCP_URL, json={
            "tool_name": "ui_capture",
            "arguments": {"area": "rhetor"}
        })
        
        capture_result = capture_resp.json()
        if capture_result['status'] == 'success':
            result = capture_result['result']
            html_length = result.get('html_length', 0)
            
            if html_length > 1000:
                print(f"   ✅ SUCCESS! Rhetor loaded properly!")
                print(f"   HTML length: {html_length} characters")
                
                # Check semantic tags
                selectors = result.get('selectors_available', {})
                semantic_tags = {k: v for k, v in selectors.items() if 'data-tekton' in k and v > 0}
                
                print(f"\n   Found {len(semantic_tags)} types of semantic tags:")
                for tag, count in semantic_tags.items():
                    print(f"     {tag}: {count}")
                    
                # Check coverage
                expected_tags = [
                    '[data-tekton-area]',
                    '[data-tekton-zone]',
                    '[data-tekton-component]',
                    '[data-tekton-type]'
                ]
                
                missing = [tag for tag in expected_tags if tag not in semantic_tags]
                if missing:
                    print(f"\n   Missing tags: {', '.join(missing)}")
                else:
                    print("\n   ✅ All expected tag types present!")
                    
            else:
                print(f"   ❌ Rhetor not fully loaded (only {html_length} chars)")
                print(f"   Selector tried: {result.get('found_with_selector', 'Unknown')}")
        else:
            print(f"   ❌ Capture failed: {capture_result.get('error', 'Unknown')}")

asyncio.run(test_nav_fix())