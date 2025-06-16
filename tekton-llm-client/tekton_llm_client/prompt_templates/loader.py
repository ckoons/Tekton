"""
Template loader for Tekton LLM Client.

This module provides utilities for loading prompt templates from files or
directories.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
import importlib.resources

from .registry import PromptTemplate

logger = logging.getLogger(__name__)

def load_template(source: str, name: Optional[str] = None) -> PromptTemplate:
    """
    Load a template from a file or resource.
    
    Args:
        source: Path to a template file or a resource path
        name: Optional name for the template (defaults to filename without extension)
            
    Returns:
        PromptTemplate object
        
    Raises:
        FileNotFoundError: If template file not found
        ValueError: If template data is invalid
    """
    # Check if it's a file path
    if os.path.exists(source):
        return _load_from_file(source, name)
        
    # Check if it's a package resource
    try:
        # Try to load from package resources
        template_text = _load_from_resources(source)
        
        # Determine name if not provided
        if name is None:
            name = os.path.basename(source)
            if name.endswith('.json') or name.endswith('.txt'):
                name = name.rsplit('.', 1)[0]
                
        # Determine if it's JSON or plain text
        if source.endswith('.json'):
            try:
                template_data = json.loads(template_text)
                template_data['name'] = template_data.get('name', name)
                return PromptTemplate(**template_data)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse '{source}' as JSON, treating as plain text template")
                return PromptTemplate(name=name, template=template_text)
        else:
            # Treat as plain text template
            return PromptTemplate(name=name, template=template_text)
            
    except Exception as e:
        raise FileNotFoundError(f"Template not found: {source}") from e

def _load_from_file(file_path: str, name: Optional[str] = None) -> PromptTemplate:
    """
    Load a template from a file.
    
    Args:
        file_path: Path to a template file (JSON or text)
        name: Optional name for the template
            
    Returns:
        PromptTemplate object
        
    Raises:
        FileNotFoundError: If template file not found
        ValueError: If template data is invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Template file not found: {file_path}")
        
    # Determine name if not provided
    if name is None:
        name = os.path.basename(file_path)
        if name.endswith('.json') or name.endswith('.txt'):
            name = name.rsplit('.', 1)[0]
    
    try:
        # Determine if it's JSON or plain text
        if file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                try:
                    template_data = json.load(f)
                    template_data['name'] = template_data.get('name', name)
                    return PromptTemplate(**template_data)
                except json.JSONDecodeError:
                    # Not valid JSON, treat as plain text
                    f.seek(0)
                    return PromptTemplate(name=name, template=f.read())
        else:
            # Treat as plain text template
            with open(file_path, 'r') as f:
                return PromptTemplate(name=name, template=f.read())
    except Exception as e:
        raise ValueError(f"Error loading template from {file_path}: {str(e)}") from e

def _load_from_resources(resource_path: str) -> str:
    """
    Load a template from a package resource.
    
    Args:
        resource_path: Resource path in the format 'package.subpackage:filename'
            
    Returns:
        Template content as string
        
    Raises:
        FileNotFoundError: If resource not found
    """
    try:
        if ':' in resource_path:
            package_name, filename = resource_path.split(':', 1)
            return importlib.resources.read_text(package_name, filename)
        else:
            # Try to load from the templates package
            return importlib.resources.read_text(
                'tekton_llm_client.prompt_templates.templates', 
                resource_path
            )
    except Exception as e:
        raise FileNotFoundError(f"Resource not found: {resource_path}") from e

def load_templates_from_directory(directory: str) -> Dict[str, PromptTemplate]:
    """
    Load all templates from a directory.
    
    Args:
        directory: Directory containing template files
            
    Returns:
        Dictionary of template name to PromptTemplate object
    """
    if not os.path.exists(directory):
        logger.warning(f"Templates directory not found: {directory}")
        return {}
        
    templates = {}
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        if os.path.isfile(file_path) and (filename.endswith('.json') or filename.endswith('.txt')):
            try:
                name = filename.rsplit('.', 1)[0]  # Remove extension
                template = load_template(file_path, name)
                templates[template.name] = template
            except Exception as e:
                logger.error(f"Error loading template from {file_path}: {str(e)}")
                
    return templates