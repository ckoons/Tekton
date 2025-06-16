#!/usr/bin/env python3
"""
Metrics Manager Module

Manages component metrics creation, updating, and threshold checks.
"""

import time
from typing import Dict, Any, Optional

from ...metrics_integration import MetricCategory, MetricUnit
from ...lifecycle import ComponentState


class MetricsManager:
    """
    Manages component metrics, creation, and threshold checking.
    """
    
    # Threshold constants
    CPU_WARNING_THRESHOLD = 0.7
    CPU_CRITICAL_THRESHOLD = 0.9
    MEMORY_WARNING_THRESHOLD = 0.7
    MEMORY_CRITICAL_THRESHOLD = 0.9
    ERROR_RATE_THRESHOLD = 0.1
    
    def __init__(self, 
                component_id: str, 
                metrics_manager,
                state_manager):
        """
        Initialize metrics manager.
        
        Args:
            component_id: Component ID
            metrics_manager: Metrics manager instance
            state_manager: State manager instance
        """
        self.component_id = component_id
        self.metrics_manager = metrics_manager
        self.state_manager = state_manager
        self.start_time = time.time()
        self.metrics = {}
        
        # Create default metrics
        self._create_default_metrics()
        
    def _create_default_metrics(self) -> None:
        """Create default metrics for the component."""
        registry = self.metrics_manager.get_registry()
        
        # CPU usage
        registry.create_gauge(
            name="cpu_usage",
            description="CPU usage percentage",
            category=MetricCategory.RESOURCE,
            unit=MetricUnit.PERCENTAGE
        )
        
        # Memory usage
        registry.create_gauge(
            name="memory_usage",
            description="Memory usage in bytes",
            category=MetricCategory.RESOURCE,
            unit=MetricUnit.BYTES
        )
        
        # Uptime
        registry.create_gauge(
            name="uptime",
            description="Component uptime in seconds",
            category=MetricCategory.SYSTEM,
            unit=MetricUnit.SECONDS
        )
        
        # State
        registry.create_gauge(
            name="state",
            description="Component state (0=unknown, 1=initializing, 2=ready, 3=active, 4=degraded, 5=error, 6=failed)",
            category=MetricCategory.SYSTEM
        )
        
    def update_metrics(self, metrics: Dict[str, float]) -> None:
        """
        Update component metrics.
        
        Args:
            metrics: Dictionary of metric name to value
        """
        # Update local metrics
        self.metrics.update(metrics)
        
        # Update registry metrics
        registry = self.metrics_manager.get_registry()
        for name, value in metrics.items():
            # Get or create metric
            metric = registry.get(name)
            if metric:
                # Update existing metric
                if hasattr(metric, "set"):
                    metric.set(value)
                elif hasattr(metric, "observe"):
                    metric.observe(value)
            else:
                # Create new gauge metric
                gauge = registry.create_gauge(
                    name=name,
                    description=f"Custom metric: {name}",
                    category=MetricCategory.COMPONENT
                )
                gauge.set(value)
                
        # Update uptime metric
        uptime_metric = registry.get("uptime")
        if uptime_metric:
            uptime_metric.set(time.time() - self.start_time)
            
        # Check for automatic state changes based on metrics
        self._check_metrics_thresholds(metrics)
        
    def _check_metrics_thresholds(self, metrics: Dict[str, float]) -> None:
        """
        Check metrics against thresholds for automatic state changes.
        
        Args:
            metrics: Dictionary of metric name to value
        """
        current_state = self.state_manager.state
        
        # Skip checks if already in degraded or error state
        if current_state in [ComponentState.DEGRADED.value, ComponentState.ERROR.value]:
            return
            
        # Check CPU usage
        if "cpu_usage" in metrics:
            cpu_usage = metrics["cpu_usage"]
            if cpu_usage > self.CPU_CRITICAL_THRESHOLD:
                self.state_manager.update_state(
                    ComponentState.ERROR.value,
                    reason="high_cpu_usage",
                    details=f"CPU usage exceeds critical threshold: {cpu_usage:.1%}"
                )
            elif cpu_usage > self.CPU_WARNING_THRESHOLD:
                self.state_manager.update_state(
                    ComponentState.DEGRADED.value,
                    reason="high_cpu_usage",
                    details=f"CPU usage exceeds warning threshold: {cpu_usage:.1%}"
                )
                
        # Check memory usage
        if "memory_usage" in metrics and "memory_limit" in metrics:
            memory_usage = metrics["memory_usage"]
            memory_limit = metrics["memory_limit"]
            memory_pct = memory_usage / memory_limit if memory_limit > 0 else 0
            
            if memory_pct > self.MEMORY_CRITICAL_THRESHOLD:
                self.state_manager.update_state(
                    ComponentState.ERROR.value,
                    reason="high_memory_usage",
                    details=f"Memory usage exceeds critical threshold: {memory_pct:.1%}"
                )
            elif memory_pct > self.MEMORY_WARNING_THRESHOLD:
                self.state_manager.update_state(
                    ComponentState.DEGRADED.value,
                    reason="high_memory_usage",
                    details=f"Memory usage exceeds warning threshold: {memory_pct:.1%}"
                )
                
        # Check error rate
        if "request_count" in metrics and "error_count" in metrics and metrics["request_count"] > 0:
            error_rate = metrics["error_count"] / metrics["request_count"]
            
            if error_rate > self.ERROR_RATE_THRESHOLD:
                self.state_manager.update_state(
                    ComponentState.DEGRADED.value,
                    reason="high_error_rate",
                    details=f"Error rate exceeds threshold: {error_rate:.1%}"
                )
                
    def record_request(self,
                    endpoint: str, 
                    duration: float,
                    status_code: int,
                    is_error: bool) -> None:
        """
        Record a request for metrics.
        
        Args:
            endpoint: Request endpoint
            duration: Request duration in seconds
            status_code: HTTP status code
            is_error: Whether the request resulted in an error
        """
        self.metrics_manager.record_request(
            endpoint=endpoint,
            duration=duration,
            status_code=status_code,
            is_error=is_error
        )
