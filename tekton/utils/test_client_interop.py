#!/usr/bin/env python3
"""
Component Client Interoperability Test

This script tests the interoperability of Tekton component clients.
"""

import sys
from .client_interop_tests import parse_args, run_tests

if __name__ == "__main__":
    # Parse args and run tests
    config = parse_args()
    sys.exit(run_tests(config))