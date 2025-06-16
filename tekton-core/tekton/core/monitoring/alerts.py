#!/usr/bin/env python3
"""
Alerts Module

This module provides classes for managing alerts and notifications.
"""

import time
from enum import Enum
from typing import Dict, Any, Optional, List, Callable

from ..logging_integration import get_logger, LogCategory

# Configure logger
logger = get_logger("tekton.monitoring.alerts")


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Alert:
    """Alert for notification of issues."""
    
    def __init__(self,
                severity: AlertSeverity,
                title: str,
                description: str,
                component_id: Optional[str] = None,
                timestamp: Optional[float] = None,
                source: str = "monitoring"):
        """
        Initialize an alert.
        
        Args:
            severity: Alert severity
            title: Alert title
            description: Alert description
            component_id: Optional component ID
            timestamp: Optional timestamp (defaults to current time)
            source: Alert source
        """
        self.severity = severity
        self.title = title
        self.description = description
        self.component_id = component_id
        self.timestamp = timestamp or time.time()
        self.source = source
        self.id = f"{int(self.timestamp)}_{component_id or 'system'}"
        self.acknowledged = False
        self.resolved = False
        self.resolved_timestamp = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "id": self.id,
            "severity": self.severity.value if isinstance(self.severity, AlertSeverity) else self.severity,
            "title": self.title,
            "description": self.description,
            "component_id": self.component_id,
            "timestamp": self.timestamp,
            "source": self.source,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
            "resolved_timestamp": self.resolved_timestamp
        }
        
    def acknowledge(self) -> None:
        """Acknowledge the alert."""
        self.acknowledged = True
        
    def resolve(self) -> None:
        """Resolve the alert."""
        self.resolved = True
        self.resolved_timestamp = time.time()


class AlertManager:
    """Manager for alert handling and distribution."""
    
    def __init__(self, alert_retention_days: int = 7):
        """
        Initialize alert manager.
        
        Args:
            alert_retention_days: Number of days to retain resolved alerts
        """
        self.alerts: Dict[str, Alert] = {}
        self.alert_hooks: List[Callable[[Alert], None]] = []
        self.alert_retention_days = alert_retention_days
        
    def add_alert(self, alert: Alert) -> None:
        """
        Add an alert.
        
        Args:
            alert: Alert to add
        """
        self.alerts[alert.id] = alert
        self._trigger_alert_hooks(alert)
        
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolve an alert.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if the alert was resolved
        """
        if alert_id in self.alerts:
            self.alerts[alert_id].resolve()
            return True
        return False
        
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if the alert was acknowledged
        """
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledge()
            return True
        return False
        
    def get_alerts(self, 
                component_id: Optional[str] = None,
                include_resolved: bool = False,
                include_acknowledged: bool = True) -> List[Alert]:
        """
        Get alerts, optionally filtered.
        
        Args:
            component_id: Optional component ID
            include_resolved: Whether to include resolved alerts
            include_acknowledged: Whether to include acknowledged alerts
            
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
            
        # Filter by acknowledgment status if specified
        if not include_acknowledged:
            alerts = [a for a in alerts if not a.acknowledged]
            
        # Sort by timestamp, newest first
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
        
    def clean_up_alerts(self) -> int:
        """
        Clean up old resolved alerts.
        
        Returns:
            Number of alerts removed
        """
        cutoff_time = time.time() - (self.alert_retention_days * 24 * 60 * 60)
        alerts_to_remove = []
        
        for alert_id, alert in self.alerts.items():
            if alert.resolved and alert.resolved_timestamp and alert.resolved_timestamp < cutoff_time:
                alerts_to_remove.append(alert_id)
                
        for alert_id in alerts_to_remove:
            del self.alerts[alert_id]
            
        return len(alerts_to_remove)
        
    def register_alert_hook(self, hook: Callable[[Alert], None]) -> None:
        """
        Register a hook to be called when an alert is created.
        
        Args:
            hook: Function to call with the alert
        """
        self.alert_hooks.append(hook)
        
    def _trigger_alert_hooks(self, alert: Alert) -> None:
        """
        Trigger alert hooks.
        
        Args:
            alert: Alert that was created
        """
        for hook in self.alert_hooks:
            try:
                hook(alert)
            except Exception as e:
                logger.error(
                    f"Error in alert hook: {e}",
                    category=LogCategory.SYSTEM,
                    exception=e
                )
                
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary of alerts
        """
        return {alert_id: alert.to_dict() for alert_id, alert in self.alerts.items()}