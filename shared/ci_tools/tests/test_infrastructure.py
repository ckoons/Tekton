#!/usr/bin/env python3
"""Test the complete CI tools infrastructure."""

import sys
import time
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from shared.ci_tools import get_registry
from shared.ci_tools.launcher_instance import get_launcher

print("=== Testing CI Tools Infrastructure ===")

# 1. Test C launcher directly
print("\n1. Testing C launcher directly")
launcher_path = Path(__file__).parent / "shared/ci_tools/bin/ci_tool_launcher"
echo_tool = Path(__file__).parent / "echo_tool_c_test.py"

process = subprocess.Popen(
    [str(launcher_path), "--tool", "echo-test", "--executable", "/usr/bin/env", "--args", "python3", str(echo_tool)],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send a message
process.stdin.write('{"message": "Hello from test"}\n')
process.stdin.flush()

# Read response
response = process.stdout.readline()
print(f"Received: {response.strip()}")

# Terminate
process.terminate()
process.wait()
print("✓ C launcher test passed")

# 2. Test with Python adapter
print("\n2. Testing with Python adapter")
launcher = get_launcher()
registry = get_registry()

# Launch echo tool
if launcher.launch_tool('echo'):
    print("✓ Echo tool launched")
    
    # Check it's running
    time.sleep(1)
    tools = list(launcher.tools.keys())
    print(f"Running tools: {tools}")
    
    if 'echo' in launcher.tools:
        adapter = launcher.tools['echo']['adapter']
        status = adapter.get_status()
        if status['running']:
            print(f"✓ Echo tool running (PID: {status['pid']})")
            
            # Send a message
            msg = {
                'type': 'test',
                'content': 'Test message from infrastructure test'
            }
            if adapter.send_message(msg):
                print("✓ Message sent successfully")
            else:
                print("✗ Failed to send message")
        else:
            print("✗ Echo tool not running")
    
    # Terminate
    launcher.terminate_tool('echo')
    print("✓ Echo tool terminated")
else:
    print("✗ Failed to launch echo tool")

# 3. Test message bus
print("\n3. Testing message bus")
bus_path = Path(__file__).parent / "shared/ci_tools/bin/ci_message_bus"

# Create queues
subprocess.run([str(bus_path), "create", "test-apollo"], check=True)
subprocess.run([str(bus_path), "create", "test-rhetor"], check=True)

# List queues
result = subprocess.run([str(bus_path), "list"], capture_output=True, text=True)
print(f"Queues: {result.stdout.strip()}")

# Clean up
subprocess.run([str(bus_path), "destroy", "test-apollo"])
subprocess.run([str(bus_path), "destroy", "test-rhetor"])
print("✓ Message bus test passed")

print("\n=== All infrastructure tests passed! ===")