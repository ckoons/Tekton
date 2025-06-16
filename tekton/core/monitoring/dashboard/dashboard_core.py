#!/usr/bin/env python3
"""
Core Dashboard Module

This module provides the core functionality for the Tekton Health Dashboard.
"""

import json
import time
from typing import Dict, List, Any, Optional, Callable

from ...lifecycle import ComponentState
from ...logging_integration import get_logger, LogCategory
from ...metrics_integration import get_metrics_manager
from ..health import HealthStatus, ComponentHealth, SystemHealth, state_to_health_status
from ..alerts import Alert, AlertSeverity, AlertManager
from ..detector import IssueDetector

# Internal imports
from .resource_integration import get_resource_monitor
from .update_loop import update_component_status, update_mock_data, update_dependency_graph
from .issue_detection import check_for_issues, detect_component_issues, detect_dependency_cycles
from .metrics_processing import generate_health_metrics, calculate_health_score
from .spectral_analysis import run_spectral_analysis
from .web_interface import start_dashboard_server

# Configure logger
logger = get_logger("tekton.monitoring.dashboard")


class HealthDashboard:
    """
    Interactive health dashboard for Tekton components.
    
    Provides real-time monitoring, alerting, and visualization of component health,
    dependencies, and system metrics.
    """
    
    def __init__(self, 
                registry: Optional[Any] = None, 
                update_interval: float = 5.0,
                enable_resource_monitoring: bool = True):
        """
        Initialize the health dashboard.
        
        Args:
            registry: Optional component registry
            update_interval: Interval between updates in seconds
            enable_resource_monitoring: Whether to enable system resource monitoring
        """
        self.registry = registry
        self.update_interval = update_interval
        self.metrics_manager = get_metrics_manager("tekton.health_dashboard")
        self.component_status = {}
        self.alerts = []
        self.alert_handlers = []
        self.dependency_graph = {}
        self.update_task = None
        self.running = False
        self.spectral_analyzer = None
        self.resource_monitor = None
        self.resource_integration = None
        
        # Create system health
        self.system_health = SystemHealth()
        
        # Initialize alert manager 
        self.alert_manager = AlertManager(alert_retention_days=7)
        
        # Initialize issue detector
        self.issue_detector = IssueDetector(self.alert_manager)
        
        # Setup system health to use alerts from alert manager
        self.system_health.alerts = self.alert_manager.alerts
        
        # Configure logger
        self.logger = get_logger("tekton.monitoring.dashboard")
        
        # Try to import spectral analyzer
        try:
            from ...metrics.analysis.spectral_analyzer import EnhancedSpectralAnalyzer
            self.spectral_analyzer = EnhancedSpectralAnalyzer()
            self.logger.info("Enhanced spectral analyzer initialized")
        except ImportError:
            self.logger.warning("Enhanced spectral analyzer not available")
            self.spectral_analyzer = None
            
        # Initialize resource monitoring if enabled
        if enable_resource_monitoring:
            self._init_resource_monitoring()
            
    def _init_resource_monitoring(self):
        """Initialize the resource monitoring integration."""
        # Get resource monitor
        self.resource_monitor = get_resource_monitor()
        
        if self.resource_monitor:
            try:
                # Import integration class
                from ...resource_monitor import ResourceMonitorDashboardIntegration
                
                # Initialize integration
                self.resource_integration = ResourceMonitorDashboardIntegration(
                    self.resource_monitor,
                    dashboard_update_interval=self.update_interval
                )
                
                # Add alert handler to process resource alerts
                self.resource_monitor.add_alert_handler(self._resource_alert_handler)
                
                self.logger.info("Resource monitoring initialized")
            except ImportError:
                self.logger.warning("Resource monitor found but dashboard integration not available")
        else:
            self.logger.warning("Resource monitoring not available")
    
    def _resource_alert_handler(self, resource_name: str, level: str, value: float, threshold: float):
        """Handle alerts from the resource monitor.
        
        Args:
            resource_name: Name of the resource (e.g., "system_cpu")
            level: Alert level ("WARNING" or "CRITICAL")
            value: Current resource value
            threshold: Threshold that was exceeded
        """
        # Convert to dashboard alert severity
        severity = AlertSeverity.CRITICAL if level == "CRITICAL" else AlertSeverity.WARNING
        
        # Extract component ID if this is a component resource
        component_id = None
        if resource_name.startswith("component_"):
            parts = resource_name.split("_")
            if len(parts) >= 3:
                component_id = parts[1]
        
        # Generate alert
        self._generate_alert(
            severity=severity,
            title=f"Resource Alert: {resource_name}",
            description=f"{resource_name} at {value:.1f}% (threshold: {threshold:.1f}%)",
            component_id=component_id
        )
        
    def update_system_metrics(self, metrics: Dict[str, float]):
        """Update system-wide metrics on the dashboard.
        
        Args:
            metrics: Dictionary of system metrics to update
        """
        # Update system health metrics
        if hasattr(self.system_health, "system_metrics"):
            self.system_health.system_metrics.update(metrics)
        else:
            self.system_health.system_metrics = metrics
            
    def update_component_metrics(self, component_id: str, metrics: Dict[str, float]):
        """Update metrics for a specific component.
        
        Args:
            component_id: Component identifier
            metrics: Dictionary of metrics to update
        """
        # Get component
        component = self.system_health.get_component(component_id)
        if component:
            # Update component metrics
            if not component.metrics:
                component.metrics = {}
            component.metrics.update(metrics)
            
            # Update component in status dictionary
            if component_id in self.component_status:
                if "metrics" not in self.component_status[component_id]:
                    self.component_status[component_id]["metrics"] = {}
                self.component_status[component_id]["metrics"].update(metrics)
                
                # Recalculate health score
                self.component_status[component_id]["health"] = calculate_health_score({
                    "component_id": component_id,
                    "state": self.component_status[component_id]["state"],
                    "metrics": self.component_status[component_id]["metrics"]
                })
    
    async def start(self):
        """Start the health dashboard."""
        import asyncio
        
        if self.running:
            return
            
        self.running = True
        
        # Start resource monitoring if available
        if self.resource_monitor:
            self.resource_monitor.start()
            
            # Start dashboard integration if available
            if self.resource_integration:
                self.resource_integration.start()
        
        # Start the update loop
        self.update_task = asyncio.create_task(self._update_loop())
        
        # Start HTTP server for dashboard UI if aiohttp is available
        try:
            import aiohttp
            from aiohttp import web
            self.server_task = asyncio.create_task(start_dashboard_server(self))
            self.logger.info("Health dashboard HTTP server started")
        except ImportError:
            self.logger.info("Health dashboard started (without HTTP server - aiohttp not available)")
        
    async def stop(self):
        """Stop the health dashboard."""
        import asyncio
        
        if not self.running:
            return
            
        self.running = False
        
        # Stop resource monitoring if available
        if self.resource_monitor:
            self.resource_monitor.stop()
            
            # Stop dashboard integration if available
            if self.resource_integration:
                self.resource_integration.stop()
        
        # Cancel update task
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
                
        # Cancel server task if it exists
        if hasattr(self, 'server_task') and self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass
                
        self.logger.info("Health dashboard stopped")
        
    async def _update_loop(self):
        """Update component status regularly."""
        import asyncio
        
        while self.running:
            try:
                # If registry available, get components from it
                if self.registry:
                    # Update component status
                    components = await self.registry.get_all_components()
                    for component in components:
                        update_component_status(self, component)
                else:
                    # Use mock data for example
                    update_mock_data(self)
                
                # Update dependency graph
                update_dependency_graph(self)
                
                # Check for issues
                check_for_issues(self)
                
                # Generate health metrics
                generate_health_metrics(self)
                
                # Run spectral analysis if available
                if self.spectral_analyzer:
                    run_spectral_analysis(self)
                
            except Exception as e:
                self.logger.error(f"Error updating health dashboard: {e}", exception=e)
                
            # Wait before next update
            await asyncio.sleep(self.update_interval)
    
    def _generate_alert(self, severity, title, description, component_id=None):
        """Generate an alert.
        
        Args:
            severity: Alert severity
            title: Alert title
            description: Alert description
            component_id: Optional component ID
        """
        # Check if a similar alert already exists
        for alert in self.alerts:
            if (alert.title == title and 
                alert.component_id == component_id and 
                not alert.resolved):
                # Update existing alert
                alert.update_count()
                return alert
        
        # Create new alert
        alert = Alert(
            severity=severity,
            title=title,
            description=description,
            component_id=component_id
        )
        
        # Add to alert manager
        self.alert_manager.add_alert(alert)
        
        # Notify handlers
        for handler in self.alert_handlers:
            handler(alert)
            
        return alert
    
    def register_alert_handler(self, handler):
        """Register a handler for alerts.
        
        Args:
            handler: Function to call when an alert is generated
        """
        self.alert_handlers.append(handler)
    
    def get_system_health(self):
        """Get the current system health."""
        return self.system_health
    
    def get_component_status(self, component_id):
        """Get the status of a specific component."""
        return self.component_status.get(component_id)
    
    def get_alerts(self, component_id=None, include_resolved=False):
        """Get alerts, optionally filtered by component."""
        return self.alert_manager.get_alerts(component_id, include_resolved)
    
    def to_dict(self):
        """Convert dashboard to dictionary."""
        return {
            "components": list(self.component_status.values()),
            "alerts": [alert.to_dict() for alert in self.alerts if not alert.resolved],
            "dependency_graph": self.dependency_graph,
            "metrics": self.system_health.metrics,
            "timestamp": time.time()
        }
    
    def to_json(self):
        """Convert dashboard to JSON."""
        return json.dumps(self.to_dict())


# For backward compatibility
class MonitoringDashboard(HealthDashboard):
    """Backwards compatibility wrapper around HealthDashboard."""
    
    def __init__(self, 
                hermes_url: Optional[str] = None,
                update_interval: float = 10.0,
                alert_retention_days: int = 7):
        """
        Initialize monitoring dashboard.
        
        Args:
            hermes_url: Optional URL of Hermes service
            update_interval: Interval in seconds for updating health status
            alert_retention_days: Number of days to retain resolved alerts
        """
        super().__init__(update_interval=update_interval)
        self.hermes_url = hermes_url
        self.alert_retention_days = alert_retention_days
        
        # Override alert manager retention
        self.alert_manager = AlertManager(alert_retention_days)
        self.issue_detector = IssueDetector(self.alert_manager)
        self.system_health.alerts = self.alert_manager.alerts


# Singleton dashboard instance
_dashboard: Optional[MonitoringDashboard] = None

def get_dashboard() -> MonitoringDashboard:
    """
    Get the monitoring dashboard singleton.
    
    Returns:
        Monitoring dashboard
    """
    global _dashboard
    if _dashboard is None:
        _dashboard = MonitoringDashboard()
    return _dashboard