"""Command-line interface for Rhetor.

This module provides a command-line interface for interacting with Rhetor.
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable

from rhetor.core.prompt_engine import PromptEngine, PromptLibrary, PromptTemplate
from rhetor.core.communication import CommunicationEngine, Message, Conversation
from rhetor.core.context_manager import ContextManager, TokenCounter
from rhetor.core.template_manager import TemplateManager
from rhetor.core.prompt_registry import PromptRegistry
from rhetor.cli.cli_parser import parse_args
from rhetor.cli.cli_commands import (
    # Template management commands
    list_templates, create_template, get_template, update_template,
    delete_template, list_template_versions, render_template,
    # Prompt registry commands
    list_prompts, create_prompt, get_prompt, update_prompt,
    delete_prompt, compare_prompts, generate_prompt,
    # System prompt commands
    create_system_prompt, show_system_prompt, list_components,
    # Message commands
    send_message, list_messages, show_message,
    # Conversation commands
    create_conversation, list_conversations, show_conversation,
    # Context management commands
    list_contexts, get_context, delete_context, search_context, summarize_context,
    # Hermes commands
    register_with_hermes
)

logger = logging.getLogger(__name__)


class RhetorCLI:
    """Command-line interface for Rhetor."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the CLI.
        
        Args:
            data_dir: Directory for storing data
        """
        # Set up data directory
        if data_dir:
            self.data_dir = data_dir
        else:
            home_dir = os.path.expanduser("~")
            self.data_dir = os.path.join(home_dir, ".tekton", "data", "rhetor")
        
        os.makedirs(self.data_dir, exist_ok=True)
        self.templates_dir = os.path.join(self.data_dir, "templates")
        os.makedirs(self.templates_dir, exist_ok=True)
        self.conversations_dir = os.path.join(self.data_dir, "conversations")
        os.makedirs(self.conversations_dir, exist_ok=True)
        self.contexts_dir = os.path.join(self.data_dir, "contexts")
        os.makedirs(self.contexts_dir, exist_ok=True)
        self.prompts_dir = os.path.join(self.data_dir, "prompts")
        os.makedirs(self.prompts_dir, exist_ok=True)
        
        # Initialize legacy modules
        self.prompt_library = PromptLibrary(self.templates_dir)
        self.prompt_engine = PromptEngine(self.prompt_library)
        self.communication_engine = CommunicationEngine("rhetor")
        
        # Initialize enhanced modules
        self.template_manager = TemplateManager(base_dir=self.templates_dir)
        self.prompt_registry = PromptRegistry(base_dir=self.prompts_dir, template_manager=self.template_manager)
        self.context_manager = None  # Will be initialized asynchronously when needed
        self.token_counter = TokenCounter()
        
        # Load conversations
        self.communication_engine.load_conversations(self.conversations_dir)
        
        # Set up command handlers
        self.commands = {
            "template": {
                "list": self.list_templates,
                "create": self.create_template,
                "get": self.get_template,
                "update": self.update_template,
                "delete": self.delete_template,
                "versions": self.list_template_versions,
                "render": self.render_template,
            },
            "prompt": {
                "list": self.list_prompts,
                "create": self.create_prompt,
                "get": self.get_prompt,
                "update": self.update_prompt,
                "delete": self.delete_prompt,
                "compare": self.compare_prompts,
                "generate": self.generate_prompt,
            },
            "system": {
                "create": self.create_system_prompt,
                "show": self.show_system_prompt,
                "list-components": self.list_components,
            },
            "message": {
                "send": self.send_message,
                "list": self.list_messages,
                "show": self.show_message,
            },
            "conversation": {
                "create": self.create_conversation,
                "list": self.list_conversations,
                "show": self.show_conversation,
            },
            "context": {
                "list": self.list_contexts,
                "get": self.get_context,
                "delete": self.delete_context,
                "search": self.search_context,
                "summarize": self.summarize_context,
            },
            "hermes": {
                "register": self.register_with_hermes,
            }
        }
    
    def run(self, args: Optional[List[str]] = None) -> None:
        """Run the CLI with the given arguments.
        
        Args:
            args: Command-line arguments
        """
        # Parse arguments
        parsed_args = parse_args(args)
        
        # Set up logging
        log_level = logging.DEBUG if parsed_args.debug else logging.INFO
        logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # Override data directory if specified
        if parsed_args.data_dir:
            self.data_dir = parsed_args.data_dir
            self.templates_dir = os.path.join(self.data_dir, "templates")
            os.makedirs(self.templates_dir, exist_ok=True)
            self.conversations_dir = os.path.join(self.data_dir, "conversations")
            os.makedirs(self.conversations_dir, exist_ok=True)
            self.contexts_dir = os.path.join(self.data_dir, "contexts")
            os.makedirs(self.contexts_dir, exist_ok=True)
            self.prompts_dir = os.path.join(self.data_dir, "prompts")
            os.makedirs(self.prompts_dir, exist_ok=True)
            
            # Reinitialize legacy modules
            self.prompt_library = PromptLibrary(self.templates_dir)
            self.prompt_engine = PromptEngine(self.prompt_library)
            self.communication_engine = CommunicationEngine("rhetor")
            self.communication_engine.load_conversations(self.conversations_dir)
            
            # Reinitialize enhanced modules
            self.template_manager = TemplateManager(base_dir=self.templates_dir)
            self.prompt_registry = PromptRegistry(base_dir=self.prompts_dir, template_manager=self.template_manager)
            self.context_manager = None  # Will be initialized lazily when needed
            self.token_counter = TokenCounter()
        
        # Execute command
        if not parsed_args.command:
            parser = parse_args()
            parser.print_help()
            return
        
        if not parsed_args.subcommand:
            from rhetor.cli.cli_parser import create_parser
            parser = create_parser()
            subparsers = parser._subparsers._group_actions[0]
            subparsers._name_parser_map[parsed_args.command].print_help()
            return
        
        # Look up and execute the appropriate command handler
        cmd_group = self.commands.get(parsed_args.command, {})
        cmd_handler = cmd_group.get(parsed_args.subcommand)
        
        if cmd_handler:
            # Convert args to dictionary and remove command and subcommand
            args_dict = vars(parsed_args)
            args_dict.pop("command")
            args_dict.pop("subcommand")
            args_dict.pop("debug", None)
            args_dict.pop("data_dir", None)
            
            # For commands that may need asyncio
            if parsed_args.command == "hermes" or parsed_args.command == "context":
                asyncio.run(cmd_handler(**args_dict))
            else:
                cmd_handler(**args_dict)
        else:
            print(f"Unknown command: {parsed_args.command} {parsed_args.subcommand}")
    
    # Command handler methods that delegate to module functions
    
    # Template management commands
    def list_templates(self, **kwargs) -> None:
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            list_templates(None, api_client, **kwargs)
        else:
            list_templates(self.template_manager, None, **kwargs)
    
    def create_template(self, **kwargs) -> None:
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            create_template(None, api_client, **kwargs)
        else:
            create_template(self.template_manager, None, **kwargs)
    
    def get_template(self, **kwargs) -> None:
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            get_template(None, api_client, **kwargs)
        else:
            get_template(self.template_manager, None, **kwargs)
    
    def update_template(self, **kwargs) -> None:
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            update_template(None, api_client, **kwargs)
        else:
            update_template(self.template_manager, None, **kwargs)
    
    def delete_template(self, **kwargs) -> None:
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            delete_template(None, api_client, **kwargs)
        else:
            delete_template(self.template_manager, None, **kwargs)
    
    def list_template_versions(self, **kwargs) -> None:
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            list_template_versions(None, api_client, **kwargs)
        else:
            list_template_versions(self.template_manager, None, **kwargs)
    
    def render_template(self, **kwargs) -> None:
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            render_template(None, api_client, **kwargs)
        else:
            render_template(self.template_manager, None, **kwargs)
    
    # Prompt registry commands
    def list_prompts(self, **kwargs) -> None:
        # Check if this is the new prompt registry command or legacy command
        if "component" in kwargs or "tag" in kwargs or "remote" in kwargs:
            api_client = None  # TODO: Initialize API client if remote=True
            if kwargs.pop("remote", False):
                list_prompts(None, api_client, **kwargs)
            else:
                list_prompts(self.prompt_registry, None, **kwargs)
        else:
            # Legacy behavior
            list_prompts(self.prompt_library, **kwargs)
    
    def create_prompt(self, **kwargs) -> None:
        # Check if this is the new prompt registry command or legacy command
        if "component" in kwargs or "tags" in kwargs or "is_default" in kwargs or "parent_id" in kwargs or "file" in kwargs or "remote" in kwargs:
            api_client = None  # TODO: Initialize API client if remote=True
            if kwargs.pop("remote", False):
                create_prompt(None, api_client, **kwargs)
            else:
                create_prompt(self.prompt_registry, None, **kwargs)
        else:
            # Legacy behavior
            create_prompt(self.prompt_library, self.templates_dir, **kwargs)
    
    def get_prompt(self, **kwargs) -> None:
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            get_prompt(None, api_client, **kwargs)
        else:
            get_prompt(self.prompt_registry, None, **kwargs)
    
    def update_prompt(self, **kwargs) -> None:
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            update_prompt(None, api_client, **kwargs)
        else:
            update_prompt(self.prompt_registry, None, **kwargs)
    
    def delete_prompt(self, **kwargs) -> None:
        # Check if this is name (legacy) or id (new)
        if "name" in kwargs:
            # Legacy behavior
            delete_prompt(self.prompt_library, self.templates_dir, **kwargs)
        else:
            api_client = None  # TODO: Initialize API client if remote=True
            if kwargs.pop("remote", False):
                delete_prompt(None, api_client, **kwargs)
            else:
                delete_prompt(self.prompt_registry, None, **kwargs)
    
    def compare_prompts(self, **kwargs) -> None:
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            compare_prompts(None, api_client, **kwargs)
        else:
            compare_prompts(self.prompt_registry, None, **kwargs)
    
    def generate_prompt(self, **kwargs) -> None:
        generate_prompt(self.prompt_engine, **kwargs)
    
    # System prompt commands
    def create_system_prompt(self, **kwargs) -> None:
        create_system_prompt(**kwargs)
    
    def show_system_prompt(self, **kwargs) -> None:
        show_system_prompt(**kwargs)
    
    def list_components(self, **kwargs) -> None:
        list_components(**kwargs)
    
    # Message commands
    def send_message(self, **kwargs) -> None:
        send_message(self.communication_engine, self.conversations_dir, **kwargs)
    
    def list_messages(self, **kwargs) -> None:
        list_messages(self.communication_engine, **kwargs)
    
    def show_message(self, **kwargs) -> None:
        show_message(self.communication_engine, **kwargs)
    
    # Conversation commands
    def create_conversation(self, **kwargs) -> None:
        create_conversation(self.communication_engine, self.conversations_dir, **kwargs)
    
    def list_conversations(self, **kwargs) -> None:
        list_conversations(self.communication_engine, **kwargs)
    
    def show_conversation(self, **kwargs) -> None:
        show_conversation(self.communication_engine, **kwargs)
    
    # Context management commands
    async def list_contexts(self, **kwargs) -> None:
        # Lazy initialize context manager if needed
        if self.context_manager is None:
            self.context_manager = ContextManager(base_dir=self.contexts_dir, token_counter=self.token_counter)
            await self.context_manager.initialize()
        
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            await list_contexts(None, api_client, **kwargs)
        else:
            await list_contexts(self.context_manager, None, **kwargs)
    
    async def get_context(self, **kwargs) -> None:
        # Lazy initialize context manager if needed
        if self.context_manager is None:
            self.context_manager = ContextManager(base_dir=self.contexts_dir, token_counter=self.token_counter)
            await self.context_manager.initialize()
        
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            await get_context(None, api_client, **kwargs)
        else:
            await get_context(self.context_manager, None, **kwargs)
    
    async def delete_context(self, **kwargs) -> None:
        # Lazy initialize context manager if needed
        if self.context_manager is None:
            self.context_manager = ContextManager(base_dir=self.contexts_dir, token_counter=self.token_counter)
            await self.context_manager.initialize()
        
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            await delete_context(None, api_client, **kwargs)
        else:
            await delete_context(self.context_manager, None, **kwargs)
    
    async def search_context(self, **kwargs) -> None:
        # Lazy initialize context manager if needed
        if self.context_manager is None:
            self.context_manager = ContextManager(base_dir=self.contexts_dir, token_counter=self.token_counter)
            await self.context_manager.initialize()
        
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            await search_context(None, api_client, **kwargs)
        else:
            await search_context(self.context_manager, None, **kwargs)
    
    async def summarize_context(self, **kwargs) -> None:
        # Lazy initialize context manager if needed
        if self.context_manager is None:
            self.context_manager = ContextManager(base_dir=self.contexts_dir, token_counter=self.token_counter)
            await self.context_manager.initialize()
        
        api_client = None  # TODO: Initialize API client if remote=True
        if kwargs.pop("remote", False):
            await summarize_context(None, api_client, **kwargs)
        else:
            await summarize_context(self.context_manager, None, **kwargs)
    
    # Hermes commands
    async def register_with_hermes(self, **kwargs) -> None:
        await register_with_hermes(self.prompt_engine, self.communication_engine, **kwargs)


def main() -> None:
    """Run the CLI."""
    cli = RhetorCLI()
    cli.run()


if __name__ == "__main__":
    main()