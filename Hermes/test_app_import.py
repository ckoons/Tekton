#!/usr/bin/env python3
"""
Test what happens when we import the app the way uvicorn does.
"""

import importlib

print("Testing app import as uvicorn would do it...")
print("=" * 60)

# Import the way uvicorn does
module_str = "hermes.api.app"
app_str = "app"

print(f"Importing {module_str}:{app_str}")

# Import the module
module = importlib.import_module(module_str)
app = getattr(module, app_str)

print(f"App type: {type(app)}")
print(f"App title: {getattr(app, 'title', 'N/A')}")

# Check routes
routes = list(app.routes)
print(f"\nTotal routes: {len(routes)}")

# Check MCP routes
mcp_routes = [r for r in routes if hasattr(r, 'path') and 'mcp' in r.path.lower()]
print(f"MCP routes: {len(mcp_routes)}")

if mcp_routes:
    print("\nMCP route paths:")
    for route in mcp_routes[:10]:
        methods = list(route.methods) if hasattr(route, 'methods') else []
        print(f"  {route.path} - {methods}")
else:
    print("\nNO MCP ROUTES FOUND!")
    
# Check if mcp_router was imported
print(f"\nChecking if mcp_router is imported in module...")
if hasattr(module, 'mcp_router'):
    print("  mcp_router found in module")
else:
    print("  mcp_router NOT found in module")