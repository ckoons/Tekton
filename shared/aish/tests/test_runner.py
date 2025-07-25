#!/usr/bin/env python3
"""
Simple test runner for aish functional tests.
Tests actual command execution without mocks.
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class AishTest:
    """Base class for aish tests"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.passed = False
        self.error_message = ""
        self.setup_commands = []
        self.teardown_commands = []
    
    def run_command(self, cmd: str, timeout: int = 10) -> Tuple[int, str, str]:
        """Run a command and return (exit_code, stdout, stderr)"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    def setup(self):
        """Run setup commands"""
        for cmd in self.setup_commands:
            exit_code, _, stderr = self.run_command(cmd)
            if exit_code != 0:
                raise Exception(f"Setup failed: {cmd}\n{stderr}")
    
    def teardown(self):
        """Run teardown commands - always run even if test fails"""
        for cmd in self.teardown_commands:
            # Don't fail on teardown errors, just report them
            exit_code, _, stderr = self.run_command(cmd)
            if exit_code != 0:
                print(f"{YELLOW}Warning: Teardown command failed: {cmd}{RESET}")
    
    def test(self) -> bool:
        """Override this method in subclasses"""
        raise NotImplementedError
    
    def run(self) -> bool:
        """Run the test with setup and teardown"""
        try:
            self.setup()
            self.passed = self.test()
            return self.passed
        except Exception as e:
            self.passed = False
            self.error_message = str(e)
            return False
        finally:
            self.teardown()


class TestSuite:
    """Collection of tests"""
    
    def __init__(self, name: str):
        self.name = name
        self.tests: List[AishTest] = []
        self.start_time = None
        self.end_time = None
    
    def add_test(self, test: AishTest):
        """Add a test to the suite"""
        self.tests.append(test)
    
    def run(self, verbose: bool = False) -> Dict[str, any]:
        """Run all tests and return results"""
        self.start_time = datetime.now()
        results = {
            "suite": self.name,
            "total": len(self.tests),
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        print(f"\n{BLUE}Running {self.name}{RESET}")
        print("=" * 60)
        
        for test in self.tests:
            if verbose:
                print(f"\nRunning: {test.name}")
                print(f"  {test.description}")
            else:
                print(f"  {test.name}...", end=" ", flush=True)
            
            success = test.run()
            
            if success:
                results["passed"] += 1
                if verbose:
                    print(f"  {GREEN}✓ PASSED{RESET}")
                else:
                    print(f"{GREEN}✓{RESET}")
            else:
                results["failed"] += 1
                if verbose:
                    print(f"  {RED}✗ FAILED{RESET}")
                    if test.error_message:
                        print(f"    Error: {test.error_message}")
                else:
                    print(f"{RED}✗{RESET}")
            
            results["tests"].append({
                "name": test.name,
                "passed": test.passed,
                "error": test.error_message
            })
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print(f"Total: {results['total']} | " +
              f"{GREEN}Passed: {results['passed']}{RESET} | " +
              f"{RED}Failed: {results['failed']}{RESET} | " +
              f"Time: {duration:.2f}s")
        
        return results


def load_all_tests() -> List[TestSuite]:
    """Load all test suites"""
    suites = []
    
    # Import test modules and create suites
    from . import test_basic
    from . import test_forward
    from . import test_purpose
    from . import test_terma
    from . import test_route
    from . import test_unified
    from . import test_inbox
    
    suites.append(test_basic.create_suite())
    suites.append(test_forward.create_suite())
    suites.append(test_purpose.create_suite())
    suites.append(test_terma.create_suite())
    suites.append(test_route.create_suite())
    suites.append(test_unified.create_suite())
    suites.append(test_inbox.create_suite())
    
    return suites


def run_all_tests(verbose: bool = False, suite_name: Optional[str] = None) -> bool:
    """Run all tests or a specific suite"""
    suites = load_all_tests()
    
    if suite_name:
        # Run specific suite
        suites = [s for s in suites if s.name.lower() == suite_name.lower()]
        if not suites:
            print(f"{RED}Error: Test suite '{suite_name}' not found{RESET}")
            return False
    
    total_passed = 0
    total_failed = 0
    
    for suite in suites:
        results = suite.run(verbose)
        total_passed += results["passed"]
        total_failed += results["failed"]
    
    print(f"\n{BLUE}Overall Results:{RESET}")
    print(f"  Total Tests: {total_passed + total_failed}")
    print(f"  {GREEN}Passed: {total_passed}{RESET}")
    print(f"  {RED}Failed: {total_failed}{RESET}")
    
    return total_failed == 0


if __name__ == "__main__":
    # Simple CLI for running tests
    import argparse
    parser = argparse.ArgumentParser(description="Run aish tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("suite", nargs="?", help="Specific test suite to run")
    args = parser.parse_args()
    
    success = run_all_tests(args.verbose, args.suite)
    sys.exit(0 if success else 1)