#!/usr/bin/env python3
"""
Main entry point for Tekton Core API server.
"""

import os
import sys

# Add Tekton root to path if not already present using TektonEnviron
from shared.env import TektonEnviron
tekton_root = TektonEnviron.get('TEKTON_ROOT')
if tekton_root and tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)
elif not tekton_root:
    # Fallback for development
    tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if tekton_root not in sys.path:
        sys.path.insert(0, tekton_root)

from shared.utils.global_config import GlobalConfig

if __name__ == "__main__":
    # Get port from GlobalConfig
    global_config = GlobalConfig.get_instance()
    default_port = global_config.config.tekton_core.port
    
    # Use direct uvicorn.run() to ensure startup events work
    import uvicorn
    from tekton.api.app import app
    
    print(f"Starting Tekton Core on port {default_port}...")
    uvicorn.run(app, host="0.0.0.0", port=default_port)