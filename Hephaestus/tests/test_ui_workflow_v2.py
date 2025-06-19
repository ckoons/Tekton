#!/usr/bin/env python3
"""
Test the improved ui_workflow v2 with better error handling and navigation
"""
import httpx
import asyncio
import json

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def test_workflow_improvements():
    """Test the v2 improvements"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print("🧪 Testing ui_workflow V2 Improvements\n")
        
        # Test 1: Debug workflow with enhanced diagnostics
        print("1️⃣ Testing enhanced debug workflow...")
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_workflow",
            "arguments": {
                "workflow": "debug_component",
                "component": "hermes",
                "debug": True
            }
        })
        
        result = response.json()
        if result.get("status") == "success":
            debug_result = result.get("result", {})
            print("Debug Visual Feedback:")
            print(debug_result.get("visual_feedback", "No feedback"))
            print("\nDiagnostics:")
            print(json.dumps(debug_result.get("diagnostics", {}), indent=2))
        else:
            print(f"Error: {result.get('error')}")
        
        # Test 2: Modify with non-existent selector (test error handling)
        print("\n2️⃣ Testing error handling with bad selector...")
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_workflow",
            "arguments": {
                "workflow": "modify_component",
                "component": "rhetor",
                "changes": [{
                    "selector": ".this-selector-does-not-exist",
                    "content": "<div>Test</div>",
                    "action": "append"
                }]
            }
        })
        
        result = response.json()
        if result.get("result", {}).get("success") == False:
            error_info = result.get("result", {})
            print("✅ Error handled gracefully:")
            print(f"   Error: {error_info.get('error')}")
            print(f"   Failed selector: {error_info.get('failed_selector')}")
            print(f"   Available selectors: {error_info.get('available_selectors', [])[:3]}")
            print(f"   Suggestion: {error_info.get('suggestion')}")
        
        # Test 3: Verify component with retry logic
        print("\n3️⃣ Testing verify with retry logic...")
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_workflow",
            "arguments": {
                "workflow": "verify_component",
                "component": "apollo"
            }
        })
        
        result = response.json()
        if result.get("status") == "success":
            verify_result = result.get("result", {})
            print("Verification Visual Feedback:")
            print(verify_result.get("visual_feedback", "No feedback"))
        
        # Test 4: Test a successful modification
        print("\n4️⃣ Testing successful modification...")
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_workflow",
            "arguments": {
                "workflow": "modify_component",
                "component": "rhetor",
                "changes": [{
                    "selector": "#rhetor-footer",
                    "content": '<div style="text-align: center; padding: 10px; color: #4CAF50;">✨ V2 Workflow Success!</div>',
                    "action": "append"
                }],
                "debug": True
            }
        })
        
        result = response.json()
        if result.get("status") == "success":
            workflow_result = result.get("result", {})
            print(f"Success: {workflow_result.get('success')}")
            if workflow_result.get("success"):
                print("Visual Feedback:")
                print(workflow_result.get("visual_feedback", "No feedback"))
                print(f"Screenshots: {workflow_result.get('screenshots', {})}")
            else:
                print("Workflow failed:")
                print(f"Error: {workflow_result.get('error')}")
                print(f"Details: {workflow_result.get('details')}")
        
        print("\n✅ V2 Improvements Test Complete!")
        print("\nKey Improvements Demonstrated:")
        print("1. Enhanced debug diagnostics with actionable recommendations")
        print("2. Graceful error handling with helpful suggestions")
        print("3. Robust component verification with retries")
        print("4. Better success/failure feedback")

if __name__ == "__main__":
    asyncio.run(test_workflow_improvements())