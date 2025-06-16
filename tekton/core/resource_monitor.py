#!/usr/bin/env python3
"""
Resource monitoring system for Tekton.

This module provides re-exports to maintain backward compatibility
with the original resource_monitor.py file.
"""

# Re-export all classes for backward compatibility
from .resource_monitoring.config import ResourceConfig, ResourceThreshold
from .resource_monitoring.metrics import ResourceMetrics
from .resource_monitoring.monitor import ResourceMonitor
from .resource_monitoring.dashboard_integration import ResourceMonitorDashboardIntegration

__all__ = [
    "ResourceMonitor",
    "ResourceConfig",
    "ResourceThreshold",
    "ResourceMetrics",
    "ResourceMonitorDashboardIntegration"
]
