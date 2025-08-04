#!/usr/bin/env python3
"""Simple test of echo tool."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from shared.ci_tools import get_registry
from shared.ci_tools.launcher_instance import get_launcher

# Launch echo
launcher = get_launcher()
print("Launching echo tool...")
success = launcher.launch_tool('echo')
print(f"Launch success: {success}")

if success:
    # Wait a bit
    time.sleep(1)
    
    # Check status
    if 'echo' in launcher.tools:
        adapter = launcher.tools['echo']['adapter']
        status = adapter.get_status()
        print(f"Echo tool status: running={status['running']}, pid={status.get('pid')}")
        
        # Send a test message
        msg = {'type': 'test', 'message': 'Hello from Python!'}
        sent = adapter.send_message(msg)
        print(f"Message sent: {sent}")
        
        # Wait and terminate
        time.sleep(1)
        launcher.terminate_tool('echo')
        print("Echo tool terminated")
    else:
        print("Echo not in launcher.tools")
else:
    print("Failed to launch echo tool")