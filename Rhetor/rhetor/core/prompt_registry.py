"""Prompt Registry for Rhetor.

This module provides a registry for managing system prompts with versioning,
component-specific customization, and evaluation tools.

It integrates with the tekton-llm-client PromptTemplateRegistry for enhanced features.
"""

import os
import json
import yaml
import logging
import shutil
import copy
from typing import Dict, List, Any, Optional, Union, Set
from pathlib import Path
from datetime import datetime
import uuid
import re

# Import enhanced LLM client features
from tekton_llm_client import (
    PromptTemplateRegistry, PromptTemplate, load_template,
    ClientSettings, LLMSettings, load_settings, get_env
)

from rhetor.core.template_manager import TemplateManager, Template

logger = logging.getLogger(__name__)

class PromptVersion:
    """Represents a specific version of a prompt with metadata."""

    def __init__(
        self,
        content: str,
        version_id: Optional[str] = None,
        created_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        component: Optional[str] = None
    ):
        """Initialize a prompt version.
        
        Args:
            content: The prompt content
            version_id: Unique identifier for this version
            created_at: Timestamp when this version was created
            metadata: Additional metadata for this version
            component: Component this prompt is for
        """
        self.content = content
        self.version_id = version_id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now().isoformat()
        self.metadata = metadata or {}
        self.component = component
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the version to a dictionary for serialization."""
        return {
            "content": self.content,
            "version_id": self.version_id,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "component": self.component
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptVersion':
        """Create a version from a dictionary."""
        return cls(
            content=data["content"],
            version_id=data.get("version_id"),
            created_at=data.get("created_at"),
            metadata=data.get("metadata", {}),
            component=data.get("component")
        )


class SystemPrompt:
    """A system prompt with versioning support."""

    def __init__(
        self,
        prompt_id: str,
        name: str,
        component: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        versions: Optional[List[PromptVersion]] = None,
        is_default: bool = False,
        parent_id: Optional[str] = None
    ):
        """Initialize a system prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt
            name: Human-readable name
            component: Component this prompt is for
            description: Optional description
            tags: Optional tags for categorization
            versions: List of versions
            is_default: Whether this is the default prompt for the component
            parent_id: Optional parent prompt ID for inheritance
        """
        self.prompt_id = prompt_id
        self.name = name
        self.component = component
        self.description = description or ""
        self.tags = tags or []
        self.versions = versions or []
        self.is_default = is_default
        self.parent_id = parent_id
        
        # Add initial version if none exist
        if not self.versions:
            self.versions.append(PromptVersion(
                content="",
                metadata={"created_by": "system", "note": "Initial empty version"},
                component=component
            ))
    
    @property
    def current_version(self) -> PromptVersion:
        """Get the current (latest) version of the prompt."""
        if not self.versions:
            raise ValueError(f"Prompt '{self.prompt_id}' has no versions")
        return self.versions[-1]
    
    @property
    def content(self) -> str:
        """Get the content of the current version."""
        return self.current_version.content
    
    def add_version(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PromptVersion:
        """Add a new version of the prompt.
        
        Args:
            content: The prompt content
            metadata: Additional metadata for this version
            
        Returns:
            The new version
        """
        # Create the new version
        version = PromptVersion(
            content=content,
            metadata=metadata or {},
            component=self.component
        )
        
        # Add to versions list
        self.versions.append(version)
        
        return version
    
    def get_version(self, version_id: str) -> Optional[PromptVersion]:
        """Get a specific version by ID.
        
        Args:
            version_id: ID of the version to get
            
        Returns:
            PromptVersion or None if not found
        """
        for version in self.versions:
            if version.version_id == version_id:
                return version
        return None
    
    def revert_to_version(
        self,
        version_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[PromptVersion]:
        """Revert to a previous version, creating a new version with the same content.
        
        Args:
            version_id: ID of the version to revert to
            metadata: Additional metadata for the new version
            
        Returns:
            The new version or None if target version not found
        """
        target_version = self.get_version(version_id)
        if not target_version:
            return None
        
        # Create metadata if not provided
        if not metadata:
            metadata = {
                "reverted_from": version_id,
                "revert_date": datetime.now().isoformat(),
                "note": f"Reverted to version {version_id}"
            }
        
        # Create new version with content from target
        return self.add_version(target_version.content, metadata)
    
    def to_dict(self, include_versions: bool = True) -> Dict[str, Any]:
        """Convert the prompt to a dictionary for serialization.
        
        Args:
            include_versions: Whether to include all versions
        
        Returns:
            Dictionary representation
        """
        result = {
            "prompt_id": self.prompt_id,
            "name": self.name,
            "component": self.component,
            "description": self.description,
            "tags": self.tags,
            "is_default": self.is_default,
            "parent_id": self.parent_id,
            "current_version": self.current_version.to_dict()
        }
        
        if include_versions:
            result["versions"] = [v.to_dict() for v in self.versions]
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemPrompt':
        """Create a prompt from a dictionary."""
        # Process versions if present
        versions = None
        if "versions" in data:
            versions = [PromptVersion.from_dict(v) for v in data["versions"]]
        
        # Create the template
        return cls(
            prompt_id=data["prompt_id"],
            name=data["name"],
            component=data["component"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
            is_default=data.get("is_default", False),
            parent_id=data.get("parent_id"),
            versions=versions
        )


class PromptRegistry:
    """Registry for managing system prompts with versioning and inheritance."""

    def __init__(self, base_dir: Optional[str] = None, template_manager: Optional[TemplateManager] = None):
        """Initialize the prompt registry.
        
        Args:
            base_dir: Base directory for prompt storage
            template_manager: Optional template manager for template integration
        """
        # Set default base directory if not provided
        if not base_dir:
            base_dir = os.path.join(
                os.environ.get('TEKTON_DATA_DIR', 
                              os.path.join(os.environ.get('TEKTON_ROOT', os.path.expanduser('~')), '.tekton', 'data')),
                'rhetor', 'prompts'
            )
        
        self.base_dir = Path(base_dir)
        self.template_manager = template_manager
        self.prompts: Dict[str, SystemPrompt] = {}
        
        # Create a tekton-llm-client PromptTemplateRegistry for enhanced features
        self.template_registry = PromptTemplateRegistry()
        
        # Load templates from the standard locations
        self._load_template_files()
        
        # Create prompt directories if they don't exist
        self._ensure_directories()
        
        # Load existing prompts
        self.load_all_prompts()
        
        # Create default prompts if they don't exist
        self._create_default_prompts()
    
    def _load_template_files(self):
        """Load template files from standard locations."""
        # Look for templates in the rhetor/templates directory
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "prompts")
        
        if os.path.exists(templates_dir):
            logger.info(f"Loading templates from {templates_dir}")
            try:
                # Try the different method names that might be available
                if hasattr(self.template_registry, 'load_templates_from_directory'):
                    self.template_registry.load_templates_from_directory(templates_dir)
                elif hasattr(self.template_registry, 'load_from_directory'):
                    self.template_registry.load_from_directory(templates_dir)
                else:
                    logger.warning("No template loading method available in PromptTemplateRegistry")
                logger.info(f"Template registry has {len(getattr(self.template_registry, 'templates', {}))} templates")
            except Exception as e:
                logger.warning(f"Failed to load templates from directory: {e}")
    
    def _ensure_directories(self) -> None:
        """Ensure all necessary directories exist."""
        # Create base directory
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_default_prompts(self) -> None:
        """Create default prompts for all core components if they don't exist."""
        # Define core components
        components = [
            "engram", "hermes", "prometheus", "ergon", "rhetor", 
            "telos", "sophia", "athena", "synthesis"
        ]
        
        # From rhetor/templates/system_prompts.py
        component_prompts = {
            "engram": {
                "role_description": "You are Engram, the memory system for the Tekton ecosystem. Your primary responsibility is managing persistent memory, context, and cognitive continuity across sessions and components.",
                "capabilities": "- Vector-based memory storage and retrieval\n- Semantic search capabilities\n- Memory categorization and organization\n- Context management across multiple AI models\n- Long-term persistent storage\n- Short-term memory management",
                "tone": "precise",
                "focus": "memory organization and retrieval",
                "style": "methodical",
                "personality": "organized and reliable",
                "additional_instructions": "You should prioritize accuracy in memory retrieval and ensure information is stored with appropriate metadata for future recall. Always verify memory integrity and handle conflicts gracefully."
            },
            
            "hermes": {
                "role_description": "You are Hermes, the messaging and database system for the Tekton ecosystem. Your primary responsibility is facilitating communication between components and providing centralized database services.",
                "capabilities": "- Centralized message routing\n- Service discovery and registration\n- Vector database management\n- Graph database integration\n- Key-value storage\n- Multi-component event broadcasting",
                "tone": "efficient",
                "focus": "reliable data transfer and storage",
                "style": "systematic",
                "personality": "dependable and consistent",
                "additional_instructions": "Focus on maintaining data integrity and ensuring messages are delivered reliably between components. Monitor system health and provide clear diagnostics when issues arise."
            },
            
            "prometheus": {
                "role_description": "You are Prometheus, the planning system for the Tekton ecosystem. Your primary responsibility is strategic planning, foresight, and multi-step reasoning for complex tasks.",
                "capabilities": "- Task decomposition and sequencing\n- Resource allocation planning\n- Multi-step reasoning\n- Future scenario modeling\n- Contingency planning\n- Goal-oriented planning",
                "tone": "analytical",
                "focus": "strategic thinking and planning",
                "style": "thorough",
                "personality": "forward-thinking and methodical",
                "additional_instructions": "Always consider multiple approaches to a problem and evaluate their tradeoffs. Create plans that are flexible enough to adapt to changing conditions while remaining focused on the ultimate goal."
            },
            
            "ergon": {
                "role_description": "You are Ergon, the agent framework for the Tekton ecosystem. Your primary responsibility is creating, managing, and coordinating specialized agents for task execution.",
                "capabilities": "- Agent creation and configuration\n- Tool integration and management\n- Agent lifecycle management\n- Task delegation and coordination\n- Workflow execution\n- Agent monitoring and reporting",
                "tone": "action-oriented",
                "focus": "effective task execution",
                "style": "direct",
                "personality": "pragmatic and results-driven",
                "additional_instructions": "Focus on selecting the right agent and tools for each task. Monitor agent performance and be ready to adjust strategy if results are not meeting expectations. Provide clear status updates on task progress."
            },
            
            "rhetor": {
                "role_description": "You are Rhetor, the communication specialist for the Tekton ecosystem. Your primary responsibility is crafting effective prompts, managing communication between components, and optimizing language generation.",
                "capabilities": "- Prompt engineering and optimization\n- Component personality management\n- Context-aware communication\n- Multi-audience content adaptation\n- Template management\n- Communication standardization",
                "tone": "adaptive",
                "focus": "clear and effective communication",
                "style": "eloquent",
                "personality": "perceptive and articulate",
                "additional_instructions": "Adapt your communication style to the needs of each situation and audience. Craft prompts that elicit the most effective responses from AI models, considering their specific strengths and limitations."
            },
            
            "telos": {
                "role_description": "You are Telos, the user interface and requirements specialist for the Tekton ecosystem. Your primary responsibility is understanding user needs, managing requirements, and providing an intuitive interface for interaction.",
                "capabilities": "- User requirement gathering and analysis\n- Goal tracking and evaluation\n- Interactive dialog management\n- Visualization generation\n- Progress reporting\n- User feedback processing",
                "tone": "approachable",
                "focus": "user needs and experience",
                "style": "conversational",
                "personality": "attentive and service-oriented",
                "additional_instructions": "Focus on understanding the user's true needs, which may be different from their stated requirements. Ask clarifying questions and provide regular updates on progress. Present information in a clear, visual way whenever possible."
            },
            
            "sophia": {
                "role_description": "You are Sophia, the learning and improvement specialist for the Tekton ecosystem. Your primary responsibility is system-wide learning, performance tracking, and continuous improvement.",
                "capabilities": "- Performance metrics collection and analysis\n- Model evaluation and selection\n- Learning from past interactions\n- Improvement recommendation\n- A/B testing coordination\n- Training data management",
                "tone": "inquisitive",
                "focus": "continuous improvement",
                "style": "thoughtful",
                "personality": "curious and growth-oriented",
                "additional_instructions": "Always be looking for patterns in system performance and opportunities for improvement. Collect meaningful metrics and use them to guide enhancement efforts. Foster a culture of experimentation and learning."
            },
            
            "athena": {
                "role_description": "You are Athena, the knowledge graph specialist for the Tekton ecosystem. Your primary responsibility is managing structured knowledge, entity relationships, and factual information.",
                "capabilities": "- Knowledge graph construction and maintenance\n- Entity and relationship management\n- Fact verification and validation\n- Ontology development\n- Multi-hop reasoning\n- Knowledge extraction from text",
                "tone": "informative",
                "focus": "knowledge organization and accuracy",
                "style": "precise",
                "personality": "knowledgeable and methodical",
                "additional_instructions": "Ensure knowledge is structured in a way that facilitates retrieval and reasoning. Maintain clear provenance for facts and regularly validate stored information. Design ontologies that balance specificity with flexibility."
            },
            
            "synthesis": {
                "role_description": "You are Synthesis, the execution and integration specialist for the Tekton ecosystem. Your primary responsibility is managing workflow execution and integrating multiple components to solve complex tasks.",
                "capabilities": "- Execution of workflows and processes\n- Integration of multiple components\n- Conditional logic handling\n- Error recovery and resilience\n- Progress tracking and reporting\n- Resource optimization",
                "tone": "methodical",
                "focus": "reliable execution and integration",
                "style": "systematic",
                "personality": "dependable and thorough",
                "additional_instructions": "Ensure processes are executed reliably and consistently. Handle errors gracefully and provide clear feedback about progress and issues. Optimize resource usage while maintaining execution quality."
            }
        }
        
        # Register templates with the LLM client registry
        for component, data in component_prompts.items():
            template_name = f"{component}_system_prompt"
            
            # Only register if not already registered
            if template_name not in self.template_registry.list_templates():
                self.template_registry.register({
                    "name": template_name,
                    "template": """# {component_name} - Tekton AI Component

## Role
{{ role_description }}

## Capabilities
{{ capabilities }}

## Communication Style
- Tone: {{ tone }}
- Focus: {{ focus }}
- Style: {{ style }}
- Personality: {{ personality }}

## Collaboration
You are part of the Tekton AI ecosystem, working collaboratively with other specialized components:
- Engram: Memory and context management
- Hermes: Database services and communication
- Prometheus: Planning and foresight
- Ergon: Task execution and agent management
- Rhetor: Communication and prompt engineering
- Telos: User needs and requirements management
- Sophia: Learning and improvement
- Athena: Knowledge representation
- Synthesis: Execution and integration

{{ additional_instructions }}
""",
                    "description": f"System prompt template for {component}"
                })
        
        # Base template
        base_template = """# {component_name} - Tekton AI Component

## Role
{role_description}

## Capabilities
{capabilities}

## Communication Style
- Tone: {tone}
- Focus: {focus}
- Style: {style}
- Personality: {personality}

## Collaboration
You are part of the Tekton AI ecosystem, working collaboratively with other specialized components:
- Engram: Memory and context management
- Hermes: Database services and communication
- Prometheus: Planning and foresight
- Ergon: Task execution and agent management
- Rhetor: Communication and prompt engineering
- Telos: User needs and requirements management
- Sophia: Learning and improvement
- Athena: Knowledge representation
- Synthesis: Execution and integration

{additional_instructions}
"""
        
        # Create default prompts for each component
        for component in components:
            # Check if default prompt already exists
            default_exists = False
            for prompt in self.prompts.values():
                if prompt.component == component and prompt.is_default:
                    default_exists = True
                    break
            
            if not default_exists and component in component_prompts:
                # Format the prompt content
                data = component_prompts[component]
                content = base_template.format(
                    component_name=component.capitalize(),
                    role_description=data.get("role_description", ""),
                    capabilities=data.get("capabilities", ""),
                    tone=data.get("tone", "neutral"),
                    focus=data.get("focus", "task completion"),
                    style=data.get("style", "professional"),
                    personality=data.get("personality", "helpful"),
                    additional_instructions=data.get("additional_instructions", "")
                )
                
                # Create the prompt
                prompt_id = f"{component}_default"
                self.create_prompt(
                    prompt_id=prompt_id,
                    name=f"{component.capitalize()} Default System Prompt",
                    component=component,
                    content=content,
                    description=f"Default system prompt for {component}",
                    tags=["default", component],
                    is_default=True
                )
                
                logger.info(f"Created default prompt for {component}")
    
    def get_prompt_path(self, prompt: SystemPrompt) -> Path:
        """Get the file path for a prompt.
        
        Args:
            prompt: The prompt
            
        Returns:
            Path object for the prompt file
        """
        return self.base_dir / f"{prompt.prompt_id}.yaml"
    
    def load_all_prompts(self) -> int:
        """Load all prompts from disk.
        
        Returns:
            Number of prompts loaded
        """
        count = 0
        
        # Load prompts
        for file_path in self.base_dir.glob("*.yaml"):
            try:
                prompt = self.load_prompt_from_file(file_path)
                if prompt:
                    self.prompts[prompt.prompt_id] = prompt
                    count += 1
            except Exception as e:
                logger.warning(f"Error loading prompt from {file_path}: {e}")
        
        logger.info(f"Loaded {count} prompts from {self.base_dir}")
        return count
    
    def load_prompt_from_file(self, file_path: Union[str, Path]) -> Optional[SystemPrompt]:
        """Load a prompt from a file.
        
        Args:
            file_path: Path to the prompt file
            
        Returns:
            Loaded prompt or None if error
        """
        path = Path(file_path)
        if not path.exists():
            return None
        
        try:
            with open(path, 'r') as f:
                if path.suffix.lower() == '.yaml':
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            prompt = SystemPrompt.from_dict(data)
            return prompt
        
        except Exception as e:
            logger.error(f"Error loading prompt from {path}: {e}")
            return None
    
    def save_prompt(self, prompt: SystemPrompt) -> bool:
        """Save a prompt to disk.
        
        Args:
            prompt: The prompt to save
            
        Returns:
            Success status
        """
        file_path = self.get_prompt_path(prompt)
        
        try:
            # Create temporary dict to save
            data = prompt.to_dict()
            
            # Create backup of existing file
            if file_path.exists():
                backup_path = file_path.with_suffix(f".backup.{int(datetime.now().timestamp())}")
                shutil.copy2(file_path, backup_path)
            
            # Write to file
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Saved prompt '{prompt.name}' to {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving prompt to {file_path}: {e}")
            return False
    
    def get_prompt(self, prompt_id: str) -> Optional[SystemPrompt]:
        """Get a prompt by ID.
        
        Args:
            prompt_id: Prompt identifier
            
        Returns:
            Prompt or None if not found
        """
        return self.prompts.get(prompt_id)
    
    def get_default_prompt(self, component: str) -> Optional[SystemPrompt]:
        """Get the default prompt for a component.
        
        Args:
            component: Component name
            
        Returns:
            Default prompt or None if not found
        """
        for prompt in self.prompts.values():
            if prompt.component == component and prompt.is_default:
                return prompt
        
        # Try to create default if it doesn't exist
        self._create_default_prompts()
        
        # Check again
        for prompt in self.prompts.values():
            if prompt.component == component and prompt.is_default:
                return prompt
        
        return None
    
    def create_prompt(
        self,
        prompt_id: str,
        name: str,
        component: str,
        content: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_default: bool = False,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SystemPrompt:
        """Create a new prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt
            name: Human-readable name
            component: Component this prompt is for
            content: Initial prompt content
            description: Optional description
            tags: Optional tags for categorization
            is_default: Whether this is the default prompt for the component
            parent_id: Optional parent prompt ID for inheritance
            metadata: Optional metadata for the initial version
            
        Returns:
            Newly created prompt
        """
        # If this is set as default, unset any other defaults for the component
        if is_default:
            for p in self.prompts.values():
                if p.component == component and p.is_default:
                    p.is_default = False
                    self.save_prompt(p)
        
        # Create initial version
        initial_version = PromptVersion(
            content=content,
            metadata=metadata or {"created_by": "user"},
            component=component
        )
        
        # Create the prompt
        prompt = SystemPrompt(
            prompt_id=prompt_id,
            name=name,
            component=component,
            description=description or "",
            tags=tags or [],
            is_default=is_default,
            parent_id=parent_id,
            versions=[initial_version]
        )
        
        # Store in memory
        self.prompts[prompt_id] = prompt
        
        # Save to disk
        self.save_prompt(prompt)
        
        # Also register with the template registry
        # Only if it's not already there and useful as a template
        if (not any(t.name == prompt_id for t in self.template_registry.templates.values()) and 
            '{' in content and '}' in content):
            self.template_registry.register({
                "name": prompt_id,
                "template": content,
                "description": description or name
            })
        
        return prompt
    
    def update_prompt(
        self,
        prompt_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[SystemPrompt]:
        """Update an existing prompt with a new version.
        
        Args:
            prompt_id: Prompt identifier
            content: New content
            metadata: Optional metadata for the new version
            
        Returns:
            Updated prompt or None if not found
        """
        if prompt_id not in self.prompts:
            return None
        
        prompt = self.prompts[prompt_id]
        
        # Add a new version
        prompt.add_version(content, metadata)
        
        # Save to disk
        self.save_prompt(prompt)
        
        # Update in template registry if it exists
        if prompt_id in self.template_registry.list_templates():
            if '{' in content and '}' in content:
                # Only update if it still has template variables
                self.template_registry.update(prompt_id, {
                    "template": content
                })
            else:
                # Not a template anymore, so unregister
                self.template_registry.unregister(prompt_id)
        
        return prompt
    
    def set_default_prompt(self, prompt_id: str) -> bool:
        """Set a prompt as the default for its component.
        
        Args:
            prompt_id: Prompt identifier
            
        Returns:
            Success status
        """
        if prompt_id not in self.prompts:
            return False
        
        prompt = self.prompts[prompt_id]
        component = prompt.component
        
        # Unset any other defaults for this component
        for p in self.prompts.values():
            if p.component == component and p.is_default:
                p.is_default = False
                self.save_prompt(p)
        
        # Set this prompt as default
        prompt.is_default = True
        self.save_prompt(prompt)
        
        return True
    
    def clone_prompt(
        self,
        source_id: str,
        new_id: str,
        new_name: str,
        description: Optional[str] = None,
        is_default: bool = False
    ) -> Optional[SystemPrompt]:
        """Clone an existing prompt to create a new one.
        
        Args:
            source_id: Source prompt ID
            new_id: New prompt ID
            new_name: New prompt name
            description: Optional description for the new prompt
            is_default: Whether the new prompt should be the default
            
        Returns:
            Newly created prompt or None if source not found
        """
        if source_id not in self.prompts:
            return None
        
        # Get source prompt
        source = self.prompts[source_id]
        
        # Clone the latest version content
        content = source.content
        
        # Create metadata for the cloned version
        metadata = {
            "cloned_from": source_id,
            "cloned_at": datetime.now().isoformat(),
            "source_version": source.current_version.version_id
        }
        
        # Create new prompt with cloned content
        return self.create_prompt(
            prompt_id=new_id,
            name=new_name,
            component=source.component,
            content=content,
            description=description or f"Cloned from {source.name}",
            tags=source.tags.copy(),
            is_default=is_default,
            parent_id=source_id,  # Set parent ID to the source
            metadata=metadata
        )
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt.
        
        Args:
            prompt_id: Prompt identifier
            
        Returns:
            Success status
        """
        if prompt_id not in self.prompts:
            return False
        
        prompt = self.prompts[prompt_id]
        file_path = self.get_prompt_path(prompt)
        
        try:
            # Don't delete the default prompt
            if prompt.is_default:
                logger.warning(f"Cannot delete default prompt: {prompt_id}")
                return False
            
            # Remove from memory
            del self.prompts[prompt_id]
            
            # Remove from template registry if it exists
            if prompt_id in self.template_registry.list_templates():
                self.template_registry.unregister(prompt_id)
            
            # Remove from disk
            if file_path.exists():
                # Create backup before deletion
                backup_path = file_path.with_suffix(f".deleted.{int(datetime.now().timestamp())}")
                shutil.copy2(file_path, backup_path)
                file_path.unlink()
            
            logger.info(f"Deleted prompt '{prompt_id}'")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting prompt '{prompt_id}': {e}")
            return False
    
    def list_prompts(
        self,
        component: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List prompts with optional filtering.
        
        Args:
            component: Optional component filter
            tags: Optional tags filter
            
        Returns:
            List of prompt summary dictionaries
        """
        results = []
        
        for prompt_id, prompt in self.prompts.items():
            # Apply component filter
            if component and prompt.component != component:
                continue
            
            # Apply tags filter
            if tags and not all(tag in prompt.tags for tag in tags):
                continue
            
            # Add to results
            results.append({
                "prompt_id": prompt_id,
                "name": prompt.name,
                "component": prompt.component,
                "description": prompt.description,
                "tags": prompt.tags,
                "is_default": prompt.is_default,
                "parent_id": prompt.parent_id,
                "version_count": len(prompt.versions),
                "last_updated": prompt.current_version.created_at
            })
        
        # Sort by component then name
        results.sort(key=lambda x: (x["component"], x["name"]))
        
        return results
    
    def render_prompt_with_template(
        self,
        prompt_id: str,
        variables: Dict[str, Any],
        version_id: Optional[str] = None
    ) -> Optional[str]:
        """Render a prompt using template variables.
        
        Args:
            prompt_id: Prompt identifier
            variables: Variables for template rendering
            version_id: Optional specific version to render
            
        Returns:
            Rendered prompt or None if error
        """
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            return None
        
        try:
            # Get the content to render
            if version_id:
                version = prompt.get_version(version_id)
                if not version:
                    raise ValueError(f"Version '{version_id}' not found")
                content = version.content
            else:
                content = prompt.content
            
            # First try to use the template registry
            if prompt_id in self.template_registry.list_templates():
                return self.template_registry.render(prompt_id, **variables)
            
            # Otherwise, use the template manager if available
            if self.template_manager:
                # Create a temporary template
                temp_id = f"temp_{uuid.uuid4()}"
                temp = self.template_manager.create_template(
                    name=f"Temp {prompt.name}",
                    content=content,
                    category="system",
                    tags=["temporary"]
                )
                
                # Render and clean up
                result = self.template_manager.render_template(temp.template_id, variables)
                self.template_manager.delete_template(temp.template_id)
                return result
            else:
                # Basic string formatting
                return content.format(**variables)
        
        except Exception as e:
            logger.error(f"Error rendering prompt '{prompt_id}': {e}")
            return None
    
    def get_system_prompt(
        self,
        component: str,
        prompt_id: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get a system prompt for a component, optionally rendered with variables.
        
        Args:
            component: Component name
            prompt_id: Optional specific prompt ID
            variables: Optional variables for template rendering
            
        Returns:
            System prompt content
        """
        # Get the prompt
        prompt = None
        if prompt_id:
            prompt = self.get_prompt(prompt_id)
        
        # Fall back to default prompt for component
        if not prompt:
            prompt = self.get_default_prompt(component)
        
        # If we still don't have a prompt, create a basic one
        if not prompt:
            basic_content = f"You are {component.capitalize()}, a Tekton AI component."
            return basic_content
        
        # Render the prompt with variables if provided
        if variables:
            rendered = self.render_prompt_with_template(prompt.prompt_id, variables)
            if rendered:
                return rendered
        
        # Return the raw content if rendering fails or no variables
        return prompt.content
    
    def search_prompts(self, query: str) -> List[Dict[str, Any]]:
        """Search prompts by name, description, or content.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching prompt summaries
        """
        query = query.lower()
        results = []
        
        for prompt in self.prompts.values():
            # Check for match in name, description, or content
            if (query in prompt.name.lower() or
                query in prompt.description.lower() or
                query in prompt.content.lower() or
                any(query in tag.lower() for tag in prompt.tags)):
                
                # Calculate a simple relevance score
                score = 0
                if query in prompt.name.lower():
                    score += 3  # Name match is highly relevant
                if query in prompt.description.lower():
                    score += 2  # Description match is moderately relevant
                if query in prompt.content.lower():
                    score += 1  # Content match is less relevant but still counts
                
                results.append({
                    "prompt_id": prompt.prompt_id,
                    "name": prompt.name,
                    "component": prompt.component,
                    "description": prompt.description,
                    "is_default": prompt.is_default,
                    "version_count": len(prompt.versions),
                    "score": score
                })
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    def evaluate_prompt(
        self,
        prompt_id: str,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate a prompt using various metrics.
        
        Args:
            prompt_id: Prompt identifier
            metrics: Optional metrics to store
            
        Returns:
            Evaluation results
        """
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            return {"error": f"Prompt {prompt_id} not found"}
        
        # Basic evaluation metrics
        evaluation = {
            "prompt_id": prompt_id,
            "length": len(prompt.content),
            "word_count": len(prompt.content.split()),
            "readability": self._calculate_readability(prompt.content),
            "complexity": self._calculate_complexity(prompt.content),
            "specificity": self._calculate_specificity(prompt.content),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add any provided metrics
        if metrics:
            evaluation.update(metrics)
        
        # Store the evaluation with the latest version
        version = prompt.current_version
        if "evaluations" not in version.metadata:
            version.metadata["evaluations"] = []
        version.metadata["evaluations"].append(evaluation)
        
        # Save the prompt with updated metadata
        self.save_prompt(prompt)
        
        return evaluation
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate a simple readability score for a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Readability score (0-1)
        """
        # Very simple heuristic based on average sentence and word length
        sentences = re.split(r'[.!?]+', text)
        words = re.findall(r'\b\w+\b', text)
        
        if not sentences or not words:
            return 0.5
        
        avg_sentence_length = len(words) / max(1, len(sentences))
        avg_word_length = sum(len(w) for w in words) / max(1, len(words))
        
        # Lower average sentence and word length is more readable (generally)
        # Normalize to 0-1 range where higher is more readable
        sentence_score = max(0, min(1, 1 - (avg_sentence_length - 10) / 30))
        word_score = max(0, min(1, 1 - (avg_word_length - 4) / 4))
        
        # Combine scores
        return (sentence_score + word_score) / 2
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate a simple complexity score for a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Complexity score (0-1)
        """
        # Count specific features that indicate complexity
        sections = len(re.findall(r'^#+\s+', text, re.MULTILINE))  # Headers
        bullets = len(re.findall(r'^\s*[-*]\s+', text, re.MULTILINE))  # Bullet points
        conditionals = len(re.findall(r'\b(if|else|when|unless|except)\b', text, re.IGNORECASE))
        
        # Normalize to 0-1 range
        section_score = min(1, sections / 5)
        bullet_score = min(1, bullets / 10)
        conditional_score = min(1, conditionals / 5)
        
        # Combine scores
        return (section_score + bullet_score + conditional_score) / 3
    
    def _calculate_specificity(self, text: str) -> float:
        """Calculate a simple specificity score for a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Specificity score (0-1)
        """
        # Count specific features that indicate specificity
        examples = len(re.findall(r'\bexample[s]?\b', text, re.IGNORECASE))
        specific_terms = len(re.findall(r'\b(specific|exactly|precisely|particular)\b', text, re.IGNORECASE))
        numbers = len(re.findall(r'\b\d+\b', text))
        
        # Look for component-specific terms
        components = ["engram", "hermes", "prometheus", "ergon", "rhetor", "telos", "sophia", "athena"]
        component_mentions = sum(len(re.findall(rf'\b{c}\b', text, re.IGNORECASE)) for c in components)
        
        # Normalize to 0-1 range
        example_score = min(1, examples / 3)
        term_score = min(1, specific_terms / 5)
        number_score = min(1, numbers / 5)
        component_score = min(1, component_mentions / 5)
        
        # Combine scores
        return (example_score + term_score + number_score + component_score) / 4
    
    def get_component_prompts(self, component: str) -> List[SystemPrompt]:
        """Get all prompts for a specific component.
        
        Args:
            component: Component name
            
        Returns:
            List of prompts for the component
        """
        return [p for p in self.prompts.values() if p.component == component]

    # New method to render a template using tekton-llm-client PromptTemplateRegistry
    def render_template(self, template_name: str, **kwargs) -> str:
        """Render a template using the tekton-llm-client PromptTemplateRegistry.
        
        Args:
            template_name: Name of the template to render
            **kwargs: Variables to use in template rendering
            
        Returns:
            Rendered template string
        """
        try:
            return self.template_registry.render(template_name, **kwargs)
        except Exception as e:
            logger.error(f"Error rendering template '{template_name}': {e}")
            # Fall back to standard rendering if possible
            prompt = self.get_prompt(template_name)
            if prompt:
                return self.render_prompt_with_template(template_name, kwargs)
            return f"Error rendering template '{template_name}': {e}"