#!/usr/bin/env python3
"""Example of running multiple Claude Code instances."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from shared.ci_tools.simple_launcher_v2 import SimpleToolLauncherV2

def launch_multiple_claude_instances():
    """Launch multiple Claude Code instances for different purposes."""
    
    launcher = SimpleToolLauncherV2()
    
    # Launch instances for different Coders
    instances = [
        ('coder-a-perf', 'Performance optimization work'),
        ('coder-b-memory', 'Memory Evolution Sprint'),
        ('coder-c-ui', 'UI development'),
        ('code-reviewer', 'Automated code review'),
        ('test-writer', 'Test generation'),
        ('doc-writer', 'Documentation generation')
    ]
    
    print("=== Launching Multiple Claude Code Instances ===\n")
    
    launched = []
    for instance_name, purpose in instances:
        print(f"Launching {instance_name} for {purpose}...")
        if launcher.launch_tool('claude-code', instance_name=instance_name):
            launched.append(instance_name)
            print(f"✓ {instance_name} launched successfully")
        else:
            print(f"✗ Failed to launch {instance_name}")
        time.sleep(1)  # Give each instance time to start
    
    print(f"\n✓ Launched {len(launched)} Claude Code instances")
    
    # Check all running instances
    print("\n=== Running Claude Code Instances ===")
    running = launcher.get_running_tools()
    
    for name, info in running.items():
        if 'claude' in name.lower():
            print(f"\n{name}:")
            print(f"  PID: {info['pid']}")
            print(f"  Port: {info['port']}")
            print(f"  Uptime: {time.time() - info.get('start_time', 0):.1f}s")
    
    return launched

if __name__ == '__main__':
    launched = launch_multiple_claude_instances()
    print(f"\nYou can now communicate with each instance:")
    for instance in launched:
        print(f"  aish forward claude-code:{instance} term{launched.index(instance)+1}")