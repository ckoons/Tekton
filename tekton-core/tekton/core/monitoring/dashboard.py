#!/usr/bin/env python3
"""
Monitoring Dashboard Module

This module provides a centralized dashboard for monitoring Tekton components.
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable

# Import from dashboard components
from .dashboard_components import (
    ResourceIntegration, get_resource_integration,
    HealthMetrics, generate_component_health, calculate_health_score,
    DependencyManager, build_dependency_graph, detect_dependency_cycles,
    SpectralAnalyzer, run_spectral_analysis, extract_spectral_metrics,
    DashboardServer, start_server, register_routes
)

# Import health and alerts modules
from .health import HealthStatus, ComponentHealth, SystemHealth, state_to_health_status
from .alerts import Alert, AlertSeverity, AlertManager
from .detector import IssueDetector

# Configure logger
from ..logging_integration import get_logger, LogCategory
logger = get_logger("tekton.monitoring.dashboard")


class HealthDashboard:
    """
    Interactive health dashboard for Tekton components.
    
    Provides real-time monitoring, alerting, and visualization of component health,
    dependencies, and system metrics using modular components.
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
        self.component_status = {}
        self.dependency_graph = {}
        self.update_task = None
        self.running = False
        
        # Create system health
        self.system_health = SystemHealth()
        
        # Initialize alert manager
        self.alert_manager = AlertManager(alert_retention_days=7)
        self.alert_handlers = []
        
        # Initialize issue detector
        self.issue_detector = IssueDetector(self.alert_manager)
        
        # Initialize dashboard components
        self.dependency_manager = DependencyManager(self)
        self.health_metrics = HealthMetrics(self)
        self.spectral_analyzer = SpectralAnalyzer(self)
        
        # Setup system health to use alerts from alert manager
        self.system_health.alerts = self.alert_manager.alerts
        
        # Initialize resource monitoring if enabled
        self.resource_integration = None
        if enable_resource_monitoring:
            self.resource_integration = get_resource_integration(self)
            
        # Initialize server component
        self.server = DashboardServer(self)
            
    def update_system_metrics(self, metrics: Dict[str, float]):
        """Update system-wide metrics on the dashboard.
        
        Args:
            metrics: Dictionary of system metrics to update
        """
        # Update system health metrics
        if not hasattr(self.system_health, "system_metrics"):
            self.system_health.system_metrics = {}
            
        self.system_health.system_metrics.update(metrics)
            
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
        if self.running:
            return
            
        self.running = True
        
        # Start resource integration if available
        if self.resource_integration:
            await self.resource_integration.start()
        
        # Start the update loop
        self.update_task = asyncio.create_task(self._update_loop())
        
        # Start HTTP server for dashboard UI
        try:
            await self.server.start()
        except Exception as e:
            logger.warning(f"Could not start dashboard server: {e}")
        
    async def stop(self):
        """Stop the health dashboard."""
        if not self.running:
            return
            
        self.running = False
        
        # Stop resource integration if available
        if self.resource_integration:
            await self.resource_integration.stop()
        
        # Cancel update task
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
                
        # Stop HTTP server
        try:
            await self.server.stop()
        except Exception as e:
            logger.warning(f"Error stopping dashboard server: {e}")
                
        logger.info("Health dashboard stopped")
        
    async def _update_loop(self):
        """Update component status regularly."""
        while self.running:
            try:
                # If registry available, get components from it
                if self.registry:
                    # Update component status
                    components = await self.registry.get_all_components()
                    for component in components:
                        self._update_component_status(component)
                else:
                    # Use mock data for testing
                    self._update_mock_data()
                
                # Update dependency graph
                self.dependency_manager.update_dependency_graph()
                
                # Check for issues
                self._check_for_issues()
                
                # Update health metrics
                self.health_metrics.update_system_health()
                
                # Run spectral analysis if available
                self.spectral_analyzer.run_analysis()
                
            except Exception as e:
                logger.error(f"Error updating health dashboard: {e}", exception=e)
                
            # Wait before next update
            await asyncio.sleep(self.update_interval)
    
    def _update_component_status(self, component: Dict[str, Any]):
        """Update status for a single component.
        
        Args:
            component: Component data dictionary
        """
        component_id = component.get("component_id")
        if not component_id:
            return
            
        # Generate component health
        component_health = generate_component_health(component)
        
        # Update component status
        self.component_status[component_id] = component_health
        
        # Update system health
        component_obj = ComponentHealth(
            component_id=component_id,
            component_name=component.get("component_name", component_id),
            component_type=component.get("component_type", "unknown"),
            status=state_to_health_status(component.get("state", "unknown")),
            state=component.get("state", "unknown"),
            metrics=component.get("metrics", {})
        )
        self.system_health.update_component(component_obj)
    
    def _update_mock_data(self):
        """Update with mock data for testing."""
        import random
        
        # Mock component data
        components = [
            {
                "component_id": "tekton-core",
                "component_name": "Tekton Core",
                "component_type": "core",
                "state": "RUNNING",
                "metrics": {
                    "cpu_usage": random.uniform(10, 30),
                    "memory_usage": random.uniform(15, 40),
                    "error_rate": random.uniform(0, 2),
                    "success_rate": random.uniform(98, 100)
                },
                "dependencies": []
            },
            {
                "component_id": "tekton-engram",
                "component_name": "Engram Service",
                "component_type": "memory",
                "state": "RUNNING",
                "metrics": {
                    "cpu_usage": random.uniform(20, 50),
                    "memory_usage": random.uniform(30, 60),
                    "error_rate": random.uniform(0, 5),
                    "success_rate": random.uniform(95, 100),
                    "latency": random.uniform(100, 300)
                },
                "dependencies": ["tekton-core"]
            },
            {
                "component_id": "tekton-hermes",
                "component_name": "Hermes Service",
                "component_type": "communication",
                "state": "DEGRADED" if random.random() < 0.2 else "RUNNING",
                "metrics": {
                    "cpu_usage": random.uniform(30, 70),
                    "memory_usage": random.uniform(40, 80),
                    "error_rate": random.uniform(3, 10) if random.random() < 0.2 else random.uniform(0, 3),
                    "success_rate": random.uniform(90, 97) if random.random() < 0.2 else random.uniform(97, 100),
                    "latency": random.uniform(200, 600) if random.random() < 0.2 else random.uniform(100, 200),
                    "message_throughput": random.uniform(100, 300)
                },
                "dependencies": ["tekton-core"]
            }
        ]
        
        # Update each component
        for component in components:
            self._update_component_status(component)
    
    def _check_for_issues(self):
        """Check for component issues."""
        # Check component states
        for component_id, component in self.component_status.items():
            state = component.get("state")
            status = state_to_health_status(state)
            
            if status == HealthStatus.UNHEALTHY:
                self._generate_alert(
                    severity=AlertSeverity.CRITICAL,
                    title=f"Component Unhealthy: {component.get('component_name', component_id)}",
                    description=f"Component is in {state} state",
                    component_id=component_id
                )
            elif status == HealthStatus.DEGRADED:
                self._generate_alert(
                    severity=AlertSeverity.WARNING,
                    title=f"Component Degraded: {component.get('component_name', component_id)}",
                    description=f"Component is in {state} state",
                    component_id=component_id
                )
        
        # Check for dependency cycles
        cycles = detect_dependency_cycles(self.dependency_graph)
        for cycle in cycles:
            cycle_str = " -> ".join(cycle)
            self._generate_alert(
                severity=AlertSeverity.WARNING,
                title="Dependency Cycle Detected",
                description=f"Circular dependency detected: {cycle_str}",
                component_id=None
            )
        
        # Check metrics thresholds
        for component_id, component in self.component_status.items():
            metrics = component.get("metrics", {})
            component_name = component.get("component_name", component_id)
            
            # Check CPU usage
            cpu_usage = metrics.get("cpu_usage")
            if cpu_usage and cpu_usage > 80:
                self._generate_alert(
                    severity=AlertSeverity.WARNING,
                    title=f"High CPU Usage: {component_name}",
                    description=f"CPU usage at {cpu_usage:.1f}% (threshold: 80%)",
                    component_id=component_id
                )
            
            # Check memory usage
            memory_usage = metrics.get("memory_usage")
            if memory_usage and memory_usage > 85:
                self._generate_alert(
                    severity=AlertSeverity.WARNING,
                    title=f"High Memory Usage: {component_name}",
                    description=f"Memory usage at {memory_usage:.1f}% (threshold: 85%)",
                    component_id=component_id
                )
            
            # Check error rate
            error_rate = metrics.get("error_rate")
            if error_rate and error_rate > 5:
                self._generate_alert(
                    severity=AlertSeverity.WARNING if error_rate < 10 else AlertSeverity.CRITICAL,
                    title=f"High Error Rate: {component_name}",
                    description=f"Error rate at {error_rate:.1f}% (threshold: 5%)",
                    component_id=component_id
                )
    
    def _generate_alert(self, severity, title, description, component_id=None):
        """Generate an alert.
        
        Args:
            severity: Alert severity
            title: Alert title
            description: Alert description
            component_id: Optional component ID
        """
        # Check if a similar alert already exists
        for alert in self.alert_manager.get_alerts(component_id, include_resolved=False):
            if (alert.title == title and not alert.resolved):
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


# Example usage
async def example():
    """Example of monitoring dashboard."""
    from datetime import datetime
    
    # Create dashboard
    dashboard = get_dashboard()
    
    # Register alert hook
    def alert_hook(alert):
        print(f"ALERT: {alert.severity.value.upper()} - {alert.title}")
        print(f"  {alert.description}")
        print(f"  Component: {alert.component_id}")
        print(f"  Time: {datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
    dashboard.register_alert_handler(alert_hook)
    
    # Start dashboard
    await dashboard.start()
    
    try:
        # Wait a bit for dashboard to update
        for _ in range(3):
            await asyncio.sleep(5)
            
            # Print current status
            health = dashboard.get_system_health()
            print(f"System Status: {health.overall_status.value}")
            print(f"Components: {health.metrics['total_components']} total, "
                f"{health.metrics['healthy_components']} healthy, "
                f"{health.metrics['degraded_components']} degraded, "
                f"{health.metrics['unhealthy_components']} unhealthy")
            print(f"Active Alerts: {health.metrics['active_alerts']}")
            print()
            
            # Print component details
            for component in health.components.values():
                print(f"Component: {component.component_name} ({component.component_id})")
                print(f"  Status: {component.status.value}")
                print(f"  Type: {component.component_type}")
                print(f"  State: {component.state}")
                if component.metrics:
                    print("  Metrics:")
                    for key, value in component.metrics.items():
                        print(f"    {key}: {value}")
                print()
                
    finally:
        # Stop dashboard
        await dashboard.stop()


if __name__ == "__main__":
    asyncio.run(example())