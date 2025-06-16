#!/usr/bin/env python3
"""
Component Registry Persistence Module

This module provides functionality for loading and saving registry state.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Tuple, Any, Optional

from ...lifecycle import ComponentRegistration

logger = logging.getLogger("tekton.component_lifecycle.registry.persistence")


async def load_registrations(data_dir: str) -> Tuple[Dict[str, ComponentRegistration], Dict[str, Dict[str, Any]]]:
    """
    Load component registrations from disk.
    
    Args:
        data_dir: Directory containing saved registrations
        
    Returns:
        Tuple of (components, instances)
    """
    components = {}
    instances = {}
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        logger.info(f"Data directory does not exist: {data_dir}")
        return components, instances
        
    # Load component registrations
    registrations_file = os.path.join(data_dir, "registrations.json")
    if os.path.exists(registrations_file):
        try:
            with open(registrations_file, "r") as f:
                data = json.load(f)
                
                # Process each component
                for component_data in data.get("components", []):
                    try:
                        # Create ComponentRegistration from data
                        component_id = component_data.get("component_id")
                        component = ComponentRegistration.from_dict(component_data)
                        
                        # Store component
                        components[component_id] = component
                        
                    except Exception as e:
                        logger.error(f"Error loading component: {e}")
                        
                # Load instance data
                instances = data.get("instances", {})
                
                logger.info(f"Loaded {len(components)} component registrations")
                
        except Exception as e:
            logger.error(f"Error loading registrations: {e}")
            
    return components, instances


async def save_registrations(components: Dict[str, ComponentRegistration], data_dir: str) -> bool:
    """
    Save component registrations to disk.
    
    Args:
        components: Component registrations
        data_dir: Directory to save registrations
        
    Returns:
        True if saved successfully
    """
    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    # Prepare data
    data = {
        "components": [],
        "instances": {}
    }
    
    # Add components
    for component_id, component in components.items():
        try:
            component_data = component.to_dict()
            data["components"].append(component_data)
            
        except Exception as e:
            logger.error(f"Error serializing component {component_id}: {e}")
            
    # Save to file
    registrations_file = os.path.join(data_dir, "registrations.json")
    temp_file = os.path.join(data_dir, "registrations.json.tmp")
    
    try:
        # Write to temporary file first
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2)
            
        # Atomic replace
        os.replace(temp_file, registrations_file)
        logger.debug(f"Saved {len(components)} component registrations")
        return True
        
    except Exception as e:
        logger.error(f"Error saving registrations: {e}")
        return False