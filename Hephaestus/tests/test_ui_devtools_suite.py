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
    
    tests = [
        ("test_devtools_practice_workflow.py", "Basic DevTools Workflow Test"),
        ("test_ui_screenshot_tools.py", "Screenshot Tools Test (Phase 4)"),
        ("test_ui_workflow.py", "New ui_workflow Tool Test"),
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