#!/usr/bin/env python3
"""
Test Component Registration with Hermes

This script tests the registration of Tekton components with the Hermes service
registry to ensure they're correctly registering, sending heartbeats, and unregistering.

Usage:
    python test_component_registration.py [options]

Options:
    --component: Component to test (all, sophia, prometheus, telos, harmonia, rhetor)
    --hermes-url: URL of the Hermes API
    --timeout: Timeout in seconds for registration test
"""

import os
import sys
import time
import asyncio
import argparse
import logging
import signal
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from shared.env import TektonEnviron
from shared.urls import tekton_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("registration_test")

# Get the directory where this script is located
script_dir = Path(__file__).parent.absolute()
hermes_dir = Path(script_dir).parent.absolute()
tekton_root = hermes_dir.parent.absolute()

# Add to Python path
sys.path.insert(0, str(hermes_dir))
sys.path.insert(0, str(tekton_root))

# Import Hermes modules
try:
    from hermes.core.service_discovery import ServiceRegistry
except ImportError as e:
    logger.error(f"Error importing Hermes modules: {e}")
    logger.error("Make sure Hermes is properly installed and accessible")
    sys.exit(1)

# Component paths
COMPONENT_PATHS = {
    "sophia": os.path.join(str(tekton_root), "Sophia"),
    "prometheus": os.path.join(str(tekton_root), "Prometheus"),
    "telos": os.path.join(str(tekton_root), "Telos"),
    "harmonia": os.path.join(str(tekton_root), "Harmonia"),
    "rhetor": os.path.join(str(tekton_root), "Rhetor"),
    "athena": os.path.join(str(tekton_root), "Athena")
}

# Expected component IDs
COMPONENT_IDS = {
    "sophia": ["sophia.ml"],
    "prometheus": ["prometheus.planning"],
    "telos": ["telos.requirements", "telos.ui"],
    "harmonia": ["harmonia.workflow"],
    "rhetor": ["rhetor-prompt", "rhetor-communication"],
    "athena": ["athena.knowledge"]
}

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test Component Registration with Hermes"
    )
    parser.add_argument(
        "--component",
        help="Component to test (all, sophia, prometheus, telos, harmonia, rhetor, athena)",
        default="all"
    )
    parser.add_argument(
        "--hermes-url",
        help="URL of the Hermes API",
        default=tekton_url("hermes", "/api")
    )
    parser.add_argument(
        "--timeout",
        help="Timeout in seconds for registration test",
        type=int,
        default=60
    )
    
    return parser.parse_args()

async def test_component_registration(component: str, hermes_url: str, timeout: int) -> bool:
    """
    Test registration of a component with Hermes.
    
    Args:
        component: Name of the component to test
        hermes_url: URL of the Hermes API
        timeout: Timeout in seconds
        
    Returns:
        True if registration test passed
    """
    component_path = COMPONENT_PATHS.get(component)
    if not component_path:
        logger.error(f"Unknown component: {component}")
        return False
    
    component_script = os.path.join(component_path, "register_with_hermes.py")
    if not os.path.exists(component_script):
        logger.error(f"Registration script not found: {component_script}")
        return False
    
    # Create a registry client to check for registrations
    registry = ServiceRegistry()
    await registry.start()
    
    logger.info(f"Testing registration for {component}...")
    
    # Start the registration process
    process = None
    try:
        # Start the registration process
        cmd = [sys.executable, component_script, "--hermes-url", hermes_url]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=component_path
        )
        
        logger.info(f"Started registration process for {component}")
        
        # Wait for the component to register
        expected_ids = COMPONENT_IDS.get(component, [])
        registered_ids = []
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check if all expected components are registered
            registered_ids = []
            for component_id in expected_ids:
                service = await registry.get_service(component_id)
                if service:
                    registered_ids.append(component_id)
            
            if set(registered_ids) == set(expected_ids):
                logger.info(f"All expected components for {component} registered!")
                break
            
            # Wait a bit before checking again
            await asyncio.sleep(1)
        
        # Check if all expected components were registered
        if set(registered_ids) != set(expected_ids):
            logger.error(f"Not all expected components for {component} registered!")
            logger.error(f"Expected: {expected_ids}")
            logger.error(f"Registered: {registered_ids}")
            return False
        
        # Wait a bit to let heartbeats flow
        logger.info("Waiting for heartbeats...")
        await asyncio.sleep(5)
        
        # Test heartbeats
        all_healthy = True
        for component_id in expected_ids:
            service = await registry.get_service(component_id)
            if not service or service.get("status") != "healthy":
                logger.error(f"Component {component_id} not healthy!")
                all_healthy = False
        
        if not all_healthy:
            logger.error(f"Not all components for {component} are healthy!")
            return False
        
        logger.info(f"Registration test for {component} passed!")
        return True
    
    except Exception as e:
        logger.error(f"Error testing registration for {component}: {e}")
        return False
    
    finally:
        # Clean up
        if process:
            logger.info(f"Stopping registration process for {component}")
            process.terminate()
            process.wait(timeout=5)
            logger.info(f"Registration process for {component} stopped")
        
        await registry.stop()

async def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Check if Hermes is accessible
    registry = ServiceRegistry()
    try:
        await registry.start()
        await registry.stop()
    except Exception as e:
        logger.error(f"Error connecting to Hermes at {args.hermes_url}: {e}")
        logger.error("Make sure Hermes is running and accessible")
        sys.exit(1)
    
    if args.component.lower() == "all":
        components = list(COMPONENT_PATHS.keys())
    else:
        components = [args.component.lower()]
    
    for component in components:
        if component not in COMPONENT_PATHS:
            logger.error(f"Unknown component: {component}")
            continue
        
        success = await test_component_registration(
            component=component,
            hermes_url=args.hermes_url,
            timeout=args.timeout
        )
        
        if success:
            logger.info(f"✅ {component.capitalize()} registration test PASSED")
        else:
            logger.error(f"❌ {component.capitalize()} registration test FAILED")
    
if __name__ == "__main__":
    asyncio.run(main())