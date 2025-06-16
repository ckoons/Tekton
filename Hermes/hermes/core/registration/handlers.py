"""
Registration Event Handlers - Handlers for registration-related events.

This module provides event handlers for processing registration, revocation, 
and heartbeat events in the Unified Registration Protocol.
"""

import time
import logging
from typing import Dict, Any, Optional

# Configure logger
logger = logging.getLogger(__name__)

# Manager Event Handlers

def handle_registration_request(manager, message: Dict[str, Any]) -> None:
    """
    Handle a registration request message.
    
    Args:
        manager: Registration manager instance
        message: Registration request message
    """
    try:
        payload = message["payload"]
        component_id = payload.get("component_id")
        name = payload.get("name")
        version = payload.get("version")
        component_type = payload.get("type")
        endpoint = payload.get("endpoint")
        capabilities = payload.get("capabilities", [])
        metadata = payload.get("metadata", {})
        
        if not all([component_id, name, version, component_type, endpoint]):
            logger.error("Missing required fields in registration request")
            return
        
        success, token_str = manager.register_component(
            component_id=component_id,
            name=name,
            version=version,
            component_type=component_type,
            endpoint=endpoint,
            capabilities=capabilities,
            metadata=metadata
        )
        
        # Publish response
        if success and token_str:
            manager.message_bus.publish(
                topic=f"tekton.registration.response.{component_id}",
                message={
                    "success": True,
                    "token": token_str
                }
            )
        else:
            manager.message_bus.publish(
                topic=f"tekton.registration.response.{component_id}",
                message={
                    "success": False,
                    "error": "Registration failed"
                }
            )
            
    except Exception as e:
        logger.error(f"Error handling registration request: {e}")

def handle_revocation_request(manager, message: Dict[str, Any]) -> None:
    """
    Handle a revocation request message.
    
    Args:
        manager: Registration manager instance
        message: Revocation request message
    """
    try:
        payload = message["payload"]
        component_id = payload.get("component_id")
        token_str = payload.get("token")
        
        if not all([component_id, token_str]):
            logger.error("Missing required fields in revocation request")
            return
        
        success = manager.unregister_component(
            component_id=component_id,
            token_str=token_str
        )
        
        # Publish response
        manager.message_bus.publish(
            topic=f"tekton.registration.response.{component_id}",
            message={
                "success": success,
                "operation": "revocation"
            }
        )
            
    except Exception as e:
        logger.error(f"Error handling revocation request: {e}")

def handle_heartbeat(manager, message: Dict[str, Any]) -> None:
    """
    Handle a heartbeat message.
    
    Args:
        manager: Registration manager instance
        message: Heartbeat message
    """
    try:
        payload = message["payload"]
        component_id = payload.get("component_id")
        
        # Update last seen timestamp in service registry
        service = manager.service_registry.get_service(component_id)
        if service:
            service["last_heartbeat"] = time.time()
            
    except Exception as e:
        logger.error(f"Error handling heartbeat: {e}")

# Client Event Handlers

def handle_registration_response(client, message: Dict[str, Any]) -> None:
    """
    Handle a registration response message.
    
    Args:
        client: Registration client instance
        message: Registration response message
    """
    try:
        payload = message["payload"]
        success = payload.get("success", False)
        
        if success:
            client.token = payload.get("token")
            logger.info(f"Component {client.component_id} registered successfully")
        else:
            error = payload.get("error", "Unknown error")
            logger.error(f"Registration failed: {error}")
            
    except Exception as e:
        logger.error(f"Error handling registration response: {e}")

def heartbeat_loop(client) -> None:
    """
    Main loop for sending heartbeats.
    
    This runs in a separate thread and periodically sends heartbeats
    to indicate the component is still active.
    
    Args:
        client: Registration client instance
    """
    while client.running and client.token:
        try:
            # Create heartbeat message
            heartbeat = {
                "component_id": client.component_id,
                "token": client.token,
                "timestamp": time.time(),
                "status": {
                    "healthy": True  # Can be extended with more status info
                }
            }
            
            # Publish heartbeat
            client.message_bus.publish(
                topic="tekton.registration.heartbeat",
                message=heartbeat,
                headers={
                    "event_type": "component_heartbeat",
                    "component_id": client.component_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
            
        # Sleep until next heartbeat
        time.sleep(client.heartbeat_interval)