"""Command-line argument parser for Rhetor.

This module provides the argument parser for the Rhetor CLI.
"""

import argparse
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the Rhetor CLI.
    
    Returns:
        Argument parser
    """
    parser = argparse.ArgumentParser(description="Rhetor - Tekton's communication specialist")
    
    # Add global options
    parser.add_argument("--data-dir", help="Data directory")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    # Add subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Template management commands
    template_parser = subparsers.add_parser("template", help="Template management commands")
    template_subparsers = template_parser.add_subparsers(dest="subcommand", help="Template subcommand")
    
    template_list_parser = template_subparsers.add_parser("list", help="List templates")
    template_list_parser.add_argument("--category", help="Filter by category")
    template_list_parser.add_argument("--tag", help="Filter by tag")
    template_list_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    template_create_parser = template_subparsers.add_parser("create", help="Create a template")
    template_create_parser.add_argument("name", help="Template name")
    template_create_parser.add_argument("--content", help="Template content")
    template_create_parser.add_argument("--category", default="general", help="Template category")
    template_create_parser.add_argument("--description", help="Template description")
    template_create_parser.add_argument("--tags", help="Template tags (comma-separated)")
    template_create_parser.add_argument("--file", help="Read template content from file")
    template_create_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    template_get_parser = template_subparsers.add_parser("get", help="Get a template")
    template_get_parser.add_argument("id", help="Template ID")
    template_get_parser.add_argument("--version", help="Version ID")
    template_get_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    template_update_parser = template_subparsers.add_parser("update", help="Update a template")
    template_update_parser.add_argument("id", help="Template ID")
    template_update_parser.add_argument("--content", help="New template content")
    template_update_parser.add_argument("--file", help="Read template content from file")
    template_update_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    template_delete_parser = template_subparsers.add_parser("delete", help="Delete a template")
    template_delete_parser.add_argument("id", help="Template ID")
    template_delete_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    template_versions_parser = template_subparsers.add_parser("versions", help="List template versions")
    template_versions_parser.add_argument("id", help="Template ID")
    template_versions_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    template_render_parser = template_subparsers.add_parser("render", help="Render a template")
    template_render_parser.add_argument("id", help="Template ID")
    template_render_parser.add_argument("--variables", help="Variable values (key=value,...)")
    template_render_parser.add_argument("--version", help="Version ID")
    template_render_parser.add_argument("--output", help="Output file")
    template_render_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    # Prompt registry commands
    prompt_parser = subparsers.add_parser("prompt", help="Prompt registry commands")
    prompt_subparsers = prompt_parser.add_subparsers(dest="subcommand", help="Prompt subcommand")
    
    prompt_list_parser = prompt_subparsers.add_parser("list", help="List prompts")
    prompt_list_parser.add_argument("--component", help="Filter by component")
    prompt_list_parser.add_argument("--tag", help="Filter by tag")
    prompt_list_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    prompt_create_parser = prompt_subparsers.add_parser("create", help="Create a prompt")
    prompt_create_parser.add_argument("name", help="Prompt name")
    prompt_create_parser.add_argument("component", help="Component")
    prompt_create_parser.add_argument("--content", help="Prompt content")
    prompt_create_parser.add_argument("--description", help="Prompt description")
    prompt_create_parser.add_argument("--tags", help="Prompt tags (comma-separated)")
    prompt_create_parser.add_argument("--default", dest="is_default", action="store_true", help="Set as default prompt")
    prompt_create_parser.add_argument("--parent", dest="parent_id", help="Parent prompt ID")
    prompt_create_parser.add_argument("--file", help="Read prompt content from file")
    prompt_create_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    prompt_get_parser = prompt_subparsers.add_parser("get", help="Get a prompt")
    prompt_get_parser.add_argument("id", help="Prompt ID")
    prompt_get_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    prompt_update_parser = prompt_subparsers.add_parser("update", help="Update a prompt")
    prompt_update_parser.add_argument("id", help="Prompt ID")
    prompt_update_parser.add_argument("--content", help="New prompt content")
    prompt_update_parser.add_argument("--file", help="Read prompt content from file")
    prompt_update_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    prompt_delete_parser = prompt_subparsers.add_parser("delete", help="Delete a prompt")
    prompt_delete_parser.add_argument("id", help="Prompt ID")
    prompt_delete_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    prompt_compare_parser = prompt_subparsers.add_parser("compare", help="Compare prompts")
    prompt_compare_parser.add_argument("id1", help="First prompt ID")
    prompt_compare_parser.add_argument("id2", help="Second prompt ID")
    prompt_compare_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    # Legacy prompt generation command
    prompt_generate_parser = prompt_subparsers.add_parser("generate", help="Generate a prompt from template")
    prompt_generate_parser.add_argument("name", help="Template name")
    prompt_generate_parser.add_argument("--component", help="Component to adapt for")
    prompt_generate_parser.add_argument("--variables", help="Variable values (key=value,...)")
    
    # System prompt commands
    system_parser = subparsers.add_parser("system", help="System prompt commands")
    system_subparsers = system_parser.add_subparsers(dest="subcommand", help="System prompt subcommand")
    
    system_create_parser = system_subparsers.add_parser("create", help="Create a system prompt")
    system_create_parser.add_argument("component", help="Component name")
    system_create_parser.add_argument("--role", help="Override role description")
    system_create_parser.add_argument("--capabilities", help="Override capabilities (comma-separated)")
    system_create_parser.add_argument("--tone", help="Override tone")
    system_create_parser.add_argument("--focus", help="Override focus")
    system_create_parser.add_argument("--style", help="Override style")
    system_create_parser.add_argument("--personality", help="Override personality")
    system_create_parser.add_argument("--output", help="Output file")
    
    system_show_parser = system_subparsers.add_parser("show", help="Show a system prompt")
    system_show_parser.add_argument("component", help="Component name")
    
    system_list_components_parser = system_subparsers.add_parser("list-components", help="List available components")
    
    # Message commands
    message_parser = subparsers.add_parser("message", help="Message commands")
    message_subparsers = message_parser.add_subparsers(dest="subcommand", help="Message subcommand")
    
    message_send_parser = message_subparsers.add_parser("send", help="Send a message")
    message_send_parser.add_argument("content", help="Message content")
    message_send_parser.add_argument("--recipient", help="Recipient component")
    message_send_parser.add_argument("--conversation", help="Conversation ID")
    message_send_parser.add_argument("--type", dest="message_type", default="text", help="Message type")
    
    message_list_parser = message_subparsers.add_parser("list", help="List messages")
    message_list_parser.add_argument("conversation", help="Conversation ID")
    message_list_parser.add_argument("--limit", type=int, help="Maximum number of messages")
    
    message_show_parser = message_subparsers.add_parser("show", help="Show a message")
    message_show_parser.add_argument("conversation", help="Conversation ID")
    message_show_parser.add_argument("message", help="Message ID")
    
    # Conversation commands
    conversation_parser = subparsers.add_parser("conversation", help="Conversation commands")
    conversation_subparsers = conversation_parser.add_subparsers(dest="subcommand", help="Conversation subcommand")
    
    conversation_create_parser = conversation_subparsers.add_parser("create", help="Create a conversation")
    conversation_create_parser.add_argument("participants", help="Participants (comma-separated)")
    
    conversation_list_parser = conversation_subparsers.add_parser("list", help="List conversations")
    
    conversation_show_parser = conversation_subparsers.add_parser("show", help="Show a conversation")
    conversation_show_parser.add_argument("conversation", help="Conversation ID")
    
    # Context management commands
    context_parser = subparsers.add_parser("context", help="Context management commands")
    context_subparsers = context_parser.add_subparsers(dest="subcommand", help="Context subcommand")
    
    context_list_parser = context_subparsers.add_parser("list", help="List all contexts")
    context_list_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    context_get_parser = context_subparsers.add_parser("get", help="Get context messages")
    context_get_parser.add_argument("id", help="Context ID")
    context_get_parser.add_argument("--limit", type=int, default=20, help="Maximum number of messages")
    context_get_parser.add_argument("--metadata", action="store_true", help="Include message metadata")
    context_get_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    context_delete_parser = context_subparsers.add_parser("delete", help="Delete a context")
    context_delete_parser.add_argument("id", help="Context ID")
    context_delete_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    context_search_parser = context_subparsers.add_parser("search", help="Search for messages in a context")
    context_search_parser.add_argument("id", help="Context ID")
    context_search_parser.add_argument("query", help="Search query")
    context_search_parser.add_argument("--limit", type=int, default=5, help="Maximum number of results")
    context_search_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    context_summarize_parser = context_subparsers.add_parser("summarize", help="Generate a summary of a context")
    context_summarize_parser.add_argument("id", help="Context ID")
    context_summarize_parser.add_argument("--max-tokens", type=int, default=150, help="Maximum tokens for summary")
    context_summarize_parser.add_argument("--remote", action="store_true", help="Use remote API")
    
    # Hermes commands
    hermes_parser = subparsers.add_parser("hermes", help="Hermes commands")
    hermes_subparsers = hermes_parser.add_subparsers(dest="subcommand", help="Hermes subcommand")
    
    hermes_register_parser = hermes_subparsers.add_parser("register", help="Register with Hermes")
    
    return parser


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Parsed arguments
    """
    parser = create_parser()
    return parser.parse_args(args)