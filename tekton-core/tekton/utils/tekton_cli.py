"""
Tekton CLI Argument Parsing

This module provides standardized command-line interface parsing for Tekton components,
with consistent help text, subcommand handling, and validation.

Usage:
    from tekton.utils.tekton_cli import (
        create_cli_parser,
        TektonCLI,
        run_cli_command
    )
    
    # Function-based approach
    parser = create_cli_parser(
        component_id="mycomponent",
        description="My Component CLI",
        version="1.0.0"
    )
    parser.add_argument("--config", help="Path to config file")
    args = parser.parse_args()
    
    # Class-based approach
    cli = TektonCLI(
        component_id="mycomponent",
        description="My Component CLI",
        version="1.0.0"
    )
    
    @cli.command("start")
    def start_command(args):
        print(f"Starting with config: {args.config}")
    
    cli.run()
"""

import os
import sys
import json
import logging
import argparse
import textwrap
import asyncio
from enum import Enum
from functools import wraps
from typing import Dict, Any, Optional, List, Union, Callable, Tuple, Set, Type, TypeVar, cast

# Set up logger
logger = logging.getLogger(__name__)

# Type variable for CLI commands
F = TypeVar('F', bound=Callable[..., Any])


class TektonCliError(Exception):
    """Base class for Tekton CLI errors."""
    pass


class SubcommandError(TektonCliError):
    """Raised when there is an error with a subcommand."""
    pass


class LogLevel(Enum):
    """Log level options."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def create_cli_parser(
    component_id: str,
    description: str,
    version: str = "1.0.0",
    epilog: Optional[str] = None,
    add_common_args: bool = True
) -> argparse.ArgumentParser:
    """
    Create a standardized command-line argument parser.
    
    Args:
        component_id: Component identifier
        description: Description for help text
        version: Component version
        epilog: Text to display after the argument help
        add_common_args: Whether to add common arguments
        
    Returns:
        Configured argument parser
    """
    # Create parser
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add version information
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"{component_id.capitalize()} v{version}"
    )
    
    # Add common arguments
    if add_common_args:
        parser.add_argument(
            "--log-level",
            choices=[level.name for level in LogLevel],
            default=os.environ.get("TEKTON_LOG_LEVEL", "INFO"),
            help="Logging level"
        )
        
        parser.add_argument(
            "--config",
            dest="config_file",
            help="Path to configuration file"
        )
        
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output"
        )
    
    return parser


def create_subcommand_parsers(
    parser: argparse.ArgumentParser
) -> Tuple[argparse._SubParsersAction, Dict[str, argparse.ArgumentParser]]:
    """
    Create subcommand parsers.
    
    Args:
        parser: Main argument parser
        
    Returns:
        Tuple of (subparsers action, subparser dictionary)
    """
    # Create subparsers
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        help="Commands"
    )
    
    # Make subcommand required
    subparsers.required = True
    
    # Dictionary to store subparsers
    subparser_dict: Dict[str, argparse.ArgumentParser] = {}
    
    return subparsers, subparser_dict


def add_subcommand(
    subparsers: argparse._SubParsersAction,
    subparser_dict: Dict[str, argparse.ArgumentParser],
    name: str,
    help_text: str,
    description: Optional[str] = None
) -> argparse.ArgumentParser:
    """
    Add a subcommand to a parser.
    
    Args:
        subparsers: Subparsers action
        subparser_dict: Dictionary of subparsers
        name: Subcommand name
        help_text: Help text for the subcommand
        description: Detailed description
        
    Returns:
        Subcommand parser
    """
    # Create subcommand parser
    subparser = subparsers.add_parser(
        name,
        help=help_text,
        description=description or help_text
    )
    
    # Store in dictionary
    subparser_dict[name] = subparser
    
    return subparser


def configure_logging_from_args(args: argparse.Namespace) -> None:
    """
    Configure logging based on CLI arguments.
    
    Args:
        args: Parsed command-line arguments
    """
    log_level = args.log_level if hasattr(args, "log_level") else "INFO"
    verbose = args.verbose if hasattr(args, "verbose") else False
    
    # Set log level
    level = getattr(logging, log_level)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        handlers=[logging.StreamHandler()]
    )
    
    # Set more verbose format if requested
    if verbose:
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setFormatter(logging.Formatter(
                    "%(asctime)s [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] %(message)s"
                ))
    
    logger.debug(f"Logging configured at level {log_level}")


def load_config_from_args(args: argparse.Namespace) -> Optional[Dict[str, Any]]:
    """
    Load configuration from CLI arguments.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Configuration dictionary or None
    """
    if not hasattr(args, "config_file") or not args.config_file:
        return None
    
    config_file = args.config_file
    
    try:
        # Check file existence
        if not os.path.exists(config_file):
            logger.error(f"Configuration file not found: {config_file}")
            return None
        
        # Load configuration
        with open(config_file, 'r') as f:
            # Parse based on file extension
            if config_file.endswith('.json'):
                return json.load(f)
            elif config_file.endswith(('.yml', '.yaml')):
                try:
                    import yaml
                    return yaml.safe_load(f)
                except ImportError:
                    logger.error("YAML support requires PyYAML: pip install pyyaml")
                    return None
            else:
                # Try JSON first, then YAML if available
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    try:
                        import yaml
                        f.seek(0)
                        return yaml.safe_load(f)
                    except ImportError:
                        logger.error("Failed to parse config file as JSON and YAML support not available")
                        return None
    
    except Exception as e:
        logger.error(f"Error loading configuration file: {e}")
        return None


def run_cli_command(command_func: Callable[[argparse.Namespace], Any], args: argparse.Namespace) -> int:
    """
    Run a CLI command function and handle errors.
    
    Args:
        command_func: Command function to run
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Configure logging
        if hasattr(args, "log_level"):
            configure_logging_from_args(args)
        
        # Run the command function
        result = command_func(args)
        
        # Handle coroutines
        if asyncio.iscoroutine(result):
            try:
                asyncio.run(result)
            except Exception as e:
                logger.error(f"Error in async command: {e}")
                return 1
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("Command interrupted")
        return 130
    except TektonCliError as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


class TektonCLI:
    """
    Class-based interface for Tekton component CLIs.
    
    This class provides a more structured approach to building CLIs, with support
    for subcommands, auto-generated help, and standardized argument parsing.
    """
    
    def __init__(
        self,
        component_id: str,
        description: str,
        version: str = "1.0.0",
        epilog: Optional[str] = None
    ):
        """
        Initialize a Tekton CLI.
        
        Args:
            component_id: Component identifier
            description: Description for help text
            version: Component version
            epilog: Text to display after the argument help
        """
        self.component_id = component_id
        self.description = description
        self.version = version
        self.epilog = epilog
        
        # Create parser
        self.parser = create_cli_parser(
            component_id=component_id,
            description=description,
            version=version,
            epilog=epilog
        )
        
        # Create subcommand parsers
        self.subparsers, self.subparser_dict = create_subcommand_parsers(self.parser)
        
        # Dictionary to store command handlers
        self.handlers: Dict[str, Callable] = {}
    
    def command(
        self,
        name: str,
        help_text: Optional[str] = None,
        description: Optional[str] = None
    ) -> Callable[[F], F]:
        """
        Decorator to register a command.
        
        Args:
            name: Command name
            help_text: Help text for the command
            description: Detailed description
            
        Returns:
            Decorator function
        """
        def decorator(func: F) -> F:
            # Use function docstring for help if not provided
            command_help = help_text or func.__doc__ or f"{name} command"
            command_desc = description or func.__doc__ or command_help
            
            # Clean up multiline docstring
            command_help = command_help.strip().split('\n')[0]
            command_desc = textwrap.dedent(command_desc).strip()
            
            # Create subcommand parser
            subparser = add_subcommand(
                self.subparsers,
                self.subparser_dict,
                name,
                command_help,
                command_desc
            )
            
            # Add common arguments
            subparser.add_argument(
                "--log-level",
                choices=[level.name for level in LogLevel],
                default=os.environ.get("TEKTON_LOG_LEVEL", "INFO"),
                help="Logging level"
            )
            
            subparser.add_argument(
                "--verbose",
                action="store_true",
                help="Enable verbose output"
            )
            
            # Store handler
            self.handlers[name] = func
            
            # Allow further argument customization by returning the function
            func.parser = subparser  # type: ignore
            
            return func
        
        return decorator
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Parse arguments and run the appropriate command.
        
        Args:
            args: Command-line arguments (defaults to sys.argv[1:])
            
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        # Parse arguments
        parsed_args = self.parser.parse_args(args)
        
        # Get command
        command = parsed_args.command
        
        # Get handler
        handler = self.handlers.get(command)
        if not handler:
            self.parser.print_help()
            return 1
        
        # Run command
        return run_cli_command(handler, parsed_args)


# Helper functions for common CLI patterns

def confirm_action(prompt: str, default: bool = False) -> bool:
    """
    Prompt for confirmation before an action.
    
    Args:
        prompt: Confirmation prompt
        default: Default action if user presses Enter
        
    Returns:
        True if user confirmed, False otherwise
    """
    default_text = "Y/n" if default else "y/N"
    prompt_text = f"{prompt} [{default_text}] "
    
    while True:
        response = input(prompt_text).strip().lower()
        
        if not response:
            return default
        
        if response in ('y', 'yes'):
            return True
        
        if response in ('n', 'no'):
            return False
        
        print("Please enter 'y' or 'n'")


def select_option(
    prompt: str,
    options: List[str],
    default: Optional[int] = None
) -> int:
    """
    Prompt user to select an option.
    
    Args:
        prompt: Selection prompt
        options: List of options
        default: Default option index if user presses Enter
        
    Returns:
        Selected option index
    """
    # Print options
    print(prompt)
    for i, option in enumerate(options):
        default_mark = " (default)" if i == default else ""
        print(f"{i+1}. {option}{default_mark}")
    
    # Get selection
    while True:
        if default is not None:
            response = input(f"Enter selection [1-{len(options)}, default={default+1}]: ")
        else:
            response = input(f"Enter selection [1-{len(options)}]: ")
        
        if not response and default is not None:
            return default
        
        try:
            selection = int(response)
            if 1 <= selection <= len(options):
                return selection - 1
            
            print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")


def parse_key_value_args(args_list: List[str]) -> Dict[str, str]:
    """
    Parse key=value arguments.
    
    Args:
        args_list: List of key=value strings
        
    Returns:
        Dictionary of parsed key-value pairs
        
    Raises:
        TektonCliError: If argument format is invalid
    """
    result = {}
    
    for arg in args_list:
        # Check format
        if '=' not in arg:
            raise TektonCliError(f"Invalid key-value format: {arg}, expected key=value")
        
        # Split key and value
        key, value = arg.split('=', 1)
        
        # Check key
        if not key:
            raise TektonCliError(f"Empty key in argument: {arg}")
        
        # Store key-value pair
        result[key] = value
    
    return result


def show_progress(
    iterable: Union[List[Any], range],
    desc: str = "Processing",
    total: Optional[int] = None
) -> None:
    """
    Show a progress bar for an iterable.
    
    Args:
        iterable: Iterable to process
        desc: Description for the progress bar
        total: Total number of items (auto-detected if not provided)
    """
    # Try to use tqdm if available
    try:
        from tqdm import tqdm
        yield from tqdm(iterable, desc=desc, total=total)
        return
    except ImportError:
        pass
    
    # Simple fallback
    if total is None:
        try:
            total = len(iterable)  # type: ignore
        except (TypeError, AttributeError):
            total = 0
    
    for i, item in enumerate(iterable):
        # Print progress every 10 items
        if i % 10 == 0 or i == total - 1:
            if total > 0:
                percent = (i + 1) / total * 100
                print(f"{desc}: {i+1}/{total} ({percent:.1f}%)", end="\r")
            else:
                print(f"{desc}: {i+1} items", end="\r")
        
        yield item
    
    # Print newline after completion
    print()


# Common CLI commands that can be reused

def add_version_command(cli: TektonCLI, component_id: str, version: str) -> None:
    """
    Add a version command to a CLI.
    
    Args:
        cli: TektonCLI instance
        component_id: Component identifier
        version: Component version
    """
    @cli.command("version", "Show version information")
    def version_command(args: argparse.Namespace) -> None:
        print(f"{component_id.capitalize()} v{version}")


def add_status_command(
    cli: TektonCLI,
    status_func: Callable[[], Dict[str, Any]]
) -> None:
    """
    Add a status command to a CLI.
    
    Args:
        cli: TektonCLI instance
        status_func: Function to get component status
    """
    @cli.command("status", "Show component status")
    def status_command(args: argparse.Namespace) -> None:
        # Get status
        status = status_func()
        
        # Print status
        print(f"Status: {status.get('status', 'unknown')}")
        
        # Print additional information
        for key, value in status.items():
            if key != "status":
                print(f"{key}: {value}")


def add_start_command(
    cli: TektonCLI,
    start_func: Callable[[argparse.Namespace], Any],
    options_setup: Optional[Callable[[argparse.ArgumentParser], None]] = None
) -> None:
    """
    Add a start command to a CLI.
    
    Args:
        cli: TektonCLI instance
        start_func: Function to start the component
        options_setup: Optional function to set up command options
    """
    @cli.command("start", "Start the component")
    def start_command(args: argparse.Namespace) -> Any:
        return start_func(args)
    
    # Set up options if provided
    if options_setup:
        options_setup(start_command.parser)  # type: ignore


def add_stop_command(
    cli: TektonCLI,
    stop_func: Callable[[argparse.Namespace], Any],
    options_setup: Optional[Callable[[argparse.ArgumentParser], None]] = None
) -> None:
    """
    Add a stop command to a CLI.
    
    Args:
        cli: TektonCLI instance
        stop_func: Function to stop the component
        options_setup: Optional function to set up command options
    """
    @cli.command("stop", "Stop the component")
    def stop_command(args: argparse.Namespace) -> Any:
        return stop_func(args)
    
    # Set up options if provided
    if options_setup:
        options_setup(stop_command.parser)  # type: ignore


def add_config_command(
    cli: TektonCLI,
    get_config_func: Callable[[], Dict[str, Any]],
    set_config_func: Optional[Callable[[str, str], bool]] = None
) -> None:
    """
    Add a config command to a CLI.
    
    Args:
        cli: TektonCLI instance
        get_config_func: Function to get configuration
        set_config_func: Optional function to set configuration
    """
    @cli.command("config", "Manage component configuration")
    def config_command(args: argparse.Namespace) -> None:
        if args.action == "get":
            # Get all configuration
            config = get_config_func()
            
            # Filter by key if provided
            if args.key:
                if args.key in config:
                    print(f"{args.key}={config[args.key]}")
                else:
                    print(f"Key not found: {args.key}")
                    sys.exit(1)
            else:
                # Print all configuration
                for key, value in config.items():
                    print(f"{key}={value}")
        
        elif args.action == "set" and set_config_func:
            # Set configuration
            if not args.key or not args.value:
                print("Key and value are required for set action")
                sys.exit(1)
            
            # Set configuration
            success = set_config_func(args.key, args.value)
            
            if not success:
                print(f"Failed to set {args.key}={args.value}")
                sys.exit(1)
            
            print(f"Set {args.key}={args.value}")
        
        else:
            print("Invalid action")
            sys.exit(1)
    
    # Set up subcommands
    config_subparsers = config_command.parser.add_subparsers(  # type: ignore
        title="actions",
        dest="action",
        help="Config actions"
    )
    config_subparsers.required = True
    
    # Get config
    get_parser = config_subparsers.add_parser(
        "get",
        help="Get configuration"
    )
    get_parser.add_argument(
        "key",
        nargs="?",
        help="Configuration key to get (all keys if not specified)"
    )
    
    # Set config
    if set_config_func:
        set_parser = config_subparsers.add_parser(
            "set",
            help="Set configuration"
        )
        set_parser.add_argument(
            "key",
            help="Configuration key to set"
        )
        set_parser.add_argument(
            "value",
            help="Configuration value"
        )