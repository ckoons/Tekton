#!/usr/bin/env python3
"""
Test Suites Package

Contains individual test suites for client interoperability testing.
"""

from .discovery import run_discovery_tests
from .capabilities import run_capability_tests
from .workflow import run_workflow_tests

__all__ = [
    'run_discovery_tests',
    'run_capability_tests',
    'run_workflow_tests'
]
