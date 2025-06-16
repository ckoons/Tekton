"""Main entry point for running Budget API server."""
import uvicorn
import os
import sys

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config
from budget.api.app import app

if __name__ == "__main__":
    config = get_component_config()
    port = config.budget.port if hasattr(config, 'budget') else int(os.environ.get("BUDGET_PORT"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )