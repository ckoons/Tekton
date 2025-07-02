#!/usr/bin/env python3
"""Test script for aish-Tekton integration."""

import sys
import os
from pathlib import Path

print("=== aish-Tekton Integration Test ===\n")

# Test 1: Check if aish-proxy is in the correct location
aish_proxy_path = Path(__file__).parent.parent / "shared" / "aish" / "aish-proxy"
print(f"1. Checking aish-proxy location:")
print(f"   Expected: {aish_proxy_path}")
print(f"   Exists: {aish_proxy_path.exists()}")
if aish_proxy_path.exists():
    print("   ✅ aish-proxy found in Tekton/shared/aish")
else:
    print("   ❌ aish-proxy NOT found in expected location")

# Test 2: Check if terminal launcher will find it
print("\n2. Testing terminal launcher path resolution:")
try:
    from terma.core.terminal_launcher_impl import TerminalLauncher
    launcher = TerminalLauncher()
    print(f"   Found aish-proxy at: {launcher.aish_path}")
    if "Tekton/shared/aish" in launcher.aish_path:
        print("   ✅ Terminal launcher using correct location")
    else:
        print("   ⚠️  Terminal launcher using old location")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Check environment
print("\n3. Environment check:")
print(f"   RHETOR_ENDPOINT: {os.environ.get('RHETOR_ENDPOINT', 'Not set (will use default)')}")
print(f"   Current directory: {os.getcwd()}")
print(f"   Home directory: {os.path.expanduser('~')}")

print("\n=== End of Test ===")