#!/usr/bin/env python3
"""
Tekton CLI Interface

Handles command-line argument parsing and dispatch for the Tekton launcher.
"""

import argparse
import asyncio
from typing import Dict, Any, List

from .components import COMPONENTS
from .startup import start_component, start_all_components
from .shutdown import stop_component, stop_all_components
from .status import get_component_status, print_component_status, print_system_info

def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Tekton Suite Launcher")
    
    # Main commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start Tekton components")
    start_parser.add_argument("components", nargs="*", help="Component IDs to start (default: all core components)")
    start_parser.add_argument("--all", action="store_true", help="Include optional components")
    start_parser.add_argument("--ollama-model", type=str, default="llama3", help="Model for Ollama")
    start_parser.add_argument("--claude-model", type=str, default="claude-3-sonnet-20240229", help="Model for Claude")
    start_parser.add_argument("--openai-model", type=str, default="gpt-4o-mini", help="Model for OpenAI")
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop Tekton components")
    stop_parser.add_argument("components", nargs="*", help="Component IDs to stop (default: all running components)")
    
    # Status command
    subparsers.add_parser("status", help="Show Tekton component status")
    
    # List command
    subparsers.add_parser("list", help="List available Tekton components")
    
    return parser.parse_args()

def handle_start_command(args):
    """
    Handle the 'start' command.
    
    Args:
        args: Parsed command-line arguments
    """
    if args.components:
        # Start specific components
        component_configs = {}
        
        # Add model configurations
        if "ollama" in args.components:
            component_configs["ollama"] = {"model": args.ollama_model}
        if "claude" in args.components:
            component_configs["claude"] = {"model": args.claude_model}
        if "openai" in args.components:
            component_configs["openai"] = {"model": args.openai_model}
        
        # First start the core dependencies
        core_components = ["database", "engram"]
        for component in core_components:
            if component not in args.components:
                print(f"Adding core dependency: {component}")
        
        # Combine core and requested components
        start_components = list(set(core_components + args.components))
        
        # Start each component
        for component in sorted(start_components, key=lambda c: COMPONENTS[c]["startup_sequence"]):
            if component in COMPONENTS:
                config = component_configs.get(component)
                result = asyncio.run(start_component(component, config))
                if result:
                    print(f"✅ Started {COMPONENTS[component]['name']}")
                else:
                    print(f"❌ Failed to start {COMPONENTS[component]['name']}")
            else:
                print(f"Unknown component: {component}")
    else:
        # Start all core components (or all if --all specified)
        result = asyncio.run(start_all_components(include_optional=args.all))
        if result:
            print("✅ All required Tekton components started successfully")
        else:
            print("❌ Failed to start some required Tekton components")
            
    # Show component status after starting
    status = get_component_status()
    print_component_status(status)

def handle_stop_command(args):
    """
    Handle the 'stop' command.
    
    Args:
        args: Parsed command-line arguments
    """
    if args.components:
        # Stop specific components
        for component in args.components:
            if component in COMPONENTS:
                result = asyncio.run(stop_component(component))
                if result:
                    print(f"✅ Stopped {COMPONENTS[component]['name']}")
                else:
                    print(f"❌ Failed to stop {COMPONENTS[component]['name']}")
            else:
                print(f"Unknown component: {component}")
    else:
        # Stop all running components
        result = asyncio.run(stop_all_components())
        if result:
            print("✅ All Tekton components stopped successfully")
        else:
            print("❌ Failed to stop some Tekton components")
            
    # Show component status after stopping
    status = get_component_status()
    print_component_status(status)

def handle_status_command():
    """Handle the 'status' command."""
    # Show component status
    status = get_component_status()
    print_component_status(status)
    
    # Show additional system information
    print_system_info()

def handle_list_command():
    """Handle the 'list' command."""
    # List available components
    print("Available Tekton Components:")
    print("==========================")
    
    # Sort by startup sequence
    component_ids = sorted(
        COMPONENTS.keys(),
        key=lambda c: COMPONENTS[c]["startup_sequence"]
    )
    
    for component_id in component_ids:
        component = COMPONENTS[component_id]
        optional_tag = " (Optional)" if component.get("optional", False) else ""
        dependencies = ", ".join(component["dependencies"]) if component["dependencies"] else "None"
        
        print(f"{component_id}: {component['name']}{optional_tag}")
        print(f"  Description: {component['description']}")
        print(f"  Dependencies: {dependencies}")
        print(f"  Startup Sequence: {component['startup_sequence']}")
        print("")

def process_command(args):
    """
    Process the command-line arguments and dispatch to the appropriate handler.
    
    Args:
        args: Parsed command-line arguments
    """
    if args.command == "start":
        handle_start_command(args)
    elif args.command == "stop":
        handle_stop_command(args)
    elif args.command == "status":
        handle_status_command()
    elif args.command == "list":
        handle_list_command()
    else:
        # Show help
        print("Please specify a command. Use --help for more information.")
        return False
    
    return True