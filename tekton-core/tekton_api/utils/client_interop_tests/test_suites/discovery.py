#!/usr/bin/env python3
"""
Component Discovery Test Suite

Tests component discovery functionality.
"""

import time
import logging
from typing import Dict, Any, List, Optional

from ..result_manager import TestResult, TestSuiteResult

logger = logging.getLogger("tekton.utils.client_interop_tests.discovery")


async def run_discovery_tests(clients: Dict[str, Any], suite: TestSuiteResult) -> None:
    """
    Run component discovery tests.
    
    Args:
        clients: Dictionary of client instances
        suite: Test suite result
    """
    logger.info("Running component discovery tests...")
    
    # Test Hermes client is available
    await _test_hermes_client(clients, suite)
    
    # Test component discovery via Hermes
    await _test_component_discovery(clients, suite)
    
    # Test component health check
    await _test_component_health(clients, suite)
    
    logger.info("Component discovery tests complete")


async def _test_hermes_client(clients: Dict[str, Any], suite: TestSuiteResult) -> None:
    """
    Test that Hermes client is available.
    
    Args:
        clients: Dictionary of client instances
        suite: Test suite result
    """
    start_time = time.time()
    test_name = "hermes_client_available"
    
    try:
        hermes_client = clients.get("hermes")
        
        if hermes_client is None:
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details="Hermes client not found"
            ))
            return
            
        # Test that the client has required methods
        required_methods = ["get_components", "get_component_health", "register_component"]
        missing_methods = [method for method in required_methods if not hasattr(hermes_client, method)]
        
        if missing_methods:
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Hermes client missing methods: {', '.join(missing_methods)}"
            ))
            return
            
        suite.add_result(TestResult(
            name=test_name,
            success=True,
            duration=time.time() - start_time,
            details="Hermes client initialized successfully"
        ))
        
    except Exception as e:
        suite.add_result(TestResult(
            name=test_name,
            success=False,
            duration=time.time() - start_time,
            details="Error checking Hermes client",
            error=e
        ))


async def _test_component_discovery(clients: Dict[str, Any], suite: TestSuiteResult) -> None:
    """
    Test component discovery via Hermes.
    
    Args:
        clients: Dictionary of client instances
        suite: Test suite result
    """
    start_time = time.time()
    test_name = "component_discovery"
    
    try:
        hermes_client = clients.get("hermes")
        
        if hermes_client is None:
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details="Hermes client not found"
            ))
            return
            
        # Get registered components
        components = await hermes_client.get_components()
        
        if not components or not isinstance(components, list):
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"No components found or invalid response: {components}"
            ))
            return
            
        # Check that components have required fields
        required_fields = ["component_id", "component_name", "component_type"]
        invalid_components = []
        
        for component in components:
            if not all(field in component for field in required_fields):
                invalid_components.append(component)
                
        if invalid_components:
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Components missing required fields: {invalid_components}"
            ))
            return
            
        suite.add_result(TestResult(
            name=test_name,
            success=True,
            duration=time.time() - start_time,
            details=f"Found {len(components)} components"
        ))
        
    except Exception as e:
        suite.add_result(TestResult(
            name=test_name,
            success=False,
            duration=time.time() - start_time,
            details="Error discovering components",
            error=e
        ))


async def _test_component_health(clients: Dict[str, Any], suite: TestSuiteResult) -> None:
    """
    Test component health check.
    
    Args:
        clients: Dictionary of client instances
        suite: Test suite result
    """
    start_time = time.time()
    test_name = "component_health"
    
    try:
        hermes_client = clients.get("hermes")
        
        if hermes_client is None:
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details="Hermes client not found"
            ))
            return
            
        # Get component health
        health = await hermes_client.get_component_health()
        
        if not health or not isinstance(health, dict):
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Invalid health response: {health}"
            ))
            return
            
        # Check that health data has required structure
        if "components" not in health or not isinstance(health["components"], list):
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Health data missing components: {health}"
            ))
            return
            
        # Check that components have health info
        for component in health["components"]:
            if "component_id" not in component or "status" not in component:
                suite.add_result(TestResult(
                    name=test_name,
                    success=False,
                    duration=time.time() - start_time,
                    details=f"Component missing health info: {component}"
                ))
                return
                
        suite.add_result(TestResult(
            name=test_name,
            success=True,
            duration=time.time() - start_time,
            details=f"Health check successful for {len(health['components'])} components"
        ))
        
    except Exception as e:
        suite.add_result(TestResult(
            name=test_name,
            success=False,
            duration=time.time() - start_time,
            details="Error checking component health",
            error=e
        ))
