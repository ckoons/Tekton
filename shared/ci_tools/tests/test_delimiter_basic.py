#!/usr/bin/env python3
"""
Basic tests for delimiter functionality that work reliably.
"""

import os
import sys
import json
import time
import socket
import subprocess
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_aish_execute_flag():
    """Test that aish accepts -x flag."""
    print("Test 1: aish -x flag parsing...")
    
    result = subprocess.run(
        [sys.executable, 'shared/aish/aish', '--help'],
        capture_output=True,
        text=True
    )
    
    if '-x' in result.stdout or '--execute' in result.stdout:
        print("✓ Execute flag is documented in help")
        return True
    else:
        print("✗ Execute flag not found in help")
        return False


def test_ci_tool_launch_with_delimiter():
    """Test launching ci-tool with delimiter option."""
    print("\nTest 2: ci-tool launch with delimiter...")
    
    # Launch with sleep command to keep it running
    proc = subprocess.Popen(
        [sys.executable, 'shared/aish/aish', 'ci-tool', '-n', 'test-basic', '-d', '\\n', '--', 'sleep', '10'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it time to start
    time.sleep(1)
    
    # Check if process is running
    if proc.poll() is None:
        print("✓ ci-tool launched with delimiter option")
        proc.terminate()
        proc.wait()
        
        # Clean up socket
        socket_path = '/tmp/ci_msg_test-basic.sock'
        if os.path.exists(socket_path):
            os.unlink(socket_path)
        
        return True
    else:
        print("✗ ci-tool failed to launch")
        stdout, stderr = proc.communicate()
        print(f"  Stderr: {stderr[:200]}")
        return False


def test_ci_terminal_launch_with_delimiter():
    """Test launching ci-terminal with delimiter option."""
    print("\nTest 3: ci-terminal launch with delimiter...")
    
    # Launch with sleep command to keep it running
    proc = subprocess.Popen(
        [sys.executable, 'shared/aish/aish', 'ci-terminal', '-n', 'test-term', '-d', '\\r\\n', '--', 'sleep', '10'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it time to start
    time.sleep(2)
    
    # Check if process is running or socket was created
    socket_path = '/tmp/ci_msg_test-term.sock'
    socket_created = os.path.exists(socket_path)
    
    if proc.poll() is None or socket_created:
        print("✓ ci-terminal launched with delimiter option")
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=2)
        
        # Clean up socket
        socket_path = '/tmp/ci_msg_test-term.sock'
        if os.path.exists(socket_path):
            os.unlink(socket_path)
        
        return True
    else:
        print("✗ ci-terminal failed to launch")
        stdout, stderr = proc.communicate()
        print(f"  Stderr: {stderr[:200]}")
        return False


def test_message_with_execute():
    """Test sending message with execute flag."""
    print("\nTest 4: Message with execute flag...")
    
    # Launch ci-tool
    proc = subprocess.Popen(
        [sys.executable, 'shared/aish/aish', 'ci-tool', '-n', 'test-msg', '-d', '\\n', '--', 'echo', 'started'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for socket
    socket_path = '/tmp/ci_msg_test-msg.sock'
    for _ in range(30):
        if os.path.exists(socket_path):
            break
        time.sleep(0.1)
    
    time.sleep(0.5)
    
    try:
        # Send message via aish with execute flag
        result = subprocess.run(
            [sys.executable, 'shared/aish/aish', 'test-msg', 'Hello', '-x'],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        if result.returncode == 0:
            print("✓ Message sent with execute flag")
            return True
        else:
            print(f"✗ Failed to send message: {result.stderr}")
            return False
            
    finally:
        # Cleanup
        proc.terminate()
        proc.wait()
        if os.path.exists(socket_path):
            os.unlink(socket_path)


def test_delimiter_in_wrapper_code():
    """Test that delimiter code exists in wrapper files."""
    print("\nTest 5: Delimiter code in wrappers...")
    
    # Check PTY wrapper
    pty_path = Path('shared/ci_tools/ci_pty_wrapper.py')
    if pty_path.exists():
        content = pty_path.read_text()
        if 'delimiter' in content and 'execute' in content:
            print("✓ PTY wrapper has delimiter and execute support")
        else:
            print("✗ PTY wrapper missing delimiter or execute support")
            return False
    
    # Check simple wrapper
    simple_path = Path('shared/ci_tools/ci_simple_wrapper.py')
    if simple_path.exists():
        content = simple_path.read_text()
        if 'delimiter' in content and 'execute' in content:
            print("✓ Simple wrapper has delimiter and execute support")
        else:
            print("✗ Simple wrapper missing delimiter or execute support")
            return False
    
    return True


def main():
    """Run all basic tests."""
    print("=" * 60)
    print("Basic Delimiter Functionality Tests")
    print("=" * 60)
    
    tests = [
        test_aish_execute_flag,
        test_ci_tool_launch_with_delimiter,
        test_ci_terminal_launch_with_delimiter,
        test_message_with_execute,
        test_delimiter_in_wrapper_code
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    # Clean up any leftover sockets
    for socket_file in Path('/tmp').glob('ci_msg_test*.sock'):
        try:
            socket_file.unlink()
        except:
            pass
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)