"""Main entry point for running Telos API server."""
import uvicorn
import os
import sys

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import GlobalConfig
from telos.api.app import app

if __name__ == "__main__":
    config = GlobalConfig()
    port = config.get_port('telos')
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )