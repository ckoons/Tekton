"""Command implementations for the Rhetor CLI.

This module provides the implementation of commands for the Rhetor CLI.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable

from rhetor.core.prompt_engine import PromptEngine, PromptLibrary, PromptTemplate
from rhetor.core.communication import CommunicationEngine, Message, Conversation
from rhetor.cli.cli_helpers import format_timestamp, parse_key_value_pairs

logger = logging.getLogger(__name__)


# Enhanced template management commands
def list_templates(template_manager, api_client=None, category=None, tag=None):
    """List all templates with optional filtering.
    
    Args:
        template_manager: Template manager instance (local)
        api_client: API client for remote operations
        category: Filter by category
        tag: Filter by tag
    """
    try:
        if api_client:
            # Use API client for remote operation
            response = api_client.list_templates(category=category, tag=tag)
            templates = response.get("templates", [])
            
            if not templates:
                print("No templates found")
                return
            
            print(f"Found {len(templates)} templates:")
            for template in templates:
                print(f"  {template['id']}: {template['name']}")
                print(f"    Category: {template['category']}")
                if template.get('description'):
                    print(f"    Description: {template['description']}")
                if template.get('tags'):
                    print(f"    Tags: {', '.join(template['tags'])}")
        else:
            # Use local template manager
            templates = template_manager.list_templates(category=category, tag=tag)
            
            if not templates:
                print("No templates found")
                return
            
            print(f"Found {len(templates)} templates:")
            for template in templates:
                print(f"  {template['id']}: {template['name']}")
                print(f"    Category: {template['category']}")
                if template.get('description'):
                    print(f"    Description: {template['description']}")
                if template.get('tags'):
                    print(f"    Tags: {', '.join(template['tags'])}")
    except Exception as e:
        print(f"Error listing templates: {e}")


def create_template(template_manager, api_client=None, name=None, content=None, 
                  category="general", description=None, tags=None, file=None):
    """Create a new template.
    
    Args:
        template_manager: Template manager instance (local)
        api_client: API client for remote operations
        name: Template name
        content: Template content
        category: Template category
        description: Template description
        tags: Template tags (comma-separated)
        file: Read template content from file
    """
    try:
        # Read content from file if specified
        if file:
            with open(file, 'r') as f:
                content = f.read()
        
        if not content:
            print("Error: Template content is required")
            return
        
        # Parse tags
        tag_list = tags.split(',') if tags else []
        
        if api_client:
            # Use API client for remote operation
            response = api_client.create_template(
                name=name,
                content=content,
                category=category,
                description=description,
                tags=tag_list
            )
            print(f"Created template: {response['id']}")
        else:
            # Use local template manager
            template = template_manager.create_template(
                name=name,
                content=content,
                category=category,
                description=description,
                tags=tag_list
            )
            print(f"Created template: {template['id']}")
            
    except Exception as e:
        print(f"Error creating template: {e}")


def get_template(template_manager, api_client=None, template_id=None, version_id=None):
    """Get a template by ID.
    
    Args:
        template_manager: Template manager instance (local)
        api_client: API client for remote operations
        template_id: Template ID
        version_id: Version ID (optional)
    """
    try:
        if api_client:
            # Use API client for remote operation
            response = api_client.get_template(template_id, version_id=version_id)
            
            print(f"Template: {response['id']}")
            print(f"Name: {response['name']}")
            print(f"Category: {response['category']}")
            if response.get('description'):
                print(f"Description: {response['description']}")
            if response.get('tags'):
                print(f"Tags: {', '.join(response['tags'])}")
            print(f"Version: {response.get('version_id', 'latest')}")
            print(f"Created: {response.get('created_at')}")
            print(f"Updated: {response.get('updated_at')}")
            print("\nContent:")
            print(response['content'])
        else:
            # Use local template manager
            template = template_manager.get_template(template_id, version_id=version_id)
            
            if not template:
                print(f"Template {template_id} not found")
                return
            
            print(f"Template: {template['id']}")
            print(f"Name: {template['name']}")
            print(f"Category: {template['category']}")
            if template.get('description'):
                print(f"Description: {template['description']}")
            if template.get('tags'):
                print(f"Tags: {', '.join(template['tags'])}")
            print(f"Version: {template.get('version_id', 'latest')}")
            print(f"Created: {template.get('created_at')}")
            print(f"Updated: {template.get('updated_at')}")
            print("\nContent:")
            print(template['content'])
    except Exception as e:
        print(f"Error getting template: {e}")


def update_template(template_manager, api_client=None, template_id=None, content=None, file=None):
    """Update a template.
    
    Args:
        template_manager: Template manager instance (local)
        api_client: API client for remote operations
        template_id: Template ID
        content: New template content
        file: Read template content from file
    """
    try:
        # Read content from file if specified
        if file:
            with open(file, 'r') as f:
                content = f.read()
        
        if not content:
            print("Error: Template content is required")
            return
        
        if api_client:
            # Use API client for remote operation
            response = api_client.update_template(
                template_id=template_id,
                content=content
            )
            print(f"Updated template: {response['id']}")
            print(f"New version: {response.get('version_id', 'latest')}")
        else:
            # Use local template manager
            template = template_manager.update_template(
                template_id=template_id,
                content=content
            )
            print(f"Updated template: {template['id']}")
            print(f"New version: {template.get('version_id', 'latest')}")
    except Exception as e:
        print(f"Error updating template: {e}")


def delete_template(template_manager, api_client=None, template_id=None):
    """Delete a template.
    
    Args:
        template_manager: Template manager instance (local)
        api_client: API client for remote operations
        template_id: Template ID
    """
    try:
        if api_client:
            # Use API client for remote operation
            response = api_client.delete_template(template_id)
            if response.get('success'):
                print(f"Deleted template: {template_id}")
            else:
                print(f"Failed to delete template: {template_id}")
        else:
            # Use local template manager
            success = template_manager.delete_template(template_id)
            if success:
                print(f"Deleted template: {template_id}")
            else:
                print(f"Template {template_id} not found")
    except Exception as e:
        print(f"Error deleting template: {e}")


def list_template_versions(template_manager, api_client=None, template_id=None):
    """List all versions of a template.
    
    Args:
        template_manager: Template manager instance (local)
        api_client: API client for remote operations
        template_id: Template ID
    """
    try:
        if api_client:
            # Use API client for remote operation
            response = api_client.list_template_versions(template_id)
            versions = response.get("versions", [])
            
            if not versions:
                print(f"No versions found for template {template_id}")
                return
            
            print(f"Versions for template {template_id}:")
            for version in versions:
                print(f"  {version['version_id']}")
                print(f"    Created: {version['created_at']}")
                if version.get('comment'):
                    print(f"    Comment: {version['comment']}")
        else:
            # Use local template manager
            versions = template_manager.get_template_versions(template_id)
            
            if not versions:
                print(f"No versions found for template {template_id}")
                return
            
            print(f"Versions for template {template_id}:")
            for version in versions:
                print(f"  {version['version_id']}")
                print(f"    Created: {version['created_at']}")
                if version.get('comment'):
                    print(f"    Comment: {version['comment']}")
    except Exception as e:
        print(f"Error listing template versions: {e}")


def render_template(template_manager, api_client=None, template_id=None, 
                   variables=None, version_id=None, output=None):
    """Render a template with variables.
    
    Args:
        template_manager: Template manager instance (local)
        api_client: API client for remote operations
        template_id: Template ID
        variables: Variable values (key=value,...)
        version_id: Version ID (optional)
        output: Output file (optional)
    """
    try:
        # Parse variables
        variable_dict = parse_key_value_pairs(variables) if variables else {}
        
        if api_client:
            # Use API client for remote operation
            response = api_client.render_template(
                template_id=template_id,
                variables=variable_dict,
                version_id=version_id
            )
            rendered = response.get('rendered_content')
        else:
            # Use local template manager
            rendered = template_manager.render_template(
                template_id=template_id,
                variables=variable_dict,
                version_id=version_id
            )
        
        if output:
            with open(output, 'w') as f:
                f.write(rendered)
            print(f"Rendered template saved to {output}")
        else:
            print("Rendered Template:")
            print(rendered)
    except Exception as e:
        print(f"Error rendering template: {e}")


# Extended prompt management commands
def list_prompts(prompt_registry, api_client=None, component=None, tag=None):
    """List all prompts with optional filtering.
    
    Args:
        prompt_registry: Prompt registry (local)
        api_client: API client for remote operations
        component: Filter by component
        tag: Filter by tag
    """
    try:
        if api_client:
            # Use API client for remote operation
            response = api_client.list_prompts(component=component, tag=tag)
            prompts = response.get("prompts", [])
            
            if not prompts:
                print("No prompts found")
                return
            
            print(f"Found {len(prompts)} prompts:")
            for prompt in prompts:
                is_default = " (DEFAULT)" if prompt.get('is_default') else ""
                print(f"  {prompt['id']}: {prompt['name']}{is_default}")
                print(f"    Component: {prompt['component']}")
                if prompt.get('description'):
                    print(f"    Description: {prompt['description']}")
                if prompt.get('tags'):
                    print(f"    Tags: {', '.join(prompt['tags'])}")
        else:
            # Use local prompt registry
            prompts = prompt_registry.list_prompts(component=component, tag=tag)
            
            if not prompts:
                print("No prompts found")
                return
            
            print(f"Found {len(prompts)} prompts:")
            for prompt in prompts:
                is_default = " (DEFAULT)" if prompt.get('is_default') else ""
                print(f"  {prompt['id']}: {prompt['name']}{is_default}")
                print(f"    Component: {prompt['component']}")
                if prompt.get('description'):
                    print(f"    Description: {prompt['description']}")
                if prompt.get('tags'):
                    print(f"    Tags: {', '.join(prompt['tags'])}")
    except Exception as e:
        print(f"Error listing prompts: {e}")


def create_prompt(prompt_registry, api_client=None, name=None, component=None, 
               content=None, description=None, tags=None, is_default=False, 
               parent_id=None, file=None):
    """Create a new prompt.
    
    Args:
        prompt_registry: Prompt registry (local)
        api_client: API client for remote operations
        name: Prompt name
        component: Component
        content: Prompt content
        description: Prompt description
        tags: Prompt tags (comma-separated)
        is_default: Set as default prompt for component
        parent_id: Parent prompt ID
        file: Read prompt content from file
    """
    try:
        # Read content from file if specified
        if file:
            with open(file, 'r') as f:
                content = f.read()
        
        if not content:
            print("Error: Prompt content is required")
            return
        
        # Parse tags
        tag_list = tags.split(',') if tags else []
        
        if api_client:
            # Use API client for remote operation
            response = api_client.create_prompt(
                name=name,
                component=component,
                content=content,
                description=description,
                tags=tag_list,
                is_default=is_default,
                parent_id=parent_id
            )
            print(f"Created prompt: {response['id']}")
        else:
            # Use local prompt registry
            prompt = prompt_registry.create_prompt(
                name=name,
                component=component,
                content=content,
                description=description,
                tags=tag_list,
                is_default=is_default,
                parent_id=parent_id
            )
            print(f"Created prompt: {prompt['id']}")
    except Exception as e:
        print(f"Error creating prompt: {e}")


def get_prompt(prompt_registry, api_client=None, prompt_id=None):
    """Get a prompt by ID.
    
    Args:
        prompt_registry: Prompt registry (local)
        api_client: API client for remote operations
        prompt_id: Prompt ID
    """
    try:
        if api_client:
            # Use API client for remote operation
            response = api_client.get_prompt(prompt_id)
            
            print(f"Prompt: {response['id']}")
            print(f"Name: {response['name']}")
            print(f"Component: {response['component']}")
            if response.get('is_default'):
                print("Default: Yes")
            if response.get('description'):
                print(f"Description: {response['description']}")
            if response.get('tags'):
                print(f"Tags: {', '.join(response['tags'])}")
            if response.get('parent_id'):
                print(f"Parent: {response['parent_id']}")
            print(f"Created: {response.get('created_at')}")
            print(f"Updated: {response.get('updated_at')}")
            print("\nContent:")
            print(response['content'])
        else:
            # Use local prompt registry
            prompt = prompt_registry.get_prompt(prompt_id)
            
            if not prompt:
                print(f"Prompt {prompt_id} not found")
                return
            
            print(f"Prompt: {prompt['id']}")
            print(f"Name: {prompt['name']}")
            print(f"Component: {prompt['component']}")
            if prompt.get('is_default'):
                print("Default: Yes")
            if prompt.get('description'):
                print(f"Description: {prompt['description']}")
            if prompt.get('tags'):
                print(f"Tags: {', '.join(prompt['tags'])}")
            if prompt.get('parent_id'):
                print(f"Parent: {prompt['parent_id']}")
            print(f"Created: {prompt.get('created_at')}")
            print(f"Updated: {prompt.get('updated_at')}")
            print("\nContent:")
            print(prompt['content'])
    except Exception as e:
        print(f"Error getting prompt: {e}")


def update_prompt(prompt_registry, api_client=None, prompt_id=None, content=None, file=None):
    """Update a prompt.
    
    Args:
        prompt_registry: Prompt registry (local)
        api_client: API client for remote operations
        prompt_id: Prompt ID
        content: New prompt content
        file: Read prompt content from file
    """
    try:
        # Read content from file if specified
        if file:
            with open(file, 'r') as f:
                content = f.read()
        
        if not content:
            print("Error: Prompt content is required")
            return
        
        if api_client:
            # Use API client for remote operation
            response = api_client.update_prompt(
                prompt_id=prompt_id,
                content=content
            )
            print(f"Updated prompt: {response['id']}")
        else:
            # Use local prompt registry
            prompt = prompt_registry.update_prompt(
                prompt_id=prompt_id,
                content=content
            )
            print(f"Updated prompt: {prompt['id']}")
    except Exception as e:
        print(f"Error updating prompt: {e}")


def delete_prompt(prompt_registry, api_client=None, prompt_id=None):
    """Delete a prompt.
    
    Args:
        prompt_registry: Prompt registry (local)
        api_client: API client for remote operations
        prompt_id: Prompt ID
    """
    try:
        if api_client:
            # Use API client for remote operation
            response = api_client.delete_prompt(prompt_id)
            if response.get('success'):
                print(f"Deleted prompt: {prompt_id}")
            else:
                print(f"Failed to delete prompt: {prompt_id}")
        else:
            # Use local prompt registry
            success = prompt_registry.delete_prompt(prompt_id)
            if success:
                print(f"Deleted prompt: {prompt_id}")
            else:
                print(f"Prompt {prompt_id} not found")
    except Exception as e:
        print(f"Error deleting prompt: {e}")


def compare_prompts(prompt_registry, api_client=None, prompt_id1=None, prompt_id2=None):
    """Compare two prompts.
    
    Args:
        prompt_registry: Prompt registry (local)
        api_client: API client for remote operations
        prompt_id1: First prompt ID
        prompt_id2: Second prompt ID
    """
    try:
        if api_client:
            # Use API client for remote operation
            response = api_client.compare_prompts(
                prompt_id1=prompt_id1,
                prompt_id2=prompt_id2
            )
            
            print(f"Comparison between {prompt_id1} and {prompt_id2}:")
            print(f"Similarity score: {response.get('similarity', 0):.2f}")
            print(f"Differences: {response.get('diff_count', 0)}")
            print("\nCommon tokens: ", response.get('common_token_count', 0))
            print("Unique tokens in first prompt: ", response.get('unique_tokens1_count', 0))
            print("Unique tokens in second prompt: ", response.get('unique_tokens2_count', 0))
            
            if 'diff' in response:
                print("\nDifferences:")
                print(response['diff'])
        else:
            # Use local prompt registry
            comparison = prompt_registry.compare_prompts(
                prompt_id1=prompt_id1,
                prompt_id2=prompt_id2
            )
            
            print(f"Comparison between {prompt_id1} and {prompt_id2}:")
            print(f"Similarity score: {comparison.get('similarity', 0):.2f}")
            print(f"Differences: {comparison.get('diff_count', 0)}")
            print("\nCommon tokens: ", comparison.get('common_token_count', 0))
            print("Unique tokens in first prompt: ", comparison.get('unique_tokens1_count', 0))
            print("Unique tokens in second prompt: ", comparison.get('unique_tokens2_count', 0))
            
            if 'diff' in comparison:
                print("\nDifferences:")
                print(comparison['diff'])
    except Exception as e:
        print(f"Error comparing prompts: {e}")


def generate_prompt(
    prompt_engine: PromptEngine,
    name: str,
    component: Optional[str] = None,
    variables: Optional[str] = None
) -> None:
    """Generate a prompt from a template.
    
    Args:
        prompt_engine: Prompt engine
        name: Template name
        component: Component to adapt for
        variables: Variable values (key=value,...)
    """
    try:
        # Parse variables
        variable_dict = parse_key_value_pairs(variables) if variables else {}
        
        # Generate the prompt
        prompt = prompt_engine.generate_prompt(
            template_name=name,
            component_name=component,
            **variable_dict
        )
        
        print("Generated prompt:")
        print(prompt)
    except Exception as e:
        print(f"Error generating prompt: {e}")


# System prompt commands
def create_system_prompt(
    component: str,
    role: Optional[str] = None,
    capabilities: Optional[str] = None,
    tone: Optional[str] = None,
    focus: Optional[str] = None,
    style: Optional[str] = None,
    personality: Optional[str] = None,
    output: Optional[str] = None
) -> None:
    """Create a system prompt for a component.
    
    Args:
        component: Component name
        role: Override role description
        capabilities: Override capabilities (comma-separated)
        tone: Override tone
        focus: Override focus
        style: Override style
        personality: Override personality
        output: Output file
    """
    try:
        from rhetor.templates.system_prompts import get_system_prompt
        
        # Prepare custom fields
        custom_fields = {}
        if role:
            custom_fields["role_description"] = role
        if capabilities:
            custom_fields["capabilities"] = capabilities.replace(",", "\n- ")
        if tone:
            custom_fields["tone"] = tone
        if focus:
            custom_fields["focus"] = focus
        if style:
            custom_fields["style"] = style
        if personality:
            custom_fields["personality"] = personality
        
        # Generate the system prompt
        system_prompt = get_system_prompt(component, custom_fields)
        
        # Output
        if output:
            with open(output, "w") as f:
                f.write(system_prompt)
            print(f"Saved system prompt to {output}")
        else:
            print("System prompt:")
            print(system_prompt)
    except Exception as e:
        print(f"Error creating system prompt: {e}")


def show_system_prompt(component: str) -> None:
    """Show the system prompt for a component.
    
    Args:
        component: Component name
    """
    try:
        from rhetor.templates.system_prompts import get_system_prompt
        
        system_prompt = get_system_prompt(component)
        print(system_prompt)
    except Exception as e:
        print(f"Error showing system prompt: {e}")


def list_components() -> None:
    """List all available components."""
    try:
        from rhetor.templates.system_prompts import COMPONENT_PROMPTS
        
        print("Available components:")
        for component, data in COMPONENT_PROMPTS.items():
            print(f"  {component}: {data.get('role_description', '').split('.',1)[0]}.")
    except Exception as e:
        print(f"Error listing components: {e}")


# Message commands
def send_message(
    communication_engine: CommunicationEngine,
    conversations_dir: str,
    content: str,
    recipient: Optional[str] = None,
    conversation: Optional[str] = None,
    message_type: str = "text"
) -> None:
    """Send a message.
    
    Args:
        communication_engine: Communication engine
        conversations_dir: Conversations directory
        content: Message content
        recipient: Recipient component
        conversation: Conversation ID
        message_type: Message type
    """
    message = communication_engine.send_message(
        content=content,
        recipient=recipient,
        conversation_id=conversation,
        message_type=message_type
    )
    
    # Save conversations
    communication_engine.save_conversations(conversations_dir)
    
    print(f"Sent message {message.message_id}")
    if not conversation and message.conversation_id:
        print(f"Created new conversation {message.conversation_id}")


def list_messages(
    communication_engine: CommunicationEngine,
    conversation: str,
    limit: Optional[int] = None
) -> None:
    """List messages in a conversation.
    
    Args:
        communication_engine: Communication engine
        conversation: Conversation ID
        limit: Maximum number of messages
    """
    conversation_obj = communication_engine.get_conversation(conversation)
    
    if not conversation_obj:
        print(f"Conversation {conversation} not found")
        return
    
    messages = conversation_obj.get_messages(limit=limit)
    
    if not messages:
        print("No messages found")
        return
    
    print(f"Messages in conversation {conversation}:")
    for message in messages:
        sender_str = message.sender
        recipient_str = f" to {message.recipient}" if message.recipient else ""
        print(f"  {message.message_id}: [{message.message_type}] {sender_str}{recipient_str}")
        print(f"    Content: {message.content[:50]}{'...' if len(message.content) > 50 else ''}")
        print(f"    Time: {format_timestamp(message.timestamp)}")


def show_message(
    communication_engine: CommunicationEngine,
    conversation: str,
    message: str
) -> None:
    """Show a message.
    
    Args:
        communication_engine: Communication engine
        conversation: Conversation ID
        message: Message ID
    """
    conversation_obj = communication_engine.get_conversation(conversation)
    
    if not conversation_obj:
        print(f"Conversation {conversation} not found")
        return
    
    # Find the message
    message_obj = None
    for msg in conversation_obj.messages:
        if msg.message_id == message:
            message_obj = msg
            break
    
    if not message_obj:
        print(f"Message {message} not found in conversation {conversation}")
        return
    
    print(f"Message: {message_obj.message_id}")
    print(f"Conversation: {conversation}")
    print(f"From: {message_obj.sender}")
    if message_obj.recipient:
        print(f"To: {message_obj.recipient}")
    print(f"Type: {message_obj.message_type}")
    print(f"Time: {format_timestamp(message_obj.timestamp)}")
    print("\nContent:")
    print(message_obj.content)
    
    if message_obj.references:
        print("\nReferences:")
        for ref in message_obj.references:
            print(f"  {ref}")
    
    if message_obj.metadata:
        print("\nMetadata:")
        for key, value in message_obj.metadata.items():
            print(f"  {key}: {value}")


# Conversation commands
def create_conversation(
    communication_engine: CommunicationEngine,
    conversations_dir: str,
    participants: str
) -> None:
    """Create a conversation.
    
    Args:
        communication_engine: Communication engine
        conversations_dir: Conversations directory
        participants: Participants (comma-separated)
    """
    # Parse participants
    participant_list = [p.strip() for p in participants.split(",")]
    
    # Create the conversation
    conversation_id = communication_engine.create_conversation(participant_list)
    
    # Save conversations
    communication_engine.save_conversations(conversations_dir)
    
    print(f"Created conversation {conversation_id} with participants: {participants}")


def list_conversations(communication_engine: CommunicationEngine) -> None:
    """List all conversations.
    
    Args:
        communication_engine: Communication engine
    """
    conversations = communication_engine.conversations
    
    if not conversations:
        print("No conversations found")
        return
    
    print("Conversations:")
    for conversation_id, conversation in conversations.items():
        participants_str = ", ".join(conversation.participants)
        message_count = len(conversation.messages)
        print(f"  {conversation_id}: {participants_str} ({message_count} messages)")
        print(f"    Created: {format_timestamp(conversation.created_at)}")
        print(f"    Updated: {format_timestamp(conversation.updated_at)}")


def show_conversation(communication_engine: CommunicationEngine, conversation: str) -> None:
    """Show a conversation.
    
    Args:
        communication_engine: Communication engine
        conversation: Conversation ID
    """
    conversation_obj = communication_engine.get_conversation(conversation)
    
    if not conversation_obj:
        print(f"Conversation {conversation} not found")
        return
    
    print(f"Conversation: {conversation}")
    print(f"Participants: {', '.join(conversation_obj.participants)}")
    print(f"Created: {format_timestamp(conversation_obj.created_at)}")
    print(f"Updated: {format_timestamp(conversation_obj.updated_at)}")
    print(f"Messages: {len(conversation_obj.messages)}")
    
    if conversation_obj.metadata:
        print("\nMetadata:")
        for key, value in conversation_obj.metadata.items():
            print(f"  {key}: {value}")
    
    if conversation_obj.messages:
        print("\nMessages:")
        for message in conversation_obj.messages:
            sender_str = message.sender
            recipient_str = f" to {message.recipient}" if message.recipient else ""
            print(f"  {format_timestamp(message.timestamp)} - {sender_str}{recipient_str}:")
            print(f"    {message.content}")


# Context management commands
async def list_contexts(context_manager, api_client=None):
    """List all available contexts.
    
    Args:
        context_manager: Context manager (local)
        api_client: API client for remote operations
    """
    try:
        if api_client:
            # Use API client for remote operation
            response = await api_client.list_contexts()
            contexts = response.get("contexts", [])
            
            if not contexts:
                print("No contexts found")
                return
            
            print(f"Found {len(contexts)} contexts:")
            for context in contexts:
                print(f"  {context['id']}")
                if context.get('message_count'):
                    print(f"    Messages: {context['message_count']}")
                if context.get('last_updated'):
                    print(f"    Last updated: {context['last_updated']}")
        else:
            # Use local context manager
            contexts = await context_manager.list_contexts()
            
            if not contexts:
                print("No contexts found")
                return
            
            print(f"Found {len(contexts)} contexts:")
            for context in contexts:
                print(f"  {context['id']}")
                if context.get('message_count'):
                    print(f"    Messages: {context['message_count']}")
                if context.get('last_updated'):
                    print(f"    Last updated: {context['last_updated']}")
    except Exception as e:
        print(f"Error listing contexts: {e}")


async def get_context(context_manager, api_client=None, context_id=None, limit=20, include_metadata=False):
    """Get messages in a context.
    
    Args:
        context_manager: Context manager (local)
        api_client: API client for remote operations
        context_id: Context ID
        limit: Maximum number of messages to return
        include_metadata: Include message metadata
    """
    try:
        if api_client:
            # Use API client for remote operation
            response = await api_client.get_context(
                context_id=context_id,
                limit=limit,
                include_metadata=include_metadata
            )
            messages = response.get("messages", [])
            
            if not messages:
                print(f"No messages found in context {context_id}")
                return
            
            print(f"Messages in context {context_id}:")
            for message in messages:
                print(f"  [{message.get('timestamp', 'Unknown')}] {message.get('role', 'Unknown')}: {message.get('content', '')[:50]}{'...' if len(message.get('content', '')) > 50 else ''}")
                
                if include_metadata and message.get('metadata'):
                    print(f"    Metadata:")
                    for key, value in message['metadata'].items():
                        print(f"      {key}: {value}")
        else:
            # Use local context manager
            messages = await context_manager.get_context_history(
                context_id=context_id,
                limit=limit
            )
            
            if not messages:
                print(f"No messages found in context {context_id}")
                return
            
            print(f"Messages in context {context_id}:")
            for message in messages:
                print(f"  [{message.get('timestamp', 'Unknown')}] {message.get('role', 'Unknown')}: {message.get('content', '')[:50]}{'...' if len(message.get('content', '')) > 50 else ''}")
                
                if include_metadata and message.get('metadata'):
                    print(f"    Metadata:")
                    for key, value in message['metadata'].items():
                        print(f"      {key}: {value}")
    except Exception as e:
        print(f"Error getting context messages: {e}")


async def delete_context(context_manager, api_client=None, context_id=None):
    """Delete a context and all its messages.
    
    Args:
        context_manager: Context manager (local)
        api_client: API client for remote operations
        context_id: Context ID
    """
    try:
        if api_client:
            # Use API client for remote operation
            response = await api_client.delete_context(context_id)
            if response.get('success'):
                print(f"Deleted context: {context_id}")
            else:
                print(f"Failed to delete context: {context_id}")
        else:
            # Use local context manager
            success = await context_manager.delete_context(context_id)
            if success:
                print(f"Deleted context: {context_id}")
            else:
                print(f"Failed to delete context: {context_id}")
    except Exception as e:
        print(f"Error deleting context: {e}")


async def search_context(context_manager, api_client=None, context_id=None, query=None, limit=5):
    """Search for messages in a context.
    
    Args:
        context_manager: Context manager (local)
        api_client: API client for remote operations
        context_id: Context ID
        query: Search query
        limit: Maximum number of results
    """
    try:
        if api_client:
            # Use API client for remote operation
            response = await api_client.search_context(
                context_id=context_id,
                query=query,
                limit=limit
            )
            results = response.get("results", [])
            
            if not results:
                print(f"No matching messages found in context {context_id}")
                return
            
            print(f"Search results for '{query}' in context {context_id}:")
            for result in results:
                print(f"  [{result.get('timestamp', 'Unknown')}] {result.get('role', 'Unknown')}: {result.get('content', '')[:50]}{'...' if len(result.get('content', '')) > 50 else ''}")
                if result.get('score'):
                    print(f"    Relevance: {result['score']:.2f}")
        else:
            # Use local context manager
            results = await context_manager.search_context(
                context_id=context_id,
                query=query,
                limit=limit
            )
            
            if not results:
                print(f"No matching messages found in context {context_id}")
                return
            
            print(f"Search results for '{query}' in context {context_id}:")
            for result in results:
                print(f"  [{result.get('timestamp', 'Unknown')}] {result.get('role', 'Unknown')}: {result.get('content', '')[:50]}{'...' if len(result.get('content', '')) > 50 else ''}")
                if result.get('score'):
                    print(f"    Relevance: {result['score']:.2f}")
    except Exception as e:
        print(f"Error searching context: {e}")


async def summarize_context(context_manager, api_client=None, context_id=None, max_tokens=150):
    """Generate a summary of a context.
    
    Args:
        context_manager: Context manager (local)
        api_client: API client for remote operations
        context_id: Context ID
        max_tokens: Maximum tokens for summary
    """
    try:
        if api_client:
            # Use API client for remote operation
            response = await api_client.summarize_context(
                context_id=context_id,
                max_tokens=max_tokens
            )
            summary = response.get("summary", "")
            
            if not summary:
                print(f"Failed to generate summary for context {context_id}")
                return
            
            print(f"Summary of context {context_id}:")
            print(summary)
        else:
            # Use local context manager
            summary = await context_manager.summarize_context(
                context_id=context_id,
                max_tokens=max_tokens
            )
            
            if not summary:
                print(f"Failed to generate summary for context {context_id}")
                return
            
            print(f"Summary of context {context_id}:")
            print(summary)
    except Exception as e:
        print(f"Error generating summary: {e}")


# Hermes commands
async def register_with_hermes(
    prompt_engine: PromptEngine,
    communication_engine: CommunicationEngine
) -> None:
    """Register with the Hermes service registry.
    
    Args:
        prompt_engine: Prompt engine
        communication_engine: Communication engine
    """
    try:
        # Register prompt engine
        prompt_result = await prompt_engine.register_with_hermes()
        
        # Register communication engine
        comm_result = await communication_engine.register_with_hermes()
        
        if prompt_result and comm_result:
            print("Successfully registered all Rhetor services with Hermes")
        elif prompt_result:
            print("Successfully registered prompt engine with Hermes")
            print("Failed to register communication engine with Hermes")
        elif comm_result:
            print("Failed to register prompt engine with Hermes")
            print("Successfully registered communication engine with Hermes")
        else:
            print("Failed to register with Hermes service registry")
    except Exception as e:
        print(f"Error registering with Hermes: {e}")