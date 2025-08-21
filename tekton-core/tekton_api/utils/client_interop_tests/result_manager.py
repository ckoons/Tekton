#!/usr/bin/env python3
"""
Result Manager Module

Manages test results and reporting for interop tests.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class TestResult:
    """
    Result of a single test.
    """
    name: str
    success: bool
    duration: float
    details: Optional[str] = None
    error: Optional[Exception] = None
    
    @property
    def status(self) -> str:
        """Get test status string."""
        return "PASS" if self.success else "FAIL"
    
    def __str__(self) -> str:
        """Get string representation of test result."""
        return f"{self.name}: {self.status} ({self.duration:.2f}s)" + \
               (f" - {self.details}" if self.details else "") + \
               (f" - ERROR: {self.error}" if self.error else "")


@dataclass
class TestSuiteResult:
    """
    Result of a test suite.
    """
    name: str
    start_time: float
    results: List[TestResult] = field(default_factory=list)
    end_time: Optional[float] = None
    
    @property
    def duration(self) -> float:
        """Get test suite duration."""
        end = self.end_time or time.time()
        return end - self.start_time
    
    @property
    def success(self) -> bool:
        """Check if all tests in the suite passed."""
        return all(result.success for result in self.results)
    
    @property
    def pass_count(self) -> int:
        """Get number of passing tests."""
        return sum(1 for result in self.results if result.success)
    
    @property
    def fail_count(self) -> int:
        """Get number of failing tests."""
        return sum(1 for result in self.results if not result.success)
    
    def add_result(self, result: TestResult) -> None:
        """Add a test result to the suite."""
        self.results.append(result)
    
    def complete(self) -> None:
        """Mark the test suite as complete."""
        self.end_time = time.time()
    
    def __str__(self) -> str:
        """Get string representation of test suite result."""
        status = "PASS" if self.success else "FAIL"
        return f"Suite {self.name}: {status} - {self.pass_count}/{len(self.results)} tests passed ({self.duration:.2f}s)"


class ResultManager:
    """
    Manages test results and reporting.
    """
    
    def __init__(self):
        """Initialize result manager."""
        self.suites: Dict[str, TestSuiteResult] = {}
        self.start_time = time.time()
        self.end_time = None
    
    @property
    def duration(self) -> float:
        """Get total test duration."""
        end = self.end_time or time.time()
        return end - self.start_time
    
    @property
    def success(self) -> bool:
        """Check if all test suites passed."""
        return all(suite.success for suite in self.suites.values())
    
    @property
    def pass_count(self) -> int:
        """Get total number of passing tests."""
        return sum(suite.pass_count for suite in self.suites.values())
    
    @property
    def fail_count(self) -> int:
        """Get total number of failing tests."""
        return sum(suite.fail_count for suite in self.suites.values())
    
    @property
    def total_count(self) -> int:
        """Get total number of tests."""
        return self.pass_count + self.fail_count
    
    def create_suite(self, name: str) -> TestSuiteResult:
        """Create a new test suite."""
        suite = TestSuiteResult(name=name, start_time=time.time())
        self.suites[name] = suite
        return suite
    
    def complete(self) -> None:
        """Mark all test suites as complete."""
        for suite in self.suites.values():
            suite.complete()
        self.end_time = time.time()
    
    def generate_report(self) -> str:
        """Generate a test report."""
        self.complete()
        
        lines = [
            "===== Test Results =====",
            f"Overall Status: {'PASS' if self.success else 'FAIL'}",
            f"Total Tests: {self.total_count}",
            f"Passing: {self.pass_count}",
            f"Failing: {self.fail_count}",
            f"Duration: {self.duration:.2f}s",
            "\nTest Suites:"
        ]
        
        for suite in self.suites.values():
            lines.append(f"\n{suite}")
            for result in suite.results:
                lines.append(f"  {result}")
        
        return "\n".join(lines)
