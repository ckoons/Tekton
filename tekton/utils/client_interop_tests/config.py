#!/usr/bin/env python3
"""
Test Configuration Module

Handles configuration parsing and management for interop tests.
"""

import argparse
from dataclasses import dataclass
from typing import List, Optional, Set


@dataclass
class TestConfig:
    """
    Configuration for interop tests.
    """
    test_all: bool = True
    test_discovery: bool = False
    test_capabilities: bool = False
    test_workflow: bool = False
    hermes_url: str = "http://localhost:5000"
    log_level: str = "INFO"
    
    @property
    def enabled_tests(self) -> Set[str]:
        """
        Get enabled test names.
        
        Returns:
            Set of enabled test names
        """
        tests = set()
        
        if self.test_all or self.test_discovery:
            tests.add("discovery")
        if self.test_all or self.test_capabilities:
            tests.add("capabilities")
        if self.test_all or self.test_workflow:
            tests.add("workflow")
            
        return tests


def parse_args() -> TestConfig:
    """
    Parse command line arguments.
    
    Returns:
        TestConfig object
    """
    parser = argparse.ArgumentParser(description="Test Tekton component client interoperability")
    parser.add_argument("--discovery", action="store_true", help="Test component discovery")
    parser.add_argument("--capabilities", action="store_true", help="Test component capabilities")
    parser.add_argument("--workflow", action="store_true", help="Test cross-component workflow")
    parser.add_argument("--hermes-url", default="http://localhost:5000", help="Hermes URL")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    
    args = parser.parse_args()
    
    # If any specific test is enabled, don't run all tests
    test_all = not (args.discovery or args.capabilities or args.workflow)
    
    return TestConfig(
        test_all=test_all,
        test_discovery=args.discovery,
        test_capabilities=args.capabilities,
        test_workflow=args.workflow,
        hermes_url=args.hermes_url,
        log_level=args.log_level
    )
