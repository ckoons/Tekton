#!/usr/bin/env python3
"""
Component Registry - Component registration data for Tekton

This module provides functions for generating component registration data.
"""

import os
import logging
import time
from typing import Dict, List, Any, Optional, Set, Union

# Configure logging
logger = logging.getLogger("tekton_launcher.registry")

# Import Tekton modules
try:
    from tekton.core.startup_instructions import StartUpInstructions
except ImportError:
    logger.error("Failed to import Tekton core modules. Make sure tekton-core is properly installed.")
    raise

# Component dependency map
COMPONENT_DEPENDENCIES = {
    "engram": [],
    "hermes": [],
    "athena": ["hermes"],
    "sophia": ["hermes"],
    "prometheus": ["athena"],
    "synthesis": ["prometheus"],
    "harmonia": ["hermes"],
    "rhetor": ["sophia"],
    "telos": ["rhetor"]
}

def get_component_dependencies(component_name: str) -> List[str]:
    """
    Get dependencies for a specified component.
    
    Args:
        component_name: Name of the component
        
    Returns:
        List of component names that this component depends on
    """
    component_name_lower = component_name.lower()
    return COMPONENT_DEPENDENCIES.get(component_name_lower, [])


async def create_startup_instructions(component_name: str) -> StartUpInstructions:
    """
    Create startup instructions for a specific component.
    
    Args:
        component_name: Name of the component to create instructions for
        
    Returns:
        StartUpInstructions instance
    """
    component_id = f"{component_name.lower()}.core"
    component_type = component_name.lower()
    data_directory = os.path.expanduser(f"~/.tekton/data/{component_type}")
    
    # Common capabilities and metadata
    capabilities = []
    metadata = {
        "version": "0.1.0",
        "tekton_component": True,
        "startup_timestamp": str(int(os.environ.get("TEKTON_STARTUP_TIMESTAMP", "0") or int(time.time())))
    }
    
    # Component-specific configuration
    if component_name.lower() == "synthesis":
        capabilities = [
            {
                "name": "execute_plan",
                "description": "Execute a plan generated by Prometheus",
                "parameters": {
                    "plan": "object",
                    "execution_context": "object (optional)"
                }
            },
            {
                "name": "get_execution_status",
                "description": "Get the status of an execution",
                "parameters": {
                    "execution_id": "string"
                }
            },
            {
                "name": "cancel_execution",
                "description": "Cancel an execution",
                "parameters": {
                    "execution_id": "string"
                }
            }
        ]
        metadata.update({
            "description": "Execution engine for implementing plans",
            "dependencies": ["prometheus"]
        })
        dependencies = ["prometheus.core"]
        
    elif component_name.lower() == "harmonia":
        capabilities = [
            {
                "name": "create_workflow",
                "description": "Create a workflow definition",
                "parameters": {
                    "name": "string",
                    "description": "string (optional)",
                    "tasks": "array"
                }
            },
            {
                "name": "execute_workflow",
                "description": "Execute a workflow",
                "parameters": {
                    "workflow_id": "string",
                    "input": "object (optional)"
                }
            },
            {
                "name": "get_workflow_status",
                "description": "Get the status of a workflow execution",
                "parameters": {
                    "execution_id": "string"
                }
            }
        ]
        metadata.update({
            "description": "Workflow orchestration engine",
            "dependencies": ["hermes"]
        })
        dependencies = ["hermes.core.database"]
        
    elif component_name.lower() == "athena":
        capabilities = [
            {
                "name": "create_entity",
                "description": "Create a knowledge entity",
                "parameters": {
                    "type": "string",
                    "properties": "object"
                }
            },
            {
                "name": "create_relationship",
                "description": "Create a relationship between entities",
                "parameters": {
                    "source_id": "string",
                    "target_id": "string",
                    "type": "string",
                    "properties": "object (optional)"
                }
            },
            {
                "name": "query_knowledge",
                "description": "Query the knowledge graph",
                "parameters": {
                    "query": "string",
                    "parameters": "object (optional)"
                }
            }
        ]
        metadata.update({
            "description": "Knowledge graph for structured information",
            "dependencies": ["hermes"]
        })
        dependencies = ["hermes.core.database"]
        
    elif component_name.lower() == "sophia":
        capabilities = [
            {
                "name": "generate_embedding",
                "description": "Generate an embedding for text",
                "parameters": {
                    "text": "string",
                    "model": "string (optional)"
                }
            },
            {
                "name": "classify_text",
                "description": "Classify text into categories",
                "parameters": {
                    "text": "string",
                    "categories": "array (optional)"
                }
            },
            {
                "name": "train_model",
                "description": "Train a machine learning model",
                "parameters": {
                    "model_type": "string",
                    "data": "object",
                    "parameters": "object (optional)"
                }
            }
        ]
        metadata.update({
            "description": "Machine learning system for training and inference",
            "dependencies": ["hermes"]
        })
        dependencies = ["hermes.core.database"]
        
    elif component_name.lower() == "prometheus":
        capabilities = [
            {
                "name": "create_plan",
                "description": "Create a plan for an objective",
                "parameters": {
                    "objective": "string",
                    "context": "object (optional)"
                }
            },
            {
                "name": "refine_plan",
                "description": "Refine an existing plan",
                "parameters": {
                    "plan_id": "string",
                    "feedback": "string"
                }
            }
        ]
        metadata.update({
            "description": "Planning engine for generating structured plans",
            "dependencies": ["athena"]
        })
        dependencies = ["athena.core"]
        
    elif component_name.lower() == "rhetor":
        capabilities = [
            {
                "name": "generate_message",
                "description": "Generate a natural language message",
                "parameters": {
                    "intent": "string",
                    "context": "object (optional)",
                    "tone": "string (optional)"
                }
            },
            {
                "name": "analyze_message",
                "description": "Analyze a natural language message",
                "parameters": {
                    "message": "string",
                    "analysis_type": "string (optional)"
                }
            }
        ]
        metadata.update({
            "description": "Communication system for natural language generation",
            "dependencies": ["sophia"]
        })
        dependencies = ["sophia.core"]
        
    elif component_name.lower() == "telos":
        capabilities = [
            {
                "name": "create_interface",
                "description": "Create a user interface",
                "parameters": {
                    "type": "string",
                    "configuration": "object"
                }
            },
            {
                "name": "handle_user_input",
                "description": "Handle user input from an interface",
                "parameters": {
                    "interface_id": "string",
                    "input": "object"
                }
            }
        ]
        metadata.update({
            "description": "User interface system",
            "dependencies": ["rhetor"]
        })
        dependencies = ["rhetor.core"]
        
    else:
        logger.warning(f"Unknown component: {component_name}")
        capabilities = []
        metadata.update({
            "description": f"Unknown component: {component_name}"
        })
        dependencies = []
    
    return StartUpInstructions(
        component_id=component_id,
        component_type=component_type,
        data_directory=data_directory,
        dependencies=dependencies,
        register=True,
        capabilities=capabilities,
        metadata=metadata
    )