#!/usr/bin/env python3
"""
Full test of delimiter functionality with Python interpreter
"""

import sys
import os
import time
import subprocess

def test_python_execution():
    """Test sending Python code with proper delimiters."""
    
    print("Testing Python code execution with delimiters")
    print("=" * 60)
    
    # Launch Python interpreter in ci-tool
    print("\n1. Launching Python interpreter in ci-tool...")
    proc = subprocess.Popen(
        [sys.executable, 'shared/aish/aish', 'ci-tool', '-n', 'test-python', '-d', '\\n\\n', '--', 
         sys.executable, '-u', '-i'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for Python prompt
    time.sleep(2)
    
    # Check if socket exists
    socket_path = '/tmp/ci_msg_test-python.sock'
    if not os.path.exists(socket_path):
        print("✗ Failed to create socket")
        proc.terminate()
        return
    
    print("✓ Python interpreter started")
    
    # Test cases
    test_cases = [
        ("print('Hello World')", "Hello World", "Simple print"),
        ("x = 5\\nprint(x * 2)", "10", "Multi-line with \\n"),
        ("for i in range(3):\\n    print(i)", "0\\n1\\n2", "Loop with indentation"),
    ]
    
    print("\n2. Testing code execution:")
    for code, expected, desc in test_cases:
        print(f"\n  Test: {desc}")
        print(f"  Code: {repr(code)}")
        
        # Send code with execute flag and newline delimiter
        result = subprocess.run(
            [sys.executable, 'shared/aish/aish', 'test-python', code, '-x', '\\n'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode != 0:
            print(f"  ✗ Failed to send: {result.stderr}")
            continue
        
        print(f"  ✓ Code sent")
        
        # Read output
        time.sleep(0.5)
        output_lines = []
        while True:
            try:
                import select
                ready = select.select([proc.stdout], [], [], 0.1)
                if ready[0]:
                    line = proc.stdout.readline()
                    if line and not line.startswith('>>>'):
                        output_lines.append(line.strip())
                else:
                    break
            except:
                break
        
        output = '\\n'.join(output_lines)
        if expected in output:
            print(f"  ✓ Got expected output: {expected}")
        else:
            print(f"  ✗ Expected '{expected}', got: {output}")
    
    # Test CRLF delimiter for Windows-style line endings
    print("\n3. Testing CRLF delimiter:")
    result = subprocess.run(
        [sys.executable, 'shared/aish/aish', 'test-python', "print('CRLF test')", '-x', '\\r\\n'],
        capture_output=True,
        text=True,
        timeout=2
    )
    
    if result.returncode == 0:
        print("  ✓ CRLF delimiter accepted")
    else:
        print("  ✗ CRLF delimiter failed")
    
    # Cleanup
    print("\n4. Cleanup...")
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except:
        proc.kill()
    
    if os.path.exists(socket_path):
        os.unlink(socket_path)
    
    print("✓ Test complete")
    print("=" * 60)

if __name__ == "__main__":
    test_python_execution()