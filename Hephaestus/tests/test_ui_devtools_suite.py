#!/usr/bin/env python3
"""
UI DevTools Test Suite Runner
Runs all UI DevTools tests in sequence
"""
import subprocess
import sys
import os

def run_test(test_file: str, description: str):
    """Run a single test file"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"File: {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            print("✅ PASSED")
            print(result.stdout)
        else:
            print("❌ FAILED")
            print(result.stdout)
            print(result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all UI DevTools tests"""
    print("🧪 UI DevTools Test Suite")
    print("="*60)
    
    # V2 tests are in ui_dev_tools/tests/
    v2_test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui_dev_tools", "tests")
    tests = [
        (os.path.join(v2_test_dir, "test_code_reader.py"), "Code Reader Test (V2)"),
        (os.path.join(v2_test_dir, "test_browser_verifier.py"), "Browser Verifier Test (V2)"),
        (os.path.join(v2_test_dir, "test_comparator.py"), "Comparator Test (V2)"),
        (os.path.join(v2_test_dir, "test_navigator.py"), "Navigator Test (V2)"),
        (os.path.join(v2_test_dir, "test_safe_tester.py"), "Safe Tester Test (V2)"),
    ]
    
    passed = 0
    failed = 0
    
    for test_file, description in tests:
        if run_test(test_file, description):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Test Summary:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Total:  {len(tests)}")
    print('='*60)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())