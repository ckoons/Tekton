#!/usr/bin/env python3
"""
Integration tests for aish command-line tool.
Tests both direct messages and team chat.
"""

import subprocess
import sys
import time
import json

class AishTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def run_aish_command(self, command: str, timeout: int = 30) -> tuple[int, str, str]:
        """Run an aish command and return (returncode, stdout, stderr)"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout}s"
    
    def test(self, name: str, command: str, check_fn=None, timeout: int = 30):
        """Run a test"""
        print(f"\nTesting: {name}")
        print(f"Command: {command}")
        
        start_time = time.time()
        returncode, stdout, stderr = self.run_aish_command(command, timeout)
        elapsed = time.time() - start_time
        
        # Default check: command succeeded and has output
        if check_fn is None:
            success = returncode == 0 and len(stdout.strip()) > 0
        else:
            success = check_fn(returncode, stdout, stderr)
        
        if success:
            self.passed += 1
            print(f"✓ PASSED ({elapsed:.1f}s)")
            if stdout:
                print(f"  Output preview: {stdout[:100]}...")
        else:
            self.failed += 1
            print(f"✗ FAILED ({elapsed:.1f}s)")
            print(f"  Return code: {returncode}")
            if stderr:
                print(f"  Error: {stderr[:200]}")
            if not stdout:
                print("  No output received")
        
        self.tests.append({
            "name": name,
            "command": command,
            "success": success,
            "elapsed": elapsed,
            "returncode": returncode
        })
        
        return success
    
    def summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print(f"Test Summary: {self.passed}/{self.passed + self.failed} passed")
        print("="*60)
        
        if self.failed > 0:
            print("\nFailed tests:")
            for test in self.tests:
                if not test["success"]:
                    print(f"  - {test['name']} (code: {test['returncode']})")
        
        print(f"\nTotal time: {sum(t['elapsed'] for t in self.tests):.1f}s")
        return self.failed == 0

def main():
    tester = AishTester()
    
    print("="*60)
    print("AISH Integration Test Suite")
    print("="*60)
    
    # Test 1: Direct message to Apollo
    tester.test(
        "Direct message to Apollo",
        'aish apollo "What is code quality?"',
        timeout=30
    )
    
    # Test 2: Direct message to Numa
    tester.test(
        "Direct message to Numa", 
        'aish numa "How do you manage CI models?"',
        timeout=30
    )
    
    # Test 3: Pipeline test
    tester.test(
        "Pipeline: Echo to Apollo",
        'echo "analyze this code: def foo(): pass" | aish apollo',
        timeout=30
    )
    
    # Test 4: List CIs
    def check_list(rc, out, err):
        return rc == 0 and "Available CI Specialists" in out
    
    tester.test(
        "List available CIs",
        'aish list-cis',
        check_fn=check_list,
        timeout=10
    )
    
    # Test 5: Team chat (with shorter timeout)
    def check_team_chat(rc, out, err):
        # Success if we get any response or timeout (team chat can be slow)
        return "Team responses:" in out or "Broadcasting to team" in out
    
    tester.test(
        "Team chat broadcast",
        'aish team-chat "Quick status check"',
        check_fn=check_team_chat,
        timeout=45  # Give team chat more time
    )
    
    # Test 6: Multiple sequential messages
    print("\n--- Testing message sequencing ---")
    success = True
    for i in range(3):
        if not tester.test(
            f"Sequential message {i+1}",
            f'aish apollo "test message {i+1}"',
            timeout=20
        ):
            success = False
            break
    
    # Test 7: Error handling
    def check_error(rc, out, err):
        # Should fail gracefully
        return rc != 0 or "not found" in out.lower() or "not found" in err.lower()
    
    tester.test(
        "Error handling - invalid AI",
        'aish nonexistent-ci "test"',
        check_fn=check_error,
        timeout=10
    )
    
    # Summary
    return tester.summary()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)