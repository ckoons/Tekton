#!/usr/bin/env python3
"""
Comprehensive test for CI wrapper functionality.
Tests the complete message flow without guessing.
"""

import os
import sys
import subprocess
import socket
import json
import time
import threading
from pathlib import Path

class CIWrapperTest:
    def __init__(self):
        self.test_name = "test-wrapper"
        self.socket_path = f"/tmp/ci_msg_{self.test_name}.sock"
        self.wrapper_process = None
        self.output_buffer = []
        
    def cleanup(self):
        """Clean up any existing test artifacts"""
        if self.wrapper_process:
            self.wrapper_process.terminate()
            self.wrapper_process.wait()
        if os.path.exists(self.socket_path):
            try:
                os.unlink(self.socket_path)
            except:
                pass
                
    def start_wrapper(self, use_pty=True, os_injection='auto'):
        """Start a test wrapper"""
        print(f"\n[TEST] Starting wrapper (pty={use_pty}, os_injection={os_injection})")
        
        # Choose wrapper type
        if use_pty:
            wrapper_script = str(Path(__file__).parent / 'ci_pty_wrapper.py')
        else:
            wrapper_script = str(Path(__file__).parent / 'ci_simple_wrapper.py')
        
        # Build command
        cmd = [
            sys.executable, wrapper_script,
            '--name', self.test_name,
            '--os-injection', os_injection,
            '--', 'cat'  # Use cat as a simple echo program
        ]
        
        print(f"[TEST] Command: {' '.join(cmd)}")
        
        # Start the wrapper
        self.wrapper_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True
        )
        
        # Start output readers
        def read_output(pipe, label):
            for line in pipe:
                self.output_buffer.append(f"[{label}] {line.strip()}")
                print(f"[{label}] {line.strip()}")
        
        threading.Thread(target=read_output, args=(self.wrapper_process.stdout, "STDOUT"), daemon=True).start()
        threading.Thread(target=read_output, args=(self.wrapper_process.stderr, "STDERR"), daemon=True).start()
        
        # Wait for socket to be created
        for i in range(10):
            if os.path.exists(self.socket_path):
                print(f"[TEST] Socket created: {self.socket_path}")
                return True
            time.sleep(0.5)
        
        print(f"[TEST] ERROR: Socket not created after 5 seconds")
        return False
        
    def send_message(self, content, execute=False, delimiter=None, os_injection=None):
        """Send a message to the wrapper"""
        print(f"\n[TEST] Sending message: content='{content}', execute={execute}, delimiter={repr(delimiter)}, os_injection={os_injection}")
        
        msg = {
            'from': 'test_script',
            'content': content,
            'execute': execute
        }
        
        if delimiter is not None:
            msg['delimiter'] = delimiter
        if os_injection is not None:
            msg['os_injection'] = os_injection
            
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
            sock.send(json.dumps(msg).encode('utf-8'))
            sock.close()
            print("[TEST] Message sent successfully")
            return True
        except Exception as e:
            print(f"[TEST] ERROR sending message: {e}")
            return False
            
    def wait_for_output(self, expected, timeout=2):
        """Wait for expected output"""
        start = time.time()
        while time.time() - start < timeout:
            for line in self.output_buffer:
                if expected in line:
                    print(f"[TEST] Found expected output: {expected}")
                    return True
            time.sleep(0.1)
        print(f"[TEST] Timeout waiting for: {expected}")
        return False
        
    def run_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("CI WRAPPER COMPREHENSIVE TEST")
        print("=" * 60)
        
        all_passed = True
        
        # Test 1: PTY wrapper with simple message
        print("\n### Test 1: PTY wrapper with notification message")
        self.cleanup()
        if self.start_wrapper(use_pty=True, os_injection='off'):
            if self.send_message("Test notification", execute=False):
                if self.wait_for_output("Message from test_script"):
                    print("[TEST] ✓ Test 1 passed")
                else:
                    print("[TEST] ✗ Test 1 failed - no output")
                    all_passed = False
            else:
                print("[TEST] ✗ Test 1 failed - send failed")
                all_passed = False
        else:
            print("[TEST] ✗ Test 1 failed - wrapper didn't start")
            all_passed = False
            
        # Test 2: PTY wrapper with execute
        print("\n### Test 2: PTY wrapper with execute message")
        self.cleanup()
        if self.start_wrapper(use_pty=True, os_injection='off'):
            if self.send_message("echo test", execute=True, delimiter="\n"):
                time.sleep(0.5)
                # Check if 'echo test' appears in output (cat should echo it back)
                if self.wait_for_output("echo test"):
                    print("[TEST] ✓ Test 2 passed")
                else:
                    print("[TEST] ✗ Test 2 failed - no echo")
                    all_passed = False
            else:
                print("[TEST] ✗ Test 2 failed - send failed")
                all_passed = False
        else:
            print("[TEST] ✗ Test 2 failed - wrapper didn't start")
            all_passed = False
            
        # Test 3: Simple wrapper
        print("\n### Test 3: Simple wrapper with execute message")
        self.cleanup()
        if self.start_wrapper(use_pty=False, os_injection='off'):
            if self.send_message("simple test", execute=True, delimiter="\n"):
                time.sleep(0.5)
                if self.wait_for_output("simple test"):
                    print("[TEST] ✓ Test 3 passed")
                else:
                    print("[TEST] ✗ Test 3 failed - no output")
                    all_passed = False
            else:
                print("[TEST] ✗ Test 3 failed - send failed")
                all_passed = False
        else:
            print("[TEST] ✗ Test 3 failed - wrapper didn't start")
            all_passed = False
            
        # Clean up
        self.cleanup()
        
        print("\n" + "=" * 60)
        if all_passed:
            print("ALL TESTS PASSED ✓")
        else:
            print("SOME TESTS FAILED ✗")
        print("=" * 60)
        
        return all_passed

def test_imports():
    """Test that all required modules can be imported"""
    print("\n### Testing imports")
    try:
        # Test OS injection module
        sys.path.insert(0, str(Path(__file__).parent))
        from os_injection import OSInjector, inject_message_with_delimiter
        print("[TEST] ✓ os_injection imports correctly")
        
        # Test window detector
        from window_detector import get_terminal_window_info
        print("[TEST] ✓ window_detector imports correctly")
        
        # Test registry
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from shared.aish.src.registry.ci_registry import get_registry
        print("[TEST] ✓ ci_registry imports correctly")
        
        return True
    except ImportError as e:
        print(f"[TEST] ✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # First test imports
    if not test_imports():
        print("\n[TEST] Cannot proceed - import errors must be fixed first")
        sys.exit(1)
    
    # Run wrapper tests
    tester = CIWrapperTest()
    success = tester.run_tests()
    sys.exit(0 if success else 1)