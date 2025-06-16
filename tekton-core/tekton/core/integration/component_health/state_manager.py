#!/usr/bin/env python3
"""
State Manager Module

Manages component state transitions and health status mapping.
"""

import logging
from typing import Dict, Any, Optional

from ...lifecycle import ComponentState
from ...monitoring_dashboard import HealthStatus, Alert, AlertSeverity
from ...logging_integration import LogCategory

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages component state transitions and health status mapping.
    """
    
    def __init__(self, 
                component_id: str, 
                component_name: str, 
                component_type: str,
                metrics_manager,
                logger,
                dashboard):
        """
        Initialize state manager.
        
        Args:
            component_id: Component ID
            component_name: Human-readable name
            component_type: Component type
            metrics_manager: Metrics manager instance
            logger: Logger instance
            dashboard: Dashboard instance
        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type
        self.metrics_manager = metrics_manager
        self.logger = logger
        self.dashboard = dashboard
        self.state = ComponentState.INITIALIZING.value
        
    def update_state(self, new_state: str, reason: str = None, details: str = None) -> bool:
        """
        Update component state.
        
        Args:
            new_state: New state
            reason: Optional reason for state change
            details: Optional details about state change
            
        Returns:
            True if state was updated
        """
        # Validate state
        if not ComponentState.validate_transition(self.state, new_state):
            self.logger.warning(
                f"Invalid state transition: {self.state} -> {new_state}",
                category=LogCategory.LIFECYCLE,
                context={
                    "reason": reason,
                    "details": details
                }
            )
            return False
            
        # Record previous state
        old_state = self.state
        
        # Update state
        self.state = new_state
        
        # Map state to numeric value for metrics
        state_values = {
            ComponentState.UNKNOWN.value: 0,
            ComponentState.INITIALIZING.value: 1,
            ComponentState.READY.value: 2,
            ComponentState.ACTIVE.value: 3,
            ComponentState.DEGRADED.value: 4,
            ComponentState.ERROR.value: 5,
            ComponentState.FAILED.value: 6,
            ComponentState.STOPPING.value: 7,
            ComponentState.RESTARTING.value: 8,
            ComponentState.INACTIVE.value: 9
        }
        
        # Update state metric
        state_metric = self.metrics_manager.registry.get("state")
        if state_metric:
            state_metric.set(state_values.get(new_state, 0))
            
        # Log state change
        self.logger.info(
            f"Component state changed: {old_state} -> {new_state}",
            category=LogCategory.LIFECYCLE,
            context={
                "reason": reason,
                "details": details
            }
        )
        
        # Update health status in dashboard
        health_status = self._state_to_health_status(new_state)
        component = self.dashboard.get_system_health().get_component(self.component_id)
        if component:
            component.update_status(health_status, new_state)
        
        # Create alert for significant state changes
        if new_state in [ComponentState.DEGRADED.value, ComponentState.ERROR.value, ComponentState.FAILED.value]:
            severity = AlertSeverity.WARNING if new_state == ComponentState.DEGRADED.value else AlertSeverity.ERROR
            alert = Alert(
                severity=severity,
                title=f"Component {self.component_name} state changed to {new_state}",
                description=f"Component {self.component_id} state changed from {old_state} to {new_state}" +
                           (f": {details}" if details else ""),
                component_id=self.component_id
            )
            self.dashboard.get_system_health().add_alert(alert)
            
        return True
        
    def _state_to_health_status(self, state: str) -> HealthStatus:
        """
        Convert component state to health status.
        
        Args:
            state: Component state
            
        Returns:
            Health status
        """
        if state in [ComponentState.READY.value, ComponentState.ACTIVE.value]:
            return HealthStatus.HEALTHY
        elif state in [ComponentState.DEGRADED.value, ComponentState.ERROR.value, ComponentState.INACTIVE.value]:
            return HealthStatus.DEGRADED
        elif state in [ComponentState.FAILED.value]:
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.UNKNOWN
