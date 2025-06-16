#!/usr/bin/env python3
"""
Issue Detection Module

This module provides functions for detecting issues with components and the system.
"""

import time
from typing import Dict, List, Any, Set

from ...lifecycle import ComponentState
from ..health import HealthStatus
from ..alerts import AlertSeverity


def check_for_issues(dashboard):
    """Check for system-wide issues and generate alerts.
    
    Args:
        dashboard: The dashboard instance
    """
    # Check for dependency cycles
    cycles = detect_dependency_cycles(dashboard)
    if cycles:
        for cycle in cycles:
            cycle_str = " -> ".join(cycle)
            dashboard._generate_alert(
                severity=AlertSeverity.WARNING,
                title="Dependency Cycle Detected",
                description=f"Circular dependency detected: {cycle_str}",
                component_id=None
            )
            
    # Check for critical component failures
    for component_id, status in dashboard.component_status.items():
        if status["state"] == ComponentState.FAILED.value:
            # Count dependents
            dependent_count = len(dashboard.dependency_graph.get(component_id, {}).get("dependents", []))
            
            if dependent_count > 0:
                dashboard._generate_alert(
                    severity=AlertSeverity.CRITICAL,
                    title="Critical Component Failure",
                    description=f"Component {status['name']} has failed and has {dependent_count} dependent components",
                    component_id=component_id
                )
                
    # Check for performance issues
    high_latency_count = 0
    high_error_rate_count = 0
    
    for component_id, status in dashboard.component_status.items():
        metrics = status.get("metrics", {})
        
        if metrics.get("request_latency", 0) > 1000:  # Over 1 second
            high_latency_count += 1
            
        if metrics.get("error_rate", 0) > 0.05:  # Over 5%
            high_error_rate_count += 1
            
    if high_latency_count >= 3:
        dashboard._generate_alert(
            severity=AlertSeverity.WARNING,
            title="System-Wide Performance Issue",
            description=f"{high_latency_count} components experiencing high latency",
            component_id=None
        )
        
    if high_error_rate_count >= 2:
        dashboard._generate_alert(
            severity=AlertSeverity.WARNING,
            title="System-Wide Reliability Issue",
            description=f"{high_error_rate_count} components experiencing high error rates",
            component_id=None
        )


def detect_component_issues(dashboard, component: Dict[str, Any]) -> List[Dict[str, str]]:
    """Detect issues with a component.
    
    Args:
        dashboard: The dashboard instance
        component: Component data
        
    Returns:
        List of detected issues
    """
    issues = []
    component_id = component.get("component_id")
    
    # Check component state
    state = component.get("state")
    if state in [ComponentState.DEGRADED.value, ComponentState.ERROR.value, ComponentState.FAILED.value]:
        issues.append({
            "type": "state_issue", 
            "severity": "critical" if state == ComponentState.FAILED.value else "warning",
            "message": f"Component in {state} state"
        })
        
    # Check last heartbeat
    last_heartbeat = component.get("last_heartbeat")
    if last_heartbeat:
        time_since_hb = time.time() - last_heartbeat
        if time_since_hb > 60:
            issues.append({
                "type": "heartbeat_issue",
                "severity": "critical" if time_since_hb > 300 else "warning",
                "message": f"No heartbeat for {int(time_since_hb)} seconds"
            })
            
    # Check metrics for issues
    metrics = component.get("metrics", {})
    
    # Check CPU usage
    if "cpu_usage" in metrics:
        cpu_usage = metrics["cpu_usage"]
        if cpu_usage > 0.9:
            issues.append({
                "type": "resource_issue",
                "severity": "critical",
                "message": f"High CPU usage: {cpu_usage:.1%}"
            })
        elif cpu_usage > 0.8:
            issues.append({
                "type": "resource_issue",
                "severity": "warning",
                "message": f"Elevated CPU usage: {cpu_usage:.1%}"
            })
            
    # Check memory usage
    if "memory_usage" in metrics:
        memory_usage = metrics["memory_usage"]
        if isinstance(memory_usage, float) and memory_usage > 0.9:
            issues.append({
                "type": "resource_issue",
                "severity": "critical",
                "message": f"High memory usage: {memory_usage:.1%}"
            })
        elif isinstance(memory_usage, float) and memory_usage > 0.8:
            issues.append({
                "type": "resource_issue",
                "severity": "warning",
                "message": f"Elevated memory usage: {memory_usage:.1%}"
            })
            
    # Check error rate
    if "error_rate" in metrics:
        error_rate = metrics["error_rate"]
        if error_rate > 0.1:
            issues.append({
                "type": "performance_issue",
                "severity": "critical",
                "message": f"High error rate: {error_rate:.1%}"
            })
        elif error_rate > 0.05:
            issues.append({
                "type": "performance_issue",
                "severity": "warning",
                "message": f"Elevated error rate: {error_rate:.1%}"
            })
            
    # Check for missing dependencies
    if component_id in dashboard.dependency_graph:
        for dependency in dashboard.dependency_graph[component_id].get("dependencies", []):
            if dependency not in dashboard.component_status:
                issues.append({
                    "type": "dependency_issue",
                    "severity": "warning",
                    "message": f"Missing dependency: {dependency}"
                })
            elif dashboard.component_status[dependency]["status"] != HealthStatus.HEALTHY.value:
                issues.append({
                    "type": "dependency_issue",
                    "severity": "warning",
                    "message": f"Unhealthy dependency: {dependency} ({dashboard.component_status[dependency]['status']})"
                })
            
    return issues


def detect_dependency_cycles(dashboard) -> List[List[str]]:
    """Detect cycles in the dependency graph.
    
    Args:
        dashboard: The dashboard instance
        
    Returns:
        List of detected cycles
    """
    cycles = []
    visited = set()
    rec_stack = set()
    
    def dfs(node, path):
        if node in rec_stack:
            # Found a cycle
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return
            
        if node in visited:
            return
            
        visited.add(node)
        rec_stack.add(node)
        
        for dependency in dashboard.dependency_graph.get(node, {}).get("dependencies", []):
            dfs(dependency, path + [node])
            
        rec_stack.remove(node)
    
    # Run DFS from each node
    for node in dashboard.dependency_graph:
        if node not in visited:
            dfs(node, [])
            
    return cycles