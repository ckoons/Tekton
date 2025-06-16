#!/usr/bin/env python3
"""
Model Metrics Module

This module provides functions for collecting and analyzing metrics from model adapters.
"""

import time
import logging
from typing import Dict, List, Any, Optional

# Configure logger
logger = logging.getLogger("tekton.models.metrics")


class MetricsCollector:
    """Collector for model usage metrics."""
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.metrics = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_input_tokens": 0,
            "total_embed_requests": 0,
            "total_embed_tokens": 0,
            "error_count": 0,
            "rate_limit_errors": 0,
            "fallback_count": 0,
            "average_latency": 0.0,
            "average_embed_latency": 0.0,
            "start_time": time.time(),
            "adapters": {}
        }
    
    def update_generation_metrics(self, adapter_name: str, result: Dict[str, Any], duration: float):
        """
        Update metrics for a generation request.
        
        Args:
            adapter_name: Name of the adapter used
            result: Generation result
            duration: Request duration in seconds
        """
        # Update global metrics
        self.metrics["total_requests"] += 1
        self.metrics["total_tokens"] += result.get("tokens", 0)
        
        # Update average latency
        prev_avg = self.metrics["average_latency"]
        prev_count = self.metrics["total_requests"] - 1
        self.metrics["average_latency"] = (prev_avg * prev_count + duration) / self.metrics["total_requests"]
        
        # Update adapter-specific metrics
        if adapter_name not in self.metrics["adapters"]:
            self.metrics["adapters"][adapter_name] = {
                "requests": 0,
                "tokens": 0,
                "average_latency": 0.0,
                "error_count": 0
            }
            
        adapter_metrics = self.metrics["adapters"][adapter_name]
        adapter_metrics["requests"] += 1
        adapter_metrics["tokens"] += result.get("tokens", 0)
        
        # Update adapter average latency
        prev_adapter_avg = adapter_metrics["average_latency"]
        prev_adapter_count = adapter_metrics["requests"] - 1
        adapter_metrics["average_latency"] = (
            (prev_adapter_avg * prev_adapter_count + duration) / adapter_metrics["requests"]
        )
    
    def update_embedding_metrics(self, adapter_name: str, result: Dict[str, Any], duration: float):
        """
        Update metrics for an embedding request.
        
        Args:
            adapter_name: Name of the adapter used
            result: Embedding result
            duration: Request duration in seconds
        """
        # Update global metrics
        self.metrics["total_embed_requests"] += 1
        self.metrics["total_embed_tokens"] += result.get("tokens", 0)
        
        # Update average latency
        prev_avg = self.metrics["average_embed_latency"]
        prev_count = self.metrics["total_embed_requests"] - 1
        self.metrics["average_embed_latency"] = (
            (prev_avg * prev_count + duration) / self.metrics["total_embed_requests"]
        )
        
        # Update adapter-specific metrics
        if adapter_name not in self.metrics["adapters"]:
            self.metrics["adapters"][adapter_name] = {
                "embed_requests": 0,
                "embed_tokens": 0,
                "average_embed_latency": 0.0,
                "embed_error_count": 0
            }
        
        adapter_metrics = self.metrics["adapters"][adapter_name]
        
        # Initialize embedding metrics if not present
        if "embed_requests" not in adapter_metrics:
            adapter_metrics["embed_requests"] = 0
            adapter_metrics["embed_tokens"] = 0
            adapter_metrics["average_embed_latency"] = 0.0
            adapter_metrics["embed_error_count"] = 0
            
        adapter_metrics["embed_requests"] += 1
        adapter_metrics["embed_tokens"] += result.get("tokens", 0)
        
        # Update adapter average latency
        prev_adapter_avg = adapter_metrics["average_embed_latency"]
        prev_adapter_count = adapter_metrics["embed_requests"] - 1
        adapter_metrics["average_embed_latency"] = (
            (prev_adapter_avg * prev_adapter_count + duration) / adapter_metrics["embed_requests"]
        )
    
    def update_error_metrics(self, adapter_name: str, is_embedding: bool = False, is_rate_limit: bool = False):
        """
        Update error metrics.
        
        Args:
            adapter_name: Name of the adapter that encountered the error
            is_embedding: Whether this was an embedding request
            is_rate_limit: Whether this was a rate limit error
        """
        # Update global metrics
        self.metrics["error_count"] += 1
        
        if is_rate_limit:
            self.metrics["rate_limit_errors"] += 1
            
        # Update adapter-specific metrics
        if adapter_name not in self.metrics["adapters"]:
            self.metrics["adapters"][adapter_name] = {
                "error_count": 0,
                "embed_error_count": 0,
                "rate_limit_errors": 0
            }
            
        adapter_metrics = self.metrics["adapters"][adapter_name]
        
        if is_embedding:
            if "embed_error_count" not in adapter_metrics:
                adapter_metrics["embed_error_count"] = 0
            adapter_metrics["embed_error_count"] += 1
        else:
            adapter_metrics["error_count"] += 1
            
        if is_rate_limit:
            if "rate_limit_errors" not in adapter_metrics:
                adapter_metrics["rate_limit_errors"] = 0
            adapter_metrics["rate_limit_errors"] += 1
    
    def update_fallback_metrics(self, original_adapter: str, fallback_adapter: str, is_embedding: bool = False):
        """
        Update fallback metrics.
        
        Args:
            original_adapter: Name of the original adapter that failed
            fallback_adapter: Name of the fallback adapter used
            is_embedding: Whether this was an embedding request
        """
        # Update global metrics
        if is_embedding:
            self.metrics["embed_fallback_count"] = self.metrics.get("embed_fallback_count", 0) + 1
        else:
            self.metrics["fallback_count"] += 1
            
        # Update adapter-specific metrics
        if original_adapter not in self.metrics["adapters"]:
            self.metrics["adapters"][original_adapter] = {}
            
        adapter_metrics = self.metrics["adapters"][original_adapter]
        
        if is_embedding:
            key = "embed_fallbacks"
        else:
            key = "fallbacks"
            
        if key not in adapter_metrics:
            adapter_metrics[key] = {}
            
        if fallback_adapter not in adapter_metrics[key]:
            adapter_metrics[key][fallback_adapter] = 0
            
        adapter_metrics[key][fallback_adapter] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics.
        
        Returns:
            Dictionary of metrics
        """
        # Calculate uptime
        uptime = time.time() - self.metrics["start_time"]
        metrics = self.metrics.copy()
        metrics["uptime"] = uptime
        
        # Calculate requests per minute if uptime > 0
        if uptime > 0:
            minutes = uptime / 60
            metrics["requests_per_minute"] = metrics["total_requests"] / minutes
            metrics["tokens_per_minute"] = metrics["total_tokens"] / minutes
            
        return metrics


# Singleton instance
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """
    Get the metrics collector singleton.
    
    Returns:
        MetricsCollector instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector