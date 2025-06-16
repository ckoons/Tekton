#!/usr/bin/env python3
"""
Hephaestus - Main Application Launcher

This module provides the main entry point for the Hephaestus UI server,
managing both the HTTP/WebSocket server and the MCP DevTools server.
"""

import os
import sys
import asyncio
import argparse
import logging

# Add Tekton root to path for shared imports
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from shared.utils.logging_setup import setup_component_logging
from shared.utils.global_config import GlobalConfig
from hephaestus.core.hephaestus_component import HephaestusComponent

# Use shared logging setup
logger = setup_component_logging("hephaestus")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Hephaestus UI Server")
    
    # Get port from GlobalConfig
    global_config = GlobalConfig.get_instance()
    default_http_port = global_config.config.hephaestus.port
    default_mcp_port = global_config.config.hephaestus.mcp_port
    
    parser.add_argument("--http-port", type=int, default=default_http_port,
                        help="Port to run the HTTP/WebSocket server on")
    parser.add_argument("--mcp-port", type=int, default=default_mcp_port,
                        help="Port to run the MCP DevTools server on")
    parser.add_argument("--no-mcp", action="store_true",
                        help="Disable MCP DevTools server")
    parser.add_argument("--ui-dir", default=None,
                        help="Directory containing UI files to serve")
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()
    
    # Create and initialize component
    component = HephaestusComponent()
    
    try:
        # Initialize component (includes Hermes registration)
        await component.initialize(
            capabilities=component.get_capabilities(),
            metadata=component.get_metadata()
        )
        
        logger.info(f"Hephaestus UI server running on port {args.http_port}")
        if not args.no_mcp:
            logger.info(f"MCP DevTools server running on port {args.mcp_port}")
        logger.info("Press Ctrl+C to stop")
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutdown requested...")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    finally:
        # Cleanup
        await component.shutdown()
        logger.info("Hephaestus server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Hephaestus server stopped by user")
    except Exception as e:
        logger.error(f"Hephaestus server terminated due to error: {e}", exc_info=True)
        sys.exit(1)