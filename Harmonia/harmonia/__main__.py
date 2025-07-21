#!/usr/bin/env python3
"""
Harmonia Workflow Orchestration Engine - Main Application Launcher

This module provides the main entry point for the Harmonia workflow orchestration
engine, starting the API server and initializing all required components.
"""

import os
import sys
import asyncio
import argparse

# Add Tekton root to path for shared imports
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from harmonia.core.startup_instructions import StartUpInstructions
from harmonia.core.workflow_startup import WorkflowEngineStartup

# Use shared logging setup
from shared.utils.logging_setup import setup_component_logging
from shared.utils.global_config import GlobalConfig
from shared.env import TektonEnviron
logger = setup_component_logging("harmonia")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Harmonia Workflow Orchestration Engine")
    
    # Get port from GlobalConfig
    global_config = GlobalConfig.get_instance()
    default_port = global_config.config.harmonia.port
    parser.add_argument("--port", type=int, default=default_port,
                        help="Port to run the API server on")
    parser.add_argument("--host", default=TektonEnviron.get("HARMONIA_HOST", "0.0.0.0"),
                        help="Host to bind the API server to")
    parser.add_argument("--data-dir", default=TektonEnviron.get("HARMONIA_DATA_DIR", os.path.expanduser("~/.harmonia")),
                        help="Directory for storing Harmonia data")
    hermes_port = global_config.config.hermes.port if hasattr(global_config.config, "hermes") else 8001
    hermes_host = TektonEnviron.get("HERMES_HOST", "localhost")
    default_hermes_url = f"http://{hermes_host}:{hermes_port}"
    parser.add_argument("--hermes-url", default=TektonEnviron.get("HERMES_URL", default_hermes_url),
                        help="URL of the Hermes service")
    parser.add_argument("--log-level", default=TektonEnviron.get("LOG_LEVEL", "INFO"),
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level")
    parser.add_argument("--init-only", action="store_true",
                        help="Initialize components and exit (don't start API server)")
    parser.add_argument("--auto-register", action="store_true",
                        help="Automatically register with Hermes on startup")
    parser.add_argument("--instructions-file", default=TektonEnviron.get("STARTUP_INSTRUCTIONS_FILE"),
                        help="Path to startup instructions JSON file")
    
    return parser.parse_args()


async def initialize_engine(args):
    """
    Initialize the workflow engine.
    
    Args:
        args: Command line arguments
        
    Returns:
        Initialized WorkflowEngine instance
    """
    try:
        # Load startup instructions from file if provided
        if args.instructions_file and os.path.isfile(args.instructions_file):
            logger.info(f"Loading startup instructions from {args.instructions_file}")
            instructions = StartUpInstructions.from_file(args.instructions_file)
        else:
            # Create startup instructions from arguments
            instructions = StartUpInstructions(
                data_directory=args.data_dir,
                hermes_url=args.hermes_url,
                log_level=args.log_level,
                auto_register=args.auto_register,
                initialize_db=True,
                load_previous_state=True
            )
        
        # Initialize workflow engine
        startup = WorkflowEngineStartup(instructions)
        engine = await startup.initialize()
        
        logger.info("Workflow engine initialized successfully")
        return engine
    
    except Exception as e:
        logger.error(f"Error initializing workflow engine: {e}", exc_info=True)
        raise


def run_api_server(args):
    """
    Run the API server.
    
    Args:
        args: Command line arguments
    """
    try:
        # Initialize workflow engine (happens in the app's startup event)
        # Note: TektonEnviron is read-only, so we don't set environment variables here
        # The app will use the args passed through the command line or defaults from TektonEnviron
        
        # Run the API server with socket reuse
        from shared.utils.socket_server import run_with_socket_reuse
        
        logger.info(f"Starting Harmonia API server on {args.host}:{args.port}")
        run_with_socket_reuse(
            "harmonia.api.app:app",
            host=args.host,
            port=args.port,
            log_level=args.log_level.lower(),
            timeout_graceful_shutdown=3,
            server_header=False,
            access_log=False
        )
    
    except Exception as e:
        logger.error(f"Error running API server: {e}", exc_info=True)
        raise


def main():
    """Main entry point."""
    # Parse command line arguments
    args = parse_args()
    
    # Logging is already configured at module level via setup_component_logging
    
    if args.init_only:
        # Initialize workflow engine and exit
        asyncio.run(initialize_engine(args))
        logger.info("Initialization complete. Exiting.")
    else:
        # Run the API server
        run_api_server(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Harmonia server stopped by user")
    except Exception as e:
        logger.error(f"Harmonia server terminated due to error: {e}", exc_info=True)
        sys.exit(1)