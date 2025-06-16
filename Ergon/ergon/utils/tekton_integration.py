"""
Tekton integration utilities for Ergon.

This module provides utilities for integrating Ergon with the Tekton ecosystem,
including the Single Port Architecture and shared component utilities.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List, Tuple, Union

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config

logger = logging.getLogger(__name__)

def get_component_port(component_name: str) -> int:
    """
    Get the port for a Tekton component.
    
    Args:
        component_name: Name of the component (lowercase)
        
    Returns:
        Component port
    """
    config = get_component_config()
    component_name_lower = component_name.lower()
    
    # Try to get port from config first
    if hasattr(config, component_name_lower):
        component_config = getattr(config, component_name_lower)
        if hasattr(component_config, 'port'):
            return component_config.port
    
    # Fallback to environment variables
    component_map = {
        "hephaestus": "HEPHAESTUS_PORT",
        "engram": "ENGRAM_PORT",
        "hermes": "HERMES_PORT",
        "ergon": "ERGON_PORT",
        "rhetor": "RHETOR_PORT",
        "terma": "TERMA_PORT",
        "athena": "ATHENA_PORT",
        "prometheus": "PROMETHEUS_PORT",
        "harmonia": "HARMONIA_PORT",
        "telos": "TELOS_PORT",
        "synthesis": "SYNTHESIS_PORT",
        "tekton_core": "TEKTON_CORE_PORT",
        "metis": "METIS_PORT",
        "apollo": "APOLLO_PORT",
        "budget": "BUDGET_PORT",
        "sophia": "SOPHIA_PORT",
    }
    
    env_var = component_map.get(component_name_lower)
    
    if not env_var:
        logger.warning(f"Unknown component: {component_name}.")
        raise ValueError(f"Unknown component: {component_name}")
    
    port_str = os.environ.get(env_var)
    if not port_str:
        raise ValueError(f"{env_var} not found in environment")
    
    return int(port_str)

def get_component_url(
    component_name: str,
    path: str = "",
    protocol: str = "http",
    host: Optional[str] = None
) -> str:
    """
    Get the URL for a Tekton component.
    
    Args:
        component_name: Name of the component (lowercase)
        path: URL path (should start with /)
        protocol: URL protocol (http or ws)
        host: Host name (defaults to localhost)
        
    Returns:
        Component URL
    """
    port = get_component_port(component_name)
    host = host or os.environ.get("TEKTON_HOST", "localhost")
    
    # Ensure path starts with /
    if path and not path.startswith("/"):
        path = f"/{path}"
    
    return f"{protocol}://{host}:{port}{path}"

def get_component_api_url(
    component_name: str,
    endpoint: str = "",
    host: Optional[str] = None
) -> str:
    """
    Get the API URL for a Tekton component.
    
    Args:
        component_name: Name of the component (lowercase)
        endpoint: API endpoint (without /api prefix)
        host: Host name (defaults to localhost)
        
    Returns:
        Component API URL
    """
    # Ensure endpoint doesn't start with /
    if endpoint and endpoint.startswith("/"):
        endpoint = endpoint[1:]
    
    path = f"/api/{endpoint}" if endpoint else "/api"
    return get_component_url(component_name, path, "http", host)

def get_component_websocket_url(
    component_name: str,
    path: str = "ws",
    host: Optional[str] = None
) -> str:
    """
    Get the WebSocket URL for a Tekton component.
    
    Args:
        component_name: Name of the component (lowercase)
        path: WebSocket path (defaults to "ws")
        host: Host name (defaults to localhost)
        
    Returns:
        Component WebSocket URL
    """
    # Ensure path doesn't start with /
    if path and path.startswith("/"):
        path = path[1:]
    
    return get_component_url(component_name, f"/{path}", "ws", host)

def get_component_health_url(
    component_name: str,
    host: Optional[str] = None
) -> str:
    """
    Get the health check URL for a Tekton component.
    
    Args:
        component_name: Name of the component (lowercase)
        host: Host name (defaults to localhost)
        
    Returns:
        Component health check URL
    """
    return get_component_url(component_name, "/health", "http", host)

def get_environment_config() -> Dict[str, Any]:
    """
    Get the Tekton environment configuration.
    
    Returns:
        Dictionary of component configurations
    """
    components = [
        "hephaestus", "engram", "hermes", "ergon", "rhetor", 
        "terma", "athena", "prometheus", "harmonia", "telos", 
        "synthesis", "tekton_core"
    ]
    
    config = {
        "host": os.environ.get("TEKTON_HOST", "localhost"),
        "components": {}
    }
    
    for component in components:
        port = get_component_port(component)
        config["components"][component] = {
            "port": port,
            "urls": {
                "api": get_component_api_url(component),
                "ws": get_component_websocket_url(component),
                "health": get_component_health_url(component)
            }
        }
    
    return config

def configure_for_single_port() -> Dict[str, Any]:
    """
    Configure the current application for Single Port Architecture.
    
    Returns:
        Configuration dictionary with URLs and ports
    """
    # Get the Ergon port from environment
    ergon_port = get_component_port("ergon")
    
    # Build configuration dictionary
    config = {
        "port": ergon_port,
        "host": os.environ.get("TEKTON_HOST", "localhost"),
        "api_path": "/api",
        "ws_path": "/ws",
        "health_path": "/health",
        "events_path": "/events",
        "metrics_path": "/metrics"
    }
    
    # Log the configuration
    logger.info(f"Configured Ergon for Single Port Architecture on port {ergon_port}")
    
    return config