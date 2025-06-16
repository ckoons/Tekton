"""
Registration Manager - Central management for component registration.

This module provides the manager component for the Unified Registration Protocol,
handling component registration, authentication, and coordination.
"""

import time
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple

from hermes.core.service_discovery import ServiceRegistry
from hermes.core.message_bus import MessageBus
from hermes.core.registration.tokens import RegistrationToken
from hermes.core.registration.handlers import (
    handle_registration_request,
    handle_revocation_request,
    handle_heartbeat
)

# Configure logger
logger = logging.getLogger(__name__)

class RegistrationManager:
    """
    Central manager for component registration across the Tekton ecosystem.
    
    This class manages component registration, authentication, and propagation
    of registration information between Tekton components.
    """
    
    def __init__(self, 
                service_registry: ServiceRegistry,
                message_bus: MessageBus,
                secret_key: str,
                token_expiration: int = 3600):
        """
        Initialize the registration manager.
        
        Args:
            service_registry: Service registry for component tracking
            message_bus: Message bus for event propagation
            secret_key: Secret key for token generation/validation
            token_expiration: Token validity period in seconds
        """
        self.service_registry = service_registry
        self.message_bus = message_bus
        self.secret_key = secret_key
        self.token_expiration = token_expiration
        
        # Dictionary to store active tokens
        self.active_tokens: Dict[str, Dict[str, Any]] = {}
        
        # Set up message bus subscriptions for registration events
        self._setup_subscriptions()
        
        logger.info("Registration manager initialized")
    
    async def _setup_subscriptions_async(self) -> None:
        """Set up message bus subscriptions for registration events (async version)."""
        await self.message_bus.subscribe_async("tekton.registration.request", 
                                     lambda msg: handle_registration_request(self, msg))
        await self.message_bus.subscribe_async("tekton.registration.revoke", 
                                     lambda msg: handle_revocation_request(self, msg))
        await self.message_bus.subscribe_async("tekton.registration.heartbeat", 
                                     lambda msg: handle_heartbeat(self, msg))
        logger.info("Registration event subscriptions established (async)")
        
    def _setup_subscriptions(self) -> None:
        """Set up message bus subscriptions for registration events."""
        # For non-async context, use the synchronous subscribe method
        # This is needed because the constructor is not async
        self.message_bus.subscribe("tekton.registration.request", 
                                 lambda msg: handle_registration_request(self, msg))
        self.message_bus.subscribe("tekton.registration.revoke", 
                                 lambda msg: handle_revocation_request(self, msg))
        self.message_bus.subscribe("tekton.registration.heartbeat", 
                                 lambda msg: handle_heartbeat(self, msg))
        logger.info("Registration event subscriptions established")
    
    def register_component(self, 
                         component_id: str,
                         name: str,
                         version: str,
                         component_type: str,
                         endpoint: str,
                         capabilities: List[str],
                         health_check: Optional[Callable[[], bool]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        """
        Register a component with the Tekton ecosystem.
        
        Args:
            component_id: Unique identifier for the component
            name: Human-readable name
            version: Component version
            component_type: Type of component (e.g., "engram", "ergon", "athena")
            endpoint: Component endpoint (URL or connection string)
            capabilities: List of component capabilities
            health_check: Optional function to check component health
            metadata: Additional component metadata
            
        Returns:
            Tuple of (success, token_string)
        """
        # Register with service registry
        registry_success = self.service_registry.register(
            service_id=component_id,
            name=name,
            version=version,
            endpoint=endpoint,
            capabilities=capabilities,
            health_check=health_check,
            metadata={
                "type": component_type,
                **(metadata or {})
            }
        )
        
        if not registry_success:
            logger.error(f"Failed to register component {component_id} with service registry")
            return False, None
        
        # Generate registration token
        token = RegistrationToken(
            component_id=component_id,
            secret_key=self.secret_key,
            expiration=self.token_expiration
        )
        token_str = token.generate()
        
        # Store token information
        self.active_tokens[token.token_id] = {
            "component_id": component_id,
            "issued_at": token.issued_at,
            "expires_at": token.expires_at
        }
        
        # Publish registration event - we'll use the non-async version
        # since this method is not async
        try:
            self.message_bus.publish(
                topic="tekton.registration.completed",
                message={
                    "component_id": component_id,
                    "name": name,
                    "type": component_type,
                    "version": version,
                    "capabilities": capabilities,
                    "registered_at": time.time()
                },
                headers={
                    "event_type": "component_registration",
                    "component_id": component_id
                }
            )
        except Exception as e:
            logger.error(f"Error publishing registration event: {e}")
            # Continue execution even if publishing fails
        
        logger.info(f"Component {component_id} ({name}) registered successfully")
        return True, token_str
    
    def unregister_component(self, 
                           component_id: str,
                           token_str: str) -> bool:
        """
        Unregister a component from the Tekton ecosystem.
        
        Args:
            component_id: Component ID to unregister
            token_str: Registration token for authentication
            
        Returns:
            True if unregistration successful
        """
        # Validate token
        token_payload = RegistrationToken.validate(token_str, self.secret_key)
        if not token_payload or token_payload["component_id"] != component_id:
            logger.warning(f"Invalid token for component {component_id}")
            return False
        
        # Unregister from service registry
        registry_success = self.service_registry.unregister(component_id)
        
        if not registry_success:
            logger.error(f"Failed to unregister component {component_id} from service registry")
            return False
        
        # Remove token from active tokens
        token_id = token_payload["token_id"]
        if token_id in self.active_tokens:
            del self.active_tokens[token_id]
        
        # Publish unregistration event
        self.message_bus.publish(
            topic="tekton.registration.revoked",
            message={
                "component_id": component_id,
                "revoked_at": time.time()
            },
            headers={
                "event_type": "component_unregistration",
                "component_id": component_id
            }
        )
        
        logger.info(f"Component {component_id} unregistered successfully")
        return True
    
    def validate_component(self, 
                         component_id: str,
                         token_str: str) -> bool:
        """
        Validate a component's registration.
        
        Args:
            component_id: Component ID to validate
            token_str: Registration token for authentication
            
        Returns:
            True if component is validly registered
        """
        # Validate token
        token_payload = RegistrationToken.validate(token_str, self.secret_key)
        if not token_payload or token_payload["component_id"] != component_id:
            logger.warning(f"Invalid token for component {component_id}")
            return False
        
        # Check if component is registered
        service = self.service_registry.get_service(component_id)
        if not service:
            logger.warning(f"Component {component_id} not found in registry")
            return False
        
        logger.info(f"Component {component_id} validation successful")
        return True
    
    def send_heartbeat(self,
                     component_id: str,
                     token_str: str,
                     status: Dict[str, Any] = None) -> bool:
        """
        Send a heartbeat for a component to indicate it's still active.
        
        Args:
            component_id: Component ID
            token_str: Registration token for authentication
            status: Optional status information
            
        Returns:
            True if heartbeat was processed successfully
        """
        # Validate token
        token_payload = RegistrationToken.validate(token_str, self.secret_key)
        if not token_payload or token_payload["component_id"] != component_id:
            logger.warning(f"Invalid token for component {component_id} heartbeat")
            return False
        
        # Publish heartbeat event
        self.message_bus.publish(
            topic="tekton.registration.heartbeat",
            message={
                "component_id": component_id,
                "timestamp": time.time(),
                "status": status or {}
            },
            headers={
                "event_type": "component_heartbeat",
                "component_id": component_id
            }
        )
        
        logger.debug(f"Heartbeat received for component {component_id}")
        return True