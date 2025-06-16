"""
Registry for LLM prompt templates.
"""

import os
import json
from typing import Dict, Any, Optional, List, ClassVar, Union
from pydantic import BaseModel
import jinja2
import logging

logger = logging.getLogger(__name__)

class PromptTemplate(BaseModel):
    """
    A template for LLM prompts with variable substitution using Jinja2.
    """
    
    name: str
    template: str
    description: Optional[str] = None
    version: str = "1.0.0"
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    
    def render(self, variables: Dict[str, Any] = None, **kwargs) -> str:
        """
        Render the template with the provided variables.
        
        Args:
            variables: Dictionary of variables to use in the template
            **kwargs: Additional variables to use in the template
            
        Returns:
            Rendered template as a string
        """
        variables = variables or {}
        variables.update(kwargs)
        
        # Create Jinja2 environment
        env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        try:
            # Create template from string
            jinja_template = env.from_string(self.template)
            
            # Render template with variables
            return jinja_template.render(**variables)
        except Exception as e:
            logger.error(f"Error rendering template '{self.name}': {str(e)}")
            # Return template with error message
            return f"ERROR: Failed to render template '{self.name}': {str(e)}"

class PromptTemplateRegistry:
    """
    Registry for managing prompt templates.
    
    This registry provides methods to register, retrieve, and manage
    prompt templates used throughout the Tekton ecosystem.
    """
    
    DEFAULT_TEMPLATES: ClassVar[Dict[str, Dict[str, Any]]] = {
        "general_system": {
            "template": "You are a helpful assistant that provides accurate and concise responses.",
            "description": "General-purpose system prompt for standard assistant interactions."
        },
        "code_assistant": {
            "template": "You are a coding assistant that helps with programming tasks. Focus on providing clear, efficient code with explanations when needed.",
            "description": "System prompt for code-related tasks."
        },
        "concise_response": {
            "template": "You are a helpful assistant that provides accurate and concise responses. Keep your answers brief and to the point.",
            "description": "System prompt for obtaining concise responses."
        },
        "json_response": {
            "template": "You are a helpful assistant that provides responses in JSON format only. Always ensure your entire response can be parsed as valid JSON.",
            "description": "System prompt for JSON-formatted responses."
        },
        "structured_extraction": {
            "template": """You are a data extraction assistant. Extract the requested information from the provided content.
            
Extraction format: {{ format }}

Content to extract from:
{{ content }}

Information to extract:
{{ extraction_target }}

Only include the requested information in your response, formatted according to the specified format.""",
            "description": "Template for structured data extraction tasks."
        }
    }
    
    def __init__(self, templates_dir: Optional[str] = None, load_defaults: bool = True):
        """
        Initialize the prompt template registry.
        
        Args:
            templates_dir: Directory containing template files (YAML or JSON)
            load_defaults: Whether to load the default templates
        """
        self.templates: Dict[str, PromptTemplate] = {}
        self.templates_dir = templates_dir
        
        # Load default templates
        if load_defaults:
            self._load_default_templates()
            
        # Load templates from directory if provided
        if templates_dir:
            self._load_templates_from_directory()
    
    def _load_default_templates(self) -> None:
        """Load default templates into the registry."""
        for name, template_data in self.DEFAULT_TEMPLATES.items():
            template = PromptTemplate(
                name=name,
                template=template_data["template"],
                description=template_data.get("description", ""),
                tags=template_data.get("tags", []),
                metadata=template_data.get("metadata", {})
            )
            self.templates[name] = template
            
    def _load_templates_from_directory(self) -> None:
        """Load templates from the specified directory."""
        if not self.templates_dir or not os.path.exists(self.templates_dir):
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return
            
        # Load templates from JSON files
        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.templates_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        template_data = json.load(f)
                        
                    # Check if it's a single template or a collection
                    if "name" in template_data and "template" in template_data:
                        # Single template
                        template = PromptTemplate(**template_data)
                        self.templates[template.name] = template
                    elif isinstance(template_data, dict):
                        # Collection of templates
                        for name, data in template_data.items():
                            if isinstance(data, dict) and "template" in data:
                                data["name"] = data.get("name", name)  # Use key as name if not provided
                                template = PromptTemplate(**data)
                                self.templates[name] = template
                except Exception as e:
                    logger.error(f"Error loading template from {file_path}: {str(e)}")
    
    def register(self, template: Union[PromptTemplate, Dict[str, Any]]) -> str:
        """
        Register a new template or update an existing one.
        
        Args:
            template: Template object or dictionary with template data
            
        Returns:
            Name of the registered template
        """
        if isinstance(template, dict):
            if "name" not in template or "template" not in template:
                raise ValueError("Template must include 'name' and 'template' fields")
            template = PromptTemplate(**template)
            
        self.templates[template.name] = template
        return template.name
    
    def get(self, name: str) -> Optional[PromptTemplate]:
        """
        Get a template by name.
        
        Args:
            name: Name of the template to retrieve
            
        Returns:
            PromptTemplate object or None if not found
        """
        return self.templates.get(name)
    
    def render(self, name: str, variables: Dict[str, Any] = None, **kwargs) -> str:
        """
        Render a template by name with variables.
        
        Args:
            name: Name of the template to render
            variables: Dictionary of variables for rendering
            **kwargs: Additional variables for rendering
            
        Returns:
            Rendered template as a string
            
        Raises:
            ValueError: If template not found
        """
        template = self.get(name)
        if not template:
            raise ValueError(f"Template not found: {name}")
            
        return template.render(variables, **kwargs)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all registered templates.
        
        Returns:
            List of template metadata dictionaries
        """
        return [
            {
                "name": t.name,
                "description": t.description,
                "version": t.version,
                "tags": t.tags
            }
            for t in self.templates.values()
        ]
    
    def remove(self, name: str) -> bool:
        """
        Remove a template from the registry.
        
        Args:
            name: Name of the template to remove
            
        Returns:
            True if template was removed, False if not found
        """
        if name in self.templates:
            del self.templates[name]
            return True
        return False
    
    def save_to_file(self, name: str, file_path: str) -> bool:
        """
        Save a template to a file.
        
        Args:
            name: Name of the template to save
            file_path: Path to save the template to
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If template not found
        """
        template = self.get(name)
        if not template:
            raise ValueError(f"Template not found: {name}")
            
        try:
            with open(file_path, 'w') as f:
                json.dump(template.model_dump(), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving template to {file_path}: {str(e)}")
            return False
    
    def save_all(self, directory: str) -> int:
        """
        Save all templates to a directory.
        
        Args:
            directory: Directory to save templates to
            
        Returns:
            Number of templates saved
        """
        os.makedirs(directory, exist_ok=True)
        
        count = 0
        for name, template in self.templates.items():
            file_path = os.path.join(directory, f"{name}.json")
            if self.save_to_file(name, file_path):
                count += 1
                
        return count