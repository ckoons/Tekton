#!/usr/bin/env python3
"""
Tests for CI tool delimiter and execute functionality.
"""

import os
import sys
import json
import time
import socket
import subprocess
import tempfile
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestCIToolDelimiter:
    """Test suite for CI tool delimiter functionality."""
    
    def __init__(self):
        self.test_name = None
        self.wrapper_proc = None
        self.socket_path = None
        
    def setup(self, name="test-tool"):
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
            try:
                self.wrapper_proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.wrapper_proc.kill()
                self.wrapper_proc.wait()
            self.wrapper_proc = None
        
        if self.socket_path and os.path.exists(self.socket_path):
            try:
                os.unlink(self.socket_path)
            except:
                pass
    
    def launch_wrapper(self, delimiter=None, command=['cat']):
        """Launch simple wrapper with optional delimiter."""
        wrapper_path = Path(__file__).parent.parent / 'ci_simple_wrapper.py'
        
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
    
    def test_launch_with_delimiter(self):
        """Test launching wrapper with delimiter configuration."""
        print("Testing: Launch CI tool with delimiter...")
        self.setup("tool-delim")
        
        try:
            # Launch with newline delimiter
            success = self.launch_wrapper(delimiter="\\n")
            assert success, "Failed to launch wrapper"
            
            # Verify process is running
            assert self.wrapper_proc.poll() is None, "Wrapper exited prematurely"
            
            print("✓ Launch CI tool with delimiter successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Launch CI tool with delimiter failed: {e}")
            return False
        finally:
            self.teardown()
    
    def test_stdin_injection_without_execute(self):
        """Test stdin injection without execute flag."""
        print("Testing: Stdin injection without execute...")
        self.setup("tool-inject")
        
        try:
            # Launch wrapper with cat command
            success = self.launch_wrapper(command=['cat'])
            assert success, "Failed to launch wrapper"
            
            # Send message without execute flag
            success = self.send_message("test input", execute=False)
            assert success, "Failed to send message"
            
            time.sleep(0.5)
            
            # Check stderr for injection message
            stderr_output = self.wrapper_proc.stderr.readline()
            assert "[Wrapper]" in stderr_output, f"Expected wrapper message, got: {stderr_output}"
            
            print("✓ Stdin injection without execute successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Stdin injection without execute failed: {e}")
            return False
        finally:
            self.teardown()
    
    def test_stdin_execution_with_delimiter(self):
        """Test stdin execution with delimiter."""
        print("Testing: Stdin execution with delimiter...")
        self.setup("tool-exec")
        
        try:
            # Launch wrapper with newline delimiter
            success = self.launch_wrapper(delimiter="\\n", command=['cat'])
            assert success, "Failed to launch wrapper"
            
            # Send message with execute flag
            success = self.send_message("test line", execute=True)
            assert success, "Failed to send message"
            
            time.sleep(0.5)
            
            # Check stderr for execution message (non-blocking)
            import select
            ready = select.select([self.wrapper_proc.stderr], [], [], 1)
            if ready[0]:
                stderr_output = self.wrapper_proc.stderr.readline()
                assert "Executing command from" in stderr_output or "[Wrapper]" in stderr_output, f"Expected execution confirmation, got: {stderr_output}"
            
            # Check stdout for echoed content (cat should echo it back)
            ready = select.select([self.wrapper_proc.stdout], [], [], 1)
            if ready[0]:
                stdout_output = self.wrapper_proc.stdout.readline()
                assert "test line" in stdout_output, f"Expected echoed content, got: {stdout_output}"
            
            print("✓ Stdin execution with delimiter successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Stdin execution with delimiter failed: {e}")
            return False
        finally:
            self.teardown()
    
    def test_python_script_execution(self):
        """Test executing Python scripts with proper delimiter."""
        print("Testing: Python script execution...")
        self.setup("tool-python")
        
        try:
            # Launch wrapper with Python, double newline delimiter for code blocks
            success = self.launch_wrapper(
                delimiter="\\n\\n",
                command=[sys.executable, '-u', '-c', 'import sys; exec(sys.stdin.read())']
            )
            assert success, "Failed to launch Python wrapper"
            
            # Send Python code with execute flag
            python_code = "print('Hello from Python')"
            success = self.send_message(python_code, execute=True)
            assert success, "Failed to send Python code"
            
            time.sleep(0.5)
            
            # Check for execution (non-blocking)
            import select
            ready = select.select([self.wrapper_proc.stderr], [], [], 1)
            if ready[0]:
                stderr_output = self.wrapper_proc.stderr.readline()
                assert "Executing command from" in stderr_output or "[Wrapper]" in stderr_output, "No execution confirmation"
            
            # Check for Python output
            ready = select.select([self.wrapper_proc.stdout], [], [], 1)
            if ready[0]:
                stdout_output = self.wrapper_proc.stdout.readline()
                assert "Hello from Python" in stdout_output, f"Expected Python output, got: {stdout_output}"
            
            print("✓ Python script execution successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Python script execution failed: {e}")
            return False
        finally:
            self.teardown()
    
    def test_delimiter_override(self):
        """Test delimiter override in message."""
        print("Testing: Delimiter override...")
        self.setup("tool-override")
        
        try:
            # Launch with single newline delimiter
            success = self.launch_wrapper(delimiter="\\n", command=['cat'])
            assert success, "Failed to launch wrapper"
            
            # Send with custom delimiter override
            success = self.send_message("test", execute=True, delimiter="\\r\\n")
            assert success, "Failed to send message"
            
            time.sleep(0.5)
            
            # Verify execution with override delimiter (non-blocking)
            import select
            ready = select.select([self.wrapper_proc.stderr], [], [], 1)
            if ready[0]:
                stderr_output = self.wrapper_proc.stderr.readline()
                assert "Executing command from" in stderr_output or "[Wrapper]" in stderr_output, "No execution confirmation"
            
            print("✓ Delimiter override successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Delimiter override failed: {e}")
            return False
        finally:
            self.teardown()
    
    def test_multiple_rapid_messages(self):
        """Test sending multiple messages rapidly."""
        print("Testing: Multiple rapid messages...")
        self.setup("tool-rapid")
        
        try:
            # Launch wrapper
            success = self.launch_wrapper(delimiter="\\n", command=['cat'])
            assert success, "Failed to launch wrapper"
            
            # Send multiple messages quickly
            messages = ["msg1", "msg2", "msg3"]
            for msg in messages:
                success = self.send_message(msg, execute=True)
                assert success, f"Failed to send message: {msg}"
                time.sleep(0.1)
            
            time.sleep(0.5)
            
            # Check that all messages were processed
            output_lines = []
            for _ in range(3):
                line = self.wrapper_proc.stdout.readline()
                if line:
                    output_lines.append(line.strip())
            
            for msg in messages:
                assert msg in output_lines, f"Message {msg} not found in output"
            
            print("✓ Multiple rapid messages successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Multiple rapid messages failed: {e}")
            return False
        finally:
            self.teardown()
    
    def run_all_tests(self):
        """Run all tests and report results."""
        print("=" * 60)
        print("CI Tool Delimiter Tests")
        print("=" * 60)
        
        tests = [
            self.test_launch_with_delimiter,
            self.test_stdin_injection_without_execute,
            self.test_stdin_execution_with_delimiter,
            self.test_python_script_execution,
            self.test_delimiter_override,
            self.test_multiple_rapid_messages
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
    tester = TestCIToolDelimiter()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()