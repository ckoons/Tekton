#!/usr/bin/env python3
"""
Cross-Component Workflow Test Suite

Tests workflows that involve multiple components.
"""

import time
import random
import logging
from typing import Dict, Any, List, Optional

from ..result_manager import TestResult, TestSuiteResult

logger = logging.getLogger("tekton.utils.client_interop_tests.workflow")


async def run_workflow_tests(clients: Dict[str, Any], suite: TestSuiteResult) -> None:
    """
    Run cross-component workflow tests.
    
    Args:
        clients: Dictionary of client instances
        suite: Test suite result
    """
    logger.info("Running cross-component workflow tests...")
    
    # Test knowledge-prompt workflow
    await _test_knowledge_prompt_workflow(clients, suite)
    
    # Test requirements-analysis workflow
    await _test_requirements_analysis_workflow(clients, suite)
    
    logger.info("Cross-component workflow tests complete")


async def _test_knowledge_prompt_workflow(clients: Dict[str, Any], suite: TestSuiteResult) -> None:
    """
    Test knowledge graph to prompt workflow.
    
    Args:
        clients: Dictionary of client instances
        suite: Test suite result
    """
    start_time = time.time()
    test_name = "knowledge_prompt_workflow"
    workflow_steps = []
    
    try:
        # Check required clients
        if "athena" not in clients or "rhetor" not in clients:
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details="Required clients not available for this workflow (athena, rhetor)"
            ))
            return
            
        athena_client = clients["athena"]
        rhetor_client = clients["rhetor"]
        
        # Step 1: Create entity in knowledge graph
        entity_id = f"test_entity_{random.randint(1000, 9999)}"
        entity = {
            "id": entity_id,
            "type": "test_type",
            "properties": {
                "name": "Test Entity",
                "description": "This is a test entity for workflow testing",
                "attributes": ["attribute1", "attribute2"]
            }
        }
        
        result = await athena_client.create_entity(entity)
        if not result or not isinstance(result, dict) or "id" not in result:
            workflow_steps.append("Entity creation failed")
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Failed to create entity: {result}"
            ))
            return
            
        workflow_steps.append("Created entity in knowledge graph")
        
        # Step 2: Query the entity
        entity_query = {
            "entity_id": entity_id
        }
        query_result = await athena_client.query_entity(entity_query)
        
        if not query_result or not isinstance(query_result, dict):
            workflow_steps.append("Entity query failed")
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Failed to query entity: {query_result}"
            ))
            return
            
        workflow_steps.append("Retrieved entity from knowledge graph")
        
        # Step 3: Generate prompt using entity information
        entity_desc = query_result.get("properties", {}).get("description", "No description available")
        entity_name = query_result.get("properties", {}).get("name", "Unknown entity")
        
        template_name = "entity_description"
        variables = {
            "entity_name": entity_name,
            "entity_description": entity_desc,
            "entity_attributes": ", ".join(query_result.get("properties", {}).get("attributes", []))
        }
        
        prompt = await rhetor_client.generate_prompt(template_name, variables)
        
        if not prompt or not isinstance(prompt, str) or entity_name not in prompt:
            workflow_steps.append("Prompt generation failed")
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Failed to generate prompt: {prompt}"
            ))
            return
            
        workflow_steps.append("Generated prompt from entity data")
        
        suite.add_result(TestResult(
            name=test_name,
            success=True,
            duration=time.time() - start_time,
            details=f"Workflow completed successfully: {' -> '.join(workflow_steps)}"
        ))
        
    except Exception as e:
        workflow_steps.append(f"Error: {str(e)}")
        suite.add_result(TestResult(
            name=test_name,
            success=False,
            duration=time.time() - start_time,
            details=f"Workflow failed: {' -> '.join(workflow_steps)}",
            error=e
        ))


async def _test_requirements_analysis_workflow(clients: Dict[str, Any], suite: TestSuiteResult) -> None:
    """
    Test requirements analysis workflow.
    
    Args:
        clients: Dictionary of client instances
        suite: Test suite result
    """
    start_time = time.time()
    test_name = "requirements_analysis_workflow"
    workflow_steps = []
    
    try:
        # Check required clients
        if "telos" not in clients or "sophia" not in clients:
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details="Required clients not available for this workflow (telos, sophia)"
            ))
            return
            
        telos_client = clients["telos"]
        sophia_client = clients["sophia"]
        
        # Step 1: Create project
        project_name = f"test_project_{random.randint(1000, 9999)}"
        project = await telos_client.create_project(project_name, "Test project for requirements analysis")
        
        if not project or not isinstance(project, dict) or "id" not in project:
            workflow_steps.append("Project creation failed")
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Failed to create project: {project}"
            ))
            return
            
        project_id = project["id"]
        workflow_steps.append("Created project")
        
        # Step 2: Add requirements
        requirements = [
            {
                "title": "Performance Requirement",
                "description": "The system must respond to user requests within 200ms",
                "priority": "high",
                "category": "performance"
            },
            {
                "title": "Security Requirement",
                "description": "All user data must be encrypted at rest and in transit",
                "priority": "critical",
                "category": "security"
            },
            {
                "title": "Usability Requirement",
                "description": "The system must be accessible to users with visual impairments",
                "priority": "medium",
                "category": "usability"
            }
        ]
        
        requirement_ids = []
        for req in requirements:
            result = await telos_client.add_requirement(project_id, req)
            if result and isinstance(result, dict) and "id" in result:
                requirement_ids.append(result["id"])
                
        if len(requirement_ids) != len(requirements):
            workflow_steps.append("Some requirements failed to create")
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Failed to create all requirements: {len(requirement_ids)}/{len(requirements)}"
            ))
            return
            
        workflow_steps.append(f"Added {len(requirements)} requirements")
        
        # Step 3: Analyze requirements with Sophia
        project_requirements = await telos_client.get_requirements(project_id)
        
        if not project_requirements or not isinstance(project_requirements, list):
            workflow_steps.append("Failed to retrieve requirements")
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Failed to retrieve requirements: {project_requirements}"
            ))
            return
            
        workflow_steps.append("Retrieved requirements")
        
        # Step 4: Use Sophia to analyze requirements
        model_id = "requirements_analyzer"
        input_data = {
            "requirements": project_requirements,
            "analysis_type": "complexity"
        }
        
        analysis_result = await sophia_client.analyze_requirements(model_id, input_data)
        
        if not analysis_result or not isinstance(analysis_result, dict):
            workflow_steps.append("Requirements analysis failed")
            suite.add_result(TestResult(
                name=test_name,
                success=False,
                duration=time.time() - start_time,
                details=f"Failed to analyze requirements: {analysis_result}"
            ))
            return
            
        workflow_steps.append("Analyzed requirements")
        
        # Step 5: Store analysis results back in Telos
        for req_id, analysis in analysis_result.get("requirement_analysis", {}).items():
            update_result = await telos_client.update_requirement(project_id, req_id, {"analysis": analysis})
            if not update_result:
                workflow_steps.append(f"Failed to update requirement {req_id}")
                
        workflow_steps.append("Updated requirements with analysis")
        
        suite.add_result(TestResult(
            name=test_name,
            success=True,
            duration=time.time() - start_time,
            details=f"Workflow completed successfully: {' -> '.join(workflow_steps)}"
        ))
        
    except Exception as e:
        workflow_steps.append(f"Error: {str(e)}")
        suite.add_result(TestResult(
            name=test_name,
            success=False,
            duration=time.time() - start_time,
            details=f"Workflow failed: {' -> '.join(workflow_steps)}",
            error=e
        ))
