#!/usr/bin/env python3
"""
Issue Detector Module

This module provides functionality for detecting issues in component health.
"""

from typing import Dict, Any, Optional

from ..logging_integration import get_logger, LogCategory
from .health import ComponentHealth, HealthStatus
from .alerts import Alert, AlertSeverity, AlertManager

# Configure logger
logger = get_logger("tekton.monitoring.detector")


class IssueDetector:
    """Detects issues in component health metrics."""
    
    def __init__(self, alert_manager: AlertManager):
        """
        Initialize issue detector.
        
        Args:
            alert_manager: Alert manager for creating alerts
        """
        self.alert_manager = alert_manager
        
    def check_component(self, component: ComponentHealth) -> None:
        """
        Check for issues with a component.
        
        Args:
            component: Component to check
        """
        self._check_cpu_usage(component)
        self._check_memory_usage(component)
        self._check_error_rate(component)
        self._check_heartbeat(component)
        
    def _check_cpu_usage(self, component: ComponentHealth) -> None:
        """
        Check CPU usage.
        
        Args:
            component: Component to check
        """
        if "cpu_usage" in component.metrics:
            cpu_usage = component.metrics["cpu_usage"]
            if cpu_usage > 0.9 and component.status != HealthStatus.UNHEALTHY:
                alert = Alert(
                    severity=AlertSeverity.ERROR,
                    title="Critical CPU Usage",
                    description=f"Component {component.component_id} has critical CPU usage ({cpu_usage:.0%})",
                    component_id=component.component_id
                )
                self.alert_manager.add_alert(alert)
                component.add_issue(f"Critical CPU usage: {cpu_usage:.0%}")
            elif cpu_usage > 0.7 and component.status != HealthStatus.DEGRADED:
                alert = Alert(
                    severity=AlertSeverity.WARNING,
                    title="High CPU Usage",
                    description=f"Component {component.component_id} has high CPU usage ({cpu_usage:.0%})",
                    component_id=component.component_id
                )
                self.alert_manager.add_alert(alert)
                component.add_issue(f"High CPU usage: {cpu_usage:.0%}")
                
    def _check_memory_usage(self, component: ComponentHealth) -> None:
        """
        Check memory usage.
        
        Args:
            component: Component to check
        """
        if "memory_usage" in component.metrics:
            memory_mb = component.metrics["memory_usage"] / (1024 * 1024)
            if memory_mb > 1000:  # 1GB
                alert = Alert(
                    severity=AlertSeverity.WARNING,
                    title="High Memory Usage",
                    description=f"Component {component.component_id} has high memory usage ({memory_mb:.0f} MB)",
                    component_id=component.component_id
                )
                self.alert_manager.add_alert(alert)
                component.add_issue(f"High memory usage: {memory_mb:.0f} MB")
                
    def _check_error_rate(self, component: ComponentHealth) -> None:
        """
        Check error rate.
        
        Args:
            component: Component to check
        """
        if "error_count" in component.metrics and "request_count" in component.metrics:
            if component.metrics["request_count"] > 0:
                error_rate = component.metrics["error_count"] / component.metrics["request_count"]
                if error_rate > 0.1:  # 10%
                    alert = Alert(
                        severity=AlertSeverity.ERROR,
                        title="High Error Rate",
                        description=f"Component {component.component_id} has high error rate ({error_rate:.0%})",
                        component_id=component.component_id
                    )
                    self.alert_manager.add_alert(alert)
                    component.add_issue(f"High error rate: {error_rate:.0%}")
                    
    def _check_heartbeat(self, component: ComponentHealth) -> None:
        """
        Check heartbeat.
        
        Args:
            component: Component to check
        """
        if component.last_heartbeat:
            import time
            heartbeat_age = time.time() - component.last_heartbeat
            if heartbeat_age > 60:  # 1 minute
                alert = Alert(
                    severity=AlertSeverity.ERROR,
                    title="Missing Heartbeat",
                    description=f"Component {component.component_id} has not sent a heartbeat in {heartbeat_age:.0f} seconds",
                    component_id=component.component_id
                )
                self.alert_manager.add_alert(alert)
                component.add_issue(f"Missing heartbeat: {heartbeat_age:.0f} seconds")