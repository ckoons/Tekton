#!/usr/bin/env python3
"""
Simple singleton fix for Hermes registration persistence.

This creates a module-level singleton that both app.py and endpoints.py can use.
"""

import os
from hermes.core.service_discovery import ServiceRegistry
from hermes.core.message_bus import MessageBus
from hermes.core.registration import RegistrationManager

# Create singleton instances
_service_registry = None
_message_bus = None
_registration_manager = None

def get_shared_registration_manager():
    """Get or create the shared registration manager singleton."""
    global _service_registry, _message_bus, _registration_manager
    
    if _registration_manager is None:
        # Create singleton instances
        _service_registry = ServiceRegistry()
        _message_bus = MessageBus()
        
        # Start health check monitoring
        _service_registry.start()
        
        _registration_manager = RegistrationManager(
            service_registry=_service_registry,
            message_bus=_message_bus,
            secret_key="tekton-secret-key"
        )
        
        print("[HERMES] Created singleton RegistrationManager")
    
    return _registration_manager

def get_shared_service_registry():
    """Get the shared service registry."""
    if _service_registry is None:
        get_shared_registration_manager()  # This will create it
    return _service_registry

def get_shared_message_bus():
    """Get the shared message bus."""
    if _message_bus is None:
        get_shared_registration_manager()  # This will create it
    return _message_bus
