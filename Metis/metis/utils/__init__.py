# Utility functions for Metis

# from tekton.utils.port_config import (
#     get_component_port as get_port,
#     get_component_url as get_service_url
# )

# Placeholder functions for compatibility
def get_port(component_name: str) -> int:
    """Get component port from environment variables"""
    import os
    env_var_map = {
        'metis': 'METIS_PORT',
        'telos': 'TELOS_PORT', 
        'hermes': 'HERMES_PORT'
    }
    env_var = env_var_map.get(component_name)
    if env_var and os.environ.get(env_var):
        return int(os.environ.get(env_var))
    raise ValueError(f"Port not configured for component: {component_name}. Set {env_var} environment variable.")

def get_service_url(component_name: str) -> str:
    """Get service URL - placeholder"""
    port = get_port(component_name)
    return f"http://localhost:{port}"
from metis.utils.hermes_helper import HermesClient, hermes_client

__all__ = [
    # Port configuration
    'get_port',
    'get_service_url',
    
    # Hermes integration
    'HermesClient',
    'hermes_client',
]