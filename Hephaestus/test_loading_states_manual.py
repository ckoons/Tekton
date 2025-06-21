#!/usr/bin/env python3
"""
Manual test for loading states - run this to verify the loading state system works
"""

import asyncio
import httpx
import json
import time

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def test_loading_states():
    """Test the loading state system manually"""
    async with httpx.AsyncClient(timeout=30) as client:
        print("Testing Loading State System")
        print("=" * 50)
        
        # Test navigation to multiple components
        components = ["rhetor", "athena", "metis", "settings", "profile"]
        
        for component in components:
            print(f"\nTesting {component}...")
            
            # Navigate
            response = await client.post(MCP_URL, json={
                "tool_name": "ui_navigate",
                "arguments": {"component": component}
            })
            nav_result = response.json()
            
            if nav_result["status"] == "success":
                result = nav_result["result"]
                print(f"  Navigation: {'✓' if result.get('navigation_completed') else '✗'}")
                
                # Check if loading states were used
                if "loading state: loaded" in result.get("message", ""):
                    print(f"  Loading State Used: ✓")
                    if "load_time_ms" in result:
                        print(f"  Load Time: {result['load_time_ms']}ms")
                elif result.get("loading_state_fallback"):
                    print(f"  Loading State Used: ✗ (fallback used)")
                    if "loading_state_error" in result:
                        print(f"  Fallback reason: {result['loading_state_error']}")
                else:
                    print(f"  Loading State Used: ✗")
                
            else:
                print(f"  Error: {nav_result.get('error', 'Unknown error')}")
            
            # Small delay between tests
            await asyncio.sleep(0.5)
        
        # Now capture to check loading states
        print("\n\nChecking DOM for loading states...")
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_capture",
            "arguments": {"area": "hephaestus"}
        })
        capture_result = response.json()
        
        if capture_result["status"] == "success":
            loading_states = capture_result["result"].get("loading_states", [])
            if loading_states:
                print(f"Found {len(loading_states)} loading state attributes:")
                for state in loading_states:
                    print(f"  - Component: {state.get('component')}, State: {state.get('state')}")
            else:
                print("No loading state attributes found in DOM")
                
            # Check HTML for loading attributes
            html = capture_result["result"].get("html", "")
            if "data-tekton-loading-state" in html:
                print("\nLoading state attributes ARE present in HTML")
                # Extract the actual state
                import re
                matches = re.findall(r'data-tekton-loading-state="([^"]+)"', html)
                if matches:
                    print(f"Found states: {matches}")
            else:
                print("\nNo loading state attributes in HTML")

if __name__ == "__main__":
    asyncio.run(test_loading_states())