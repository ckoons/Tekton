#!/usr/bin/env python3
"""
Test Runner Module

Orchestrates the execution of client interoperability tests.
"""

import logging
import asyncio
import sys
from typing import Dict, List, Any, Optional

from .client_manager import ClientManager
from .result_manager import ResultManager, TestSuiteResult
from .test_suites import run_discovery_tests, run_capability_tests, run_workflow_tests
from .config import TestConfig

logger = logging.getLogger("tekton.utils.client_interop_tests")


async def run_tests(config: TestConfig) -> bool:
    """
    Run client interoperability tests.
    
    Args:
        config: Test configuration
        
    Returns:
        True if all tests passed
    """
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize result manager
    result_manager = ResultManager()
    
    # Initialize client manager
    client_manager = ClientManager(config.hermes_url)
    
    try:
        # Initialize clients
        logger.info(f"Initializing clients with Hermes URL: {config.hermes_url}")
        clients = client_manager.init_clients()
        
        # Run discovery tests
        if "discovery" in config.enabled_tests:
            discovery_suite = result_manager.create_suite("discovery")
            await run_discovery_tests(clients, discovery_suite)
        
        # Run capability tests
        if "capabilities" in config.enabled_tests:
            capability_suite = result_manager.create_suite("capabilities")
            await run_capability_tests(clients, capability_suite)
        
        # Run workflow tests
        if "workflow" in config.enabled_tests:
            workflow_suite = result_manager.create_suite("workflow")
            await run_workflow_tests(clients, workflow_suite)
            
        # Generate report
        report = result_manager.generate_report()
        logger.info("\n" + report)
        
        return result_manager.success
        
    except Exception as e:
        logger.exception(f"Error running tests: {e}")
        return False
    finally:
        # Clean up clients
        client_manager.cleanup_clients()


def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Parse arguments
    config = parse_args()
    
    # Run tests
    success = asyncio.run(run_tests(config))
    
    return 0 if success else 1