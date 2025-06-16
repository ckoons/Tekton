"""Command-line interface for Telos.

This module provides a command-line interface for interacting with Telos.
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable

from telos.core.requirements import RequirementsManager
from telos.ui.cli_parser import parse_args
from telos.ui.cli_commands import (
    # Project commands
    create_project, list_projects, show_project, delete_project,
    # Requirement commands
    add_requirement, list_requirements, show_requirement, update_requirement, delete_requirement,
    # Visualization commands
    visualize_requirements,
    # Hermes commands
    register_with_hermes
)

# Import interactive refinement commands
from telos.ui.interactive_refine import (
    refine_requirement_cmd, 
    analyze_for_planning_cmd
)

logger = logging.getLogger(__name__)


class TelosCLI:
    """Command-line interface for Telos."""
    
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
            self.data_dir = os.path.join(home_dir, ".tekton", "data", "telos")
        
        os.makedirs(self.data_dir, exist_ok=True)
        self.requirements_dir = os.path.join(self.data_dir, "requirements")
        os.makedirs(self.requirements_dir, exist_ok=True)
        
        # Initialize modules
        self.requirements_manager = RequirementsManager(self.requirements_dir)
        
        # Set up command handlers
        self.commands = {
            "project": {
                "create": self.create_project,
                "list": self.list_projects,
                "show": self.show_project,
                "delete": self.delete_project,
            },
            "requirement": {
                "add": self.add_requirement,
                "list": self.list_requirements,
                "show": self.show_requirement,
                "update": self.update_requirement,
                "delete": self.delete_requirement,
            },
            "viz": {
                "requirements": self.visualize_requirements,
            },
            "refine": {
                "requirement": self.refine_requirement,
                "analyze": self.analyze_for_planning,
            },
            "prometheus": {
                "plan": self.create_plan,
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
            self.requirements_dir = os.path.join(self.data_dir, "requirements")
            os.makedirs(self.requirements_dir, exist_ok=True)
            self.requirements_manager = RequirementsManager(self.requirements_dir)
        
        # Execute command
        if not parsed_args.command:
            parser = parse_args()
            parser.print_help()
            return
        
        if not parsed_args.subcommand:
            from telos.ui.cli_parser import create_parser
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
            if parsed_args.command == "hermes":
                asyncio.run(cmd_handler(**args_dict))
            else:
                cmd_handler(**args_dict)
        else:
            print(f"Unknown command: {parsed_args.command} {parsed_args.subcommand}")
    
    # Command handlers (delegate to module functions)
    def create_project(self, **kwargs) -> None:
        create_project(self.requirements_manager, **kwargs)
    
    def list_projects(self, **kwargs) -> None:
        list_projects(self.requirements_manager, **kwargs)
    
    def show_project(self, **kwargs) -> None:
        show_project(self.requirements_manager, **kwargs)
    
    def delete_project(self, **kwargs) -> None:
        delete_project(self.requirements_manager, **kwargs)
    
    def add_requirement(self, **kwargs) -> None:
        add_requirement(self.requirements_manager, **kwargs)
    
    def list_requirements(self, **kwargs) -> None:
        list_requirements(self.requirements_manager, **kwargs)
    
    def show_requirement(self, **kwargs) -> None:
        show_requirement(self.requirements_manager, **kwargs)
    
    def update_requirement(self, **kwargs) -> None:
        update_requirement(self.requirements_manager, **kwargs)
    
    def delete_requirement(self, **kwargs) -> None:
        delete_requirement(self.requirements_manager, **kwargs)
    
    def visualize_requirements(self, **kwargs) -> None:
        visualize_requirements(self.requirements_manager, **kwargs)
    
    def refine_requirement(self, **kwargs) -> None:
        refine_requirement_cmd(self.requirements_manager, **kwargs)
    
    def analyze_for_planning(self, **kwargs) -> None:
        analyze_for_planning_cmd(self.requirements_manager, **kwargs)
    
    def create_plan(self, **kwargs) -> None:
        # Use the Prometheus connector
        from telos.prometheus_connector import create_plan_cmd
        asyncio.run(create_plan_cmd(self.requirements_manager, **kwargs))
        
    async def register_with_hermes(self, **kwargs) -> None:
        await register_with_hermes(self.requirements_manager, **kwargs)


def main() -> None:
    """Run the CLI."""
    cli = TelosCLI()
    cli.run()


if __name__ == "__main__":
    main()
