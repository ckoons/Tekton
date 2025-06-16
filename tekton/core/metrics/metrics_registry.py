#!/usr/bin/env python3
"""
Metrics Registry Module

This module provides a registry for metrics in the Tekton system.
It allows for creating, storing, and retrieving metrics by name and labels.
"""

from typing import Dict, List, Any, Optional, Union

from .metric_types import MetricType, MetricCategory, MetricUnit
from .metrics import Metric, Counter, Gauge, Histogram, Timer


class MetricsRegistry:
    """Registry for metrics."""
    
    def __init__(self, component_id: str):
        """
        Initialize metrics registry.
        
        Args:
            component_id: Component ID
        """
        self.component_id = component_id
        self.metrics: Dict[str, Metric] = {}
        
    def register(self, metric: Metric) -> Metric:
        """
        Register a metric.
        
        Args:
            metric: Metric to register
            
        Returns:
            Registered metric
        """
        # Set component ID if not already set
        if not metric.component_id:
            metric.component_id = self.component_id
            
        # Generate unique name based on labels
        unique_name = self._get_unique_name(metric)
        
        # Register metric
        self.metrics[unique_name] = metric
        
        return metric
        
    def get(self, name: str, labels: Optional[Dict[str, str]] = None) -> Optional[Metric]:
        """
        Get a metric by name and labels.
        
        Args:
            name: Metric name
            labels: Optional labels
            
        Returns:
            Metric or None if not found
        """
        unique_name = self._get_unique_name_from_parts(name, labels or {})
        return self.metrics.get(unique_name)
        
    def remove(self, name: str, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Remove a metric.
        
        Args:
            name: Metric name
            labels: Optional labels
        """
        unique_name = self._get_unique_name_from_parts(name, labels or {})
        if unique_name in self.metrics:
            del self.metrics[unique_name]
            
    def clear(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()
        
    def get_all(self) -> List[Metric]:
        """
        Get all metrics.
        
        Returns:
            List of all metrics
        """
        return list(self.metrics.values())
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert registry to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "component_id": self.component_id,
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()}
        }
        
    def to_prometheus(self) -> str:
        """
        Convert all metrics to Prometheus format.
        
        Returns:
            Prometheus format string
        """
        return "\n".join([m.to_prometheus() for m in self.metrics.values()])
        
    def _get_unique_name(self, metric: Metric) -> str:
        """
        Generate a unique name for a metric based on name and labels.
        
        Args:
            metric: Metric
            
        Returns:
            Unique name
        """
        return self._get_unique_name_from_parts(metric.name, metric.labels)
        
    def _get_unique_name_from_parts(self, name: str, labels: Dict[str, str]) -> str:
        """
        Generate a unique name from parts.
        
        Args:
            name: Metric name
            labels: Labels
            
        Returns:
            Unique name
        """
        if not labels:
            return name
            
        # Sort labels for consistent ordering
        sorted_labels = sorted(labels.items())
        label_str = ",".join([f"{k}={v}" for k, v in sorted_labels])
        
        return f"{name}{{{label_str}}}"
        
    def create_counter(self, 
                     name: str, 
                     description: str,
                     category: Union[MetricCategory, str] = MetricCategory.COMPONENT,
                     unit: Union[MetricUnit, str] = MetricUnit.COUNT,
                     labels: Optional[Dict[str, str]] = None,
                     initial_value: float = 0.0) -> Counter:
        """
        Create and register a counter.
        
        Args:
            name: Metric name
            description: Description
            category: Metric category
            unit: Metric unit
            labels: Optional labels
            initial_value: Initial value
            
        Returns:
            Registered counter
        """
        counter = Counter(
            name=name,
            description=description,
            category=category,
            unit=unit,
            component_id=self.component_id,
            labels=labels,
            initial_value=initial_value
        )
        
        return self.register(counter)
        
    def create_gauge(self, 
                   name: str, 
                   description: str,
                   category: Union[MetricCategory, str] = MetricCategory.COMPONENT,
                   unit: Union[MetricUnit, str] = MetricUnit.NONE,
                   labels: Optional[Dict[str, str]] = None,
                   initial_value: float = 0.0) -> Gauge:
        """
        Create and register a gauge.
        
        Args:
            name: Metric name
            description: Description
            category: Metric category
            unit: Metric unit
            labels: Optional labels
            initial_value: Initial value
            
        Returns:
            Registered gauge
        """
        gauge = Gauge(
            name=name,
            description=description,
            category=category,
            unit=unit,
            component_id=self.component_id,
            labels=labels,
            initial_value=initial_value
        )
        
        return self.register(gauge)
        
    def create_histogram(self, 
                       name: str, 
                       description: str,
                       buckets: List[float],
                       category: Union[MetricCategory, str] = MetricCategory.COMPONENT,
                       unit: Union[MetricUnit, str] = MetricUnit.NONE,
                       labels: Optional[Dict[str, str]] = None) -> Histogram:
        """
        Create and register a histogram.
        
        Args:
            name: Metric name
            description: Description
            buckets: Bucket boundaries
            category: Metric category
            unit: Metric unit
            labels: Optional labels
            
        Returns:
            Registered histogram
        """
        histogram = Histogram(
            name=name,
            description=description,
            buckets=buckets,
            category=category,
            unit=unit,
            component_id=self.component_id,
            labels=labels
        )
        
        return self.register(histogram)
        
    def create_timer(self, 
                   name: str, 
                   description: str,
                   buckets: Optional[List[float]] = None,
                   category: Union[MetricCategory, str] = MetricCategory.LATENCY,
                   labels: Optional[Dict[str, str]] = None) -> Timer:
        """
        Create and register a timer.
        
        Args:
            name: Metric name
            description: Description
            buckets: Optional bucket boundaries, defaults to standard latency buckets
            category: Metric category
            labels: Optional labels
            
        Returns:
            Timer object
        """
        # Use standard latency buckets if not provided
        if buckets is None:
            buckets = [0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
            
        histogram = self.create_histogram(
            name=name,
            description=description,
            buckets=buckets,
            category=category,
            unit=MetricUnit.SECONDS,
            labels=labels
        )
        
        return Timer(histogram)