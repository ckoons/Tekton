#!/usr/bin/env python3
"""
Test command handler for aish
Runs functional tests for aish commands
"""

import sys
from pathlib import Path

# Add landmarks
try:
    from landmarks import architecture_decision, integration_point, api_contract, state_checkpoint
except ImportError:
    # Landmarks not available, create no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator


@architecture_decision(
    title="Functional Test Framework",
    description="Simple command-line testing without mocks for real-world validation",
    rationale="Functional tests ensure commands work as users experience them",
    alternatives_considered=["Unit tests with mocks", "Integration test framework", "External test suite"],
    impacts=["reliability", "user confidence", "development workflow"],
    decided_by="Casey",
    decision_date="2025-01-24"
)
def handle_test_command(args=None) -> bool:
    """Handle the aish test command"""
    
    if not args:
        args = []
    
    # Handle help
    if args and args[0] == "help":
        print_test_help()
        return True
    
    # Add test directory to path
    test_dir = Path(__file__).parent.parent.parent / "tests"
    sys.path.insert(0, str(test_dir.parent))
    
    try:
        from tests.test_runner import run_all_tests
        
        # Parse arguments
        verbose = "-v" in args or "--verbose" in args
        suite_name = None
        
        # Find suite name (first non-flag argument)
        for arg in args:
            if not arg.startswith("-"):
                suite_name = arg
                break
        
        # Run tests
        success = run_all_tests(verbose=verbose, suite_name=suite_name)
        return success
        
    except ImportError as e:
        print(f"Error: Could not load test framework: {e}")
        print(f"Make sure test files exist in: {test_dir}")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def print_test_help():
    """Print detailed test help"""
    print("aish Test Framework")
    print("=" * 60)
    print()
    print("Run functional tests for aish commands")
    print()
    print("Usage:")
    print("  aish test              Run all test suites")
    print("  aish test -v           Run all tests with verbose output")
    print("  aish test <suite>      Run specific test suite")
    print("  aish test help         Show this help message")
    print()
    print("Available Test Suites:")
    print("  basic     - Basic commands (help, list, status, etc.)")
    print("  forward   - Forward command tests")
    print("  purpose   - Purpose command tests")
    print("  terma     - Terminal communication tests")
    print("  route     - Route command tests")
    print("  unified   - Unified CI registry and messaging tests")
    print()
    print("Examples:")
    print("  aish test                    # Run all tests")
    print("  aish test forward            # Run only forward tests")
    print("  aish test -v basic           # Run basic tests verbosely")
    print()
    print("Test Details:")
    print("  • Tests run actual aish commands")
    print("  • No mocking - tests real functionality")
    print("  • Automatic cleanup of test data")
    print("  • Safe to run multiple times")
    print()
    print("Adding New Tests:")
    print("  Test files: shared/aish/tests/test_*.py")
    print("  Examples:   shared/aish/tests/examples/")
    print()
    print("Exit Codes:")
    print("  0 - All tests passed")
    print("  1 - One or more tests failed")
    print()
    print("Note: Some tests may skip if required services (terma, AIs)")
    print("      are not running. This is normal and expected.")