#!/usr/bin/env python3
"""
Run Registration Server - Entry point script for the Hermes Registration API server.

This script provides a command-line interface for starting the Hermes API server,
which implements the Unified Registration Protocol.
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the registration server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Hermes Registration API Server")
    parser.add_argument(
        "--host", 
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.environ.get("PORT", "8000")),
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        default=os.environ.get("DEBUG", "False").lower() == "true",
        help="Enable debug mode with auto-reload"
    )
    parser.add_argument(
        "--secret-key",
        default=os.environ.get("HERMES_SECRET_KEY", "tekton-secret-key"),
        help="Secret key for token generation"
    )
    args = parser.parse_args()
    
    # Export configuration as environment variables
    os.environ["HOST"] = args.host
    os.environ["PORT"] = str(args.port)
    os.environ["DEBUG"] = str(args.debug).lower()
    os.environ["HERMES_SECRET_KEY"] = args.secret_key
    
    # Import and run the server
    try:
        from hermes.api import run_server
        logger.info(f"Starting Hermes Registration API server on {args.host}:{args.port}")
        run_server()
    except ImportError as e:
        logger.error(f"Failed to import Hermes API: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting Hermes API server: {e}")
        sys.exit(2)

if __name__ == "__main__":
    # Load environment variables from .env file if present
    load_dotenv()
    
    # Run main function
    main()