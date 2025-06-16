#!/usr/bin/env python3
"""
Run only unit tests for A2A Protocol v0.2.1
"""

import os
import sys
import subprocess

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Unit test suites only
test_suites = {
    "Unit Tests - JSON-RPC": "tests/unit/a2a/test_jsonrpc_messages.py",
    "Unit Tests - Agent Cards": "tests/unit/a2a/test_agent_cards.py", 
    "Unit Tests - Task Lifecycle": "tests/unit/a2a/test_task_lifecycle.py",
    "Unit Tests - Discovery": "tests/unit/a2a/test_discovery.py"
}

def run_tests():
    """Run unit tests"""
    print("=" * 80)
    print("Running A2A Protocol v0.2.1 Unit Tests")
    print("=" * 80)
    print()
    
    all_passed = True
    results = {}
    
    for suite_name, test_path in test_suites.items():
        print(f"\n{suite_name}")
        print("-" * len(suite_name))
        
        # Run pytest
        cmd = [
            sys.executable, "-m", "pytest",
            test_path,
            "-v",
            "--tb=short"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PASSED")
            results[suite_name] = "PASSED"
        else:
            print("❌ FAILED")
            results[suite_name] = "FAILED"
            all_passed = False
            
            # Extract summary line
            lines = result.stdout.split('\n')
            for line in lines:
                if 'failed' in line and 'passed' in line:
                    print(f"   {line.strip()}")
                    break
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for suite, status in results.items():
        status_icon = "✅" if status == "PASSED" else "❌"
        print(f"{status_icon} {suite}: {status}")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL UNIT TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)