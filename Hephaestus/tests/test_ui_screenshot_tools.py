#!/usr/bin/env python3
"""
Test the Phase 4 screenshot capabilities
"""

import asyncio
import httpx
import json
import base64
from pathlib import Path

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"


async def test_basic_screenshot():
    """Test basic screenshot functionality"""
    print("\n1. Testing basic screenshot...")
    print("-" * 50)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_screenshot",
            "arguments": {
                "component": "rhetor",
                "full_page": False,
                "save_to_file": True
            }
        })
        
        result = response.json()
        if result.get("status") == "success":
            data = result["result"]
            print(f"✓ Screenshot saved to: {data['file_path']}")
            print(f"✓ Dimensions: {data['dimensions']['width']}x{data['dimensions']['height']}")
            print(f"✓ Base64 size: {len(data['image'])} chars")
            
            # Decode and save locally for viewing
            if data.get('image'):
                img_data = base64.b64decode(data['image'])
                local_path = Path("test_screenshot.png")
                local_path.write_bytes(img_data)
                print(f"✓ Also saved locally as: {local_path}")
        else:
            print(f"✗ Error: {result.get('error')}")


async def test_visual_diff():
    """Test visual diff between two states"""
    print("\n2. Testing visual diff...")
    print("-" * 50)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_visual_diff",
            "arguments": {
                "before_action": {
                    "type": "navigate",
                    "component": "hermes"
                },
                "after_action": {
                    "type": "navigate", 
                    "component": "prometheus"
                }
            }
        })
        
        result = response.json()
        if result.get("status") == "success":
            data = result["result"]
            print(f"✓ Visual diff completed")
            print(f"✓ Before dimensions: {data['before']['dimensions']['width']}x{data['before']['dimensions']['height']}")
            print(f"✓ After dimensions: {data['after']['dimensions']['width']}x{data['after']['dimensions']['height']}")
            print(f"✓ Size change: {data['analysis']['size_change']} bytes")
            
            # Save both images
            for name, img_data in [("before", data['before']), ("after", data['after'])]:
                if img_data.get('screenshot'):
                    img_bytes = base64.b64decode(img_data['screenshot'])
                    local_path = Path(f"test_diff_{name}.png")
                    local_path.write_bytes(img_bytes)
                    print(f"✓ Saved {name} as: {local_path}")
        else:
            print(f"✗ Error: {result.get('error')}")


async def test_highlight_element():
    """Test screenshot with element highlighting"""
    print("\n3. Testing screenshot with highlight...")
    print("-" * 50)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_screenshot",
            "arguments": {
                "component": "rhetor",
                "full_page": False,
                "highlight": ".rhetor__title",
                "save_to_file": True
            }
        })
        
        result = response.json()
        if result.get("status") == "success":
            data = result["result"]
            print(f"✓ Screenshot with highlight saved to: {data['file_path']}")
            print("✓ The title should have a red border in the screenshot")
        else:
            print(f"✗ Error: {result.get('error')}")


async def test_all_components():
    """Test capturing all components (just check, don't run full)"""
    print("\n4. Testing capture all components (metadata only)...")
    print("-" * 50)
    
    async with httpx.AsyncClient() as client:
        # Get tool metadata instead of running it (it takes a while)
        response = await client.get("http://localhost:8088/api/mcp/v2/tools")
        tools = response.json()
        
        if "ui_capture_all_components" in tools["tools"]:
            print("✓ ui_capture_all_components tool is available")
            print("  To run it: curl -X POST ... (see above)")
            print("  Note: This captures ALL components and takes time!")
        else:
            print("✗ Tool not found!")


async def main():
    print("=" * 60)
    print("Testing Phase 4 Screenshot Tools".center(60))
    print("=" * 60)
    
    await test_basic_screenshot()
    await test_visual_diff()
    await test_highlight_element()
    await test_all_components()
    
    print("\n" + "=" * 60)
    print("Testing complete! Check the generated PNG files.".center(60))
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())