#!/usr/bin/env python3
"""
Resource Integration Component

This module provides integration with system resource monitoring.
"""

import time
from typing import Dict, List, Any, Optional, Callable

from ...logging_integration import get_logger, LogCategory
from ...metrics_integration import get_metrics_manager

# Configure logger
logger = get_logger("tekton.monitoring.dashboard.resource")


class ResourceIntegration:
    """
    Integration with system resource monitoring.
    
    Connects the dashboard with resource monitoring to display system
    and component resource usage.
    """
    
    def __init__(self, 
                resource_monitor=None,
                dashboard=None,
                update_interval: float = 5.0):
        """
        Initialize resource integration.
        
        Args:
            resource_monitor: Resource monitor instance
            dashboard: Dashboard instance
            update_interval: Update interval in seconds
        """
        self.resource_monitor = resource_monitor
        self.dashboard = dashboard
        self.update_interval = update_interval
        self.running = False
        self.update_task = None
        
        # Initialize metrics manager
        self.metrics_manager = get_metrics_manager("tekton.dashboard.resources")
        
        # Register alert handler
        if resource_monitor:
            resource_monitor.add_alert_handler(self._handle_resource_alert)
            
    def _handle_resource_alert(self, resource_name: str, level: str, value: float, threshold: float):
        """Handle resource alerts.
        
        Args:
            resource_name: Name of the resource
            level: Alert level
            value: Current value
            threshold: Threshold that was exceeded
        """
        if not self.dashboard:
            return
            
        # Extract component ID if this is a component-specific resource
        component_id = None
        if resource_name.startswith("component_"):
            parts = resource_name.split("_")
            if len(parts) >= 3:
                component_id = parts[1]
        
        # Generate dashboard alert
        from ..alerts import AlertSeverity
        severity = AlertSeverity.CRITICAL if level == "CRITICAL" else AlertSeverity.WARNING
        
        # Generate alert through dashboard
        if hasattr(self.dashboard, "_generate_alert"):
            self.dashboard._generate_alert(
                severity=severity,
                title=f"Resource Alert: {resource_name}",
                description=f"{resource_name} at {value:.1f}% (threshold: {threshold:.1f}%)",
                component_id=component_id
            )
    
    async def start(self):
        """Start resource integration."""
        import asyncio
        
        if self.running or not self.resource_monitor:
            return
            
        self.running = True
        
        # Start resource monitor if not already started
        if hasattr(self.resource_monitor, "is_running") and not self.resource_monitor.is_running():
            self.resource_monitor.start()
        
        # Start update task
        self.update_task = asyncio.create_task(self._update_loop())
        
        logger.info("Resource integration started")
        
    async def stop(self):
        """Stop resource integration."""
        import asyncio
        
        if not self.running:
            return
            
        self.running = False
        
        # Cancel update task
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Resource integration stopped")
        
    async def _update_loop(self):
        """Update resource metrics periodically."""
        import asyncio
        
        while self.running and self.dashboard and self.resource_monitor:
            try:
                # Get system metrics
                system_metrics = self.resource_monitor.get_system_metrics()
                if system_metrics:
                    # Update dashboard system metrics
                    self.dashboard.update_system_metrics(system_metrics)
                    
                # Get component metrics
                component_metrics = self.resource_monitor.get_component_metrics()
                for component_id, metrics in component_metrics.items():
                    # Update dashboard component metrics
                    self.dashboard.update_component_metrics(component_id, metrics)
                    
            except Exception as e:
                logger.error(f"Error updating resource metrics: {e}", exception=e)
                
            # Wait before next update
            await asyncio.sleep(self.update_interval)


# Singleton instance
_resource_integration = None

def get_resource_integration(dashboard=None):
    """Get resource integration singleton.
    
    Args:
        dashboard: Dashboard instance
        
    Returns:
        ResourceIntegration instance
    """
    global _resource_integration
    
    if _resource_integration is None:
        # Try to get resource monitor
        resource_monitor = None
        try:
            from ...resource_monitoring.monitor import get_resource_monitor
            resource_monitor = get_resource_monitor()
        except ImportError:
            logger.warning("Resource monitor not available")
            
        # Create integration
        _resource_integration = ResourceIntegration(
            resource_monitor=resource_monitor,
            dashboard=dashboard
        )
        
    return _resource_integration
