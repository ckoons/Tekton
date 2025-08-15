#!/usr/bin/env python3
"""
Test escape sequence interpretation for delimiters
"""

import sys
import os
import json
import time
import socket
import subprocess
import tempfile

def test_escape_interpretation():
    """Test that escape sequences are properly interpreted."""
    
    print("Testing escape sequence interpretation...")
    print("=" * 60)
    
    # Test 1: Test Python interpretation
    test_strings = [
        ('\\n', '\n', 'newline'),
        ('\\r\\n', '\r\n', 'CRLF'),
        ('\\t', '\t', 'tab'),
        ('\\\\n', '\\n', 'literal backslash-n'),
    ]
    
    print("\n1. Python string interpretation:")
    for raw, expected, desc in test_strings:
        try:
            decoded = raw.encode('utf-8').decode('unicode_escape')
            matches = decoded == expected
            print(f"  {raw:8} -> {repr(decoded):8} [{desc}] {'✓' if matches else '✗'}")
        except Exception as e:
            print(f"  {raw:8} -> ERROR: {e}")
    
    # Test 2: Test aish with execute flag
    print("\n2. Testing aish -x flag with different delimiters:")
    
    # Create a test script that shows what it receives
    test_script = """
import sys
import json
line = sys.stdin.readline()
# Show the bytes we received
print(f"Received bytes: {line.encode('utf-8')}")
print(f"Received repr: {repr(line)}")
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        script_path = f.name
    
    try:
        # Launch a ci-tool to test with
        print("\n  Launching test ci-tool...")
        proc = subprocess.Popen(
            [sys.executable, 'shared/aish/aish', 'ci-tool', '-n', 'test-escape', '--', 
             sys.executable, '-u', script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for socket
        socket_path = '/tmp/ci_msg_test-escape.sock'
        for _ in range(30):
            if os.path.exists(socket_path):
                break
            time.sleep(0.1)
        
        if not os.path.exists(socket_path):
            print("  ✗ Failed to create socket")
            return
        
        time.sleep(0.5)
        
        # Test different delimiters
        test_cases = [
            ('\\n', 'newline'),
            ('\\r\\n', 'CRLF'),
            ('\\t', 'tab'),
        ]
        
        for delimiter, desc in test_cases:
            print(f"\n  Testing {desc} delimiter: {repr(delimiter)}")
            
            # Send message with delimiter
            result = subprocess.run(
                [sys.executable, 'shared/aish/aish', 'test-escape', 'test', '-x', delimiter],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                print(f"    Message sent successfully")
            else:
                print(f"    Failed to send: {result.stderr}")
            
            # Read output
            time.sleep(0.5)
            output = proc.stdout.readline()
            if output:
                print(f"    Script output: {output.strip()}")
                # Check if the right delimiter was received
                if delimiter == '\\n' and 'b\'test\\\\n\'' in output:
                    print(f"    ✓ Correct newline received")
                elif delimiter == '\\r\\n' and 'b\'test\\\\r\\\\n\'' in output:
                    print(f"    ✓ Correct CRLF received")
                elif delimiter == '\\t' and 'b\'test\\\\t\'' in output:
                    print(f"    ✓ Correct tab received")
        
    finally:
        # Cleanup
        if 'proc' in locals():
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except:
                proc.kill()
        
        if os.path.exists(socket_path):
            os.unlink(socket_path)
        
        if os.path.exists(script_path):
            os.unlink(script_path)
    
    print("\n" + "=" * 60)
    print("Test complete")

if __name__ == "__main__":
    test_escape_interpretation()