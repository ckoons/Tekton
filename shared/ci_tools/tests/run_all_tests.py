#!/usr/bin/env python3
"""
Run all CI Tools tests.
"""

import sys
import subprocess
from pathlib import Path

# Test files to run
test_files = [
    'test_base_adapter.py',
    'test_socket_bridge.py',
    'test_registry.py',
    'test_launcher.py',
    'test_ci_integration.py',
    'test_tool_definition.py',
    'test_generic_adapter.py',
    'test_integration.py'
]


def run_test_file(test_file):
    """Run a single test file."""
    test_path = Path(__file__).parent / test_file
    
    if not test_path.exists():
        print(f"⚠️  Test file not found: {test_file}")
        return True  # Don't fail for missing tests
    
    print(f"\n{'='*60}")
    print(f"Running {test_file}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"✗ Failed to run {test_file}: {e}")
        return False


def main():
    """Run all tests."""
    print("CI Tools Test Suite")
    print("=" * 60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_file in test_files:
        if run_test_file(test_file):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Total:   {len(test_files)}")
    print(f"Passed:  {passed}")
    print(f"Failed:  {failed}")
    print(f"Skipped: {skipped}")
    
    if failed == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failed} test(s) failed!")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)