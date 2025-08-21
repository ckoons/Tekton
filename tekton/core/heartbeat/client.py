#!/usr/bin/env python3
"""
Heartbeat Client Module

This module provides a simplified interface for components to manage
their connection to Hermes, including heartbeats and health metrics.
"""

import asyncio
import logging
import os
from shared.env import TektonEnviron
import signal
import time
from typing import Dict, List, Any, Optional, Callable

from ..lifecycle import ComponentRegistration, ComponentState
from .monitor import HeartbeatMonitor

logger = logging.getLogger(__name__)


class ComponentHeartbeat:
    """
    Simplified interface for component heartbeat management.
    
    This class provides a simplified interface for components to manage
    their connection to Hermes, including automatic reconnection and
    health metrics reporting.
    """
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                component_type: str = "service",
                hermes_url: Optional[str] = None,
                heartbeat_interval: Optional[int] = None,
                capabilities: Optional[List[Dict[str, Any]]] = None,
                metadata: Optional[Dict[str, Any]] = None,
                enable_metrics: bool = True):
        """
        Initialize the component heartbeat.
        
        Args:
            component_id: ID of the component
            component_name: Name of the component
            component_type: Type of component (api, service, worker, database, etc.)
            hermes_url: URL of the Hermes API
            heartbeat_interval: Optional custom heartbeat interval in seconds
            capabilities: Component capabilities
            metadata: Component metadata
            enable_metrics: Whether to enable metrics collection
        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type
        self.hermes_url = hermes_url or TektonEnviron.get("HERMES_URL", "http://localhost:5000/api")
        self.heartbeat_interval = heartbeat_interval
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        self.enable_metrics = enable_metrics
        
        # Internal state
        self.monitor = None
        self.registration = None
        self.metrics_providers = []
        self.state = "initializing"
        self.custom_metrics = {}
        self.start_time = time.time()
        
    async def start(self) -> bool:
        """
        Start the heartbeat monitor with enhanced metrics collection.
        
        Returns:
            True if successful
        """
        try:
            # Create registration
            self.registration = ComponentRegistration(
                component_id=self.component_id,
                component_name=self.component_name,
                component_type=self.component_type,
                hermes_url=self.hermes_url,
                capabilities=self.capabilities,
                metadata=self.metadata
            )
            
            # Register with Hermes
            result = await self.registration.register()
            
            if not result:
                logger.error(f"Failed to register {self.component_id} with Hermes")
                return False
            
            # Create and start monitor with configuration
            self.monitor = HeartbeatMonitor(
                hermes_url=self.hermes_url,
                collect_metrics=self.enable_metrics,
                stagger_heartbeats=True
            )
            
            # Register component with custom interval if specified
            self.monitor.register_component(self.registration)
            if self.heartbeat_interval:
                self.monitor.set_component_interval(self.component_id, self.heartbeat_interval)
                
            # Start the monitor
            await self.monitor.start()
            
            # Set up signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            # Set initial state
            self.state = "ready"
            
            logger.info(f"Started heartbeat monitoring for {self.component_id} (type: {self.component_type})")
            return True
            
        except Exception as e:
            logger.exception(f"Error starting heartbeat for {self.component_id}: {e}")
            return False
            
    def set_state(self, new_state: str, reason: str = None, details: str = None) -> bool:
        """
        Update the component state.
        
        Args:
            new_state: New state to transition to
            reason: Reason code for the state change
            details: Additional details about the state change
            
        Returns:
            True if state was updated successfully
        """
        if not self.registration:
            logger.warning(f"Cannot update state for {self.component_id} - not registered")
            return False
            
        # Update internal state
        self.state = new_state
        
        # Update registration state with reason and details
        result = self.registration.update_state(new_state, reason, details)
        
        if result:
            logger.info(f"Updated {self.component_id} state to {new_state} ({reason or 'manual update'})")
        else:
            logger.warning(f"Invalid state transition for {self.component_id}: {self.registration.state} -> {new_state}")
            
        return result
        
    def add_metrics_provider(self, provider_func: Callable[[], Dict[str, float]]) -> None:
        """
        Add a function that provides health metrics.
        
        Args:
            provider_func: Function that returns a dictionary of metrics
        """
        self.metrics_providers.append(provider_func)
        logger.debug(f"Added metrics provider for {self.component_id}")
        
    def update_custom_metrics(self, metrics: Dict[str, float]) -> None:
        """
        Update custom metrics that will be included in heartbeats.
        
        Args:
            metrics: Dictionary of custom metrics
        """
        self.custom_metrics.update(metrics)
        
    async def collect_metrics(self) -> Dict[str, float]:
        """
        Collect all metrics from providers and custom metrics.
        
        Returns:
            Dictionary of metrics
        """
        metrics = {}
        
        # Add built-in metrics
        metrics["uptime"] = time.time() - self.start_time
        
        # Collect metrics from all providers
        for provider in self.metrics_providers:
            try:
                if asyncio.iscoroutinefunction(provider):
                    provider_metrics = await provider()
                else:
                    provider_metrics = provider()
                    
                if provider_metrics:
                    metrics.update(provider_metrics)
            except Exception as e:
                logger.error(f"Error collecting metrics from provider: {e}")
                
        # Add custom metrics
        metrics.update(self.custom_metrics)
        
        return metrics
    
    async def stop(self) -> None:
        """Stop the heartbeat monitor."""
        if self.monitor:
            await self.monitor.stop()
            self.monitor = None
            
        if self.registration:
            await self.registration.unregister()
            self.registration = None
            
        logger.info(f"Stopped heartbeat monitoring for {self.component_id}")
    
    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self._shutdown(s))
            )
    
    async def _shutdown(self, sig: signal.Signals) -> None:
        """
        Handle shutdown signal.
        
        Args:
            sig: Signal that triggered shutdown
        """
        logger.info(f"Received signal {sig.name}, shutting down")
        await self.stop()
        
        # Exit after a short delay to allow clean shutdown
        loop = asyncio.get_event_loop()
        loop.stop()