"""
Centralized port configuration for all Tekton components.

This module provides a single source of truth for port assignments across
the Tekton ecosystem, reading from the official config/port_assignments.md file.
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional

# Cache for port assignments to avoid repeated file reads
_port_cache: Optional[Dict[str, int]] = None


def load_port_assignments() -> Dict[str, int]:
    """
    Load port assignments from the official config/port_assignments.md file.
    
    Returns:
        Dictionary mapping component names to port numbers
    """
    global _port_cache
    
    if _port_cache is not None:
        return _port_cache
    
    # Find the config file relative to this module
    config_path = Path(__file__).parent.parent.parent / "config" / "port_assignments.md"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Port assignments file not found at {config_path}")
    
    port_assignments = {}
    
    # Parse the markdown table
    with open(config_path, 'r') as f:
        lines = f.readlines()
        
    in_main_table = False
    in_specialized_table = False
    
    for line in lines:
        line = line.strip()
        
        # Check for table headers
        if "| Component" in line and "| Port |" in line:
            in_main_table = True
            in_specialized_table = False
            continue
        elif "| Service" in line and "| Port |" in line:
            in_specialized_table = True
            in_main_table = False
            continue
        elif line.startswith("|---"):
            continue
        elif not line.startswith("|"):
            in_main_table = False
            in_specialized_table = False
            continue
            
        # Parse table rows
        if (in_main_table or in_specialized_table) and line.startswith("|"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:  # Including empty strings from split
                component = parts[1].strip()
                port_str = parts[2].strip()
                
                # Extract port number
                try:
                    port = int(port_str)
                    # Normalize component names
                    component_key = component.lower().replace(" ", "_").replace("-", "_")
                    
                    # Special handling for some components
                    if component == "Hephaestus UI":
                        component_key = "hephaestus"
                    elif component == "Tekton Core":
                        component_key = "tekton_core"
                        
                    port_assignments[component_key] = port
                except ValueError:
                    continue
    
    _port_cache = port_assignments
    return port_assignments


def get_component_port(component_name: Optional[str] = None) -> int:
    """
    Get the port number for a specific component.
    
    Args:
        component_name: Name of the component. If None, attempts to detect
                       from the current module's path.
    
    Returns:
        Port number for the component
    """
    if component_name is None:
        # Try to detect component from current module path
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            module_path = frame.f_back.f_globals.get('__file__', '')
            # Extract component name from path
            path_parts = Path(module_path).parts
            for part in path_parts:
                part_lower = part.lower()
                if part_lower in load_port_assignments():
                    component_name = part_lower
                    break
    
    if component_name is None:
        raise ValueError("Unable to determine component name")
    
    component_name = component_name.lower().replace("-", "_")
    
    # Single source of truth: TektonEnviron
    from shared.env import TektonEnviron
    env_var = f"{component_name.upper()}_PORT"
    port = TektonEnviron.get(env_var)
    
    if port:
        try:
            return int(port)
        except ValueError:
            raise ValueError(f"Invalid port value for {component_name}: {port}")
    
    raise ValueError(f"Port not found for component: {component_name}")


def get_component_url(component_name: str, host: str = "localhost", 
                     protocol: str = "http") -> str:
    """
    Get the base URL for a component.
    
    Args:
        component_name: Name of the component
        host: Hostname (default: localhost)
        protocol: Protocol to use (http, https, ws, wss)
    
    Returns:
        Base URL for the component
    """
    port = get_component_port(component_name)
    return f"{protocol}://{host}:{port}"


# Legacy compatibility functions
# These maintain backward compatibility with existing code
def get_rhetor_port() -> int:
    """Get Rhetor service port."""
    return get_component_port("rhetor")


def get_hermes_port() -> int:
    """Get Hermes service port."""
    return get_component_port("hermes")


def get_engram_port() -> int:
    """Get Engram service port."""
    return get_component_port("engram")


def get_athena_port() -> int:
    """Get Athena service port."""
    return get_component_port("athena")


def get_apollo_port() -> int:
    """Get Apollo service port."""
    return get_component_port("apollo")


def get_budget_port() -> int:
    """Get Budget service port."""
    return get_component_port("budget")


def get_ergon_port() -> int:
    """Get Ergon service port."""
    return get_component_port("ergon")


def get_harmonia_port() -> int:
    """Get Harmonia service port."""
    return get_component_port("harmonia")


def get_hephaestus_port() -> int:
    """Get Hephaestus UI port."""
    return get_component_port("hephaestus")


def get_metis_port() -> int:
    """Get Metis service port."""
    return get_component_port("metis")


def get_prometheus_port() -> int:
    """Get Prometheus service port."""
    return get_component_port("prometheus")


def get_sophia_port() -> int:
    """Get Sophia service port."""
    return get_component_port("sophia")


def get_synthesis_port() -> int:
    """Get Synthesis service port."""
    return get_component_port("synthesis")


def get_tekton_core_port() -> int:
    """Get Tekton Core service port."""
    return get_component_port("tekton_core")


def get_telos_port() -> int:
    """Get Telos service port."""
    return get_component_port("telos")


def get_terma_port() -> int:
    """Get Terma service port."""
    return get_component_port("terma")


# Utility functions for URL construction
def get_rhetor_url(host: str = "localhost", protocol: str = "http") -> str:
    """Get Rhetor base URL."""
    return get_component_url("rhetor", host, protocol)


def get_hermes_url(host: str = "localhost", protocol: str = "http") -> str:
    """Get Hermes base URL."""
    return get_component_url("hermes", host, protocol)


def get_engram_url(host: str = "localhost", protocol: str = "http") -> str:
    """Get Engram base URL."""
    return get_component_url("engram", host, protocol)


def get_athena_url(host: str = "localhost", protocol: str = "http") -> str:
    """Get Athena base URL."""
    return get_component_url("athena", host, protocol)


def get_prometheus_url(host: str = "localhost", protocol: str = "http") -> str:
    """Get Prometheus base URL."""
    return get_component_url("prometheus", host, protocol)




# Export all public functions
__all__ = [
    'load_port_assignments',
    'get_component_port',
    'get_component_url',
    # Legacy compatibility functions
    'get_rhetor_port',
    'get_hermes_port',
    'get_engram_port',
    'get_athena_port',
    'get_apollo_port',
    'get_budget_port',
    'get_ergon_port',
    'get_harmonia_port',
    'get_hephaestus_port',
    'get_metis_port',
    'get_prometheus_port',
    'get_sophia_port',
    'get_synthesis_port',
    'get_tekton_core_port',
    'get_telos_port',
    'get_terma_port',
    # URL helper functions
    'get_rhetor_url',
    'get_hermes_url',
    'get_engram_url',
    'get_athena_url',
    'get_prometheus_url',
]