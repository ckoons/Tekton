#!/usr/bin/env python3
"""
Test the newly implemented ui_workflow tool
"""
import httpx
import asyncio
import json

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def test_ui_workflow():
    """Test the new ui_workflow implementation"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print("🧪 Testing ui_workflow implementation\n")
        
        # Test 1: Modify component workflow
        print("1️⃣ Testing modify_component workflow...")
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_workflow",
            "arguments": {
                "workflow": "modify_component",
                "component": "rhetor",
                "changes": [{
                    "selector": "#rhetor-footer",
                    "content": '<div style="text-align: center; color: #4CAF50;">✨ Modified by ui_workflow!</div>',
                    "action": "append"
                }],
                "debug": True
            }
        })
        
        result = response.json()
        print(f"Status: {result.get('status')}")
        if result.get('status') == 'success':
            workflow_result = result.get('result', {})
            print(f"Success: {workflow_result.get('success')}")
            print(f"Steps completed: {len(workflow_result.get('steps', []))}")
            print("Visual feedback:")
            print(workflow_result.get('visual_feedback', 'No feedback'))
        else:
            print(f"Error: {result.get('error')}")
        
        # Test 2: Debug component workflow
        print("\n2️⃣ Testing debug_component workflow...")
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_workflow",
            "arguments": {
                "workflow": "debug_component",
                "component": "hermes"
            }
        })
        
        result = response.json()
        if result.get('status') == 'success':
            debug_result = result.get('result', {})
            print("Debug feedback:")
            print(debug_result.get('visual_feedback', 'No feedback'))
        
        # Test 3: Verify with invalid parameters
        print("\n3️⃣ Testing parameter validation...")
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_workflow",
            "arguments": {
                "workflow": "invalid_workflow",
                "component": "rhetor"
            }
        })
        
        result = response.json()
        if result.get('status') == 'error' or not result.get('result', {}).get('success'):
            print("✅ Correctly rejected invalid workflow")
            error_msg = result.get('error') or result.get('result', {}).get('error', '')
            print(f"Error message: {error_msg}")
            suggestion = result.get('result', {}).get('suggestion', '')
            if suggestion:
                print(f"Suggestion: {suggestion}")
        
        print("\n✅ ui_workflow implementation test complete!")

if __name__ == "__main__":
    asyncio.run(test_ui_workflow())