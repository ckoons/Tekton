#!/usr/bin/env python3
"""
Quick script to add a test solution to Registry and test it in Sandbox.
Run this after Ergon is started.
"""

import requests
import json
import time

ERGON_URL = "http://localhost:8102"

# Test solution that prints system info
test_solution = {
    "type": "solution",
    "name": "System Info Checker",
    "version": "1.0.0",
    "content": {
        "description": "Prints system information to verify sandbox isolation",
        "code": """
import os
import sys
import platform
import socket
import pwd

print("=== Sandbox Test Solution ===")
print(f"Python Version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Hostname: {socket.gethostname()}")
print(f"Current User: {pwd.getpwuid(os.getuid()).pw_name}")
print(f"Working Directory: {os.getcwd()}")
print(f"Environment Sandbox ID: {os.environ.get('SANDBOX_ID', 'Not set')}")

# List workspace contents
print("\\n=== Workspace Contents ===")
for item in os.listdir('.'):
    print(f"  - {item}")

# Try to write a file (should work in workspace)
try:
    with open('test_output.txt', 'w') as f:
        f.write("Successfully wrote to workspace!")
    print("\\n✓ File write successful")
except Exception as e:
    print(f"\\n✗ File write failed: {e}")

# Try to read home directory (should fail in sandbox-exec)
print("\\n=== Testing Isolation ===")
try:
    home_contents = os.listdir(os.path.expanduser('~'))
    print(f"⚠ WARNING: Can see home directory ({len(home_contents)} items)")
except Exception as e:
    print(f"✓ Home directory protected: {e}")

print("\\n=== Test Complete ===")
""",
        "main_file": "test.py",
        "run_command": ["python", "test.py"],
        "requires_network": False,
        "memory_limit": "512m"
    }
}

def main():
    print("Testing Ergon Sandbox System")
    print("=" * 40)
    
    # 1. Store the solution
    print("\n1. Adding test solution to Registry...")
    response = requests.post(
        f"{ERGON_URL}/api/ergon/registry/store",
        json=test_solution
    )
    
    if response.status_code != 200:
        print(f"Failed to store solution: {response.text}")
        return
    
    solution_id = response.json()["id"]
    print(f"   Solution stored with ID: {solution_id}")
    
    # 2. Start sandbox test
    print("\n2. Starting sandbox test...")
    response = requests.post(
        f"{ERGON_URL}/api/ergon/sandbox/test",
        json={
            "solution_id": solution_id,
            "timeout": 30
        }
    )
    
    if response.status_code != 200:
        print(f"Failed to start test: {response.text}")
        return
    
    sandbox_id = response.json()["sandbox_id"]
    print(f"   Sandbox created with ID: {sandbox_id}")
    
    # 3. Execute and stream output
    print("\n3. Executing solution...")
    response = requests.post(
        f"{ERGON_URL}/api/ergon/sandbox/execute",
        json={"sandbox_id": sandbox_id},
        stream=True
    )
    
    print("\n--- Output ---")
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8').replace('data: ', ''))
                if 'line' in data:
                    print(data['line'])
                elif 'done' in data:
                    break
            except:
                pass
    
    # 4. Get results
    print("\n4. Getting results...")
    time.sleep(1)  # Wait for execution to complete
    response = requests.get(f"{ERGON_URL}/api/ergon/sandbox/results/{sandbox_id}")
    
    if response.status_code == 200:
        results = response.json()
        print(f"   Status: {results['status']}")
        print(f"   Exit Code: {results.get('exit_code', 'N/A')}")
        print(f"   Execution Time: {results.get('execution_time', 'N/A')}s")
    
    # 5. Clean up
    print("\n5. Cleaning up sandbox...")
    response = requests.delete(f"{ERGON_URL}/api/ergon/sandbox/{sandbox_id}")
    print("   Sandbox cleaned up")
    
    print("\n" + "=" * 40)
    print("Test complete! Check the output above to see:")
    print("- Python version and platform (sandbox environment)")
    print("- Isolation verification (home directory protection)")
    print("- Workspace write capabilities")

if __name__ == "__main__":
    main()