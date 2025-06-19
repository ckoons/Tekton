#!/usr/bin/env python3
"""
Test the new ui_workflow tool - Compare this to the pain of the old way!
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
import asyncio
import json

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def devtools(tool_name: str, **kwargs):
    """Call UI DevTools"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            MCP_URL,
            json={"tool_name": tool_name, "arguments": kwargs}
        )
        return response.json()

async def main():
    print("🚀 UI Workflow Test - The Easy Way!\n")
    
    # THE OLD WAY (What we had to do before):
    print("❌ The OLD painful way would require:")
    print("   1. ui_navigate('hermes')")
    print("   2. asyncio.sleep(1) # hope it's enough")  
    print("   3. ui_capture('content') # not 'hermes'!")
    print("   4. ui_screenshot('hermes')")
    print("   5. ui_sandbox('content', changes, preview=True)")
    print("   6. ui_sandbox('content', changes, preview=False)") 
    print("   7. ui_screenshot('hermes', highlight=...)")
    print("   8. Hope you got the areas right!\n")
    
    # THE NEW WAY - Just works!
    print("✅ The NEW way with ui_workflow:\n")
    
    # Test 1: Add status to Hermes header
    print("1️⃣ Adding status to Hermes header...")
    result = await devtools(
        "ui_workflow",
        workflow="add_to_component",
        component="hermes",
        changes=[{
            "selector": ".hermes__header", 
            "content": '<div style="float: right; color: #4CAF50;">🟢 Connected</div>',
            "action": "append"
        }],
        debug=True
    )
    
    if result.get("status") == "success":
        print(result.get("result", {}).get("visual_feedback", ""))
    else:
        print(f"Error: {result}")
    
    # Test 2: Debug why a component isn't working
    print("\n2️⃣ Debugging Apollo component...")
    debug_result = await devtools(
        "ui_workflow",
        workflow="debug_component",
        component="apollo"
    )
    
    if debug_result.get("status") == "success":
        print(debug_result.get("result", {}).get("visual_feedback", ""))
    
    # Test 3: Quick verification
    print("\n3️⃣ Verifying Rhetor is accessible...")
    verify = await devtools(
        "ui_workflow",
        workflow="verify_component",
        component="rhetor"
    )
    
    if verify.get("status") == "success":
        print(verify.get("result", {}).get("visual_feedback", ""))
    
    print("\n🎉 So much easier! No more:")
    print("   ❌ Confusion about areas vs components")
    print("   ❌ Forgetting to wait for content to load")
    print("   ❌ Using wrong area for modifications")
    print("   ❌ Missing screenshots")
    print("\n   ✅ Just tell it what you want to do!")

if __name__ == "__main__":
    asyncio.run(main())