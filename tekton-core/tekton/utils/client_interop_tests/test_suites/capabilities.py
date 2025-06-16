#!/usr/bin/env python3
"""
Component Capabilities Test Suite

Tests component capability invocation.
"""

import time
import random
import logging
from typing import Dict, Any, List, Optional

from ..result_manager import TestResult, TestSuiteResult

logger = logging.getLogger("tekton.utils.client_interop_tests.capabilities")


async def run_capability_tests(clients: Dict[str, Any], suite: TestSuiteResult) -> None:
    """
    Run component capability tests.
    
    Args:
        clients: Dictionary of client instances
        suite: Test suite result
    """
    logger.info("Running component capability tests...")
    
    # Test Athena knowledge graph capability
    if "athena" in clients:
        await _test_athena_knowledge_graph(clients, suite)
    
    # Test Engram memory capability
    if "engram" in clients:
        await _test_engram_memory(clients, suite)
    
    # Test Rhetor prompt capability
    if "rhetor" in clients:
        await _test_rhetor_prompt(clients, suite)
    
    # Test Telos requirement capability
    if "telos" in clients:
        await _test_telos_requirements(clients, suite)
    
    # Test Sophia ML capability
    if "sophia" in clients:
        await _test_sophia_ml(clients, suite)
        
    logger.info("Component capability tests complete")


async def _test_athena_knowledge_graph(clients: Dict[str, Any], suite: TestSuiteResult) -> None:
    """
    Test Athena knowledge graph capability.
    
    Args:
        clients: Dictionary of client instances
        suite: Test suite result
    """
    start_time = time.time()
    test_name = "athena_knowledge_graph"
    
    try:
        athena_client = clients.get("athena")
        
        # Query knowledge graph
        query = {
            "entity_type": "test_entity",
            "properties": {"name": f"test_entity_{random.randint(1000, 9999)}"},
            "relationships": []
        }
        
        result = await athena_client.query_knowledge_graph(query)
        
        # Check result
        if result is None or not isinstance(result, dict):
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Invalid query result: {result}"
            ))
            return
            
        suite.add_result(TestResult(
            name=test_name,
            success=True,
            duration=time.time() - start_time,
            details="Knowledge graph query successful"
        ))
        
    except Exception as e:
        suite.add_result(TestResult(
            name=test_name,
            success=False,
            duration=time.time() - start_time,
            details="Error querying knowledge graph",
            error=e
        ))


async def _test_engram_memory(clients: Dict[str, Any], suite: TestSuiteResult) -> None:
    """
    Test Engram memory capability.
    
    Args:
        clients: Dictionary of client instances
        suite: Test suite result
    """
    start_time = time.time()
    test_name = "engram_memory"
    
    try:
        engram_client = clients.get("engram")
        
        # Store memory
        memory_id = f"test_memory_{random.randint(1000, 9999)}"
        memory_content = f"This is a test memory created at {time.time()}"
        
        await engram_client.store_memory(memory_id, memory_content)
        
        # Retrieve memory
        retrieved = await engram_client.retrieve_memory(memory_id)
        
        # Check result
        if not retrieved or memory_content not in str(retrieved):
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Memory retrieval failed. Expected: {memory_content}, Got: {retrieved}"
            ))
            return
            
        suite.add_result(TestResult(
            name=test_name,
            success=True,
            duration=time.time() - start_time,
            details="Memory store and retrieve successful"
        ))
        
    except Exception as e:
        suite.add_result(TestResult(
            name=test_name,
            success=False,
            duration=time.time() - start_time,
            details="Error testing memory capabilities",
            error=e
        ))


async def _test_rhetor_prompt(clients: Dict[str, Any], suite: TestSuiteResult) -> None:
    """
    Test Rhetor prompt capability.
    
    Args:
        clients: Dictionary of client instances
        suite: Test suite result
    """
    start_time = time.time()
    test_name = "rhetor_prompt"
    
    try:
        rhetor_client = clients.get("rhetor")
        
        # Get prompt template
        template_name = "basic_question"
        template = await rhetor_client.get_prompt_template(template_name)
        
        # Check template
        if not template or not isinstance(template, dict) or "content" not in template:
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Invalid prompt template: {template}"
            ))
            return
            
        # Generate prompt
        variables = {"question": "What is the meaning of life?"}
        prompt = await rhetor_client.generate_prompt(template_name, variables)
        
        # Check prompt
        if not prompt or variables["question"] not in prompt:
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Invalid generated prompt: {prompt}"
            ))
            return
            
        suite.add_result(TestResult(
            name=test_name,
            success=True,
            duration=time.time() - start_time,
            details="Prompt generation successful"
        ))
        
    except Exception as e:
        suite.add_result(TestResult(
            name=test_name,
            success=False,
            duration=time.time() - start_time,
            details="Error testing prompt capabilities",
            error=e
        ))


async def _test_telos_requirements(clients: Dict[str, Any], suite: TestSuiteResult) -> None:
    """
    Test Telos requirements capability.
    
    Args:
        clients: Dictionary of client instances
        suite: Test suite result
    """
    start_time = time.time()
    test_name = "telos_requirements"
    
    try:
        telos_client = clients.get("telos")
        
        # Create project
        project_name = f"test_project_{random.randint(1000, 9999)}"
        project = await telos_client.create_project(project_name, "Test project description")
        
        # Check project
        if not project or not isinstance(project, dict) or "id" not in project:
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Invalid project creation result: {project}"
            ))
            return
            
        # Add requirement
        requirement = {
            "title": "Test Requirement",
            "description": "This is a test requirement",
            "priority": "high"
        }
        
        req_result = await telos_client.add_requirement(project["id"], requirement)
        
        # Check requirement
        if not req_result or not isinstance(req_result, dict) or "id" not in req_result:
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Invalid requirement creation result: {req_result}"
            ))
            return
            
        suite.add_result(TestResult(
            name=test_name,
            success=True,
            duration=time.time() - start_time,
            details="Requirements management successful"
        ))
        
    except Exception as e:
        suite.add_result(TestResult(
            name=test_name,
            success=False,
            duration=time.time() - start_time,
            details="Error testing requirements capabilities",
            error=e
        ))


async def _test_sophia_ml(clients: Dict[str, Any], suite: TestSuiteResult) -> None:
    """
    Test Sophia ML capability.
    
    Args:
        clients: Dictionary of client instances
        suite: Test suite result
    """
    start_time = time.time()
    test_name = "sophia_ml"
    
    try:
        sophia_client = clients.get("sophia")
        
        # Get available models
        models = await sophia_client.get_available_models()
        
        # Check models
        if not models or not isinstance(models, list):
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Invalid models response: {models}"
            ))
            return
            
        # If we have models, test prediction
        if models:
            model_id = models[0]["id"] if isinstance(models[0], dict) and "id" in models[0] else models[0]
            
            # Simple prediction
            data = {"input": [1, 2, 3, 4, 5]}
            prediction = await sophia_client.predict(model_id, data)
            
            # Check prediction
            if prediction is None:
                suite.add_result(TestResult(
                    name=test_name,
                    success=False,
                    duration=time.time() - start_time,
                    details=f"Prediction failed: {prediction}"
                ))
                return
                
        suite.add_result(TestResult(
            name=test_name,
            success=True,
            duration=time.time() - start_time,
            details=f"ML capabilities check successful, found {len(models)} models"
        ))
        
    except Exception as e:
        suite.add_result(TestResult(
            name=test_name,
            success=False,
            duration=time.time() - start_time,
            details="Error testing ML capabilities",
            error=e
        ))
