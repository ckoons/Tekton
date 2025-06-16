#!/usr/bin/env python3
"""
Health Status Module

This module provides classes for tracking and managing component health.
"""

import time
from enum import Enum
from typing import Dict, List, Any, Optional, Set

from ..logging_integration import get_logger, LogCategory
from ..lifecycle import ComponentState

# Configure logger
logger = get_logger("tekton.monitoring.health")


class HealthStatus(Enum):
    """Health status for components and systems."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentHealth:
    """Health information for a component."""
    
    def __init__(self,
                component_id: str,
                component_name: str,
                component_type: str,
                status: HealthStatus = HealthStatus.UNKNOWN,
                last_heartbeat: Optional[float] = None,
                state: Optional[str] = None,
                metrics: Optional[Dict[str, float]] = None,
                dependencies: Optional[List[str]] = None):
        """
        Initialize component health.
        
        Args:
            component_id: Component ID
            component_name: Component name
            component_type: Component type
            status: Health status
            last_heartbeat: Optional timestamp of last heartbeat
            state: Optional component state
            metrics: Optional component metrics
            dependencies: Optional list of dependencies
        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type
        self.status = status
        self.last_heartbeat = last_heartbeat
        self.state = state
        self.metrics = metrics or {}
        self.dependencies = dependencies or []
        self.issues = []
        self.last_updated = time.time()
        
    def update_status(self, 
                    status: HealthStatus, 
                    state: Optional[str] = None,
                    last_heartbeat: Optional[float] = None,
                    metrics: Optional[Dict[str, float]] = None) -> None:
        """
        Update component status.
        
        Args:
            status: New health status
            state: Optional new state
            last_heartbeat: Optional new last heartbeat timestamp
            metrics: Optional new metrics
        """
        self.status = status
        if state:
            self.state = state
        if last_heartbeat:
            self.last_heartbeat = last_heartbeat
        if metrics:
            self.metrics.update(metrics)
        self.last_updated = time.time()
        
    def add_issue(self, issue: str) -> None:
        """
        Add an issue to the component.
        
        Args:
            issue: Issue description
        """
        self.issues.append({
            "description": issue,
            "timestamp": time.time()
        })
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert component health to dictionary."""
        return {
            "component_id": self.component_id,
            "component_name": self.component_name,
            "component_type": self.component_type,
            "status": self.status.value if isinstance(self.status, HealthStatus) else self.status,
            "last_heartbeat": self.last_heartbeat,
            "state": self.state,
            "metrics": self.metrics,
            "dependencies": self.dependencies,
            "issues": self.issues,
            "last_updated": self.last_updated
        }


def state_to_health_status(state: str) -> HealthStatus:
    """
    Convert component state to health status.
    
    Args:
        state: Component state
        
    Returns:
        Health status
    """
    if state == ComponentState.READY.value or state == ComponentState.ACTIVE.value:
        return HealthStatus.HEALTHY
    elif state == ComponentState.DEGRADED.value or state == ComponentState.ERROR.value:
        return HealthStatus.DEGRADED
    elif state == ComponentState.FAILED.value:
        return HealthStatus.UNHEALTHY
    else:
        return HealthStatus.UNKNOWN


class SystemHealth:
    """System-wide health information."""
    
    def __init__(self):
        """Initialize system health."""
        self.components: Dict[str, ComponentHealth] = {}
        self.alerts: Dict[str, Any] = {}  # Will be populated from alerts module
        self.overall_status = HealthStatus.UNKNOWN
        self.metrics = {
            "healthy_components": 0,
            "degraded_components": 0,
            "unhealthy_components": 0,
            "total_components": 0,
            "active_alerts": 0
        }
        self.last_updated = time.time()
        
    def add_component(self, component: ComponentHealth) -> None:
        """
        Add a component to system health.
        
        Args:
            component: Component health
        """
        self.components[component.component_id] = component
        self._update_metrics()
        
    def update_component(self, 
                        component_id: str, 
                        status: HealthStatus,
                        **kwargs) -> None:
        """
        Update a component's status.
        
        Args:
            component_id: Component ID
            status: New health status
            **kwargs: Additional arguments for update_status
        """
        if component_id not in self.components:
            logger.warning(
                f"Cannot update unknown component: {component_id}",
                category=LogCategory.SYSTEM
            )
            return
            
        self.components[component_id].update_status(status, **kwargs)
        self._update_metrics()
        
    def add_alert(self, alert: Any) -> None:
        """
        Add an alert to system health.
        
        Args:
            alert: Alert
        """
        self.alerts[alert.id] = alert
        self._update_metrics()
        
    def resolve_alert(self, alert_id: str) -> None:
        """
        Resolve an alert.
        
        Args:
            alert_id: Alert ID
        """
        if alert_id in self.alerts:
            self.alerts[alert_id].resolve()
            self._update_metrics()
        
    def get_component(self, component_id: str) -> Optional[ComponentHealth]:
        """
        Get a component by ID.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component health or None if not found
        """
        return self.components.get(component_id)
        
    def get_alerts(self, 
                component_id: Optional[str] = None, 
                include_resolved: bool = False) -> List[Any]:
        """
        Get alerts, optionally filtered by component.
        
        Args:
            component_id: Optional component ID
            include_resolved: Whether to include resolved alerts
            
        Returns:
            List of alerts
        """
        alerts = list(self.alerts.values())
        
        # Filter by component if specified
        if component_id:
            alerts = [a for a in alerts if a.component_id == component_id]
            
        # Filter by resolution status if specified
        if not include_resolved:
            alerts = [a for a in alerts if not a.resolved]
            
        # Sort by timestamp, newest first
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
        
    def _update_metrics(self) -> None:
        """Update system metrics."""
        # Count components by status
        healthy_count = sum(1 for c in self.components.values() if c.status == HealthStatus.HEALTHY)
        degraded_count = sum(1 for c in self.components.values() if c.status == HealthStatus.DEGRADED)
        unhealthy_count = sum(1 for c in self.components.values() if c.status == HealthStatus.UNHEALTHY)
        
        # Count active alerts
        active_alerts = sum(1 for a in self.alerts.values() if not a.resolved)
        
        # Update metrics
        self.metrics = {
            "healthy_components": healthy_count,
            "degraded_components": degraded_count,
            "unhealthy_components": unhealthy_count,
            "total_components": len(self.components),
            "active_alerts": active_alerts
        }
        
        # Update overall status
        if unhealthy_count > 0:
            self.overall_status = HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            self.overall_status = HealthStatus.DEGRADED
        elif healthy_count > 0:
            self.overall_status = HealthStatus.HEALTHY
        else:
            self.overall_status = HealthStatus.UNKNOWN
            
        self.last_updated = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert system health to dictionary."""
        return {
            "overall_status": self.overall_status.value if isinstance(self.overall_status, HealthStatus) else self.overall_status,
            "metrics": self.metrics,
            "components": {cid: c.to_dict() for cid, c in self.components.items()},
            "alerts": {aid: a.to_dict() for aid, a in self.alerts.items()},
            "last_updated": self.last_updated
        }