"""
Configuration module for Metis

This module manages the configuration for Metis, including
environment variables, default settings, and component integration.
"""

import os
import sys
from typing import Dict, Any

# Add Tekton root to path for imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from tekton.utils.port_config import get_metis_port, get_hermes_port, get_telos_port, get_prometheus_port

# Default configuration
DEFAULT_CONFIG = {
    # Service configuration
    "SERVICE_NAME": "Metis",
    "SERVICE_DESCRIPTION": "Task Management System for Tekton",
    "SERVICE_VERSION": "0.1.0",
    
    # Port configuration (dynamically loaded)
    "METIS_PORT": None,
    "HERMES_PORT": None,
    "TELOS_PORT": None,
    "PROMETHEUS_PORT": None,
    
    # Database configuration
    "DB_URL": lambda: f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metis.db'))}",
    
    # API configuration
    "API_PREFIX": "/api/v1",
    "WEBSOCKET_PATH": "/ws",
    "EVENTS_PATH": "/events",
    
    # Component URLs (constructed at runtime)
    "HERMES_URL": None,
    "TELOS_URL": None,
    "PROMETHEUS_URL": None,
}

def get_config() -> Dict[str, Any]:
    """
    Get the configuration for Metis.
    
    Returns:
        Dict[str, Any]: Configuration dictionary with all settings
    """
    config = DEFAULT_CONFIG.copy()
    
    # Get ports from centralized config
    config["METIS_PORT"] = get_metis_port()
    config["HERMES_PORT"] = get_hermes_port()
    config["TELOS_PORT"] = get_telos_port()
    config["PROMETHEUS_PORT"] = get_prometheus_port()
    
    # Override with environment variables (except ports which are centrally managed)
    for key in config.keys():
        if key in os.environ and not key.endswith("_PORT"):
            # Convert to appropriate type
            if isinstance(config[key], int):
                config[key] = int(os.environ[key])
            elif isinstance(config[key], bool):
                config[key] = os.environ[key].lower() in ("true", "1", "yes")
            else:
                config[key] = os.environ[key]
    
    # Construct component URLs
    config["HERMES_URL"] = f"http://localhost:{config['HERMES_PORT']}"
    config["TELOS_URL"] = f"http://localhost:{config['TELOS_PORT']}"
    config["PROMETHEUS_URL"] = f"http://localhost:{config['PROMETHEUS_PORT']}"
    
    return config

# Global config instance for import
config = get_config()