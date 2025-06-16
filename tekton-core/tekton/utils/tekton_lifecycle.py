"""
Tekton Component Lifecycle Management

This module provides a standardized component lifecycle framework for Tekton components,
handling initialization, startup, shutdown, health checking, and resource management.

Usage:
    from tekton.utils.tekton_lifecycle import (
        TektonLifecycle,
        lifecycle_manager,
        startup_handler
    )
    
    # Class-based approach
    class MyComponent(TektonLifecycle):
        async def initialize(self):
            # Initialize resources
            pass
            
        async def start(self):
            # Start the component
            pass
            
        async def stop(self):
            # Stop the component
            pass
            
    # Function-based approach with decorators
    @startup_handler
    async def start_component():
        # Start the component
        pass
    
    @lifecycle_manager
    async def run_component():
        # Run the component
        pass
"""

import os
import sys
import asyncio
import logging
import signal
import time
import atexit
import functools
import traceback
from enum import Enum
from typing import Dict, Any, Optional, List, Union, Callable, Tuple, TypeVar, Type, cast
from datetime import datetime, timedelta

# Import Tekton utilities
from .tekton_errors import (
    TektonError,
    InitializationError,
    LifecycleError,
    ShutdownError
)
from .tekton_logging import get_logger
from .tekton_registration import TektonComponent, ComponentStatus

# Set up logger
logger = logging.getLogger(__name__)

# Type variables for generic functions
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


class LifecycleState(Enum):
    """Component lifecycle states."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class LifecycleEvent(Enum):
    """Component lifecycle events."""
    INITIALIZE = "initialize"
    INITIALIZATION_COMPLETED = "initialization_completed"
    INITIALIZATION_FAILED = "initialization_failed"
    START = "start"
    START_COMPLETED = "start_completed"
    START_FAILED = "start_failed"
    STOP = "stop"
    STOP_COMPLETED = "stop_completed"
    STOP_FAILED = "stop_failed"
    ERROR = "error"
    HEALTH_CHECK = "health_check"
    HEALTH_CHECK_FAILED = "health_check_failed"
    SHUTDOWN = "shutdown"


class TektonLifecycle:
    """
    Base class for Tekton components with lifecycle management.
    
    This class provides a standardized interface for component initialization,
    startup, shutdown, and health checking.
    """
    
    def __init__(
        self,
        component_id: str,
        component_name: Optional[str] = None,
        component_type: Optional[str] = None,
        version: str = "1.0.0",
        description: Optional[str] = None,
        hermes_registration: bool = True,
        auto_start: bool = False
    ):
        """
        Initialize a Tekton component with lifecycle management.
        
        Args:
            component_id: Component identifier
            component_name: Human-readable name (defaults to component_id)
            component_type: Component type (defaults to component_id)
            version: Component version
            description: Component description
            hermes_registration: Whether to register with Hermes
            auto_start: Whether to automatically start on initialization
        """
        self.component_id = component_id
        self.component_name = component_name or component_id.capitalize()
        self.component_type = component_type or component_id
        self.version = version
        self.description = description or f"{self.component_name} component"
        self.hermes_registration = hermes_registration
        self.auto_start = auto_start
        
        # Lifecycle state
        self.state = LifecycleState.UNINITIALIZED
        self.error: Optional[Exception] = None
        self.start_time: Optional[datetime] = None
        self.stop_time: Optional[datetime] = None
        
        # Component registration
        self.hermes_component: Optional[TektonComponent] = None
        
        # Event handlers
        self.event_handlers: Dict[LifecycleEvent, List[Callable]] = {
            event: [] for event in LifecycleEvent
        }
        
        # Resource tracking
        self.resources: List[Tuple[Any, str]] = []
        self.tasks: List[asyncio.Task] = []
        self.shutdown_event = asyncio.Event()
        
        # Health check
        self.health_check_interval = 60  # seconds
        self.health_check_task: Optional[asyncio.Task] = None
        
        # Logger
        self.logger = get_logger(f"tekton.{component_id}")
    
    async def initialize(self) -> bool:
        """
        Initialize the component.
        
        This method should be overridden by subclasses to implement
        component-specific initialization.
        
        Returns:
            True if initialization was successful
        """
        # Default implementation does nothing
        return True
    
    async def start(self) -> bool:
        """
        Start the component.
        
        This method should be overridden by subclasses to implement
        component-specific startup.
        
        Returns:
            True if startup was successful
        """
        # Default implementation does nothing
        return True
    
    async def stop(self) -> bool:
        """
        Stop the component.
        
        This method should be overridden by subclasses to implement
        component-specific shutdown.
        
        Returns:
            True if shutdown was successful
        """
        # Default implementation does nothing
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check component health.
        
        This method should be overridden by subclasses to implement
        component-specific health checks.
        
        Returns:
            Health status information
        """
        # Default health check
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
            
        return {
            "component_id": self.component_id,
            "status": self.state.value,
            "uptime_seconds": uptime,
            "version": self.version,
            "error": str(self.error) if self.error else None
        }
    
    async def lifecycle_initialize(self) -> bool:
        """
        Initialize the component's lifecycle.
        
        This method sets up the component's lifecycle, including registration
        with Hermes if enabled.
        
        Returns:
            True if initialization was successful
        """
        if self.state != LifecycleState.UNINITIALIZED:
            self.logger.warning(f"Component {self.component_id} already initialized")
            return self.state == LifecycleState.INITIALIZED
        
        # Update state
        self.state = LifecycleState.INITIALIZING
        self.logger.info(f"Initializing component {self.component_id}")
        
        # Trigger event
        await self._trigger_event(LifecycleEvent.INITIALIZE)
        
        try:
            # Register with Hermes if enabled
            if self.hermes_registration:
                from .tekton_registration import TektonComponent
                
                try:
                    self.hermes_component = TektonComponent(
                        component_id=self.component_id,
                        component_name=self.component_name,
                        component_type=self.component_type,
                        version=self.version,
                        description=self.description,
                        status=ComponentStatus.INITIALIZING
                    )
                    
                    # Registration will happen in start method
                except Exception as e:
                    self.logger.warning(f"Failed to create Hermes component: {e}")
            
            # Call component-specific initialization
            success = await self.initialize()
            
            if success:
                # Update state
                self.state = LifecycleState.INITIALIZED
                self.logger.info(f"Component {self.component_id} initialized successfully")
                
                # Trigger event
                await self._trigger_event(LifecycleEvent.INITIALIZATION_COMPLETED)
                
                # Auto-start if enabled
                if self.auto_start:
                    asyncio.create_task(self.lifecycle_start())
                
                return True
            else:
                # Update state
                self.state = LifecycleState.ERROR
                self.error = InitializationError(f"Component {self.component_id} initialization failed")
                self.logger.error(f"Component {self.component_id} initialization failed")
                
                # Trigger event
                await self._trigger_event(LifecycleEvent.INITIALIZATION_FAILED)
                
                return False
        
        except Exception as e:
            # Update state
            self.state = LifecycleState.ERROR
            self.error = e
            self.logger.error(f"Component {self.component_id} initialization failed: {e}")
            
            # Trigger event
            await self._trigger_event(LifecycleEvent.INITIALIZATION_FAILED)
            
            return False
    
    async def lifecycle_start(self) -> bool:
        """
        Start the component's lifecycle.
        
        This method starts the component, including registering with Hermes
        if enabled and starting health checks.
        
        Returns:
            True if startup was successful
        """
        if self.state == LifecycleState.RUNNING:
            self.logger.warning(f"Component {self.component_id} already running")
            return True
        
        if self.state == LifecycleState.UNINITIALIZED:
            # Initialize first
            success = await self.lifecycle_initialize()
            if not success:
                return False
        
        if self.state != LifecycleState.INITIALIZED:
            self.logger.error(
                f"Cannot start component {self.component_id} in state {self.state.value}"
            )
            return False
        
        # Update state
        self.state = LifecycleState.STARTING
        self.logger.info(f"Starting component {self.component_id}")
        
        # Trigger event
        await self._trigger_event(LifecycleEvent.START)
        
        try:
            # Register with Hermes if enabled
            if self.hermes_registration and self.hermes_component:
                try:
                    success = await self.hermes_component.register()
                    if not success:
                        self.logger.warning(
                            f"Failed to register component {self.component_id} with Hermes"
                        )
                    # Continue even if registration fails
                except Exception as e:
                    self.logger.warning(f"Error registering with Hermes: {e}")
            
            # Call component-specific startup
            success = await self.start()
            
            if success:
                # Update state
                self.state = LifecycleState.RUNNING
                self.start_time = datetime.now()
                self.logger.info(f"Component {self.component_id} started successfully")
                
                # Start health checks
                self._start_health_checks()
                
                # Update Hermes status if registered
                if self.hermes_registration and self.hermes_component:
                    try:
                        await self.hermes_component.update_status(ComponentStatus.READY)
                    except Exception as e:
                        self.logger.warning(f"Error updating Hermes status: {e}")
                
                # Trigger event
                await self._trigger_event(LifecycleEvent.START_COMPLETED)
                
                return True
            else:
                # Update state
                self.state = LifecycleState.ERROR
                self.error = LifecycleError(f"Component {self.component_id} startup failed")
                self.logger.error(f"Component {self.component_id} startup failed")
                
                # Update Hermes status if registered
                if self.hermes_registration and self.hermes_component:
                    try:
                        await self.hermes_component.update_status(ComponentStatus.ERROR)
                    except Exception as e:
                        self.logger.warning(f"Error updating Hermes status: {e}")
                
                # Trigger event
                await self._trigger_event(LifecycleEvent.START_FAILED)
                
                return False
        
        except Exception as e:
            # Update state
            self.state = LifecycleState.ERROR
            self.error = e
            self.logger.error(f"Component {self.component_id} startup failed: {e}")
            
            # Update Hermes status if registered
            if self.hermes_registration and self.hermes_component:
                try:
                    await self.hermes_component.update_status(ComponentStatus.ERROR)
                except Exception as hermes_error:
                    self.logger.warning(f"Error updating Hermes status: {hermes_error}")
            
            # Trigger event
            await self._trigger_event(LifecycleEvent.START_FAILED)
            
            return False
    
    async def lifecycle_stop(self) -> bool:
        """
        Stop the component's lifecycle.
        
        This method stops the component, including unregistering from Hermes
        if enabled and stopping health checks.
        
        Returns:
            True if shutdown was successful
        """
        if self.state == LifecycleState.STOPPED:
            self.logger.warning(f"Component {self.component_id} already stopped")
            return True
        
        if self.state in (LifecycleState.UNINITIALIZED, LifecycleState.INITIALIZING):
            self.logger.warning(f"Component {self.component_id} not started, nothing to stop")
            return True
        
        # Update state
        previous_state = self.state
        self.state = LifecycleState.STOPPING
        self.logger.info(f"Stopping component {self.component_id}")
        
        # Trigger event and shutdown
        await self._trigger_event(LifecycleEvent.STOP)
        self.shutdown_event.set()
        
        # Stop health checks
        self._stop_health_checks()
        
        try:
            # Update Hermes status if registered
            if self.hermes_registration and self.hermes_component:
                try:
                    await self.hermes_component.update_status(ComponentStatus.SHUTDOWN)
                except Exception as e:
                    self.logger.warning(f"Error updating Hermes status: {e}")
            
            # Call component-specific shutdown
            if previous_state in (LifecycleState.RUNNING, LifecycleState.ERROR):
                success = await self.stop()
            else:
                # Component wasn't fully started
                success = True
            
            # Stop all tasks
            await self._stop_tasks()
            
            # Close all resources
            await self._close_resources()
            
            # Unregister from Hermes if registered
            if self.hermes_registration and self.hermes_component:
                try:
                    await self.hermes_component.unregister()
                    await self.hermes_component.close()
                except Exception as e:
                    self.logger.warning(f"Error unregistering from Hermes: {e}")
            
            if success:
                # Update state
                self.state = LifecycleState.STOPPED
                self.stop_time = datetime.now()
                self.logger.info(f"Component {self.component_id} stopped successfully")
                
                # Trigger event
                await self._trigger_event(LifecycleEvent.STOP_COMPLETED)
                
                return True
            else:
                # Update state
                self.state = LifecycleState.ERROR
                self.error = ShutdownError(f"Component {self.component_id} shutdown failed")
                self.logger.error(f"Component {self.component_id} shutdown failed")
                
                # Trigger event
                await self._trigger_event(LifecycleEvent.STOP_FAILED)
                
                return False
        
        except Exception as e:
            # Update state
            self.state = LifecycleState.ERROR
            self.error = e
            self.logger.error(f"Component {self.component_id} shutdown failed: {e}")
            
            # Trigger event
            await self._trigger_event(LifecycleEvent.STOP_FAILED)
            
            return False
    
    async def _health_check_loop(self) -> None:
        """Run periodic health checks."""
        try:
            while not self.shutdown_event.is_set():
                if self.state == LifecycleState.RUNNING:
                    try:
                        # Trigger health check event
                        await self._trigger_event(LifecycleEvent.HEALTH_CHECK)
                        
                        # Run health check
                        health_info = await self.health_check()
                        self.logger.debug(f"Health check: {health_info}")
                        
                        # Update Hermes status if needed
                        if self.hermes_registration and self.hermes_component:
                            try:
                                status = ComponentStatus.READY
                                
                                # Check for degraded state
                                if health_info.get("status") == "degraded":
                                    status = ComponentStatus.DEGRADED
                                
                                await self.hermes_component.update_status(status)
                            except Exception as e:
                                self.logger.warning(f"Error updating Hermes status: {e}")
                    
                    except Exception as e:
                        self.logger.error(f"Health check failed: {e}")
                        
                        # Trigger health check failed event
                        await self._trigger_event(LifecycleEvent.HEALTH_CHECK_FAILED)
                        
                        # Update Hermes status if needed
                        if self.hermes_registration and self.hermes_component:
                            try:
                                await self.hermes_component.update_status(ComponentStatus.DEGRADED)
                            except Exception as hermes_error:
                                self.logger.warning(f"Error updating Hermes status: {hermes_error}")
                
                # Wait for next interval or shutdown
                try:
                    await asyncio.wait_for(
                        self.shutdown_event.wait(),
                        timeout=self.health_check_interval
                    )
                    return  # Shutdown event was set
                except asyncio.TimeoutError:
                    # Continue with health checks
                    pass
        
        except asyncio.CancelledError:
            # Task was cancelled, clean up
            pass
        except Exception as e:
            self.logger.error(f"Health check loop failed: {e}")
    
    def _start_health_checks(self) -> None:
        """Start the health check task."""
        if not self.health_check_task or self.health_check_task.done():
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            self.logger.debug("Health check task started")
    
    def _stop_health_checks(self) -> None:
        """Stop the health check task."""
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
            self.logger.debug("Health check task stopped")
    
    async def _stop_tasks(self) -> None:
        """Stop all tracked tasks."""
        for task in self.tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except (asyncio.CancelledError, Exception):
                    pass
        
        self.tasks.clear()
    
    async def _close_resources(self) -> None:
        """Close all tracked resources."""
        for resource, method_name in reversed(self.resources):
            try:
                close_method = getattr(resource, method_name, None)
                if close_method and callable(close_method):
                    if asyncio.iscoroutinefunction(close_method):
                        await close_method()
                    else:
                        close_method()
            except Exception as e:
                self.logger.warning(f"Error closing resource: {e}")
        
        self.resources.clear()
    
    async def _trigger_event(self, event: LifecycleEvent) -> None:
        """
        Trigger a lifecycle event.
        
        Args:
            event: Event to trigger
        """
        handlers = self.event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(self)
                else:
                    handler(self)
            except Exception as e:
                self.logger.error(f"Error in event handler for {event.value}: {e}")
    
    def add_event_handler(self, event: LifecycleEvent, handler: Callable) -> None:
        """
        Add a handler for a lifecycle event.
        
        Args:
            event: Event to handle
            handler: Handler function or coroutine
        """
        self.event_handlers.setdefault(event, []).append(handler)
    
    def remove_event_handler(self, event: LifecycleEvent, handler: Callable) -> None:
        """
        Remove a handler for a lifecycle event.
        
        Args:
            event: Event to handle
            handler: Handler function or coroutine
        """
        if event in self.event_handlers:
            self.event_handlers[event] = [
                h for h in self.event_handlers[event] if h != handler
            ]
    
    def track_resource(self, resource: Any, close_method_name: str = "close") -> Any:
        """
        Track a resource for cleanup.
        
        Args:
            resource: Resource to track
            close_method_name: Name of the method to call for cleanup
            
        Returns:
            The tracked resource
        """
        self.resources.append((resource, close_method_name))
        return resource
    
    def create_task(self, coro: Callable) -> asyncio.Task:
        """
        Create and track an asyncio task.
        
        Args:
            coro: Coroutine to run as a task
            
        Returns:
            The created task
        """
        task = asyncio.create_task(coro())
        self.tasks.append(task)
        return task
    
    def setup_signal_handlers(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        """
        Set up signal handlers for graceful shutdown.
        
        Args:
            loop: Event loop to register handlers with (uses current loop if None)
        """
        def handle_signal(sig):
            self.logger.info(f"Received signal {sig}, initiating shutdown")
            asyncio.create_task(self.lifecycle_stop())
        
        loop = loop or asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
    
    async def run(self) -> int:
        """
        Run the component.
        
        This method initializes, starts, and runs the component until it is
        stopped by a signal or error.
        
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            # Initialize and start
            if not await self.lifecycle_initialize():
                return 1
            
            if not await self.lifecycle_start():
                return 1
            
            # Set up signal handlers
            self.setup_signal_handlers()
            
            # Wait for shutdown event
            await self.shutdown_event.wait()
            
            # Stop component
            if await self.lifecycle_stop():
                return 0
            else:
                return 1
        
        except Exception as e:
            self.logger.error(f"Error running component: {e}")
            return 1


# Decorator for startup handlers
def startup_handler(func: Optional[F] = None, *, error_code: int = 1) -> F:
    """
    Decorator for component startup handlers.
    
    This decorator adds proper signal handling and error handling to
    a component's startup function.
    
    Args:
        func: Function to decorate
        error_code: Exit code to return on error
        
    Returns:
        Decorated function
    """
    def decorator(f: F) -> F:
        @functools.wraps(f)
        async def wrapper(*args: Any, **kwargs: Any) -> int:
            logger.info("Starting component...")
            
            # Set up signal handling
            loop = asyncio.get_running_loop()
            stop_event = asyncio.Event()
            
            def signal_handler():
                logger.info("Shutdown signal received")
                stop_event.set()
            
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, signal_handler)
            
            try:
                # Call the original function
                await f(*args, **kwargs)
                
                # Wait for stop event
                logger.info("Component started, waiting for shutdown signal")
                await stop_event.wait()
                
                logger.info("Component shutting down...")
                return 0
            
            except Exception as e:
                logger.error(f"Error in component: {e}")
                traceback.print_exc()
                return error_code
            
            finally:
                # Clean up signal handlers
                for sig in (signal.SIGINT, signal.SIGTERM):
                    loop.remove_signal_handler(sig)
        
        return cast(F, wrapper)
    
    if func is None:
        return decorator
    
    return decorator(func)


# Decorator for lifecycle managers
def lifecycle_manager(func: Optional[F] = None, *, cleanup: Optional[Callable] = None) -> F:
    """
    Decorator for component lifecycle managers.
    
    This decorator adds proper resource cleanup and signal handling to
    a component's lifecycle function.
    
    Args:
        func: Function to decorate
        cleanup: Optional cleanup function to call on exit
        
    Returns:
        Decorated function
    """
    def decorator(f: F) -> F:
        @functools.wraps(f)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            resources = []
            
            async def cleanup_resources():
                for resource in reversed(resources):
                    try:
                        if hasattr(resource, "close"):
                            close_method = getattr(resource, "close")
                            if asyncio.iscoroutinefunction(close_method):
                                await close_method()
                            else:
                                close_method()
                    except Exception as e:
                        logger.warning(f"Error closing resource: {e}")
            
            def track_resource(resource):
                resources.append(resource)
                return resource
            
            # Register custom cleanup
            if cleanup:
                atexit.register(cleanup)
            
            # Add resource tracking
            kwargs["track_resource"] = track_resource
            
            try:
                # Call the original function
                return await f(*args, **kwargs)
            
            finally:
                # Clean up resources
                await cleanup_resources()
                
                # Unregister custom cleanup
                if cleanup:
                    atexit.unregister(cleanup)
        
        return cast(F, wrapper)
    
    if func is None:
        return decorator
    
    return decorator(func)


# Utility functions

async def run_with_lifecycle(
    component_id: str,
    initialize_func: Callable[[], Any],
    start_func: Callable[[], Any],
    stop_func: Callable[[], Any],
    health_check_func: Optional[Callable[[], Dict[str, Any]]] = None,
    component_name: Optional[str] = None,
    component_type: Optional[str] = None,
    version: str = "1.0.0",
    description: Optional[str] = None,
    hermes_registration: bool = True
) -> int:
    """
    Run a component with lifecycle management.
    
    This function creates a TektonLifecycle instance for the component,
    using the provided functions for initialization, startup, and shutdown.
    
    Args:
        component_id: Component identifier
        initialize_func: Function for initialization
        start_func: Function for startup
        stop_func: Function for shutdown
        health_check_func: Optional function for health checking
        component_name: Human-readable name
        component_type: Component type
        version: Component version
        description: Component description
        hermes_registration: Whether to register with Hermes
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Create a lifecycle wrapper class
    class ComponentLifecycle(TektonLifecycle):
        async def initialize(self) -> bool:
            result = initialize_func()
            if asyncio.iscoroutine(result):
                return await result
            return bool(result)
        
        async def start(self) -> bool:
            result = start_func()
            if asyncio.iscoroutine(result):
                return await result
            return bool(result)
        
        async def stop(self) -> bool:
            result = stop_func()
            if asyncio.iscoroutine(result):
                return await result
            return bool(result)
        
        async def health_check(self) -> Dict[str, Any]:
            if health_check_func:
                result = health_check_func()
                if asyncio.iscoroutine(result):
                    return await result
                return result
            return await super().health_check()
    
    # Create and run the component
    component = ComponentLifecycle(
        component_id=component_id,
        component_name=component_name,
        component_type=component_type,
        version=version,
        description=description,
        hermes_registration=hermes_registration
    )
    
    return await component.run()


def get_uptime(start_time: Optional[datetime] = None) -> Optional[float]:
    """
    Get component uptime in seconds.
    
    Args:
        start_time: Component start time
        
    Returns:
        Uptime in seconds or None if not started
    """
    if start_time is None:
        return None
    
    return (datetime.now() - start_time).total_seconds()


def format_uptime(seconds: Optional[float]) -> str:
    """
    Format uptime as a human-readable string.
    
    Args:
        seconds: Uptime in seconds
        
    Returns:
        Formatted uptime string
    """
    if seconds is None:
        return "Not started"
    
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or parts:
        parts.append(f"{hours}h")
    if minutes > 0 or parts:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    
    return " ".join(parts)