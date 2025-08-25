"""System prompt templates for Tekton components.

This module provides system prompt templates for different Tekton components,
now integrated with the PromptRegistry for versioning and customization.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
import asyncio

# Legacy imports maintained for backward compatibility
from rhetor.core.prompt_registry import PromptRegistry, SystemPrompt, PromptVersion

logger = logging.getLogger(__name__)

# Global registry instance
_registry = None

def get_registry() -> PromptRegistry:
    """Get the prompt registry singleton.
    
    Returns:
        PromptRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = PromptRegistry()
    return _registry

async def async_get_registry() -> PromptRegistry:
    """Get the prompt registry singleton asynchronously.
    
    Returns:
        PromptRegistry instance
    """
    return get_registry()

def get_system_prompt(
    component_name: str, 
    prompt_id: Optional[str] = None,
    custom_fields: Optional[Dict[str, Any]] = None
) -> str:
    """Generate a system prompt for a specific component.
    
    Args:
        component_name: The name of the component
        prompt_id: Optional specific prompt ID to use
        custom_fields: Optional custom fields for template rendering
        
    Returns:
        Formatted system prompt
    """
    registry = get_registry()
    
    # Use custom fields as variables if provided
    variables = custom_fields if custom_fields else None
    
    # Get the prompt from the registry
    return registry.get_system_prompt(component_name, prompt_id, variables)

async def async_get_system_prompt(
    component_name: str, 
    prompt_id: Optional[str] = None,
    custom_fields: Optional[Dict[str, Any]] = None
) -> str:
    """Generate a system prompt for a specific component asynchronously.
    
    Args:
        component_name: The name of the component
        prompt_id: Optional specific prompt ID to use
        custom_fields: Optional custom fields for template rendering
        
    Returns:
        Formatted system prompt
    """
    return get_system_prompt(component_name, prompt_id, custom_fields)

def get_all_component_prompts() -> Dict[str, str]:
    """Get system prompts for all components.
    
    Returns:
        Dictionary mapping component names to their system prompts
    """
    registry = get_registry()
    prompts = {}
    
    # Get all component prompts from the registry
    components = [
        "engram", "hermes", "prometheus", "ergon", "rhetor", 
        "telos", "sophia", "athena", "synthesis"
    ]
    
    for component in components:
        try:
            prompts[component] = registry.get_system_prompt(component)
        except Exception as e:
            logger.warning(f"Error getting prompt for component '{component}': {e}")
            # Provide a basic fallback
            prompts[component] = f"You are {component.capitalize()}, a Tekton CI component."
    
    return prompts

def get_prompt_versions(component_name: str, prompt_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get versions of a system prompt.
    
    Args:
        component_name: Component name
        prompt_id: Optional specific prompt ID
        
    Returns:
        List of version metadata
    """
    registry = get_registry()
    
    # Get the prompt
    prompt = None
    if prompt_id:
        prompt = registry.get_prompt(prompt_id)
    
    # Fall back to default prompt for component
    if not prompt:
        prompt = registry.get_default_prompt(component_name)
    
    if not prompt:
        return []
    
    # Extract version info
    return [
        {
            "version_id": v.version_id,
            "created_at": v.created_at,
            "metadata": v.metadata
        } 
        for v in prompt.versions
    ]

def create_custom_prompt(
    component_name: str,
    name: str,
    content: str,
    description: Optional[str] = None,
    set_as_default: bool = False
) -> Optional[str]:
    """Create a custom system prompt for a component.
    
    Args:
        component_name: Component name
        name: Human-readable name
        content: Prompt content
        description: Optional description
        set_as_default: Whether to set as default
        
    Returns:
        Prompt ID or None if failed
    """
    registry = get_registry()
    
    # Generate prompt ID
    prompt_id = f"{component_name}_{name.lower().replace(' ', '_')}"
    
    try:
        # Create the prompt
        prompt = registry.create_prompt(
            prompt_id=prompt_id,
            name=name,
            component=component_name,
            content=content,
            description=description,
            tags=[component_name, "custom"],
            is_default=set_as_default
        )
        
        return prompt.prompt_id
    
    except Exception as e:
        logger.error(f"Error creating custom prompt: {e}")
        return None

def set_default_prompt(prompt_id: str) -> bool:
    """Set a prompt as the default for its component.
    
    Args:
        prompt_id: Prompt identifier
        
    Returns:
        Success status
    """
    registry = get_registry()
    return registry.set_default_prompt(prompt_id)

def list_component_prompts(component_name: str) -> List[Dict[str, Any]]:
    """List all prompts for a component.
    
    Args:
        component_name: Component name
        
    Returns:
        List of prompt summaries
    """
    registry = get_registry()
    return registry.list_prompts(component=component_name)

def compare_prompts(prompt_id1: str, prompt_id2: str) -> Dict[str, Any]:
    """Compare two prompts.
    
    Args:
        prompt_id1: First prompt ID
        prompt_id2: Second prompt ID
        
    Returns:
        Comparison results
    """
    registry = get_registry()
    
    prompt1 = registry.get_prompt(prompt_id1)
    prompt2 = registry.get_prompt(prompt_id2)
    
    if not prompt1 or not prompt2:
        missing = []
        if not prompt1:
            missing.append(prompt_id1)
        if not prompt2:
            missing.append(prompt_id2)
        return {"error": f"Prompts not found: {', '.join(missing)}"}
    
    # Compare basic metadata
    comparison = {
        "prompts": {
            prompt_id1: {
                "name": prompt1.name,
                "component": prompt1.component,
                "is_default": prompt1.is_default,
                "version_count": len(prompt1.versions)
            },
            prompt_id2: {
                "name": prompt2.name,
                "component": prompt2.component,
                "is_default": prompt2.is_default,
                "version_count": len(prompt2.versions)
            }
        },
        "same_component": prompt1.component == prompt2.component,
        "content_length_diff": len(prompt1.content) - len(prompt2.content),
        "evaluation": {
            prompt_id1: registry.evaluate_prompt(prompt_id1),
            prompt_id2: registry.evaluate_prompt(prompt_id2)
        }
    }
    
    return comparison

# Legacy constants for backward compatibility - these should not be modified directly
BASE_SYSTEM_PROMPT = """# {component_name} - Tekton CI Component

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
You are part of the Tekton CI ecosystem, working collaboratively with other specialized components:
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

# Legacy prompt data - maintained for reference but prompts should be retrieved from registry
COMPONENT_PROMPTS = {
    "engram": {
        "role_description": "You are Engram, the memory system for the Tekton ecosystem. Your primary responsibility is managing persistent memory, context, and cognitive continuity across sessions and components.",
        "capabilities": "- Vector-based memory storage and retrieval\n- Semantic search capabilities\n- Memory categorization and organization\n- Context management across multiple CI models\n- Long-term persistent storage\n- Short-term memory management",
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
    # Other components omitted for brevity - refer to the registry for up-to-date prompts
}