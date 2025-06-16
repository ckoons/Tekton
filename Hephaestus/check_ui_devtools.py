#!/usr/bin/env python3
"""
Quick check script for UI DevTools MCP status
Use this at the start of any UI development work
"""

import sys
import httpx
import asyncio
import subprocess
import time


async def check_mcp_status():
    """Check if the UI DevTools MCP is running"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8088/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print("✅ UI DevTools MCP is running")
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Component: {data.get('component', 'unknown')}")
                return True
    except Exception as e:
        print("❌ UI DevTools MCP is NOT running")
        return False
    
    return False


async def check_hermes_registration():
    """Check if MCP is registered with Hermes"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/api/components", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                components = data.get('components', [])
                mcp = next((c for c in components if c['name'] == 'hephaestus_ui_devtools'), None)
                if mcp:
                    print("✅ Registered with Hermes")
                    return True
                else:
                    print("⚠️  Not registered with Hermes (may still be starting)")
    except:
        print("⚠️  Cannot check Hermes registration")
    
    return False


def offer_to_start():
    """Offer to start the MCP"""
    print("\nWould you like to start the UI DevTools MCP? (y/n): ", end='')
    response = input().strip().lower()
    
    if response == 'y':
        print("Starting UI DevTools MCP...")
        try:
            # Start in background
            subprocess.Popen(
                ["./run_mcp.sh"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd="/Users/cskoons/projects/github/Tekton/Hephaestus"
            )
            
            # Wait for startup
            print("Waiting for MCP to start", end='')
            for i in range(10):
                print(".", end='', flush=True)
                time.sleep(1)
                
                # Check if it's up
                try:
                    import requests
                    resp = requests.get("http://localhost:8088/health", timeout=1)
                    if resp.status_code == 200:
                        print("\n✅ MCP started successfully!")
                        return True
                except:
                    pass
            
            print("\n⚠️  MCP may still be starting. Check again in a few seconds.")
            
        except Exception as e:
            print(f"❌ Failed to start MCP: {e}")
            print("   Please run manually: ./Hephaestus/run_mcp.sh")
    else:
        print("\nTo start manually:")
        print("  cd $TEKTON_ROOT/Hephaestus")
        print("  ./run_mcp.sh")
    
    return False


async def main():
    """Main check routine"""
    print("UI DevTools MCP Status Check")
    print("=" * 40)
    
    # Check MCP
    mcp_running = await check_mcp_status()
    
    if mcp_running:
        # Also check Hermes
        await check_hermes_registration()
        
        print("\n✅ Ready for UI development!")
        print("\nQuick test command:")
        print('  curl -X POST http://localhost:8088/api/mcp/v2/execute \\')
        print('    -H "Content-Type: application/json" \\')
        print('    -d \'{"tool_name": "ui_capture", "arguments": {"component": "rhetor"}}\'')
        
    else:
        print("\n⚠️  UI DevTools MCP is required for safe UI development")
        print("   Without it, Claude might install React!")
        
        # Offer to start
        offer_to_start()
    
    print("\n" + "=" * 40)
    print("Remember: No MCP = Risk of Nuclear Destruction")


if __name__ == "__main__":
    asyncio.run(main())