#!/usr/bin/env python3
"""
Health Metrics Component

This module provides health metrics calculation and analysis for the dashboard.
"""

import time
from typing import Dict, List, Any, Optional, Callable

from ...logging_integration import get_logger, LogCategory
from ..health import HealthStatus, ComponentHealth, SystemHealth, state_to_health_status

# Configure logger
logger = get_logger("tekton.monitoring.dashboard.health")


class HealthMetrics:
    """
    Health metrics calculation and management.
    
    Provides functions for calculating component and system health scores,
    generating health metrics, and detecting issues.
    """
    
    def __init__(self, dashboard=None):
        """
        Initialize health metrics.
        
        Args:
            dashboard: Dashboard instance
        """
        self.dashboard = dashboard
        
    def update_system_health(self):
        """Update system health metrics."""
        if not self.dashboard:
            return
            
        system_health = self.dashboard.system_health
        component_status = self.dashboard.component_status
        
        # Count components by status
        total = len(component_status)
        healthy = sum(1 for c in component_status.values() if c.get("status") == HealthStatus.HEALTHY)
        degraded = sum(1 for c in component_status.values() if c.get("status") == HealthStatus.DEGRADED)
        unhealthy = sum(1 for c in component_status.values() if c.get("status") == HealthStatus.UNHEALTHY)
        unknown = total - healthy - degraded - unhealthy
        
        # Count active alerts
        active_alerts = len(self.dashboard.get_alerts())
        
        # Update metrics
        system_health.metrics.update({
            "total_components": total,
            "healthy_components": healthy,
            "degraded_components": degraded,
            "unhealthy_components": unhealthy,
            "unknown_components": unknown,
            "active_alerts": active_alerts,
            "health_percentage": (healthy / total * 100) if total > 0 else 100.0
        })
        
        # Update overall status based on component counts
        if unhealthy > 0:
            system_health.overall_status = HealthStatus.UNHEALTHY
        elif degraded > 0:
            system_health.overall_status = HealthStatus.DEGRADED
        else:
            system_health.overall_status = HealthStatus.HEALTHY


def generate_component_health(component_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate health data for a component.
    
    Args:
        component_data: Component data dictionary
        
    Returns:
        Component health dictionary
    """
    component_id = component_data.get("component_id", "unknown")
    component_name = component_data.get("component_name", component_id)
    component_type = component_data.get("component_type", "unknown")
    state = component_data.get("state", "unknown")
    
    # Calculate health status
    status = state_to_health_status(state)
    
    # Calculate health score
    health = calculate_health_score(component_data)
    
    # Extract metrics
    metrics = component_data.get("metrics", {})
    
    # Create component health
    return {
        "component_id": component_id,
        "component_name": component_name,
        "component_type": component_type,
        "state": state,
        "status": status,
        "health": health,
        "metrics": metrics,
        "last_updated": time.time()
    }


def calculate_health_score(component_data: Dict[str, Any]) -> float:
    """Calculate a health score for a component.
    
    Args:
        component_data: Component data dictionary
        
    Returns:
        Health score (0.0 to 1.0)
    """
    # Get component state
    state = component_data.get("state", "unknown")
    status = state_to_health_status(state)
    
    # Base score based on status
    if status == HealthStatus.HEALTHY:
        base_score = 1.0
    elif status == HealthStatus.DEGRADED:
        base_score = 0.5
    elif status == HealthStatus.UNHEALTHY:
        base_score = 0.0
    else:  # UNKNOWN
        base_score = 0.0
    
    # Get metrics
    metrics = component_data.get("metrics", {})
    
    # Adjust score based on metrics
    if metrics:
        # Error rate adjustments
        error_rate = metrics.get("error_rate", 0.0)
        error_adjustment = max(0.0, 0.5 - error_rate / 2)  # Larger error rates reduce score
        
        # Latency adjustments
        latency = metrics.get("latency", 0.0)
        latency_threshold = metrics.get("latency_threshold", 1000.0)  # Default 1000ms
        latency_adjustment = max(0.0, 0.5 - min(latency / latency_threshold, 1.0) / 2)
        
        # Resource usage adjustments
        cpu_usage = metrics.get("cpu_usage", 0.0)
        memory_usage = metrics.get("memory_usage", 0.0)
        resource_adjustment = max(0.0, 0.5 - (cpu_usage + memory_usage) / 400)  # Average % / 2
        
        # Success rate adjustment
        success_rate = metrics.get("success_rate", 100.0)
        success_adjustment = success_rate / 200  # Half weight for success rate
        
        # Calculate final score with adjustments
        adjustments = [error_adjustment, latency_adjustment, resource_adjustment, success_adjustment]
        adjustment_count = sum(1 for adj in adjustments if adj > 0)
        
        if adjustment_count > 0:
            avg_adjustment = sum(adjustments) / adjustment_count
            return max(0.0, min(1.0, base_score * avg_adjustment))
    
    # Return base score if no adjustments
    return base_score
