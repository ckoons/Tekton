"""
Service Discovery - Registry for Tekton components and capabilities.

This module provides service registration, discovery, and health monitoring
for Tekton components.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Set, Callable
import threading
import asyncio

# Configure logger
logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Registry for Tekton components and their capabilities.
    
    This class provides methods for registering components, discovering
    services, and monitoring component health.
    """
    
    def __init__(self, 
                check_interval: int = 30,
                timeout: int = 10):
        """
        Initialize the service registry.
        
        Args:
            check_interval: Interval in seconds between health checks
            timeout: Timeout in seconds for health check responses
        """
        self.check_interval = check_interval
        self.timeout = timeout
        
        # Dictionary to store registered services
        self.services: Dict[str, Dict[str, Any]] = {}
        
        # Dictionary to store last health check results
        self.health: Dict[str, bool] = {}
        
        # Health check thread
        self.health_check_thread = None
        self.running = False
        
        logger.info("Service registry initialized")
    
    def start(self) -> None:
        """Start the health check monitoring thread."""
        if self.running:
            return
            
        self.running = True
        self.health_check_thread = threading.Thread(target=self._health_check_loop)
        self.health_check_thread.daemon = True
        self.health_check_thread.start()
        logger.info("Health check monitoring started")
    
    def register(self, 
                service_id: str, 
                name: str,
                version: str,
                endpoint: str,
                capabilities: List[str],
                health_check: Optional[Callable[[], bool]] = None,
                metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a service with the registry.
        
        Args:
            service_id: Unique identifier for the service
            name: Human-readable name
            version: Service version
            endpoint: Service endpoint (URL or connection string)
            capabilities: List of service capabilities
            health_check: Optional function to check service health
            metadata: Additional service metadata
            
        Returns:
            True if registration successful
        """
        if service_id in self.services:
            logger.warning(f"Service {service_id} already registered, updating registration")
        
        self.services[service_id] = {
            "name": name,
            "version": version,
            "endpoint": endpoint,
            "capabilities": capabilities,
            "health_check": health_check,
            "metadata": metadata or {},
            "registered_at": time.time()
        }
        
        # Initialize health as unknown
        self.health[service_id] = None
        
        logger.info(f"Registered service {service_id} ({name} v{version})")
        return True
    
    def unregister(self, service_id: str) -> bool:
        """
        Unregister a service from the registry.
        
        Args:
            service_id: Service ID to unregister
            
        Returns:
            True if unregistration successful
        """
        if service_id in self.services:
            del self.services[service_id]
            
            if service_id in self.health:
                del self.health[service_id]
                
            logger.info(f"Unregistered service {service_id}")
            return True
        
        logger.warning(f"Service {service_id} not found in registry")
        return False
    
    def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered service.
        
        Args:
            service_id: Service ID to look up
            
        Returns:
            Service information or None if not found
        """
        return self.services.get(service_id)
    
    def find_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """
        Find services by capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of services with the requested capability
        """
        matching_services = []
        
        for service_id, service in self.services.items():
            if capability in service["capabilities"]:
                # Include service ID in the result
                result = service.copy()
                result["id"] = service_id
                result["healthy"] = self.health.get(service_id, None)
                matching_services.append(result)
        
        return matching_services
    
    def get_all_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered services.
        
        Returns:
            Dictionary of all services
        """
        # Create a copy with health information
        result = {}
        for service_id, service in self.services.items():
            service_copy = service.copy()
            service_copy["healthy"] = self.health.get(service_id, None)
            result[service_id] = service_copy
            
        return result
    
    def _health_check_loop(self) -> None:
        """
        Main loop for health check monitoring.
        
        This runs in a separate thread and periodically checks
        the health of all registered services.
        """
        while self.running:
            for service_id, service in self.services.items():
                try:
                    # Check if service has a health check function
                    health_check = service.get("health_check")
                    if health_check and callable(health_check):
                        # Call the health check function
                        healthy = health_check()
                        self.health[service_id] = healthy
                        
                        if not healthy:
                            logger.warning(f"Service {service_id} is unhealthy")
                    
                except Exception as e:
                    logger.error(f"Error checking health of service {service_id}: {e}")
                    self.health[service_id] = False
            
            # Sleep until next check interval
            time.sleep(self.check_interval)
    
    def stop(self) -> None:
        """Stop the health check monitoring thread."""
        self.running = False
        if self.health_check_thread and self.health_check_thread.is_alive():
            self.health_check_thread.join(timeout=5)
        logger.info("Health check monitoring stopped")