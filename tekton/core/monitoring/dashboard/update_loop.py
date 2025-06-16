#!/usr/bin/env python3
"""
Update Loop Module

This module provides functions for updating component status and dependency information.
"""

import time
import random
from typing import Dict, Any

from ...lifecycle import ComponentState
from ..health import HealthStatus, ComponentHealth

from .metrics_processing import calculate_health_score
from .issue_detection import detect_component_issues


def update_component_status(dashboard, component: Dict[str, Any]):
    """Update status of a single component.
    
    Args:
        dashboard: The dashboard instance
        component: Component data
    """
    component_id = component.get("component_id")
    if not component_id:
        return
        
    # Import dependency to avoid circular imports
    from ..health import state_to_health_status
        
    # Extract component state
    state = component.get("state")
    status = state_to_health_status(state)
        
    # Get or create component
    comp_health = dashboard.system_health.get_component(component_id)
    if comp_health:
        # Update existing component
        comp_health.update_status(
            status=status,
            state=state,
            last_heartbeat=component.get("last_heartbeat"),
            metrics=component.get("metrics")
        )
    else:
        # Create new component
        comp_health = ComponentHealth(
            component_id=component_id,
            component_name=component.get("component_name", component_id),
            component_type=component.get("component_type", "unknown"),
            status=status,
            state=state,
            last_heartbeat=component.get("last_heartbeat"),
            metrics=component.get("metrics"),
            dependencies=component.get("dependencies", [])
        )
        dashboard.system_health.add_component(comp_health)
                        
    # Store component status
    dashboard.component_status[component_id] = {
        "id": component_id,
        "name": component.get("component_name", component_id),
        "type": component.get("component_type", "unknown"),
        "state": state,
        "status": status.value,
        "last_heartbeat": component.get("last_heartbeat"),
        "health": calculate_health_score(component),
        "metrics": component.get("metrics", {}),
        "issues": detect_component_issues(dashboard, component),
        "dependencies": component.get("dependencies", [])
    }
    
    # Check for issues
    dashboard.issue_detector.check_component(comp_health)


def update_dependency_graph(dashboard):
    """Update the component dependency graph.
    
    Args:
        dashboard: The dashboard instance
    """
    # Initialize dependency graph
    dashboard.dependency_graph = {}
    
    # Add all components to the graph
    for component_id in dashboard.component_status:
        dashboard.dependency_graph[component_id] = {
            "dependencies": [],
            "dependents": []
        }
        
    # Add dependency relationships
    for component_id, status in dashboard.component_status.items():
        for dependency in status.get("dependencies", []):
            if dependency in dashboard.dependency_graph:
                # Add dependency
                dashboard.dependency_graph[component_id]["dependencies"].append(dependency)
                # Add dependent relationship
                dashboard.dependency_graph[dependency]["dependents"].append(component_id)


def update_mock_data(dashboard):
    """Update mock data for example.
    
    Args:
        dashboard: The dashboard instance
    """
    # Add mock components if none exist
    if not dashboard.component_status:
        # Create initial mock components
        _initialize_mock_components(dashboard)
    else:
        # Update existing mock data
        _update_existing_mock_data(dashboard)


def _initialize_mock_components(dashboard):
    """Initialize mock components for testing/demo purposes.
    
    Args:
        dashboard: The dashboard instance
    """
    # Mock component 1
    dashboard.component_status["example.service1"] = {
        "id": "example.service1",
        "name": "Example Service 1",
        "type": "service",
        "state": ComponentState.READY.value,
        "status": HealthStatus.HEALTHY.value,
        "last_heartbeat": time.time(),
        "health": 95,
        "metrics": {
            "cpu_usage": 0.2,
            "memory_usage": 0.3,
            "request_count": 1000,
            "error_rate": 0.01,
            "request_latency": 200
        },
        "issues": [],
        "dependencies": ["example.database"]
    }
    
    # Mock component 2
    dashboard.component_status["example.service2"] = {
        "id": "example.service2",
        "name": "Example Service 2",
        "type": "service",
        "state": ComponentState.DEGRADED.value,
        "status": HealthStatus.DEGRADED.value,
        "last_heartbeat": time.time(),
        "health": 60,
        "metrics": {
            "cpu_usage": 0.8,
            "memory_usage": 0.7,
            "request_count": 500,
            "error_rate": 0.08,
            "request_latency": 800
        },
        "issues": [
            {
                "type": "performance_issue",
                "severity": "warning",
                "message": "Elevated error rate: 8.0%"
            }
        ],
        "dependencies": ["example.database"]
    }
    
    # Mock component 3
    dashboard.component_status["example.database"] = {
        "id": "example.database",
        "name": "Example Database",
        "type": "database",
        "state": ComponentState.READY.value,
        "status": HealthStatus.HEALTHY.value,
        "last_heartbeat": time.time(),
        "health": 90,
        "metrics": {
            "cpu_usage": 0.4,
            "memory_usage": 0.5,
            "connection_count": 20,
            "query_count": 5000,
            "query_latency": 50
        },
        "issues": [],
        "dependencies": []
    }
    
    # Add to system health
    for component_id, status in dashboard.component_status.items():
        dashboard.system_health.add_component(
            ComponentHealth(
                component_id=component_id,
                component_name=status["name"],
                component_type=status["type"],
                status=HealthStatus(status["status"]),
                state=status["state"],
                last_heartbeat=status["last_heartbeat"],
                metrics=status["metrics"],
                dependencies=status["dependencies"]
            )
        )
    
    # Add an alert
    dashboard._generate_alert(
        severity=HealthStatus.DEGRADED,
        title="High CPU Usage",
        description="Component example.service2 has high CPU usage (80%)",
        component_id="example.service2"
    )


def _update_existing_mock_data(dashboard):
    """Update existing mock components with random variations.
    
    Args:
        dashboard: The dashboard instance
    """
    # Update each component
    for component_id, status in dashboard.component_status.items():
        # Randomly update metrics
        metrics = status["metrics"]
        
        if "cpu_usage" in metrics:
            metrics["cpu_usage"] += (random.random() - 0.5) * 0.1
            metrics["cpu_usage"] = max(0.0, min(1.0, metrics["cpu_usage"]))
            
        if "memory_usage" in metrics:
            metrics["memory_usage"] += (random.random() - 0.5) * 0.1
            metrics["memory_usage"] = max(0.0, min(1.0, metrics["memory_usage"]))
            
        if "request_latency" in metrics:
            metrics["request_latency"] += (random.random() - 0.5) * 50
            metrics["request_latency"] = max(10, metrics["request_latency"])
            
        if "error_rate" in metrics:
            metrics["error_rate"] += (random.random() - 0.5) * 0.02
            metrics["error_rate"] = max(0.0, min(1.0, metrics["error_rate"]))
            
        # Update health score
        status["health"] = calculate_health_score({
            "component_id": component_id, 
            "state": status["state"], 
            "metrics": metrics
        })
        
        # Update status based on metrics
        if metrics.get("cpu_usage", 0) > 0.9 or metrics.get("error_rate", 0) > 0.1:
            status["state"] = ComponentState.ERROR.value
            status["status"] = HealthStatus.UNHEALTHY.value
        elif metrics.get("cpu_usage", 0) > 0.7 or metrics.get("error_rate", 0) > 0.05:
            status["state"] = ComponentState.DEGRADED.value
            status["status"] = HealthStatus.DEGRADED.value
        else:
            status["state"] = ComponentState.READY.value
            status["status"] = HealthStatus.HEALTHY.value
            
        # Update last heartbeat
        status["last_heartbeat"] = time.time()
        
        # Update issues
        status["issues"] = detect_component_issues(
            dashboard, 
            {
                "component_id": component_id, 
                "state": status["state"], 
                "metrics": metrics
            }
        )
        
        # Update component in system health
        comp_health = dashboard.system_health.get_component(component_id)
        if comp_health:
            comp_health.update_status(
                status=HealthStatus(status["status"]),
                state=status["state"],
                last_heartbeat=status["last_heartbeat"],
                metrics=status["metrics"]
            )
            
            # Check for issues
            dashboard.issue_detector.check_component(comp_health)