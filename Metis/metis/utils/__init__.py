# Utility functions for Metis

import os
import sys

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from shared.env import TektonEnviron
from shared.urls import tekton_url

# from tekton.utils.port_config import (
#     get_component_port as get_port,
#     get_component_url as get_service_url
# )

# Compatibility functions updated to use TektonEnviron and tekton_url
def get_port(component_name: str) -> int:
    """Get component port from environment variables"""
    env_var_map = {
        'metis': 'METIS_PORT',
        'telos': 'TELOS_PORT', 
        'hermes': 'HERMES_PORT'
    }
    env_var = env_var_map.get(component_name)
    if env_var:
        port_str = TektonEnviron.get(env_var)
        if port_str:
            return int(port_str)
    raise ValueError(f"Port not configured for component: {component_name}. Set {env_var} environment variable.")

def get_service_url(component_name: str) -> str:
    """Get service URL using tekton_url"""
    return tekton_url(component_name)
from metis.utils.hermes_helper import HermesClient, hermes_client

__all__ = [
    # Port configuration
    'get_port',
    'get_service_url',
    
    # Hermes integration
    'HermesClient',
    'hermes_client',
]