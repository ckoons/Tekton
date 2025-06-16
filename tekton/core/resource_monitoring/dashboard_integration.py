#!/usr/bin/env python3
"""
Integration between ResourceMonitor and the HealthDashboard.
"""

import asyncio
import logging
from typing import Optional

from .monitor import ResourceMonitor

logger = logging.getLogger(__name__)


class ResourceMonitorDashboardIntegration:
    """Integration between ResourceMonitor and the HealthDashboard."""
    
    def __init__(
        self, 
        resource_monitor: ResourceMonitor, 
        dashboard_update_interval: float = 5.0
    ):
        """
        Initialize the dashboard integration.
        
        Args:
            resource_monitor: ResourceMonitor instance to integrate with
            dashboard_update_interval: How often to update the dashboard (seconds)
        """
        self.resource_monitor = resource_monitor
        self.update_interval = dashboard_update_interval
        self._running = False
        self._update_task = None
        
        # Register alert handler
        self.resource_monitor.add_alert_handler(self._alert_handler)
        
        # Import dashboard module - using late import to avoid circular dependencies
        try:
            from tekton.core.monitoring.dashboard import get_dashboard
            self.dashboard = get_dashboard()
        except (ImportError, AttributeError):
            logger.warning("Health dashboard not available for resource monitor integration")
            self.dashboard = None
            
    def _alert_handler(self, resource_name: str, level: str, value: float, threshold: float) -> None:
        """Handle resource alerts by sending them to the dashboard."""
        if not self.dashboard:
            return
            
        alert_type = "resource"
        severity = "high" if level == "CRITICAL" else "medium"
        
        self.dashboard.add_alert(
            title=f"Resource Alert: {resource_name}",
            message=f"{resource_name} is at {value:.1f}% (threshold: {threshold:.1f}%)",
            alert_type=alert_type,
            severity=severity,
            component_id=resource_name.split('_')[1] if resource_name.startswith("component_") else None
        )
        
    async def _update_dashboard(self) -> None:
        """Update the dashboard with current resource metrics."""
        if not self.dashboard:
            return
            
        while self._running:
            try:
                metrics = self.resource_monitor.get_current_metrics()
                
                # Update system metrics
                self.dashboard.update_system_metrics({
                    "cpu": metrics.cpu_percent,
                    "memory": metrics.memory_percent,
                    "disk": max(metrics.disk_percent.values()) if metrics.disk_percent else 0,
                    "network": sum(nic.get("total_mbps", 0) for nic in metrics.network_mbps.values()) 
                                 if metrics.network_mbps else 0
                })
                
                # Update component metrics
                for component_id, comp_metrics in metrics.component_metrics.items():
                    self.dashboard.update_component_metrics(
                        component_id,
                        {
                            "cpu": comp_metrics.get("cpu_percent", 0),
                            "memory": comp_metrics.get("memory_percent", 0)
                        }
                    )
                    
            except Exception as e:
                logger.error(f"Error updating dashboard with resource metrics: {e}")
                
            await asyncio.sleep(self.update_interval)
            
    def start(self) -> None:
        """Start the dashboard integration updates."""
        if self._running or not self.dashboard:
            return
            
        self._running = True
        self._update_task = asyncio.create_task(self._update_dashboard())
        logger.info("Resource monitor dashboard integration started")
        
    def stop(self) -> None:
        """Stop the dashboard integration updates."""
        if not self._running:
            return
            
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            self._update_task = None
            
        logger.info("Resource monitor dashboard integration stopped")
