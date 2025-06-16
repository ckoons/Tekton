#!/usr/bin/env python3
"""
Resource Monitoring Integration Module

This module provides integration between the dashboard and resource monitoring system.
"""

from typing import Optional
from ...logging_integration import get_logger

# Configure logger
logger = get_logger("tekton.monitoring.dashboard.resource")

def get_resource_monitor():
    """Get the resource monitor singleton."""
    try:
        from ...resource_monitor import ResourceMonitor, ResourceMonitorDashboardIntegration
        # Import as needed to avoid circular imports
        from importlib import import_module
        resource_monitor_module = import_module("....resource_monitor", package=__name__)
        
        # If there's already a singleton instance, use it
        if hasattr(resource_monitor_module, "_resource_monitor_instance"):
            return resource_monitor_module._resource_monitor_instance
            
        # Otherwise create a new one
        monitor = ResourceMonitor()
        
        # Store on the module for singleton access
        resource_monitor_module._resource_monitor_instance = monitor
        return monitor
    except ImportError:
        logger.warning("Resource monitor not available")
        return None