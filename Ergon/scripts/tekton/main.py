#!/usr/bin/env python3
"""
Tekton Suite Launcher - Main Entry Point

This module serves as the main entry point for the Tekton suite launcher,
setting up signal handlers and dispatching commands.
"""

import sys
import signal
import asyncio
import logging

from .cli import parse_arguments, process_command
from .shutdown import stop_all_components

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tekton")

def setup_signal_handlers():
    """Set up signal handlers to gracefully shut down components."""
    def signal_handler(sig, frame):
        print("\nReceived interrupt signal, shutting down Tekton components...")
        asyncio.run(stop_all_components())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main entry point for the Tekton suite launcher."""
    # Set up signal handlers
    setup_signal_handlers()
    
    # Parse command-line arguments
    args = parse_arguments()
    
    # Process the command
    success = process_command(args)
    
    # Return status code
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()