"""Prompt Engine for Rhetor.

This module provides tools for creating, managing, and optimizing prompts for different AI models.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)

class PromptTemplate:
    """A template for generating prompts."""

    def __init__(
        self, 
        template: str, 
        variables: Optional[List[str]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        model_type: Optional[str] = None
    ):
        """Initialize a prompt template.
        
        Args:
            template: The template string with placeholders {variable_name}
            variables: List of variable names expected in the template
            name: Optional name for the template
            description: Optional description of the template
            model_type: Optional model type this template is optimized for
        """
        self.template = template
        self.variables = variables or []
        self.name = name
        self.description = description
        self.model_type = model_type
        
        # Validate that all variables in the template are in the variables list
        self._validate_variables()
    
    def _validate_variables(self) -> None:
        """Validate that all variables used in the template are declared."""
        import re
        # Find all {variable} patterns in the template
        pattern = r'\{([^{}]*)\}'
        template_vars = set(re.findall(pattern, self.template))
        
        # Check if any variables are missing from the declared list
        missing_vars = template_vars - set(self.variables)
        if missing_vars:
            self.variables.extend(list(missing_vars))
            logger.warning(f"Added missing variables to template: {missing_vars}")
    
    def format(self, **kwargs) -> str:
        """Format the template with the provided variables.
        
        Args:
            **kwargs: The variables to use in formatting
            
        Returns:
            The formatted prompt
            
        Raises:
            KeyError: If a required variable is missing
        """
        # Check for missing variables
        missing_vars = set(self.variables) - set(kwargs.keys())
        if missing_vars:
            raise KeyError(f"Missing required variables: {missing_vars}")
        
        # Format the template
        return self.template.format(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the template to a dictionary for serialization."""
        return {
            "template": self.template,
            "variables": self.variables,
            "name": self.name,
            "description": self.description,
            "model_type": self.model_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """Create a template from a dictionary."""
        return cls(
            template=data["template"],
            variables=data.get("variables", []),
            name=data.get("name"),
            description=data.get("description"),
            model_type=data.get("model_type")
        )


class PromptLibrary:
    """A library of prompt templates."""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """Initialize a prompt library.
        
        Args:
            templates_dir: Directory to load templates from
        """
        self.templates: Dict[str, PromptTemplate] = {}
        
        # Load templates from directory if provided
        if templates_dir:
            self.load_from_directory(templates_dir)
    
    def add_template(self, name: str, template: PromptTemplate) -> None:
        """Add a template to the library."""
        self.templates[name] = template
    
    def get_template(self, name: str) -> PromptTemplate:
        """Get a template by name."""
        if name not in self.templates:
            raise KeyError(f"Template '{name}' not found")
        return self.templates[name]
    
    def save_to_directory(self, directory: str) -> None:
        """Save all templates to a directory.
        
        Args:
            directory: Directory to save templates to
        """
        directory_path = Path(directory)
        directory_path.mkdir(parents=True, exist_ok=True)
        
        for name, template in self.templates.items():
            file_path = directory_path / f"{name}.json"
            with open(file_path, 'w') as f:
                json.dump(template.to_dict(), f, indent=2)
    
    def load_from_directory(self, directory: str) -> None:
        """Load templates from a directory.
        
        Args:
            directory: Directory to load templates from
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            logger.warning(f"Templates directory {directory} does not exist")
            return
        
        for file_path in directory_path.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                template = PromptTemplate.from_dict(data)
                self.add_template(file_path.stem, template)
                logger.info(f"Loaded template '{file_path.stem}' from {file_path}")
            except Exception as e:
                logger.error(f"Error loading template from {file_path}: {e}")


class PromptEngine:
    """Engine for managing and optimizing prompts for different models."""
    
    def __init__(self, library: Optional[PromptLibrary] = None):
        """Initialize the prompt engine.
        
        Args:
            library: Optional prompt library to use
        """
        self.library = library or PromptLibrary()
        self.personality_traits: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default personality traits
        self._initialize_default_personalities()
    
    def _initialize_default_personalities(self) -> None:
        """Initialize default personality traits for components."""
        self.personality_traits = {
            "engram": {
                "tone": "technical",
                "focus": "memory and context",
                "style": "precise",
                "personality": "organized and methodical"
            },
            "hermes": {
                "tone": "efficient",
                "focus": "system communication",
                "style": "concise",
                "personality": "reliable and consistent"
            },
            "prometheus": {
                "tone": "analytical",
                "focus": "planning and foresight",
                "style": "structured",
                "personality": "strategic and forward-thinking"
            },
            "ergon": {
                "tone": "action-oriented",
                "focus": "task execution",
                "style": "direct",
                "personality": "pragmatic and results-driven"
            },
            "rhetor": {
                "tone": "eloquent",
                "focus": "effective communication",
                "style": "adaptable",
                "personality": "perceptive and articulate"
            },
            "telos": {
                "tone": "consultative",
                "focus": "user needs and goals",
                "style": "interactive",
                "personality": "attentive and service-oriented"
            },
            "sophia": {
                "tone": "inquisitive",
                "focus": "learning and improvement",
                "style": "thoughtful",
                "personality": "curious and growth-oriented"
            },
            "athena": {
                "tone": "informative",
                "focus": "knowledge and wisdom",
                "style": "comprehensive",
                "personality": "insightful and knowledgeable"
            }
        }
    
    def get_component_personality(self, component_name: str) -> Dict[str, Any]:
        """Get the personality traits for a component."""
        return self.personality_traits.get(component_name.lower(), {})
    
    def set_component_personality(self, component_name: str, traits: Dict[str, Any]) -> None:
        """Set the personality traits for a component."""
        self.personality_traits[component_name.lower()] = traits
    
    def generate_prompt(self, template_name: str, component_name: Optional[str] = None, **kwargs) -> str:
        """Generate a prompt using a template and optionally adapt it for a component personality.
        
        Args:
            template_name: Name of the template to use
            component_name: Optional component to adapt the prompt for
            **kwargs: Variables to use in the template
            
        Returns:
            The formatted prompt
        """
        template = self.library.get_template(template_name)
        
        # Format the basic prompt
        prompt = template.format(**kwargs)
        
        # Adapt for component personality if specified
        if component_name:
            prompt = self._adapt_for_component(prompt, component_name)
        
        return prompt
    
    def _adapt_for_component(self, prompt: str, component_name: str) -> str:
        """Adapt a prompt for a specific component's personality."""
        traits = self.get_component_personality(component_name)
        if not traits:
            return prompt
        
        # Simple adaptation: Add personality guidance at the end of the prompt
        personality_note = (
            f"\n\nNote: As {component_name}, maintain a {traits.get('tone', 'neutral')} tone "
            f"with a focus on {traits.get('focus', 'the task at hand')}. "
            f"Your communication style should be {traits.get('style', 'straightforward')} "
            f"and your personality should be {traits.get('personality', 'professional')}."
        )
        
        return prompt + personality_note
    
    def create_system_prompt(self, component_name: str, role_description: str, 
                           capabilities: List[str], constraints: Optional[List[str]] = None) -> str:
        """Create a system prompt for a component.
        
        Args:
            component_name: Name of the component
            role_description: Description of the component's role
            capabilities: List of component capabilities
            constraints: Optional list of constraints
            
        Returns:
            A system prompt
        """
        traits = self.get_component_personality(component_name)
        
        # Build the system prompt
        prompt = [
            f"# {component_name.title()} - Tekton AI Component",
            f"\n## Role\n{role_description}",
            "\n## Capabilities"
        ]
        
        # Add capabilities
        for capability in capabilities:
            prompt.append(f"- {capability}")
        
        # Add constraints if provided
        if constraints:
            prompt.append("\n## Constraints")
            for constraint in constraints:
                prompt.append(f"- {constraint}")
        
        # Add personality guidance
        if traits:
            prompt.append("\n## Communication Style")
            prompt.append(f"- Tone: {traits.get('tone', 'neutral')}")
            prompt.append(f"- Focus: {traits.get('focus', 'task-oriented')}")
            prompt.append(f"- Style: {traits.get('style', 'professional')}")
            prompt.append(f"- Personality: {traits.get('personality', 'helpful')}")
        
        # Add Tekton collaboration note
        prompt.append("\n## Collaboration")
        prompt.append("You are part of the Tekton AI ecosystem, working collaboratively with other specialized components:")
        prompt.append("- Engram: Memory and context management")
        prompt.append("- Hermes: Database services and communication")
        prompt.append("- Prometheus: Planning and foresight")
        prompt.append("- Ergon: Task execution and agent management")
        prompt.append("- Rhetor: Communication and prompt engineering")
        prompt.append("- Telos: User needs and requirements management")
        prompt.append("- Sophia: Learning and improvement")
        prompt.append("- Athena: Knowledge representation")
        
        return "\n".join(prompt)

    async def register_with_hermes(self, service_registry=None) -> bool:
        """Register Rhetor with the Hermes service registry.
        
        Args:
            service_registry: Optional service registry instance
            
        Returns:
            Success status
        """
        try:
            # Try to import the service registry if not provided
            if service_registry is None:
                try:
                    from hermes.core.service_discovery import ServiceRegistry
                    service_registry = ServiceRegistry()
                    await service_registry.start()
                except ImportError:
                    logger.error("Could not import Hermes ServiceRegistry")
                    return False
            
            # Register Rhetor
            success = await service_registry.register(
                service_id="rhetor",
                name="Rhetor",
                version=__import__("rhetor").__version__,
                capabilities=["prompt_engineering", "communication", "personality_management"],
                metadata={
                    "component_type": "core",
                    "description": "AI communication specialist"
                }
            )
            
            if success:
                logger.info("Registered Rhetor with Hermes service registry")
            else:
                logger.warning("Failed to register Rhetor with Hermes")
            
            return success
        
        except Exception as e:
            logger.error(f"Error registering with Hermes: {e}")
            return False


class ContextManager:
    """Manager for AI contexts across components."""
    
    def __init__(self):
        """Initialize the context manager."""
        self.contexts = {}
    
    def create_context(self, name: str, context_data: Dict[str, Any]) -> None:
        """Create a new context."""
        self.contexts[name] = context_data
    
    def get_context(self, name: str) -> Dict[str, Any]:
        """Get a context by name."""
        return self.contexts.get(name, {})
    
    def update_context(self, name: str, updates: Dict[str, Any]) -> None:
        """Update an existing context."""
        if name in self.contexts:
            self.contexts[name].update(updates)
    
    def merge_contexts(self, names: List[str]) -> Dict[str, Any]:
        """Merge multiple contexts."""
        merged = {}
        for name in names:
            if name in self.contexts:
                merged.update(self.contexts[name])
        return merged