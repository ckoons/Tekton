"""Entry point for python -m hermes"""
import os
import sys

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from shared.utils.global_config import GlobalConfig

if __name__ == "__main__":
    # Get port from GlobalConfig
    global_config = GlobalConfig.get_instance()
    default_port = global_config.config.hermes.port
    
    # Use direct uvicorn.run() to ensure startup events work
    import uvicorn
    from hermes.api.app import app
    
    print(f"Starting Hermes on port {default_port}...")
    uvicorn.run(app, host="0.0.0.0", port=default_port)