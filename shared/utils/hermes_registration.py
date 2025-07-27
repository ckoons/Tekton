"""
Hermes Registration Utility for Tekton Components

Provides standard registration functionality for components to register with Hermes.
"""
import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime


logger = logging.getLogger(__name__)


class HermesRegistration:
    """Handles component registration with Hermes"""
    
    def __init__(self, hermes_url: str = "http://localhost:8001"):
        self.hermes_url = hermes_url
        self.registration_data: Optional[Dict[str, Any]] = None
        self.is_registered = False
        
    async def register_component(
        self,
        component_name: str,
        port: int,
        version: str,
        capabilities: List[str],
        health_endpoint: str = "/health",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register a component with Hermes"""
        try:
            # Prepare registration data matching the API schema
            registration_request = {
                "name": component_name,
                "version": version,
                "type": component_name,  # Use component name as type
                "endpoint": f"http://localhost:{port}",
                "capabilities": capabilities,
                "metadata": metadata or {}
            }
            
            # Store additional data for internal use
            self.registration_data = {
                **registration_request,
                "port": port,
                "health_endpoint": health_endpoint,
                "status": "active",
                "registered_at": datetime.now().isoformat()
            }
            
            registration_url = f"{self.hermes_url}/api/register"
            logger.info(f"Attempting to register {component_name} with Hermes at: {registration_url}")
            logger.debug(f"Registration data: {registration_request}")
            
            # DEBUG: Write to file
            with open(f"/tmp/{component_name}_registration_debug.txt", "a") as f:
                f.write(f"[{datetime.now()}] POST to: {registration_url}\n")
                f.write(f"[{datetime.now()}] Data: {registration_request}\n")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    registration_url,
                    json=registration_request,
                    timeout=5
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        self.is_registered = True
                        logger.info(f"Successfully registered {component_name} with Hermes")
                        # DEBUG: Write to file
                        with open(f"/tmp/{component_name}_registration_debug.txt", "a") as f:
                            f.write(f"[{datetime.now()}] SUCCESS: {result}\n")
                        return True
                    else:
                        response_text = await resp.text()
                        logger.error(f"Failed to register with Hermes: HTTP {resp.status} - {response_text}")
                        # DEBUG: Write to file
                        with open(f"/tmp/{component_name}_registration_debug.txt", "a") as f:
                            f.write(f"[{datetime.now()}] FAILED: HTTP {resp.status} - {response_text}\n")
                        return False
                        
        except aiohttp.ClientError as e:
            logger.warning(f"Could not connect to Hermes at {self.hermes_url}/api/register: {e}")
            # DEBUG: Write to file
            with open(f"/tmp/{component_name}_registration_debug.txt", "a") as f:
                f.write(f"[{datetime.now()}] CLIENT ERROR: {e}\n")
            return False
        except Exception as e:
            logger.error(f"Error registering with Hermes: {e}")
            # DEBUG: Write to file
            with open(f"/tmp/{component_name}_registration_debug.txt", "a") as f:
                f.write(f"[{datetime.now()}] ERROR: {e}\n")
            return False
    
    async def heartbeat(self, component_name: str, status: str = "healthy") -> bool:
        """Send heartbeat to Hermes"""
        if not self.is_registered:
            return False
            
        try:
            heartbeat_data = {
                "component_id": component_name,
                "status": {"health": status}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hermes_url}/api/heartbeat",
                    json=heartbeat_data,
                    timeout=2
                ) as resp:
                    return resp.status == 200
                    
        except Exception as e:
            logger.debug(f"Heartbeat failed: {e}")
            return False
    
    async def deregister(self, component_name: str) -> bool:
        """Deregister from Hermes"""
        if not self.is_registered:
            return True
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hermes_url}/api/unregister",
                    json={"component_name": component_name},
                    timeout=2
                ) as resp:
                    if resp.status == 200:
                        self.is_registered = False
                        logger.info(f"Successfully deregistered {component_name} from Hermes")
                        return True
                    return False
                    
        except Exception as e:
            logger.debug(f"Deregistration failed: {e}")
            return False


async def register_with_hermes(
    component_name: str,
    port: int,
    version: str,
    capabilities: List[str],
    hermes_url: str = "http://localhost:8001",
    metadata: Optional[Dict[str, Any]] = None
) -> HermesRegistration:
    """Convenience function to register a component with Hermes"""
    registration = HermesRegistration(hermes_url)
    await registration.register_component(
        component_name=component_name,
        port=port,
        version=version,
        capabilities=capabilities,
        metadata=metadata
    )
    return registration


# Background task for periodic heartbeats
async def heartbeat_loop(
    registration: HermesRegistration,
    component_name: str,
    interval: int = 30
):
    """Send periodic heartbeats to Hermes"""
    while registration.is_registered:
        await asyncio.sleep(interval)
        await registration.heartbeat(component_name)