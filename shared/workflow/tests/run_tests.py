#!/usr/bin/env python3
"""
Run all workflow tests.

This script runs the complete test suite for the workflow handler.
"""

import os
import sys
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Run all tests."""
    print("=" * 60)
    print("Running Workflow Handler Test Suite")
    print("=" * 60)
    
    # Get test directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run all tests with coverage if available
    args = [
        test_dir,
        "-v",  # Verbose
        "--tb=short",  # Short traceback format
    ]
    
    # Try to add coverage if available
    try:
        import pytest_cov
        args.extend([
            "--cov=workflow_handler",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
        print("Running with coverage reporting...")
    except ImportError:
        print("Coverage not available. Install pytest-cov for coverage reports.")
    
    print("\nRunning tests...\n")
    
    # Run pytest
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())