#!/usr/bin/env python3
"""
Heartbeat Metrics Module

This module provides utilities for collecting component metrics.
"""

import time
import random
from typing import Dict, Any, Optional


async def collect_component_metrics(component_id: str, component_type: Optional[str] = None) -> Dict[str, float]:
    """
    Collect health metrics for a component.
    
    Args:
        component_id: Component ID
        component_type: Optional component type for type-specific metrics
        
    Returns:
        Dictionary of health metrics
    """
    # Base values - these would come from actual monitoring in a real implementation
    base_metrics = {
        "cpu_usage": 0.2 + random.random() * 0.1,        # 20-30% CPU
        "memory_usage": 0.3 + random.random() * 0.1,     # 30-40% Memory
        "request_latency": 50 + random.random() * 20,    # 50-70ms latency
        "error_rate": 0.01 + random.random() * 0.01,     # 1-2% error rate
        "throughput": 100 + random.random() * 20,        # 100-120 req/sec
    }
    
    # Apply component-type specific variations
    if component_type:
        if component_type == "database":
            base_metrics["cpu_usage"] += 0.1            # Higher CPU for DB
            base_metrics["memory_usage"] += 0.2         # Higher memory for DB
        elif component_type == "api":
            base_metrics["request_latency"] -= 20       # Lower latency for API
            base_metrics["throughput"] += 50            # Higher throughput for API
        elif component_type == "worker":
            base_metrics["cpu_usage"] += 0.15           # Higher CPU for workers
            base_metrics["request_latency"] = 0         # Workers don't handle requests
            base_metrics["throughput"] = 0              # Workers don't handle requests
    
    return base_metrics


def aggregate_health_metrics(component_health: Dict[str, Any], registrations: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregate health metrics across all components.
    
    Args:
        component_health: Dictionary of component health metrics
        registrations: Dictionary of component registrations
        
    Returns:
        Dictionary of aggregated metrics
    """
    result = {
        "timestamp": time.time(),
        "total_components": len(component_health),
        "healthy_components": 0,
        "degraded_components": 0,
        "failed_components": 0,
        "avg_cpu_usage": 0.0,
        "avg_memory_usage": 0.0,
        "avg_request_latency": 0.0,
        "avg_error_rate": 0.0,
        "components": {}
    }
    
    # No components, return empty stats
    if not component_health:
        return result
        
    # Calculate component statistics
    cpu_sum = 0.0
    memory_sum = 0.0
    latency_sum = 0.0
    error_rate_sum = 0.0
    component_count = 0
    
    from ..lifecycle import ComponentState
    
    for component_id, metrics in component_health.items():
        if component_id not in registrations:
            continue
            
        component = registrations[component_id]
        component_state = component.state
        
        # Get component-specific stats
        cpu = metrics.get("cpu_usage", 0.0)
        memory = metrics.get("memory_usage", 0.0)
        latency = metrics.get("request_latency", 0.0)
        error_rate = metrics.get("error_rate", 0.0)
        
        # Add to aggregates
        cpu_sum += cpu
        memory_sum += memory
        
        # Only count latency and error_rate for components that handle requests
        if component.component_type in ["api", "web", "service"]:
            latency_sum += latency
            error_rate_sum += error_rate
            
        # Count component status
        if ComponentState.is_active(component_state):
            result["healthy_components"] += 1
        elif ComponentState.is_degraded(component_state):
            result["degraded_components"] += 1
        elif ComponentState.is_terminal(component_state):
            result["failed_components"] += 1
            
        # Check if component needs attention
        needs_attention = False
        attention_reason = None
        
        if cpu > 0.85:
            needs_attention = True
            attention_reason = "High CPU usage"
        elif memory > 0.85:
            needs_attention = True
            attention_reason = "High memory usage"
        elif error_rate > 0.1:
            needs_attention = True
            attention_reason = "High error rate"
        elif ComponentState.is_degraded(component_state):
            needs_attention = True
            attention_reason = f"Component in degraded state: {component_state}"
        elif ComponentState.is_terminal(component_state):
            needs_attention = True
            attention_reason = f"Component in failed state: {component_state}"
        
        # Add component-specific data
        result["components"][component_id] = {
            "cpu_usage": cpu,
            "memory_usage": memory,
            "request_latency": latency,
            "error_rate": error_rate,
            "state": component_state,
            "needs_attention": needs_attention,
            "reason": attention_reason
        }
        
        component_count += 1
        
    # Calculate averages
    if component_count > 0:
        result["avg_cpu_usage"] = cpu_sum / component_count
        result["avg_memory_usage"] = memory_sum / component_count
        
        # Calculate service-specific averages
        service_count = sum(1 for cid, metrics in result["components"].items() 
                        if registrations[cid].component_type in ["api", "web", "service"])
                        
        if service_count > 0:
            result["avg_request_latency"] = latency_sum / service_count
            result["avg_error_rate"] = error_rate_sum / service_count
    
    return result