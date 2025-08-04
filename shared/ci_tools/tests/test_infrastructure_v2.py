#!/usr/bin/env python3
"""Test the complete CI tools infrastructure."""

import json
import time
import socket
import sys
import os

# Add shared directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

from ci_tools.simple_launcher_v2 import SimpleToolLauncherV2

def test_echo_tool():
    """Test the echo tool with socket communication."""
    print("\n=== Testing Echo Tool Infrastructure ===\n")
    
    # Create launcher
    launcher = SimpleToolLauncherV2()
    
    # Launch echo tool
    print("1. Launching echo tool...")
    if launcher.launch_tool('echo'):
        print("✓ Echo tool launched successfully")
    else:
        print("✗ Failed to launch echo tool")
        return False
    
    # Give it time to start
    time.sleep(2)
    
    # Check status
    status = launcher.get_tool_status('echo')
    print(f"\n2. Tool status: {json.dumps(status, indent=2)}")
    
    if not status['running']:
        print("✗ Echo tool is not running")
        return False
    
    # Test socket communication
    port = status['port']
    print(f"\n3. Testing socket communication on port {port}...")
    
    try:
        # Connect to echo tool
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect(('localhost', port))
        
        # Send test message
        test_msg = {'message': 'Hello from test!', 'timestamp': time.time()}
        client.send(json.dumps(test_msg).encode('utf-8'))
        
        # Receive response
        response = client.recv(4096).decode('utf-8')
        client.close()
        
        resp_data = json.loads(response)
        print(f"✓ Received response: {resp_data}")
        
        if 'Echo: Hello from test!' in resp_data.get('content', ''):
            print("✓ Echo response is correct")
        else:
            print("✗ Echo response is incorrect")
            return False
            
    except Exception as e:
        print(f"✗ Socket communication failed: {e}")
        return False
    
    # Check if still running
    print("\n4. Checking if tool is still running...")
    status = launcher.get_tool_status('echo')
    if status['running']:
        print("✓ Echo tool is still running")
        print(f"   Uptime: {status.get('uptime', 0):.2f} seconds")
    else:
        print("✗ Echo tool has stopped")
        return False
    
    # Terminate tool
    print("\n5. Terminating echo tool...")
    if launcher.terminate_tool('echo'):
        print("✓ Echo tool terminated successfully")
    else:
        print("✗ Failed to terminate echo tool")
        return False
    
    # Verify terminated
    time.sleep(1)
    status = launcher.get_tool_status('echo')
    if not status['running']:
        print("✓ Echo tool is confirmed stopped")
    else:
        print("✗ Echo tool is still running after termination")
        return False
    
    print("\n✓ All tests passed!")
    return True

def test_c_infrastructure():
    """Test C launcher and message bus directly."""
    print("\n=== Testing C Infrastructure ===\n")
    
    # Test C launcher
    print("1. Testing C launcher...")
    launcher_path = os.path.join(os.path.dirname(__file__), 'shared/ci_tools/bin/ci_tool_launcher')
    if os.path.exists(launcher_path):
        print(f"✓ C launcher found at: {launcher_path}")
        # Could add more tests here if needed
    else:
        print("✗ C launcher not found")
        return False
    
    # Test message bus
    print("\n2. Testing C message bus...")
    msgbus_path = os.path.join(os.path.dirname(__file__), 'shared/ci_tools/bin/ci_message_bus')
    if os.path.exists(msgbus_path):
        print(f"✓ C message bus found at: {msgbus_path}")
        # Could add more tests here if needed
    else:
        print("✗ C message bus not found")
        return False
    
    return True

if __name__ == '__main__':
    # Test C infrastructure first
    if not test_c_infrastructure():
        print("\nC infrastructure tests failed!")
        sys.exit(1)
    
    # Test echo tool
    if not test_echo_tool():
        print("\nEcho tool tests failed!")
        sys.exit(1)
    
    print("\n✓ All infrastructure tests passed!")