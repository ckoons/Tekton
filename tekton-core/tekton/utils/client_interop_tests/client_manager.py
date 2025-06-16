#!/usr/bin/env python3
"""
Client Manager Module

Manages component clients for interop tests.
"""

import os
import sys
import importlib
import logging
from typing import Dict, Any, Optional, List

# Configure logging
logger = logging.getLogger("tekton.utils.client_interop_tests")


class ClientManager:
    """
    Manages component clients for interop tests.
    """
    
    def __init__(self, hermes_url: str):
        """
        Initialize client manager.
        
        Args:
            hermes_url: URL of the Hermes service
        """
        self.hermes_url = hermes_url
        self.clients = {}
        self.client_modules = {}
        
    def init_clients(self) -> Dict[str, Any]:
        """
        Initialize component clients.
        
        Returns:
            Dictionary of component clients
        """
        # Try to import client modules
        for component in ["hermes", "athena", "ergon", "engram", "rhetor", "telos", "sophia", "synthia"]:
            try:
                # Try from Tekton installed package
                module_name = f"tekton.clients.{component}_client"
                module = importlib.import_module(module_name)
                self.client_modules[component] = module
                logger.info(f"Imported {component} client from Tekton package")
            except ImportError:
                # Try relative to current path (development mode)
                try:
                    relative_path = os.path.join(os.path.dirname(__file__), f"../../../clients/{component}_client.py")
                    if os.path.exists(relative_path):
                        sys.path.insert(0, os.path.dirname(relative_path))
                        module = importlib.import_module(f"{component}_client")
                        self.client_modules[component] = module
                        logger.info(f"Imported {component} client from development path")
                    else:
                        logger.warning(f"Could not find {component} client module")
                except ImportError as e:
                    logger.warning(f"Could not import {component} client: {e}")
                    
        # Initialize clients
        for component, module in self.client_modules.items():
            try:
                client_class = getattr(module, f"{component.capitalize()}Client")
                self.clients[component] = client_class(hermes_url=self.hermes_url)
                logger.info(f"Initialized {component} client")
            except (AttributeError, Exception) as e:
                logger.warning(f"Could not initialize {component} client: {e}")
                
        return self.clients
        
    def cleanup_clients(self) -> None:
        """Clean up component clients."""
        for component, client in self.clients.items():
            try:
                if hasattr(client, "close"):
                    client.close()
                elif hasattr(client, "cleanup"):
                    client.cleanup()
                logger.info(f"Cleaned up {component} client")
            except Exception as e:
                logger.warning(f"Error cleaning up {component} client: {e}")
                
        self.clients = {}
