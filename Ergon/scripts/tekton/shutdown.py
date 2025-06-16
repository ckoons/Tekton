#!/usr/bin/env python3
"""
Tekton Component Shutdown

Contains functions for stopping Tekton components.
"""

import sys
import logging
import subprocess
from typing import Dict, Any, Optional, List

from .components import COMPONENTS, running_components, component_processes, running_lock

# Initialize imports needed for shutdown
try:
    # Import Ergon modules
    from ergon.core.memory import client_manager
except ImportError as e:
    logging.error(f"Error importing Ergon modules: {e}")
    logging.error("Please make sure Ergon is installed correctly.")
    sys.exit(1)

logger = logging.getLogger("tekton.shutdown")

async def stop_component(component_id: str) -> bool:
    """
    Stop a running component.
    
    Args:
        component_id: ID of the component to stop
        
    Returns:
        True if successful
    """
    logger.info(f"Stopping component: {component_id}...")
    
    # If there's a client registration, deregister it
    component = COMPONENTS.get(component_id)
    if component and "client_id" in component:
        client_id = component["client_id"]
        try:
            success = await client_manager.deregister_client(client_id)
            if success:
                logger.info(f"Deregistered client {client_id} for component {component_id}")
            else:
                logger.warning(f"Failed to deregister client {client_id} for component {component_id}")
        except Exception as e:
            logger.error(f"Error deregistering client {client_id}: {e}")
    
    # If the component has a process, terminate it
    with running_lock:
        if component_id in component_processes:
            process = component_processes[component_id]
            try:
                # Try to terminate gracefully
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if termination doesn't work
                    process.kill()
                
                logger.info(f"Stopped process for component {component_id}")
                # Remove from tracked processes
                del component_processes[component_id]
            except Exception as e:
                logger.error(f"Error stopping process for component {component_id}: {e}")
                return False
        
        # Mark as not running
        if component_id in running_components:
            del running_components[component_id]
    
    logger.info(f"Component {component_id} stopped successfully")
    return True

async def stop_all_components() -> bool:
    """
    Stop all running components in reverse dependency order.
    
    Returns:
        True if all components stopped successfully
    """
    logger.info("Stopping all Tekton components...")
    
    # Get components in reverse startup order
    component_ids = sorted(
        COMPONENTS.keys(),
        key=lambda c: COMPONENTS[c]["startup_sequence"],
        reverse=True
    )
    
    # Stop each component
    all_success = True
    for component_id in component_ids:
        with running_lock:
            if component_id in running_components:
                success = await stop_component(component_id)
                if not success:
                    all_success = False
    
    logger.info("All Tekton components stopped")
    return all_success