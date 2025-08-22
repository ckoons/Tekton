#!/usr/bin/env python3
"""
Test runner for Construct system tests.
"""

import subprocess
import sys
from pathlib import Path

def run_test(test_file):
    """Run a test file and return success status."""
    print(f"\n{'='*60}")
    print(f"Running {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run([
            sys.executable, test_file
        ], cwd=Path(__file__).parent.parent, capture_output=False)
        
        if result.returncode == 0:
            print(f"✅ {test_file} PASSED")
            return True
        else:
            print(f"❌ {test_file} FAILED (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"❌ {test_file} ERROR: {e}")
        return False

def main():
    """Run all construct tests."""
    test_dir = Path(__file__).parent / "construct"
    
    # Setup test data first
    print("Setting up test data...")
    setup_result = run_test(test_dir / "setup_test_data.py")
    if not setup_result:
        print("❌ Test setup failed, aborting...")
        sys.exit(1)
    
    # Run tests
    tests = [
        "test_integration.py",
        "test_construct_system.py",
        "test_sandbox_solution.py"
    ]
    
    results = {}
    for test in tests:
        test_path = test_dir / test
        if test_path.exists():
            results[test] = run_test(test_path)
        else:
            print(f"⚠️  {test} not found, skipping...")
            results[test] = None
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    for test, result in results.items():
        if result is True:
            print(f"✅ {test}")
        elif result is False:
            print(f"❌ {test}")
        else:
            print(f"⚠️  {test} (skipped)")
    
    print(f"\nPassed: {passed}, Failed: {failed}, Skipped: {skipped}")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("🎉 All tests passed!")

if __name__ == "__main__":
    main()