#!/usr/bin/env python3
"""
Integration tests for CI wrapper delimiter functionality.
Tests end-to-end scenarios with real programs.
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


class TestCIWrapperIntegration:
    """Integration test suite for CI wrappers."""
    
    def __init__(self):
        self.processes = []
        self.temp_files = []
        
    def cleanup(self):
        """Clean up all test resources."""
        # Terminate all processes
        for proc in self.processes:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
        self.processes = []
        
        # Clean up temp files
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        self.temp_files = []
        
        # Clean up sockets
        for socket_file in Path('/tmp').glob('ci_msg_test*.sock'):
            try:
                socket_file.unlink()
            except:
                pass
    
    def launch_ci_terminal(self, name, delimiter=None, command='cat'):
        """Launch ci-terminal wrapper."""
        aish_path = Path(__file__).parent.parent.parent / 'aish' / 'aish'
        
        cmd = [sys.executable, str(aish_path), 'ci-terminal', '-n', name]
        if delimiter:
            cmd.extend(['-d', delimiter])
        cmd.extend(['--', command])
        
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes.append(proc)
        
        # Wait for socket
        socket_path = f"/tmp/ci_msg_{name}.sock"
        for _ in range(30):  # 3 seconds
            if os.path.exists(socket_path):
                time.sleep(0.2)  # Extra time for socket to be ready
                return proc
            time.sleep(0.1)
        
        return None
    
    def launch_ci_tool(self, name, delimiter=None, command=None):
        """Launch ci-tool wrapper."""
        aish_path = Path(__file__).parent.parent.parent / 'aish' / 'aish'
        
        if command is None:
            command = ['cat']
        
        cmd = [sys.executable, str(aish_path), 'ci-tool', '-n', name]
        if delimiter:
            cmd.extend(['-d', delimiter])
        cmd.append('--')
        cmd.extend(command)
        
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes.append(proc)
        
        # Wait for socket
        socket_path = f"/tmp/ci_msg_{name}.sock"
        for _ in range(30):  # 3 seconds
            if os.path.exists(socket_path):
                time.sleep(0.2)
                return proc
            time.sleep(0.1)
        
        return None
    
    def send_via_aish(self, ci_name, message, execute=False, delimiter=None):
        """Send message via aish command."""
        aish_path = Path(__file__).parent.parent.parent / 'aish' / 'aish'
        
        cmd = [sys.executable, str(aish_path), ci_name, message]
        if execute:
            cmd.append('-x')
            if delimiter:
                cmd.append(delimiter)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return result.returncode == 0, result.stdout, result.stderr
    
    def test_echo_with_execute(self):
        """Test echo command with execute flag."""
        print("Testing: Echo with execute flag...")
        
        try:
            # Launch ci-tool with echo
            proc = self.launch_ci_tool('test-echo', delimiter='\\n', command=['echo', 'Ready'])
            assert proc is not None, "Failed to launch ci-tool"
            
            # Wait for initial output
            time.sleep(0.5)
            initial_output = proc.stdout.readline()
            assert 'Ready' in initial_output, "Echo not ready"
            
            # Send message with execute
            success, stdout, stderr = self.send_via_aish('test-echo', 'Hello World', execute=True)
            assert success, f"Failed to send message: {stderr}"
            
            time.sleep(0.5)
            
            # Check output
            output = proc.stdout.readline()
            assert 'Hello World' in output, f"Expected 'Hello World', got: {output}"
            
            print("✓ Echo with execute successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Echo with execute failed: {e}")
            return False
        finally:
            self.cleanup()
    
    def test_python_code_execution(self):
        """Test Python code execution with delimiter."""
        print("Testing: Python code execution...")
        
        try:
            # Create a simple Python script that reads and executes
            script = """
import sys
while True:
    try:
        line = input()
        if line.strip():
            exec(line)
            sys.stdout.flush()
    except EOFError:
        break
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.stderr.flush()
"""
            script_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
            script_file.write(script)
            script_file.close()
            self.temp_files.append(script_file.name)
            
            # Launch ci-tool with Python script
            proc = self.launch_ci_tool(
                'test-python',
                delimiter='\\n',
                command=[sys.executable, '-u', script_file.name]
            )
            assert proc is not None, "Failed to launch Python ci-tool"
            
            # Send Python code with execute
            success, stdout, stderr = self.send_via_aish(
                'test-python',
                "print('Hello from Python')",
                execute=True
            )
            assert success, f"Failed to send Python code: {stderr}"
            
            time.sleep(0.5)
            
            # Check output
            output = proc.stdout.readline()
            assert 'Hello from Python' in output, f"Expected Python output, got: {output}"
            
            print("✓ Python code execution successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Python code execution failed: {e}")
            return False
        finally:
            self.cleanup()
    
    def test_background_execution(self):
        """Test background execution with &."""
        print("Testing: Background execution...")
        
        try:
            # Launch in background using shell
            aish_path = Path(__file__).parent.parent.parent / 'aish' / 'aish'
            cmd = f"{sys.executable} {aish_path} ci-tool -n test-bg -d '\\n' -- echo 'Background' &"
            
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it time to start
            time.sleep(1)
            
            # Check if socket exists (indicates it's running in background)
            socket_path = "/tmp/ci_msg_test-bg.sock"
            assert os.path.exists(socket_path), "Background process didn't create socket"
            
            # Send a message to it
            success, stdout, stderr = self.send_via_aish('test-bg', 'test', execute=True)
            
            # Clean up background process
            subprocess.run(['pkill', '-f', 'ci_msg_test-bg'], capture_output=True)
            
            print("✓ Background execution successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Background execution failed: {e}")
            return False
        finally:
            # Extra cleanup for background process
            subprocess.run(['pkill', '-f', 'ci_msg_test-bg'], capture_output=True)
            if os.path.exists("/tmp/ci_msg_test-bg.sock"):
                os.unlink("/tmp/ci_msg_test-bg.sock")
    
    def test_output_redirection(self):
        """Test output redirection with pipes."""
        print("Testing: Output redirection...")
        
        try:
            # Create temp file for output
            output_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
            output_file.close()
            self.temp_files.append(output_file.name)
            
            # Launch with output redirection
            aish_path = Path(__file__).parent.parent.parent / 'aish' / 'aish'
            cmd = [
                sys.executable, str(aish_path),
                'ci-tool', '-n', 'test-redirect', '-d', '\\n',
                '--', 'echo', 'Initial'
            ]
            
            with open(output_file.name, 'w') as outfile:
                proc = subprocess.Popen(
                    cmd,
                    stdout=outfile,
                    stderr=subprocess.DEVNULL,
                    text=True
                )
                self.processes.append(proc)
            
            # Wait for startup
            time.sleep(1)
            
            # Send message
            success, stdout, stderr = self.send_via_aish('test-redirect', 'Redirected', execute=True)
            
            time.sleep(0.5)
            
            # Check output file
            with open(output_file.name, 'r') as f:
                content = f.read()
                assert 'Initial' in content, f"Missing initial output in: {content}"
                assert 'Redirected' in content, f"Missing redirected output in: {content}"
            
            print("✓ Output redirection successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Output redirection failed: {e}")
            return False
        finally:
            self.cleanup()
    
    def test_delimiter_chain(self):
        """Test chaining messages with different delimiters."""
        print("Testing: Delimiter chain...")
        
        try:
            # Launch wrapper with newline delimiter
            proc = self.launch_ci_tool('test-chain', delimiter='\\n', command=['cat'])
            assert proc is not None, "Failed to launch ci-tool"
            
            # Send with default delimiter
            success, stdout, stderr = self.send_via_aish('test-chain', 'Line1', execute=True)
            assert success, "Failed to send first message"
            
            # Send with custom delimiter
            success, stdout, stderr = self.send_via_aish('test-chain', 'Line2', execute=True, delimiter='\\r\\n')
            assert success, "Failed to send second message"
            
            # Send without execute (raw)
            success, stdout, stderr = self.send_via_aish('test-chain', 'Line3', execute=False)
            assert success, "Failed to send third message"
            
            time.sleep(1)
            
            # Read all output
            output_lines = []
            while True:
                import select
                ready = select.select([proc.stdout], [], [], 0.1)
                if ready[0]:
                    line = proc.stdout.readline()
                    if line:
                        output_lines.append(line.strip())
                    else:
                        break
                else:
                    break
            
            # Verify we got different types of output
            assert 'Line1' in ' '.join(output_lines), "Missing Line1"
            assert 'Line2' in ' '.join(output_lines), "Missing Line2"
            
            print("✓ Delimiter chain successful")
            return True
            
        except AssertionError as e:
            print(f"✗ Delimiter chain failed: {e}")
            return False
        finally:
            self.cleanup()
    
    def run_all_tests(self):
        """Run all integration tests."""
        print("=" * 60)
        print("CI Wrapper Integration Tests")
        print("=" * 60)
        
        tests = [
            self.test_echo_with_execute,
            self.test_python_code_execution,
            self.test_background_execution,
            self.test_output_redirection,
            self.test_delimiter_chain
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
    tester = TestCIWrapperIntegration()
    try:
        success = tester.run_all_tests()
    finally:
        tester.cleanup()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()