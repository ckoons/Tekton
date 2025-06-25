"""
Standard base class for Tekton components.

This module provides a base class that standardizes component initialization,
registration, and lifecycle management across all Tekton components.
"""
import asyncio
import importlib
import logging
import os
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional, Type, Callable

from fastapi import FastAPI

from shared.utils.global_config import GlobalConfig
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.utils.errors import StartupError
from shared.utils.health_check import create_health_response

# Try to import landmarks decorators, but make them optional
try:
    from landmarks import architecture_decision, state_checkpoint, performance_boundary
except ImportError:
    # Create no-op decorators if landmarks module is not available
    def architecture_decision(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


@architecture_decision(
    title="Standardized component lifecycle",
    rationale="All components follow same init/startup/shutdown patterns for consistency and reliability",
    alternatives_considered=["Component-specific initialization", "Container orchestration only", "No standard base"],
    impacts=["all_components", "startup_time", "maintenance"],
    decided_by="team",
    patterns=["template_method", "dependency_injection"]
)
@state_checkpoint(
    title="Component lifecycle state",
    state_type="lifecycle",
    persistence=False,
    consistency_requirements="Sequential state transitions",
    recovery_strategy="Restart component on failure"
)
class StandardComponentBase:
    """
    Base class for standardizing Tekton component initialization.
    
    Provides:
    - Standard startup sequence
    - Hermes registration
    - Health check implementation  
    - Graceful shutdown
    - Common service initialization
    - MCP bridge initialization
    """
    
    def __init__(self, component_name: str, version: str):
        """
        Initialize base component.
        
        Args:
            component_name: Name of the component (e.g., 'prometheus', 'apollo')
            version: Component version string
        """
        self.component_name = component_name
        self.version = version
        self.global_config = GlobalConfig.get_instance()
        self.config = self.global_config.get_component_config(component_name)
        self.logger = logging.getLogger(component_name)
        self.data_dir = None
        
    async def initialize(self, 
                        capabilities: List[str], 
                        metadata: Optional[Dict[str, Any]] = None):
        """
        Standard initialization sequence for all components.
        
        Args:
            capabilities: List of component capabilities
            metadata: Optional metadata for Hermes registration
        """
        try:
            self.logger.info(f"Initializing {self.component_name} v{self.version}")
            
            # 1. Setup logging
            setup_component_logging(self.component_name)
            
            # 2. Initialize data directories
            self.data_dir = self.global_config.get_data_dir(self.component_name)
            self.logger.debug(f"Data directory: {self.data_dir}")
            
            # 3. Component-specific pre-initialization
            await self._pre_init()
            
            # 4. Register with Hermes
            await self._register_with_hermes(capabilities, metadata)
            
            # 5. Initialize shared services (if needed)
            await self._initialize_services()
            
            # 6. Initialize MCP bridge (if needed)
            await self._initialize_mcp()
            
            # 7. Component-specific initialization
            await self._component_specific_init()
            
            self.logger.info(f"{self.component_name} initialization complete")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.component_name}: {e}")
            raise StartupError(f"Component initialization failed: {e}", self.component_name)
    
    async def _pre_init(self):
        """Pre-initialization hook - override if needed."""
        pass
    
    async def _register_with_hermes(self, capabilities: List[str], metadata: Optional[Dict[str, Any]]):
        """
        Standard Hermes registration process.
        
        Args:
            capabilities: List of component capabilities
            metadata: Optional metadata for registration
        """
        self.logger.debug("Registering with Hermes")
        
        self.global_config.hermes_registration = HermesRegistration()
        
        # Prepare metadata
        registration_metadata = metadata or {}
        registration_metadata.update({
            'data_dir': self.data_dir,
            'uptime': self.global_config.uptime,
        })
        
        # Register
        self.global_config.is_registered_with_hermes = await self.global_config.hermes_registration.register_component(
            component_name=self.component_name,
            port=self.config.port,
            version=self.version,
            capabilities=capabilities,
            metadata=registration_metadata
        )
        
        if self.global_config.is_registered_with_hermes:
            self.logger.info("Successfully registered with Hermes")
            # Start heartbeat
            self.global_config.heartbeat_task = asyncio.create_task(
                heartbeat_loop(self.global_config.hermes_registration, self.component_name)
            )
        else:
            self.logger.warning("Failed to register with Hermes - continuing in standalone mode")
    
    async def _initialize_services(self):
        """
        Initialize common services needed by this component.
        Override in subclass to initialize specific services.
        
        Example:
            rhetor_url = self.global_config.get_service_url('rhetor')
            self.global_config.set_service('llm_client',
                TektonLLMClient(base_url=rhetor_url))
        """
        pass
    
    async def _initialize_mcp(self):
        """
        Initialize MCP bridge if needed.
        Override in subclass if component uses MCP.
        """
        if not self.global_config.mcp_enabled:
            self.logger.debug("MCP is disabled system-wide")
            return
            
        # Override this method and call _initialize_mcp_bridge with appropriate params
        pass
    
    async def _initialize_mcp_bridge(self, bridge_class_path: str, **kwargs):
        """
        Standard MCP bridge initialization helper.
        
        Args:
            bridge_class_path: Full path to bridge class (e.g., 'apollo.api.mcp_bridge.ApolloMCPBridge')
            **kwargs: Additional arguments for bridge initialization
        """
        try:
            # Import bridge class dynamically
            module_path, class_name = bridge_class_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            bridge_class = getattr(module, class_name)
            
            # Initialize with standard params + component-specific kwargs
            self.global_config.mcp_bridge = bridge_class(
                component_name=self.component_name,
                **kwargs
            )
            
            self.logger.info("MCP bridge initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP bridge: {e}")
            raise
    
    async def _component_specific_init(self):
        """
        Component-specific initialization.
        Override in subclass to add component-specific initialization.
        """
        pass
    
    async def shutdown(self):
        """Standard shutdown sequence for all components."""
        self.logger.info(f"Shutting down {self.component_name}")
        
        try:
            # 1. Component-specific cleanup first
            await self._component_specific_cleanup()
            
            # 2. Cancel heartbeat
            if self.global_config.heartbeat_task:
                self.global_config.heartbeat_task.cancel()
                try:
                    await self.global_config.heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            # 3. Deregister from Hermes
            if self.global_config.hermes_registration and self.global_config.is_registered_with_hermes:
                # Fix: Use correct method name 'deregister' instead of 'deregister_component'
                await self.global_config.hermes_registration.deregister(self.component_name)
                self.logger.info("Deregistered from Hermes")
            
            # 4. Cleanup MCP bridge
            if self.global_config.mcp_bridge:
                if hasattr(self.global_config.mcp_bridge, 'cleanup'):
                    await self.global_config.mcp_bridge.cleanup()
            
            # 5. Clear runtime state
            self.global_config.clear_runtime_state()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    async def _component_specific_cleanup(self):
        """
        Component-specific cleanup.
        Override in subclass to add component-specific cleanup.
        """
        pass
    
    def create_app(self, 
                   title: Optional[str] = None,
                   description: Optional[str] = None,
                   startup_callback: Optional[Callable] = None,
                   **fastapi_kwargs) -> FastAPI:
        """
        Create standard FastAPI app with lifespan management.
        
        Args:
            title: Optional API title (defaults to component name)
            description: Optional API description
            **fastapi_kwargs: Additional kwargs for FastAPI
            
        Returns:
            Configured FastAPI application
        """
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Store reference in app.state
            app.state.component = self
            app.state.global_config = self.global_config
            
            # Startup - call the callback if provided
            if startup_callback:
                await startup_callback()
            
            yield
            
            # Shutdown
            await self.shutdown()
        
        # Extract any conflicting params from kwargs
        final_kwargs = fastapi_kwargs.copy()
        
        # Use provided values or fallback to kwargs or defaults
        final_title = title or final_kwargs.pop('title', f"{self.component_name.title()} API")
        final_version = final_kwargs.pop('version', self.version)
        final_description = description or final_kwargs.pop('description', None)
        
        app = FastAPI(
            title=final_title,
            version=final_version,
            description=final_description,
            lifespan=lifespan,
            **final_kwargs
        )
        
        # Add CORS middleware (standard for all components)
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        return app
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status for this component.
        Override to add component-specific health checks.
        
        Returns:
            Health status dictionary
        """
        # Get component-specific health info
        component_health = self._get_component_health() or {}
        
        # Build details dict
        details = {
            "uptime": self.global_config.uptime,
            **component_health
        }
        
        # Use create_health_response with correct parameters
        health_response = create_health_response(
            component_name=self.component_name,
            port=self.config.port,
            version=self.version,
            status="healthy",  # Can be overridden based on component health
            registered=self.global_config.is_registered_with_hermes,
            details=details
        )
        
        # Convert to dict for JSON response
        return health_response.model_dump()
    
    def _get_component_health(self) -> Optional[Dict[str, Any]]:
        """
        Get component-specific health information.
        Override in subclass to add custom health checks.
        
        Returns:
            Dictionary of health information or None
        """
        return None