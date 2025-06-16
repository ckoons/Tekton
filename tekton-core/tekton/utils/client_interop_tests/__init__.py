#!/usr/bin/env python3
"""
Client Interop Tests Package

This package contains modules for testing interoperability between
different Tekton components and their clients.
"""

from .runner import run_tests
from .config import parse_args, TestConfig

__all__ = [
    'run_tests',
    'parse_args',
    'TestConfig'
]
