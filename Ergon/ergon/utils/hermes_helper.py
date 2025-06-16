"""Helper for Hermes integration.

This module provides helper functions for integrating Ergon with Hermes.
"""

import os
import sys
import logging
import asyncio
import time
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

async def register_with_hermes(
    service_id: str,
    name: str,
    capabilities: List[str],
    metadata: Optional[Dict[str, Any]] = None,
    version: str = "0.1.0",
    endpoint: Optional[str] = None
) -> bool:
    """Register a service with the Hermes service registry.
    
    Args:
        service_id: Unique identifier for the service
        name: Human-readable name for the service
        capabilities: List of capabilities
        metadata: Additional metadata for the service
        version: Service version
        endpoint: Service endpoint URL
        
    Returns:
        Success status
    """
    try:
        # Find the Hermes directory by looking in the parent of the current directory
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        parent_dir = os.path.dirname(current_dir)
        hermes_dir = os.path.join(parent_dir, "Hermes")
        
        if not os.path.exists(hermes_dir):
            logger.error(f"Hermes directory not found at {hermes_dir}")
            return False
        
        # Add Hermes to path if not already there
        if hermes_dir not in sys.path:
            sys.path.insert(0, hermes_dir)
            logger.debug(f"Added Hermes directory to path: {hermes_dir}")
        
        # Since we're having issues with direct ServiceRegistry import,
        # let's create a JSON registration file that Hermes can discover
        registration_dir = os.path.join(hermes_dir, "registrations")
        os.makedirs(registration_dir, exist_ok=True)
        
        import json
        import uuid
        
        # Create registration data
        registration_data = {
            "service_id": service_id,
            "name": name,
            "version": version,
            "endpoint": endpoint,
            "capabilities": capabilities,
            "metadata": metadata or {},
            "instance_uuid": str(uuid.uuid4()),
            "registration_time": time.time(),
            "status": "active"
        }
        
        # Add UI component metadata if this is a UI-enabled service
        if "ui_enabled" in (metadata or {}) and metadata.get("ui_enabled"):
            registration_data["ui_component"] = metadata.get("ui_component", service_id)
        
        # Write registration to file
        registration_file = os.path.join(registration_dir, f"{service_id}.json")
        with open(registration_file, "w") as f:
            json.dump(registration_data, f, indent=2)
            
        logger.info(f"Created registration file for {name} at {registration_file}")
        success = True
        
        if success:
            logger.info(f"Successfully registered {name} with Hermes")
            return True
        else:
            logger.warning(f"Failed to register {name} with Hermes")
            return False
    
    except Exception as e:
        logger.error(f"Error registering with Hermes: {e}")
        return False