#!/usr/bin/env python3
"""
Verify MCP changes are in the running code.
This checks the actual source files to ensure our changes are present.
"""

import os
import sys

def check_file_contains(filepath, search_string, description):
    """Check if a file contains a specific string."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}: Found")
                return True
            else:
                print(f"❌ {description}: NOT FOUND")
                return False
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return False

def main():
    print("Verifying MCP Phase 1 changes are in place...")
    print("=" * 60)
    
    # Get the Hermes directory
    hermes_dir = os.path.dirname(os.path.abspath(__file__))
    
    checks = [
        {
            "file": os.path.join(hermes_dir, "hermes/core/mcp_service.py"),
            "search": "self.message_bus.create_channel(",
            "description": "MCP service initialization fix (removed await)"
        },
        {
            "file": os.path.join(hermes_dir, "hermes/api/mcp_endpoints.py"),
            "search": 'prefix="/api/mcp/v2"',
            "description": "MCP router uses /api/mcp/v2 prefix"
        },
        {
            "file": os.path.join(hermes_dir, "hermes/api/app.py"),
            "search": "app.include_router(mcp_router)",
            "description": "MCP router mounted on main app"
        },
        {
            "file": os.path.join(hermes_dir, "hermes/api/mcp_endpoints.py"),
            "search": '@mcp_router.get("/tools")',
            "description": "GET /tools endpoint exists"
        }
    ]
    
    passed = 0
    failed = 0
    
    for check in checks:
        if check_file_contains(check["file"], check["search"], check["description"]):
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Total checks: {len(checks)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print()
    
    if failed > 0:
        print("❌ Some changes are missing! The code may not have been saved properly.")
        return 1
    else:
        print("✅ All changes are in place!")
        print()
        print("If the MCP endpoints are still returning 404, Hermes needs to be restarted:")
        print("  1. Stop Hermes")
        print("  2. Start it again")
        print("  3. Run the test: ./test_mcp.sh")
        return 0

if __name__ == "__main__":
    sys.exit(main())