#!/usr/bin/env python3
"""
Simple test to check component state
"""
import httpx
import asyncio

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def simple_test():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Just navigate and capture
        print("Navigating to rhetor...")
        nav_response = await client.post(MCP_URL, json={
            "tool_name": "ui_navigate",
            "arguments": {"component": "rhetor"}
        })
        print(f"Navigation: {nav_response.json()['status']}")
        
        await asyncio.sleep(2)
        
        print("\nCapturing current state...")
        capture_response = await client.post(MCP_URL, json={
            "tool_name": "ui_capture",
            "arguments": {}
        })
        
        result = capture_response.json()['result']
        print(f"Loaded component: {result.get('loaded_component')}")
        print(f"Working with: {result.get('working_with')}")
        
        # Try semantic scan
        print("\nRunning semantic scan...")
        scan_response = await client.post(MCP_URL, json={
            "tool_name": "ui_semantic_scan",
            "arguments": {}
        })
        
        if scan_response.json()['status'] == 'success':
            scores = scan_response.json()['result'].get('component_scores', {})
            if 'rhetor' in scores:
                print(f"Rhetor score: {scores['rhetor']}")
            else:
                print("Rhetor not found in scan")

asyncio.run(simple_test())