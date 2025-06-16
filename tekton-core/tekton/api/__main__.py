#!/usr/bin/env python3
"""
Main entry point for Tekton Core API server.
"""

import os
import sys

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from shared.utils.socket_server import run_component_server
from shared.utils.global_config import GlobalConfig

if __name__ == "__main__":
    # Get port from GlobalConfig
    global_config = GlobalConfig.get_instance()
    default_port = global_config.config.tekton_core.port
    
    run_component_server(
        component_name="tekton_core",
        app_module="tekton.api.app",
        default_port=default_port,
        reload=False
    )