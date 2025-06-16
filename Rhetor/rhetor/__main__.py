"""Entry point for python -m rhetor"""
import os
import sys

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Initialize Tekton environment before other imports
try:
    from shared.utils.tekton_startup import tekton_component_startup
    # Load environment variables from Tekton's three-tier system
    tekton_component_startup("rhetor")
except ImportError as e:
    print(f"[RHETOR] Could not load Tekton environment manager: {e}")
    print(f"[RHETOR] Continuing with system environment variables")

from shared.utils.socket_server import run_component_server
from shared.utils.global_config import GlobalConfig

if __name__ == "__main__":
    # Get port from GlobalConfig
    global_config = GlobalConfig.get_instance()
    default_port = global_config.config.rhetor.port
    
    run_component_server(
        component_name="rhetor",
        app_module="rhetor.api.app",
        default_port=default_port,
        reload=False
    )