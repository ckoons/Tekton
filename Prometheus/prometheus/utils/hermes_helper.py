"""
Hermes Helper

This module provides helper functions for integrating with the Hermes service registry.
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.global_config import GlobalConfig

# Configure logging
logger = logging.getLogger("prometheus.utils.hermes_helper")


async def register_with_hermes(
    component_id: str,
    component_name: str,
    component_type: str,
    capabilities: List[Dict[str, Any]],
    endpoint: str,
    description: Optional[str] = None,
    dependencies: Optional[List[str]] = None,
    hermes_url: Optional[str] = None,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Register a component with Hermes.
    
    Args:
        component_id: ID of the component
        component_name: Name of the component
        component_type: Type of the component
        capabilities: List of capabilities
        endpoint: API endpoint for the component
        description: Optional description of the component
        dependencies: Optional list of dependencies
        hermes_url: Optional URL of Hermes API
        additional_metadata: Optional additional metadata
        
    Returns:
        True if registration was successful, False otherwise
    """
    try:
        # Try to import from tekton-core
        try:
            from tekton.utils.hermes_registration import register_component
            
            # Register component
            result = await register_component(
                component_id=component_id,
                component_name=component_name,
                component_type=component_type,
                component_version="0.1.0",
                capabilities=capabilities,
                hermes_url=hermes_url,
                endpoint=endpoint,
                dependencies=dependencies,
                additional_metadata=additional_metadata
            )
            
            if result:
                logger.info(f"Registered {component_name} with Hermes")
                return True
            else:
                logger.error(f"Failed to register {component_name} with Hermes")
                return False
                
        except ImportError:
            logger.warning("Could not import Hermes registration utilities from tekton-core.")
            
            # Try to import from Hermes directly
            try:
                # Try to find Hermes
                hermes_dir = None
                if True:  # Always use path resolution instead of env var
                    import sys
                    from pathlib import Path
                    
                    script_dir = Path(__file__).parent.parent.parent.absolute()
                    potential_hermes_dir = os.path.normpath(os.path.join(script_dir, "../Hermes"))
                    
                    if os.path.exists(potential_hermes_dir):
                        hermes_dir = potential_hermes_dir
                        sys.path.insert(0, hermes_dir)
                
                from hermes.core.service_discovery import ServiceRegistry
                
                # Start service registry
                registry = ServiceRegistry()
                await registry.start()
                
                # Convert capabilities to simple list
                simple_capabilities = []
                for cap in capabilities:
                    simple_capabilities.append(cap["name"])
                
                # Build metadata
                metadata = {
                    "description": description or f"{component_name} component",
                    "version": "0.1.0",
                    "dependencies": dependencies or []
                }
                if additional_metadata:
                    metadata.update(additional_metadata)
                
                # Register component
                success = await registry.register(
                    service_id=component_id,
                    name=component_name,
                    version="0.1.0",
                    endpoint=endpoint,
                    capabilities=simple_capabilities,
                    metadata=metadata
                )
                
                if success:
                    logger.info(f"Registered {component_name} with Hermes service registry")
                    await registry.stop()
                    return True
                else:
                    logger.error(f"Failed to register {component_name} with Hermes")
                    await registry.stop()
                    return False
                    
            except ImportError as e:
                logger.error(f"Could not import Hermes modules: {e}")
                return False
                
    except Exception as e:
        logger.error(f"Error registering with Hermes: {e}")
        return False


async def prometheus_capabilities() -> List[Dict[str, Any]]:
    """
    Get Prometheus forward planning capabilities.
    
    Returns:
        List of capability definitions
    """
    return [
        {
            "name": "create_plan",
            "description": "Create a plan for a specified objective",
            "parameters": {
                "objective": "string",
                "context": "object (optional)",
                "complexity_threshold": "number (optional)",
                "max_iterations": "number (optional)"
            }
        },
        {
            "name": "create_plan_from_requirements",
            "description": "Create a plan from a set of requirements",
            "parameters": {
                "project_id": "string",
                "plan_name": "string",
                "methodology": "string"
            }
        },
        {
            "name": "get_plan",
            "description": "Get a plan by ID",
            "parameters": {
                "plan_id": "string"
            }
        },
        {
            "name": "update_plan",
            "description": "Update a plan",
            "parameters": {
                "plan_id": "string",
                "updates": "object"
            }
        },
        {
            "name": "allocate_resources",
            "description": "Allocate resources to a plan",
            "parameters": {
                "plan_id": "string",
                "allocations": "object"
            }
        },
        {
            "name": "generate_timeline",
            "description": "Generate a timeline for a plan",
            "parameters": {
                "plan_id": "string"
            }
        },
        {
            "name": "calculate_critical_path",
            "description": "Calculate the critical path for a plan",
            "parameters": {
                "plan_id": "string"
            }
        }
    ]


async def epimethius_capabilities() -> List[Dict[str, Any]]:
    """
    Get Epimethius retrospective analysis capabilities.
    
    Returns:
        List of capability definitions
    """
    return [
        {
            "name": "create_retrospective",
            "description": "Create a retrospective for a plan",
            "parameters": {
                "plan_id": "string",
                "name": "string",
                "format": "string",
                "facilitator": "string"
            }
        },
        {
            "name": "analyze_performance",
            "description": "Analyze performance data for a plan",
            "parameters": {
                "plan_id": "string",
                "metrics": "array (optional)"
            }
        },
        {
            "name": "identify_patterns",
            "description": "Identify patterns in retrospective data",
            "parameters": {
                "retrospective_id": "string"
            }
        },
        {
            "name": "generate_improvements",
            "description": "Generate improvement suggestions",
            "parameters": {
                "source_type": "string",
                "source_id": "string"
            }
        },
        {
            "name": "track_improvement_progress",
            "description": "Track improvement progress",
            "parameters": {
                "filters": "object (optional)"
            }
        },
        {
            "name": "analyze_historical_data",
            "description": "Analyze historical data",
            "parameters": {
                "filters": "object"
            }
        }
    ]