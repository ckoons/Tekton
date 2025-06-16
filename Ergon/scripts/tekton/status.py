#!/usr/bin/env python3
"""
Tekton Component Status

Contains functions for checking and displaying Tekton component status.
"""

import sys
import logging
from typing import Dict, Any

from .components import COMPONENTS, running_components, running_lock

# Initialize imports needed for status
try:
    # Import Ergon modules
    from ergon.utils.config.settings import settings
except ImportError as e:
    logging.error(f"Error importing Ergon modules: {e}")
    logging.error("Please make sure Ergon is installed correctly.")
    sys.exit(1)

logger = logging.getLogger("tekton.status")

def get_component_status() -> Dict[str, Dict[str, Any]]:
    """
    Get the status of all components.
    
    Returns:
        Dictionary of component status information
    """
    status = {}
    
    with running_lock:
        for component_id, component in COMPONENTS.items():
            status[component_id] = {
                "name": component["name"],
                "description": component["description"],
                "running": component_id in running_components,
                "optional": component.get("optional", False),
                "startup_sequence": component["startup_sequence"]
            }
    
    return status

def print_component_status(status: Dict[str, Dict[str, Any]]) -> None:
    """
    Print the status of all components.
    
    Args:
        status: Dictionary of component status information
    """
    print("\nTekton Component Status:")
    print("========================")
    
    # Get components in startup order
    component_ids = sorted(
        status.keys(),
        key=lambda c: status[c]["startup_sequence"]
    )
    
    for component_id in component_ids:
        component = status[component_id]
        running_status = "✅ Running" if component["running"] else "❌ Stopped"
        optional_tag = " (Optional)" if component.get("optional", False) else ""
        
        print(f"{component['name']}{optional_tag}: {running_status}")
        print(f"  {component['description']}")
    
    print("")

def print_system_info():
    """Print system information about the Tekton environment."""
    print("System Information:")
    print(f"Tekton Home: {settings.tekton_home}")
    print(f"Database Path: {settings.database_url.replace('sqlite:///', '')}")
    print(f"Vector Store Path: {settings.vector_db_path}")
    
    # Show API key availability
    if settings.has_anthropic:
        print("Anthropic API: Available")
    else:
        print("Anthropic API: Not configured")
        
    if settings.has_openai:
        print("OpenAI API: Available")
    else:
        print("OpenAI API: Not configured")
        
    if settings.has_ollama:
        print("Ollama: Available")
    else:
        print("Ollama: Not available")