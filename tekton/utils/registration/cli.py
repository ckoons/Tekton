"""
Command-line interface for component registration.
"""

import os
from shared.env import TektonEnviron
import sys
import yaml
import json
import logging
import asyncio
import argparse
import signal
import traceback
from typing import Dict, Any, Optional, List, Tuple

from .config import load_component_config, validate_component_config, generate_component_config_template
from .registry import register_component, unregister_component, get_registration_status
from .models import ComponentConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("tekton-register")


# Signal handling for graceful shutdown
shutdown_event = asyncio.Event()
client = None


def handle_signal(signum, frame):
    """Handle termination signals."""
    logger.info(f"Received signal {signum}")
    shutdown_event.set()


# Set up signal handling
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


def print_status(status: Dict[str, Any], component_id: str) -> None:
    """Print the registration status."""
    print(f"Component: {component_id}")
    print(f"Registered: {status['registered']}")
    print(f"Status: {status['status']}")
    
    if status['registered'] and status['details']:
        details = status['details']
        print("\nDetails:")
        print(f"  Name: {details.get('name', 'N/A')}")
        print(f"  Version: {details.get('version', 'N/A')}")
        print(f"  Description: {details.get('description', 'N/A')}")
        print(f"  Host: {details.get('host', 'N/A')}")
        print(f"  Port: {details.get('port', 'N/A')}")
        
        capabilities = details.get('capabilities', [])
        print(f"\n  Capabilities: {len(capabilities)}")
        for capability in capabilities:
            print(f"    - {capability.get('name', 'N/A')} ({capability.get('id', 'N/A')})")
            methods = capability.get('methods', [])
            if methods:
                print(f"      Methods: {len(methods)}")
                for method in methods:
                    print(f"        - {method.get('name', 'N/A')} ({method.get('id', 'N/A')})")


async def register_command(args) -> int:
    """Register a component with Hermes."""
    global client
    
    component_id = args.component
    config_file = args.config
    hermes_url = args.hermes_url
    
    try:
        # Load component configuration
        config = load_component_config(component_id, config_file)
        
        # Validate configuration
        errors = validate_component_config(config)
        if errors:
            logger.error("Invalid component configuration:")
            for error in errors:
                logger.error(f"  - {error}")
            return 1
        
        # Register component
        success, client = await register_component(
            component_id, config, hermes_url, start_heartbeat=True
        )
        
        if success:
            logger.info(f"Component {component_id} registered successfully")
            
            # Wait for signals
            logger.info("Registration active. Press Ctrl+C to unregister and exit.")
            await shutdown_event.wait()
            
            # Unregister on shutdown
            logger.info(f"Unregistering component {component_id}")
            if client:
                await client.unregister()
                await client.close()
            
            return 0
        else:
            logger.error(f"Failed to register component {component_id}")
            return 1
    
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Invalid configuration: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error registering component: {e}")
        logger.debug(traceback.format_exc())
        return 1


async def unregister_command(args) -> int:
    """Unregister a component from Hermes."""
    component_id = args.component
    hermes_url = args.hermes_url
    
    try:
        # Unregister component
        success = await unregister_component(component_id, hermes_url)
        
        if success:
            logger.info(f"Component {component_id} unregistered successfully")
            return 0
        else:
            logger.error(f"Failed to unregister component {component_id}")
            return 1
    
    except Exception as e:
        logger.error(f"Error unregistering component: {e}")
        logger.debug(traceback.format_exc())
        return 1


async def status_command(args) -> int:
    """Get the registration status of a component."""
    component_id = args.component
    hermes_url = args.hermes_url
    
    try:
        # Get registration status
        status = await get_registration_status(component_id, hermes_url)
        
        # Print status
        print_status(status, component_id)
        
        # Return success if registered, failure otherwise
        return 0 if status["registered"] else 1
    
    except Exception as e:
        logger.error(f"Error getting component status: {e}")
        logger.debug(traceback.format_exc())
        return 1


def generate_command(args) -> int:
    """Generate a component configuration template."""
    component_id = args.component
    output_file = args.output
    port = args.port
    name = args.name or component_id.capitalize()
    
    try:
        # Generate template
        template = generate_component_config_template(component_id, name, port)
        
        # Convert to YAML
        yaml_template = yaml.dump(template, sort_keys=False, indent=2)
        
        # Write to file or stdout
        if output_file:
            with open(output_file, "w") as f:
                f.write(yaml_template)
            logger.info(f"Template written to {output_file}")
        else:
            print(yaml_template)
        
        return 0
    
    except Exception as e:
        logger.error(f"Error generating template: {e}")
        logger.debug(traceback.format_exc())
        return 1


async def list_command(args) -> int:
    """List all registered components."""
    hermes_url = args.hermes_url
    
    try:
        # Use the registry endpoint directly
        import aiohttp
        
        url = f"{hermes_url}/registry/services"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Print all registered components
                    print("Registered Components:")
                    for component in data:
                        print(f"  - {component.get('name', 'N/A')} ({component.get('component_id', 'N/A')})")
                        print(f"    Version: {component.get('version', 'N/A')}")
                        print(f"    Host: {component.get('host', 'N/A')}:{component.get('port', 'N/A')}")
                        print(f"    Capabilities: {len(component.get('capabilities', []))}")
                        print()
                    
                    return 0
                else:
                    logger.error(f"Failed to list components: {response.status}")
                    return 1
    
    except Exception as e:
        logger.error(f"Error listing components: {e}")
        logger.debug(traceback.format_exc())
        return 1


async def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Tekton Component Registration Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # register command
    register_parser = subparsers.add_parser("register", help="Register a component with Hermes")
    register_parser.add_argument("--component", required=True, help="Component ID")
    register_parser.add_argument("--config", help="Path to configuration file")
    register_parser.add_argument("--hermes-url", help="URL of the Hermes API")
    
    # unregister command
    unregister_parser = subparsers.add_parser("unregister", help="Unregister a component from Hermes")
    unregister_parser.add_argument("--component", required=True, help="Component ID")
    unregister_parser.add_argument("--hermes-url", help="URL of the Hermes API")
    
    # status command
    status_parser = subparsers.add_parser("status", help="Get the registration status of a component")
    status_parser.add_argument("--component", required=True, help="Component ID")
    status_parser.add_argument("--hermes-url", help="URL of the Hermes API")
    
    # generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a component configuration template")
    generate_parser.add_argument("--component", required=True, help="Component ID")
    generate_parser.add_argument("--name", help="Component name")
    generate_parser.add_argument("--port", type=int, default=8000, help="Component port")
    generate_parser.add_argument("--output", help="Output file path")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List all registered components")
    list_parser.add_argument("--hermes-url", help="URL of the Hermes API")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set Hermes URL from environment or default
    if hasattr(args, "hermes_url") and args.hermes_url is None:
        args.hermes_url = TektonEnviron.get("HERMES_URL", "http://localhost:8001/api")
    
    # Execute command
    if args.command == "register":
        return await register_command(args)
    elif args.command == "unregister":
        return await unregister_command(args)
    elif args.command == "status":
        return await status_command(args)
    elif args.command == "generate":
        return generate_command(args)
    elif args.command == "list":
        return await list_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)