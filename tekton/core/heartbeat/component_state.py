#!/usr/bin/env python3
"""
Component State Module

This module provides utilities for tracking component health metrics and state.
"""

import time
from typing import Dict, Any, Optional

import logging
logger = logging.getLogger(__name__)


class ComponentHealthMetrics:
    """
    Container for component health metrics.
    
    Tracks CPU, memory, latency, error rates, and other metrics for a component.
    """
    
    def __init__(self, component_id: str):
        """
        Initialize health metrics.
        
        Args:
            component_id: ID of the component
        """
        self.component_id = component_id
        self.metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "request_latency": 0.0,
            "error_rate": 0.0,
            "throughput": 0.0,
            "last_metric_time": time.time(),
            "latency": 0.0,
            "last_error": None,
            "last_error_time": 0.0
        }
        
        # Track state-related metrics
        self.needs_attention = False
        self.attention_reason = None
        
    def update(self, metrics: Dict[str, Any]) -> None:
        """
        Update health metrics.
        
        Args:
            metrics: New metrics data
        """
        self.metrics.update(metrics)
        self.metrics["last_metric_time"] = time.time()
        
        # Check for concerning metric values
        self._check_thresholds()
        
    def record_error(self, error: str) -> None:
        """
        Record an error.
        
        Args:
            error: Error message
        """
        self.metrics["last_error"] = error
        self.metrics["last_error_time"] = time.time()
        
        # Increment error rate if tracking requests
        if "error_count" in self.metrics and "request_count" in self.metrics:
            self.metrics["error_count"] = self.metrics.get("error_count", 0) + 1
            if self.metrics["request_count"] > 0:
                self.metrics["error_rate"] = self.metrics["error_count"] / self.metrics["request_count"]
                
        # Set needs attention flag
        self.needs_attention = True
        self.attention_reason = f"Error: {error}"
        
    def record_latency(self, latency: float) -> None:
        """
        Record request latency.
        
        Args:
            latency: Request latency in seconds
        """
        self.metrics["latency"] = latency
        
        # Check if latency is too high
        if latency > 1.0:  # More than 1 second is concerning
            self.needs_attention = True
            self.attention_reason = f"High latency: {latency:.2f}s"
            
    def _check_thresholds(self) -> None:
        """Check if any metrics exceed warning thresholds."""
        # Reset attention flags
        self.needs_attention = False
        self.attention_reason = None
        
        # Check CPU usage
        if self.metrics["cpu_usage"] > 0.85:
            self.needs_attention = True
            self.attention_reason = f"High CPU usage: {self.metrics['cpu_usage']:.1%}"
            
        # Check memory usage
        elif self.metrics["memory_usage"] > 0.85:
            self.needs_attention = True
            self.attention_reason = f"High memory usage: {self.metrics['memory_usage']:.1%}"
            
        # Check error rate
        elif self.metrics["error_rate"] > 0.1:
            self.needs_attention = True
            self.attention_reason = f"High error rate: {self.metrics['error_rate']:.1%}"
            
        # Check latency
        elif self.metrics["request_latency"] > 500:  # Over 500ms is concerning
            self.needs_attention = True
            self.attention_reason = f"High request latency: {self.metrics['request_latency']:.0f}ms"
            
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary of health metrics
        """
        return {
            "component_id": self.component_id,
            "metrics": self.metrics.copy(),
            "needs_attention": self.needs_attention,
            "attention_reason": self.attention_reason
        }