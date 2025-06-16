#!/usr/bin/env python3
"""
Metrics Core Module

This module defines the base metric classes used in the Tekton metrics system.
It provides Counter, Gauge, Histogram, and Timer implementations.
"""

import time
from typing import Dict, List, Any, Optional, Union

from .metric_types import MetricType, MetricCategory, MetricUnit


class Metric:
    """Base class for metrics."""
    
    def __init__(self,
                name: str,
                description: str,
                type: Union[MetricType, str],
                category: Union[MetricCategory, str],
                unit: Union[MetricUnit, str] = MetricUnit.NONE,
                component_id: Optional[str] = None,
                labels: Optional[Dict[str, str]] = None):
        """
        Initialize a metric.
        
        Args:
            name: Metric name
            description: Description of the metric
            type: Metric type
            category: Metric category
            unit: Metric unit
            component_id: Optional component ID
            labels: Optional labels for the metric
        """
        self.name = name
        self.description = description
        self.type = type.value if isinstance(type, MetricType) else type
        self.category = category.value if isinstance(category, MetricCategory) else category
        self.unit = unit.value if isinstance(unit, MetricUnit) else unit
        self.component_id = component_id
        self.labels = labels or {}
        self.created_at = time.time()
        self.last_updated = self.created_at
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "category": self.category,
            "unit": self.unit,
            "component_id": self.component_id,
            "labels": self.labels,
            "created_at": self.created_at,
            "last_updated": self.last_updated
        }
        
    def to_prometheus(self) -> str:
        """Convert metric to Prometheus format."""
        # Convert labels to Prometheus format
        prometheus_labels = ",".join([f'{k}="{v}"' for k, v in self.labels.items()])
        prometheus_labels = f"{{{prometheus_labels}}}" if prometheus_labels else ""
        
        # Create help and type lines
        help_line = f"# HELP {self.name} {self.description}"
        type_line = f"# TYPE {self.name} {self._prometheus_type()}"
        
        return f"{help_line}\n{type_line}"
        
    def _prometheus_type(self) -> str:
        """Convert metric type to Prometheus type."""
        prometheus_types = {
            MetricType.COUNTER.value: "counter",
            MetricType.GAUGE.value: "gauge",
            MetricType.HISTOGRAM.value: "histogram",
            MetricType.SUMMARY.value: "summary"
        }
        return prometheus_types.get(self.type, "untyped")
    
    def reset(self) -> None:
        """Reset the metric (to be implemented by subclasses)."""
        pass


class Counter(Metric):
    """Counter metric that only increases."""
    
    def __init__(self, 
                name: str, 
                description: str,
                category: Union[MetricCategory, str] = MetricCategory.COMPONENT,
                unit: Union[MetricUnit, str] = MetricUnit.COUNT,
                component_id: Optional[str] = None,
                labels: Optional[Dict[str, str]] = None,
                initial_value: float = 0.0):
        """
        Initialize a counter metric.
        
        Args:
            name: Metric name
            description: Description of the metric
            category: Metric category
            unit: Metric unit
            component_id: Optional component ID
            labels: Optional labels for the metric
            initial_value: Initial value for the counter
        """
        super().__init__(
            name=name,
            description=description,
            type=MetricType.COUNTER,
            category=category,
            unit=unit,
            component_id=component_id,
            labels=labels
        )
        self.value = initial_value
        
    def increment(self, amount: float = 1.0) -> float:
        """
        Increment the counter.
        
        Args:
            amount: Amount to increment by (must be positive)
            
        Returns:
            Current value
        """
        if amount < 0:
            raise ValueError("Counter can only be incremented by positive values")
            
        self.value += amount
        self.last_updated = time.time()
        return self.value
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert counter to dictionary."""
        result = super().to_dict()
        result["value"] = self.value
        return result
        
    def to_prometheus(self) -> str:
        """Convert counter to Prometheus format."""
        base = super().to_prometheus()
        labels = ",".join([f'{k}="{v}"' for k, v in self.labels.items()])
        labels = f"{{{labels}}}" if labels else ""
        
        value_line = f"{self.name}{labels} {self.value}"
        return f"{base}\n{value_line}"
        
    def reset(self) -> None:
        """Reset the counter to zero."""
        self.value = 0.0
        self.last_updated = time.time()


class Gauge(Metric):
    """Gauge metric that can increase or decrease."""
    
    def __init__(self, 
                name: str, 
                description: str,
                category: Union[MetricCategory, str] = MetricCategory.COMPONENT,
                unit: Union[MetricUnit, str] = MetricUnit.NONE,
                component_id: Optional[str] = None,
                labels: Optional[Dict[str, str]] = None,
                initial_value: float = 0.0):
        """
        Initialize a gauge metric.
        
        Args:
            name: Metric name
            description: Description of the metric
            category: Metric category
            unit: Metric unit
            component_id: Optional component ID
            labels: Optional labels for the metric
            initial_value: Initial value for the gauge
        """
        super().__init__(
            name=name,
            description=description,
            type=MetricType.GAUGE,
            category=category,
            unit=unit,
            component_id=component_id,
            labels=labels
        )
        self.value = initial_value
        
    def set(self, value: float) -> float:
        """
        Set the gauge value.
        
        Args:
            value: New value
            
        Returns:
            Current value
        """
        self.value = value
        self.last_updated = time.time()
        return self.value
        
    def increment(self, amount: float = 1.0) -> float:
        """
        Increment the gauge.
        
        Args:
            amount: Amount to increment by
            
        Returns:
            Current value
        """
        self.value += amount
        self.last_updated = time.time()
        return self.value
        
    def decrement(self, amount: float = 1.0) -> float:
        """
        Decrement the gauge.
        
        Args:
            amount: Amount to decrement by
            
        Returns:
            Current value
        """
        self.value -= amount
        self.last_updated = time.time()
        return self.value
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert gauge to dictionary."""
        result = super().to_dict()
        result["value"] = self.value
        return result
        
    def to_prometheus(self) -> str:
        """Convert gauge to Prometheus format."""
        base = super().to_prometheus()
        labels = ",".join([f'{k}="{v}"' for k, v in self.labels.items()])
        labels = f"{{{labels}}}" if labels else ""
        
        value_line = f"{self.name}{labels} {self.value}"
        return f"{base}\n{value_line}"
        
    def reset(self) -> None:
        """Reset the gauge to zero."""
        self.value = 0.0
        self.last_updated = time.time()


class Histogram(Metric):
    """Histogram metric for distribution of values."""
    
    def __init__(self, 
                name: str, 
                description: str,
                buckets: List[float],
                category: Union[MetricCategory, str] = MetricCategory.COMPONENT,
                unit: Union[MetricUnit, str] = MetricUnit.NONE,
                component_id: Optional[str] = None,
                labels: Optional[Dict[str, str]] = None):
        """
        Initialize a histogram metric.
        
        Args:
            name: Metric name
            description: Description of the metric
            buckets: List of bucket upper boundaries
            category: Metric category
            unit: Metric unit
            component_id: Optional component ID
            labels: Optional labels for the metric
        """
        super().__init__(
            name=name,
            description=description,
            type=MetricType.HISTOGRAM,
            category=category,
            unit=unit,
            component_id=component_id,
            labels=labels
        )
        self.buckets = sorted(buckets) + [float('inf')]
        self.bucket_counts = [0] * len(self.buckets)
        self.count = 0
        self.sum = 0.0
        
    def observe(self, value: float) -> None:
        """
        Record an observation.
        
        Args:
            value: Observed value
        """
        self.count += 1
        self.sum += value
        
        # Increment bucket counts for all buckets that the value falls into
        for i, boundary in enumerate(self.buckets):
            if value <= boundary:
                self.bucket_counts[i] += 1
                
        self.last_updated = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert histogram to dictionary."""
        result = super().to_dict()
        result.update({
            "buckets": self.buckets[:-1],  # Exclude inf
            "bucket_counts": self.bucket_counts,
            "count": self.count,
            "sum": self.sum
        })
        return result
        
    def to_prometheus(self) -> str:
        """Convert histogram to Prometheus format."""
        base = super().to_prometheus()
        labels = ",".join([f'{k}="{v}"' for k, v in self.labels.items()])
        labels_str = f"{{{labels}}}" if labels else ""
        
        lines = []
        
        # Add bucket lines
        for i, boundary in enumerate(self.buckets):
            bucket_labels = f"{labels},{{'le':'{boundary}'}}" if labels else f"{{'le':'{boundary}'}}"
            lines.append(f"{self.name}_bucket{bucket_labels} {self.bucket_counts[i]}")
            
        # Add sum and count
        lines.append(f"{self.name}_sum{labels_str} {self.sum}")
        lines.append(f"{self.name}_count{labels_str} {self.count}")
        
        return f"{base}\n" + "\n".join(lines)
        
    def reset(self) -> None:
        """Reset the histogram."""
        self.bucket_counts = [0] * len(self.buckets)
        self.count = 0
        self.sum = 0.0
        self.last_updated = time.time()


class Timer:
    """Timer for measuring duration of operations."""
    
    def __init__(self, histogram: Histogram):
        """
        Initialize a timer.
        
        Args:
            histogram: Histogram to record times
        """
        self.histogram = histogram
        self.start_time = None
        
    def start(self) -> 'Timer':
        """
        Start the timer.
        
        Returns:
            Self for method chaining
        """
        self.start_time = time.time()
        return self
        
    def stop(self) -> float:
        """
        Stop the timer and record the duration.
        
        Returns:
            Duration in seconds
        """
        if self.start_time is None:
            raise ValueError("Timer was not started")
            
        duration = time.time() - self.start_time
        self.histogram.observe(duration)
        self.start_time = None
        return duration
        
    async def __aenter__(self) -> 'Timer':
        """Async context manager entry."""
        self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        self.stop()
        
    def __enter__(self) -> 'Timer':
        """Context manager entry."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()