#!/usr/bin/env python3
"""
Test script for CI Tools integration.
"""

import sys
import os
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Test imports
print("Testing CI Tools imports...")
try:
    from shared.ci_tools import get_registry, ToolLauncher
    from shared.ci_tools.adapters import ClaudeCodeAdapter
    print("✓ CI Tools imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test registry
print("\nTesting CI Tools Registry...")
registry = get_registry()
tools = registry.get_tools()
print(f"✓ Found {len(tools)} registered tools:")
for tool_name, config in tools.items():
    print(f"  - {tool_name}: {config['description']} (port {config['port']})")

# Test tool status
print("\nTesting tool status...")
for tool_name in tools:
    status = registry.get_tool_status(tool_name)
    running = "running" if status.get('running') else "stopped"
    print(f"  - {tool_name}: {running}")

# Test adapter creation
print("\nTesting Claude Code adapter...")
try:
    adapter = ClaudeCodeAdapter(port=8400)
    print("✓ Claude Code adapter created")
    
    # Test executable finding
    exe_path = adapter.get_executable_path()
    if exe_path:
        print(f"✓ Claude Code executable found: {exe_path}")
    else:
        print("✗ Claude Code executable not found (this is expected if not installed)")
    
    # Test capabilities
    caps = adapter.get_capabilities()
    print(f"✓ Capabilities: {', '.join(k for k, v in caps.items() if v)}")
    
except Exception as e:
    print(f"✗ Adapter test failed: {e}")

# Test launcher
print("\nTesting Tool Launcher...")
try:
    launcher = ToolLauncher.get_instance()
    print("✓ Tool launcher singleton created")
    
    # Get all status
    all_status = launcher.get_all_status()
    print(f"✓ Launcher tracking {len(launcher.tools)} active tools")
    
except Exception as e:
    print(f"✗ Launcher test failed: {e}")

print("\n✅ CI Tools integration test complete!")
print("\nTo test with aish:")
print("  aish list type tool      # List available CI tools")
print("  aish claude-code 'test'  # Send message to Claude Code")