"""
Helper module for registering with Hermes service registry.
"""

import os
import sys
import logging
import json
import asyncio
from pathlib import Path
import aiohttp

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config

logger = logging.getLogger(__name__)

HERMES_API_URL = os.environ.get("HERMES_API_URL", "http://localhost:8100")
config = get_component_config()
RHETOR_PORT = config.rhetor.port if hasattr(config, 'rhetor') else int(os.environ.get("RHETOR_PORT"))

# Check if this is running in the Tekton environment
TEKTON_ROOT = Path(__file__).parent.parent.parent.parent
IS_TEKTON_ENV = TEKTON_ROOT.name == "Tekton" and (TEKTON_ROOT / "Hermes").exists()

async def register_with_hermes():
    """
    Register Rhetor with the Hermes service registry.
    
    Returns:
        True if registration successful, False otherwise
    """
    try:
        # Read version from package or default to 0.1.0
        try:
            from .. import __version__
            version = __version__
        except (ImportError, AttributeError):
            version = "0.1.0"
        
        # Create registration data
        registration_data = {
            "id": "rhetor",
            "name": "Rhetor",
            "description": "LLM Management System for Tekton",
            "version": version,
            "url": f"http://localhost:{RHETOR_PORT}",
            "capabilities": [
                "llm_management",
                "prompt_engineering",
                "context_management",
                "model_selection"
            ],
            "endpoints": {
                "http": f"http://localhost:{RHETOR_PORT}",
                "ws": f"ws://localhost:{RHETOR_PORT}/ws"
            },
            "dependencies": ["engram"],
            "lifecycle": {
                "startup_script": "tekton-launch --components rhetor",
                "shutdown_script": "tekton-kill",
                "status_check": {
                    "url": f"http://localhost:{RHETOR_PORT}/health",
                    "success_code": 200
                }
            },
            "metadata": {
                "icon": "🗣️",
                "ui_color": "#7e57c2",
                "priority": 40,
                "managed_port": RHETOR_PORT,
                "core_component": True,
                "replaces": "llm_adapter"
            }
        }
        
        # Try to register with Hermes
        registration_url = f"{HERMES_API_URL}/api/register"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                registration_url,
                json=registration_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Successfully registered Rhetor with Hermes: {result}")
                    
                    # Also save registration to the Hermes registrations directory if in Tekton environment
                    if IS_TEKTON_ENV:
                        registrations_dir = TEKTON_ROOT / "Hermes" / "registrations"
                        if registrations_dir.exists():
                            with open(registrations_dir / "rhetor.json", "w") as f:
                                json.dump(registration_data, f, indent=2)
                            logger.info(f"Saved registration to {registrations_dir / 'rhetor.json'}")
                    
                    return True
                elif response.status == 404:
                    logger.warning("Hermes service registry not found. Is Hermes running?")
                    return False
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to register with Hermes: {response.status} - {error_text}")
                    return False
    except aiohttp.ClientConnectorError:
        logger.warning("Could not connect to Hermes service registry. Is Hermes running?")
        return False
    except Exception as e:
        logger.error(f"Error registering with Hermes: {e}")
        return False

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the registration
    asyncio.run(register_with_hermes())
EOL < /dev/null