#!/usr/bin/env python3
"""Test echo tool directly with logging."""

import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.insert(0, str(Path(__file__).parent))

from shared.ci_tools import get_registry
from shared.ci_tools.launcher_instance import get_launcher

# Test launching
launcher = get_launcher()
registry = get_registry()

print(f"Launcher ID: {id(launcher)}")
print(f"Registry ID: {id(registry)}")

# Launch echo
print("\nLaunching echo tool...")
success = launcher.launch_tool('echo')
print(f"Launch result: {success}")

# Check status
print(f"\nLauncher tools: {list(launcher.tools.keys())}")

# Wait a bit
import time
time.sleep(2)

# Check again
print(f"\nAfter 2 seconds:")
print(f"Launcher tools: {list(launcher.tools.keys())}")

# Check process
if launcher.tools:
    for name, info in launcher.tools.items():
        adapter = info['adapter']
        status = adapter.get_status()
        print(f"Tool {name} status: {status}")
        if adapter.process:
            print(f"Process poll: {adapter.process.poll()}")