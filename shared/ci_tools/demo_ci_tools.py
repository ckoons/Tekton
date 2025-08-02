#!/usr/bin/env python3
"""
Demo script for CI Tools integration with Tekton.

This demonstrates how CI tools like Claude Code, Cursor, and Continue
can be integrated as first-class citizens in the Tekton ecosystem.
"""

import sys
import time
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

print("=== CI Tools Integration Demo ===\n")

# Import and test the integration
print("1. Testing CI Tools Registry...")
from shared.ci_tools import get_registry
registry = get_registry()
tools = registry.get_tools()

print(f"   Found {len(tools)} registered CI tools:")
for name, config in tools.items():
    print(f"   - {name}: {config['description']}")
    print(f"     Port: {config['port']}")
    print(f"     Capabilities: {', '.join(k for k, v in config.get('capabilities', {}).items() if v)}")
    print()

print("\n2. Testing aish Integration...")
print("   The following commands are now available:")
print("   - aish list                    # Shows all CIs including tools")
print("   - aish list type tool          # Filter to show only CI tools")
print("   - aish list json tool          # Get tool info in JSON format")
print("   - aish claude-code 'message'   # Send message to Claude Code")
print("   - aish cursor 'message'        # Send message to Cursor")
print("   - aish continue 'message'      # Send message to Continue")

print("\n3. Architecture Highlights:")
print("   - CI tools are registered in the unified CI registry")
print("   - Each tool has a dedicated port (8400-8449 range)")
print("   - Socket bridge handles bidirectional communication")
print("   - Tool adapters translate between Tekton and tool-specific formats")
print("   - Automatic process lifecycle management")
print("   - Integration with Apollo-Rhetor coordination")

print("\n4. Example Usage Scenarios:")
print("   a) Code Review:")
print("      aish claude-code 'Review the authentication module for security issues'")
print("\n   b) Refactoring:")
print("      aish cursor 'Refactor UserService to use dependency injection'")
print("\n   c) Debugging:")
print("      aish continue 'Help debug this TypeError in the payment module'")
print("\n   d) Chaining Tools:")
print("      echo 'Design a caching system' | aish prometheus | aish claude-code")
print("\n   e) Forwarding Output:")
print("      aish forward claude-code alice    # Forward Claude's output to alice's terminal")

print("\n5. Session Management (Future Enhancement):")
print("   - aish session create review --tool claude-code")
print("   - aish session resume review")
print("   - aish session save review")

print("\n6. Tool Status:")
from shared.ci_tools import ToolLauncher
launcher = ToolLauncher.get_instance()
status = launcher.get_all_status()

for tool_name in tools:
    tool_status = status.get(tool_name, {})
    if tool_status.get('running'):
        print(f"   {tool_name}: Running (PID: {tool_status.get('adapter_status', {}).get('pid')})")
    else:
        print(f"   {tool_name}: Stopped")

print("\n7. Benefits:")
print("   - Unified interface for all CI tools through aish")
print("   - Programmatic control over development tools")
print("   - Leverage subscription models (Claude Max, etc.)")
print("   - Seamless integration with Tekton's orchestration")
print("   - Context sharing across all CI types")

print("\n=== Demo Complete ===")
print("\nTo start using CI tools:")
print("1. Ensure the tool is installed (e.g., claude-code in PATH)")
print("2. Use aish to send messages: aish claude-code 'Hello!'")
print("3. The tool will launch automatically on first use")
print("4. Responses appear in your terminal")
print("\nNote: This is a prototype - actual tool executables need to be installed.")