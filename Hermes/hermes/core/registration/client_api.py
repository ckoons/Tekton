"""
Registration Client API - HTTP client for the Unified Registration Protocol.

This module provides a client for components to interact with the Hermes
registration system via HTTP API endpoints.
"""

import json
import time
import logging
import threading
import requests
from typing import Dict, List, Any, Optional, Callable, Union

try:
    from shared.urls import hermes_url as get_hermes_url
except ImportError:
    get_hermes_url = None

# Configure logger
logger = logging.getLogger(__name__)

class RegistrationClientAPI:
    """
    HTTP client for interacting with the Tekton registration system.
    
    This class provides methods for components to register, unregister,
    and maintain their presence in the Tekton ecosystem using the HTTP API.
    """
    
    def __init__(self,
                component_id: str,
                name: str,
                version: str,
                component_type: str,
                endpoint: str,
                capabilities: List[str],
                api_endpoint: str = None,
                metadata: Optional[Dict[str, Any]] = None,
                heartbeat_interval: int = 60):
        """
        Initialize the registration client.
        
        Args:
            component_id: Unique identifier for this component
            name: Human-readable name
            version: Component version
            component_type: Type of component (e.g., "engram", "ergon", "athena")
            endpoint: Component endpoint (URL or connection string)
            capabilities: List of component capabilities
            api_endpoint: Hermes API endpoint URL
            metadata: Additional component metadata
            heartbeat_interval: Interval in seconds for sending heartbeats
        """
        self.component_id = component_id
        self.name = name
        self.version = version
        self.component_type = component_type
        self.endpoint = endpoint
        self.capabilities = capabilities
        if api_endpoint:
            self.api_endpoint = api_endpoint.rstrip("/")
        elif get_hermes_url:
            self.api_endpoint = get_hermes_url("/api").rstrip("/")
        else:
            self.api_endpoint = "http://localhost:8000/api"
        self.metadata = metadata or {}
        self.heartbeat_interval = heartbeat_interval
        
        # Registration token
        self.token = None
        
        # Heartbeat thread
        self.heartbeat_thread = None
        self.running = False
        
        logger.info(f"Registration client API initialized for component {component_id}")
    
    def register(self) -> bool:
        """
        Register this component with the Tekton ecosystem.
        
        Returns:
            True if registration successful
        """
        if self.token:
            logger.warning(f"Component {self.component_id} already registered")
            return True
        
        # Create registration request
        request = {
            "component_id": self.component_id,
            "name": self.name,
            "version": self.version,
            "type": self.component_type,
            "endpoint": self.endpoint,
            "capabilities": self.capabilities,
            "metadata": self.metadata
        }
        
        try:
            # Send registration request
            response = requests.post(
                f"{self.api_endpoint}/register",
                json=request,
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                if self.token:
                    logger.info(f"Component {self.component_id} registered successfully")
                    self._start_heartbeat()
                    return True
                else:
                    logger.error("Registration successful but no token received")
                    return False
            else:
                logger.error(f"Registration failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending registration request: {e}")
            return False
    
    def unregister(self) -> bool:
        """
        Unregister this component from the Tekton ecosystem.
        
        Returns:
            True if unregistration successful
        """
        if not self.token:
            logger.warning("Component not registered")
            return True
        
        try:
            # Stop heartbeat thread
            self._stop_heartbeat()
            
            # Send unregistration request
            response = requests.post(
                f"{self.api_endpoint}/unregister",
                params={"component_id": self.component_id},
                headers={
                    "Content-Type": "application/json",
                    "X-Authentication-Token": self.token
                }
            )
            
            # Check response
            if response.status_code == 200:
                self.token = None
                logger.info(f"Component {self.component_id} unregistered successfully")
                return True
            else:
                logger.error(f"Unregistration failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending unregistration request: {e}")
            return False
    
    def find_services(self, 
                     capability: Optional[str] = None,
                     component_type: Optional[str] = None,
                     healthy_only: bool = False) -> List[Dict[str, Any]]:
        """
        Find services based on criteria.
        
        Args:
            capability: Optional capability to search for
            component_type: Optional component type to filter by
            healthy_only: Whether to only return healthy services
            
        Returns:
            List of matching services
        """
        try:
            # Create query request
            request = {
                "capability": capability,
                "component_type": component_type,
                "healthy_only": healthy_only
            }
            
            # Send query request
            response = requests.post(
                f"{self.api_endpoint}/query",
                json=request,
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            # Check response
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Service query failed with status {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error sending service query request: {e}")
            return []
    
    def _send_heartbeat(self) -> bool:
        """
        Send a heartbeat to the registration service.
        
        Returns:
            True if heartbeat successful
        """
        if not self.token:
            logger.warning("Component not registered, cannot send heartbeat")
            return False
        
        try:
            # Create heartbeat request
            request = {
                "component_id": self.component_id,
                "status": {
                    "healthy": True,
                    "timestamp": time.time()
                }
            }
            
            # Send heartbeat request
            response = requests.post(
                f"{self.api_endpoint}/heartbeat",
                json=request,
                headers={
                    "Content-Type": "application/json",
                    "X-Authentication-Token": self.token
                }
            )
            
            # Check response
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Heartbeat failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending heartbeat request: {e}")
            return False
    
    def _heartbeat_loop(self) -> None:
        """
        Main loop for sending heartbeats.
        
        This runs in a separate thread and periodically sends heartbeats
        to indicate the component is still active.
        """
        while self.running and self.token:
            try:
                success = self._send_heartbeat()
                if not success:
                    logger.warning("Failed to send heartbeat")
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
            
            # Sleep until next heartbeat
            time.sleep(self.heartbeat_interval)
    
    def _start_heartbeat(self) -> None:
        """Start the heartbeat thread."""
        if self.running:
            return
            
        self.running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        logger.info("Heartbeat thread started")
    
    def _stop_heartbeat(self) -> None:
        """Stop the heartbeat thread."""
        self.running = False
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)
        logger.info("Heartbeat thread stopped")