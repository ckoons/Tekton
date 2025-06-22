"""
Global configuration and state management for Tekton components.

This module provides a unified configuration system that replaces scattered
global variables with a centralized, singleton configuration object.
"""
import os
import time
import logging
import asyncio
from typing import Dict, Any, Optional, TypeVar, Generic

from shared.utils.env_config import get_component_config as _get_original_component_config
# Try to import landmarks decorators, but make them optional
try:
    from landmarks import state_checkpoint, architecture_decision
except ImportError:
    # Create no-op decorators if landmarks module is not available
    def state_checkpoint(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def architecture_decision(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)

T = TypeVar('T')


@state_checkpoint(
    title="Global configuration singleton",
    state_type="singleton",
    persistence=False,
    consistency_requirements="Thread-safe access required",
    recovery_strategy="Reinitialize from environment on restart",
    impacts=["all_components"],
    critical=True
)
@architecture_decision(
    title="Centralized configuration management",
    rationale="Replace scattered globals with unified config to reduce coupling and improve testability",
    alternatives_considered=["Distributed config files", "Environment variables only", "Database config"],
    impacts=["configuration", "state_management", "service_discovery"],
    decided_by="team",
    date="2024-10-15"
)
class GlobalConfig:
    """
    Unified global configuration and state management for Tekton components.
    
    This class:
    1. Wraps ComponentConfig for environment-based configuration
    2. Manages runtime state (services, registration, etc.)
    3. Provides data directory management
    4. Acts as a service registry for shared services
    5. Provides service URL resolution (future: Hermes service discovery)
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            # Wrap ComponentConfig
            self._component_config = _get_original_component_config()
            
            # Runtime state
            self._services: Dict[str, Any] = {}
            self._registration_info: Dict[str, Any] = {}
            self._start_time = time.time()
            
            # Service URL cache - populated once from Hermes
            self._service_urls: Dict[str, str] = {}
            self._service_urls_loaded = False
            
            # Component-specific state (will be set by components)
            self.hermes_registration = None
            self.heartbeat_task = None
            self.is_registered_with_hermes = False
            self.mcp_bridge = None
            
            # Setup base data directory
            self._base_data_dir = os.environ.get('TEKTON_DATA_DIR',
                os.path.join(os.path.expanduser('~'), '.tekton', 'data'))
            
            self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'GlobalConfig':
        """Get singleton instance of GlobalConfig."""
        return cls()
    
    # Configuration access (delegate to ComponentConfig)
    @property
    def config(self):
        """Access raw component configs for backward compatibility."""
        return self._component_config
    
    def get_component_config(self, component_name: str):
        """
        Get configuration for a specific component.
        
        Args:
            component_name: Name of the component (e.g., 'rhetor', 'apollo')
            
        Returns:
            Component-specific configuration object
        """
        return getattr(self._component_config, component_name.lower())
    
    # Data directory management
    def get_data_dir(self, component_name: str) -> str:
        """
        Get data directory for a component, creating it if necessary.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Path to component's data directory
        """
        component_dir = os.path.join(self._base_data_dir, component_name.lower())
        os.makedirs(component_dir, exist_ok=True)
        return component_dir
    
    # Service registry
    def get_service(self, service_name: str, factory_func=None):
        """
        Get or create a shared service.
        
        Args:
            service_name: Name of the service (e.g., 'llm_client', 'budget_manager')
            factory_func: Optional factory function to create the service if not exists
            
        Returns:
            Service instance or None if not found and no factory provided
        """
        if service_name not in self._services and factory_func:
            logger.debug(f"Creating service: {service_name}")
            self._services[service_name] = factory_func()
        return self._services.get(service_name)
    
    def set_service(self, service_name: str, service_instance):
        """
        Register a service instance.
        
        Args:
            service_name: Name of the service
            service_instance: The service instance to register
        """
        logger.debug(f"Registering service: {service_name}")
        self._services[service_name] = service_instance
    
    def remove_service(self, service_name: str):
        """
        Remove a service from the registry.
        
        Args:
            service_name: Name of the service to remove
        """
        if service_name in self._services:
            logger.debug(f"Removing service: {service_name}")
            del self._services[service_name]
    
    # Service URL resolution
    def _load_service_urls(self):
        """Load all service URLs from Hermes once."""
        if self._service_urls_loaded:
            return
            
        try:
            import requests
            response = requests.get("http://localhost:8001/components", timeout=2.0)
            if response.ok:
                data = response.json()
                for component in data.get('components', []):
                    name = component.get('name')
                    endpoint = component.get('endpoint')
                    if name and endpoint:
                        self._service_urls[name] = endpoint
                logger.info(f"Loaded {len(self._service_urls)} service URLs from Hermes")
        except Exception as e:
            logger.debug(f"Could not load service URLs from Hermes: {e}")
        
        self._service_urls_loaded = True
    
    def get_service_url(self, component_name: str) -> str:
        """
        Get URL for a component service using Hermes service discovery.
        
        Queries Hermes once on first call to get all service URLs,
        then uses cached values. Falls back to localhost if Hermes
        is unavailable or component not found.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Service URL (e.g., "http://localhost:8003")
        """
        # Load service URLs from Hermes on first call
        if not self._service_urls_loaded:
            self._load_service_urls()
        
        # Check cache first
        if component_name in self._service_urls:
            return self._service_urls[component_name]
        
        # Fallback to localhost configuration
        config = self.get_component_config(component_name)
        return f"http://localhost:{config.port}"
    
    # Runtime state
    @property
    def uptime(self) -> float:
        """Get component uptime in seconds."""
        return time.time() - self._start_time
    
    def set_registration_info(self, component_name: str, info: Dict[str, Any]):
        """
        Store registration information for a component.
        
        Args:
            component_name: Name of the component
            info: Registration information dictionary
        """
        self._registration_info[component_name] = info
    
    def get_registration_info(self, component_name: str) -> Optional[Dict[str, Any]]:
        """
        Get registration information for a component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Registration information or None if not registered
        """
        return self._registration_info.get(component_name)
    
    def clear_runtime_state(self):
        """Clear all runtime state (useful for testing)."""
        self._services.clear()
        self._registration_info.clear()
        self._service_urls.clear()
        self._service_urls_loaded = False
        self.hermes_registration = None
        self.heartbeat_task = None
        self.is_registered_with_hermes = False
        self.mcp_bridge = None
        self._start_time = time.time()
    
    # Tekton-wide settings
    @property
    def debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.config.tekton.debug
    
    @property
    def log_level(self) -> str:
        """Get configured log level."""
        return self.config.tekton.log_level
    
    @property
    def mcp_enabled(self) -> bool:
        """Check if MCP is enabled system-wide."""
        return self.config.tekton.mcp_enabled


# Update the original get_component_config to return GlobalConfig
def get_component_config():
    """
    Get the global ComponentConfig instance.
    
    This now returns the GlobalConfig's internal component config
    for backward compatibility.
    
    Returns:
        ComponentConfig instance wrapped by GlobalConfig
    """
    return GlobalConfig.get_instance().config