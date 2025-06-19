#!/usr/bin/env python3
"""
Example of using the UI DevTools Client

This shows the clean Python API for UI DevTools operations.
"""
import asyncio
import sys
import os

# Add parent directory to path to import the client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui_devtools_client import UIDevToolsClient

async def main():
    """Example UI DevTools operations using the client"""
    
    # Initialize the client
    ui = UIDevToolsClient()
    
    print("🔧 UI DevTools Client Example\n")
    
    try:
        # 1. List available areas
        print("1️⃣ Listing available UI areas...")
        areas = await ui.list_areas()
        print(f"   Found {len(areas)} areas")
        for area, info in areas.items():
            print(f"   - {area}: {info.get('description', '')}")
        
        # 2. Navigate to a component
        print("\n2️⃣ Navigating to Hermes...")
        nav_result = await ui.navigate("hermes")
        print(f"   Status: {nav_result.get('status', 'unknown')}")
        
        # 3. Capture the content area
        print("\n3️⃣ Capturing content area...")
        capture = await ui.capture("content")
        element_count = len(capture.get('structure', {}).get('elements', []))
        print(f"   Found {element_count} elements")
        
        # 4. Take a screenshot
        print("\n4️⃣ Taking screenshot...")
        screenshot = await ui.screenshot("hermes", save_to_file=True)
        file_path = screenshot.get('file_path', 'Not saved')
        print(f"   Saved to: {file_path}")
        
        # 5. Make a simple change
        print("\n5️⃣ Adding a test element...")
        sandbox_result = await ui.sandbox(
            area="content",
            changes=[{
                "type": "html",
                "selector": "body",
                "content": '<div style="position: fixed; top: 10px; right: 10px; background: #4CAF50; color: white; padding: 5px;">UI DevTools Test</div>',
                "action": "append"
            }],
            preview=False
        )
        print(f"   Change applied: {sandbox_result.get('applied', False)}")
        
        print("\n✅ Example completed successfully!")
        print("\n💡 Tips:")
        print("   - Always navigate before capturing component content")
        print("   - Use 'content' area for component modifications")
        print("   - Check file_path in screenshot results")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure the MCP server is running:")
        print("   cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh")

if __name__ == "__main__":
    asyncio.run(main())