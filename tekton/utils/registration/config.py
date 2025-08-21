"""
Configuration loading and validation for component registration.
"""

import os
from shared.env import TektonEnviron
import yaml
import logging
from typing import Dict, Any, List, Optional

from .models import ComponentConfig, dict_to_component_config


logger = logging.getLogger(__name__)


def find_config_file(component_id: str) -> Optional[str]:
    """
    Find the configuration file for a component.
    
    Args:
        component_id: The ID of the component
        
    Returns:
        The path to the configuration file or None if not found
    """
    # Check in the current directory
    if os.path.exists(f"{component_id}.yaml"):
        return f"{component_id}.yaml"
    
    if os.path.exists(f"{component_id}.yml"):
        return f"{component_id}.yml"
    
    # Check in the config directory
    tekton_dir = TektonEnviron.get("TEKTON_ROOT")
    if tekton_dir:
        # Check in Tekton config directory
        config_dir = os.path.join(tekton_dir, "config", "components")
        if os.path.exists(config_dir):
            if os.path.exists(os.path.join(config_dir, f"{component_id}.yaml")):
                return os.path.join(config_dir, f"{component_id}.yaml")
            
            if os.path.exists(os.path.join(config_dir, f"{component_id}.yml")):
                return os.path.join(config_dir, f"{component_id}.yml")
    
    # Check in component directory
    if tekton_dir and os.path.exists(os.path.join(tekton_dir, component_id)):
        component_dir = os.path.join(tekton_dir, component_id)
        
        # Check in component root
        if os.path.exists(os.path.join(component_dir, f"{component_id}.yaml")):
            return os.path.join(component_dir, f"{component_id}.yaml")
        
        if os.path.exists(os.path.join(component_dir, f"{component_id}.yml")):
            return os.path.join(component_dir, f"{component_id}.yml")
        
        # Check in component config directory
        config_dir = os.path.join(component_dir, "config")
        if os.path.exists(config_dir):
            if os.path.exists(os.path.join(config_dir, f"{component_id}.yaml")):
                return os.path.join(config_dir, f"{component_id}.yaml")
            
            if os.path.exists(os.path.join(config_dir, f"{component_id}.yml")):
                return os.path.join(config_dir, f"{component_id}.yml")
    
    # Not found
    return None


def load_component_config(component_id: str, config_file: Optional[str] = None) -> ComponentConfig:
    """
    Load the configuration for a component.
    
    Args:
        component_id: The ID of the component
        config_file: Optional path to the configuration file
        
    Returns:
        The component configuration
        
    Raises:
        FileNotFoundError: If the configuration file is not found
        ValueError: If the configuration is invalid
    """
    if not config_file:
        config_file = find_config_file(component_id)
        
    if not config_file:
        raise FileNotFoundError(f"Configuration file for component '{component_id}' not found")
    
    try:
        with open(config_file, "r") as f:
            config_data = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"Failed to load configuration file: {e}")
    
    # Validate the configuration
    if not isinstance(config_data, dict):
        raise ValueError("Configuration must be a dictionary")
    
    if "component" not in config_data:
        raise ValueError("Configuration must have a 'component' section")
    
    # Convert to ComponentConfig
    try:
        component_config = dict_to_component_config(config_data)
    except Exception as e:
        raise ValueError(f"Failed to parse configuration: {e}")
    
    # Ensure component ID matches
    if component_config.id != component_id:
        logger.warning(
            f"Component ID in configuration ({component_config.id}) "
            f"does not match requested ID ({component_id})"
        )
    
    return component_config


def validate_component_config(config: ComponentConfig) -> List[str]:
    """
    Validate a component configuration.
    
    Args:
        config: The component configuration to validate
        
    Returns:
        A list of validation errors (empty if valid)
    """
    errors = []
    
    # Validate component ID
    if not config.id:
        errors.append("Component ID is required")
    elif not config.id.isalnum() and not "_" in config.id:
        errors.append("Component ID must be alphanumeric (can include underscores)")
    
    # Validate component name
    if not config.name:
        errors.append("Component name is required")
    
    # Validate component version
    if not config.version:
        errors.append("Component version is required")
    
    # Validate port
    if not isinstance(config.port, int):
        errors.append("Port must be an integer")
    elif not (1024 <= config.port <= 65535):
        errors.append("Port must be between 1024 and 65535")
    
    # Validate capabilities
    capability_ids = set()
    for i, capability in enumerate(config.capabilities):
        # Validate capability ID
        if not capability.id:
            errors.append(f"Capability {i + 1} ID is required")
        elif capability.id in capability_ids:
            errors.append(f"Duplicate capability ID: {capability.id}")
        else:
            capability_ids.add(capability.id)
        
        # Validate capability name
        if not capability.name:
            errors.append(f"Name for capability '{capability.id}' is required")
        
        # Validate methods
        method_ids = set()
        for j, method in enumerate(capability.methods):
            # Validate method ID
            if not method.id:
                errors.append(f"Method {j + 1} ID is required for capability '{capability.id}'")
            elif method.id in method_ids:
                errors.append(f"Duplicate method ID '{method.id}' in capability '{capability.id}'")
            else:
                method_ids.add(method.id)
            
            # Validate method name
            if not method.name:
                errors.append(f"Name for method '{method.id}' in capability '{capability.id}' is required")
    
    return errors


def generate_component_config_template(component_id: str, name: str, port: int) -> Dict[str, Any]:
    """
    Generate a template component configuration.
    
    Args:
        component_id: The ID of the component
        name: The name of the component
        port: The port the component listens on
        
    Returns:
        A dictionary with the template configuration
    """
    return {
        "component": {
            "id": component_id,
            "name": name,
            "version": "0.1.0",
            "description": f"The {name} component of the Tekton ecosystem",
            "port": port
        },
        "capabilities": [
            {
                "id": "example_capability",
                "name": "Example Capability",
                "description": "An example capability",
                "methods": [
                    {
                        "id": "example_method",
                        "name": "Example Method",
                        "description": "An example method",
                        "parameters": [
                            {
                                "name": "param_name",
                                "type": "string",
                                "required": True,
                                "description": "An example parameter"
                            }
                        ],
                        "returns": {
                            "type": "object",
                            "description": "An example return value"
                        }
                    }
                ]
            }
        ],
        "config": {
            "example_config_key": "example_value"
        }
    }