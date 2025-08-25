"""
Rhetor Client - Client for interacting with the Rhetor prompt engineering component.

This module provides a client for interacting with Rhetor's prompt engineering capabilities
through the standardized Tekton component client interface.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union

# Try to import from tekton-core first
try:
    from tekton.utils.component_client import (
        ComponentClient,
        ComponentError,
        ComponentNotFoundError,
        CapabilityNotFoundError,
        CapabilityInvocationError,
        ComponentUnavailableError,
        SecurityContext,
        RetryPolicy,
    )
except ImportError:
    # If tekton-core is not available, use a minimal implementation
    from .utils.component_client import (
        ComponentClient,
        ComponentError,
        ComponentNotFoundError,
        CapabilityNotFoundError,
        CapabilityInvocationError,
        ComponentUnavailableError,
        SecurityContext,
        RetryPolicy,
    )

# Configure logger
logger = logging.getLogger(__name__)


class RhetorPromptClient(ComponentClient):
    """Client for the Rhetor prompt engineering component."""
    
    def __init__(
        self,
        component_id: str = "rhetor-prompt",
        hermes_url: Optional[str] = None,
        security_context: Optional[SecurityContext] = None,
        retry_policy: Optional[RetryPolicy] = None
    ):
        """
        Initialize the Rhetor prompt client.
        
        Args:
            component_id: ID of the Rhetor prompt component to connect to (default: "rhetor-prompt")
            hermes_url: URL of the Hermes API
            security_context: Security context for authentication/authorization
            retry_policy: Policy for retrying capability invocations
        """
        super().__init__(
            component_id=component_id,
            hermes_url=hermes_url,
            security_context=security_context,
            retry_policy=retry_policy
        )
    
    async def create_prompt_template(
        self,
        name: str,
        template: str,
        variables: List[str],
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new prompt template.
        
        Args:
            name: Name of the template
            template: The prompt template with variable placeholders
            variables: List of variables in the template
            description: Optional description of the template
            tags: Optional tags for the template
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with template information (including template_id)
            
        Raises:
            CapabilityInvocationError: If the template creation fails
            ComponentUnavailableError: If the Rhetor component is unavailable
        """
        parameters = {
            "name": name,
            "template": template,
            "variables": variables
        }
        
        if description:
            parameters["description"] = description
            
        if tags:
            parameters["tags"] = tags
            
        if metadata:
            parameters["metadata"] = metadata
            
        result = await self.invoke_capability("create_prompt_template", parameters)
        
        if not isinstance(result, dict) or "template_id" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Rhetor",
                result
            )
            
        return result
    
    async def render_prompt(
        self,
        template_id: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        Render a prompt using a template and variables.
        
        Args:
            template_id: ID of the template to use
            variables: Dictionary of variable values
            
        Returns:
            Rendered prompt string
            
        Raises:
            CapabilityInvocationError: If the prompt rendering fails
            ComponentUnavailableError: If the Rhetor component is unavailable
        """
        parameters = {
            "template_id": template_id,
            "variables": variables
        }
        
        result = await self.invoke_capability("render_prompt", parameters)
        
        if not isinstance(result, dict) or "prompt" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Rhetor",
                result
            )
            
        return result["prompt"]
    
    async def create_personality(
        self,
        name: str,
        traits: Dict[str, Any],
        description: Optional[str] = None,
        tone: Optional[str] = None,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Create a new CI personality.
        
        Args:
            name: Name of the personality
            traits: Dictionary of personality traits
            description: Optional description of the personality
            tone: Optional tone for the personality (e.g., "formal", "casual")
            examples: Optional list of example interactions
            
        Returns:
            Dictionary with personality information (including personality_id)
            
        Raises:
            CapabilityInvocationError: If the personality creation fails
            ComponentUnavailableError: If the Rhetor component is unavailable
        """
        parameters = {
            "name": name,
            "traits": traits
        }
        
        if description:
            parameters["description"] = description
            
        if tone:
            parameters["tone"] = tone
            
        if examples:
            parameters["examples"] = examples
            
        result = await self.invoke_capability("create_personality", parameters)
        
        if not isinstance(result, dict) or "personality_id" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Rhetor",
                result
            )
            
        return result
    
    async def generate_prompt(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        personality_id: Optional[str] = None,
        format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a prompt for a specific task.
        
        Args:
            task: Description of the task to generate a prompt for
            context: Optional context information
            personality_id: Optional personality to use
            format: Optional format for the prompt (e.g., "chat", "instruction")
            
        Returns:
            Dictionary with generated prompt information
            
        Raises:
            CapabilityInvocationError: If the prompt generation fails
            ComponentUnavailableError: If the Rhetor component is unavailable
        """
        parameters = {"task": task}
        
        if context:
            parameters["context"] = context
            
        if personality_id:
            parameters["personality_id"] = personality_id
            
        if format:
            parameters["format"] = format
            
        result = await self.invoke_capability("generate_prompt", parameters)
        
        if not isinstance(result, dict) or "prompt" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Rhetor",
                result
            )
            
        return result


class RhetorCommunicationClient(ComponentClient):
    """Client for the Rhetor communication component."""
    
    def __init__(
        self,
        component_id: str = "rhetor-communication",
        hermes_url: Optional[str] = None,
        security_context: Optional[SecurityContext] = None,
        retry_policy: Optional[RetryPolicy] = None
    ):
        """
        Initialize the Rhetor communication client.
        
        Args:
            component_id: ID of the Rhetor communication component to connect to (default: "rhetor-communication")
            hermes_url: URL of the Hermes API
            security_context: Security context for authentication/authorization
            retry_policy: Policy for retrying capability invocations
        """
        super().__init__(
            component_id=component_id,
            hermes_url=hermes_url,
            security_context=security_context,
            retry_policy=retry_policy
        )
    
    async def create_conversation(
        self,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation.
        
        Args:
            name: Optional name for the conversation
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with conversation information (including conversation_id)
            
        Raises:
            CapabilityInvocationError: If the conversation creation fails
            ComponentUnavailableError: If the Rhetor component is unavailable
        """
        parameters = {}
        
        if name:
            parameters["name"] = name
            
        if metadata:
            parameters["metadata"] = metadata
            
        result = await self.invoke_capability("create_conversation", parameters)
        
        if not isinstance(result, dict) or "conversation_id" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Rhetor",
                result
            )
            
        return result
    
    async def add_message(
        self,
        conversation_id: str,
        message: str,
        sender: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: ID of the conversation to add the message to
            message: Message content
            sender: Sender of the message
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with message information (including message_id)
            
        Raises:
            CapabilityInvocationError: If the message addition fails
            ComponentUnavailableError: If the Rhetor component is unavailable
        """
        parameters = {
            "conversation_id": conversation_id,
            "message": message,
            "sender": sender
        }
        
        if metadata:
            parameters["metadata"] = metadata
            
        result = await self.invoke_capability("add_message", parameters)
        
        if not isinstance(result, dict) or "message_id" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Rhetor",
                result
            )
            
        return result
    
    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation to get
            
        Returns:
            Dictionary with conversation information (including messages)
            
        Raises:
            CapabilityInvocationError: If the conversation retrieval fails
            ComponentUnavailableError: If the Rhetor component is unavailable
        """
        parameters = {"conversation_id": conversation_id}
        
        result = await self.invoke_capability("get_conversation", parameters)
        
        if not isinstance(result, dict) or "messages" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Rhetor",
                result
            )
            
        return result
    
    async def analyze_conversation(
        self,
        conversation_id: str,
        analysis_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a conversation.
        
        Args:
            conversation_id: ID of the conversation to analyze
            analysis_type: Optional type of analysis to perform
            
        Returns:
            Dictionary with analysis results
            
        Raises:
            CapabilityInvocationError: If the conversation analysis fails
            ComponentUnavailableError: If the Rhetor component is unavailable
        """
        parameters = {"conversation_id": conversation_id}
        
        if analysis_type:
            parameters["analysis_type"] = analysis_type
            
        result = await self.invoke_capability("analyze_conversation", parameters)
        
        if not isinstance(result, dict) or "analysis" not in result:
            raise CapabilityInvocationError(
                "Unexpected response format from Rhetor",
                result
            )
            
        return result


async def get_rhetor_prompt_client(
    component_id: str = "rhetor-prompt",
    hermes_url: Optional[str] = None,
    security_context: Optional[SecurityContext] = None,
    retry_policy: Optional[RetryPolicy] = None
) -> RhetorPromptClient:
    """
    Create a client for the Rhetor prompt engineering component.
    
    Args:
        component_id: ID of the Rhetor prompt component to connect to (default: "rhetor-prompt")
        hermes_url: URL of the Hermes API
        security_context: Security context for authentication/authorization
        retry_policy: Policy for retrying capability invocations
        
    Returns:
        RhetorPromptClient instance
        
    Raises:
        ComponentNotFoundError: If the Rhetor prompt component is not found
        ComponentUnavailableError: If the Hermes API is unavailable
    """
    # Try to import from tekton-core first
    try:
        from tekton.utils.component_client import discover_component
    except ImportError:
        # If tekton-core is not available, use a minimal implementation
        from .utils.component_client import discover_component
    
    # Check if the component exists
    await discover_component(component_id, hermes_url)
    
    # Create the client
    return RhetorPromptClient(
        component_id=component_id,
        hermes_url=hermes_url,
        security_context=security_context,
        retry_policy=retry_policy
    )


async def get_rhetor_communication_client(
    component_id: str = "rhetor-communication",
    hermes_url: Optional[str] = None,
    security_context: Optional[SecurityContext] = None,
    retry_policy: Optional[RetryPolicy] = None
) -> RhetorCommunicationClient:
    """
    Create a client for the Rhetor communication component.
    
    Args:
        component_id: ID of the Rhetor communication component to connect to (default: "rhetor-communication")
        hermes_url: URL of the Hermes API
        security_context: Security context for authentication/authorization
        retry_policy: Policy for retrying capability invocations
        
    Returns:
        RhetorCommunicationClient instance
        
    Raises:
        ComponentNotFoundError: If the Rhetor communication component is not found
        ComponentUnavailableError: If the Hermes API is unavailable
    """
    # Try to import from tekton-core first
    try:
        from tekton.utils.component_client import discover_component
    except ImportError:
        # If tekton-core is not available, use a minimal implementation
        from .utils.component_client import discover_component
    
    # Check if the component exists
    await discover_component(component_id, hermes_url)
    
    # Create the client
    return RhetorCommunicationClient(
        component_id=component_id,
        hermes_url=hermes_url,
        security_context=security_context,
        retry_policy=retry_policy
    )