#!/usr/bin/env python3
"""
Add debug output to app.py to understand the loading sequence.
"""

import os

# Read the app.py file
app_file = os.path.join(os.path.dirname(__file__), "hermes/api/app.py")

with open(app_file, 'r') as f:
    content = f.read()

# Find where to add debug output - after the app.include_router(mcp_router) line
lines = content.split('\n')
new_lines = []

for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Add debug after app creation
    if line.strip().startswith('app = FastAPI('):
        # Find the closing parenthesis
        j = i + 1
        while j < len(lines) and not lines[j].strip().endswith(')'):
            j += 1
        if j < len(lines):
            new_lines.append(lines[j])
            new_lines.append('print(f"[DEBUG] Main app created with {len(app.routes)} routes")')
            i = j
            continue
    
    # Add debug after MCP router inclusion
    if 'app.include_router(mcp_router)' in line:
        new_lines.append('print(f"[DEBUG] MCP router included, app now has {len(app.routes)} routes")')
        new_lines.append('print(f"[DEBUG] MCP routes: {[r.path for r in app.routes if hasattr(r, \'path\') and \'mcp\' in r.path]}")')

# Write back
with open(app_file + '.debug', 'w') as f:
    f.write('\n'.join(new_lines))

print("Debug version created at hermes/api/app.py.debug")
print("To use it, copy it over the original:")
print("  cp hermes/api/app.py.debug hermes/api/app.py")