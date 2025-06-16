#!/usr/bin/env python3
"""
Simple registration wrapper to ensure components register with Hermes.
Can be called from any component's startup to guarantee registration.
"""
import asyncio
import os
import sys
import logging

# Import from same directory
from .hermes_registration import HermesRegistration

logger = logging.getLogger(__name__)

async def ensure_component_registered(
    component_name: str,
    port: int,
    version: str = "0.1.0",
    capabilities: list = None,
    metadata: dict = None
) -> bool:
    """
    Ensure a component is registered with Hermes.
    This is a simple wrapper that handles common registration issues.
    """
    try:
        hermes = HermesRegistration()
        success = await hermes.register_component(
            component_name=component_name,
            port=port,
            version=version,
            capabilities=capabilities or [],
            metadata=metadata or {}
        )
        
        if success:
            logger.info(f"Successfully registered {component_name} with Hermes")
        else:
            logger.warning(f"Failed to register {component_name} with Hermes")
            
        return success
        
    except Exception as e:
        logger.error(f"Error registering {component_name}: {e}")
        return False

def register_component_sync(
    component_name: str,
    port: int,
    version: str = "0.1.0", 
    capabilities: list = None,
    metadata: dict = None
) -> bool:
    """Synchronous wrapper for registration."""
    return asyncio.run(ensure_component_registered(
        component_name, port, version, capabilities, metadata
    ))

if __name__ == "__main__":
    # Test registration
    import sys
    if len(sys.argv) > 1:
        name = sys.argv[1]
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        print(f"Registering {name} on port {port}...")
        result = register_component_sync(name, port)
        print(f"Result: {result}")