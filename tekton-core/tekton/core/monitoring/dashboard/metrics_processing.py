#!/usr/bin/env python3
"""
Metrics Processing Module

This module provides functions for processing and calculating metrics for components and the system.
"""

from typing import Dict, Any

from ...lifecycle import ComponentState
from ..health import HealthStatus
from ..alerts import AlertSeverity


def calculate_health_score(component: Dict[str, Any]) -> float:
    """Calculate health score (0-100) for a component.
    
    Args:
        component: Component data
        
    Returns:
        Health score (0-100)
    """
    state = component.get("state", "unknown")
    
    # Base score depends on state
    if state == ComponentState.READY.value:
        base_score = 90
    elif state == ComponentState.ACTIVE.value:
        base_score = 90
    elif state == ComponentState.DEGRADED.value:
        base_score = 50
    elif state == ComponentState.ERROR.value:
        base_score = 30
    elif state == ComponentState.FAILED.value:
        base_score = 10
    else:
        base_score = 70
        
    # Adjust based on metrics if available
    metrics = component.get("metrics", {})
    
    # Deduct points for high CPU
    if "cpu_usage" in metrics:
        cpu_usage = metrics["cpu_usage"]
        if cpu_usage > 0.9:
            base_score -= 20
        elif cpu_usage > 0.8:
            base_score -= 10
        elif cpu_usage > 0.7:
            base_score -= 5
            
    # Deduct points for high memory
    if "memory_usage" in metrics:
        memory_usage = metrics["memory_usage"]
        if isinstance(memory_usage, float) and memory_usage > 0.9:
            base_score -= 15
        elif isinstance(memory_usage, float) and memory_usage > 0.8:
            base_score -= 10
            
    # Deduct points for high error rate
    if "error_rate" in metrics:
        error_rate = metrics["error_rate"]
        if error_rate > 0.1:
            base_score -= 25
        elif error_rate > 0.05:
            base_score -= 15
        elif error_rate > 0.01:
            base_score -= 5
            
    # Ensure score is between 0 and 100
    return max(0, min(100, base_score))


def generate_health_metrics(dashboard):
    """Generate health metrics for monitoring.
    
    Args:
        dashboard: The dashboard instance
    """
    # Get component metrics
    component_count = len(dashboard.component_status)
    healthy_count = sum(1 for status in dashboard.component_status.values() 
                       if status["status"] == HealthStatus.HEALTHY.value)
    degraded_count = sum(1 for status in dashboard.component_status.values() 
                        if status["status"] == HealthStatus.DEGRADED.value)
    unhealthy_count = sum(1 for status in dashboard.component_status.values() 
                        if status["status"] == HealthStatus.UNHEALTHY.value)
    
    # Get alert metrics
    total_alerts = len(dashboard.alerts)
    active_alerts = sum(1 for alert in dashboard.alerts if not alert.resolved)
    critical_alerts = sum(1 for alert in dashboard.alerts 
                        if not alert.resolved and alert.severity == AlertSeverity.CRITICAL)
    
    # Calculate average health
    average_health = sum(status.get("health", 0) for status in dashboard.component_status.values())
    average_health = average_health / component_count if component_count > 0 else 0
    
    # Update metrics
    metrics = {
        "healthy_components": healthy_count,
        "degraded_components": degraded_count,
        "unhealthy_components": unhealthy_count,
        "total_components": component_count,
        "alert_count": active_alerts,
        "critical_alert_count": critical_alerts,
        "average_health": average_health
    }
    
    # Update system health metrics
    dashboard.system_health.metrics.update(metrics)
    
    # Update registry metrics
    registry = dashboard.metrics_manager.registry
    for name, value in metrics.items():
        gauge = registry.get(name)
        if gauge:
            gauge.set(value)
        else:
            registry.create_gauge(
                name=name,
                description=f"Health metric: {name}",
                category="health"
            ).set(value)