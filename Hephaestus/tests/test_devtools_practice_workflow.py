#!/usr/bin/env python3
import httpx
import asyncio
import json
from typing import Any, Dict

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def devtools(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Clean wrapper for UI DevTools API calls"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            MCP_URL,
            json={"tool_name": tool_name, "arguments": kwargs}
        )
        return response.json()

async def main():
    # Step 1: Get recommendations for the task
    print("🔍 Getting recommendations...")
    recommendations = await devtools(
        "ui_recommend_approach",
        target_description="hermes header area",
        intended_change="add connection status indicator"
    )
    print(json.dumps(recommendations, indent=2))
    
    # Step 2: Navigate to Hermes first (to ensure browser is ready)
    print("\n🧭 Navigating to Hermes...")
    nav_result = await devtools("ui_navigate", component="hermes")
    print(f"Navigation result: {nav_result.get('result', {}).get('status', 'Unknown')}")
    
    # Step 3: Take a "before" screenshot
    print("\n📸 Taking 'before' screenshot...")
    before_screenshot = await devtools(
        "ui_screenshot",
        component="hermes",
        save_to_file=True
    )
    print(f"Screenshot saved: {before_screenshot.get('result', {}).get('screenshot_path', 'Unknown')}")
    
    # Step 4: Capture the structure
    print("\n🏗️ Capturing Hermes structure...")
    structure = await devtools("ui_capture", area="hermes")
    print(f"Captured {len(structure.get('result', {}).get('elements', []))} elements")
    
    # Step 5: Preview the change
    print("\n✨ Previewing status indicator addition...")
    preview = await devtools(
        "ui_sandbox",
        area="hermes",
        changes=[{
            "type": "html",
            "selector": ".hermes__header",
            "content": '<div class="hermes__status">🟢 Connected</div>',
            "action": "append"
        }],
        preview=True
    )
    print(f"Preview result: {preview.get('result', {}).get('status', 'Unknown')}")
    
    # Ask if we should apply
    input("\nPress Enter to apply the change (or Ctrl+C to cancel)...")
    
    # Step 6: Apply the change
    print("\n🔨 Applying the change...")
    apply_result = await devtools(
        "ui_sandbox",
        area="hermes",
        changes=[{
            "type": "html",
            "selector": ".hermes__header",
            "content": '<div class="hermes__status">🟢 Connected</div>',
            "action": "append"
        }],
        preview=False
    )
    print(f"Apply result: {apply_result.get('result', {}).get('status', 'Unknown')}")
    
    # Step 7: Take "after" screenshot with highlight
    print("\n📸 Taking 'after' screenshot with highlight...")
    after_screenshot = await devtools(
        "ui_screenshot",
        component="hermes",
        highlight=".hermes__status",
        save_to_file=True
    )
    print(f"Screenshot saved: {after_screenshot.get('result', {}).get('screenshot_path', 'Unknown')}")
    
    print("\n✅ Practice task complete! Check the screenshots to see the difference.")

if __name__ == "__main__":
    asyncio.run(main())