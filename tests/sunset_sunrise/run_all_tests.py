#!/usr/bin/env python3
"""
Run all sunset/sunrise tests.
Comprehensive test suite for the Apollo/Rhetor consciousness management system.
"""

import sys
import asyncio
import subprocess
from pathlib import Path

# Add path to Tekton root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def run_test(test_file: str, description: str) -> bool:
    """Run a single test file."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Check if test passed
        if result.returncode == 0:
            # Look for success indicators in output (or verification script success)
            if ("All tests passed" in result.stdout or 
                "PASSED" in result.stdout or
                "Registry ready for production use" in result.stdout):
                print(f"✅ {description}: PASSED")
                return True
        
        # Test failed - show output
        print(f"❌ {description}: FAILED")
        print("\nOutput:")
        print(result.stdout)
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
        return False
        
    except subprocess.TimeoutExpired:
        print(f"❌ {description}: TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False


async def main():
    """Run all sunset/sunrise tests."""
    
    print("🌅 Sunset/Sunrise Test Suite 🌄")
    print("="*60)
    print("Testing the Apollo/Rhetor consciousness management system")
    print("="*60)
    
    test_dir = Path(__file__).parent
    
    tests = [
        ("test_registry_sunset_sunrise.py", "Registry Operations"),
        ("test_sunset_sunrise_integration.py", "Full Integration"),
        ("verify_sunset_sunrise.py", "Status Verification")
    ]
    
    results = []
    
    for test_file, description in tests:
        test_path = test_dir / test_file
        if test_path.exists():
            passed = run_test(str(test_path), description)
            results.append((description, passed))
        else:
            print(f"⚠️ Test file not found: {test_file}")
            results.append((description, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name:<30} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 ALL SUNSET/SUNRISE TESTS PASSED! 🎉")
        print("\nThe consciousness management system is fully operational:")
        print("  • Registry state management ✅")
        print("  • Apollo orchestration ✅")
        print("  • Rhetor monitoring ✅")
        print("  • Claude integration ✅")
        print("  • Thread safety ✅")
        print("  • Persistence ✅")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))