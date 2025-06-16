#!/usr/bin/env python3
"""
Resource monitoring system for Tekton.

This module provides functionality to monitor system resources (CPU, memory, disk, network)
and component-specific resource usage. It includes threshold-based alerting.
"""

import asyncio
import time
import psutil
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any

import logging
logger = logging.getLogger(__name__)

from .config import ResourceConfig, ResourceThreshold
from .metrics import ResourceMetrics
from .gpu_utils import check_gpu_availability, get_gpu_metrics
from .system_info import get_system_info


class ResourceMonitor:
    """
    System resource monitor for Tekton.
    
    Monitors CPU, memory, disk, network, and optionally GPU usage with
    threshold-based alerting. Supports component-specific resource tracking.
    
    Features:
    - System-wide resource monitoring
    - Component-specific resource tracking
    - Threshold-based alerting with configurable thresholds
    - Historical data retention
    - Optional GPU monitoring
    """
    
    def __init__(
        self, 
        config: Optional[ResourceConfig] = None,
        alert_handlers: Optional[List[Callable[[str, str, float, float], None]]] = None
    ):
        """
        Initialize the resource monitor.
        
        Args:
            config: Configuration for resource thresholds and monitoring behavior
            alert_handlers: Functions to call when thresholds are exceeded
                            Each handler receives (resource_type, level, value, threshold)
        """
        self.config = config or ResourceConfig()
        self.alert_handlers = alert_handlers or []
        
        # Initialize metrics storage
        self.metrics_history: List[ResourceMetrics] = []
        self.component_pids: Dict[str, List[int]] = {}
        
        # For rate calculations
        self._last_network_bytes: Dict[str, tuple[int, int]] = {}  # (sent, received)
        self._last_network_time = time.time()
        
        # Alert cooldown tracking
        self._last_alerts: Dict[str, float] = {}
        
        # Monitor state
        self._running = False
        self._monitor_task = None
        
        # Detect GPU availability
        self._has_gpu = check_gpu_availability()
        
    def register_component(self, component_id: str, pids: List[int]) -> None:
        """
        Register a component for specific resource monitoring.
        
        Args:
            component_id: Unique identifier for the component
            pids: List of process IDs associated with this component
        """
        self.component_pids[component_id] = pids
        
    def unregister_component(self, component_id: str) -> None:
        """Remove a component from specific monitoring."""
        if component_id in self.component_pids:
            del self.component_pids[component_id]
            
    def _get_component_metrics(self) -> Dict[str, Dict[str, float]]:
        """Collect resource usage metrics for registered components."""
        component_metrics = {}
        
        for component_id, pids in self.component_pids.items():
            cpu_percent = 0.0
            memory_percent = 0.0
            valid_pids = []
            
            for pid in pids:
                try:
                    process = psutil.Process(pid)
                    cpu_percent += process.cpu_percent(interval=0.1)
                    memory_percent += process.memory_percent()
                    valid_pids.append(pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Update the list of valid PIDs
            self.component_pids[component_id] = valid_pids
            
            component_metrics[component_id] = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent
            }
            
        return component_metrics
        
    def _calculate_network_rates(self) -> Dict[str, Dict[str, float]]:
        """Calculate network throughput in Mbps."""
        current_time = time.time()
        counters = psutil.net_io_counters(pernic=True)
        network_rates = {}
        
        for interface, data in counters.items():
            if interface in self._last_network_bytes:
                last_sent, last_recv = self._last_network_bytes[interface]
                last_time = self._last_network_time
                
                # Calculate bytes per second
                time_diff = current_time - last_time
                bytes_sent = data.bytes_sent - last_sent
                bytes_recv = data.bytes_recv - last_recv
                
                if time_diff > 0:
                    # Convert to Mbps (megabits per second)
                    sent_mbps = (bytes_sent * 8 / 1_000_000) / time_diff
                    recv_mbps = (bytes_recv * 8 / 1_000_000) / time_diff
                    network_rates[interface] = {
                        "sent_mbps": sent_mbps,
                        "recv_mbps": recv_mbps,
                        "total_mbps": sent_mbps + recv_mbps
                    }
            
            # Update last values
            self._last_network_bytes[interface] = (data.bytes_sent, data.bytes_recv)
            
        self._last_network_time = current_time
        return network_rates
                
    def collect_metrics(self) -> ResourceMetrics:
        """
        Collect current system resource metrics.
        
        Returns:
            ResourceMetrics object with current usage data
        """
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Get disk usage
        disk_percent = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_percent[partition.mountpoint] = usage.percent
            except (PermissionError, OSError):
                continue
                
        # Get network throughput
        network_mbps = self._calculate_network_rates()
        
        # Get component-specific metrics
        component_metrics = self._get_component_metrics()
        
        # Get GPU metrics if available
        gpu_percent = get_gpu_metrics() if self._has_gpu else None
        
        # Create metrics object
        metrics = ResourceMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            network_mbps=network_mbps,
            gpu_percent=gpu_percent,
            component_metrics=component_metrics
        )
        
        # Add to history and clean up old entries
        self.metrics_history.append(metrics)
        self._prune_history()
        
        # Check thresholds and trigger alerts
        self._check_thresholds(metrics)
        
        return metrics
        
    def _prune_history(self) -> None:
        """Remove metrics older than the retention period."""
        if not self.metrics_history:
            return
            
        retention_seconds = self.config.retention_hours * 3600
        cutoff_time = datetime.now().timestamp() - retention_seconds
        
        self.metrics_history = [
            m for m in self.metrics_history 
            if m.timestamp.timestamp() >= cutoff_time
        ]
        
    def _check_thresholds(self, metrics: ResourceMetrics) -> None:
        """Check if any metrics exceed configured thresholds."""
        current_time = time.time()
        
        # Check system CPU
        self._check_single_threshold(
            "system_cpu", 
            metrics.cpu_percent, 
            self.config.cpu_threshold,
            current_time
        )
        
        # Check system memory
        self._check_single_threshold(
            "system_memory", 
            metrics.memory_percent, 
            self.config.memory_threshold,
            current_time
        )
        
        # Check disks
        for mount, usage in metrics.disk_percent.items():
            self._check_single_threshold(
                f"disk_{mount}", 
                usage, 
                self.config.disk_threshold,
                current_time
            )
            
        # Check network interfaces
        for interface, data in metrics.network_mbps.items():
            if "total_mbps" in data:
                self._check_single_threshold(
                    f"network_{interface}", 
                    data["total_mbps"], 
                    self.config.network_threshold_mbps,
                    current_time
                )
                
        # Check GPU if available
        if metrics.gpu_percent:
            for gpu_id, data in metrics.gpu_percent.items():
                if "utilization" in data and self.config.gpu_threshold:
                    self._check_single_threshold(
                        f"gpu_{gpu_id}", 
                        data["utilization"], 
                        self.config.gpu_threshold,
                        current_time
                    )
                    
        # Check component-specific metrics
        for component_id, comp_metrics in metrics.component_metrics.items():
            # Get component-specific thresholds if configured
            cpu_threshold = (
                self.config.component_thresholds.get(component_id, {}).get("cpu_threshold") 
                or self.config.cpu_threshold
            )
            memory_threshold = (
                self.config.component_thresholds.get(component_id, {}).get("memory_threshold") 
                or self.config.memory_threshold
            )
            
            # Check component CPU
            self._check_single_threshold(
                f"component_{component_id}_cpu", 
                comp_metrics["cpu_percent"], 
                cpu_threshold,
                current_time
            )
            
            # Check component memory
            self._check_single_threshold(
                f"component_{component_id}_memory", 
                comp_metrics["memory_percent"], 
                memory_threshold,
                current_time
            )
            
    def _check_single_threshold(
        self, 
        resource_name: str, 
        value: float, 
        threshold: ResourceThreshold,
        current_time: float
    ) -> None:
        """
        Check a single value against its thresholds and trigger alerts if needed.
        
        Args:
            resource_name: Name/identifier of the resource being checked
            value: Current value to check
            threshold: Threshold object with warning and critical levels
            current_time: Current timestamp for cooldown checks
        """
        # Determine alert level
        alert_level = None
        if value >= threshold.critical:
            alert_level = "CRITICAL"
        elif value >= threshold.warning:
            alert_level = "WARNING"
            
        if not alert_level:
            return
            
        # Check cooldown period
        alert_key = f"{resource_name}_{alert_level}"
        last_alert_time = self._last_alerts.get(alert_key, 0)
        
        if current_time - last_alert_time < self.config.alert_cooldown_seconds:
            return  # Still in cooldown period
            
        # Update last alert time
        self._last_alerts[alert_key] = current_time
        
        # Trigger handlers
        threshold_value = (
            threshold.critical if alert_level == "CRITICAL" else threshold.warning
        )
        
        for handler in self.alert_handlers:
            try:
                handler(resource_name, alert_level, value, threshold_value)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
                
        # Log the alert
        logger.warning(
            f"Resource alert: {resource_name} is {alert_level} "
            f"(value: {value:.1f}, threshold: {threshold_value:.1f})"
        )
    
    async def _monitoring_loop(self) -> None:
        """Background task for periodic resource monitoring."""
        while self._running:
            try:
                self.collect_metrics()
            except Exception as e:
                logger.error(f"Error collecting resource metrics: {e}")
                
            await asyncio.sleep(self.config.check_interval_seconds)
            
    def start(self) -> None:
        """Start the resource monitoring background task."""
        if self._running:
            return
            
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Resource monitoring started")
        
    def stop(self) -> None:
        """Stop the resource monitoring background task."""
        if not self._running:
            return
            
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            self._monitor_task = None
            
        logger.info("Resource monitoring stopped")
        
    def get_current_metrics(self) -> ResourceMetrics:
        """Get the most recent metrics."""
        if not self.metrics_history:
            return self.collect_metrics()
        return self.metrics_history[-1]
        
    def get_metrics_history(
        self, 
        hours: Optional[int] = None
    ) -> List[ResourceMetrics]:
        """
        Get historical metrics.
        
        Args:
            hours: Number of hours of history to retrieve (None for all available)
            
        Returns:
            List of ResourceMetrics objects
        """
        if hours is None:
            return self.metrics_history
            
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        return [
            m for m in self.metrics_history 
            if m.timestamp.timestamp() >= cutoff_time
        ]
        
    def add_alert_handler(
        self, 
        handler: Callable[[str, str, float, float], None]
    ) -> None:
        """
        Add a new alert handler.
        
        Args:
            handler: Function to call when thresholds are exceeded
                    Receives (resource_name, level, value, threshold)
        """
        if handler not in self.alert_handlers:
            self.alert_handlers.append(handler)
            
    def remove_alert_handler(
        self, 
        handler: Callable[[str, str, float, float], None]
    ) -> None:
        """Remove an alert handler."""
        if handler in self.alert_handlers:
            self.alert_handlers.remove(handler)
            
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information."""
        return get_system_info()
