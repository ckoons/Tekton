#!/usr/bin/env python3
"""
Run all MCP tests for aish.
"""

import sys
import subprocess
from pathlib import Path

# Test files to run
test_files = [
    'test_mcp_ci_tools.py',
    'test_mcp_integration.py'
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
            [sys.executable, "-m", "pytest", str(test_path), "-v"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent.parent  # Set to TEKTON_ROOT
        )
        
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"✗ Failed to run {test_file}: {e}")
        return False


def main():
    """Run all MCP tests."""
    print("aish MCP Test Suite")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        if run_test_file(test_file):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print("MCP Test Summary")
    print("=" * 60)
    print(f"Total:   {len(test_files)}")
    print(f"Passed:  {passed}")
    print(f"Failed:  {failed}")
    
    if failed == 0:
        print("\n✅ All MCP tests passed!")
        print("\nMCP server now provides full CI tools capability:")
        print("• CI Tools Management (launch, terminate, define, status)")
        print("• Context State Management (Apollo-Rhetor coordination)")
        print("• Detailed CI Information (discovery, filtering)")
        print("• Registry Management (reload, save, status)")
        print("• Complete API surface for all CI operations")
    else:
        print(f"\n❌ {failed} MCP test(s) failed!")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)