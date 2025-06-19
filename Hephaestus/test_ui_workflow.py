#!/usr/bin/env python3
"""Test ui_workflow after fixes"""

import httpx
import asyncio
import json
from datetime import datetime

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def test_ui_workflow():
    print("Testing ui_workflow tool...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Verify component
        print("\n1. Testing verify_component workflow...")
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_workflow",
            "arguments": {
                "workflow": "verify_component",
                "component": "rhetor",
                "debug": True
            }
        })
        result = response.json()
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Test 2: Modify component
        print("\n2. Testing modify_component workflow...")
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_workflow",
            "arguments": {
                "workflow": "modify_component",
                "component": "rhetor",
                "changes": [{
                    "selector": ".rhetor__footer",
                    "content": f'<div class="workflow-test" style="text-align:center; padding:10px; color:#4CAF50;">✅ UI Workflow Test - {datetime.now().strftime("%H:%M:%S")}</div>',
                    "action": "append"
                }],
                "debug": True
            }
        })
        result = response.json()
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Test 3: Debug component
        print("\n3. Testing debug_component workflow...")
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_workflow",
            "arguments": {
                "workflow": "debug_component",
                "component": "hermes",
                "debug": True
            }
        })
        result = response.json()
        print(f"Result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_ui_workflow())