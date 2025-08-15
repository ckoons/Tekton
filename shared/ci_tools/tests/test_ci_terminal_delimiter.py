#!/usr/bin/env python3
"""
Tests for CI terminal delimiter and execute functionality.
"""

import os
import sys
import json
import time
import socket
import subprocess
import tempfile
import threading
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestCITerminalDelimiter:
    """Test suite for CI terminal delimiter functionality."""
    
    def __init__(self):
        self.test_name = None
        self.wrapper_proc = None
        self.socket_path = None
        
    def setup(self, name="test-ci"):
        """Setup test environment."""
        self.test_name = name
        self.socket_path = f"/tmp/ci_msg_{name}.sock"
        # Clean up any existing socket
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
    
    def teardown(self):
        """Cleanup test environment."""
        if self.wrapper_proc:
            self.wrapper_proc.terminate()
            self.wrapper_proc.wait(timeout=2)
            self.wrapper_proc = None
        
        if self.socket_path and os.path.exists(self.socket_path):
            try:
                os.unlink(self.socket_path)
            except:
                pass
    
    def launch_wrapper(self, delimiter=None, command=['cat']):
        """Launch PTY wrapper with optional delimiter."""
        wrapper_path = Path(__file__).parent.parent / 'ci_pty_wrapper.py'
        
        cmd = [sys.executable, str(wrapper_path), '--name', self.test_name]
        if delimiter:
            cmd.extend(['--delimiter', delimiter])
        cmd.append('--')
        cmd.extend(command)
        
        self.wrapper_proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for socket to be ready
        for _ in range(20):  # 2 seconds max
            if os.path.exists(self.socket_path):
                time.sleep(0.1)  # Extra time for socket to be listening
                return True
            time.sleep(0.1)
        
        return False
    
    def send_message(self, content, execute=False, delimiter=None):
        """Send a message to the wrapper via socket."""
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
            
            message = {
                'from': 'test',
                'content': content,
                'type': 'message',
                'execute': execute
            }
            
            if delimiter is not None:
                message['delimiter'] = delimiter
            
            sock.send(json.dumps(message).encode('utf-8'))
            sock.close()
            return True
            
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
    
    def read_output(self, timeout=1):
        """Read output from wrapper with timeout."""
        import select
        
        output = []
        ready = select.select([self.wrapper_proc.stdout], [], [], timeout)
        if ready[0]:
            while True:
                ready = select.select([self.wrapper_proc.stdout], [], [], 0.1)
                if ready[0]:
                    line = self.wrapper_proc.stdout.readline()
                    if line:
                        output.append(line)
                    else:
                        break
                else:
                    break
        
        return ''.join(output)
    
    def test_launch_with_delimiter(self):
        """Test launching wrapper with delimiter configuration."""
        print("Testing: Launch with delimiter...")
        self.setup("test-delim")
        
        try:
            # Launch with newline delimiter
            success = self.launch_wrapper(delimiter="\\n")
            assert success, "Failed to launch wrapper"
            
            # Verify process is running
            assert self.wrapper_proc.poll() is None, "Wrapper exited prematurely"
            
            print("✓ Launch with delimiter successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Launch with delimiter failed: {e}")
            return False
        finally:
            self.teardown()
    
    def test_execute_without_delimiter(self):
        """Test sending message without execute flag (raw injection)."""
        print("Testing: Message without execute flag...")
        self.setup("test-raw")
        
        try:
            # Launch wrapper with echo command
            success = self.launch_wrapper(command=['echo'])
            assert success, "Failed to launch wrapper"
            
            # Send message without execute flag
            success = self.send_message("test message", execute=False)
            assert success, "Failed to send message"
            
            time.sleep(0.5)
            
            # Read stderr for injection confirmation
            stderr_output = self.wrapper_proc.stderr.readline()
            assert "[PTY Wrapper]" in stderr_output, f"Expected PTY wrapper message, got: {stderr_output}"
            
            print("✓ Message without execute flag successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Message without execute failed: {e}")
            return False
        finally:
            self.teardown()
    
    def test_execute_with_default_delimiter(self):
        """Test sending message with execute flag using wrapper's default delimiter."""
        print("Testing: Execute with default delimiter...")
        self.setup("test-exec-default")
        
        try:
            # Launch wrapper with \n delimiter
            success = self.launch_wrapper(delimiter="\\n")
            assert success, "Failed to launch wrapper"
            
            # Send message with execute flag (should use wrapper's delimiter)
            success = self.send_message("echo 'executed'", execute=True)
            assert success, "Failed to send message"
            
            time.sleep(0.5)
            
            # Read stderr for execution confirmation
            stderr_output = self.wrapper_proc.stderr.readline()
            assert "Executing command from" in stderr_output or "[PTY Wrapper]" in stderr_output, f"Expected execution message, got: {stderr_output}"
            
            print("✓ Execute with default delimiter successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Execute with default delimiter failed: {e}")
            return False
        finally:
            self.teardown()
    
    def test_execute_with_override_delimiter(self):
        """Test sending message with custom delimiter override."""
        print("Testing: Execute with override delimiter...")
        self.setup("test-exec-override")
        
        try:
            # Launch wrapper with \n delimiter
            success = self.launch_wrapper(delimiter="\\n")
            assert success, "Failed to launch wrapper"
            
            # Send message with execute flag and custom delimiter
            success = self.send_message("test", execute=True, delimiter="\\r\\n")
            assert success, "Failed to send message"
            
            time.sleep(0.5)
            
            # Read stderr for execution confirmation
            stderr_output = self.wrapper_proc.stderr.readline()
            assert "Executing command from" in stderr_output or "[PTY Wrapper]" in stderr_output, f"Expected execution message, got: {stderr_output}"
            
            print("✓ Execute with override delimiter successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Execute with override delimiter failed: {e}")
            return False
        finally:
            self.teardown()
    
    def test_multiple_delimiter_types(self):
        """Test different delimiter types."""
        print("Testing: Multiple delimiter types...")
        
        delimiters = ["\\n", "\\r\\n", "\\n\\n"]
        
        for delim in delimiters:
            self.setup(f"test-delim-{delim.replace('\\', '')}")
            
            try:
                # Launch wrapper with specific delimiter
                success = self.launch_wrapper(delimiter=delim)
                assert success, f"Failed to launch wrapper with delimiter {delim}"
                
                # Send message with execute flag
                success = self.send_message("test", execute=True)
                assert success, f"Failed to send message with delimiter {delim}"
                
                time.sleep(0.2)
                
                print(f"  ✓ Delimiter {repr(delim)} works")
                
            except AssertionError as e:
                print(f"  ✗ Delimiter {repr(delim)} failed: {e}")
                return False
            finally:
                self.teardown()
        
        print("✓ Multiple delimiter types successful")
        return True
    
    def run_all_tests(self):
        """Run all tests and report results."""
        print("=" * 60)
        print("CI Terminal Delimiter Tests")
        print("=" * 60)
        
        tests = [
            self.test_launch_with_delimiter,
            self.test_execute_without_delimiter,
            self.test_execute_with_default_delimiter,
            self.test_execute_with_override_delimiter,
            self.test_multiple_delimiter_types
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
            
            print()
        
        print("=" * 60)
        print(f"Results: {passed} passed, {failed} failed")
        print("=" * 60)
        
        return failed == 0


def main():
    """Main test runner."""
    tester = TestCITerminalDelimiter()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()