#!/usr/bin/env python3
"""
Heartbeat Monitor Module

This module provides the core heartbeat monitoring functionality
for tracking component health and managing reconnection.
"""

import asyncio
import logging
import os
from shared.env import TektonEnviron
import time
from typing import Dict, Any, Optional, Set, List

from ..lifecycle import ComponentRegistration
from .metrics import collect_component_metrics, aggregate_health_metrics
from .component_state import ComponentHealthMetrics

# Configure logging
logger = logging.getLogger(__name__)


class HeartbeatMonitor:
    """
    Monitors the connection to Hermes and handles reconnection.
    
    This class maintains heartbeats to Hermes and automatically
    re-registers components if Hermes restarts or becomes unavailable.
    Enhanced with configurable heartbeat intervals and metrics collection.
    """
    
    def __init__(self, 
                hermes_url: Optional[str] = None,
                default_interval: int = 5,
                retry_interval: int = 5,
                max_retries: int = -1,
                collect_metrics: bool = True,
                stagger_heartbeats: bool = True):  # -1 means infinite retries
        """
        Initialize the heartbeat monitor.
        
        Args:
            hermes_url: URL of the Hermes API
            default_interval: Default heartbeat interval in seconds
            retry_interval: Interval between retries in seconds
            max_retries: Maximum number of retries (-1 for infinite)
            collect_metrics: Whether to collect health metrics
            stagger_heartbeats: Whether to stagger heartbeats to prevent thundering herd
        """
        self.hermes_url = hermes_url or TektonEnviron.get("HERMES_URL", "http://localhost:5000/api")
        self.default_interval = default_interval
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.collect_metrics = collect_metrics
        self.stagger_heartbeats = stagger_heartbeats
        
        # Component registrations and settings
        self.registrations: Dict[str, ComponentRegistration] = {}
        self.component_intervals: Dict[str, float] = {}  # Customizable intervals by component
        self.component_health: Dict[str, Dict[str, Any]] = {}  # Health tracking by component
        
        # Active tasks
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}
        self.metrics_task = None
        self.running = False
        self.active_task = None
        
        # Type-specific intervals
        self.type_intervals = {
            "database": 3,    # More frequent for critical services
            "api": 5,         # Standard interval
            "worker": 10,     # Less frequent for background workers
            "ui": 15          # Least frequent for UI components
        }
        
        # Metric collection configuration
        self.metrics_collection_interval = 15  # seconds
        
    def register_component(self, registration: ComponentRegistration) -> None:
        """
        Register a component with the monitor.
        
        Args:
            registration: ComponentRegistration instance
        """
        component_id = registration.component_id
        self.registrations[component_id] = registration
        logger.info(f"Added component {component_id} to heartbeat monitor")
        
        # Start heartbeat task if monitor is running
        if self.running and component_id not in self.heartbeat_tasks:
            self.heartbeat_tasks[component_id] = asyncio.create_task(
                self._component_heartbeat_loop(component_id)
            )
    
    def unregister_component(self, component_id: str) -> None:
        """
        Unregister a component from the monitor.
        
        Args:
            component_id: ID of the component to unregister
        """
        if component_id in self.registrations:
            del self.registrations[component_id]
            
            # Cancel heartbeat task if it exists
            if component_id in self.heartbeat_tasks:
                self.heartbeat_tasks[component_id].cancel()
                del self.heartbeat_tasks[component_id]
                
            logger.info(f"Removed component {component_id} from heartbeat monitor")
    
    async def start(self) -> None:
        """Start the heartbeat monitor with enhanced metrics collection."""
        if self.running:
            logger.warning("Heartbeat monitor already running")
            return
            
        self.running = True
        logger.info("Starting heartbeat monitor")
        
        # Start heartbeat tasks for registered components
        for component_id in self.registrations:
            if component_id not in self.heartbeat_tasks:
                self.heartbeat_tasks[component_id] = asyncio.create_task(
                    self._component_heartbeat_loop(component_id)
                )
        
        # Start the main monitoring task
        self.active_task = asyncio.create_task(self._monitor_loop())
        
        # Start metrics collection task if enabled
        if self.collect_metrics:
            self.metrics_task = asyncio.create_task(self._metrics_collection_loop())
            logger.info(f"Started metrics collection task (interval: {self.metrics_collection_interval}s)")
    
    async def stop(self) -> None:
        """Stop the heartbeat monitor."""
        if not self.running:
            return
            
        self.running = False
        logger.info("Stopping heartbeat monitor")
        
        # Cancel all heartbeat tasks
        for component_id, task in self.heartbeat_tasks.items():
            task.cancel()
            
        self.heartbeat_tasks.clear()
        
        # Cancel the main monitoring task
        if self.active_task:
            self.active_task.cancel()
            self.active_task = None
            
        # Cancel metrics collection task
        if self.metrics_task:
            self.metrics_task.cancel()
            self.metrics_task = None
            
    async def _metrics_collection_loop(self) -> None:
        """Collect and aggregate metrics for all components on a regular interval."""
        try:
            while self.running:
                try:
                    # Get all component health metrics
                    metrics = aggregate_health_metrics(self.component_health, self.registrations)
                    
                    # Log metrics summary if there are components
                    if metrics["total_components"] > 0:
                        logger.debug(f"Collected metrics for {metrics['total_components']} components: "
                                    f"CPU: {metrics['avg_cpu_usage']:.1%}, "
                                    f"Memory: {metrics['avg_memory_usage']:.1%}, "
                                    f"Latency: {metrics['avg_request_latency']:.1f}ms, "
                                    f"Error rate: {metrics['avg_error_rate']:.2%}")
                    
                    # Check for degraded components
                    for component_id, stats in metrics.get("components", {}).items():
                        if stats.get("needs_attention", False):
                            logger.warning(f"Component {component_id} needs attention: {stats.get('reason', 'unknown reason')}")
                            
                            # Attempt recovery for degraded components
                            if stats.get("state") in ["degraded", "error", "failed"] and self._should_auto_recover(component_id):
                                # Trigger recovery attempt
                                asyncio.create_task(self._attempt_component_recovery(component_id))
                    
                except Exception as e:
                    logger.error(f"Error in metrics collection: {e}")
                
                # Wait for next collection
                await asyncio.sleep(self.metrics_collection_interval)
                
        except asyncio.CancelledError:
            logger.info("Metrics collection task cancelled")
    
    def _should_auto_recover(self, component_id: str) -> bool:
        """
        Determine if a component should be automatically recovered.
        
        Args:
            component_id: Component ID
            
        Returns:
            True if component should be auto-recovered
        """
        if component_id not in self.registrations:
            return False
            
        component = self.registrations[component_id]
        
        # Don't try to recover if too many attempts already
        if component.recovery_attempts >= 3:
            return False
            
        # Don't try to recover if last attempt was too recent (within 5 minutes)
        if component.last_recovery_time > 0 and time.time() - component.last_recovery_time < 300:
            return False
            
        # Check component type - only auto-recover certain types
        auto_recover_types = ["api", "worker", "service"]
        if component.component_type not in auto_recover_types:
            return False
            
        return True
        
    async def _attempt_component_recovery(self, component_id: str) -> bool:
        """
        Attempt to recover a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            True if recovery was initiated
        """
        if component_id not in self.registrations:
            return False
            
        component = self.registrations[component_id]
        
        # Record recovery attempt
        recovery_count = component.record_recovery_attempt()
        logger.warning(f"Attempting auto-recovery for component {component_id} (attempt {recovery_count})")
        
        # Attempt to reconnect
        success = await self._reconnect_component(component_id)
        
        return success
        
    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        try:
            while self.running:
                try:
                    # Check if Hermes is available
                    hermes_available = await self._check_hermes_availability()
                    
                    if not hermes_available:
                        logger.warning("Hermes appears to be unavailable, will attempt to reconnect components")
                        await self._reconnect_all_components()
                    
                    # Wait before next check
                    await asyncio.sleep(self.retry_interval * 2)
                    
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.error(f"Error in monitor loop: {e}")
                    await asyncio.sleep(self.retry_interval)
                    
        except asyncio.CancelledError:
            logger.info("Monitor loop cancelled")
    
    async def _component_heartbeat_loop(self, component_id: str) -> None:
        """
        Heartbeat loop for a specific component with configurable intervals and metrics.
        
        Args:
            component_id: ID of the component
        """
        retries = 0
        consecutive_failures = 0
        
        try:
            # Apply staggered start if enabled
            if self.stagger_heartbeats:
                # Use component_id hash to create a staggered start time within the interval
                component_hash = hash(component_id) % 1000 / 1000.0
                stagger_time = self._get_heartbeat_interval(component_id) * component_hash
                logger.debug(f"Staggering heartbeat start for {component_id} by {stagger_time:.2f} seconds")
                await asyncio.sleep(stagger_time)
            
            while self.running and (self.max_retries < 0 or retries < self.max_retries):
                if component_id not in self.registrations:
                    logger.warning(f"Component {component_id} no longer registered, stopping heartbeat")
                    return
                    
                registration = self.registrations[component_id]
                
                # Collect health metrics if enabled
                health_metrics = None
                if self.collect_metrics:
                    health_metrics = await collect_component_metrics(component_id, registration.component_type)
                
                try:
                    # Generate heartbeat sequence number
                    registration.heartbeat_sequence += 1
                    sequence = registration.heartbeat_sequence
                    
                    # Determine component state for heartbeat
                    state = registration.state
                    
                    # Prepare heartbeat payload
                    heartbeat_data = {
                        "component": component_id,
                        "instance_uuid": registration.instance_uuid,
                        "sequence": sequence,
                        "state": state,
                        "timestamp": time.time()
                    }
                    
                    # Add health metrics if available
                    if health_metrics:
                        heartbeat_data["health_metrics"] = health_metrics
                        
                    # Add basic metadata
                    heartbeat_data["metadata"] = {
                        "component_type": registration.component_type,
                        "version": registration.version,
                        "uptime": time.time() - registration.start_time,
                        "interval": self._get_heartbeat_interval(component_id)
                    }
                    
                    # Send heartbeat
                    import aiohttp
                    
                    heartbeat_start = time.time()
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{self.hermes_url}/registration/heartbeat",
                            json=heartbeat_data,
                            timeout=3  # Add timeout to prevent blocking
                        ) as response:
                            if response.status == 200:
                                # Track latency
                                latency = time.time() - heartbeat_start
                                if component_id in self.component_health:
                                    self.component_health[component_id]["latency"] = latency
                                
                                logger.debug(f"Sent heartbeat #{sequence} for {component_id} (latency: {latency:.3f}s)")
                                consecutive_failures = 0
                            else:
                                error = await response.text()
                                logger.warning(f"Failed to send heartbeat for {component_id}: {error}")
                                consecutive_failures += 1
                                
                                # Update health info
                                if component_id in self.component_health:
                                    self.component_health[component_id]["last_error"] = error
                                    self.component_health[component_id]["last_error_time"] = time.time()
                                
                                # If multiple consecutive failures, try to re-register
                                if consecutive_failures >= 3:
                                    logger.warning(f"Multiple heartbeat failures for {component_id}, attempting to re-register")
                                    await self._reconnect_component(component_id)
                                    consecutive_failures = 0
                
                except asyncio.CancelledError:
                    raise
                except asyncio.TimeoutError:
                    logger.warning(f"Heartbeat request timeout for {component_id}")
                    consecutive_failures += 1
                    
                    # Update health info
                    if component_id in self.component_health:
                        self.component_health[component_id]["last_error"] = "Request timeout"
                        self.component_health[component_id]["last_error_time"] = time.time()
                    
                    # If multiple consecutive timeouts, try to re-register
                    if consecutive_failures >= 3:
                        logger.warning(f"Multiple heartbeat timeouts for {component_id}, attempting to re-register")
                        await self._reconnect_component(component_id)
                        consecutive_failures = 0
                
                except Exception as e:
                    logger.warning(f"Error sending heartbeat for {component_id}: {e}")
                    consecutive_failures += 1
                    
                    # Update health info
                    if component_id in self.component_health:
                        self.component_health[component_id]["last_error"] = str(e)
                        self.component_health[component_id]["last_error_time"] = time.time()
                    
                    # If multiple consecutive failures, try to re-register
                    if consecutive_failures >= 3:
                        logger.warning(f"Multiple heartbeat failures for {component_id}, attempting to re-register")
                        await self._reconnect_component(component_id)
                        consecutive_failures = 0
                
                # Dynamically adjust the heartbeat interval based on component state
                interval = self._get_heartbeat_interval(component_id)
                
                # Modify interval based on consecutive failures
                if consecutive_failures > 0:
                    # Backoff for failures, but not too much
                    interval = min(interval * (1 + 0.5 * consecutive_failures), 30)
                
                # Wait before next heartbeat
                await asyncio.sleep(interval)
                
                retries += 1
        
        except asyncio.CancelledError:
            logger.info(f"Heartbeat loop for {component_id} cancelled")
            
    def _get_heartbeat_interval(self, component_id: str) -> float:
        """
        Get the appropriate heartbeat interval for a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Interval in seconds
        """
        # Check for component-specific interval
        if component_id in self.component_intervals:
            return self.component_intervals[component_id]
            
        # Check for component-type specific interval
        if component_id in self.registrations:
            component_type = self.registrations[component_id].component_type
            if component_type in self.type_intervals:
                return self.type_intervals[component_type]
        
        # Return default interval
        return self.default_interval
        
    def set_component_interval(self, component_id: str, interval: float) -> None:
        """
        Set a custom heartbeat interval for a specific component.
        
        Args:
            component_id: Component ID
            interval: Interval in seconds
        """
        self.component_intervals[component_id] = max(1.0, interval)  # Ensure minimum 1 second
        logger.info(f"Set custom heartbeat interval for {component_id}: {self.component_intervals[component_id]} seconds")
        
    async def _check_hermes_availability(self) -> bool:
        """
        Check if Hermes is available.
        
        Returns:
            True if Hermes is available
        """
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.hermes_url}/health",
                    timeout=3
                ) as response:
                    return response.status == 200
        
        except Exception:
            return False
    
    async def _reconnect_component(self, component_id: str) -> bool:
        """
        Reconnect a specific component to Hermes.
        
        Args:
            component_id: ID of the component to reconnect
            
        Returns:
            True if reconnection was successful
        """
        if component_id not in self.registrations:
            logger.warning(f"Component {component_id} not registered, cannot reconnect")
            return False
            
        registration = self.registrations[component_id]
        
        try:
            # Re-register with Hermes
            result = await registration.register()
            
            if result:
                logger.info(f"Successfully reconnected {component_id} to Hermes")
                return True
            else:
                logger.error(f"Failed to reconnect {component_id} to Hermes")
                return False
                
        except Exception as e:
            logger.error(f"Error reconnecting {component_id} to Hermes: {e}")
            return False
    
    async def _reconnect_all_components(self) -> Dict[str, bool]:
        """
        Reconnect all registered components to Hermes.
        
        Returns:
            Dictionary mapping component IDs to reconnection status
        """
        results = {}
        
        for component_id in self.registrations:
            results[component_id] = await self._reconnect_component(component_id)
            
            # Wait briefly between reconnections to avoid overwhelming Hermes
            await asyncio.sleep(0.5)
        
        # Log summary
        success_count = sum(1 for status in results.values() if status)
        logger.info(f"Reconnected {success_count}/{len(results)} components to Hermes")
        
        return results