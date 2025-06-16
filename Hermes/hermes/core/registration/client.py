"""
Registration Client - Client for interacting with the registration system.

This module provides a client for components to register and maintain
their presence in the Tekton ecosystem.
"""

import time
import threading
import logging
from typing import Dict, List, Any, Optional

from hermes.core.message_bus import MessageBus
from hermes.core.registration.handlers import handle_registration_response, heartbeat_loop

# Configure logger
logger = logging.getLogger(__name__)

class RegistrationClient:
    """
    Client for interacting with the Tekton registration system.
    
    This class provides methods for components to register, unregister,
    and maintain their presence in the Tekton ecosystem.
    """
    
    def __init__(self,
                component_id: str,
                name: str,
                version: str,
                component_type: str,
                endpoint: str,
                capabilities: List[str],
                message_bus: MessageBus,
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
            message_bus: Message bus for communication
            metadata: Additional component metadata
            heartbeat_interval: Interval in seconds for sending heartbeats
        """
        self.component_id = component_id
        self.name = name
        self.version = version
        self.component_type = component_type
        self.endpoint = endpoint
        self.capabilities = capabilities
        self.message_bus = message_bus
        self.metadata = metadata or {}
        self.heartbeat_interval = heartbeat_interval
        
        # Registration token
        self.token = None
        
        # Heartbeat thread
        self.heartbeat_thread = None
        self.running = False
        
        # Set up message bus subscriptions
        self._setup_subscriptions()
        
        logger.info(f"Registration client initialized for component {component_id}")
    
    def _setup_subscriptions(self) -> None:
        """Set up message bus subscriptions for registration events."""
        self.message_bus.subscribe(
            f"tekton.registration.response.{self.component_id}",
            lambda msg: handle_registration_response(self, msg)
        )
    
    async def register(self) -> bool:
        """
        Register this component with the Tekton ecosystem.
        
        Returns:
            True if registration successful
        """
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
        
        # Publish registration request
        request_success = self.message_bus.publish(
            topic="tekton.registration.request",
            message=request,
            headers={
                "event_type": "registration_request",
                "component_id": self.component_id
            }
        )
        
        if not request_success:
            logger.error("Failed to send registration request")
            return False
        
        # Wait for response (in a real implementation, this would use async/await)
        # For now, we'll simulate with a simple loop
        max_wait = 10  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if self.token:
                self._start_heartbeat()
                return True
            time.sleep(0.1)
        
        logger.error("Timed out waiting for registration response")
        return False
    
    async def unregister(self) -> bool:
        """
        Unregister this component from the Tekton ecosystem.
        
        Returns:
            True if unregistration successful
        """
        if not self.token:
            logger.warning("Component not registered")
            return False
        
        # Stop heartbeat thread
        self._stop_heartbeat()
        
        # Create revocation request
        request = {
            "component_id": self.component_id,
            "token": self.token
        }
        
        # Publish revocation request
        request_success = self.message_bus.publish(
            topic="tekton.registration.revoke",
            message=request,
            headers={
                "event_type": "revocation_request",
                "component_id": self.component_id
            }
        )
        
        if not request_success:
            logger.error("Failed to send revocation request")
            return False
        
        # Clear token
        self.token = None
        
        logger.info(f"Component {self.component_id} unregistered")
        return True
    
    def _start_heartbeat(self) -> None:
        """Start the heartbeat thread."""
        if self.running:
            return
            
        self.running = True
        self.heartbeat_thread = threading.Thread(target=lambda: heartbeat_loop(self))
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        logger.info("Heartbeat thread started")
    
    def _stop_heartbeat(self) -> None:
        """Stop the heartbeat thread."""
        self.running = False
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)
        logger.info("Heartbeat thread stopped")