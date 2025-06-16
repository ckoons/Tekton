#!/usr/bin/env python3
"""
Debug script to check what routes are actually registered in the Hermes app.
"""

import sys
import os

# Add Hermes to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app
from hermes.api.app import app

print("Checking routes in Hermes app...")
print("=" * 60)

# Get all routes
routes = []
for route in app.routes:
    if hasattr(route, 'path'):
        routes.append({
            'path': route.path,
            'methods': list(route.methods) if hasattr(route, 'methods') else [],
            'name': route.name if hasattr(route, 'name') else 'Unknown'
        })

# Sort and display routes
routes.sort(key=lambda x: x['path'])

print(f"Found {len(routes)} routes:\n")

# Group by path prefix
mcp_routes = [r for r in routes if 'mcp' in r['path'].lower()]
api_routes = [r for r in routes if r['path'].startswith('/api')]
other_routes = [r for r in routes if r not in mcp_routes and r not in api_routes]

if mcp_routes:
    print("MCP Routes:")
    for route in mcp_routes:
        print(f"  {route['path']} - {route['methods']} - {route['name']}")
    print()

if api_routes:
    print("API Routes:")
    for route in api_routes[:20]:  # Limit to first 20
        print(f"  {route['path']} - {route['methods']} - {route['name']}")
    if len(api_routes) > 20:
        print(f"  ... and {len(api_routes) - 20} more")
    print()

print("\nChecking for MCP router...")
# Try to import and check MCP router
try:
    from hermes.api.mcp_endpoints import mcp_router
    print(f"MCP router found with prefix: {mcp_router.prefix}")
    print(f"MCP router has {len(mcp_router.routes)} routes")
    for route in mcp_router.routes[:5]:
        if hasattr(route, 'path'):
            print(f"  {route.path} - {route.methods if hasattr(route, 'methods') else 'N/A'}")
except Exception as e:
    print(f"Error checking MCP router: {e}")