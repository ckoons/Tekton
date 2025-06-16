#!/usr/bin/env python3
"""
Fix for the PromptTemplateRegistry in Rhetor.

This module monkey-patches the tekton-llm-client PromptTemplateRegistry class to add
the missing load_from_directory method. This is a temporary fix until the FastMCP sprint
can properly align the interfaces.
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional, List
import importlib

logger = logging.getLogger(__name__)

def apply_fix():
    """Apply the fix to the PromptTemplateRegistry class."""
    try:
        # Get the PromptTemplateRegistry class
        from tekton_llm_client import PromptTemplateRegistry
        
        # Check if the method already exists
        if hasattr(PromptTemplateRegistry, 'load_from_directory'):
            logger.info("PromptTemplateRegistry already has load_from_directory method")
            return True
        
        # Define the missing method
        def load_from_directory(self, directory: str) -> int:
            """
            Load templates from a directory.
            
            Args:
                directory: Directory containing template files
                
            Returns:
                Number of templates loaded
            """
            logger.info(f"Loading templates from directory: {directory}")
            
            # Check if directory exists
            if not os.path.exists(directory):
                logger.warning(f"Directory not found: {directory}")
                return 0
                
            # Count loaded templates
            count = 0
            
            # Go through files in the directory
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                
                # Skip directories
                if os.path.isdir(filepath):
                    continue
                    
                # Skip non-template files
                if not (filename.endswith('.json') or filename.endswith('.yaml') or 
                        filename.endswith('.yml') or filename.endswith('.py')):
                    continue
                
                try:
                    # Handle Python files differently
                    if filename.endswith('.py'):
                        module_name = filename[:-3]  # Remove .py extension
                        spec = importlib.util.spec_from_file_location(module_name, filepath)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            
                            # Look for template definitions
                            for attr_name in dir(module):
                                if attr_name.endswith('_template') or attr_name.endswith('_templates'):
                                    templates = getattr(module, attr_name)
                                    if isinstance(templates, dict):
                                        self.register(templates)
                                        count += 1
                                    elif isinstance(templates, list):
                                        for template in templates:
                                            if isinstance(template, dict):
                                                self.register(template)
                                                count += 1
                    else:
                        # Handle JSON and YAML files
                        with open(filepath, 'r') as f:
                            if filename.endswith('.json'):
                                data = json.load(f)
                            else:  # YAML
                                data = yaml.safe_load(f)
                                
                            # Support both single template and list of templates
                            if isinstance(data, dict):
                                # Single template
                                if 'name' in data and ('template' in data or 'content' in data):
                                    self.register(data)
                                    count += 1
                                # Dictionary of templates by name
                                else:
                                    for name, template_data in data.items():
                                        if isinstance(template_data, dict):
                                            if 'template' in template_data or 'content' in template_data:
                                                template_data['name'] = name
                                                self.register(template_data)
                                                count += 1
                            elif isinstance(data, list):
                                # List of templates
                                for template in data:
                                    if isinstance(template, dict) and 'name' in template and ('template' in template or 'content' in template):
                                        self.register(template)
                                        count += 1
                                        
                except Exception as e:
                    logger.error(f"Error loading template from {filepath}: {e}")
            
            logger.info(f"Loaded {count} templates from {directory}")
            return count
        
        # Add the method to the class
        PromptTemplateRegistry.load_from_directory = load_from_directory
        
        logger.info("Added load_from_directory method to PromptTemplateRegistry")
        return True
        
    except Exception as e:
        logger.error(f"Failed to apply fix to PromptTemplateRegistry: {e}")
        return False

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    
    # Apply the fix
    success = apply_fix()
    print(f"Fix applied: {success}")