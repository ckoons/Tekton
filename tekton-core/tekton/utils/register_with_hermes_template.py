#!/usr/bin/env python3
"""
Register {COMPONENT_NAME} with Hermes Service Registry

This script registers the {COMPONENT_NAME} component with the Hermes service registry,
allowing other components to discover and use its capabilities.

Usage:
    python register_with_hermes.py [options]

Environment Variables:
    HERMES_URL: URL of the Hermes API (default: http://localhost:8000/api)
    STARTUP_INSTRUCTIONS_FILE: Path to JSON file with startup instructions
    {COMPONENT_UPPER}_API_ENDPOINT: API endpoint for the component (optional)

Options:
    --hermes-url: URL of the Hermes API (overrides HERMES_URL env var)
    --instructions-file: Path to startup instructions JSON file
    --endpoint: API endpoint for the component
    --help: Show this help message
"""

import os
import sys
import asyncio
import signal
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from shared.env import TektonEnviron

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("{COMPONENT_LOWER}.registration")

# Get the directory where this script is located
script_dir = Path(__file__).parent.absolute()

# Add parent directories to path (specific to your component's structure)
component_dir = os.path.abspath(os.path.join(script_dir, "../.."))
tekton_root = os.path.abspath(os.path.join(component_dir, ".."))
tekton_core_dir = os.path.join(tekton_root, "tekton-core")

# Add to Python path
sys.path.insert(0, str(component_dir))
sys.path.insert(0, str(tekton_root))
sys.path.insert(0, str(tekton_core_dir))

# Check if we're in a virtual environment
in_venv = sys.prefix != sys.base_prefix
if not in_venv:
    venv_dir = os.path.join(component_dir, "venv")
    if os.path.exists(venv_dir):
        logger.warning(f"Not running in the {COMPONENT_NAME} virtual environment.")
        logger.warning(f"Consider activating it with: source {venv_dir}/bin/activate")

# Import registration utilities
try:
    from tekton.utils.hermes_registration import (
        HermesRegistrationClient,
        register_component,
        load_startup_instructions
    )
    REGISTRATION_UTILS_AVAILABLE = True
except ImportError:
    logger.warning("Could not import Tekton registration utilities.")
    logger.warning("Falling back to direct Hermes client import.")
    REGISTRATION_UTILS_AVAILABLE = False

    # Try to import from Hermes directly
    try:
        hermes_dir = TektonEnviron.get("HERMES_DIR")
        if hermes_dir and os.path.exists(hermes_dir):
            sys.path.insert(0, hermes_dir)
            
        from hermes.utils.registration_helper import register_component
        logger.info("Successfully imported Hermes registration helper")
    except ImportError as e:
        logger.error(f"Error importing Hermes modules: {e}")
        logger.error("Make sure Hermes is properly installed and accessible")
        sys.exit(1)

# Import {COMPONENT_NAME}-specific modules
try:
    # Import your component's modules here
    # Example: from {COMPONENT_LOWER}.integrations.hermes.adapter import HermesAdapter
    from {COMPONENT_LOWER}.core.{MAIN_MODULE} import {MAIN_CLASS}
    logger.info(f"Successfully imported {COMPONENT_NAME} modules")
except ImportError as e:
    logger.error(f"Error importing {COMPONENT_NAME} modules: {e}")
    logger.error(f"Make sure {COMPONENT_NAME} is properly installed and accessible")
    sys.exit(1)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=f"Register {COMPONENT_NAME} with Hermes Service Registry"
    )
    parser.add_argument(
        "--hermes-url",
        help="URL of the Hermes API",
        default=TektonEnviron.get("HERMES_URL", "http://localhost:8000/api")
    )
    parser.add_argument(
        "--instructions-file",
        help="Path to startup instructions JSON file",
        default=TektonEnviron.get("STARTUP_INSTRUCTIONS_FILE")
    )
    parser.add_argument(
        "--endpoint",
        help=f"API endpoint for {COMPONENT_NAME}",
        default=TektonEnviron.get("{COMPONENT_UPPER}_API_ENDPOINT")
    )
    
    return parser.parse_args()

async def register_{COMPONENT_LOWER}_with_hermes(
    hermes_url: Optional[str] = None,
    instructions_file: Optional[str] = None,
    endpoint: Optional[str] = None
) -> bool:
    """
    Register {COMPONENT_NAME} with Hermes service registry.
    
    Args:
        hermes_url: URL of the Hermes API
        instructions_file: Path to JSON file with startup instructions
        endpoint: API endpoint for {COMPONENT_NAME}
        
    Returns:
        True if registration was successful
    """
    # Check for startup instructions file
    if instructions_file and os.path.isfile(instructions_file):
        logger.info(f"Loading startup instructions from {instructions_file}")
        instructions = load_startup_instructions(instructions_file)
        # Extract relevant information from instructions
        # This will vary based on your component's needs
    else:
        instructions = {}
    
    # Define component information
    component_id = instructions.get("component_id", "{COMPONENT_ID}")
    component_name = instructions.get("name", "{COMPONENT_NAME}")
    component_type = instructions.get("type", "{COMPONENT_TYPE}")
    component_version = instructions.get("version", "0.1.0")
    
    # Define capabilities specific to {COMPONENT_NAME}
    # Customize this section based on your component's capabilities
    capabilities = {CAPABILITIES}
    
    # Define dependencies
    dependencies = instructions.get("dependencies", {DEPENDENCIES})
    
    # Define additional metadata
    metadata = {
        "description": "{COMPONENT_DESCRIPTION}",
        # Add any additional metadata specific to your component
    }
    if instructions.get("metadata"):
        metadata.update(instructions["metadata"])
    
    # If endpoint is not provided, use a default or from instructions
    if not endpoint:
        endpoint = instructions.get("endpoint", "{DEFAULT_ENDPOINT}")
    
    try:
        # Use standardized registration utility if available
        if REGISTRATION_UTILS_AVAILABLE:
            client = await register_component(
                component_id=component_id,
                component_name=component_name,
                component_type=component_type,
                component_version=component_version,
                capabilities=capabilities,
                hermes_url=hermes_url,
                dependencies=dependencies,
                endpoint=endpoint,
                additional_metadata=metadata
            )
            
            if client:
                logger.info(f"Successfully registered {component_name} with Hermes")
                
                # Set up signal handlers
                loop = asyncio.get_event_loop()
                client.setup_signal_handlers(loop)
                
                # Keep the registration active until interrupted
                stop_event = asyncio.Event()
                
                def handle_signal(sig):
                    logger.info(f"Received signal {sig.name}, shutting down")
                    asyncio.create_task(client.close())
                    stop_event.set()
                
                for sig in (signal.SIGINT, signal.SIGTERM):
                    loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
                
                logger.info("Registration active. Press Ctrl+C to unregister and exit...")
                try:
                    await stop_event.wait()
                except Exception as e:
                    logger.error(f"Error during registration: {e}")
                    await client.close()
                
                return True
            else:
                logger.error(f"Failed to register {component_name} with Hermes")
                return False
        else:
            # Fall back to direct Hermes registration
            success = await register_component(
                component_id=component_id,
                component_name=component_name,
                hermes_url=hermes_url,
                capabilities=[cap["name"] for cap in capabilities],
                description=metadata["description"],
                version=component_version
            )
            
            if success:
                logger.info(f"Successfully registered {component_name} with Hermes")
                
                # Keep the registration active until interrupted
                try:
                    logger.info("Registration active. Press Ctrl+C to unregister and exit...")
                    # Run indefinitely until interrupted
                    while True:
                        await asyncio.sleep(60)
                        logger.info(f"{component_name} registration still active...")
                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt received, unregistering...")
                finally:
                    # Unregister from Hermes before exiting
                    await unregister_component(component_id, hermes_url)
                    logger.info(f"{component_name} unregistered from Hermes")
                
                return True
            else:
                logger.error(f"Failed to register {component_name} with Hermes")
                return False
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return False

async def main():
    """Main entry point."""
    args = parse_arguments()
    
    logger.info(f"Registering {COMPONENT_NAME} with Hermes service registry...")
    
    success = await register_{COMPONENT_LOWER}_with_hermes(
        hermes_url=args.hermes_url,
        instructions_file=args.instructions_file,
        endpoint=args.endpoint
    )
    
    if success:
        logger.info(f"{COMPONENT_NAME} registration process complete")
    else:
        logger.error(f"Failed to register {COMPONENT_NAME} with Hermes")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())