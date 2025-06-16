#!/usr/bin/env python3
"""
Metrics Manager Module

This module provides a manager for component metrics with Hermes integration.
It handles metrics reporting, common metrics creation, and system metric updates.
"""

import os
import time
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Callable, TypeVar, Union, Tuple

from ..logging_integration import get_logger, LogCategory
from .metrics_registry import MetricsRegistry
from .metric_types import MetricType, MetricCategory, MetricUnit
from .metrics import Counter, Gauge, Histogram, Timer

# Configure logger
logger = get_logger("tekton.metrics")


class MetricsManager:
    """Manager for component metrics with Hermes integration."""
    
    def __init__(self, 
                component_id: str,
                hermes_url: Optional[str] = None,
                report_interval: float = 30.0):
        """
        Initialize metrics manager.
        
        Args:
            component_id: Component ID
            hermes_url: Optional URL of Hermes service
            report_interval: Interval in seconds for reporting metrics
        """
        self.component_id = component_id
        self.hermes_url = hermes_url
        self.report_interval = report_interval
        self.registry = MetricsRegistry(component_id)
        self.reporting_task = None
        self.running = False
        
        # Create common metrics
        self._create_common_metrics()
        
        # Get logger
        self.logger = get_logger(component_id)
        
    def _create_common_metrics(self) -> None:
        """Create common metrics for all components."""
        # CPU usage
        self.registry.create_gauge(
            name="cpu_usage",
            description="CPU usage percentage",
            category=MetricCategory.RESOURCE,
            unit=MetricUnit.PERCENTAGE
        )
        
        # Memory usage
        self.registry.create_gauge(
            name="memory_usage",
            description="Memory usage in bytes",
            category=MetricCategory.RESOURCE,
            unit=MetricUnit.BYTES
        )
        
        # Request count
        self.registry.create_counter(
            name="request_count",
            description="Total number of requests",
            category=MetricCategory.THROUGHPUT,
            unit=MetricUnit.REQUESTS
        )
        
        # Error count
        self.registry.create_counter(
            name="error_count",
            description="Total number of errors",
            category=MetricCategory.ERROR,
            unit=MetricUnit.ERRORS
        )
        
        # Request latency
        self.registry.create_histogram(
            name="request_latency",
            description="Request latency in seconds",
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0],
            category=MetricCategory.LATENCY,
            unit=MetricUnit.SECONDS
        )
        
    async def start(self) -> None:
        """Start metrics reporting."""
        if self.running:
            return
            
        self.running = True
        
        # Start reporting task if Hermes URL is provided
        if self.hermes_url:
            self.reporting_task = asyncio.create_task(self._reporting_loop())
            self.logger.info("Started metrics reporting", category=LogCategory.METRICS)
        
    async def stop(self) -> None:
        """Stop metrics reporting."""
        if not self.running:
            return
            
        self.running = False
        
        # Cancel reporting task
        if self.reporting_task:
            self.reporting_task.cancel()
            try:
                await self.reporting_task
            except asyncio.CancelledError:
                pass
            self.reporting_task = None
            
        self.logger.info("Stopped metrics reporting", category=LogCategory.METRICS)
        
    async def _reporting_loop(self) -> None:
        """Metrics reporting loop."""
        try:
            while self.running:
                try:
                    # Update system metrics
                    self._update_system_metrics()
                    
                    # Report metrics to Hermes
                    await self._report_metrics()
                    
                    # Log metrics
                    self.logger.debug(
                        f"Reported metrics to Hermes: {len(self.registry.metrics)} metrics",
                        category=LogCategory.METRICS
                    )
                    
                except Exception as e:
                    self.logger.error(
                        f"Failed to report metrics: {e}",
                        category=LogCategory.METRICS,
                        exception=e
                    )
                    
                # Wait for next report
                await asyncio.sleep(self.report_interval)
                
        except asyncio.CancelledError:
            self.logger.info("Metrics reporting cancelled", category=LogCategory.METRICS)
            
    def _update_system_metrics(self) -> None:
        """Update system metrics."""
        try:
            # Get CPU usage metric
            cpu_metric = self.registry.get("cpu_usage")
            if cpu_metric and isinstance(cpu_metric, Gauge):
                # Set to a random value for now
                # In a real implementation, get actual CPU usage
                cpu_metric.set(0.3)
                
            # Get memory usage metric
            memory_metric = self.registry.get("memory_usage")
            if memory_metric and isinstance(memory_metric, Gauge):
                # Set to a random value for now
                # In a real implementation, get actual memory usage
                memory_metric.set(1024 * 1024 * 100)  # 100 MB
                
        except Exception as e:
            self.logger.error(
                f"Failed to update system metrics: {e}",
                category=LogCategory.METRICS,
                exception=e
            )
            
    async def _report_metrics(self) -> None:
        """Report metrics to Hermes."""
        if not self.hermes_url:
            return
            
        # Get all metrics
        metrics_data = self.registry.to_dict()
        
        # Add timestamp and component info
        report = {
            "component_id": self.component_id,
            "timestamp": time.time(),
            "metrics": metrics_data
        }
        
        # In a real implementation, send to Hermes
        # For now, just log that we would send it
        self.logger.debug(
            f"Would send metrics to Hermes: {len(metrics_data['metrics'])} metrics",
            category=LogCategory.METRICS,
            context={"url": self.hermes_url}
        )
        
    def get_registry(self) -> MetricsRegistry:
        """
        Get the metrics registry.
        
        Returns:
            Metrics registry
        """
        return self.registry
        
    def record_request(self, 
                     endpoint: str, 
                     duration: float, 
                     status_code: int,
                     is_error: bool = False) -> None:
        """
        Record a request.
        
        Args:
            endpoint: Request endpoint
            duration: Request duration in seconds
            status_code: HTTP status code
            is_error: Whether the request resulted in an error
        """
        # Get request count metric with endpoint label
        request_count = self.registry.get("request_count", {"endpoint": endpoint})
        if not request_count:
            request_count = self.registry.create_counter(
                name="request_count",
                description="Total number of requests",
                category=MetricCategory.THROUGHPUT,
                unit=MetricUnit.REQUESTS,
                labels={"endpoint": endpoint}
            )
            
        # Increment request count
        request_count.increment()
        
        # Get latency histogram with endpoint label
        latency = self.registry.get("request_latency", {"endpoint": endpoint})
        if not latency:
            latency = self.registry.create_histogram(
                name="request_latency",
                description="Request latency in seconds",
                buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0],
                category=MetricCategory.LATENCY,
                unit=MetricUnit.SECONDS,
                labels={"endpoint": endpoint}
            )
            
        # Record latency
        latency.observe(duration)
        
        # Record error if applicable
        if is_error:
            error_count = self.registry.get("error_count", {"endpoint": endpoint})
            if not error_count:
                error_count = self.registry.create_counter(
                    name="error_count",
                    description="Total number of errors",
                    category=MetricCategory.ERROR,
                    unit=MetricUnit.ERRORS,
                    labels={"endpoint": endpoint}
                )
                
            error_count.increment()
            
    def create_request_timer(self, endpoint: str) -> Timer:
        """
        Create a timer for measuring request duration.
        
        Args:
            endpoint: Request endpoint
            
        Returns:
            Timer object
        """
        # Get or create latency histogram
        latency = self.registry.get("request_latency", {"endpoint": endpoint})
        if not latency:
            latency = self.registry.create_histogram(
                name="request_latency",
                description="Request latency in seconds",
                buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0],
                category=MetricCategory.LATENCY,
                unit=MetricUnit.SECONDS,
                labels={"endpoint": endpoint}
            )
            
        return Timer(latency)