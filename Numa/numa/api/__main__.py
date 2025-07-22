"""Main entry point for running Numa API server."""
import uvicorn
from shared.utils.env_config import get_component_config
from shared.env import TektonEnviron
from numa.api.app import app

if __name__ == "__main__":
    config = get_component_config()
    port = config.numa.port if hasattr(config, 'numa') else int(TektonEnviron.get("NUMA_PORT", "8011"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )