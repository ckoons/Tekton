#!/usr/bin/env python3
"""Test launching directly to see what happens."""

import subprocess
import os

env = os.environ.copy()
env['TEKTON_CI_PORT'] = '12345'

# Launch the echo tool directly
process = subprocess.Popen(
    ['/opt/anaconda3/bin/python', 'echo_tool_socket_aware.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env,
    text=True
)

# Get initial output
import time
time.sleep(0.5)

# Check if still running
if process.poll() is None:
    print("Process is still running")
    
    # Send a test message
    process.stdin.write('{"message": "test"}\n')
    process.stdin.flush()
    
    # Read response
    time.sleep(0.1)
    stdout = process.stdout.readline()
    if stdout:
        print(f"stdout: {stdout.strip()}")
    
    # Terminate
    process.terminate()
else:
    print(f"Process exited with code: {process.poll()}")
    
# Get all output
stdout, stderr = process.communicate()
print(f"\nAll stdout:\n{stdout}")
print(f"\nAll stderr:\n{stderr}")