#!/usr/bin/env python3
"""
Component Health Adapter Module

Main adapter that integrates component health with metrics, logging, and monitoring.
"""

import os
import time
import json
import asyncio
import uuid
from typing import Dict, List, Any, Optional, Callable, Union, Set

from ...logging_integration import get_logger, LogCategory, LogLevel
from ...metrics_integration import get_metrics_manager, MetricCategory, MetricUnit
from ...monitoring_dashboard import get_dashboard, HealthStatus, Alert, AlertSeverity
from ...lifecycle import ComponentState
from ...graceful_degradation import CircuitBreaker, NoFallbackAvailableError

from .state_manager import StateManager
from .metrics_manager import MetricsManager
from .task_manager import TaskManager
from .logging_manager import LoggingManager
from .capability_manager import CapabilityManager


class ComponentHealthAdapter:
    """
    Adapter that integrates component health with metrics, logging, and monitoring.
    
    This class provides a unified interface for managing component health,
    metrics, and logging, and reporting health status to the monitoring dashboard.
    """
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                component_type: str,
                version: str = "0.1.0",
                hermes_url: Optional[str] = None):
        """
        Initialize component health adapter.
        
        Args:
            component_id: Component ID
            component_name: Human-readable name
            component_type: Type of component
            version: Component version
            hermes_url: Optional URL of Hermes service
        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type
        self.version = version
        self.hermes_url = hermes_url
        self.instance_id = str(uuid.uuid4())
        self.start_time = time.time()
        
        # Get logger
        self.logger = get_logger(component_id)
        
        # Get metrics manager
        self.metrics_mgr = get_metrics_manager(component_id)
        
        # Get dashboard
        self.dashboard = get_dashboard()
        
        # Create component managers
        self.state_manager = StateManager(
            component_id=component_id,
            component_name=component_name,
            component_type=component_type,
            metrics_manager=self.metrics_mgr,
            logger=self.logger,
            dashboard=self.dashboard
        )
        
        self.metrics_manager = MetricsManager(
            component_id=component_id,
            metrics_manager=self.metrics_mgr,
            state_manager=self.state_manager
        )
        
        self.task_manager = TaskManager(
            component_id=component_id,
            metrics_manager=self.metrics_manager,
            logger=self.logger
        )
        
        self.logging_manager = LoggingManager(
            logger=self.logger,
            metrics_manager=self.metrics_manager
        )
        
        self.capability_manager = CapabilityManager(
            logger=self.logger
        )
        
    async def start(self) -> bool:
        """
        Start the component health adapter.
        
        Returns:
            True if successful
        """
        # Start metrics reporting
        await self.metrics_mgr.start()
        
        # Start dashboard
        await self.dashboard.start()
        
        # Log startup
        self.logger.info(
            f"Component {self.component_name} starting",
            category=LogCategory.STARTUP,
            context={
                "component_type": self.component_type,
                "version": self.version,
                "instance_id": self.instance_id
            }
        )
        
        # Initialize state
        self.state_manager.state = ComponentState.INITIALIZING.value
        
        return True
        
    async def stop(self) -> None:
        """Stop the component health adapter."""
        # Update state
        old_state = self.state_manager.state
        self.state_manager.state = ComponentState.STOPPING.value
        
        # Log shutdown
        self.logger.info(
            f"Component {self.component_name} stopping",
            category=LogCategory.SHUTDOWN,
            context={
                "component_type": self.component_type,
                "version": self.version,
                "instance_id": self.instance_id,
                "uptime": time.time() - self.start_time,
                "previous_state": old_state
            }
        )
        
        # Shutdown tasks
        await self.task_manager.shutdown_tasks()
        
        # Stop metrics reporting
        await self.metrics_mgr.stop()
        
    # State Management
    
    @property
    def state(self) -> str:
        """Get current component state."""
        return self.state_manager.state
        
    def update_state(self, new_state: str, reason: str = None, details: str = None) -> bool:
        """
        Update component state.
        
        Args:
            new_state: New state
            reason: Optional reason for state change
            details: Optional details about state change
            
        Returns:
            True if state was updated
        """
        return self.state_manager.update_state(new_state, reason, details)
        
    # Capability Management
    
    def add_dependency(self, dependency_id: str) -> None:
        """
        Add a dependency for the component.
        
        Args:
            dependency_id: Dependency component ID
        """
        self.capability_manager.add_dependency(dependency_id)
        
    def register_capability(self, 
                         capability_name: str,
                         handler: Callable,
                         level: int = 100,
                         description: str = None) -> None:
        """
        Register a capability for the component.
        
        Args:
            capability_name: Capability name
            handler: Handler function
            level: Capability level (higher is better)
            description: Optional description
        """
        self.capability_manager.register_capability(
            capability_name=capability_name,
            handler=handler,
            level=level,
            description=description
        )
        
    # Metrics Management
    
    def update_metrics(self, metrics: Dict[str, float]) -> None:
        """
        Update component metrics.
        
        Args:
            metrics: Dictionary of metric name to value
        """
        self.metrics_manager.update_metrics(metrics)
        
    # Task Management
    
    def run_task(self, coro, *args, **kwargs) -> asyncio.Task:
        """
        Run a coroutine as a task and track it.
        
        Args:
            coro: Coroutine to run
            *args: Arguments for coroutine
            **kwargs: Keyword arguments for coroutine
            
        Returns:
            Task object
        """
        return self.task_manager.run_task(coro, *args, **kwargs)
        
    async def call_with_timeout(self, 
                           func: Callable, 
                           *args, 
                           timeout: float = 10.0, 
                           fallback: Optional[Callable] = None, 
                           **kwargs) -> Any:
        """
        Call a function with timeout and optional fallback.
        
        Args:
            func: Function to call
            *args: Arguments for function
            timeout: Timeout in seconds
            fallback: Optional fallback function
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
            
        Raises:
            asyncio.TimeoutError: If the function times out and no fallback is provided
        """
        return await self.task_manager.call_with_timeout(
            func=func,
            *args,
            timeout=timeout,
            fallback=fallback,
            **kwargs
        )
        
    def create_circuit_breaker(self, 
                           name: str, 
                           failure_threshold: int = 5,
                           recovery_timeout: float = 30.0) -> CircuitBreaker:
        """
        Create a circuit breaker for a operation.
        
        Args:
            name: Circuit breaker name
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time in seconds before trying recovery
            
        Returns:
            Circuit breaker
        """
        return self.task_manager.create_circuit_breaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
        
    # Logging Management
    
    def log_request(self, 
                  endpoint: str, 
                  method: str, 
                  status_code: int, 
                  duration: float,
                  request_id: Optional[str] = None,
                  correlation_id: Optional[str] = None,
                  context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a request.
        
        Args:
            endpoint: Request endpoint
            method: HTTP method
            status_code: HTTP status code
            duration: Request duration in seconds
            request_id: Optional request ID
            correlation_id: Optional correlation ID
            context: Optional additional context
        """
        self.logging_manager.log_request(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration=duration,
            request_id=request_id,
            correlation_id=correlation_id,
            context=context
        )